from typing import TYPE_CHECKING

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
		return hash(self.buildingId)


class Site:
	def __init__(self, json: dict, fio: "FIO"):
		self.buildings = []
		for building in json["Buildings"]:
			self.buildings.append(SiteBuilding(building, fio))
		self.siteId = json["SiteId"]
		self.planetId = json["PlanetId"]
		self.planetIdentifier = json["PlanetIdentifier"]
		self.planetName = json["PlanetName"]
		self.planetFoundedEpochMs = json["PlanetFoundedEpochMs"]
		self.investedPermits = json["InvestedPermits"]
		self.maximumPermits = json["MaximumPermits"]

	def __repr__(self):
		return f"<Site `{self.siteId}`>"

	def __hash__(self):
		return hash(self.siteId)
