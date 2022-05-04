from backtesting.lib import TrailingStrategy, crossover
from backtesting.test import SMA
from talib import ADX, ATR, EMA, RSI


class RsiAdx(TrailingStrategy):
    def init(self):
        close = self.data.Close
        self.ema1 = self.I(EMA, close, 200)
        self.rsi = self.I(RSI, close)
        self.adx = self.I(ADX, self.data.High, self.data.Low, self.data.Close)
        self.adxMA = self.I(SMA, self.adx, 14)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)

    def next(self):
        if (
            crossover(75, self.rsi)
            and self.adx > 20
            and self.adx > self.adxMA
            and self.data.Close > self.ema1
        ):
            self.buy(
                tp=self.data.Close[-1] + self.atr[-1] * 1.5,
                sl=self.data.Close[-1] - self.atr[-1] * 2,
            )
        elif (
            crossover(self.rsi, 25)
            and self.adx > 20
            and self.adx > self.adxMA
            and self.data.Close < self.ema1
        ):
            self.sell(
                tp=self.data.Close[-1] - self.atr[-1] * 6.5,
                sl=self.data.Close[-1] + self.atr[-1] * 2,
            )
