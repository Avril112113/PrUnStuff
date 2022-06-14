# for some reason `@cache` was nuking typing info :/
from functools import cache, lru_cache

from .FIOApi import FIOApi
from .Material import Material
from .Building import Building
from .Planet import Planet
from .Storage import Storage
from .Recipe import Recipe
from .Site import Site
from .Exchange import Exchange


class FIO:
	"""
	Interface for PrUn data, provided by FIO rest API
	Uses `FIOApi` class, but provides a more convenient interface
	"""
	# A developer note: This interface HEAVILY relies on the `FIOApi` caching of it's api calls

	def __init__(self, key: str):
		self.api = FIOApi(key)

	@lru_cache
	def getMaterial(self, ticker: str):
		return Material(self.api.material(ticker.upper()), self)

	@lru_cache
	def getBuilding(self, ticker: str):
		return Building(self.api.building(ticker.upper()), self)

	@lru_cache
	def getRecipes(self, ticker: str):
		return [Recipe(recipe, self) for recipe in self.api.recipes(ticker)]

	@lru_cache
	def getPlanet(self, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Planet(self.api.planet(planet), self)

	@lru_cache
	def getSite(self, username: str, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Site(self.api.site(username, planet), self)

	@lru_cache
	def getMySite(self, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Site(self.api.mysite(planet), self)

	def clearSiteCache(self):
		self.api.site.clearCache()  # Method from jsoncache.py

	@lru_cache
	def getStorage(self, username: str, storageDescription: str):
		"""
		:param storageDescription: 'StorageId', 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Storage(self.api.storage(username, storageDescription), self)

	@lru_cache
	def getMyStorage(self, storageDescription: str):
		"""
		:param storageDescription: 'StorageId', 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return Storage(self.api.mystorage(storageDescription), self)

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
