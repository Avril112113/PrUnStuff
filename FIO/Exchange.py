from datetime import datetime
from dateutil.parser import isoparse
from functools import total_ordering
from typing import TYPE_CHECKING

from ..utils import formatTimedelta
from .Material import Material

if TYPE_CHECKING:
	from .FIO import FIO


@total_ordering
class MaterialExchangeOrder:
	def __init__(self, json: dict, materialExchange: "MaterialExchange", fio: "FIO"):
		self.materialExchange = materialExchange
		self.orderId = json["OrderId"]
		self.companyId = json["CompanyId"]
		self.companyName = json["CompanyName"]
		self.companyCode = json["CompanyCode"]
		self.itemCount = json["ItemCount"]
		self.itemCost = json["ItemCost"]

	def __repr__(self):
		return f"<MaterialExchangeOrder `{self.itemCount}x{self.materialExchange.material.ticker}` {self.itemCost:.2f} {self.materialExchange.currency} @ `{self.materialExchange.exchangeCode}`>"

	def __hash__(self):
		return hash((self.__class__, self.orderId))

	def __lt__(self, other: "MaterialExchangeOrder"):
		return self.itemCost < other.itemCost

	def __eq__(self, other: "MaterialExchangeOrder"):
		return self.itemCost == other.itemCost

	def format(self):
		countStr = str(self.itemCount) if self.itemCount is not None else "∞"
		return f"{self.itemCost:.2f} {self.materialExchange.currency} {countStr:>4}x{self.materialExchange.material.ticker} by {self.companyName}"


class MaterialExchange:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio

		self.material = fio.getMaterial(json["MaterialTicker"])
		self.exchangeCode = json["ExchangeCode"]
		self.mmBuy = json["MMBuy"]
		self.mmSell = json["MMSell"]
		self.priceAverage = json["PriceAverage"]
		self.ask = json["Ask"]
		self.askCount = json["AskCount"]
		self.supply = json["Supply"]
		self.bid = json["Bid"]
		self.bidCount = json["BidCount"]
		self.demand = json["Demand"]
		self._buyingOrders = None
		self._sellingOrders = None
		self._cxDataModelId = None
		self._exchangeName = None
		self._currency = None
		self._previous = None
		self._price = None
		self._priceTimeEpochMs = None
		self._high = None
		self._allTimeHigh = None
		self._low = None
		self._allTimeLow = None
		self._traded = None
		self._volumeAmount = None
		self._narrowPriceBandLow = None
		self._narrowPriceBandHigh = None
		self._widePriceBandLow = None
		self._widePriceBandHigh = None
		self._userNameSubmitted = None
		self._timestamp = None
		self._update(json)

	def __repr__(self):
		return f"<MaterialExchange `{self.material.ticker}` @ `{self.exchangeCode}`>"

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


class Exchange:
	def __init__(self, json: dict, fio: "FIO"):
		self.fio = fio

		self.naturalId = json["NaturalId"]
		self.name = json["Name"]
		self.systemId = json["SystemId"]
		self.systemNaturalId = json["SystemNaturalId"]
		self.systemName = json["SystemName"]
		self.commisionTimeEpochMs = json["CommisionTimeEpochMs"]
		self.comexId = json["ComexId"]
		self.comexName = json["ComexName"]
		self.comexCode = json["ComexCode"]
		self.warehouseId = json["WarehouseId"]
		self.countryCode = json["CountryCode"]
		self.countryName = json["CountryName"]
		self.currencyNumericCode = json["CurrencyNumericCode"]
		self.currencyCode = json["CurrencyCode"]
		self.currencyName = json["CurrencyName"]
		self.currencyDecimals = json["CurrencyDecimals"]
		self.governorId = json["GovernorId"]
		self.governorUserName = json["GovernorUserName"]
		self.governorCorporationId = json["GovernorCorporationId"]
		self.governorCorporationName = json["GovernorCorporationName"]
		self.governorCorporationCode = json["GovernorCorporationCode"]
		self.userNameSubmitted = json["UserNameSubmitted"]
		self.timestamp = json["Timestamp"]

	def __repr__(self):
		return f"<Exchange `{self.comexCode}`>"

	def __hash__(self):
		return hash((self.__class__, self.comexId))

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
