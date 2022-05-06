from backtesting.lib import TrailingStrategy, crossover
from backtesting.test import SMA
from talib import ADX, ATR, EMA, RSI


class FlatMarket(TrailingStrategy):
    bars_back = 10

    def init(self):
        close = self.data.Close
        self.ema1 = self.I(EMA, close, 200)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)

    def next(self):
        highs_and_lows = []
        for i in range(1, self.bars_back):
            highs_and_lows.append(self.data.High[-i])
            highs_and_lows.append(self.data.Low[-i])

        series_max = max(highs_and_lows)
        series_min = min(highs_and_lows)
        print("------------------")
        print(series_max)
        print(series_min)
        print(self.data.Close[-1])
        print("------------------")
        print(series_max - series_min)
        print(self.data.Close[-1] * 0.7 / 100)

        if series_max - series_min < self.data.Close[-1] * 0.7 / 100:
            self.buy(
                limit=self.data.Close[-1] + self.atr[-1] * 4,
                tp=self.data.Close[-1] + self.atr[-1] * 3,
                sl=self.data.Close[-1] - self.atr[-1],
            )
            self.sell(
                limit=self.data.Close[-1] - self.atr[-1] * 4,
                tp=self.data.Close[-1] - self.atr[-1] * 3,
                sl=self.data.Close[-1] + self.atr[-1],
            )
