from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.parser import isoparse

from .Material import Material
from .Recipe import Recipe
from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class Building:
	def __init__(self, json: dict, fio: "FIO"):
		self.buildingCosts = {}
		for itemJson in json["BuildingCosts"]:
			ticker = itemJson["CommodityTicker"]
			amount = itemJson["Amount"]
			self.buildingCosts[fio.getMaterial(ticker)] = amount
		self.recipes: dict[str, Recipe] = {}

		self.name = json["Name"]
		self.ticker = json["Ticker"]
		self.expertise = json["Expertise"]
		self.pioneers = json["Pioneers"]
		self.settlers = json["Settlers"]
		self.technicians = json["Technicians"]
		self.engineers = json["Engineers"]
		self.scientists = json["Scientists"]
		self.areaCost = json["AreaCost"]
		self.userNameSubmitted = json["UserNameSubmitted"]
		self.timestamp = json["Timestamp"]

		for recipeJson in json["Recipes"]:
			if len(recipeJson["Outputs"]) > 0:
				self.recipes[recipeJson["RecipeName"]] = Recipe(recipeJson, fio, building=self)
		
	def __repr__(self):
		return f"<Building `{self.ticker}`>"

	def __hash__(self):
		return hash((self.__class__, self.ticker))

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)

	def recipesOutputMaterial(self, material: Material):
		return list(recipe for recipe in self.recipes.values() if recipe.isMaterialOutput(material))

	def recipesInputMaterial(self, material: Material):
		return list(recipe for recipe in self.recipes.values() if recipe.isMaterialInput(material))
