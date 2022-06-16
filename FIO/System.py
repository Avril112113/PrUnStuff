from datetime import datetime
from typing import TYPE_CHECKING, Optional
from dateutil.parser import isoparse

from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class System:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio
		self._planets = None

		self.connections = json["Connections"]
		self.systemId: str = json["SystemId"]
		self.name: str = json["Name"]
		self.naturalId: str = json["NaturalId"]
		self.type: str = json["Type"]
		self.positionX: float = json["PositionX"]
		self.positionY: float = json["PositionY"]
		self.positionZ: float = json["PositionZ"]
		self.sectorId: str = json["SectorId"]
		self.subSectorId: str = json["SubSectorId"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]
		self._luminosity: Optional[float] = None
		self._mass: Optional[float] = None
		self._massSol: Optional[float] = None
		self._update(json)

	def __repr__(self):
		return f"<System `{self.name}`>"

	def __hash__(self):
		return hash((self.__class__, self.systemId))

	def _update(self, json: dict):
		if "Luminosity" in json:
			self._luminosity = json["Luminosity"]
		if "Mass" in json:
			self._mass = json["Mass"]
		if "MassSol" in json:
			self._massSol = json["MassSol"]

	@property
	def luminosity(self):
		if self._luminosity is None:
			self._update(self.fio.api.systemstarsstar(self.systemId))
		return self._luminosity

	@property
	def mass(self):
		if self._mass is None:
			self._update(self.fio.api.systemstarsstar(self.systemId))
		return self._mass

	@property
	def massSol(self):
		if self._massSol is None:
			self._update(self.fio.api.systemstarsstar(self.systemId))
		return self._massSol

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)

	@property
	def planets(self):
		if self._planets is None:
			self._planets = {}
			if not self.fio.api.allplanets.isCached():
				for planet in self.fio.getAllPlanets():
					if planet.systemId == self.systemId:
						self._planets[planet.planetId] = planet
			else:
				for result in self.fio.api.planet.speedQuery("SystemId", self.systemId):
					planet = self.fio.getPlanet(result["planet"])
					self._planets[planet.planetId] = planet
		return self._planets

	@property
	def sector(self):
		return self.fio.getWorldSector(self.sectorId)
