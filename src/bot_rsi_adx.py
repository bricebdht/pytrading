import time
from datetime import datetime, timedelta

import requests
import schedule
import telegram_send
from binance.client import Client
from binance.enums import HistoricalKlinesType
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from formatters.binance_formatter import format_binance_data
from talib import ADX, ATR, EMA, RSI, SMA

OPTIMAL_PARAMETERS = {
    "5m": {
        "interval": Client.KLINE_INTERVAL_5MINUTE,
        "atr_length": 8,
        "long_sl_multiplier": 2,
        "long_rr_ratio": 2,
        "short_sl_multiplier": 2,
        "short_rr_ratio": 2,
    },
    "15m": {
        "interval": Client.KLINE_INTERVAL_15MINUTE,
        "atr_length": 11,
        "long_sl_multiplier": 1,
        "long_rr_ratio": 2,
        "short_sl_multiplier": 2,
        "short_rr_ratio": 2,
    },
    "30m": {
        "interval": Client.KLINE_INTERVAL_30MINUTE,
        "atr_length": 14,
        "long_sl_multiplier": 2,
        "long_rr_ratio": 1.5,
        "short_sl_multiplier": 2,
        "short_rr_ratio": 2,
    },
}

TIMEFRAME = "30m"


def create_order_with_sl_and_tp(
    client: Client,
    side: str,
    quantity: float,
    price: float,
    sl_price: float,
    tp_price: float,
    symbol="BTCUSDT",
):
    price = round(price)
    sl_price = round(sl_price)
    tp_price = round(tp_price)
    # ORDER
    client.futures_create_order(
        symbol=symbol,
        side=side,
        type="LIMIT",
        timeInForce="GTC",
        quantity=quantity,
        price=price,
    )
    # STOP LOSS
    close_position_side = "SELL" if side == "BUY" else "SELL"
    client.futures_create_order(
        symbol=symbol,
        side=close_position_side,
        type="STOP",
        timeInForce="GTC",
        quantity=quantity,
        reduceOnly=True,
        price=sl_price,
        stopPrice=sl_price,
    )
    # TAKE PROFIT
    client.futures_create_order(
        symbol=symbol,
        side=close_position_side,
        type="TAKE_PROFIT",
        timeInForce="GTC",
        quantity=quantity,
        reduceOnly=True,
        price=tp_price,
        stopPrice=tp_price,
    )
    print(f"----- {side} order created -----")
    print(f"Price: {price}")
    print(f"Stop loss: {sl_price}")
    print(f"Take profit: {tp_price}")
    telegram_send.send(
        messages=[
            f"----- {side} order created -----",
            f"Price: {price}",
            f"Stop loss: {sl_price}",
            f"Take profit: {tp_price}",
        ]
    )


def clean_open_orders(client: Client, symbol="BTCUSDT"):
    try:
        open_orders = client.futures_get_open_orders(symbol=symbol)
    except requests.exceptions.Timeout:
        print("----- Request timeout: futures_get_open_orders -----")
    if len(open_orders) == 1 and open_orders[0]["type"] in ["STOP", "TAKE_PROFIT"]:
        print("----- Canceling order -----")
        print(open_orders[0])
        telegram_send.send(
            messages=[
                "----- Canceling order -----",
                open_orders[0],
            ]
        )
        client.futures_cancel_all_open_orders(symbol=symbol)


def run_bot():
    symbol = "BTCUSDT"
    client = Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
        requests_params={"timeout": 20},
    )
    clean_open_orders(client)
    from_date = datetime.now() - timedelta(days=6)
    try:
        candles = client.get_historical_klines(
            symbol=symbol,
            interval=TIMEFRAME,
            start_str=from_date.isoformat(),
            klines_type=HistoricalKlinesType.FUTURES,
        )
    except requests.exceptions.Timeout:
        print("----- Request timeout: get_historical_klines -----")

    chart_data = format_binance_data(candles)
    close = chart_data["Close"]
    high = chart_data["High"]
    low = chart_data["Low"]

    ema1 = EMA(close, 200)
    rsi = RSI(close)
    adx = ADX(high, low, close)
    adx_ma = SMA(adx, 14)
    atr = ATR(high, low, close, OPTIMAL_PARAMETERS[TIMEFRAME]["atr_length"])

    last_ema1 = ema1[-2]
    last_rsi = rsi[-2]
    last_adx = adx[-2]
    last_adx_ma = adx_ma[-2]
    last_atr = atr[-2]
    last_close = close[-2]

    current_price = close[-1]

    now = datetime.now()
    minutes = int(now.strftime("%M"))
    seconds = int(now.strftime("%S"))
    if minutes % 15 == 0 and seconds <= 12:
        print(
            f"{now.strftime('%m/%d/%YT%H:%M:%S')} - I'm alive. Current price: {current_price}"
        )
        telegram_send.send(messages=[f"I'm alive. Current price: {current_price}"])
    if (
        last_ema1 < last_close
        and last_adx > 20
        and last_adx > last_adx_ma
        and last_rsi > 75
    ):
        print(f"{now.strftime('%m/%d/%YT%H:%M:%S')} - BUY")
        telegram_send.send(messages=["BUY"])
        sl_price = (
            current_price
            - OPTIMAL_PARAMETERS[TIMEFRAME]["long_sl_multiplier"] * last_atr
        )
        tp_price = (
            current_price
            + OPTIMAL_PARAMETERS[TIMEFRAME]["long_sl_multiplier"]
            * OPTIMAL_PARAMETERS[TIMEFRAME]["long_rr_ratio"]
            * last_atr
        )
        create_order_with_sl_and_tp(
            client,
            "BUY",
            0.001,
            current_price
            + last_atr
            / 2,  # Set starting price above current price to increase the chance to see the order filled
            sl_price,
            tp_price,
        )
    elif (
        last_ema1 > last_close
        and last_adx > 20
        and last_adx > last_adx_ma
        and last_rsi < 25
    ):
        print(f"{now.strftime('%m/%d/%YT%H:%M:%S')} - SELL")
        telegram_send.send(messages=["SELL"])
        sl_price = (
            current_price
            + OPTIMAL_PARAMETERS[TIMEFRAME]["short_sl_multiplier"] * last_atr
        )
        tp_price = (
            current_price
            - OPTIMAL_PARAMETERS[TIMEFRAME]["short_sl_multiplier"]
            * OPTIMAL_PARAMETERS[TIMEFRAME]["short_rr_ratio"]
            * last_atr
        )
        create_order_with_sl_and_tp(
            client,
            "SELL",
            0.001,
            current_price
            - last_atr
            / 2,  # Set starting price below current price to increase the chance to see the order filled
            sl_price,
            tp_price,
        )


schedule.every(10).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)
