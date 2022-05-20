from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .FIO import FIO


from .Recipe import Recipe


class Building:
	def __init__(self, json: dict, fio: "FIO"):
		self.buildingCosts = {}
		for itemJson in json["BuildingCosts"]:
			ticker = itemJson["CommodityTicker"]
			self.buildingCosts[ticker] = fio.getMaterial(ticker)
		self.recipes: dict[str, Recipe] = {}
		for recipe in json["Recipes"]:
			if len(recipe["Outputs"]) > 0:
				self.recipes[recipe["RecipeName"]] = Recipe(recipe, fio)

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
		return hash(self.ticker)
