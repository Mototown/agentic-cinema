# Agentic Cinema — Script Continuity & Breakdown Agent

Hackathon: [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/) (deadline **9 Sep 2026, 2:00 PM PT**).

## Assumptions

- This repo is **private** for now. A judging submission will likely need a **public** repo plus a license file; that is not done here.
- **Gemini is live** when `GEMINI_API_KEY` is set (official `google-genai` SDK). Without a key, the sample demo still runs on the local heuristic parser.
- **Agent Engine is wired, not deployed.** `adk_agent/` is a real ADK `root_agent` that calls `BreakdownAgent`. `scripts/deploy_agent_engine.py` will not claim a deploy if `GOOGLE_CLOUD_PROJECT` or Application Default Credentials are missing.
- **IBM track chosen.** watsonx.ai Granite is wired in code (`agents/watsonx_client.py`). IBM Bob has **not** been used on this repo yet; see [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).
- Input is a production-format screenplay (INT./EXT. headings). PDF needs optional `pypdf`.
- Sample script is original and short.

## Open in IBM Bob

IBM Bob has **not** been used yet. There is no session to export. After you open this repo in Bob, do the three tasks listed at the top of [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) (parser tests, O.S./V.O. characters, watsonx fail-closed tests). Run these first so you know the baseline:

```bash
python3 examples/run_breakdown.py
python3 -m unittest discover -s tests
```

Expected demo shape: title `Dust On The Glass`, 4 scenes, 3 continuity flags, 4 shooting groups. Do not invent past Bob sessions.

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
python3 -m unittest discover -s tests
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

## Built with IBM Bob

**Not yet.** IBM Bob is IBM’s agentic SDLC coding partner ([bob.ibm.com](https://www.ibm.com/products/bob), [IBM track resources](https://agentic-cinema.devpost.com/details/ibm-resources)). The IBM track requires demonstrating Bob as part of development. Existing commits were produced outside Bob (local Cursor / Grok Bot). There is no Bob session to export.

Planned (required for the IBM track):

1. Open this repo in IBM Bob.
2. Continue development there (planning, code, tests, review).
3. Export the Bob session / report for judges. Do not invent sessions.

watsonx.ai (below) is a real IBM Cloud API call at runtime. It does **not** replace Bob.

## IBM watsonx.ai (runtime hook)

`BreakdownAgent` calls `WatsonxClient.review_continuity` after the local parse (and optional Gemini). That client:

1. Reads `WATSONX_API_KEY` (or `WATSONX_APIKEY`) and `WATSONX_PROJECT_ID`. Optional: `WATSONX_URL` (default `https://us-south.ml.cloud.ibm.com`), `WATSONX_MODEL` (default `ibm/granite-3-8b-instruct`).
2. If either required env var is missing, it **does not** call IBM. The demo still works. `scripts/ibm_watsonx_check.py` prints `NOT CONFIGURED` and exits 1.
3. If both are set, it requests an IAM token from `https://iam.cloud.ibm.com/identity/token`, then POSTs text generation to watsonx.ai. On HTTP/API failure it keeps the local/Gemini breakdown and notes the failure. No secrets are committed.

```bash
export WATSONX_API_KEY="ibm-cloud-api-key"
export WATSONX_PROJECT_ID="watsonx-project-id"
# optional: export WATSONX_URL=https://us-south.ml.cloud.ibm.com
python3 scripts/ibm_watsonx_check.py
python3 examples/run_breakdown.py
python3 -m unittest discover -s tests
```

Confluent is optional on this track and is not integrated.

## Next IBM-track steps

1. **Open this repo in IBM Bob** and do the three tasks in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md). Export a real session report.
2. Set watsonx credentials and confirm a live Granite continuity review (no keys in git).
3. Optional Confluent, if you want evented breakdown jobs.
4. Public repo + license for judging.
5. Deploy Agent Engine on a real GCP project and record the resource name.

## Layout

```
src/agentic_cinema/     models, parser, continuity, shooting groups
agents/                 BreakdownAgent, Gemini client, watsonx.ai client
adk_agent/              ADK root_agent for Agent Engine
scripts/                deploy_agent_engine.py, ibm_watsonx_check.py (both fail closed)
DEVELOPMENT_LOG.md      factual IBM Bob / watsonx status
examples/               sample script + runner
tests/                  stdlib unittest lock for the sample demo
```
