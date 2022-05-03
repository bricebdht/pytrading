from datetime import datetime
from typing import List

import pandas as pd


def format_binance_data(klines: List[List[str]]):
    raw_data = pd.DataFrame(
        klines,
        columns=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "Close time",
            "Quote asset volume",
            "Number of trades",
            "Taker buy base asset volume",
            "Taker buy quote asset volume",
            "Can be ignored",
        ],
        dtype=float,
    )

    for i in raw_data.index:
        raw_data.at[i, "Date"] = datetime.fromtimestamp(raw_data.at[i, "Date"] / 1000)

    raw_data.index = pd.DatetimeIndex(raw_data["Date"])
    return raw_data[["Date", "Open", "High", "Low", "Close", "Volume"]]
