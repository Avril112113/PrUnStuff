import inspect
import json
import os


def jsoncache(param_upper=False):
	"""
	Only works with bound methods, where the first parameter is `self` or `cls`
	Only supports between 0-2 other arguments!
	All arguments must not be default (kwargs are simply not passed through)
	:param param_upper: Only works on the first argument
	"""
	def decorator(original_func):
		file_path = f"{os.path.dirname(os.path.abspath(inspect.getfile(original_func)))}/cache/{original_func.__name__}.json"
		try:
			cache = json.load(open(file_path, "r"))
		except (IOError, ValueError):
			cache = None

		def new_func(self, *args):
			nonlocal cache
			if len(args) > 0:
				if cache is None:
					cache = {}
				arg0 = args[0].upper() if param_upper else args[0]
				if len(args) > 1:
					arg1 = args[1]
					if arg0 not in cache:
						cache[arg0] = {}
					if arg1 not in cache[arg0]:
						cache[arg0][arg1] = original_func(self, *args)
						json.dump(cache, open(file_path, "w"), indent="\t")
					return cache[arg0][arg1]
				else:
					if arg0 not in cache:
						cache[arg0] = original_func(self, *args)
						json.dump(cache, open(file_path, "w"), indent="\t")
					return cache[arg0]
			else:
				if cache is None:
					cache = original_func(self, *args)
					json.dump(cache, open(file_path, "w"), indent="\t")
				return cache

		return new_func
	return decorator
