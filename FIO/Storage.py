from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.parser import isoparse

from .Material import Material
from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class StorageItem:
	def __init__(self, json: dict, fio: "FIO"):
		# NOTE: some fields was removed, since they can be accessed via `self.material`
		self.material = fio.getMaterial(json["MaterialTicker"])
		self.materialAmount = json["MaterialAmount"]
		self.materialValue = json["MaterialValue"]
		self.materialValueCurrency = json["MaterialValueCurrency"]
		self.type = json["Type"]
		self.totalWeight = json["TotalWeight"]
		self.totalVolume = json["TotalVolume"]


class Storage:
	def __init__(self, json: dict, fio: "FIO", username: str):
		self.username = username

		self.storageItems = {}
		for item in json["StorageItems"]:
			self.storageItems[fio.getMaterial(item["MaterialTicker"])] = StorageItem(item, fio)
		self.storageId = json["StorageId"]
		self.addressableId = json["AddressableId"]
		self.name = json["Name"]
		self.weightLoad = json["WeightLoad"]
		self.weightCapacity = json["WeightCapacity"]
		self.volumeLoad = json["VolumeLoad"]
		self.volumeCapacity = json["VolumeCapacity"]
		self.fixedStore = json["FixedStore"]
		self.type = json["Type"]
		self.userNameSubmitted = json["UserNameSubmitted"]
		self.timestamp = json["Timestamp"]

	def __repr__(self):
		return f"<Storage `{self.storageId}`>"

	def __hash__(self):
		return hash((self.__class__, self.storageId))

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)

	def getItemAmount(self, material: Material):
		"""Gets an item in the storage, defaults to `0` if the storage doesn't contain that item"""
		item = self.storageItems.get(material, None)
		if item is None:
			return 0
		return item.materialAmount
