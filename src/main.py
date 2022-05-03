from datetime import datetime, timedelta

import mplfinance as mpf
from backtesting import Backtest
from backtesting.test import GOOG
from binance.client import Client
from formatters.binance_formatter import format_binance_data
from strategies.sma_cross import SmaCross

client = Client()
from_date = datetime.now() - timedelta(days=600)
candles = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1DAY,
    start_str=from_date.isoformat(),
)

chart_data = format_binance_data(candles)

# mpf.plot(chart_data.tail(50), type="candle")

bt = Backtest(chart_data, SmaCross, cash=100000, commission=0.002)

results = bt.run()
print(results)
bt.plot(filename="src/results/SmaCross")
