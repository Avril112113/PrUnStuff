# PrUnStuff
This project is just to make, making tools for PrUn easier using FIOs rest API.

There are 2 layers of abstraction over the FIO API and finally a helper class for PrUn.  
FIO Rest API -> [`FIOApi` class](#FIOApi-class) -> [`FIO` class](#FIOApi-class) -> [`PrUnStuff` class](#PrUnStuff-class)


# TIP
Use the following to see when data is being retrieved from FIO, as retrieving this data can hang the application for a while depending on how much isn't cached yet.  
```py
import logging

logging.basicConfig(level=logging.NOTSET)
logging.getLogger("urllib3.connectionpool").disabled = True
```


# Getting FIO Api Key
[https://fio.fnar.net/settings](https://fio.fnar.net/settings)  
You must have used FIO for PrUn and have an account, this is done by simply using the browser extension and reloading the PrUn webpage.  
Once you've got an FIO account, go to `Settings` -> `Create API Key` to create the key.  
Note: This API (as of editing this readme) does not support writing anything to FIO, as it's unnecessary, so the API Key does not need write access.


# FIOApi class
This class reads from the FIO rest api and caches the results.  
The cache can be found in the same directory as `FIOApi.py`  
Most methods in that class has `.clearCache()` method that, though this method will not show on autocomplete.  
All methods from this class returns the json data from the API.
```py
from PrUnStuff import FIOApi

fioApi = FIOApi("YOUR_FIO_API_KEY")
print(fioApi.material("H2O")["Name"])
```

# FIO class
The FIO class is the 2nd layer abstraction, it provides a cleaner interface for using the data from FIO.  
```py
from PrUnStuff import FIO

fio = FIO("YOUR_FIO_API_KEY")
matEx = fio.getExchange("IC1").getMaterialExchange("BSE")
print(matEx.supply / matEx.demand)
```

# PrUnStuff class
This final class contains pre-made methods for some stuff you might want to do for PrUn.  
For example, PrUnStuff class has `producibleWithStorageContents()` which gets the amount of some resource you can produce with the contents of a storage.
```py
from typing import Union
from PrUnStuff import PrUnStuff
from PrUnStuff.FIO import *


def printProduction(prUnStuff: PrUnStuff, planet: Planet, material: Material, recipes: list[BuildingRecipe], buildingUseLimits: Union[None, bool, dict[Building, int]] = True):
	siteBuildingUseLimits = prUnStuff.getBuildingUseLimitsForRecipesAtSite(planet, recipes)
	if buildingUseLimits is True:
		buildingUseLimits = siteBuildingUseLimits
	resources, recipesUsed, buildingsUsed = prUnStuff.producibleWithStorageContents(
		planet, material,
		buildingUseLimits=buildingUseLimits,
		recipes=recipes
	)
	consumed, produced = prUnStuff.getConsumedProducedFromRecipesUsed(recipesUsed)
	# TODO: Fix this
	# prodTime = prUnStuff.getProductionTime(planet, recipes, recipesUsed)

	print("-- Buildings utilisation --")
	buildingUsage = prUnStuff.getBuildingUsage(siteBuildingUseLimits, buildingsUsed)
	for building, amount in buildingsUsed.items():
		print(f"{building.ticker} {buildingUsage[building]*100:.1f}%")
	print("-- Final resources --")
	for material, amount in resources.items():
		print(f"{material.ticker} x{amount:,}")
	print("-- Consumed resources --")
	for material, count in consumed.items():
		print(f"{material.ticker} x{count:,}")
	print("-- Recipes used --")
	for recipe, used in recipesUsed.items():
		print(f"{recipe.recipeName}\tused {used} times")
	print("-- Produced resources --")
	for material, count in produced.items():
		print(f"{material.ticker} x{count:,}")


prUnStuff = PrUnStuff("YOUR_FIO_API_KEY")
fio = prUnStuff.fio
planet = fio.getPlanet("VH-331a")

finalMaterial = fio.getMaterial("C")
frm = fio.getBuilding("FRM")
inc = fio.getBuilding("INC")
involvedRecipes = [
	inc.recipes["4xHCP 2xGRN 2xMAI = 4xC"],
	frm.recipes["2xH2O = 4xHCP"],
	frm.recipes["1xH2O = 4xGRN"],
	frm.recipes["4xH2O = 12xMAI"],
]
siteBuildingUseLimits = prUnStuff.getBuildingUseLimitsForRecipesAtSite(planet, involvedRecipes)
printProduction(prUnStuff, planet, finalMaterial, involvedRecipes, buildingUseLimits=siteBuildingUseLimits)
```
