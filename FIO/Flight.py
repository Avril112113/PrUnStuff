from datetime import datetime
from typing import TYPE_CHECKING
from dateutil.parser import isoparse

from ..utils import formatTimedelta

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
	def __init__(self, json: dict, fio: "FIO", userNameSubmitted: str, timestamp: str):
		self.fio = fio
		self.userNameSubmitted = userNameSubmitted
		self.timestamp = timestamp

		self.segments = json["Segments"]
		self.flightId = json["FlightId"]
		self.shipId = json["ShipId"]
		self.origin = json["Origin"]
		self.destination = json["Destination"]
		self.departureTimeEpochMs = json["DepartureTimeEpochMs"]
		self.departureDatetime = datetime.fromtimestamp(self.departureTimeEpochMs/1000)
		self.arrivalTimeEpochMs = json["ArrivalTimeEpochMs"]
		self.arrivalDatetime = datetime.fromtimestamp(self.arrivalTimeEpochMs/1000)
		self.currentSegmentIndex = json["CurrentSegmentIndex"]
		self.stlDistance = json["StlDistance"]
		self.ftlDistance = json["FtlDistance"]
		self.isAborted = json["IsAborted"]

	def __repr__(self):
		return f"<Flight `{self.flightId}`>"

	def __hash__(self):
		return hash((self.__class__, self.flightId))

	@property
	def ship(self):
		# TODO: based on the username from __init__
		return self.fio.getMyShip(self.shipId)

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)
