```markdown
# Algorithmic Trading System

A comprehensive Python-based algorithmic trading platform featuring real-time execution, market monitoring, and data analysis tools. Built with Alpaca Trade API and real-time data streams.

## 🚀 Features

### Core Trading Engine
- **Real-time Scalping Bot** - Multi-indicator strategy (RSI, MACD, EMA trends)s
- **Multi-Asset Portfolio** - Simultaneous monitoring of TSLA, AAPL, NVDA, META, AMZN
- **Risk Management** - Automated position sizing (1% portfolio) with stop-loss/take-profit
- **Paper Trading** - Full compatibility with Alpaca paper trading

### Market Intelligence
- **Global Market Status** - Real-time monitoring of 7 major stock exchanges
- **Historical Data Collector** - Bulk minute-data download for backtesting
- **WebSocket Streaming** - Low-latency real-time market data

### Analytics & Logging
- **Trade Analytics** - Comprehensive CSV logging with PnL tracking
- **Performance Metrics** - Entry/exit timing, position duration, profit analysis
- **Strategy Validation** - Paper trading mode for risk-free testing



## 📊 Trading Strategy

### Entry Signals
- **RSI Conditions**: <35 for long, >56 for short
- **MACD Confirmation**: MACD > Signal line for long, MACD < Signal for short  
- **Trend Analysis**: EMA crossover (20/50 period) for direction confirmation

### Exit Conditions
- **Take Profit**: 0.25% price movement
- **Stop Loss**: 0.15% price movement  
- **Time Limit**: Maximum 8-minute holding period
- **Position Size**: 1% of portfolio per trade

### Risk Management
```python
self.config = {
    "take_profit_pct": 0.0025,    # 0.25%
    "stop_loss_pct": 0.0015,      # 0.15%
    "max_hold_minutes": 8,
    "rsi_buy_threshold": 35,
    "position_size_pct": 0.01     # 1% of portfolio
}
```

## 🌍 Market Coverage

**Real-time monitoring of major exchanges:**
- 🇺🇸 NYSE/NASDAQ (US) - 9:30 AM - 4:00 PM ET
- 🇨🇦 Toronto (TSX) - 9:30 AM - 4:00 PM ET  
- 🇬🇧 London (LSE) - 8:00 AM - 4:30 PM GMT
- 🇩🇪 Frankfurt (FWB) - 8:00 AM - 8:00 PM CET
- 🇯🇵 Tokyo (TSE) - 9:00 AM - 3:00 PM JST
- 🇭🇰 Hong Kong (HKEX) - 9:30 AM - 4:00 PM HKT
- 🇨🇳 Shanghai (SSE) - 9:30 AM - 3:00 PM CST

## 📈 Data Collection

**Historical data features:**
- Minute-level OHLCV data
- Multi-symbol batch processing  
- Custom date range support
- CSV export for analysis
- Pandas DataFrame integration

```python
# Example: Download minute data for backtesting
symbols = ['TSLA', 'AAPL', 'NVDA']
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
```

## 🏛️ Market Status Utility

Real-time global market status checker that monitors trading hours across major exchanges:

```python
from market_status import get_live_market_status

# Check which markets are currently open
open_markets = get_live_market_status()
for market in open_markets:
    print(f"🟢 {market['market']} | Local Time: {market['local_time']}")
```

**Supported Markets:**
- **Americas**: NYSE/NASDAQ, TSX (Toronto)
- **Europe**: London (LSE), Frankfurt (FWB)  
- **Asia**: Tokyo (TSE), Hong Kong (HKEX), Shanghai (SSE)

**Features:**
- Real-time timezone conversion
- Business day detection (Mon-Fri)
- Extended hours support
- Local time display for each market

## 📊 Historical Data Collector

Batch data downloader for backtesting and analysis:

```python
# Download minute-level data for multiple symbols
python collect_historical_data.py
```

**Capabilities:**
- Minute-level OHLCV data from Alpaca
- Multi-symbol batch processing
- CSV export for easy analysis
- Custom date range support
- Pandas DataFrame integration

**Output:**
```
minute_tsla.csv
minute_aapl.csv  
minute_nvda.csv
```

**Use Cases:**
- Strategy backtesting
- Technical indicator development
- Market analysis and research

## 🎯 Core Trading Bot

### Live Scalping Bot Features:
```python
class LiveScalpingBot:
    def __init__(self):
        self.config = {
            "take_profit_pct": 0.0025,
            "stop_loss_pct": 0.0015, 
            "max_hold_minutes": 8,
            "rsi_buy_threshold": 35
        }
```

**Key Components:**
- Real-time WebSocket data streaming
- Automated entry/exit signal generation
- Position management and risk controls
- Comprehensive trade logging
- Performance analytics

## 📋 Requirements

```txt
alpaca-trade-api>=2.0.0
pandas>=1.5.0
numpy>=1.21.0
pytz>=2022.7
aiohttp>=3.8.0
yfinance>=0.2.0
python-dateutil>=2.8.0
```

## ⚠️ Important Disclaimers

**🚨 Educational Purpose Only**
- This system is for **portfolio demonstration and educational purposes**
- **PAPER TRADE ONLY** - Test thoroughly before considering live deployment
- Past performance does not guarantee future results
- Algorithmic trading carries substantial risk

**🔒 License & Usage**
```
PERSONAL USE LICENSE - PERMISSION REQUIRED
This repository is for portfolio display and educational viewing only.

STRICTLY PROHIBITED WITHOUT PERMISSION:
- Copying, modifying, or redistributing code
- Commercial use or deployment
- Forking or reproducing any component

Contact me for usage permissions.
```

## 🛡️ Risk Warning

- **Only use risk capital** you can afford to lose
- **Extensive paper trading** recommended before live deployment  
- **Monitor performance** continuously and adjust parameters
- **Understand all code** before execution in any environment

## 📞 Support

For questions about the code structure or to request usage permissions, please open an issue or contact me directly.

---

**Built with Python, Alpaca Trade API, and real-time data streams for educational demonstration.**
