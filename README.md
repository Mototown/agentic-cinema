# Agentic Cinema — Script Continuity & Breakdown Agent

Hackathon: [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/) (deadline **9 Sep 2026, 2:00 PM PT**).

## Assumptions

- This repo is **private** for now. A judging submission will likely need a **public** repo plus a license file; that is not done here.
- The first version is a **local heuristic agent**. It does **not** yet call Gemini, Agent Builder, or any partner MCP (IBM, Grafana, Parallel, ClickHouse, Replit). Those are required for a valid entry and are listed as next work, not as shipped.
- Input is a production-format screenplay (INT./EXT. headings). Fountain-ish text works. PDF needs optional `pypdf`.
- Continuity flags are conservative guesses, not a script supervisor.
- Sample script is original, short, and written for the demo.

## The problem

Pre-production still starts with a script supervisor and AD walking a screenplay by hand: who is in the scene, where it is, day or night, what has to be on the truck, what might be VFX, and which scenes can share a company move. Continuity errors (a character in two places with no time cut, a DAY/NIGHT flip on the same set) are cheap to miss on the page and expensive on the lot.

## The agent’s job

Accept a screenplay (`.txt` now; `.pdf` if pypdf is installed). Return a structured breakdown:

- characters, locations, props
- per-scene day/night and INT/EXT
- VFX cue notes (keyword-level)
- continuity risk flags
- suggested shooting groups (same location + time of day)

## Current technical state

Working locally, no cloud:

```bash
python3 -m pip install -e .
python3 -m agentic_cinema examples/sample_script.txt
# or
python3 examples/run_breakdown.py
```

`BreakdownAgent.run()` is the public method. Gemini is a stub (`agents/gemini_client.py`) that only records that a key exists. No Google Cloud project is required to run the demo.

## Next 3 development priorities

1. **Gemini pass** — send the local breakdown + scene text to Gemini and replace/refine flags and VFX notes. Do not skip the local parse; use it as the grounded skeleton.
2. **Agent Builder** — put BreakdownAgent behind Gemini Enterprise Agent Builder / Agent Engine so the entry actually runs on Google Cloud, not only on a laptop.
3. **Partner track** — pick one of IBM, Grafana, Parallel, ClickHouse, or Replit and **call it in code** (required for judging). Not chosen yet.

## Layout

```
src/agentic_cinema/   models, parser, continuity, shooting groups
agents/               BreakdownAgent + Gemini stub
examples/             sample script + runner
```
