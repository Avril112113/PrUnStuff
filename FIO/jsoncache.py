import functools
import inspect
import os
import typing
from datetime import datetime, timedelta
from peewee import *
from peewee import Metadata
# import orjson
import quickle


def jsonCacheHook(dct):
	if "__class__" in dct:
		if dct["__class__"] + "datetime":
			return datetime.fromisoformat(dct["__value__"])
	return dct


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


class JsonCache:
	DATETIME_KEY = "cached_datetime"
	VALUE_KEY = "cached_value"
	dbs = {}

	def __init__(
			self, f: callable,
			paramOpts: list[ParamOpts] = None,
			invalidateTime: timedelta = None,
			speedQueryFields: list[str] = None):
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

		self.db_file_path = f"{os.path.dirname(os.path.abspath(inspect.getfile(f)))}/cache.db"
		self.db = self.dbs.get(self.db_file_path, None)
		if self.db is None:
			self.db = SqliteDatabase(self.db_file_path)
			self.db.connect()

		class CacheModel(Model):
			_meta: Metadata
			_modified = DateTimeField(default=datetime.now)

			def save(self, *args, **kwargs):
				self._modified = datetime.now()
				return super(CacheModel, self).save(*args, **kwargs)
		self.keys = []
		for param in inspect.signature(f).parameters.values():
			if param.name != "self" and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
				CacheModel._meta.add_field(param.name, TextField())
				self.keys.append(param.name)
		if len(self.keys) <= 0:
			CacheModel._meta.add_field("id", AutoField())
		CacheModel._meta.add_field("_data", BlobField())
		for fieldName in self.speedQueryFields:
			CacheModel._meta.add_field(f"_sq_{fieldName}", TextField())
		CacheModel._meta.set_table_name(f.__name__)
		CacheModel.bind(self.db)
		self.model = CacheModel
		self.db.create_tables([CacheModel])

	def __call__(self, *rawArgs):
		startIndex = 1 if self.hasSelf else 0
		args = [
			(self.paramOpts[i-startIndex].convert(rawArgs[i]) if (len(self.paramOpts) > i-startIndex and self.paramOpts[i-startIndex] is not None) else rawArgs[i])
			for i in range(startIndex, len(rawArgs))
		]
		recordKeys = {self.keys[i]: args[i] for i in range(len(args))}
		if len(recordKeys) == 0:
			recordKeys = {"id": 0}
		dbCache = self.model.get_or_none(**recordKeys)
		if dbCache is not None:
			invalid = self.invalidateTime is not None and datetime.now() > datetime.fromisoformat(str(dbCache._modified))+self.invalidateTime
			if not invalid:
				return quickle.loads(dbCache._data)
		if self.hasSelf:
			args.insert(0, rawArgs[0])
		value = self.f(*args)
		dbFields = {
			"_data": quickle.dumps(value)
		}
		for fieldName in self.speedQueryFields:
			dbFields[f"_sq_{fieldName}"] = value[fieldName]
		if dbCache is not None:
			for field, value in dbFields.items():
				setattr(dbCache, field, value)
			dbCache.save()
		else:
			self.model.create(**recordKeys, **dbFields)
		return value

	def cacheValue(self, value, *args):
		jsonData = quickle.dumps(value)
		defaults = {"_data": jsonData}
		for fieldName in self.speedQueryFields:
			defaults[f"_sq_{fieldName}"] = value[fieldName]
		dbCache, created = self.model.get_or_create(**{self.keys[i]: args[i] for i in range(len(args))}, defaults=defaults)
		if not created:
			dbCache._data = jsonData
			dbCache.save()

	def isCached(self, *args):
		return self.model.get_or_none(**{self.keys[i]: args[i] for i in range(len(args))}) is not None

	def speedQuery(self, speedQueryField: str, value: typing.Union[str, int]):
		fieldName = f"_sq_{speedQueryField}"
		values = []
		for data in self.model.select().filter(**{fieldName: value}).execute():
			values.append({key: getattr(data, f"{key}") for key in self.keys})
		return values

	def clearCache(self):
		self.model.delete().execute()

	def addMethods(self, wrapper: callable):
		"""This is used for a very hacky solution..."""
		setattr(wrapper, "cacheValue", self.cacheValue)
		setattr(wrapper, "clearCache", self.clearCache)
		setattr(wrapper, "isCached", self.isCached)
		setattr(wrapper, "speedQuery", self.speedQuery)


def jsoncache(
		paramOpts: list[ParamOpts] = None,
		invalidateTime: timedelta = None,
		speedQueryFields: list[str] = None):
	T = typing.TypeVar("T", bound=typing.Callable)

	def decorator(f: T) -> T:
		cache = JsonCache(f, paramOpts, invalidateTime, speedQueryFields)

		@functools.wraps(f)
		def wrap(*args):
			return cache(*args)
		cache.addMethods(wrap)
		return wrap
	return decorator
