from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import pandas as pd

API_KEY = "Enter Your Own Key"
API_SECRET="Enter Your Own Key"


client = StockHistoricalDataClient(API_KEY, API_SECRET)

symbols = ['TSLA', 'AAPL', 'NVDA']
start = datetime(2025, 4,28)
end = datetime(2025,4,30)# adjust to any date range you want

for symbol in symbols:
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        start=start,
        end=end,
        timeframe=TimeFrame.Minute
    )
    bars = client.get_stock_bars(request).df
    df = bars[bars.index.get_level_values(0) == symbol].reset_index()
    df.rename(columns={'timestamp': 'timestamp'}, inplace=True)
    df.to_csv(f"minute_{symbol.lower()}.csv", index=False)
    print(f"Saved: minute_{symbol.lower()}.csv")