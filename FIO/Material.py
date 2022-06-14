from datetime import datetime
from typing import TYPE_CHECKING

from dateutil.parser import isoparse

if TYPE_CHECKING:
	from .FIO import FIO


class Material:
	def __init__(self, json: dict, fio: "FIO"):
		self.categoryName: str = json["CategoryName"]
		self.categoryId: str = json["CategoryId"]
		self.name: str = json["Name"]
		self.matId: str = json["MatId"]
		self.ticker: str = json["Ticker"]
		self.weight: str = json["Weight"]
		self.volume: str = json["Volume"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]

	def __repr__(self):
		return f"<Material `{self.ticker}`>"

	def __hash__(self):
		return hash((self.__class__, self.ticker))

	@property
	def timedelta(self):
		return datetime.utcnow() - isoparse(self.timestamp)

	def formatTimedelta(self):
		delta = self.timedelta
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		return f"{days}days {hours}h {minutes}m"
