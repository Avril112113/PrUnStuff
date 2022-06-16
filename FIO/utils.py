import re
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .FIO import FIO


LOCATION_REGEX = re.compile(r"(\w+) \(([\w-]+)\) - (?:(\w+) \(([\w-]+)\))?(STATION)?")


def parseLocation(fio: "FIO", location: str):
	match = LOCATION_REGEX.match(location)
	if match is None:
		return None, None, None
	systemName, systemNaturalId, planetName, planetNaturalId, otherPlaceName = match.groups()
	system = None
	planet = None
	if systemNaturalId is not None:
		system = fio.getSystem(systemNaturalId)
	if planetNaturalId is not None:
		planet = fio.getPlanet(planetNaturalId)
	return system, planet, otherPlaceName


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
