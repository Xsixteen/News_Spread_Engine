#!/usr/bin/env python3
"""
Momentum Pipeline Runner

Runs only at 12:00-12:59 GMT and 20:00-20:59 GMT.
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
    # Check time
    now_gmt = datetime.now(timezone.utc)
    current_hour = now_gmt.hour
    
    print(f"Momentum Pipeline - Current Time (GMT): {now_gmt.strftime('%Y-%m-%d %H:%M:%S')}")

    # Allowed run windows: 12 GMT and 20 GMT
    if current_hour not in [12, 20]:
        print(f"⚠️  Skipping execution. Pipeline only runs at 12 GMT and 20 GMT. (Current hour: {current_hour})")
        sys.exit(0)

    print("✅ Time check passed. Starting pipeline...")

    steps = [
        ("01", "pipeline/momentum_01_fetch_data.py", "Fetch Momentum Data (SMA + Open Price)"),
        ("02", "pipeline/momentum_02_action.py", "Determine Momentum Action"),
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
