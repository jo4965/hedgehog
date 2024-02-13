from exchange.binance import OrderResponse
from utility import pocket


def find_apikey_by_user_name(user_name: str):
    records = pocket.get_full_list("api_key",
                                   query_params={
                                       "filter": "user_name = '%s'" % user_name
                                   })

    for rec in records:
        return rec

    return None


"""
    rec.user_name,
    rec.discord_webhook_key
    rec.binance_api_key,
    rec.binance_api_secret,
    rec.upbit_api_key,
    rec.upbit_api_secert,
    rec.binance_leverage,
    rec.krw_amount_to_buy
"""


def find_hedge_by_user_name(user_name: str):
    records = pocket.get_full_list("current_hedge",
                                   query_params={
                                       "filter": "user_name = '%s'" % user_name
                                   })

    return records


def save_current_hedge(user_name: str, base, exchange, amount, KRW_price: float, USD_price: float):
    pocket.create("current_hedge",
                  {
                      "user_name": user_name,
                      "base": base,
                      "exchange": exchange,
                      "amount": amount,
                      "KRW_price": KRW_price,
                      "USD_price": USD_price
                  })


def save_history(user_name: str,
                 base,
                 exchange, leverage,
                 when: str,
                 amount, KRW_price: float, USD_price: float):
    pocket.create("history",
                  {
                      "user_name": user_name,
                      "base": base,
                      "exchange": exchange,
                      "leverage": leverage,
                      "when": when,
                      "amount": amount,
                      "KRW_price": KRW_price,
                      "USD_price": USD_price
                  })


def save_current_hedge_from_upbit(user_name, base, upbit_response, one_dollar_into_krw: float):
    bought_amount = float(upbit_response.get("executed_volume"))
    bought_price_krw = float(upbit_response.get("price"))

    save_current_hedge(user_name, base, "Upbit",
                       bought_amount,
                       round(bought_price_krw),
                       round(bought_price_krw / one_dollar_into_krw))  # dollar exchange

    save_history(user_name, base, "Upbit", 1, "entry",
                 bought_amount,
                 round(bought_price_krw),
                 round(bought_price_krw / one_dollar_into_krw))  # dollar exchange


def save_current_hedge_from_binance(user_name, base, leverage, binance_response: OrderResponse,
                                    one_dollar_into_krw: float):
    bought_amount = binance_response.origQty
    bought_price_usd = binance_response.cumQuote

    save_current_hedge(user_name, base, "Binance",
                       bought_amount,
                       round(bought_price_usd * one_dollar_into_krw),
                       round(bought_price_usd))  # dollar exchange

    save_history(user_name, base, "Binance", leverage, "entry",
                 bought_amount,
                 round(bought_price_usd * one_dollar_into_krw),
                 round(bought_price_usd))  # dollar exchange


def save_close_history_from_upbit(user_name, base, upbit_response, one_dollar_into_krw):
    sell_amount = float(upbit_response.get("executed_volume"))
    sell_price_krw = 0.0

    for trade in upbit_response.get("trades"):
        sell_price_krw += float(trade.get("funds"))

    save_history(user_name, base, "Upbit", 1, "close",
                 sell_amount,
                 round(sell_price_krw),
                 round(sell_price_krw / one_dollar_into_krw))  # dollar exchange


def save_close_history_from_binance(user_name, base, leverage, binance_response: OrderResponse,
                                    one_dollar_into_krw: float):
    close_amount = binance_response.origQty
    close_price_usd = binance_response.cumQuote

    save_history(user_name, base, "Binance", leverage, "close",
                 close_amount,
                 round(close_price_usd * one_dollar_into_krw),
                 round(close_price_usd))  # dollar exchange


def clear_current_hedge(records):
    for rec in records:
        pocket.delete("current_hedge", rec.id)


def calculate_and_save_profit(user_name, base, leverage, amount,
                              entry_kimp_krw, close_kimp_krw):
    pocket.create("profit",
                  {
                      "user_name": user_name,
                      "base": base,
                      "leverage": leverage,
                      "amount": amount,
                      "KRW_entry_kimp": round(entry_kimp_krw),
                      "KRW_close_kimp": round(close_kimp_krw),
                      "KRW_kimp_profit": round(close_kimp_krw - entry_kimp_krw),
                  })


def calculate_entry_kimp(hedge_records):
    upbit_buy_price_krw = 0.0
    binance_entry_price_krw = 0.0
    for rec in hedge_records:
        if rec.exchange == "Binance":
            binance_entry_price_krw += rec.krw_price
        elif rec.exchange == "Upbit":
            upbit_buy_price_krw += rec.krw_price

    entry_kimp_krw = upbit_buy_price_krw - binance_entry_price_krw
    entry_kimp_percent = entry_kimp_krw / binance_entry_price_krw * 100
    return (entry_kimp_krw, entry_kimp_percent)
