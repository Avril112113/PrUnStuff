from datetime import datetime
from typing import TYPE_CHECKING, Optional
from dateutil.parser import isoparse

from .Location import Location
from .utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class Ship:
	def __init__(self, json: dict, fio: "FIO", username: str, userNameSubmitted: str, timestamp: str):
		self.fio = fio
		self.username = username
		self.userNameSubmitted = userNameSubmitted
		self.timestamp = timestamp

		self._repairMaterials = json["RepairMaterials"]
		self.shipId: str = json["ShipId"]
		self.storeId: str = json["StoreId"]
		self.stlFuelStoreId: str = json["StlFuelStoreId"]
		self.ftlFuelStoreId: str = json["FtlFuelStoreId"]
		self.registration: str = json["Registration"]
		self.name: str = json["Name"]
		self.commissioningTimeEpochMs = json["CommissioningTimeEpochMs"]
		self.commissioningDatetime = datetime.fromtimestamp(self.commissioningTimeEpochMs/1000)
		self.blueprintNaturalId: str = json["BlueprintNaturalId"]
		self.flightId: str = json["FlightId"]
		self.acceleration: float = json["Acceleration"]
		self.thrust: float = json["Thrust"]
		self.mass: float = json["Mass"]
		self.operatingEmptyMass: float = json["OperatingEmptyMass"]
		self.reactorPower: float = json["ReactorPower"]
		self.emitterPower: float = json["EmitterPower"]
		self.volume: float = json["Volume"]
		self.condition: float = json["Condition"]
		self.lastRepairEpochMs: int = json["LastRepairEpochMs"]
		self.lastRepairDatetime = None if self.lastRepairEpochMs is None else datetime.fromtimestamp(self.lastRepairEpochMs / 1000)
		self.locationStr: str = json["Location"]  # The only time I will break my rule of "keep the fields the same as the json"...
		self.stlFuelFlowRate: float = json["StlFuelFlowRate"]
		self._location: Optional[Location] = None

	def __repr__(self):
		return f"<Ship `{self.registration}`>"

	def __hash__(self):
		return hash((self.__class__, self.shipId))

	@property
	def repairMaterials(self):
		repairMaterials = {}
		for repairMaterialJson in self._repairMaterials:
			repairMaterials[self.fio.getMaterial(repairMaterialJson["MaterialTicker"])] = repairMaterialJson["Amount"]
		return repairMaterials

	@property
	def flight(self):
		return None if self.flightId is None else self.fio.getFlight(self.username, self.flightId)

	@property
	def store(self):
		return self.fio.getStorage(self.username, self.storeId)

	@property
	def ftlFuelStore(self):
		return self.fio.getStorage(self.username, self.ftlFuelStoreId)

	@property
	def stlFuelStore(self):
		return self.fio.getStorage(self.username, self.stlFuelStoreId)

	@property
	def fuel(self):
		return self.fio.getShipFuel(self.username, self.shipId)

	@property
	def location(self):
		if self._location is None:
			self._location = Location.fromLocationString(self.fio, self.locationStr)
			self._location.inFlight = self.flightId is not None
		return self._location

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
