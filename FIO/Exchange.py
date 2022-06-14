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
		self.material = fio.getMaterial(json["MaterialTicker"])
		self.buyingOrders = []
		for order in json["BuyingOrders"]:
			self.buyingOrders.append(MaterialExchangeOrder(order, self, fio))
		self.buyingOrders.sort(reverse=True)
		self.sellingOrders = json["SellingOrders"]
		self.sellingOrders = []
		for order in json["SellingOrders"]:
			self.sellingOrders.append(MaterialExchangeOrder(order, self, fio))
		self.sellingOrders.sort(reverse=True)
		self.cxDataModelId = json["CXDataModelId"]
		self.exchangeName = json["ExchangeName"]
		self.exchangeCode = json["ExchangeCode"]
		self.currency = json["Currency"]
		self.previous = json["Previous"]
		self.price = json["Price"]
		self.priceTimeEpochMs = json["PriceTimeEpochMs"]
		self.high = json["High"]
		self.allTimeHigh = json["AllTimeHigh"]
		self.low = json["Low"]
		self.allTimeLow = json["AllTimeLow"]
		self.ask = json["Ask"]
		self.askCount = json["AskCount"]
		self.bid = json["Bid"]
		self.bidCount = json["BidCount"]
		self.supply = json["Supply"]
		self.demand = json["Demand"]
		self.traded = json["Traded"]
		self.volumeAmount = json["VolumeAmount"]
		self.priceAverage = json["PriceAverage"]
		self.narrowPriceBandLow = json["NarrowPriceBandLow"]
		self.narrowPriceBandHigh = json["NarrowPriceBandHigh"]
		self.widePriceBandLow = json["WidePriceBandLow"]
		self.widePriceBandHigh = json["WidePriceBandHigh"]
		self.mmBuy = json["MMBuy"]
		self.mmSell = json["MMSell"]
		self.userNameSubmitted = json["UserNameSubmitted"]
		self.timestamp = json["Timestamp"]

	def __repr__(self):
		return f"<MaterialExchange `{self.material.ticker}` @ `{self.exchangeCode}`>"

	def __hash__(self):
		return hash((self.__class__, self.cxDataModelId))

	@property
	def timedelta(self):
		return datetime.utcnow() - isoparse(self.timestamp)

	def formatTimedelta(self):
		return formatTimedelta(self.timedelta)


class Exchange:
	def __init__(self, json: dict, fio: "FIO"):
		self._fio = fio
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
	def timedelta(self):
		return datetime.utcnow() - isoparse(self.timestamp)

	def formatTimedelta(self):
		delta = self.timedelta
		days, hours, minutes = delta.days, delta.seconds // 3600, delta.seconds // 60 % 60
		return f"{days}days {hours}h {minutes}m"

	def getMaterialExchange(self, material: Material):
		return MaterialExchange(self._fio.api.exchange(material.ticker, self.comexCode), self._fio)
