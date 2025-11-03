import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
import os
import csv
import yfinance as yf
import time

API_KEY = "Enter Your Own Key"
SECRET_KEY = "Enter Your Own Key"
BASE_URL = "https://paper-api.alpaca.markets"

LIVE_SYMBOLS = ['TSLA', 'AAPL', 'NVDA', 'META', 'AMZN']

class LiveScalpingBot:
    def __init__(self):
        self.client = TradingClient(API_KEY, SECRET_KEY, paper=True)
        self.data = {symbol: [] for symbol in LIVE_SYMBOLS}
        self.open_positions = {}
        self.csv_file = "live_trades_log.csv"
        self.last_update_time = {symbol: None for symbol in LIVE_SYMBOLS}

        self.config = {
            "take_profit_pct": 0.0025,  # 0.25%
            "stop_loss_pct": 0.0015,    # 0.15%
            "max_hold_minutes": 8,
            "rsi_buy_threshold": 35,
            "polling_interval": 15       # seconds between Yahoo Finance checks
        }

        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "symbol", "side", "entry_price", "exit_price",
                    "quantity", "elapsed_minutes", "pnl"
                ])

    async def fetch_yahoo_data(self):
        """Fetch real-time data from Yahoo Finance for all symbols"""
        while True:
            try:
                for symbol in LIVE_SYMBOLS:
                    # Get the latest data point
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='1d', interval='1m')
                    
                    if not data.empty:
                        latest = data.iloc[-1]
                        timestamp = latest.name.to_pydatetime().replace(tzinfo=timezone.utc)
                        
                        # Only add if it's new data
                        if self.last_update_time[symbol] is None or timestamp > self.last_update_time[symbol]:
                            self.data[symbol].append({
                                'timestamp': timestamp,
                                'open': latest['Open'],
                                'high': latest['High'],
                                'low': latest['Low'],
                                'close': latest['Close']
                            })
                            self.last_update_time[symbol] = timestamp
                            
                            # Keep only the most recent 100 data points
                            if len(self.data[symbol]) > 100:
                                self.data[symbol].pop(0)
                            
                            # Process the new data
                            await self.check_entry(symbol)
                            await self.check_exit(symbol)
                
                # Wait before next poll
                await asyncio.sleep(self.config['polling_interval'])
                
            except Exception as e:
                print(f"Error fetching data: {e}")
                await asyncio.sleep(30)  # Wait longer if error occurs

    async def check_entry(self, symbol):
        if symbol in self.open_positions:
            return

        price_data = self.data[symbol]
        if len(price_data) < 50:
            return

        rsi = self.calculate_rsi(price_data)
        macd, signal = self.calculate_macd(price_data)
        trend = self.calculate_trend(price_data)

        if None in (rsi, macd, signal, trend):
            return

        latest_price = price_data[-1]['close']
        if rsi < self.config['rsi_buy_threshold'] and macd > signal and trend == 'up':
            direction = OrderSide.BUY
        elif rsi > 56 and macd < signal and trend == 'down':
            direction = OrderSide.SELL
        else:
            return

        account = self.client.get_account()
        buying_power = float(account.buying_power)
        qty = round((buying_power * 0.01) / latest_price, 2)

        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=direction,
            time_in_force=TimeInForce.DAY,
            type=OrderType.MARKET
        )
        self.client.submit_order(order)
        now = datetime.now(timezone.utc)
        print(f"[ENTRY] {symbol} | {direction.name} {qty} @ {latest_price:.2f} | Time: {now.strftime('%H:%M:%S')} UTC")
        self.open_positions[symbol] = {
            'entry_time': now,
            'entry_price': latest_price,
            'side': direction.name,
            'qty': qty
        }

    async def check_exit(self, symbol):
        if symbol not in self.open_positions:
            return

        price_data = self.data[symbol]
        if not price_data:
            return
            
        current_price = price_data[-1]['close']
        pos = self.open_positions[symbol]
        pnl = (current_price - pos['entry_price']) * pos['qty']
        if pos['side'] == 'SELL':
            pnl *= -1

        tp = pos['entry_price'] * (1 + self.config['take_profit_pct']) if pos['side'] == 'BUY' else pos['entry_price'] * (1 - self.config['take_profit_pct'])
        sl = pos['entry_price'] * (1 - self.config['stop_loss_pct']) if pos['side'] == 'BUY' else pos['entry_price'] * (1 + self.config['stop_loss_pct'])
        elapsed = (datetime.now(timezone.utc) - pos['entry_time']).total_seconds() / 60

        take_profit_condition = (current_price >= tp) if pos['side'] == 'BUY' else (current_price <= tp)
        stop_loss_condition = (current_price <= sl) if pos['side'] == 'BUY' else (current_price >= sl)

        if take_profit_condition or stop_loss_condition or elapsed >= self.config['max_hold_minutes']:
            closing_side = OrderSide.SELL if pos['side'] == 'BUY' else OrderSide.BUY
            order = MarketOrderRequest(
                symbol=symbol,
                qty=pos['qty'],
                side=closing_side,
                time_in_force=TimeInForce.DAY,
                type=OrderType.MARKET
            )
            self.client.submit_order(order)

            print(f"[EXIT] {symbol} | {closing_side.name} {pos['qty']} @ {current_price:.2f} | Entry: {pos['entry_price']:.2f} | "
                  f"Elapsed: {elapsed:.1f}m | PnL: {'+' if pnl >= 0 else ''}{pnl:.2f}")

            with open(self.csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    pos['side'],
                    pos['entry_price'],
                    current_price,
                    pos['qty'],
                    round(elapsed, 2),
                    round(pnl, 2)
                ])

            del self.open_positions[symbol]

    def calculate_rsi(self, price_data, period=14):
        closes = [p['close'] for p in price_data][-period:]
        if len(closes) < period:
            return None
        delta = np.diff(closes)
        gains = delta[delta > 0].sum()
        losses = -delta[delta < 0].sum()
        rs = gains / losses if losses != 0 else 0
        return 100 - (100 / (1 + rs))

    def calculate_macd(self, price_data, short_period=12, long_period=26, signal_period=9):
        closes = pd.Series([p['close'] for p in price_data])
        if len(closes) < long_period:
            return None, None
        macd = closes.ewm(span=short_period).mean() - closes.ewm(span=long_period).mean()
        signal = macd.ewm(span=signal_period).mean()
        return macd.iloc[-1], signal.iloc[-1]

    def calculate_trend(self, price_data, short_ema=20, long_ema=50):
        closes = pd.Series([p['close'] for p in price_data])
        if len(closes) < long_ema:
            return None
        ema_short = closes.ewm(span=short_ema).mean().iloc[-1]
        ema_long = closes.ewm(span=long_ema).mean().iloc[-1]
        if ema_short > ema_long:
            return 'up'
        elif ema_short < ema_long:
            return 'down'
        else:
            return 'neutral'

    async def run(self):
        print(" Starting live trading bot with Yahoo Finance data...")
        await self.fetch_yahoo_data()

if __name__ == "__main__":
    bot = LiveScalpingBot()
    asyncio.run(bot.run())