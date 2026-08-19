"""Agent Development Kit wrapper around BreakdownAgent.

Used by: adk run / adk deploy agent_engine
Not imported by the local CLI demo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for extra in (_ROOT, _ROOT / "src"):
    s = str(extra)
    if s not in sys.path:
        sys.path.insert(0, s)

try:
    from google.adk.agents.llm_agent import Agent
except ImportError as exc:
    raise ImportError(
        "google-adk is required for Agent Builder / Agent Engine. "
        "Install with: pip install google-adk\n"
        "The local CLI does not need ADK: python3 -m agentic_cinema examples/sample_script.txt"
    ) from exc

from agents.breakdown_agent import BreakdownAgent


def breakdown_screenplay(script_text: str) -> dict:
    """Break down a screenplay into the standard schema.

    Args:
        script_text: Full screenplay text using INT./EXT. production headings.

    Returns:
        dict with title, characters, locations, props, scenes, continuity_flags,
        shooting_groups, engine, notes. Same schema as BreakdownAgent.run_json().
    """
    result = BreakdownAgent().run("adk://tool", raw_text=script_text).to_dict()
    # Keep payload JSON-serializable and bounded for the model.
    return json.loads(json.dumps(result))


root_agent = Agent(
    name="script_continuity_breakdown",
    model="gemini-2.5-flash",
    description="Pre-production script breakdown: characters, locations, props, continuity, shooting groups.",
    instruction=(
        "You are a script-continuity agent for film pre-production. "
        "When the user provides a screenplay, call breakdown_screenplay with the full text. "
        "Return the tool JSON as-is (characters, locations, props, scenes, "
        "continuity_flags, shooting_groups). Do not invent partner tools or cloud deploys. "
        "If the user has not pasted a script, ask for one."
    ),
    tools=[breakdown_screenplay],
)
