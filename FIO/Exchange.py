import math
import sys
from datetime import datetime
from dateutil.parser import isoparse
from functools import total_ordering
from typing import TYPE_CHECKING, Optional

from .Material import Material
from .Location import Location
from ..utils import formatTimedelta

if TYPE_CHECKING:
	from .FIO import FIO


@total_ordering
class MaterialExchangeOrder:
	def __init__(self, json: dict, materialExchange: "MaterialExchange", fio: "FIO"):
		self.materialExchange = materialExchange
		self.orderId: str = json["OrderId"]
		self.companyId: str = json["CompanyId"]
		self.companyName: str = json["CompanyName"]
		self.companyCode: str = json["CompanyCode"]
		self.itemCount: int = sys.maxsize if json["ItemCount"] is None else json["ItemCount"]
		self.itemCost: float = json["ItemCost"]

	def __repr__(self):
		return f"<MaterialExchangeOrder `{self.formatItemCount()}x{self.materialExchange.material.ticker}` {self.itemCost:.2f} {self.materialExchange.currency} @ `{self.materialExchange.exchangeCode}`>"

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __hash__(self):
		return hash((self.__class__, self.orderId))

	def __lt__(self, other: "MaterialExchangeOrder"):
		return self.itemCost < other.itemCost

	def formatItemCount(self):
		return "∞" if self.itemCount == sys.maxsize else str(self.itemCount)

	def format(self):
		return f"{self.itemCost:.2f} {self.materialExchange.currency} {self.formatItemCount():>4}x{self.materialExchange.material.ticker} by {self.companyName}"


class MaterialExchange:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio

		self.material = fio.getMaterial(json["MaterialTicker"])
		self.exchangeCode: str = json["ExchangeCode"]
		self.mmBuy: float = json["MMBuy"]
		self.mmSell: float = json["MMSell"]
		self.priceAverage: float = json["PriceAverage"]
		self.ask: float = json["Ask"]
		self.askCount: int = json["AskCount"]
		self.supply: int = json["Supply"]
		self.bid: float = json["Bid"]
		self.bidCount: int = json["BidCount"]
		self.demand: int = json["Demand"]
		self._buyingOrders: Optional[list[MaterialExchangeOrder]] = None
		self._sellingOrders: Optional[list[MaterialExchangeOrder]] = None
		self._cxDataModelId: Optional[str] = None
		self._exchangeName: Optional[str] = None
		self._currency: Optional[str] = None
		self._previous: Optional[any] = None  # Unknown type
		self._price: Optional[float] = None
		self._priceTimeEpochMs: Optional[int] = None
		self._high: Optional[float] = None
		self._allTimeHigh: Optional[float] = None
		self._low: Optional[float] = None
		self._allTimeLow: Optional[float] = None
		self._traded: Optional[int] = None
		self._volumeAmount: Optional[float] = None
		self._narrowPriceBandLow: Optional[float] = None
		self._narrowPriceBandHigh: Optional[float] = None
		self._widePriceBandLow: Optional[float] = None
		self._widePriceBandHigh: Optional[float] = None
		self._userNameSubmitted: Optional[str] = None
		self._timestamp: Optional[str] = None
		self._update(json)

	def __repr__(self):
		return f"<MaterialExchange `{self.material.ticker}` @ `{self.exchangeCode}`>"

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __hash__(self):
		return hash((self.__class__, self.cxDataModelId))

	def _update(self, json: dict):
		if "BuyingOrders" in json:
			self._buyingOrders = []
			for order in json["BuyingOrders"]:
				self._buyingOrders.append(MaterialExchangeOrder(order, self, self.fio))
			self._buyingOrders.sort(reverse=True)
		if "SellingOrders" in json:
			self._sellingOrders = json["SellingOrders"]
			self._sellingOrders = []
			for order in json["SellingOrders"]:
				self._sellingOrders.append(MaterialExchangeOrder(order, self, self.fio))
			self._sellingOrders.sort(reverse=True)
		if "CXDataModelId" in json:
			self._cxDataModelId = json["CXDataModelId"]
		if "ExchangeName" in json:
			self._exchangeName = json["ExchangeName"]
		if "Currency" in json:
			self._currency = json["Currency"]
		if "Previous" in json:
			self._previous = json["Previous"]
		if "Price" in json:
			self._price = json["Price"]
		if "PriceTimeEpochMs" in json:
			self._priceTimeEpochMs = json["PriceTimeEpochMs"]
		if "High" in json:
			self._high = json["High"]
		if "AllTimeHigh" in json:
			self._allTimeHigh = json["AllTimeHigh"]
		if "Low" in json:
			self._low = json["Low"]
		if "AllTimeLow" in json:
			self._allTimeLow = json["AllTimeLow"]
		if "Traded" in json:
			self._traded = json["Traded"]
		if "VolumeAmount" in json:
			self._volumeAmount = json["VolumeAmount"]
		if "NarrowPriceBandLow" in json:
			self._narrowPriceBandLow = json["NarrowPriceBandLow"]
		if "NarrowPriceBandHigh" in json:
			self._narrowPriceBandHigh = json["NarrowPriceBandHigh"]
		if "WidePriceBandLow" in json:
			self._widePriceBandLow = json["WidePriceBandLow"]
		if "WidePriceBandHigh" in json:
			self._widePriceBandHigh = json["WidePriceBandHigh"]
		if "UserNameSubmitted" in json:
			self._userNameSubmitted = json["UserNameSubmitted"]
		if "Timestamp" in json:
			self._timestamp = json["Timestamp"]

	@property
	def buyingOrders(self):
		if self._buyingOrders is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._buyingOrders

	@property
	def sellingOrders(self):
		if self._sellingOrders is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._sellingOrders

	@property
	def cxDataModelId(self):
		if self._cxDataModelId is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._cxDataModelId

	@property
	def exchangeName(self):
		if self._exchangeName is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._exchangeName

	@property
	def currency(self):
		if self._currency is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._currency

	@property
	def previous(self):
		if self._previous is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._previous

	@property
	def price(self):
		if self._price is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._price

	@property
	def priceTimeEpochMs(self):
		if self._priceTimeEpochMs is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._priceTimeEpochMs

	@property
	def high(self):
		if self._high is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._high

	@property
	def allTimeHigh(self):
		if self._allTimeHigh is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._allTimeHigh

	@property
	def low(self):
		if self._low is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._low

	@property
	def allTimeLow(self):
		if self._allTimeLow is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._allTimeLow

	@property
	def traded(self):
		if self._traded is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._traded

	@property
	def volumeAmount(self):
		if self._volumeAmount is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._volumeAmount

	@property
	def narrowPriceBandLow(self):
		if self._narrowPriceBandLow is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._narrowPriceBandLow

	@property
	def narrowPriceBandHigh(self):
		if self._narrowPriceBandHigh is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._narrowPriceBandHigh

	@property
	def widePriceBandLow(self):
		if self._widePriceBandLow is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._widePriceBandLow

	@property
	def widePriceBandHigh(self):
		if self._widePriceBandHigh is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._widePriceBandHigh

	@property
	def userNameSubmitted(self):
		if self._userNameSubmitted is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._userNameSubmitted

	@property
	def timestamp(self):
		if self._timestamp is None:
			self._update(self.fio.api.exchange(self.material.ticker, self.exchangeCode))
		return self._timestamp

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)

	def compare(self, materialExchange: "MaterialExchange"):
		"""Compares this materialExchange's most profitable buying order to the others cheapest selling order"""
		assert self.material == materialExchange.material, "MaterialExchange.compare() must be between the same material"
		if len(self.sellingOrders) <= 0 or len(materialExchange.buyingOrders) <= 0:
			return None, None, None
		buy = self.sellingOrders[-1]
		sell = materialExchange.buyingOrders[0]
		return buy, sell, sell.itemCost - buy.itemCost

	def compareAllOrders(self, materialExchange: "MaterialExchange", maxVolume: float, maxWeight: float, stopIfUnprofitable=True):
		"""
		Compares this materialExchange's most profitable buying order to the others cheapest selling order
		This will fill either maxVolume or maxWeight (or partially if not enough orders) with this materialExchange
		"""
		assert self.material == materialExchange.material, "MaterialExchange.compare() must be between the same material"
		buyOrdersUsed = []
		sellOrdersUsed = []
		if len(self.sellingOrders) <= 0 or len(materialExchange.buyingOrders) <= 0:
			return buyOrdersUsed, sellOrdersUsed, 0, 0, 0, 0
		volume, weight = 0, 0
		profit = 0
		buyOrderIndex = 0  # starts at -1 and gets decremented
		buyOrder = None
		buyOrderRemaining = 0
		sellOrderIndex = -1  # starts at 0 and get incremented
		sellOrder = None
		sellOrderRemaining = 0
		totalItemCount = 0
		while True:
			isAvailableBuyAndSellOrder = buyOrderIndex < len(self.buyingOrders) and abs(sellOrderIndex)-1 < len(materialExchange.sellingOrders)
			if buyOrderRemaining <= 0 and isAvailableBuyAndSellOrder:
				buyOrderIndex -= 1
				buyOrder = self.sellingOrders[buyOrderIndex]
				buyOrdersUsed.append(buyOrder)
				buyOrderRemaining = buyOrder.itemCount
			if sellOrderRemaining <= 0 and isAvailableBuyAndSellOrder:
				sellOrderIndex += 1
				sellOrder = materialExchange.buyingOrders[sellOrderIndex]
				sellOrdersUsed.append(sellOrder)
				sellOrderRemaining = sellOrder.itemCount
			if sellOrderRemaining <= 0 or buyOrderRemaining <= 0:
				break
			profitPerUnit = sellOrder.itemCost - buyOrder.itemCost
			maxItemCountVolume = math.floor((maxVolume-volume)/self.material.volume)
			maxItemCountWeight = math.floor((maxWeight-weight)/self.material.weight)
			itemCount = min(buyOrderRemaining, sellOrderRemaining, maxItemCountVolume, maxItemCountWeight)
			totalItemCount += itemCount
			profit += profitPerUnit * itemCount
			sellOrderRemaining -= itemCount
			buyOrderRemaining -= itemCount
			volume += self.material.volume * itemCount
			weight += self.material.weight * itemCount
			if volume + self.material.volume >= maxVolume or weight + self.material.weight >= maxWeight:
				break
		return buyOrdersUsed, sellOrdersUsed, profit, totalItemCount, volume, weight


class Exchange:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio

		self.naturalId: str = json["NaturalId"]
		self.name: str = json["Name"]
		self.systemId: str = json["SystemId"]
		self.systemNaturalId: str = json["SystemNaturalId"]
		self.systemName: str = json["SystemName"]
		self.commisionTimeEpochMs: int = json["CommisionTimeEpochMs"]
		self.comexId: str = json["ComexId"]
		self.comexName: str = json["ComexName"]
		self.comexCode: str = json["ComexCode"]
		self.warehouseId: str = json["WarehouseId"]
		self.countryCode: str = json["CountryCode"]
		self.countryName: str = json["CountryName"]
		self.currencyNumericCode: str = json["CurrencyNumericCode"]
		self.currencyCode: str = json["CurrencyCode"]
		self.currencyName: str = json["CurrencyName"]
		self.currencyDecimals: int = json["CurrencyDecimals"]
		self.governorId: str = json["GovernorId"]
		self.governorUserName: str = json["GovernorUserName"]
		self.governorCorporationId: str = json["GovernorCorporationId"]
		self.governorCorporationName: str = json["GovernorCorporationName"]
		self.governorCorporationCode: str = json["GovernorCorporationCode"]
		self.userNameSubmitted: str = json["UserNameSubmitted"]
		self.timestamp: str = json["Timestamp"]

	def __repr__(self):
		return f"<Exchange `{self.comexCode}`>"

	def __eq__(self, other):
		return hash(self) == hash(other)

	def __hash__(self):
		return hash((self.__class__, self.comexId))

	@property
	def system(self):
		return self.fio.getSystem(self.systemId)

	@property
	def location(self):
		location = Location(self.fio)
		location.system = self.system
		location.atStation = True
		return location

	@property
	def datetime(self):
		return isoparse(self.timestamp)

	@property
	def timedelta(self):
		return datetime.utcnow() - self.datetime

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)

	def getMaterialExchange(self, material: Material):
		return MaterialExchange(self.fio.api.exchange(material.ticker, self.comexCode), self.fio)

	def getAllMaterialExchanges(self):
		# There is no way to just get this exchanges materials :cry:
		# We *may* have just wanted the info from `exchangefull` but this way we catch every use case, what's the harm?
		if not self.fio.api.allmaterials.isCached():
			self.fio.api.allmaterials()
		if not self.fio.api.exchangefull.isCached():
			self.fio.api.exchangefull()
		materialExchanges = {}
		for data in self.fio.api.exchange.speedQuery("ExchangeCode", self.comexCode):
			materialExchange = self.getMaterialExchange(self.fio.getMaterial(data["material"]))
			materialExchanges[materialExchange.material] = materialExchange
		return materialExchanges
