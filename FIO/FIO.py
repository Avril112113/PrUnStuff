# for some reason `@cache` was nuking typing info :/
from functools import cache, lru_cache
from typing import Optional

from .FIOApi import FIOApi
from .Material import Material
from .Building import Building
from .Planet import Planet
from .Storage import Storage
from .Recipe import Recipe
from .Site import Site
from .Exchange import Exchange
from .Ship import Ship
from .Flight import Flight
from .System import System
from .WorldSector import WorldSector


class FIO:
	"""
	Interface for PrUn data, provided by FIO rest API
	Uses `FIOApi` class, but provides a more convenient interface
	"""

	def __init__(self, key: str):
		self.api = FIOApi(key)

	@lru_cache
	def getMaterial(self, ticker: str):
		return Material(self.api.material(ticker.upper()), self)

	@lru_cache
	def getAllMaterials(self):
		return list(self.getMaterial(materialJson["Ticker"]) for materialJson in self.api.allmaterials())

	@lru_cache
	def getBuilding(self, ticker: str):
		return Building(self.api.building(ticker.upper()), self)

	@lru_cache
	def getAllBuildings(self):
		# This is done because `Building` loads materials from the FIO API, which is every material if we load all buildings
		# This also speeds stuff up a lot
		self.getAllMaterials()
		return list(self.getBuilding(buildingJson["Ticker"]) for buildingJson in self.api.allbuildings())

	@lru_cache
	def getRecipe(self, recipeName: str):
		return Recipe(self.api.recipes(recipeName), self)

	@lru_cache
	def getAllRecipes(self):
		return list(self.getRecipe(recipeJson["RecipeName"]) for recipeJson in self.api.allrecipes())

	@lru_cache
	def getPlanet(self, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Planet(self.api.planet(planet), self)

	@lru_cache
	def getAllPlanets(self):
		return list(self.getPlanet(planetJson["PlanetId"]) for planetJson in self.api.allplanets())

	@lru_cache
	def getSite(self, username: Optional[str], planet: str):
		"""
		:param username:
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		username = self.api.default_name if username is None else username
		data = self.api.site(username, planet)
		return Site(data, self, username)

	def getMySite(self, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return self.getSite(None, planet)

	def clearSiteCache(self):
		self.api.site.clearCache()  # Method from jsoncache.py

	@lru_cache
	def getStorage(self, username: Optional[str], storageDescription: str):
		"""
		:param username:
		:param storageDescription: 'StorageId', 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		username = self.api.default_name if username is None else username
		data = self.api.storage(username, storageDescription)
		return Storage(data, self, username)

	def getMyStorage(self, storageDescription: str):
		"""
		:param storageDescription: 'StorageId', 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return self.getStorage(None, storageDescription)

	def clearStorageCache(self):
		self.api.storage.clearCache()  # Method from jsoncache.py

	@lru_cache
	def getExchanges(self) -> dict[str, Exchange]:
		return {exchange["ComexCode"]: Exchange(exchange, self) for exchange in self.api.exchangestation()}

	@lru_cache
	def getExchange(self, exchange: str):
		return self.getExchanges().get(exchange, None)

	def clearExchangeCache(self):
		"""
		You are probably looking to use `clearMaterialExchangeCache()` instead...
		This method clears the cache for the existing stations, not the contents.
		"""
		self.api.exchangestation.clearCache()  # Method from jsoncache.py

	def clearMaterialExchangeCache(self):
		self.api.exchange.clearCache()  # Method from jsoncache.py

	@lru_cache
	def getShips(self, username: Optional[str]):
		username = self.api.default_name if username is None else username
		data = self.api.ships(username)
		return {ship["ShipId"]: Ship(ship, self, username, data["UserNameSubmitted"], data["Timestamp"]) for ship in data["Ships"]}

	@lru_cache
	def getMyShips(self):
		return self.getShips(None)

	@lru_cache
	def getShip(self, username: Optional[str], idOrRegistration: str) -> Optional[Ship]:
		for ship in self.getShips(username).values():
			if ship.shipId == idOrRegistration or ship.registration == idOrRegistration:
				return ship
		return None

	def getMyShip(self, idOrRegistration: str):
		return self.getShip(None, idOrRegistration)

	@lru_cache
	def getShipsFuel(self, username: Optional[str]):
		username = self.api.default_name if username is None else username
		data = self.api.shipsfuel(username)
		return [Storage(storage, self, username) for storage in data]

	def getMyShipsFuel(self):
		return self.getShipsFuel(None)

	@lru_cache
	def getShipFuel(self, username: Optional[str], idOrRegistration: str):
		for storage in self.getShipsFuel(username):
			if storage.addressableId == idOrRegistration or storage.name == idOrRegistration:
				return storage
		return None

	def getMyShipFuel(self, idOrRegistration: str):
		return self.getShipFuel(None, idOrRegistration)

	@lru_cache
	def getFlights(self, username: Optional[str]) -> dict[str, Flight]:
		username = self.api.default_name if username is None else username
		data = self.api.flights(username)
		return {flight["FlightId"]: Flight(flight, self, username, data["UserNameSubmitted"], data["Timestamp"]) for flight in data["Flights"]}

	def getMyFlights(self):
		return self.getFlights(None)

	@lru_cache
	def getFlight(self, username: Optional[str], idOrShipIdOrShipRegistration: str):
		for flight in self.getFlights(username).values():
			if \
				flight.flightId == idOrShipIdOrShipRegistration or \
				flight.ship.shipId == idOrShipIdOrShipRegistration or \
				flight.ship.registration == idOrShipIdOrShipRegistration:
				return flight
		return None

	def getMyFlight(self, idOrRegistration: str):
		return self.getFlight(None, idOrRegistration)

	@lru_cache
	def getSystems(self):
		return list(System(systemJson, self) for systemJson in self.api.systemstars())

	@lru_cache
	def getSystemsMap(self):
		systemsMap = {}
		for systemJson in self.api.systemstars():
			system = System(systemJson, self)
			systemsMap[system.systemId] = system
			systemsMap[system.name] = system
			systemsMap[system.naturalId] = system
		return systemsMap

	@lru_cache
	def getSystem(self, systemId: str):
		"""
		:param systemId: SystemId, SystemName or SystemNaturalId
		"""
		return self.getSystemsMap().get(systemId, None)

	@lru_cache
	def getWorldSectors(self):
		return {worldSectorJson["SectorId"]: WorldSector(worldSectorJson, self) for worldSectorJson in self.api.systemstarsworldsectors()}

	@lru_cache
	def getWorldSector(self, sectorId: str):
		return self.getWorldSectors().get(sectorId, None)

