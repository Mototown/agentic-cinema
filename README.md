# Agentic Cinema — Script Continuity & Breakdown Agent

Hackathon: [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/) (deadline **9 Sep 2026, 2:00 PM PT**).

## Assumptions

- This repo is **private** for now. A judging submission will likely need a **public** repo plus a license file; that is not done here.
- **Gemini is live** when `GEMINI_API_KEY` is set (official `google-genai` SDK). Without a key, the sample demo still runs on the local heuristic parser. That is intentional.
- **Agent Builder / Agent Engine is not wired.** Neither is a partner MCP (IBM, Grafana, Parallel, ClickHouse, Replit). Those are the next two jobs, not shipped.
- Input is a production-format screenplay (INT./EXT. headings). PDF needs optional `pypdf`.
- Continuity flags are assists for an AD / script supervisor, not a replacement.
- Sample script is original and short.

## The problem

Pre-production still starts with walking a screenplay by hand: who is in the scene, where it is, day or night, what has to be on the truck, what might be VFX, and which scenes can share a company move. Continuity misses are cheap on the page and expensive on the lot.

## The agent’s job

Accept a screenplay. Return a structured breakdown:

- characters, locations, props
- per-scene day/night and INT/EXT
- VFX notes
- continuity risk flags
- suggested shooting groups (same location + time of day)

Local parse is the skeleton. Gemini refines it. Scene numbers are not invented.

## Current technical state

```bash
python3 -m pip install -e .
python3 -m agentic_cinema examples/sample_script.txt
# or
python3 examples/run_breakdown.py
```

With Gemini:

```bash
export GEMINI_API_KEY="your-key"   # from Google AI Studio; never commit it
# optional: export GEMINI_MODEL=gemini-2.5-flash
python3 -m agentic_cinema examples/sample_script.txt --json
```

`BreakdownAgent.run()` is the public method. `engine` is `local-heuristic` without a key, or `local-heuristic+<model>` after a successful Gemini call. Failed Gemini calls fall back to the local breakdown and say so in `notes`.

## Next two development priorities

1. **Agent Builder on GCP** — run this agent on Gemini Enterprise Agent Builder / Agent Engine, not only as a local Python CLI.
2. **Partner track** — pick one of IBM, Grafana, Parallel, ClickHouse, or Replit and **call it in code** (required for judging). Not chosen yet.

## Layout

```
src/agentic_cinema/   models, parser, continuity, shooting groups
agents/               BreakdownAgent + Gemini client (google-genai)
examples/             sample script + runner
```
