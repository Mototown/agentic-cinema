from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Allow running from repo root without install.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "src"))

from agents.breakdown_agent import BreakdownAgent


def main() -> None:
    p = argparse.ArgumentParser(description="Script Continuity & Breakdown Agent")
    p.add_argument("script", nargs="?", default=str(ROOT / "examples" / "sample_script.txt"))
    p.add_argument("--json", action="store_true", help="print JSON only")
    args = p.parse_args()
    agent = BreakdownAgent()
    data = agent.run_json(args.script)
    if args.json:
        print(json.dumps(data, indent=2))
        return
    print(f"{data['title']}  [{data['engine']}]")
    print(f"scenes {len(data['scenes'])}  characters {len(data['characters'])}  locations {len(data['locations'])}")
    print("characters:", ", ".join(data["characters"]) or "—")
    print("locations:", " | ".join(data["locations"]) or "—")
    if data["props"]:
        print("props:", ", ".join(data["props"]))
    print("\nShooting groups")
    for g in data["shooting_groups"]:
        print(f"  {g['location']} / {g['time_of_day']}: scenes {g['scene_numbers']}")
    print("\nContinuity")
    if not data["continuity_flags"]:
        print("  none flagged")
    for f in data["continuity_flags"]:
        print(f"  [{f['severity']}] sc {f['scene_numbers']}: {f['message']}")
    for n in data["notes"]:
        print("note:", n)


if __name__ == "__main__":
    main()
