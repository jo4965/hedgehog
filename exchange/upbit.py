import pyupbit
import json
import time

from enum import Enum


def change_into_upbit_symbol(symbol: str):
    if symbol.startswith("KRW-"):
        return symbol
    else:
        return "KRW-" + symbol


def get_current_price(symbol) -> float:
    return pyupbit.get_current_price(symbol)


class UpbitClient:
    FEE = 0.0001

    def __init__(self, key, secret):
        self.client = pyupbit.Upbit(key, secret)

    def calculate_buy_price_from_amount_plus_fee(self, symbol, amount):
        # 사려는 개수 만큼의 현재가를 곱한 후 오차 값을 더한 값을 계산
        current_price = get_current_price(symbol)
        how_much = current_price * amount
        # how_much += how_much * self.FEE
        return how_much

    def request_order_with_amount(self, symbol, buy_or_sell, amount):
        symbol = change_into_upbit_symbol(symbol)
        # 매수 시에는 개수로 호출이 불가능하여 개수에 해당하는 가격을 구해와야 함
        if buy_or_sell == "BUY":
            price = self.calculate_buy_price_from_amount_plus_fee(symbol, amount)
            buy_res = self.client.buy_market_order(symbol, price)
            return self.client.get_order(buy_res['uuid'])
        elif buy_or_sell == "SELL":
            sell_res = self.client.sell_market_order(symbol, amount)
            return self.client.get_order(sell_res['uuid'])
        else:
            print("type must be BUY or SELL")

    # price of crypto in KRW
    def request_buy_order(self, symbol, KRW_amount_to_buy):
        symbol = change_into_upbit_symbol(symbol)
        buy_res = self.client.buy_market_order(symbol, KRW_amount_to_buy)
        return self.client.get_order(buy_res['uuid'])

    # number of crypto
    def request_sell_order(self, symbol, amount):
        symbol = change_into_upbit_symbol(symbol)
        sell_res = self.client.sell_market_order(symbol, amount)
        return self.client.get_order(sell_res['uuid'])

    def query_order(self, uuid):
        res = self.client.get_order(uuid)
        return res

    def query_individual_order(self, uuid):
        res = self.client.get_individual_order(uuid)
        return res

    def wait_until_order_done(self, response):
        while True:
            query_res = self.query_order(response.get("uuid"))
            if OrderState.is_order_completed(query_res):
                return query_res
            else:
                time.sleep(0.5)


class OrderState(Enum):
    WAIT = "wait"
    DONE = "done"
    CANCEL = "cancel"

    @classmethod
    def is_order_completed(state, res: dict):
        return OrderState.DONE.value == res.get("state") \
                or OrderState.CANCEL.value == res.get("state")
