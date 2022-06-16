from datetime import datetime
from typing import TYPE_CHECKING
from dateutil.parser import isoparse

from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


class SubSector:
	def __init__(self, json: dict, fio: "FIO"):
		self.vertices: list[tuple[float, float, float]] = list((vert["X"], vert["Y"], vert["Z"]) for vert in json["Vertices"])
		self.ssId: str = json["SSId"]

	def __repr__(self):
		return f"<SubSector `{self.ssId}`>"

	def __hash__(self):
		return hash((self.__class__, self.ssId))


class WorldSector:
	def __init__(self, json: dict, fio: "FIO"):
		self.subSectors = list(SubSector(subSector, fio) for subSector in json["SubSectors"])
		self.sectorId: str = json["SectorId"]
		self.name: str = json["Name"]
		self.hexQ: int = json["HexQ"]
		self.hexR: int = json["HexR"]
		self.hexS: int = json["HexS"]
		self.size: int = json["Size"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]

	def __repr__(self):
		return f"<WorldSector `{self.name}`>"

	def __hash__(self):
		return hash((self.__class__, self.sectorId))

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
