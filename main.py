import json
from exchange import UpbitClient, BinanceFuturesClient, OrderState
from utility.logback import LoggerWithDiscord
from dto.models import HedgeData
import hedge_adapter

import ipaddress
import traceback
from fastapi import FastAPI, Request, status, BackgroundTasks
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
import os
from dotenv import load_dotenv

load_dotenv()

VERSION = "beta"
app = FastAPI(default_response_class=ORJSONResponse)
admin_logger = LoggerWithDiscord(os.getenv("DISCORD_WEBHOOK_URL"))


@app.on_event("startup")
async def startup():
    admin_logger.log_message(f"Hedgehog %s 실행 완료!" % VERSION)


whitelist = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7", "127.0.0.1", "125.178.123.80"]


@app.middleware("http")
async def whitelist_middleware(request: Request, call_next):
    try:
        if request.client.host not in whitelist and not ipaddress.ip_address(request.client.host).is_private:
            msg = f"{request.client.host}는 안됩니다"
            print(msg)
            return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                                  content=f"{request.client.host}는 허용되지 않습니다")
    except:
        admin_logger.log_error_message(traceback.format_exc(), "미들웨어 에러")
    else:
        response = await call_next(request)
        return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    msgs = [f"[에러{index + 1}] " + f"{error.get('msg')} \n{error.get('loc')}" for index, error in
            enumerate(exc.errors())]
    message = "[Error]\n"
    for msg in msgs:
        message = message + msg + "\n"

    admin_logger.log_validation_error_message(f"{message}\n {exc.body}")
    return await request_validation_exception_handler(request, exc)


@app.get("/hi")
async def welcome():
    return "hi!!"


def create_default_error():
    return {
        "result": "error"
    }


@app.post("/hedge")
async def hedge(hedge_data: HedgeData, background_tasks: BackgroundTasks):
    # zenike
    user_name = hedge_data.user_name

    # BTC
    base = hedge_data.base

    # USDT.P
    quote = hedge_data.quote

    # ON or OFF
    hedge = hedge_data.hedge

    amount = hedge_data.amount

    result = start_hedge(user_name, base, quote, amount, hedge, background_tasks)
    return result


def start_hedge(user_name, base, quote, amount, hedge, background_tasks: BackgroundTasks):
    user_info = hedge_adapter.find_apikey_by_user_name(user_name)
    if user_info is None:
        background_tasks.add_task(admin_logger.log_error_message,
                                  "No matching data for username: %s " % user_name)
        return create_default_error()

    logger_with_discord = LoggerWithDiscord(user_info.discord_webhook_key)

    if hedge == "ON":
        binance_client = BinanceFuturesClient(user_info.binance_api_key,
                                              user_info.binance_api_secret)

        # binance short
        binance_short_res = binance_client.request_order_with_conditions(base, "SELL", "MARKET",
                                                                         amount,
                                                                         leverage=user_info.binance_leverage)

        if binance_short_res.status != "FILLED":
            binance_short_res = binance_client.wait_until_order_done(binance_short_res)

        hedge_adapter.save_current_hedge_from_binance(user_name, base,
                                                      user_info.binance_leverage,
                                                      binance_short_res)

        upbit_client = UpbitClient(user_info.upbit_api_key,
                                   user_info.upbit_api_secret)

        # upbit_buy_res = upbit_client.request_buy_order(base, user_info.krw_amount_to_buy)
        upbit_buy_res = upbit_client.request_order_with_amount(base, "BUY", amount)
        if not OrderState.is_order_completed(upbit_buy_res):
            upbit_buy_res = upbit_client.wait_until_order_done(upbit_buy_res)

        upbit_amount = float(upbit_buy_res.get("executed_volume"))

        hedge_adapter.save_current_hedge_from_upbit(user_name, base, upbit_buy_res)

        upbit_buy_krw = float(upbit_buy_res.get("price"))
        binance_short_usd = binance_short_res.cumQuote

        background_tasks.add_task(logger_with_discord.log_hedge_message,
                                  "binance", base, quote,
                                  amount,
                                  upbit_amount,
                                  upbit_buy_krw,
                                  binance_short_usd * 1350,
                                  hedge)

        return {"result": "success"}

    elif hedge == "OFF":
        hedge_records = hedge_adapter.find_hedge_by_user_name(user_name)

        upbit_amount = 0
        binance_amount = 0

        for rec in hedge_records:
            if rec.exchange == "Binance":
                binance_amount += rec.amount
            elif rec.exchange == "Upbit":
                upbit_amount += rec.amount
            else:
                background_tasks.add_task(admin_logger.log_error_message,
                                          "Not available exchange name: %s " % rec.exchange)
                background_tasks.add_task(logger_with_discord.log_error_message,
                                          "Not available exchange name: %s " % rec.exchange)
                return create_default_error()

        if upbit_amount == 0 or binance_amount == 0:
            background_tasks.add_task(logger_with_discord.log_message(
                "종료할 수량이 없습니다. Upbit: %d, Binance: %d" % (upbit_amount, binance_amount)))
            return create_default_error()

        upbit_client = UpbitClient(user_info.upbit_api_key,
                                   user_info.upbit_api_secret)

        upbit_sell_res = upbit_client.request_sell_order(base, upbit_amount)
        if not OrderState.is_order_completed(upbit_sell_res):
            upbit_sell_res = upbit_client.wait_until_order_done(upbit_sell_res)

        hedge_adapter.save_close_history_from_upbit(user_name, base, upbit_sell_res)

        binance_client = BinanceFuturesClient(user_info.binance_api_key,
                                              user_info.binance_api_secret)

        # binance close
        binance_close_res = binance_client.request_order_with_conditions(base, "BUY", "MARKET",
                                                                         binance_amount,
                                                                         leverage=user_info.binance_leverage)

        if binance_close_res.status != "FILLED":
            binance_close_res = binance_client.wait_until_order_done(binance_close_res)

        hedge_adapter.save_close_history_from_binance(user_name, base, user_info.binance_leverage,
                                                      binance_close_res)

        upbit_sell_price_krw = 0
        for trade in upbit_sell_res.get("trades"):
            upbit_sell_price_krw += float(trade.get("funds"))

        binance_close_price_usd = binance_close_res.cumQuote
        binance_close_amount = binance_close_res.origQty

        hedge_adapter.calculate_and_save_profit(user_name, base, user_info.binance_leverage, binance_amount,
                                                upbit_sell_price_krw,
                                                binance_close_price_usd * 1350,
                                                hedge_records)
        hedge_adapter.clear_current_hedge(hedge_records)

        background_tasks.add_task(logger_with_discord.log_hedge_message,
                                  "binance", base, quote,
                                  binance_close_amount,
                                  upbit_amount,
                                  binance_close_price_usd * 1350,
                                  upbit_sell_price_krw,
                                  hedge)

        return {"result": "success"}


ENVIRON_BINANCE_KEY = "BINANCE_KEY"
ENVIRON_BINANCE_SECRET = "BINANCE_SECRET"
ENVIRON_UPBIT_KEY = "UPBIT_KEY"
ENVIRON_UPBIT_SECRET = "UPBIT_SECRET"

if __name__ == '__main__':
    pass
    # symbol = "BTCUSDT"
    # binance_client = BinanceFuturesClient(key=os.getenv(ENVIRON_BINANCE_KEY),
    #                                       secret=os.getenv(ENVIRON_BINANCE_SECRET))
    #
    # upbit_client = UpbitClient(os.getenv(ENVIRON_UPBIT_KEY), os.getenv(ENVIRON_UPBIT_SECRET))

    # binance_client.create_order_with_conditions(symbol, "SELL", "MARKET", 0.003, leverage=10)
    # binance_client.cancel_order(symbol, 261724492140)

    # res = um_futures_client.account()
    # res = um_futures_client.funding_rate(symbol = "BTCUSDT")

    # print(json.dumps(res))

    # res = binance_client.client.query_order(
    #     symbol="BTCUSDT", orderId = 261724492140
    # )
    # res = um_futures_client.get_position_mode()
    # res = um_futures_client.get_all_orders(symbol = "BTCUSDT")

    # print(res)
    # res = upbit_client.get_chance("KRW-BTC")
    # res = pyupbit.get_current_price("KRW-BTC")
    # won = res * 0.006
    # import pdb
    # pdb.set_trace()
    # ret = upbit_client.calculate_buy_price_from_amount_plus_fee("KRW-BTC", 0.001)
    # res = upbit_client.create_order("KRW-BTC", "SELL", 0.00099972)

    # res = upbit_client.client.get_order("7c10b104-5cb8-4b4a-ab82-846541e6e072")
    # print(res);
    # print(won)
    # print(json.dumps(res))
