from datetime import datetime
from typing import TYPE_CHECKING
from dateutil.parser import isoparse

from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class System:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio
		self._planets = None

		self.connections = json["Connections"]
		self.systemId = json["SystemId"]
		self.name = json["Name"]
		self.naturalId = json["NaturalId"]
		self.type = json["Type"]
		self.positionX = json["PositionX"]
		self.positionY = json["PositionY"]
		self.positionZ = json["PositionZ"]
		self.sectorId = json["SectorId"]
		self.subSectorId = json["SubSectorId"]
		self.userNameSubmitted = json["UserNameSubmitted"]
		self.timestamp = json["Timestamp"]
		self._luminosity = None
		self._mass = None
		self._massSol = None
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
				# This may contain duplicate planets with different values (PlanetName, PlanetId etc)
				for result in self.fio.api.planet.speedQuery("SystemId", self.systemId):
					planet = self.fio.getPlanet(result["planet"])
					self._planets[planet.planetId] = planet  # This will remove duplicates
		return self._planets
