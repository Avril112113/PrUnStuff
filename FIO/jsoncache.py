import functools
import inspect
import json
import os
import typing
from datetime import datetime, timedelta
from peewee import *
from peewee import Metadata


class JsonCacheEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return {"__class__": "datetime", "__value__": obj.isoformat()}
		return json.JSONEncoder.default(self, obj)


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

	def __init__(self, f: callable, paramOpts: list[ParamOpts] = None, invalidateTime: timedelta = None):
		"""
		WARN: Does not support kwargs (AKA default arguments), they are simply not accepted to enforce this
		WARN: Only supports string arguments
		:param f: The original function
		:param paramOpts: The options for each parameter
		:param invalidateTime: The timedelta before the cache is refreshed
		"""
		self.f = f
		self.hasSelf = next(iter(inspect.signature(f).parameters.values())).name == "self"
		self.paramOpts = paramOpts if paramOpts is not None else []
		self.invalidateTime = invalidateTime

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
		CacheModel._meta.add_field("_json", TextField())
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
				return json.loads(dbCache._json)
		if self.hasSelf:
			args.insert(0, rawArgs[0])
		value = self.f(*args)
		if dbCache is not None:
			dbCache._json = json.dumps(value)
			dbCache.save()
		else:
			self.model.create(**recordKeys, _json=json.dumps(value))
		return value

	def cacheValue(self, value, *args):
		jsonData = json.dumps(value)
		dbCache, created = self.model.get_or_create(**{self.keys[i]: args[i] for i in range(len(args))}, defaults={"_json": jsonData})
		if not created:
			dbCache._json = jsonData
			dbCache.save()

	def clearCache(self):
		self.model.delete().execute()

	def addMethods(self, wrapper: callable):
		"""This is used for a very hacky solution..."""
		setattr(wrapper, "cacheValue", self.cacheValue)
		setattr(wrapper, "clearCache", self.clearCache)


def jsoncache(paramOpts: list[ParamOpts] = None, invalidateTime: timedelta = None):
	T = typing.TypeVar("T", bound=typing.Callable)

	def decorator(f: T) -> T:
		cache = JsonCache(f, paramOpts, invalidateTime)

		@functools.wraps(f)
		def wrap(*args):
			return cache(*args)
		cache.addMethods(wrap)
		return wrap
	return decorator
