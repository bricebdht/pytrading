import time
from datetime import datetime, timedelta

import schedule
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from formatters.binance_formatter import format_binance_data
from talib import ADX, ATR, EMA, RSI, SMA


def create_order_with_sl_and_tp(
    client: Client,
    side: str,
    quantity: float,
    price: float,
    sl_price: float,
    tp_price: float,
    symbol="BTCUSDT",
):
    # ORDER
    client.create_test_order(
        symbol=symbol,
        side=side,
        type="limit",
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


def clean_open_orders(client: Client, symbol="BTCUSDT"):
    open_orders = client.futures_get_open_orders(symbol=symbol)
    if len(open_orders) == 1 and open_orders[0]["type"] in ["STOP", "TAKE_PROFIT"]:
        print("----- Canceling order -----")
        print(open_orders[0])
        client.futures_cancel_all_open_orders(symbol=symbol)


def run_bot():
    symbol = "BTCUSDT"
    client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
    clean_open_orders(client)
    from_date = datetime.now() - timedelta(days=2)
    candles = client.get_historical_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str=from_date.isoformat(),
        klines_type="FUTURES",
    )

    chart_data = format_binance_data(candles)
    close = chart_data["Close"]
    high = chart_data["High"]
    low = chart_data["Low"]

    ema1 = EMA(close, 200)
    rsi = RSI(close)
    adx = ADX(high, low, close)
    adx_ma = SMA(adx, 14)
    atr = ATR(high, low, close, 14)

    last_ema1 = ema1[-1]
    last_rsi = rsi[-1]
    last_adx = adx[-1]
    last_adx_ma = adx_ma[-1]
    last_close = close[-1]

    order_price = close[0]
    if (
        last_ema1 < last_close
        and last_adx > 20
        and last_adx > last_adx_ma
        and last_rsi > 75
    ):
        print("BUY")
        sl_price = order_price - 2 * atr[0]
        tp_price = order_price + 1.5 * atr[0]
        create_order_with_sl_and_tp(
            client, "BUY", 0.001, order_price, sl_price, tp_price
        )
    elif (
        last_ema1 > last_close
        and last_adx > 20
        and last_adx > last_adx_ma
        and last_rsi < 25
    ):
        print("SELL")
        sl_price = order_price + 2 * atr[0]
        tp_price = order_price - 1.5 * atr[0]
        create_order_with_sl_and_tp(
            client, "SELL", 0.001, order_price, sl_price, tp_price
        )


schedule.every(10).seconds.do(run_bot)


while True:
    schedule.run_pending()
    time.sleep(1)
