import re
import sys
from typing import TYPE_CHECKING, Optional

from .System import System
from .Planet import Planet

if TYPE_CHECKING:
	from .FIO import FIO


class Location:
	LOCATION_STR_REGEX = re.compile(r"(\w+) \(([\w-]+)\) - (?:(\w+) \(([\w-]+)\))?(STATION)?")

	def __init__(self, fio: "FIO"):
		self.fio = fio

		self.system: Optional[System] = None
		self.planet: Optional[Planet] = None
		self.atStation = False
		self.inFlight = None

	def __repr__(self):
		return f"<Location `{self.locationString()}`>"

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __hash__(self):
		return hash((self.__class__, self.system, self.planet, self.atStation))

	def locationString(self, ignoreCustom=False):
		parts = []
		if self.system is not None:
			parts.append(f"{self.system.name} ({self.system.naturalId})")
		if self.planet is not None:
			parts.append(f"{self.planet.planetName} ({self.planet.planetNaturalId})")
		if self.atStation:
			if not ignoreCustom and self.system is not None:
				parts.append(f"{self.system.name} Station ({self.system.name})")
			else:
				parts.append("STATION")
		# Custom that are not in the FIO Api
		if not ignoreCustom:
			if self.inFlight:
				parts.append("FLIGHT")
			if len(parts) <= 0:
				parts.append("NOWHERE")
		return " - ".join(parts)

	@classmethod
	def fromLocationString(cls, fio: "FIO", locationStr: str):
		location = cls(fio)
		match = cls.LOCATION_STR_REGEX.match(locationStr)
		if match is None:
			return location
		systemName, systemNaturalId, planetName, planetNaturalId, otherPlaceName = match.groups()
		if systemNaturalId is not None:
			location.system = fio.getSystem(systemNaturalId)
		if planetNaturalId is not None:
			location.planet = fio.getPlanet(planetNaturalId)
		if otherPlaceName == "STATION":
			location.atStation = True
		elif otherPlaceName is not None:
			print(f"WARNING: missing handler for location string otherPlaceName {otherPlaceName:r}", file=sys.stderr)
		return location
