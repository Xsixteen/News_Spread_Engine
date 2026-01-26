#!/usr/bin/env python3
"""
Momentum Pipeline Step 02: Determine Action
Determines 'buy' or 'sell' action based on 'MOMENTUM_ACTION' env var and SMA 200 vs Open Price logic.
"""
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_data():
    """Load momentum_data.json"""
    path = "data/momentum_data.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
        
    with open(path, "r") as f:
        return json.load(f)

def main():
    print("="*60)
    print("MOMENTUM STEP 02: Determine Action")
    print("="*60)

    try:
        momentum_action = os.getenv("MOMENTUM_ACTION")
        if not momentum_action:
            print("⚠️  'MOMENTUM_ACTION' environment variable not set. No actions will be taken.")
            return

        momentum_action = momentum_action.lower()
        if momentum_action not in ["buy", "sell"]:
            print(f"⚠️  Invalid 'MOMENTUM_ACTION' value: {momentum_action}. Expected 'buy' or 'sell'.")
            return

        print(f"ℹ️  Action Mode: {momentum_action.upper()}")

        data_wrapper = load_data()
        data = data_wrapper.get("data", {})
        
        print(f"\n📊 Analyzing {len(data)} tickers...")
        
        for ticker, metrics in data.items():
            if "error" in metrics:
                print(f"  {ticker}: ⚠️  Skipping (Error in data: {metrics['error']})")
                continue
                
            sma_200 = metrics.get("sma_200")
            open_price = metrics.get("open_price")
            
            if sma_200 is None or open_price is None:
                print(f"  {ticker}: ⚠️  Skipping (Missing metrics)")
                continue
                
            action = "NONE"
            
            # Logic based on momentum_action
            if momentum_action == "buy":
                # Buy Condition: Open Price >= 1.01 * SMA 200 (1% above)
                threshold = sma_200 * 1.01
                if open_price >= threshold:
                    action = "BUY"
            
            elif momentum_action == "sell":
                # Sell Condition: Open Price <= 0.99 * SMA 200 (1% below)
                threshold = sma_200 * 0.99
                if open_price <= threshold:
                    action = "SELL"
            
            # Output result
            if action != "NONE":
                print(f"  {ticker}: 🚨 {action} (Open: {open_price}, SMA200: {sma_200})")
            else:
                 print(f"  {ticker}: 🔴 No Action  - (Open: {open_price}, SMA200: {sma_200})")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
