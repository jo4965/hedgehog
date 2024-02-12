import json

import binance.error
from binance.um_futures import UMFutures
import datetime
import time


# side = "SELL"
# type = "MARKET"
# marginType = "ISOLATED" or "CROSSED"

def change_into_binance_symbol(symbol: str):
    if "USDT" in symbol:
        return symbol
    else:
        return symbol + "USDT"


class OrderResponse:
    def __init__(self, symbol, orderId, clientOrderId, status, origQty, cumQuote, updateTime):
        self.symbol = symbol
        self.orderId = orderId
        self.clientOrderId = clientOrderId
        self.status = status
        self.origQty = float(origQty)
        self.cumQuote = float(cumQuote)

        kst = datetime.timezone(datetime.timedelta(hours=9))
        self.updateTime = datetime.datetime.fromtimestamp(updateTime // 1000, tz=kst).strftime(
            '%Y-%m-%d %H:%M:%S')


class BinanceFuturesClient:
    def __init__(self, key, secret):
        self.client = UMFutures(key, secret)

    def change_current_condition(self, symbol, leverage: int, marginType):
        self.client.change_leverage(symbol=symbol, leverage=leverage)
        try:
            self.client.change_margin_type(symbol=symbol, marginType=marginType)
        except binance.error.ClientError as e:
            if e.error_code == -4048:
                print(
                    "WARNING: Ignore changing margin type into %s because marginType cannot be modified while having any position" % (
                        marginType))
            elif e.error_code == -4046:
                print("WARNING: Ignore changing margin type: No need to change margin type - %s " % marginType)
            else:
                print("ERROR: Changing margin type into %s failed " % marginType)
                print(e)

    # the price must be bigger than 100$
    def request_order(self, symbol, side, type, quantity: float) -> OrderResponse:
        usdt_symbol = change_into_binance_symbol(symbol)
        res = self.client.new_order(
            symbol=usdt_symbol,
            side=side,
            type=type,
            quantity=quantity)

        return OrderResponse(usdt_symbol,
                             res['orderId'],
                             res['clientOrderId'],
                             res['status'],
                             res['origQty'],
                             res['cumQuote'],
                             res['updateTime'])

    def cancel_order(self, symbol, orderId: int):
        res = self.client.cancel_order(
            symbol=symbol, orderId=orderId
        )
        print(json.dumps(res))
        return res

    # def

    """
    {
        "orderId": 261724492140,
        "symbol": "BTCUSDT",
        "status": "NEW",
        "clientOrderId": "upzp7VNxLoFGjbnBQYOonG",
        "price": "0.00",
        "avgPrice": "0.00",
        "origQty": "0.003",
        "executedQty": "0.000",
        "cumQty": "0.000",
        "cumQuote": "0.00000",
        "timeInForce": "GTC",
        "type": "MARKET",
        "reduceOnly": false,
        "closePosition": false,
        "side": "SELL",
        "positionSide": "BOTH",
        "stopPrice": "0.00",
        "workingType": "CONTRACT_PRICE",
        "priceProtect": false,
        "origType": "MARKET",
        "priceMatch": "NONE",
        "selfTradePreventionMode": "NONE",
        "goodTillDate": 0,
        "updateTime": 1707505101775
    }
    """

    def request_order_with_conditions(self,
                                      symbol, side, type,
                                      quantity: float,
                                      leverage=1, marginType="CROSSED") \
            -> OrderResponse:
        usdt_symbol = change_into_binance_symbol(symbol)
        self.change_current_condition(usdt_symbol, leverage, marginType)

        res = self.request_order(symbol=usdt_symbol,
                                 side=side,
                                 type=type,
                                 quantity=quantity)
        return res

    def query_order(self, symbol, order_id):
        usdt_symbol = change_into_binance_symbol(symbol)

        res = self.client.query_order(usdt_symbol, order_id)
        return OrderResponse(usdt_symbol,
                             res['orderId'],
                             res['clientOrderId'],
                             res['status'],
                             res['origQty'],
                             res['cumQuote'],
                             res['updateTime'])

    def wait_until_order_done(self, response: OrderResponse):
        while True:
            query_res = self.query_order(response.symbol,
                                         response.orderId)
            if query_res.status == "FILLED":
                return query_res
            else:
                time.sleep(0.5)
