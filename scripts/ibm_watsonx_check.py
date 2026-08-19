#!/usr/bin/env python3
"""Fail-closed check for the IBM watsonx.ai hook. Not used by the sample demo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from agents.watsonx_client import WatsonxClient


def main() -> None:
    client = WatsonxClient()
    if not client.enabled:
        print(
            "IBM watsonx.ai NOT CONFIGURED. Missing: "
            + ", ".join(client.missing())
            + ".\nSet them in the environment (never commit). Local demo does not need them:\n"
            "  python3 examples/run_breakdown.py",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"watsonx credentials present. model={client.model} url={client.url}")
    print("Not sending a live generate unless you call BreakdownAgent with a script.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
