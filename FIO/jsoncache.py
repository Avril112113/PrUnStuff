import functools
import inspect
import json
import os
import sys
import traceback
import typing
from datetime import datetime, timedelta


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

	def __init__(self, f, hasSelf: bool = True, paramOpts: list[ParamOpts] = None, invalidateTime: timedelta = None):
		"""
		NOTE: Does not support kwargs (AKA default arguments), they are simply not accepted to enforce this
		:param f: The original function
		:param hasSelf: If True, the first argument is not processed for the cache but is still passed to the funcion
		:param paramOpts: The options for each parameter
		:param invalidateTime: The timedelta before the cache is refreshed
		"""
		self.f = f
		self.hasSelf = hasSelf
		self.paramOpts = paramOpts if paramOpts is not None else []
		self.invalidateTime = invalidateTime
		self.cache_folder_path = f"{os.path.dirname(os.path.abspath(inspect.getfile(f)))}/cache"
		self.cache_file_path = f"{self.cache_folder_path}/{f.__name__}.json"
		self.cache = {}
		self.readCache()

	def __call__(self, *rawArgs):
		startIndex = 1 if self.hasSelf else 0
		args = [
			(self.paramOpts[i-startIndex].convert(rawArgs[i]) if (len(self.paramOpts) > i-startIndex and self.paramOpts[i-startIndex] is not None) else rawArgs[i])
			for i in range(startIndex, len(rawArgs))
		]
		argCache = self.cache
		for arg in args:
			if arg not in argCache:
				argCache[arg] = {}
			argCache = argCache[arg]
		if self.hasSelf:
			args.insert(0, rawArgs[0])
		# self.cache[self.DATETIME_KEY] = self.cache.get(self.DATETIME_KEY, datetime.datetime.now())
		# self.cache[self.VALUE_KEY] = self.cache.get(self.VALUE_KEY, None)
		shouldCheckInvalidate = self.invalidateTime is not None and self.DATETIME_KEY in argCache
		if (
			self.VALUE_KEY not in argCache
				or
			(shouldCheckInvalidate and (datetime.now() >= argCache[self.DATETIME_KEY]+self.invalidateTime))
		):
			# noinspection PyBroadException
			try:
				argCache[self.VALUE_KEY] = self.f(*args)
				argCache[self.DATETIME_KEY] = datetime.now()
				self.writeCache()  # TODO: This could be done after a minute or when the program stops
			except Exception:
				traceback.print_exc()
		if self.VALUE_KEY not in argCache:
			raise KeyError("There was an error in caching the value and there was no already cached value to use. (See above)")
		return argCache[self.VALUE_KEY]

	def readCache(self):
		try:
			self.cache = json.load(open(self.cache_file_path, "r"), object_hook=jsonCacheHook)
		except (IOError, ValueError):
			pass

	def writeCache(self):
		try:
			if not os.path.isdir(self.cache_folder_path):
				os.mkdir(self.cache_folder_path)
			json.dump(self.cache, open(self.cache_file_path, "w"), indent="\t", cls=JsonCacheEncoder)
		except IOError:
			sys.stderr.write(f"Failed to write cache file! {self.cache_file_path}\n")

	def clearCache(self):
		self.cache = {}
		self.writeCache()

	def addMethods(self, wrapper: callable):
		"""This is used for a very hacky solution..."""
		setattr(wrapper, "clearCache", self.clearCache)


def jsoncache(hasSelf: bool = True, paramOpts: list[ParamOpts] = None, invalidateTime: timedelta = None):
	T = typing.TypeVar("T", bound=typing.Callable)

	def decorator(f: T) -> T:
		cache = JsonCache(f, hasSelf, paramOpts, invalidateTime)

		@functools.wraps(f)
		def wrap(*args):
			return cache(*args)
		cache.addMethods(wrap)
		return wrap
	return decorator


# def jsoncache(param_upper=False):
# 	"""
# 	Only works with bound methods, where the first parameter is `self` or `cls`
# 	Only supports between 0-2 other arguments!
# 	All arguments must not be default (kwargs are simply not passed through)
# 	:param param_upper: Only works on the first argument
# 	"""
# 	def decorator(original_func):
# 		file_path = f"{os.path.dirname(os.path.abspath(inspect.getfile(original_func)))}/cache/{original_func.__name__}.json"
# 		try:
# 			cache = json.load(open(file_path, "r"))
# 		except (IOError, ValueError):
# 			cache = None
#
# 		def new_func(self, *args):
# 			nonlocal cache
# 			if len(args) > 0:
# 				if cache is None:
# 					cache = {}
# 				arg0 = args[0].upper() if param_upper else args[0]
# 				if len(args) > 1:
# 					arg1 = args[1]
# 					if arg0 not in cache:
# 						cache[arg0] = {}
# 					if arg1 not in cache[arg0]:
# 						cache[arg0][arg1] = original_func(self, *args)
# 						json.dump(cache, open(file_path, "w"), indent="\t")
# 					return cache[arg0][arg1]
# 				else:
# 					if arg0 not in cache:
# 						cache[arg0] = original_func(self, *args)
# 						json.dump(cache, open(file_path, "w"), indent="\t")
# 					return cache[arg0]
# 			else:
# 				if cache is None:
# 					cache = original_func(self, *args)
# 					json.dump(cache, open(file_path, "w"), indent="\t")
# 				return cache
#
# 		return new_func
# 	return decorator
