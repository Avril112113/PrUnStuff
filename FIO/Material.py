from datetime import datetime
from typing import TYPE_CHECKING
from dateutil.parser import isoparse

from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class Material:
	def __init__(self, json: dict, fio: "FIO"):
		self.categoryName: str = json["CategoryName"]
		self.categoryId: str = json["CategoryId"]
		self.name: str = json["Name"]
		self.matId: str = json["MatId"]
		self.ticker: str = json["Ticker"]
		self.weight: float = json["Weight"]
		self.volume: float = json["Volume"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]

	def __repr__(self):
		return f"<Material `{self.ticker}`>"

	def __hash__(self):
		return hash((self.__class__, self.ticker))

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
