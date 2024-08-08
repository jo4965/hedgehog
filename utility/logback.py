import sys
from datetime import datetime, timedelta
from dhooks import Webhook, Embed
from loguru import logger
from devtools import debug, pformat
import traceback
import os

from dotenv import load_dotenv

load_dotenv()

logger.remove(0)
logger.add(
    "./log/hedgehog.log",
    rotation="1 days",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
)


def parse_time(utc_timestamp):
    timestamp = utc_timestamp + timedelta(hours=9).seconds
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%y-%m-%d %H:%M:%S")


def logger_test():
    date = parse_time(datetime.utcnow().timestamp())
    logger.info(date)


class LoggerWithDiscord:
    def __init__(self, user_webhook_url):
        try:
            self.discord_hook = Webhook(user_webhook_url)
        except Exception as e:
            print("웹훅 URL이 유효하지 않습니다: ", user_webhook_url)

    def log_message(self, message="None", embed: Embed = None):
        if self.discord_hook:
            if embed:
                self.discord_hook.send(embed=embed)
            else:
                self.discord_hook.send(message)
        else:
            logger.info(message)
            print(message)

    def log_hedge_on_message(self, upbit_amount, upbit_buy_krw,
                             one_dollar_into_krw):
        date = parse_time(datetime.utcnow().timestamp())
        embed = Embed(title="헷지 시작", description="", color=0x0000FF)
        embed.add_field(name="일시", value="20" + str(date), inline=False)

        upbit_usdt_price = upbit_buy_krw / upbit_amount

        embed.add_field(
            name="비교",
            value=f"현재 환율: {one_dollar_into_krw}\nTether 가격: {round(upbit_usdt_price, 1)}원",
            inline=False,
        )

        embed.add_field(
            name="주문 정보",
            value=f"Tether 주문량: {upbit_amount}개\n총 가격: {round(upbit_buy_krw)}원",
            inline=False,
        )

        kimp_krw = upbit_usdt_price - one_dollar_into_krw
        kimp_percent = kimp_krw / one_dollar_into_krw * 100

        embed.add_field(
            name="김프",
            value=f"헷지 시작시 김프: {round(kimp_percent, 2)}%, {round(kimp_krw)}원",
            inline=False,
        )
        self.log_message("nothing", embed)

    def log_hedge_off_message(self, upbit_amount,
                              upbit_entry_krw_price, upbit_close_krw_price,
                              one_dollar_into_krw):

        date = parse_time(datetime.utcnow().timestamp())
        embed = Embed(title="헷지 종료", description="", color=0x0000FF)
        embed.add_field(name="일시", value="20" + str(date), inline=False)
        embed.add_field(name="환율", value=f"{one_dollar_into_krw}원", inline=False)

        embed.add_field(
            name="수량",
            value=f"UPBIT: {upbit_amount}",
            inline=False,
        )

        embed.add_field(
            name="손익 계산",
            value=f"Entry: {round(upbit_entry_krw_price)}원\nClose: {round(upbit_close_krw_price)}원\nProfit: {round(upbit_close_krw_price - upbit_entry_krw_price)}",
            inline=False,
        )

        self.log_message("nothing", embed)

    def log_error_message(self, error, name):
        embed = Embed(title=f"{name} 에러", description=f"[{name} 에러가 발생했습니다]\n{error}", color=0xFF0000)
        logger.error(f"{name} [에러가 발생했습니다]\n{error}")
        self.log_message(embed=embed)

    def log_validation_error_message(self, msg):
        logger.error(f"검증 오류가 발생했습니다\n{msg}")
        self.log_message(msg)
