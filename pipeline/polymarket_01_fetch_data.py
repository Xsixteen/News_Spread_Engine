import os
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path to allow importing from root if needed
sys.path.append(str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def fetch_events():
    url = "https://gamma-api.polymarket.com/events"
    # Fetch parameters - fetching active events using closed=false
    params = {
        "closed": "false",
        "limit": 1000
    }
    
    events = []
    
    # Simple pagination handling
    # We'll fetch a few pages to ensure we get enough candidates
    # The API might not use 'page', it might use 'offset'. 
    # Based on common patterns and limited docs seen:
    # If the docs don't specify, we'll try to fetch a decent amount.
    # We'll start with one request and see if we get a list.
    
    print(f"Fetching events from {url}...")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Determine if data is a list (direct results) or dictionary with key
        if isinstance(data, list):
            events = data
        elif isinstance(data, dict) and 'data' in data:
            events = data['data']
        else:
            # unexpected format
            events = []
            
        print(f"Fetched {len(events)} events.")
        return events
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def get_max_odds(event):
    """
    Extract the maximum odds (price) from any market in the event.
    Returns a float between 0 and 1.
    """
    max_price = 0.0
    
    markets = event.get("markets", [])
    if not markets:
        return 0.0
        
    for market in markets:
        # Check outcome prices
        # 'outcomePrices' is typically a JSON string of list of strings, eg '["0.1", "0.9"]'
        # or a list directly.
        prices_raw = market.get("outcomePrices")
        
        prices = []
        if isinstance(prices_raw, str):
            try:
                prices = json.loads(prices_raw)
            except:
                continue
        elif isinstance(prices_raw, list):
            prices = prices_raw
            
        for p in prices:
            try:
                price_float = float(p)
                if price_float > max_price:
                    max_price = price_float
            except:
                pass
                
    return max_price

def main():
    # 1. Load configuration
    try:
        lower_threshold = float(os.getenv("POLYMARKET_ODDS_THRESHOLD", "0.70"))
    except ValueError:
        print("Invalid POLYMARKET_ODDS_THRESHOLD, defaulting to 0.70")
        lower_threshold = 0.70
        
    try:
        upper_threshold = float(os.getenv("POLYMARKET_ODDS_UPPER_THRESHOLD", "0.85"))
    except ValueError:
        print("Invalid POLYMARKET_ODDS_UPPER_THRESHOLD, defaulting to 0.85")
        upper_threshold = 0.85
        
    print(f"Odds Threshold: {lower_threshold} <= Odds <= {upper_threshold}")
    
    # 2. Fetch data
    events = fetch_events()
    
    if not events:
        print("No events found.")
        return

    # 3. Filter and Process
    candidates = []
    
    for event in events:
        # Ensure it is active (API filter should handle this, but double check)
        if not event.get("active", False):
            continue
            
        # Get volume
        try:
            volume = float(event.get("volume", 0))
        except:
            volume = 0.0
            
        # Get max odds
        max_odds = get_max_odds(event)
        
        if lower_threshold <= max_odds <= upper_threshold:
            candidates.append({
                "title": event.get("title"),
                "volume": volume,
                "max_odds": max_odds,
                "id": event.get("id"),
                "slug": event.get("slug")
            })
    
    # 4. Sort by volume (descending)
    candidates.sort(key=lambda x: x["volume"], reverse=True)
    
    # 5. Top 15
    top_15 = candidates[:15]
    
    # 6. Save and Output
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "polymarket_events.json"
    
    with open(output_file, "w") as f:
        json.dump(top_15, f, indent=4)
        
    print(f"\nSaved top {len(top_15)} events to {output_file}")
    print("\nTop Events:")
    for i, ev in enumerate(top_15, 1):
        print(f"{i}. {ev['title']} | Vol: ${ev['volume']:,.0f} | Max Odds: {ev['max_odds']:.2f}")

if __name__ == "__main__":
    main()
