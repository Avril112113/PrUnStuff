import functools
import inspect
import os
import typing
from datetime import datetime, timedelta

import peewee
from peewee import *
from peewee import Metadata
import quickle


class ParamOpts:
	def __init__(self, upper: bool = False, lower: bool = False):
		self.upper = upper
		self.lower = lower

	def convert(self, value: any):
		if self.upper:
			return value.upper()
		if self.lower:
			return value.upper()
		return value


class DBCache:
	DATETIME_KEY = "cached_datetime"
	VALUE_KEY = "cached_value"
	dbs = {}

	# noinspection PyProtectedMember
	def __init__(
			self, f: callable,
			paramOpts: list[ParamOpts] = None,
			invalidateTime: timedelta = None,
			speedQueryFields: list[str] = None,
			variedParams: dict[str, tuple[str, ...]] = None):
		"""
		WARN: Does not support kwargs (AKA default arguments), they are simply not accepted to enforce this
		WARN: Only supports string arguments
		`speedQuery` only works when the result of this function is a dictionary
		:param f: The original function
		:param paramOpts: The options for each parameter
		:param invalidateTime: The timedelta before the cache is refreshed
		:param speedQueryFields: List of extra fields to store in the cache database
		"""
		self.f = f
		self.hasSelf = next(iter(inspect.signature(f).parameters.values())).name == "self"
		self.paramOpts = paramOpts if paramOpts is not None else []
		self.invalidateTime = invalidateTime
		self.speedQueryFields = speedQueryFields if speedQueryFields is not None else []
		self.variedParams = variedParams if variedParams is not None else []

		self.db_file_path = f"{os.path.dirname(os.path.abspath(inspect.getfile(f)))}/cache.db"
		self.db = self.dbs.get(self.db_file_path, None)
		if self.db is None:
			self.db = SqliteDatabase(self.db_file_path)
			self.db.connect()

		class CacheModel(Model):
			_meta: Metadata
			_modified = DateTimeField(default=datetime.now)
			id = AutoField()

			def save(self, *args, **kwargs):
				self._modified = datetime.now()
				return super(CacheModel, self).save(*args, **kwargs)
		self.paramNames = []
		for param in inspect.signature(f).parameters.values():
			if param.name != "self" and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
				if param.name in self.variedParams:
					for variedParam in self.variedParams[param.name]:
						CacheModel._meta.add_field(f"{param.name}_{variedParam}", TextField())
				else:
					CacheModel._meta.add_field(param.name, TextField())
				self.paramNames.append(param.name)
		CacheModel._meta.add_field("_data", BlobField())
		for fieldName in self.speedQueryFields:
			CacheModel._meta.add_field(f"_sq_{fieldName}", TextField())
		CacheModel._meta.set_table_name(f.__name__)
		CacheModel.bind(self.db)
		self.model = CacheModel
		self.db.create_tables([CacheModel])

	def getQueryExpression(self, args: typing.Union[list[str], tuple[str]]):
		if len(args) == 0:
			return self.model.id == 1
		query: typing.Optional[peewee.Expression] = None
		for i in range(len(args)):
			expr: typing.Optional[peewee.Expression] = None
			paramName = self.paramNames[i]
			if paramName in self.variedParams:
				for variedParam in self.variedParams[paramName]:
					field: peewee.Field = getattr(self.model, f"{paramName}_{variedParam}")
					subExpr = field == args[i]
					if expr is None:
						expr = subExpr
					else:
						expr = expr | subExpr
			else:
				field: peewee.Field = getattr(self.model, paramName)
				expr = field == args[i]
			if query is None:
				query = expr
			else:
				query = query & expr
		return query
	
	def getModelFieldValues(self, args: typing.Union[list[str], tuple[str]], value: any):
		fields = {
			"_data": quickle.dumps(value)
		}
		for i in range(len(args)):
			paramName = self.paramNames[i]
			if paramName in self.variedParams:
				for variedParam in self.variedParams[paramName]:
					fields[f"{paramName}_{variedParam}"] = value[variedParam]
			else:
				fields[f"{paramName}"] = args[i]
		for fieldName in self.speedQueryFields:
			fields[f"_sq_{fieldName}"] = value[fieldName]
		return fields

	def getValueFromParamName(self, data: Model, paramName: str):
		if paramName in self.variedParams:
			return getattr(data, f"{paramName}_{self.variedParams[paramName][0]}")
		else:
			return getattr(data, paramName)

	def isCacheInvalid(self, cache: "Model"):
		invalid = self.invalidateTime is not None and datetime.now() > datetime.fromisoformat(str(cache._modified)) + self.invalidateTime
		return invalid

	def __call__(self, *rawArgs):
		startIndex = 1 if self.hasSelf else 0
		args = [
			(self.paramOpts[i-startIndex].convert(rawArgs[i]) if (len(self.paramOpts) > i-startIndex and self.paramOpts[i-startIndex] is not None) else rawArgs[i])
			for i in range(startIndex, len(rawArgs))
		]
		cache = self.model.get_or_none(self.getQueryExpression(args))
		if cache is not None and not self.isCacheInvalid(cache):
			return quickle.loads(cache._data)
		if self.hasSelf:
			callResult = self.f(rawArgs[0], *args)
		else:
			callResult = self.f(*args)
		dbFields = self.getModelFieldValues(args, callResult)
		if cache is not None:
			for field, value in dbFields.items():
				setattr(cache, field, value)
			cache.save()
		else:
			self.model.create(**dbFields)
		return callResult

	def cacheValue(self, value, *args: str):
		dbCache = self.model.get_or_none(self.getQueryExpression(args))
		if dbCache is None:
			self.model.create(**self.getModelFieldValues(args, value))
		else:
			dbCache._data = quickle.dumps(value)
			dbCache.save()

	def isCached(self, *args: str):
		cache = self.model.get_or_none(self.getQueryExpression(args))
		if cache is None:
			return False
		return not self.isCacheInvalid(cache)

	def speedQuery(self, speedQueryField: str, value: typing.Union[str, int]):
		fieldName = f"_sq_{speedQueryField}"
		values = []
		for data in self.model.select().where(getattr(self.model, fieldName) == value).execute():
			values.append({paramName: self.getValueFromParamName(data, paramName) for paramName in self.paramNames})
		return values

	def clearCache(self):
		self.model.delete().execute()

	def addMethods(self, wrapper: callable):
		"""This is used for a very hacky solution..."""
		setattr(wrapper, "cacheValue", self.cacheValue)
		setattr(wrapper, "clearCache", self.clearCache)
		setattr(wrapper, "isCached", self.isCached)
		setattr(wrapper, "speedQuery", self.speedQuery)


def dbcache(
		paramOpts: list[ParamOpts] = None,
		invalidateTime: timedelta = None,
		speedQueryFields: list[str] = None,
		variedParams: dict[str, tuple[str, ...]] = None):
	T = typing.TypeVar("T", bound=typing.Callable)

	def decorator(f: T) -> T:
		cache = DBCache(f, paramOpts, invalidateTime, speedQueryFields, variedParams)

		@functools.wraps(f)
		def wrap(*args):
			return cache(*args)
		cache.addMethods(wrap)
		return wrap
	return decorator
