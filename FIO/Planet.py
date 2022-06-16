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

		self.planetId: str = json["PlanetId"]
		self.planetNaturalId: str = json["PlanetNaturalId"]
		self.planetName: str = json["PlanetName"]
		self.namer: str = json["Namer"]
		self.namingDataEpochMs: int = json["NamingDataEpochMs"]
		self.nameable: bool = json["Nameable"]
		self.systemId: str = json["SystemId"]
		self.gravity = json["Gravity"]
		self.magneticField = json["MagneticField"]
		self.mass: float = json["Mass"]
		self.massEarth: float = json["MassEarth"]
		self.orbitSemiMajorAxis: int = json["OrbitSemiMajorAxis"]
		self.orbitEccentricity: float = json["OrbitEccentricity"]
		self.orbitInclination: float = json["OrbitInclination"]
		self.orbitRightAscension: float = json["OrbitRightAscension"]
		self.orbitPeriapsis: float = json["OrbitPeriapsis"]
		self.orbitIndex: int = json["OrbitIndex"]
		self.pressure: float = json["Pressure"]
		self.radiation: float = json["Radiation"]
		self.radius: float = json["Radius"]
		self.sunlight: float = json["Sunlight"]
		self.surface: str = json["Surface"]
		self.temperature: float = json["Temperature"]
		self.fertility: float = json["Fertility"]
		self.hasLocalMarket: bool = json["HasLocalMarket"]
		self.hasChamberOfCommerce: bool = json["HasChamberOfCommerce"]
		self.hasWarehouse: bool = json["HasWarehouse"]
		self.hasAdministrationCenter: bool = json["HasAdministrationCenter"]
		self.hasShipyard: bool = json["HasShipyard"]
		self.factionCode: str = json["FactionCode"]
		self.factionName: str = json["FactionName"]
		self.governorId: str = json["GovernorId"]
		self.governorUserName: str = json["GovernorUserName"]
		self.governorCorporationId: str = json["GovernorCorporationId"]
		self.governorCorporationName: str = json["GovernorCorporationName"]
		self.governorCorporationCode: str = json["GovernorCorporationCode"]
		self.currencyName: str = json["CurrencyName"]
		self.currencyCode: str = json["CurrencyCode"]
		self.collectorId: str = json["CollectorId"]
		self.collectorName: str = json["CollectorName"]
		self.collectorCode: str = json["CollectorCode"]
		self.baseLocalMarketFee: float = json["BaseLocalMarketFee"]
		self.localMarketFeeFactor: float = json["LocalMarketFeeFactor"]
		self.warehouseFee: float = json["WarehouseFee"]
		self.populationId: str = json["PopulationId"]
		self.cogcProgramStatus: str = json["COGCProgramStatus"]
		self.planetTier: int = json["PlanetTier"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]

	def __repr__(self):
		return f"<Planet `{self.planetNaturalId}`>"

	def __hash__(self):
		return hash((self.__class__, self.planetId))

	@property
	def system(self):
		return self.fio.getSystem(self.systemId)

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
