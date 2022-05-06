import time
from datetime import datetime, timedelta

import ccxt
import pandas as pd
import schedule
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from formatters.binance_formatter import format_binance_data
from talib import ADX, ATR, EMA, RSI, SMA


def run_bot():
    symbol = "BTCUSDT"
    client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
    from_date = datetime.now() - timedelta(days=20)
    candles = client.get_historical_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str=from_date.isoformat(),
    )

    chart_data = format_binance_data(candles)
    close = chart_data["Close"]
    high = chart_data["High"]
    low = chart_data["Low"]

    ema1 = EMA(close, 200)
    rsi = RSI(close)
    adx = ADX(high, low, close)
    adxMA = SMA(adx, 14)
    atr = ATR(high, low, close, 14)

    last_ema1 = ema1[-1]
    last_rsi = rsi[-1]
    last_adx = adx[-1]
    last_adx_ma = adxMA[-1]
    last_close = close[-1]

    order = client.create_test_order(
        symbol=symbol,
        side="BUY",
        type="limit",
        timeInForce="GTC",
        quantity=0.002,
        price=last_close + 50,
    )
    print(order)
    # if (
    #     last_ema1 < last_close
    #     and last_adx > 20
    #     and last_adx > last_adx_ma
    #     and last_rsi > 75
    # ):
    #     print("BUY")
    #     # client.create_test_order(
    #     #     symbol,
    #     #     "BUY",
    #     #     "limit",
    #     #     "GTC",
    #     #     0.002,
    #     #     close + 50,
    #     # )
    # elif (
    #     last_ema1 > last_close
    #     and last_adx > 20
    #     and last_adx > last_adx_ma
    #     and last_rsi < 25
    # ):
    #     print("SELL")

    #     # client.create_test_order(
    #     #     symbol,
    #     #     "SELL",
    #     #     "limit",
    #     #     "GTC",
    #     #     0.002,
    #     #     close - 50,
    #     # )


schedule.every(10).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)
