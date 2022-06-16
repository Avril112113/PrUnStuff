from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.parser import isoparse

from .Material import Material
from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class StorageItem:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio

		# NOTE: some fields was removed, since they can be accessed via `self.material`
		self.materialId = json["MaterialId"]
		self.materialName = json["MaterialName"]
		self.materialTicker = json["MaterialTicker"]
		self.materialAmount = json["MaterialAmount"]
		self.materialValue = json["MaterialValue"]
		self.materialValueCurrency = json["MaterialValueCurrency"]
		self.type = json["Type"]
		self.totalWeight = json["TotalWeight"]
		self.totalVolume = json["TotalVolume"]

	@property
	def material(self):
		return self.fio.getMaterial(self.materialTicker)


class Storage:
	def __init__(self, json: dict, fio: "FIO", username: str):
		self.username = username

		self.storageItems = {}
		for item in json["StorageItems"]:
			self.storageItems[fio.getMaterial(item["MaterialTicker"])] = StorageItem(item, fio)
		self.storageId: str = json["StorageId"]
		self.addressableId: str = json["AddressableId"]
		self.name: str = json["Name"]
		self.weightLoad: float = json["WeightLoad"]
		self.weightCapacity: float = json["WeightCapacity"]
		self.volumeLoad: float = json["VolumeLoad"]
		self.volumeCapacity: float = json["VolumeCapacity"]
		self.fixedStore: bool = json["FixedStore"]
		self.type: str = json["Type"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]

	def __repr__(self):
		return f"<Storage `{self.storageId}`>"

	def __eq__(self, other):
		return hash(self) == hash(other)

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

	def __contains__(self, material: Material):
		return self.storageItems.get(material, None) is not None
