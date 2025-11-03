import pytz
from datetime import datetime, time

def get_live_market_status():
    """Check which major stock markets are open right now"""
    now = datetime.now(pytz.utc)
    markets = {
        # Americas
        "NYSE/NASDAQ (US)": {
            "timezone": "America/New_York",
            "open": time(9, 30),  # 9:30 AM ET
            "close": time(16, 0)   # 4:00 PM ET
        },
        "Toronto (TSX)": {
            "timezone": "America/Toronto",
            "open": time(9, 30),
            "close": time(16, 0)
        },
        
        # Europe
        "London (LSE)": {
            "timezone": "Europe/London",
            "open": time(8, 0),    # 8:00 AM GMT
            "close": time(16, 30)  # 4:30 PM GMT
        },
        "Frankfurt (FWB)": {
            "timezone": "Europe/Berlin",
            "open": time(8, 0),
            "close": time(20, 0)  # Extended hours
        },
        
        # Asia
        "Tokyo (TSE)": {
            "timezone": "Asia/Tokyo",
            "open": time(9, 0),    # 9:00 AM JST
            "close": time(15, 0)   # 3:00 PM JST
        },
        "Hong Kong (HKEX)": {
            "timezone": "Asia/Hong_Kong",
            "open": time(9, 30),
            "close": time(16, 0)
        },
        "Shanghai (SSE)": {
            "timezone": "Asia/Shanghai",
            "open": time(9, 30),
            "close": time(15, 0)
        }
    }

    open_markets = []
    for market, details in markets.items():
        tz = pytz.timezone(details["timezone"])
        local_time = now.astimezone(tz)
        
        # Check if weekday (Mon-Fri) and within trading hours
        if local_time.weekday() < 5:  # 0-4 = Monday-Friday
            market_open = details["open"]
            market_close = details["close"]
            current_time = local_time.time()
            
            if market_open <= current_time <= market_close:
                open_markets.append({
                    "market": market,
                    "local_time": local_time.strftime("%H:%M"),
                    "hours": f"{market_open.strftime('%H:%M')}-{market_close.strftime('%H:%M')}"
                })

    return open_markets

# Get currently open markets
open_now = get_live_market_status()
print("=== MARKETS OPEN RIGHT NOW ===")
for market in open_now:
    print(f"{market['market']} | Local Time: {market['local_time']} | Hours: {market['hours']}")