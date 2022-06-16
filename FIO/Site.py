from typing import TYPE_CHECKING

from .Building import Building

if TYPE_CHECKING:
	from .FIO import FIO


class SiteBuilding:
	def __init__(self, json: dict, fio: "FIO"):
		self.reclaimableMaterials = json["ReclaimableMaterials"]  # TODO: Better interface for this
		self.repairMaterials = json["RepairMaterials"]  # TODO: Better interface for this
		self.buildingCreated = json["BuildingCreated"]
		self.buildingId = json["BuildingId"]
		self.building = fio.getBuilding(json["BuildingTicker"])
		self.buildingLastRepair = json["BuildingLastRepair"]
		self.condition = json["Condition"]

	def __repr__(self):
		return f"<SiteBuilding `{self.buildingId}`>"

	def __hash__(self):
		return hash((self.__class__, self.buildingId))


class Site:
	def __init__(self, json: dict, fio: "FIO", username: str):
		self.username = username

		self.buildings = []
		for building in json["Buildings"]:
			self.buildings.append(SiteBuilding(building, fio))
		self.siteId: str = json["SiteId"]
		self.planetId: str = json["PlanetId"]
		self.planetIdentifier: str = json["PlanetIdentifier"]
		self.planetName: str = json["PlanetName"]
		self.planetFoundedEpochMs: int = json["PlanetFoundedEpochMs"]
		self.investedPermits: int = json["InvestedPermits"]
		self.maximumPermits: int = json["MaximumPermits"]

	def __repr__(self):
		return f"<Site `{self.siteId}`>"

	def __hash__(self):
		return hash((self.__class__, self.siteId))

	def buildingsOfType(self, building: Building):
		return list(siteBuilding for siteBuilding in self.buildings if siteBuilding.building == building)
