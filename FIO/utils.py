import re
from datetime import timedelta


LOCATION_REGEX = re.compile(r"(\w+) \(([\w-]+)\) - (?:(\w+) \(([\w-]+)\))?(STATION)?")


def formatTimedelta(timeDelta: timedelta, alwaysIncludeSeconds=False):
	days, hours, minutes = timeDelta.days, timeDelta.seconds // 3600, timeDelta.seconds // 60 % 60
	seconds = timeDelta.seconds - hours*3600 - minutes*60
	parts = []
	if days > 0:
		parts.append(f"{days}days")
	if hours > 0:
		parts.append(f"{hours}h")
	if minutes > 0:
		parts.append(f"{minutes}m")
	if alwaysIncludeSeconds or days <= 0:
		parts.append(f"{seconds}s")
	return " ".join(parts)
