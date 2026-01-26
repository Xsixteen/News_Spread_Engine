import json
import sys
from pathlib import Path

# Add parent directory to path to allow importing from root if needed
sys.path.append(str(Path(__file__).parent.parent))

def main():
    # 1. Load data
    input_file = Path("data/polymarket_events.json")
    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        return

    try:
        with open(input_file, "r") as f:
            events = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode {input_file}.")
        return

    if not events:
        print("No events to report.")
        return

    # 2. Generate Markdown Table
    # Headers: Rank, Event, Volume, Max Odds
    markdown_lines = [
        "# Top Polymarket Opportunities",
        "",
        "| Rank | Event | Volume | Max Odds |",
        "|---|---|---|---|"
    ]

    for i, event in enumerate(events, 1):
        title = event.get("title", "Unknown Event")
        # Escape pipes in title to avoid breaking table
        title = title.replace("|", r"\|")
        
        volume = event.get("volume", 0)
        max_odds = event.get("max_odds", 0)
        
        # Format volume as money
        vol_str = f"${volume:,.0f}"
        
        # Format odds
        odds_str = f"{max_odds:.2f}"
        
        row = f"| {i} | {title} | {vol_str} | {odds_str} |"
        markdown_lines.append(row)

    markdown_content = "\n".join(markdown_lines)

    # 3. Save Report
    output_file = Path("data/polymarket_report.md")
    
    with open(output_file, "w") as f:
        f.write(markdown_content)

    print(f"Report generated at {output_file}")
    print(f"Includes {len(events)} events.")

if __name__ == "__main__":
    main()
