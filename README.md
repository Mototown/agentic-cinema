# Agentic Cinema — Script Continuity & Breakdown Agent

Hackathon: [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/) (deadline **9 Sep 2026, 2:00 PM PT**).

## Assumptions

- This repo is **private** for now. A judging submission will likely need a **public** repo plus a license file; that is not done here.
- **Gemini is live** when `GEMINI_API_KEY` is set (official `google-genai` SDK). Without a key, the sample demo still runs on the local heuristic parser.
- **Agent Engine is wired, not deployed.** `adk_agent/` is a real ADK `root_agent` that calls `BreakdownAgent`. `scripts/deploy_agent_engine.py` will not claim a deploy if `GOOGLE_CLOUD_PROJECT` or Application Default Credentials are missing.
- **No partner integration** (IBM, Grafana, Parallel, ClickHouse, Replit). Not chosen yet.
- Input is a production-format screenplay (INT./EXT. headings). PDF needs optional `pypdf`.
- Sample script is original and short.

## The problem

Pre-production still starts with walking a screenplay by hand: who is in the scene, where it is, day or night, what has to be on the truck, what might be VFX, and which scenes can share a company move.

## The agent’s job

Accept a screenplay. Return a structured breakdown:

- characters, locations, props
- per-scene day/night and INT/EXT
- VFX notes
- continuity risk flags
- suggested shooting groups (same location + time of day)

Local parse is the skeleton. Gemini refines it when a key is present. The ADK agent exposes that same JSON via a `breakdown_screenplay` tool.

## Local run (no GCP)

```bash
python3 -m pip install -e .
python3 -m agentic_cinema examples/sample_script.txt
# or
python3 examples/run_breakdown.py
```

With Gemini (still no GCP):

```bash
export GEMINI_API_KEY="your-key"   # Google AI Studio; never commit it
# optional: export GEMINI_MODEL=gemini-2.5-flash
python3 -m agentic_cinema examples/sample_script.txt --json
```

`engine` is `local-heuristic` without a key, or `local-heuristic+<model>` after a successful Gemini call.

## GCP run (Agent Builder / Agent Engine)

This is **not** deployed from this machine unless you have a project and ADC.

```bash
python3 -m pip install -e ".[gcp]"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"   # optional, default us-central1
gcloud auth login
gcloud auth application-default login
# Enable Agent Platform API + Cloud Resource Manager API on the project.
python3 scripts/deploy_agent_engine.py
```

That script runs `adk deploy agent_engine` against `adk_agent/`. If project or credentials are missing, it prints `NOT DEPLOYED.` and exits 1.

Optional local ADK smoke (still not a cloud deploy):

```bash
adk run adk_agent
```

## Next two development priorities

1. **Actually deploy** on a GCP project and record the Agent Engine resource name (this repo only has the path).
2. **Partner track** — pick one of IBM, Grafana, Parallel, ClickHouse, or Replit and **call it in code**.

## Layout

```
src/agentic_cinema/     models, parser, continuity, shooting groups
agents/                 BreakdownAgent + Gemini client
adk_agent/              ADK root_agent for Agent Engine
scripts/                deploy_agent_engine.py (fails closed)
examples/               sample script + runner
```
