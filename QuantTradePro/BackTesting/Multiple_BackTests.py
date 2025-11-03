import pandas as pd
import numpy as np
import logging
from datetime import datetime
import pytz
from pathlib import Path
import copy

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class BacktestScalpingBot:
    def __init__(self, data_folder, starting_capital=5000):
        self.data_folder = Path(data_folder)
        self.starting_capital = starting_capital
        self.target_assets = ['TSLA', 'AAPL', 'NVDA']
        self.market_data = {
            symbol: pd.read_csv(self.data_folder / f'minute_{symbol.lower()}.csv', parse_dates=['timestamp'])
            for symbol in self.target_assets
        }

        # Define multiple strategy configurations
        self.strategies = [
            {
                "name": "Strategy_1_High_RR",
                "take_profit_pct": 0.0040,
                "stop_loss_pct": 0.0010,
                "max_hold_minutes": 15,
                "rsi_buy_threshold": 35
            },
            {
                "name": "Strategy_2_Tight_Scalp",
                "take_profit_pct": 0.0030,
                "stop_loss_pct": 0.0010,
                "max_hold_minutes": 10,
                "rsi_buy_threshold": 30
            },
            {
                "name": "Strategy_3_Balanced",
                "take_profit_pct": 0.0025,
                "stop_loss_pct": 0.0015,
                "max_hold_minutes": 8,
                "rsi_buy_threshold": 35
            },
            {   
                "name": "High_Tight_Mix",
                'take_profit_pct': 0.003,
                'stop_loss_pct': 0.0015,
                "max_hold_minutes": 10,
                "rsi_buy_threshold": 30
            }
        ]

    def run_all_strategies(self):
        results = []
        for strat in self.strategies:
            logging.info(f"\nRunning {strat['name']}...")
            result = self.run_backtest_for_strategy(strat)
            results.append(result)

        print("\n=== STRATEGY COMPARISON SUMMARY ===")
        for res in results:
            win_rate = (res['wins'] / res['trades'] * 100) if res['trades'] > 0 else 0
            print(f"{res['name']} => Trades: {res['trades']}, Wins: {res['wins']}, Losses: {res['losses']}, "
                  f"Win Rate: {win_rate:.2f}%, PnL: {res['pnl']:.2f}, Ending Capital: {res['capital']:.2f}")

    def run_backtest_for_strategy(self, config):
        price_data = {symbol: [] for symbol in self.target_assets}
        capital = self.starting_capital
        daily_pnl = 0
        trade_count = 0
        wins = 0
        losses = 0
        active_positions = {}

        min_len = min(len(self.market_data[symbol]) for symbol in self.target_assets)
        for i in range(min_len):
            for symbol in self.target_assets:
                row = self.market_data[symbol].iloc[i]
                price = row['close']

                # Update price history
                price_data[symbol].append({
                    'timestamp': row['timestamp'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close']
                })

                # Evaluate entry
                if symbol not in active_positions:
                    rsi = self.calculate_rsi(price_data[symbol])
                    macd, signal = self.calculate_macd(price_data[symbol])
                    trend = self.calculate_trend(price_data[symbol])

                    if rsi is None or macd is None or signal is None or trend is None:
                        continue

                    if rsi < config['rsi_buy_threshold'] and macd > signal and trend == 'up':
                        direction = "buy"
                    elif rsi > 56 and macd < signal and trend == 'down':
                        direction = "sell"
                    else:
                        continue

                    position_size = capital * 0.1 / price
                    active_positions[symbol] = {
                        'entry_time': row['timestamp'],
                        'entry_price': price,
                        'direction': direction,
                        'size': position_size
                    }

            # Manage exits
            for symbol, pos in list(active_positions.items()):
                current = price_data[symbol][-1]
                current_price = current['close']
                elapsed = (current['timestamp'] - pos['entry_time']).total_seconds() / 60

                pnl = (current_price - pos['entry_price']) * pos['size']
                if pos['direction'] == 'sell':
                    pnl *= -1

                if (
                    pnl >= pos['entry_price'] * config['take_profit_pct'] * pos['size'] or
                    pnl <= -pos['entry_price'] * config['stop_loss_pct'] * pos['size'] or
                    elapsed >= config['max_hold_minutes']
                ):
                    capital += pnl
                    daily_pnl += pnl
                    trade_count += 1
                    if pnl > 0:
                        wins += 1
                    else:
                        losses += 1
                    del active_positions[symbol]

        return {
            "name": config["name"],
            "trades": trade_count,
            "wins": wins,
            "losses": losses,
            "pnl": daily_pnl,
            "capital": capital
        }

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

# Run all strategies
if __name__ == "__main__":
    bot = BacktestScalpingBot(data_folder=".", starting_capital=5000)
    bot.run_all_strategies()
