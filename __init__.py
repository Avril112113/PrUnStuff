import math
import sys

from PrUnStuff.FIO import *


class PrUnStuff:
	def __init__(self, fio_key: str):
		self.fio = FIO(fio_key)

	def getAvailableResourcesForRecipe(self, planet: str, building: str, recipe: str, resourcesAvailable: dict = None):
		"""Gets the amount of resources available for a recipe, recursively, to all possible recipe paths that could aid in making this item"""
		storage = self.fio.getMyStorage(planet)
		site = self.fio.getMySite(planet)
		building = self.fio.getBuilding(building)
		recipe = building.recipes[recipe]
		assert recipe is not None, "Recipe not found for building"
		resourcesAvailable = resourcesAvailable if resourcesAvailable is not None else {}
		for requirement in recipe.inputs:
			resourcesAvailable[requirement.ticker] = storage.getItemAmount(requirement.ticker)
			for siteBuilding in site.buildings:
				for buildingRecipe in siteBuilding.building.recipes.values():
					if buildingRecipe.isMaterialOutput(requirement.ticker):
						self.getAvailableResourcesForRecipe(planet, siteBuilding.building.ticker, buildingRecipe.recipeName, resourcesAvailable)
		return resourcesAvailable

	def sim_produceRecipe(
			self,
			recipe: Recipe, resourcesAvailable: dict, produceAll=False, maxRecipeUse=sys.maxsize,
			requirementsRecipes: dict[str, Recipe] = {}, recipesUsed={}
	):
		producedAnything = False
		while True:
			hasRequirements = True
			for inputMaterial in recipe.inputs:
				missing = inputMaterial.amount - resourcesAvailable[inputMaterial.ticker]
				if missing > 0:
					requirementRecipe = requirementsRecipes.get(inputMaterial.ticker, None)
					if requirementRecipe is None:
						hasRequirements = False
						break
					requirementProduceCount = math.ceil(missing / requirementRecipe.getOutputMaterial(inputMaterial.ticker).amount)
					if not all([
						self.sim_produceRecipe(requirementRecipe, resourcesAvailable, produceAll=False, requirementsRecipes=requirementsRecipes, recipesUsed=recipesUsed)
						for i in range(requirementProduceCount)
					]):
						hasRequirements = False
						break
			if not hasRequirements:
				break
			if recipe not in recipesUsed:
				recipesUsed[recipe] = 1
			else:
				if recipesUsed[recipe] + 1 >= maxRecipeUse:
					break
				recipesUsed[recipe] += 1
			for recipeMaterial in recipe.inputs:
				resourcesAvailable[recipeMaterial.material.ticker] -= recipeMaterial.amount
			for recipeMaterial in recipe.outputs:
				if recipeMaterial.material.ticker not in resourcesAvailable:
					resourcesAvailable[recipeMaterial.material.ticker] = 0
				resourcesAvailable[recipeMaterial.material.ticker] += recipeMaterial.amount
			producedAnything = True
			if not produceAll:
				break
		return producedAnything

	def producibleWithStorageContents(self, planet: str, materialTicker: str, recipes: dict[str, list[str]], maxRecipeUse=sys.maxsize):
		"""
		:param planet:
		:param materialTicker: Target material
		:param recipes: {"INC": ["4xHCP 2xGRN 2xMAI = 4xC"], "FRM": ["2xH2O = 4xHCP", "1xH2O = 4xGRN", "4xH2O = 12xMAI"]}
		:param maxRecipeUse: The max amount any recipe can be used, useful for limiting due to order size maxed at 20
		"""
		material = self.fio.getMaterial(materialTicker)
		recipesForTarget = []
		requirementsRecipes = {}
		for buildingTicker, recipeNames in recipes.items():
			for recipeName in recipeNames:
				building = self.fio.getBuilding(buildingTicker)
				recipe = building.recipes.get(recipeName, None)
				if recipe is None:
					raise Exception(f"Invalid recipe {buildingTicker} -> {recipeName}")
				if recipe.isMaterialOutput(material.ticker):
					recipesForTarget.append((building, recipe))
				for outputMaterial in recipe.outputs:
					if outputMaterial.material.ticker in requirementsRecipes:
						print(f"WARNING: Found duplicate recipe for resource `{outputMaterial.material.ticker}`, using first one that was found. Please avoid duplicate recipes!")
					else:
						requirementsRecipes[outputMaterial.material.ticker] = recipe
		if len(recipesForTarget) > 1:
			raise Exception("Found multiple recipes for target material, please ensure there is only one recipe for the target material.")
		elif len(recipesForTarget) <= 0:
			raise Exception("Found no recipes for target resource.")
		building, materialRecipe = recipesForTarget[0]
		resources = self.getAvailableResourcesForRecipe(planet, building.ticker, materialRecipe.recipeName)
		resources[material.ticker] = 0
		recipesUsed = {}
		self.sim_produceRecipe(materialRecipe, resources, produceAll=True, requirementsRecipes=requirementsRecipes, maxRecipeUse=maxRecipeUse, recipesUsed=recipesUsed)
		return resources, recipesUsed

	def getConsumedProducedFromRecipesUsed(self, recipesUsed: dict[Recipe, int]):
		consumed = {}
		produced = {}
		for recipe, count in recipesUsed.items():
			for inputMaterial in recipe.inputs:
				if inputMaterial.ticker not in consumed:
					consumed[inputMaterial.ticker] = inputMaterial.amount * count
				else:
					consumed[inputMaterial.ticker] += inputMaterial.amount * count
			for outputMaterial in recipe.outputs:
				if outputMaterial.ticker not in produced:
					produced[outputMaterial.ticker] = outputMaterial.amount * count
				else:
					produced[outputMaterial.ticker] += outputMaterial.amount * count
		return consumed, produced
