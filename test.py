
import json
from exchange import BinanceFuturesClient, UpbitClient, OrderState
import os
from fastapi import BackgroundTasks
from dotenv import load_dotenv
from main import start_hedge
from dto.models import HedgeData
load_dotenv()

ENVIRON_BINANCE_KEY="BINANCE_KEY"
ENVIRON_BINANCE_SECRET="BINANCE_SECRET"
ENVIRON_UPBIT_KEY="UPBIT_KEY"
ENVIRON_UPBIT_SECRET="UPBIT_SECRET"

if __name__ == '__main__':

    start_hedge("zenike", "BTC", "USDT.P", 0.003, "OFF", BackgroundTasks())

    # symbol = "BTCUSDT"
    # binance_client = BinanceFuturesClient(key=os.getenv(ENVIRON_BINANCE_KEY),
    #                                       secret=os.getenv(ENVIRON_BINANCE_SECRET))
    #

    # upbit_client = UpbitClient(os.getenv(ENVIRON_UPBIT_KEY), os.getenv(ENVIRON_UPBIT_SECRET))
    # res = upbit_client.request_sell_order("KRW-BTC", 0.00306734)

    #
    # binance_client.create_order_with_conditions(symbol, "SELL", "MARKET", 0.003, leverage=10)
    # binance_client.cancel_order(symbol, 261724492140)
    #
    # res = um_futures_client.account()
    # res = um_futures_client.funding_rate(symbol = "BTCUSDT")
    #
    # print(json.dumps(res))
    #
    # res = binance_client.client.query_order(
    #     symbol="BTCUSDT", orderId = 261724492140
    # )
    # res = um_futures_client.get_position_mode()
    # res = um_futures_client.get_all_orders(symbol = "BTCUSDT")
    #
    # print(res)
    # res = upbit_client.get_chance("KRW-BTC")
    # res = pyupbit.get_current_price("KRW-BTC")
    # won = res * 0.006
    # import pdb
    # pdb.set_trace()
    # ret = upbit_client.calculate_buy_price_from_amount_plus_fee("KRW-BTC", 0.001)
    # res = upbit_client.request_buy_order("BTC", 10000)
    # res = upbit_client.query_individual_order("e72e554e-77b9-4e82-a145-d2cfdb1cb8c7")
    # if not OrderState.is_order_completed(res):
    #     res = upbit_client.wait_until_order_done(res)
    #
    #
    # print(json.dumps(res))
    #
    # res = upbit_client.client.get_order("7c10b104-5cb8-4b4a-ab82-846541e6e072")
    # print(res);
    # print(won)
    # print(json.dumps(res))