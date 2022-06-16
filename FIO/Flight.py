from datetime import datetime
from typing import TYPE_CHECKING, Optional
from dateutil.parser import isoparse

from .System import System
from .Planet import Planet
from .utils import formatTimedelta, parseLocation


if TYPE_CHECKING:
	from .FIO import FIO


class FlightLine:
	def __init__(self, json: dict, fio: "FIO"):
		self.type = json["Type"]
		self.lineId = json["LineId"]
		self.lineNaturalId = json["LineNaturalId"]
		self.lineName = json["LineName"]

	def __repr__(self):
		return f"<FlightLine `{self.lineId}>"

	def __hash__(self):
		return hash((self.__class__, self.lineId))


class FlightSegment:
	def __init__(self, json: dict, fio: "FIO", flight: "Flight"):
		self.flight = flight

		self.originLines = []
		for lineJson in json["OriginLines"]:
			self.originLines.append(FlightLine(lineJson, fio))
		self.destinationLines = []
		for lineJson in json["DestinationLines"]:
			self.destinationLines.append(FlightLine(lineJson, fio))
		self.type = json["Type"]
		self.departureTimeEpochMs = json["DepartureTimeEpochMs"]
		self.departureDatetime = datetime.fromtimestamp(self.departureTimeEpochMs/1000)
		self.arrivalTimeEpochMs = json["ArrivalTimeEpochMs"]
		self.arrivalDatetime = datetime.fromtimestamp(self.arrivalTimeEpochMs/1000)
		self.stlDistance = json["StlDistance"]
		self.stlFuelConsumption = json["StlFuelConsumption"]
		self.ftlDistance = json["FtlDistance"]
		self.ftlFuelConsumption = json["FtlFuelConsumption"]
		self.origin = json["Origin"]
		self.destination = json["Destination"]

	def __repr__(self):
		return f"<FlightSegment `{self.origin}` -> `{self.destination}`>"

	def __hash__(self):
		return hash((self.__class__, self.flight.flightId, self.origin, self.destination))


class Flight:
	def __init__(self, json: dict, fio: "FIO", username: str, userNameSubmitted: str, timestamp: str):
		self.fio = fio
		self.username = username
		self.userNameSubmitted = userNameSubmitted
		self.timestamp = timestamp

		self.segments = []
		for segmentJson in json["Segments"]:
			self.segments.append(FlightSegment(segmentJson, fio, self))
		self.flightId: str = json["FlightId"]
		self.shipId: str = json["ShipId"]
		self.origin: str = json["Origin"]
		self.destination: str = json["Destination"]
		self.departureTimeEpochMs: int = json["DepartureTimeEpochMs"]
		self.departureDatetime = datetime.fromtimestamp(self.departureTimeEpochMs/1000)
		self.arrivalTimeEpochMs: int = json["ArrivalTimeEpochMs"]
		self.arrivalDatetime = datetime.fromtimestamp(self.arrivalTimeEpochMs/1000)
		self.currentSegmentIndex: int = json["CurrentSegmentIndex"]
		self.stlDistance: int = json["StlDistance"]
		self.ftlDistance: int = json["FtlDistance"]
		self.isAborted: bool = json["IsAborted"]
		self._originSystem: Optional[System] = None
		self._originPlanet: Optional[Planet] = None
		self._originOtherPlaceName: Optional[Planet] = None
		self._destinationSystem: Optional[System] = None
		self._destinationPlanet: Optional[Planet] = None
		self._destinationOtherPlaceName: Optional[Planet] = None

	def __repr__(self):
		return f"<Flight `{self.flightId}`>"

	def __hash__(self):
		return hash((self.__class__, self.flightId))

	@property
	def ship(self):
		return self.fio.getShip(self.username, self.shipId)

	@property
	def originSystem(self):
		if self._originSystem is None:
			self._originSystem, self._originPlanet, self._originOtherPlaceName = parseLocation(self.fio, self.origin)
		return self._originSystem

	@property
	def originPlanet(self):
		if self._originPlanet is None:
			self._originSystem, self._originPlanet, self._originOtherPlaceName = parseLocation(self.fio, self.origin)
		return self._originPlanet

	@property
	def originOtherPlaceName(self):
		if self._originOtherPlaceName is None:
			self._originSystem, self._originPlanet, self._originOtherPlaceName = parseLocation(self.fio, self.origin)
		return self._originOtherPlaceName

	@property
	def destinationSystem(self):
		if self._destinationSystem is None:
			self._destinationSystem, self._destinationPlanet, self._destinationOtherPlaceName = parseLocation(self.fio, self.destination)
		return self._destinationSystem

	@property
	def destinationPlanet(self):
		if self._destinationPlanet is None:
			self._destinationSystem, self._destinationPlanet, self._destinationOtherPlaceName = parseLocation(self.fio, self.destination)
		return self._destinationPlanet

	@property
	def destinationOtherPlaceName(self):
		if self._destinationOtherPlaceName is None:
			self._destinationSystem, self._destinationPlanet, self._destinationOtherPlaceName = parseLocation(self.fio, self.destination)
		return self._destinationOtherPlaceName

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
