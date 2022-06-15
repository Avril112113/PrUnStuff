from datetime import datetime
from typing import TYPE_CHECKING
from dateutil.parser import isoparse

from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class Ship:
	def __init__(self, json: dict, fio: "FIO", username: str, userNameSubmitted: str, timestamp: str):
		self.fio = fio
		self.username = username
		self.userNameSubmitted = userNameSubmitted
		self.timestamp = timestamp

		self.repairMaterials = json["RepairMaterials"]
		self.shipId = json["ShipId"]
		self.storeId = json["StoreId"]
		self.stlFuelStoreId = json["StlFuelStoreId"]
		self.ftlFuelStoreId = json["FtlFuelStoreId"]
		self.registration = json["Registration"]
		self.name = json["Name"]
		self.commissioningTimeEpochMs = json["CommissioningTimeEpochMs"]
		self.commissioningDatetime = datetime.fromtimestamp(self.commissioningTimeEpochMs/1000)
		self.blueprintNaturalId = json["BlueprintNaturalId"]
		self.flightId = json["FlightId"]
		self.acceleration = json["Acceleration"]
		self.thrust = json["Thrust"]
		self.mass = json["Mass"]
		self.operatingEmptyMass = json["OperatingEmptyMass"]
		self.reactorPower = json["ReactorPower"]
		self.emitterPower = json["EmitterPower"]
		self.volume = json["Volume"]
		self.condition = json["Condition"]
		self.lastRepairEpochMs = json["LastRepairEpochMs"]
		self.lastRepairDatetime = None if self.lastRepairEpochMs is None else datetime.fromtimestamp(self.lastRepairEpochMs / 1000)
		self.location = json["Location"]
		self.stlFuelFlowRate = json["StlFuelFlowRate"]

	def __repr__(self):
		return f"<Ship `{self.registration}`>"

	def __hash__(self):
		return hash((self.__class__, self.shipId))

	@property
	def flight(self):
		return None if self.flightId is None else self.fio.getFlight(self.username, self.flightId)

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
