from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.parser import isoparse

from .Material import Material

if TYPE_CHECKING:
	from .FIO import FIO


from .Recipe import Recipe


class BuildingRecipe(Recipe):
	def __init__(self, json: dict, fio: "FIO", building: "Building"):
		super().__init__(json, fio)
		self.building = building


class Building:
	def __init__(self, json: dict, fio: "FIO"):
		self.buildingCosts = {}
		for itemJson in json["BuildingCosts"]:
			ticker = itemJson["CommodityTicker"]
			amount = itemJson["Amount"]
			self.buildingCosts[fio.getMaterial(ticker)] = amount
		self.recipes: dict[str, Recipe] = {}
		for recipeJson in json["Recipes"]:
			if len(recipeJson["Outputs"]) > 0:
				self.recipes[recipeJson["RecipeName"]] = BuildingRecipe(recipeJson, fio, self)

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
		
	def __repr__(self):
		return f"<Building `{self.ticker}`>"

	def __hash__(self):
		return hash((self.__class__, self.ticker))

	@property
	def timedelta(self):
		return datetime.utcnow() - isoparse(self.timestamp)

	def formatTimedelta(self):
		delta = self.timedelta
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		return f"{days}days {hours}h {minutes}m"

	def recipesOutputMaterial(self, material: Material):
		return list(recipe for recipe in self.recipes.values() if recipe.isMaterialOutput(material))

	def recipesInputMaterial(self, material: Material):
		return list(recipe for recipe in self.recipes.values() if recipe.isMaterialInput(material))
