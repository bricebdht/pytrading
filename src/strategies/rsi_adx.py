import pandas as pd
from backtesting.lib import SignalStrategy, TrailingStrategy
from backtesting.test import SMA
from talib import ADX, EMA, RSI


class RsiAdx(SignalStrategy, TrailingStrategy):
    n1 = 20
    n2 = 50

    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()

        def rsi_indicator():
            rsi = RSI(self.data.Close)
            return rsi, SMA(rsi, 14)

        def adx_indicator():
            adx = ADX(self.data.High, self.data.Low, self.data.Close)
            return adx, SMA(adx, 14)

        rsi = RSI(self.data.Close)
        rsiMA = SMA(rsi, 14)

        adx = ADX(self.data.High, self.data.Low, self.data.Close)
        adxMA = SMA(adx, 14)

        ema = EMA(self.data.Close, timeperiod=200)

        # Precompute the indicators
        ema = self.I(EMA, self.data.Close, 200, overlay=True)
        rsi = self.I(rsi_indicator)

        adx = self.I(adx_indicator)

        # Where sma1 crosses sma2 upwards. Diff gives us [-1,0, *1*]
        signal = (
            (pd.Series(adx) > adxMA and pd.Series(rsi) > rsiMA)
            .astype(int)
            .diff()
            .fillna(0)
        )
        signal = signal.replace(-1, 0)  # Upwards/long only

        # Use 95% of available liquidity (at the time) on each order.
        # (Leaving a value of 1. would instead buy a single share.)
        entry_size = signal * 0.95

        # Set order entry sizes using the method provided by
        # `SignalStrategy`. See the docs.
        self.set_signal(entry_size=entry_size)

        # Set trailing stop-loss to 2x ATR using
        # the method provided by `TrailingStrategy`
        self.set_trailing_sl(2)
