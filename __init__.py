import math
import sys
from datetime import timedelta

from .FIO import *


class PrUnStuff:
	def __init__(self, fio_key: str):
		self.fio = FIO(fio_key)

	def getAvailableResourcesForRecipe(self, planet: Planet, recipe: Recipe, resourcesAvailable: dict[Material, int] = None):
		"""Gets the amount of resources available for a recipe, recursively, to all possible recipe paths that could aid in making this item"""
		storage = self.fio.getMyStorage(planet.planetId)
		site = self.fio.getMySite(planet.planetId)
		resourcesAvailable = resourcesAvailable if resourcesAvailable is not None else {}
		for requirement in recipe.inputs.values():
			resourcesAvailable[requirement.material] = storage.getItemAmount(requirement.material)
			for siteBuilding in site.buildings:
				for recipe in siteBuilding.building.recipes.values():
					if recipe.isMaterialOutput(requirement.material):
						self.getAvailableResourcesForRecipe(planet, recipe, resourcesAvailable)
		return resourcesAvailable

	def sim_produceRecipe(
			self,
			recipe: Recipe, resourcesAvailable: dict[Material, int], produceAll=False, buildingUseLimits: dict[Building, int] = None,
			requirementsRecipes: dict[Material, Recipe] = None, recipesUsed: dict[Recipe, int] = None, buildingsUsed: dict[Building, int] = None
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
			for inputMaterial in recipe.inputs.values():
				missing = inputMaterial.amount - resourcesAvailable[inputMaterial.material]
				if missing > 0:
					if inputMaterial.material not in requirementsRecipes:
						hasRequirements = False
						break
					requirementRecipe = requirementsRecipes[inputMaterial.material]
					requirementProduceCount = math.ceil(missing / requirementRecipe.outputs[inputMaterial.material].amount)
					if not all([
						self.sim_produceRecipe(
							requirementRecipe, resourcesAvailable, produceAll=False, buildingUseLimits=buildingUseLimits,
							requirementsRecipes=requirementsRecipes, recipesUsed=recipesUsed, buildingsUsed=buildingsUsed
						)
						for i in range(requirementProduceCount)
					]):
						hasRequirements = False
						break
			if not hasRequirements:
				break
			if recipe.building not in buildingsUsed:
				buildingsUsed[recipe.building] = 1
			else:
				maxUse = buildingUseLimits.get(recipe.building, None)
				if maxUse is not None and buildingsUsed[recipe.building] >= maxUse:
					break
				buildingsUsed[recipe.building] += 1
			if recipe not in recipesUsed:
				recipesUsed[recipe] = 1
			else:
				recipesUsed[recipe] += 1
			for recipeMaterial in recipe.inputs.values():
				resourcesAvailable[recipeMaterial.material] -= recipeMaterial.amount
			for recipeMaterial in recipe.outputs.values():
				if recipeMaterial.material not in resourcesAvailable:
					resourcesAvailable[recipeMaterial.material] = 0
				resourcesAvailable[recipeMaterial.material] += recipeMaterial.amount
			producedAnything = True
			if not produceAll:
				break
		return producedAnything

	def getBuildingUseLimitsForRecipesAtSite(self, planet: Planet, recipes: list[Recipe]):
		buildingUseLimits = {}
		site = self.fio.getMySite(planet.planetId)
		for recipe in recipes:
			buildingUseLimits[recipe.building] = len(site.buildingsOfType(recipe.building)) * 20
		return buildingUseLimits

	def producibleWithStorageContents(self, planet: Planet, material: Material, recipes: list[Recipe], buildingUseLimits: dict[Building, int] = None):
		"""
		:param planet:
		:param material: Target material
		:param recipes:
		:param buildingUseLimits: A dict with keys being a building ticker and values of the max amount of times that recipes can be used in that building
		"""
		recipesForTarget = []
		requirementsRecipes = {}
		for recipe in recipes:
			if recipe.isMaterialOutput(material):
				recipesForTarget.append(recipe)
			for outputMaterial in recipe.outputs.values():
				if outputMaterial.material in requirementsRecipes:
					print(f"WARNING: Found duplicate recipe for resource `{outputMaterial.material.ticker}`, using first one that was found ({requirementsRecipes[outputMaterial.material.ticker]}). Please avoid duplicate recipes!")
				else:
					requirementsRecipes[outputMaterial.material] = recipe
		if len(recipesForTarget) > 1:
			raise Exception("Found multiple recipes for target material, please ensure there is only one recipe for the target material.")
		elif len(recipesForTarget) <= 0:
			raise Exception("Found no recipes for target resource.")
		recipe = recipesForTarget[0]
		resources = self.getAvailableResourcesForRecipe(planet, recipe)
		resources[material] = 0
		recipesUsed: dict[Recipe, int] = {}
		buildingsUsed: dict[Building, int] = {}
		self.sim_produceRecipe(
			recipe, resources, produceAll=True, buildingUseLimits=buildingUseLimits,
			requirementsRecipes=requirementsRecipes, recipesUsed=recipesUsed, buildingsUsed=buildingsUsed
		)
		return resources, recipesUsed, buildingsUsed

	def getConsumedProducedFromRecipesUsed(self, recipesUsed: dict[Recipe, int]):
		consumed = {}
		produced = {}
		for recipe, count in recipesUsed.items():
			for inputMaterial in recipe.inputs.values():
				if inputMaterial.ticker not in consumed:
					consumed[inputMaterial] = inputMaterial.amount * count
				else:
					consumed[inputMaterial] += inputMaterial.amount * count
			for outputMaterial in recipe.outputs.values():
				if outputMaterial not in produced:
					produced[outputMaterial] = outputMaterial.amount * count
				else:
					produced[outputMaterial] += outputMaterial.amount * count
		return consumed, produced

	def getProductionTime(self, planet: Planet, recipes: list[Recipe], recipesUsed: dict[Recipe, int]):
		prodTime = timedelta()
		site = self.fio.getMySite(planet.planetId)
		for recipe in recipes:
			if recipe in recipesUsed:
				count = recipesUsed[recipe]
				buildingCount = len(site.buildingsOfType(recipe.building))
				prodTime += recipe.timeDelta * count / buildingCount
		return prodTime

	def getBuildingUsage(self, buildingUseLimits: dict[Building, int], buildingsUsed: dict[Building, int]):
		globalBuildingUsage = dict({building: amount / buildingUseLimits[building] for building, amount in buildingsUsed.items()})
		usageSum = sum(globalBuildingUsage.values())
		if usageSum == 0:
			return dict({k: 0 for k, v in globalBuildingUsage.items()})
		factor = max(globalBuildingUsage.values())
		return dict({k: v / factor for k, v in globalBuildingUsage.items()})

	def estimateBuildingCost(self, building: Building, exchange: Exchange, planet: Planet, storage: Storage = None):
		"""
		:param building:
		:param exchange:
		:param planet:
		:param storage: If supplied, it will take into account the storage
		:return: -1 if a required material is not available to be bought.
		"""
		cost = 0
		materialCosts = {}
		inStorage = {}
		requiredMaterials = building.buildingCosts.copy()
		for material, amount in planet.getAdditionalBuildMaterials(building.areaCost).items():
			requiredMaterials[material] = requiredMaterials.get(material, 0) + amount
		for material, amount in requiredMaterials.items():
			if storage is not None:
				amount -= storage.getItemAmount(material)
				inStorage[material] = storage.getItemAmount(material)
			matEx = exchange.getMaterialExchange(material)
			i = len(matEx.sellingOrders)-1
			orderedCost = 0
			while amount > 0:
				if i < 0:
					return -1, {}, exchange.currencyCode
				order = matEx.sellingOrders[i]
				itemCount = min(amount, order.itemCount if order.itemCount is not None else sys.maxsize)
				orderedCost += itemCount * order.itemCost
				amount -= itemCount
				i -= 1
			materialCosts[material] = orderedCost
			cost += orderedCost
		return cost, materialCosts, exchange.currencyCode, requiredMaterials, inStorage

