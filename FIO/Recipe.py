from datetime import timedelta
from typing import TYPE_CHECKING

from .Material import Material

if TYPE_CHECKING:
	from .FIO import FIO


class RecipeMaterial:
	def __init__(self, json: dict, fio: "FIO"):
		# TODO: support `allrecipes` as it probably doesn't work
		self.materialTicker = json.get("CommodityTicker", json.get("Ticker", None))
		self.material = fio.getMaterial(self.materialTicker)
		self.weight = json.get("Weight", None)
		self.volume = json.get("Volume", None)
		self.amount = json["Amount"]

	def __repr__(self):
		return f"<RecipeMaterial `{self.amount}x{self.materialTicker}`>"

	def __hash__(self):
		return hash((self.__class__, self.amount, self.materialTicker))

	@property
	def ticker(self):
		return self.material.ticker


class Recipe:
	def __init__(self, json: dict, fio: "FIO"):
		self.inputs = {}
		for recipeInputJson in json["Inputs"]:
			recipeInput = RecipeMaterial(recipeInputJson, fio)
			self.inputs[recipeInput.material] = recipeInput
		self.outputs = {}
		for recipeOutputJson in json["Outputs"]:
			recipeOutput = RecipeMaterial(recipeOutputJson, fio)
			self.outputs[recipeOutput.material] = recipeOutput
		self.timeMs = json.get("DurationMs", json.get("TimeMs", None))
		self.timeDelta = timedelta(milliseconds=self.timeMs)
		self.recipeName = json["RecipeName"]

	def __repr__(self):
		return f"<Recipe `{self.recipeName}`>"

	def __hash__(self):
		return hash((self.__class__, self.recipeName))

	def isMaterialInput(self, material: Material):
		return any(material == recipeInput.material for recipeInput in self.inputs.values())

	def isMaterialOutput(self, material: Material):
		return any(material == recipeOutput.material for recipeOutput in self.outputs.values())
