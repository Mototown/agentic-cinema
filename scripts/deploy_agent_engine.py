#!/usr/bin/env python3
"""Deploy adk_agent to Vertex AI Agent Engine. Does not pretend success.

Exits 1 with a plain message if GCP project or credentials are missing.
Never called by the local sample demo.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "adk_agent"


def fail(msg: str) -> None:
    print("NOT DEPLOYED.", msg, file=sys.stderr)
    print(
        "Local demo does not need GCP: python3 examples/run_breakdown.py",
        file=sys.stderr,
    )
    raise SystemExit(1)


def require_project() -> tuple[str, str]:
    project = (os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT_ID") or "").strip()
    region = (os.environ.get("GOOGLE_CLOUD_LOCATION") or "us-central1").strip()
    if not project:
        fail(
            "GOOGLE_CLOUD_PROJECT is not set. "
            "Create a GCP project, enable Agent Platform, then:\n"
            "  export GOOGLE_CLOUD_PROJECT=your-project-id\n"
            "  gcloud auth login\n"
            "  gcloud auth application-default login\n"
            "  python3 scripts/deploy_agent_engine.py"
        )
    return project, region


def require_adc() -> None:
    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError
    except ImportError:
        fail("google-auth is not installed. pip install google-adk  (or google-auth)")
    try:
        creds, _ = google.auth.default()
    except DefaultCredentialsError:
        fail(
            "No Application Default Credentials. Run:\n"
            "  gcloud auth application-default login"
        )
    if creds is None:
        fail("Application Default Credentials were empty.")


def require_adk() -> str:
    path = shutil.which("adk")
    if not path:
        fail("ADK CLI not found. pip install google-adk")
    return path


def main() -> None:
    project, region = require_project()
    require_adc()
    adk = require_adk()
    cmd = [
        adk,
        "deploy",
        "agent_engine",
        f"--project={project}",
        f"--region={region}",
        "--display_name=Script Continuity Breakdown",
        str(AGENT_DIR),
    ]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(ROOT))
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
