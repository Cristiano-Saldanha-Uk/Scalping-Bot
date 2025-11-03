import asyncio
import aiohttp
import numpy as np
import pandas as pd
from datetime import datetime, timezone, time
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class TwelveDataScalper:
    def __init__(self):
        # Trading Configuration
        self.client = TradingClient(
            "Enter Your Own Key",
            "Enter Your Own Key",
            paper=True
        )
        self.symbols = ["AAPL", "TSLA", "AMZN", "MSFT", "NVDA"]
        self.data = {symbol: [] for symbol in self.symbols}
        self.open_positions = {}
        
        # Twelve Data Config
        self.twelve_data_key = "Enter Your Own Key"
        self.base_url = "https://api.twelvedata.com"
        
        # Strategy Parameters
        self.config = {
            "take_profit_pct": 0.0025,
            "stop_loss_pct": 0.0015,
            "max_hold_minutes": 8,
            "rsi_buy_threshold": 35,
            "position_size_pct": 0.01,
            "poll_interval": 60,
            "market_open": time(9, 30),  # 9:30 AM
            "market_close": time(16, 0)  # 4:00 PM
        }

    async def check_market_open(self):
        """Check if market is currently open"""
        now = datetime.now(timezone.utc).astimezone()
        
        # Check weekday (Mon-Fri)
        if now.weekday() >= 5:  # Saturday(5) or Sunday(6)
            return False
            
        # Check time window
        market_open = self.config['market_open']
        market_close = self.config['market_close']
        current_time = now.time()
        
        return market_open <= current_time <= market_close

    async def verify_alpaca_connection(self):
        """Check Alpaca API connectivity"""
        try:
            account = await self.client.get_account()
            return account.trading_blocked is False
        except Exception:
            return False

    async def verify_twelvedata_connection(self):
        """Check Twelve Data API connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/time_series?symbol=AAPL&interval=1min&apikey={self.twelve_data_key}"
                async with session.get(url) as response:
                    return response.status == 200
        except Exception:
            return False

    async def fetch_realtime_data(self):
        """Main data fetching loop with health checks"""
        while True:
            # Verify market conditions
            market_open = await self.check_market_open()
            alpaca_connected = await self.verify_alpaca_connection()
            twelvedata_connected = await self.verify_twelvedata_connection()
            
            if not all([market_open, alpaca_connected, twelvedata_connected]):
                status = {
                    "Market Open": market_open,
                    "Alpaca Connected": alpaca_connected,
                    "TwelveData Connected": twelvedata_connected
                }
                print(f"Waiting for conditions: {status}")
                await asyncio.sleep(60)
                continue
                
            # Fetch data if all conditions met
            for symbol in self.symbols:
                try:
                    async with aiohttp.ClientSession() as session:
                        # Get real-time price
                        price_url = f"{self.base_url}/price?symbol={symbol}&apikey={self.twelve_data_key}"
                        async with session.get(price_url) as price_response:
                            price_data = await price_response.json()
                        
                        # Get minute bars
                        intraday_url = f"{self.base_url}/time_series?symbol={symbol}&interval=1min&outputsize=100&apikey={self.twelve_data_key}"
                        async with session.get(intraday_url) as intraday_response:
                            intraday_data = await intraday_response.json()
                        
                        if 'price' in price_data and 'values' in intraday_data:
                            price = float(price_data['price'])
                            latest_bar = intraday_data['values'][0]
                            
                            self.data[symbol].append({
                                'timestamp': datetime.now(timezone.utc),
                                'open': float(latest_bar['open']),
                                'high': float(latest_bar['high']),
                                'low': float(latest_bar['low']),
                                'close': price,
                                'volume': int(latest_bar['volume'])
                            })
                            
                            if len(self.data[symbol]) > 100:
                                self.data[symbol].pop(0)
                                
                            await self.process_symbol(symbol)
                            
                except Exception as e:
                    print(f"Error processing {symbol}: {str(e)}")
            
            await asyncio.sleep(self.config['poll_interval'])

    # ... (keep all other methods unchanged: process_symbol, check_entry, place_order, etc.)

    async def run(self):
        """Start the trading bot with health monitoring"""
        print("Starting bot with connectivity checks...")
        try:
            # Initial connection checks
            if not await self.verify_alpaca_connection():
                raise ConnectionError("Alpaca API connection failed")
            if not await self.verify_twelvedata_connection():
                raise ConnectionError("Twelve Data API connection failed")
            
            print("All APIs connected successfully. Starting main loop...")
            await self.fetch_realtime_data()
            
        except Exception as e:
            print(f"Fatal error: {str(e)}")
        finally:
            print("Bot stopped")

if __name__ == "__main__":
    bot = TwelveDataScalper()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")