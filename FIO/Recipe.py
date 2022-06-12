from datetime import timedelta
from typing import TYPE_CHECKING

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
		return hash(({self.amount}, {self.materialTicker}))

	@property
	def ticker(self):
		return self.material.ticker


class Recipe:
	def __init__(self, json: dict, fio: "FIO"):
		self.inputs = [RecipeMaterial(recipeMaterial, fio) for recipeMaterial in json["Inputs"]]
		self.outputs = [RecipeMaterial(recipeMaterial, fio) for recipeMaterial in json["Outputs"]]
		self.timeMs = json.get("DurationMs", json.get("TimeMs", None))
		self.timeDelta = timedelta(milliseconds=self.timeMs)
		self.recipeName = json["RecipeName"]

	def __repr__(self):
		return f"<Recipe `{self.recipeName}`>"

	def __hash__(self):
		return hash(self.recipeName)

	def isMaterialInput(self, ticker: str):
		return any(ticker == material.material.ticker for material in self.inputs)

	def isMaterialOutput(self, ticker: str):
		return any(ticker == material.material.ticker for material in self.outputs)

	def getInputMaterial(self, ticker: str):
		return next((material for material in self.inputs if ticker == material.material.ticker), None)

	def getOutputMaterial(self, ticker: str):
		return next((material for material in self.outputs if ticker == material.material.ticker), None)
