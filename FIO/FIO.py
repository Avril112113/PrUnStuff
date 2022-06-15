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
	def getBuilding(self, ticker: str):
		return Building(self.api.building(ticker.upper()), self)

	@lru_cache
	def getRecipe(self, ticker: str):
		return Recipe(self.api.recipes(ticker), self)

	@lru_cache
	def getPlanet(self, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Planet(self.api.planet(planet), self)

	@lru_cache
	def getSite(self, username: Optional[str], planet: str):
		"""
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
		return [Ship(ship, self, username, data["UserNameSubmitted"], data["Timestamp"]) for ship in data["Ships"]]

	@lru_cache
	def getMyShips(self):
		return self.getShips(None)

	@lru_cache
	def getShip(self, username: Optional[str], idOrRegistration: str):
		for ship in self.getShips(username):
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
	def getFlights(self, username: Optional[str]):
		username = self.api.default_name if username is None else username
		data = self.api.flights(username)
		return [Flight(flight, self, username, data["UserNameSubmitted"], data["Timestamp"]) for flight in data["Flights"]]

	def getMyFlights(self):
		return self.getFlights(None)

	@lru_cache
	def getFlight(self, username: Optional[str], idOrShipIdOrShipRegistration: str):
		for flight in self.getFlights(username):
			if \
				flight.flightId == idOrShipIdOrShipRegistration or \
				flight.ship.shipId == idOrShipIdOrShipRegistration or \
				flight.ship.registration == idOrShipIdOrShipRegistration:
				return flight
		return None

	def getMyFlight(self, idOrRegistration: str):
		return self.getFlight(None, idOrRegistration)
