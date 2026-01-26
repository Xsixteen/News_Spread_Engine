#!/usr/bin/env python3
"""
Momentum Pipeline Step 01: Fetch Data
Fetches SMA (200-day) and Open Price for tickers in data/momentum.json.
"""
import json
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_tickers():
    """Load tickers from momentum.json"""
    path = "data/momentum.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
        
    with open(path, "r") as f:
        config = json.load(f)
        
    # Handle different potential structures
    if isinstance(config, list):
        return config
    elif isinstance(config, dict) and "tickers" in config:
        return config["tickers"]
    else:
        raise ValueError(f"Invalid format in {path}. Expected list or dict with 'tickers' key.")

def get_sma_200(ticker, api_key):
    """Fetch 200-day SMA"""
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "SMA",
        "symbol": ticker,
        "interval": "daily",
        "time_period": 200,
        "series_type": "close",
        "apikey": api_key
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if "Error Message" in data:
        raise ValueError(f"API Error: {data['Error Message']}")
    if "Note" in data:
         # Check for rate limit note specifically
         print(f"    ⚠️  Note from API: {data['Note']}")
    
    if "Technical Analysis: SMA" in data:
        technical_data = data["Technical Analysis: SMA"]
        if technical_data:
            latest_date = list(technical_data.keys())[0]
            return float(technical_data[latest_date]["SMA"])
            
    return None

def get_open_price(ticker, api_key):
    """Fetch Open Price from Global Quote"""
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": api_key
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if "Error Message" in data:
        raise ValueError(f"API Error: {data['Error Message']}")
    
    quote = data.get("Global Quote", {})
    if quote:
        # 02. open
        return float(quote.get("02. open", 0.0))
        
    return None

def main():
    print("="*60)
    print("MOMENTUM STEP 01: Fetch Data (SMA 200 + Open)")
    print("="*60)

    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY not found in .env")

        tickers = load_tickers()
        print(f"\n📊 Processing {len(tickers)} tickers...")
        
        results = {}
        
        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] {ticker}...", end=" ", flush=True)
            
            try:
                # Fetch SMA 200
                sma = get_sma_200(ticker, api_key)
                
                # Fetch Open Price
                # Need delay between calls
                time.sleep(12) 
                
                open_price = get_open_price(ticker, api_key)
                
                results[ticker] = {
                    "sma_200": sma,
                    "open_price": open_price,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"✓ (SMA 200: {sma}, Open: {open_price})")
                
                # Rate limit delay for next ticker
                if i < len(tickers):
                    time.sleep(12)
                    
            except Exception as e:
                print(f"✗ ({e})")
                results[ticker] = {"error": str(e)}
                
        # Save output
        output_file = "data/momentum_data.json"
        with open(output_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "data": results
            }, f, indent=2)
            
        print(f"\n✓ Saved to {output_file}")
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
