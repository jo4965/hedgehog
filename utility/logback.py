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

    def log_hedge_message(self, exchange, base, quote, exchange_amount, upbit_amount, exchange_krw_price, upbit_krw_price, hedge):
        date = parse_time(datetime.utcnow().timestamp())
        hedge_type = "헷지" if hedge == "ON" else "헷지 종료"
        content = f"{hedge_type}: {base} ==> {exchange}:{exchange_amount} UPBIT:{upbit_amount}"
        embed = Embed(title="헷지", description=content, color=0x0000FF)
        embed.add_field(name="일시", value=str(date), inline=False)
        embed.add_field(name="거래소", value=f"{exchange}-UPBIT", inline=False)
        embed.add_field(name="심볼", value=f"{base}/{quote}-{base}/KRW", inline=False)
        embed.add_field(name="거래유형", value=hedge_type, inline=False)
        embed.add_field(
            name="수량",
            value=f"{exchange}:{exchange_amount} UPBIT:{upbit_amount}",
            inline=False,
        )

        embed.add_field(
            name="가격",
            value=f"{exchange}:{exchange_krw_price}원\n UPBIT:{upbit_krw_price}원",
            inline=False,
        )
        self.log_message(content, embed)

    def log_error_message(self, error, name):
        embed = Embed(title=f"{name} 에러", description=f"[{name} 에러가 발생했습니다]\n{error}", color=0xFF0000)
        logger.error(f"{name} [에러가 발생했습니다]\n{error}")
        self.log_message(embed=embed)

    def log_validation_error_message(self, msg):
        logger.error(f"검증 오류가 발생했습니다\n{msg}")
        self.log_message(msg)
