from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .FIO import FIO


class Planet:
	def __init__(self, json: dict, fio: "FIO"):
		# TODO: The list fields below
		# self.resources = json["Resources"]
		# self.buildRequirements = json["BuildRequirements"]
		# self.productionFees = json["ProductionFees"]
		# self.cogcPrograms = json["COGCPrograms"]
		# self.cogcVotes = json["COGCVotes"]
		# self.cogcUpkeep = json["COGCUpkeep"]

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
		return hash(self.planetId)
