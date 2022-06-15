from datetime import timedelta
from typing import Optional
import requests
import logging

from .FIOExceptions import *
from .jsoncache import jsoncache, ParamOpts


logger = logging.getLogger("FIOApi")


class FIOApi:
	_auth_name: str = None
	API_URL = "https://rest.fnar.net/"

	def __init__(self, key: str):
		self.api_key = key

	def get(self, endpoint: str, body: Optional[dict] = None, exceptions={}, exceptionArgs=(), ignore401=False):
		response = requests.get(
			self.API_URL + endpoint.lstrip("/"),
			headers={
				"Authorization": self.api_key
			},
			json=body
		)
		if response.status_code == 401 and not ignore401:
			raise FIONotAuthenticated(response)
		if response.status_code != 200:
			exception = exceptions.get(response.status_code, None)
			if exception is not None:
				raise exception(response, *exceptionArgs)
			else:
				raise FIOUnknown(response)
		return response

	# def post(self, endpoint: str, body: Optional[dict], ignore401=False):
	# 	response = requests.post(
	# 		self.API_URL + endpoint.lstrip("/"),
	# 		headers={
	# 			"Authorization": self.api_key
	# 		},
	# 		json=body
	# 	)
	# 	if response.status_code == 401 and not ignore401:
	# 		raise FIONotAuthenticated()
	# 	return response

	@property
	def _default_name(self):
		if self._auth_name is None:
			self.auth()
		return self._auth_name

	def auth(self):
		response = self.get("/auth", None, ignore401=True)
		if response.status_code == 200:
			name = response.content.decode()
			self._auth_name = name
			return True, name
		return False, None

	@jsoncache()
	def allbuildings(self):
		logger.info("allbuildings()")
		data = self.get("/building/allbuildings").json()
		for buildingJson in data:
			self.building.cacheValue(buildingJson, buildingJson["Ticker"])
		return data

	@jsoncache(paramOpts=[ParamOpts(upper=True)])
	def building(self, ticker: str):
		logger.info(f"building(\"{ticker}\")")
		return self.get(
			f"/building/{ticker}",
			exceptions={204: FIOBuildingNotFound},
			exceptionArgs=(ticker,)
		).json()

	@jsoncache()
	def allplanets(self):
		logger.info("allplanets()")
		data = self.get("/planet/allplanets/full").json()
		for planetJson in data:
			self.planet.cacheValue(planetJson, planetJson["PlanetId"])
			self.planet.cacheValue(planetJson, planetJson["PlanetNaturalId"])
			self.planet.cacheValue(planetJson, planetJson["PlanetName"])
		return data

	@jsoncache()
	def planet(self, planet: str):
		"""
		:param planet: 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		logger.info(f"planet(\"{planet}\")")
		return self.get(
			f"/planet/{planet}",
			exceptions={204: FIOPlanetNotFound},
			exceptionArgs=(planet,)
		).json()

	@jsoncache()
	def allmaterials(self):
		logger.info("allmaterials()")
		data = self.get("/material/allmaterials").json()
		for materialJson in data:
			self.material.cacheValue(materialJson, materialJson["Ticker"])
		return data

	@jsoncache(paramOpts=[ParamOpts(upper=True)])
	def material(self, ticker: str):
		logger.info(f"material(\"{ticker}\")")
		return self.get(
			f"/material/{ticker}",
			exceptions={204: FIOMaterialNotFound},
			exceptionArgs=(ticker,)
		).json()

	@jsoncache()
	def allrecipes(self):
		logger.info("allrecipes()")
		data = self.get("/recipes/allrecipes").json()
		for recipeJson in data:
			self.recipes.cacheValue(recipeJson, recipeJson["RecipeName"])
		return data

	@jsoncache()
	def recipes(self, ticker: str):
		logger.info(f"recipes(\"{ticker}\")")
		return self.get(f"/recipes/{ticker}").json()

	@jsoncache(paramOpts=[ParamOpts(upper=True)], invalidateTime=timedelta(hours=6))
	def sites(self, username: str):
		logger.info(f"sites(\"{username}\")")
		return self.get(f"/sites/{username.upper()}").json()

	def mysites(self):
		return self.sites(self._default_name)

	@jsoncache(paramOpts=[ParamOpts(upper=True)], invalidateTime=timedelta(hours=6))
	def site(self, username: str, planet: str):
		logger.info(f"sites(\"{username}\", \"{planet}\")")
		return self.get(f"/sites/{username.upper()}/{planet}").json()

	def mysite(self, planet: str):
		return self.site(self._default_name, planet)

	@jsoncache(paramOpts=[ParamOpts(upper=True)], invalidateTime=timedelta(minutes=15))
	def storages(self, username: str):
		logger.info(f"storages(\"{username}\")")
		return self.get(f"/storage/{username.upper()}").json()

	def mystorages(self):
		return self.storages(self._default_name)

	@jsoncache(paramOpts=[ParamOpts(upper=True)], invalidateTime=timedelta(minutes=15))
	def storage(self, username: str, storageDescription: str):
		"""
		:param storageDescription: 'StorageId', 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		logger.info(f"storage(\"{username}\", \"{storageDescription}\")")
		return self.get(f"/storage/{username.upper()}/{storageDescription}").json()

	def mystorage(self, storageDescription: str):
		"""
		:param storageDescription: 'StorageId', 'PlanetId', 'PlanetNaturalId' or 'PlanetName'
		"""
		return self.storage(self._default_name, storageDescription)

	@jsoncache(paramOpts=[ParamOpts(upper=True), ParamOpts(upper=True)], invalidateTime=timedelta(minutes=15))
	def exchange(self, material: str, commodityExchange: str):
		logger.info(f"exchange(\"{material}\", \"{commodityExchange}\")")
		return self.get(f"/exchange/{material.upper()}.{commodityExchange.upper()}").json()

	@jsoncache(paramOpts=[ParamOpts(upper=True)])
	def exchangestation(self):
		logger.info(f"exchangestation()")
		return self.get(f"/exchange/station").json()
