from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from agents.breakdown_agent import BreakdownAgent

script = ROOT / "examples" / "sample_script.txt"
data = BreakdownAgent().run_json(script)
print(json.dumps(data, indent=2)[:4000])
print("...")
print("scenes", len(data["scenes"]), "flags", len(data["continuity_flags"]), "groups", len(data["shooting_groups"]))
