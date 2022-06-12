import math
from datetime import timedelta

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
			building: Building, recipe: Recipe, resourcesAvailable: dict, produceAll=False, buildingUseLimits: dict[str, int] = None,
			requirementsRecipes: dict[str, tuple[Building, Recipe]] = None, recipesUsed: dict[Recipe, int] = None, buildingsUsed: dict[Building, int] = None
	):
		if buildingUseLimits is None:
			buildingUseLimits = {}
		if requirementsRecipes is None:
			requirementsRecipes = {}
		if recipesUsed is None:
			recipesUsed = {}
		if buildingsUsed is None:
			buildingsUsed = {}
		producedAnything = False
		while True:
			hasRequirements = True
			for inputMaterial in recipe.inputs:
				missing = inputMaterial.amount - resourcesAvailable[inputMaterial.ticker]
				if missing > 0:
					if inputMaterial.ticker not in requirementsRecipes:
						hasRequirements = False
						break
					requirementBuilding, requirementRecipe = requirementsRecipes[inputMaterial.ticker]
					requirementProduceCount = math.ceil(missing / requirementRecipe.getOutputMaterial(inputMaterial.ticker).amount)
					if not all([
						self.sim_produceRecipe(
							requirementBuilding, requirementRecipe, resourcesAvailable, produceAll=False, buildingUseLimits=buildingUseLimits,
							requirementsRecipes=requirementsRecipes, recipesUsed=recipesUsed, buildingsUsed=buildingsUsed
						)
						for i in range(requirementProduceCount)
					]):
						hasRequirements = False
						break
			if not hasRequirements:
				break
			if building not in buildingsUsed:
				buildingsUsed[building] = 1
			else:
				maxUse = buildingUseLimits.get(building.ticker, None)
				if maxUse is not None and buildingsUsed[building] >= maxUse:
					break
				buildingsUsed[building] += 1
			if recipe not in recipesUsed:
				recipesUsed[recipe] = 1
			else:
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

	def getBuildingUseLimitsForRecipesAtSite(self, planet: str, recipes: dict[str, list[str]]):
		buildingUseLimits = {}
		site = self.fio.getMySite(planet)
		for buildingTicker in recipes.keys():
			buildingUseLimits[buildingTicker] = len(site.buildingsOfType(buildingTicker)) * 20
		return buildingUseLimits

	def producibleWithStorageContents(self, planet: str, materialTicker: str, recipes: dict[str, list[str]], buildingUseLimits: dict[str, int] = None):
		"""
		:param planet:
		:param materialTicker: Target material
		:param recipes: {"INC": ["4xHCP 2xGRN 2xMAI = 4xC"], "FRM": ["2xH2O = 4xHCP", "1xH2O = 4xGRN", "4xH2O = 12xMAI"]}
		:param buildingUseLimits: A dict with keys being a building ticker and values of the max amount of times that recipes can be used in that building
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
						print(f"WARNING: Found duplicate recipe for resource `{outputMaterial.material.ticker}`, using first one that was found ({requirementsRecipes[outputMaterial.material.ticker]}). Please avoid duplicate recipes!")
					else:
						requirementsRecipes[outputMaterial.material.ticker] = (building, recipe)
		if len(recipesForTarget) > 1:
			raise Exception("Found multiple recipes for target material, please ensure there is only one recipe for the target material.")
		elif len(recipesForTarget) <= 0:
			raise Exception("Found no recipes for target resource.")
		building, materialRecipe = recipesForTarget[0]
		resources = self.getAvailableResourcesForRecipe(planet, building.ticker, materialRecipe.recipeName)
		resources[material.ticker] = 0
		recipesUsed: dict[Recipe, int] = {}
		buildingsUsed: dict[Building, int] = {}
		self.sim_produceRecipe(
			building, materialRecipe, resources, produceAll=True, buildingUseLimits=buildingUseLimits,
			requirementsRecipes=requirementsRecipes, recipesUsed=recipesUsed, buildingsUsed=buildingsUsed
		)
		return resources, recipesUsed, buildingsUsed

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

	def getProductionTime(self, planet: str, recipes: dict[str, list[str]], recipesUsed: dict[Recipe, int]):
		prodTime = timedelta()
		site = self.fio.getMySite(planet)
		for buildingTicker, buildingRecipes in recipes.items():
			building = self.fio.getBuilding(buildingTicker)
			for buildingRecipe in buildingRecipes:
				recipe = building.recipes[buildingRecipe]
				if recipe in recipesUsed:
					count = recipesUsed[recipe]
					buildingCount = len(site.buildingsOfType(buildingTicker))
					prodTime += recipe.timeDelta * count / buildingCount
		return prodTime

	def getBuildingUsage(self, buildingUseLimits: dict[str, int], buildingsUsed: dict[Building, int]):
		globalBuildingUsage = dict({building: amount / buildingUseLimits[building.ticker] for building, amount in buildingsUsed.items()})
		usageSum = sum(globalBuildingUsage.values())
		if usageSum == 0:
			return dict({k: 0 for k, v in globalBuildingUsage.items()})
		factor = max(globalBuildingUsage.values())
		return dict({k: v / factor for k, v in globalBuildingUsage.items()})

