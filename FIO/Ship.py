from datetime import datetime
from typing import TYPE_CHECKING, Optional
from dateutil.parser import isoparse

from .System import System
from .Planet import Planet
from .utils import formatTimedelta, parseLocation

if TYPE_CHECKING:
	from .FIO import FIO


class Ship:
	def __init__(self, json: dict, fio: "FIO", username: str, userNameSubmitted: str, timestamp: str):
		self.fio = fio
		self.username = username
		self.userNameSubmitted = userNameSubmitted
		self.timestamp = timestamp

		self.repairMaterials = json["RepairMaterials"]  # TODO:
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
		self.location: str = json["Location"]
		self.stlFuelFlowRate: float = json["StlFuelFlowRate"]
		self._system: Optional[System] = None
		self._planet: Optional[Planet] = None
		self._otherPlaceName: Optional[str] = None

	def __repr__(self):
		return f"<Ship `{self.registration}`>"

	def __hash__(self):
		return hash((self.__class__, self.shipId))

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
	def system(self):
		if self._system is None:
			self._system, self._planet, self._otherPlaceName = parseLocation(self.fio, self.location)
		return self._system

	@property
	def planet(self):
		if self._planet is None:
			self._system, self._planet, self._otherPlaceName = parseLocation(self.fio, self.location)
		return self._planet

	@property
	def otherPlaceName(self):
		if self._otherPlaceName is None:
			self._system, self._planet, self._otherPlaceName = parseLocation(self.fio, self.location)
		return self._otherPlaceName

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
