import json
from exchange import UpbitClient, BinanceFuturesClient, OrderState
from utility.logback import LoggerWithDiscord
from dto.models import HedgeData
import hedge_adapter
import time
import ipaddress
import traceback
from fastapi import FastAPI, Request, status, BackgroundTasks
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
import os
import requests
import math
from dotenv import load_dotenv
import sys
import traceback
from utility import pocket

load_dotenv()

VERSION = "beta"
app = FastAPI(default_response_class=ORJSONResponse)
admin_logger = LoggerWithDiscord(os.getenv("DISCORD_WEBHOOK_URL"))


def floor_with_precision(number, precision):
    return math.floor(number * (10 ** precision)) / 10 ** precision


def request_one_dollar_into_krw():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'

    exchange = requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']


@app.on_event("startup")
async def startup():
    admin_logger.log_message(f"Hedgehog %s 실행 완료!" % VERSION)


whitelist = ["182.231.107.125", "52.89.214.238", "34.212.75.30",
             "54.218.53.128", "52.32.178.7", "127.0.0.1", "125.178.123.80"]


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

@app.get("/hi2")
async def welcome2():
    try:
        pocket.auth()
    except Exception as e:
        traceback.print_exc()

    return "hi2!"

def enter_hedge(user_name, base, how_much, one_dollar_into_krw, kimp_percent, background_tasks):
    user_info = hedge_adapter.find_apikey_by_user_name(user_name)

    if user_info is None:
        background_tasks.add_task(admin_logger.log_error_message,
                                  "No matching data for username: %s " % user_name,
                                  "Request Body")
        return create_default_error()

    logger_with_discord = LoggerWithDiscord(user_info.discord_webhook_key)

    # Upbit buy
    upbit_client = UpbitClient(user_info.upbit_api_key,
                               user_info.upbit_api_secret)

    # upbit_buy_res = upbit_client.request_buy_order(base, user_info.krw_amount_to_buy)
    while True:
        try:
            upbit_buy_res = upbit_client.request_order_with_money(base, "BUY", how_much)
            if not OrderState.is_order_completed(upbit_buy_res):
                upbit_buy_res = upbit_client.wait_until_order_done(upbit_buy_res)

            break
        except Exception as e:
            background_tasks.add_task(logger_with_discord.log_message,
                                      "업비트 매수에 실패했습니다. 재시도 합니다.\n 에러: %s\n Traceback: %s" % (
                                      str(e), traceback.format_exc()))
            time.sleep(1)

    hedge_adapter.save_current_hedge_from_upbit(user_name, base, upbit_buy_res, one_dollar_into_krw)

    upbit_buy_krw = float(upbit_buy_res.get("price"))
    upbit_amount = float(upbit_buy_res.get("executed_volume"))

    background_tasks.add_task(logger_with_discord.log_hedge_on_message,
                              upbit_amount,
                              upbit_buy_krw,
                              one_dollar_into_krw,
                              kimp_percent)

    return {"result": "success"}


def close_hedge(user_name, base, one_dollar_into_krw, kimp_percent, background_tasks):
    user_info = hedge_adapter.find_apikey_by_user_name(user_name)

    if user_info is None:
        background_tasks.add_task(admin_logger.log_error_message,
                                  "No matching data for username: %s " % user_name,
                                  "Request Body")
        return create_default_error()

    logger_with_discord = LoggerWithDiscord(user_info.discord_webhook_key)

    hedge_records = hedge_adapter.find_hedge_by_user_name(user_name)

    upbit_amount = 0
    upbit_buy_price_krw = 0.0
    upbit_buy_price_usd = 0.0

    for rec in hedge_records:
        if rec.exchange == "Upbit":
            upbit_amount += rec.amount
            upbit_buy_price_krw += rec.krw_price
            upbit_buy_price_usd += rec.usd_price
        else:
            background_tasks.add_task(admin_logger.log_error_message,
                                      "Not available exchange name: %s " % rec.exchange,
                                      "DB Exchange Name")
            background_tasks.add_task(logger_with_discord.log_error_message,
                                      "Not available exchange name: %s " % rec.exchange,
                                      "DB Exchange Name")
            return create_default_error()

    if upbit_amount == 0:
        background_tasks.add_task(logger_with_discord.log_message,
                                  "종료할 수량이 없습니다. Upbit: %d" % upbit_amount)
        return create_default_error()

    upbit_client = UpbitClient(user_info.upbit_api_key,
                               user_info.upbit_api_secret)

    upbit_sold_amount, upbit_sell_price_krw = upbit_client.split_request_sell_order(base, upbit_amount)
    hedge_adapter.save_close_history_from_upbit(user_name, base, upbit_sold_amount, upbit_sell_price_krw,
                                                one_dollar_into_krw)

    former_one_dollar_into_krw = upbit_buy_price_krw / upbit_buy_price_usd
    upbit_tether_price = upbit_buy_price_krw / upbit_amount

    entry_kimp_krw = upbit_tether_price - former_one_dollar_into_krw
    entry_kimp_percent = entry_kimp_krw / former_one_dollar_into_krw * 100

    close_kimp_krw = kimp_percent * one_dollar_into_krw / 100

    close_kimp_krw_with_fee = (upbit_sell_price_krw * 0.9995) / upbit_amount

    hedge_adapter.calculate_and_save_profit(user_name, base, upbit_sold_amount,
                                            entry_kimp_krw,
                                            close_kimp_krw_with_fee)

    hedge_adapter.clear_current_hedge(hedge_records)

    background_tasks.add_task(logger_with_discord.log_hedge_off_message,
                              upbit_sold_amount,
                              upbit_buy_price_krw, upbit_sell_price_krw,
                              one_dollar_into_krw, kimp_percent)

    return {"result": "success"}


@app.post("/hedge")
async def hedge(hedge_data: HedgeData, background_tasks: BackgroundTasks):
    # zenike
    user_name = hedge_data.user_name

    # BTC
    base = hedge_data.base

    how_much = hedge_data.how_much

    # ON or OFF
    hedge = hedge_data.hedge
    one_dollar_krw = hedge_data.one_dollar_krw

    kimp = hedge_data.kimp

    try:
        return start_hedge(user_name, base, how_much, one_dollar_krw, kimp, hedge, background_tasks)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        background_tasks.add_task(admin_logger.log_error_message,
                                  "Unknown error: %s %s" % (str(e), traceback.format_exc()),
                                  "Unknown error")

        return create_default_error()


def start_hedge(user_name, base, how_much, one_dollar_krw, kimp, hedge, background_tasks: BackgroundTasks):
    if hedge == "ON":
        return enter_hedge(user_name, base, how_much, one_dollar_krw, kimp, background_tasks)
    elif hedge == "OFF":
        return close_hedge(user_name, base, one_dollar_krw, kimp, background_tasks)


if __name__ == '__main__':
    pass
