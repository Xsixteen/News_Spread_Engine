#!/usr/bin/env python3
"""
Polymarket Pipeline Runner

Runs the Polymarket data fetching pipeline.
"""
import subprocess
import sys
import time
from datetime import datetime, timezone

def run_step(step_name, script_path, description):
    """
    Execute a pipeline step
    """
    print("\n" + "="*80)
    print(f"▶ {step_name}: {description}")
    print("="*80)

    start = time.time()
    result = subprocess.run([sys.executable, script_path], text=True)
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n✅ {step_name} complete ({elapsed:.1f}s)")
        return True
    else:
        print(f"\n❌ {step_name} FAILED ({elapsed:.1f}s)")
        return False

def main():
    print(f"Polymarket Pipeline - Starting at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")

    steps = [
        ("01", "pipeline/polymarket_01_fetch_data.py", "Fetch Top Polymarket Events"),
        ("02", "pipeline/polymarket_02_report.py", "Generate Markdown Report"),
    ]

    start_time = time.time()
    completed = 0
    
    for step_name, script, desc in steps:
        if run_step(step_name, script, desc):
            completed += 1
            time.sleep(1)
        else:
            print("\n⚠️  Pipeline stopped due to error")
            break

    elapsed = time.time() - start_time
    print("\n" + "="*80)
    status = '✅ COMPLETE' if completed == len(steps) else '❌ STOPPED'
    print(f"{status}: {completed}/{len(steps)} steps ({elapsed:.1f}s)")
    print("="*80)

    if completed != len(steps):
        sys.exit(1)

if __name__ == "__main__":
    main()
