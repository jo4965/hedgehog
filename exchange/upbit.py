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


def calculate_sell_krw_from_res(sell_response):
    sell_price_krw = 0.0
    for trade in sell_response.get("trades"):
        sell_price_krw += float(trade.get("funds"))

    return sell_price_krw


def get_sold_amount_from_res(sell_response):
    return float(sell_response.get("executed_volume"))


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

    # 0.1개 보다 크면 0.1개씩 쪼개서 팝니다.
    def split_request_sell_order(self, symbol, amount):
        leftover = amount
        split_amount = 0.1
        sold_amount = 0.0
        sold_price_krw = 0.0
        while leftover > 0.0:
            if leftover < split_amount:
                amount_to_sell = leftover
            else:
                amount_to_sell = split_amount

            while True:
                try:
                    upbit_sell_res = self.request_sell_order(symbol, amount_to_sell)
                    if not OrderState.is_order_completed(upbit_sell_res):
                        upbit_sell_res = self.wait_until_order_done(upbit_sell_res)

                    sold_amount += get_sold_amount_from_res(upbit_sell_res)
                    sold_price_krw += calculate_sell_krw_from_res(upbit_sell_res)
                    break
                except Exception as e:
                    time.sleep(1)

            leftover -= split_amount

        return sold_amount, sold_price_krw



class OrderState(Enum):
    WAIT = "wait"
    DONE = "done"
    CANCEL = "cancel"

    @classmethod
    def is_order_completed(state, res: dict):
        return OrderState.DONE.value == res.get("state") \
                or OrderState.CANCEL.value == res.get("state")
