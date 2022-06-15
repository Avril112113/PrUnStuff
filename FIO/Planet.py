from datetime import datetime
from typing import TYPE_CHECKING
from dateutil.parser import isoparse

from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class PlanetResource:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio
		self.materialId = json["MaterialId"]
		self.resourceType = json["ResourceType"]
		self.factor = json["Factor"]


class PlanetBuildRequirement:
	def __init__(self, json: dict, fio: "FIO"):
		self.materialName = json["MaterialName"]
		self.materialId = json["MaterialId"]
		self.materialTicker = json["MaterialTicker"]
		self.material = fio.getMaterial(self.materialTicker)
		self.materialCategory = json["MaterialCategory"]
		self.materialAmount = json["MaterialAmount"]
		self.materialWeight = json["MaterialWeight"]
		self.materialWeight = json["MaterialWeight"]


class PlanetProductionFee:
	def __init__(self, json: dict, fio: "FIO"):
		self.category = json["Category"]
		self.workforceLevel = json["WorkforceLevel"]
		self.feeAmount = json["FeeAmount"]
		self.feeCurrency = json["FeeCurrency"]


class PlanetCOGCProgram:
	def __init__(self, json: dict, fio: "FIO"):
		self.programType = json["ProgramType"]
		self.startEpochMs = json["StartEpochMs"]
		self.startDatetime = datetime.fromtimestamp(self.startEpochMs/1000)
		self.endEpochMs = json["EndEpochMs"]
		self.endDatetime = datetime.fromtimestamp(self.endEpochMs/1000)


class PlanetCOGCVote:
	def __init__(self, json: dict, fio: "FIO"):
		self.companyName = json["CompanyName"]
		self.companyCode = json["CompanyCode"]
		self.influence = json["Influence"]
		self.voteType = json["VoteType"]
		self.voteTimeEpochMs = json["VoteTimeEpochMs"]
		self.voteDatetime = datetime.fromtimestamp(self.voteTimeEpochMs/1000)


class PlanetCOGCUpkeep:
	def __init__(self, json: dict, fio: "FIO"):
		raise NotImplementedError(str(json))


class Planet:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio

		self.resources = {}
		for resourceJson in json["Resources"]:
			resource = PlanetResource(resourceJson, fio)
			self.resources[resource.materialId] = resource

		self.buildRequirements = {}
		for requirementJson in json["BuildRequirements"]:
			requirement = PlanetBuildRequirement(requirementJson, fio)
			self.buildRequirements[requirement.material] = requirement

		self.productionFees = {}
		for feeJson in json["ProductionFees"]:
			productionFee = PlanetProductionFee(feeJson, fio)
			if productionFee.category not in self.buildRequirements:
				self.buildRequirements[productionFee.category] = {}
			self.buildRequirements[productionFee.category][productionFee.workforceLevel] = productionFee

		self.cogcPrograms = []
		for programJson in json["COGCPrograms"]:
			program = PlanetCOGCProgram(programJson, fio)
			self.cogcPrograms.append(program)

		self.cogcVotes = []
		for voteJson in json["COGCVotes"]:
			vote = PlanetCOGCVote(voteJson, fio)
			self.cogcVotes.append(vote)

		self.cogcUpkeep = []
		for upkeepJson in json["COGCUpkeep"]:
			upkeep = PlanetCOGCUpkeep(upkeepJson, fio)
			self.cogcUpkeep.append(upkeep)

		self.planetId = json["PlanetId"]
		self.planetNaturalId = json["PlanetNaturalId"]
		self.planetName = json["PlanetName"]
		self.namer = json["Namer"]
		self.namingDataEpochMs = json["NamingDataEpochMs"]
		self.nameable = json["Nameable"]
		self.systemId = json["SystemId"]
		self.gravity = json["Gravity"]
		self.magneticField = json["MagneticField"]
		self.mass = json["Mass"]
		self.massEarth = json["MassEarth"]
		self.orbitSemiMajorAxis = json["OrbitSemiMajorAxis"]
		self.orbitEccentricity = json["OrbitEccentricity"]
		self.orbitInclination = json["OrbitInclination"]
		self.orbitRightAscension = json["OrbitRightAscension"]
		self.orbitPeriapsis = json["OrbitPeriapsis"]
		self.orbitIndex = json["OrbitIndex"]
		self.pressure = json["Pressure"]
		self.radiation = json["Radiation"]
		self.radius = json["Radius"]
		self.sunlight = json["Sunlight"]
		self.surface = json["Surface"]
		self.temperature = json["Temperature"]
		self.fertility = json["Fertility"]
		self.hasLocalMarket = json["HasLocalMarket"]
		self.hasChamberOfCommerce = json["HasChamberOfCommerce"]
		self.hasWarehouse = json["HasWarehouse"]
		self.hasAdministrationCenter = json["HasAdministrationCenter"]
		self.hasShipyard = json["HasShipyard"]
		self.factionCode = json["FactionCode"]
		self.factionName = json["FactionName"]
		self.governorId = json["GovernorId"]
		self.governorUserName = json["GovernorUserName"]
		self.governorCorporationId = json["GovernorCorporationId"]
		self.governorCorporationName = json["GovernorCorporationName"]
		self.governorCorporationCode = json["GovernorCorporationCode"]
		self.currencyName = json["CurrencyName"]
		self.currencyCode = json["CurrencyCode"]
		self.collectorId = json["CollectorId"]
		self.collectorName = json["CollectorName"]
		self.collectorCode = json["CollectorCode"]
		self.baseLocalMarketFee = json["BaseLocalMarketFee"]
		self.localMarketFeeFactor = json["LocalMarketFeeFactor"]
		self.warehouseFee = json["WarehouseFee"]
		self.populationId = json["PopulationId"]
		self.cogcProgramStatus = json["COGCProgramStatus"]
		self.planetTier = json["PlanetTier"]
		self.userNameSubmitted = json["UserNameSubmitted"]
		self.timestamp = json["Timestamp"]

	def __repr__(self):
		return f"<Planet `{self.planetNaturalId}`>"

	def __hash__(self):
		return hash((self.__class__, self.planetId))

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def getProductionFee(self, category: str, workforceLevel: str):
		return self.productionFees.get(category, {}).get(workforceLevel, None)

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)

	def getAdditionalBuildMaterials(self, area: int):
		additionalMaterials = {}
		# https://handbook.apex.prosperousuniverse.com/wiki/building-costs/#costs-calculation
		if self.surface:
			additionalMaterials[self.fio.getMaterial("MCG")] = area * 4
		else:
			additionalMaterials[self.fio.getMaterial("AEF")] = area / 3
		if self.pressure < 0.25:
			additionalMaterials[self.fio.getMaterial("SEA")] = area * 1
		elif self.pressure > 2:
			additionalMaterials[self.fio.getMaterial("HSE")] = 1
		if self.gravity < 0.25:
			additionalMaterials[self.fio.getMaterial("MGC")] = 1
		elif self.gravity > 2.5:
			additionalMaterials[self.fio.getMaterial("BL")] = 1
		if self.temperature < -25:
			additionalMaterials[self.fio.getMaterial("INS")] = area * 10
		elif self.gravity > 75:
			additionalMaterials[self.fio.getMaterial("TSH")] = 1
		return additionalMaterials
