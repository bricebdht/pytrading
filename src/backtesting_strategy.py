from datetime import datetime, timedelta

from backtesting import Backtest
from binance.client import Client
from formatters.binance_formatter import format_binance_data
from strategies.flat_market import FlatMarket
from strategies.rsi_adx import RsiAdx

client = Client()
from_date = datetime.now() - timedelta(days=125)
candles = client.get_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_30MINUTE,
    start_str=from_date.isoformat(),
)

chart_data = format_binance_data(candles)


bt = Backtest(
    chart_data, FlatMarket, cash=5000000, commission=0.06 / 100, exclusive_orders=True
)

results = bt.run()
results.to_csv("src/results/stats.csv")

bt.plot(filename="src/results/charts")
