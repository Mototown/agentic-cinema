# Agentic Cinema — Script Continuity & Breakdown Agent

Hackathon: [Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/) (deadline **9 Sep 2026, 2:00 PM PT**).

## Assumptions

- This repo is **private** for now. A judging submission will likely need a **public** repo plus a license file; that is not done here.
- **Gemini is live** when `GEMINI_API_KEY` is set (official `google-genai` SDK). Without a key, the sample demo still runs on the local heuristic parser.
- **Agent Engine is wired, not deployed.** `adk_agent/` is a real ADK `root_agent` that calls `BreakdownAgent`. `scripts/deploy_agent_engine.py` will not claim a deploy if `GOOGLE_CLOUD_PROJECT` or Application Default Credentials are missing.
- **IBM track chosen.** watsonx.ai Granite is wired in code (`agents/watsonx_client.py`). Two IBM Bob sessions have been run on this repo; see [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).
- Input is a production-format screenplay (INT./EXT. headings). PDF needs optional `pypdf`.
- Sample script is original and short.

## IBM Bob sessions

Two development sessions have been run in IBM Bob. See [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for the factual record of what was done in each session. Run the baseline checks at any time:

```bash
python3 examples/run_breakdown.py
python3 -m unittest discover -s tests
```

Current sample demo shape: title `Dust On The Glass`, 4 scenes, 4 continuity flags, 4 shooting groups.

## The problem

Pre-production still starts with walking a screenplay by hand: who is in the scene, where it is, day or night, what has to be on the truck, what might be VFX, and which scenes can share a company move.

## The agent's job

Accept a screenplay. Return a structured breakdown:

- characters, locations, props
- per-scene day/night and INT/EXT
- VFX notes
- continuity risk flags
- suggested shooting groups (same location + time of day)
- `quality_notes` summarising analysis completeness and scheduling readiness

Local parse is the skeleton. Gemini refines it when a key is present. The ADK agent exposes that same JSON via a `breakdown_screenplay` tool.

## What this agent is good for

**Strengths — what it reliably does today:**

- **Parses production-format scripts** (`INT./EXT.` headings, Fountain conventions) into a structured scene list in under a second, with no API key required.
- **Detects characters** from all-caps cues, including `(O.S.)`, `(V.O.)`, and `(CONT'D)` suffixes that a naïve parser would miss.
- **Extracts handled props** from verb patterns (`picks up`, `grabs`, `holds`, etc.) and flags props that are introduced but never referenced again — a common continuity oversight.
- **Flags continuity risks**: same-location day/night flips, character location jumps within a 5-scene window (configurable), and single-appearance characters that are easy to drop from a shooting day.
- **Groups scenes for scheduling** by INT/EXT setup, location, and time of day — INT and EXT at the same location are correctly kept separate because they need different lighting rigs and permits.
- **Writes production-specific group reasons**: each group tells the coordinator what setup type, what cast is required, whether VFX is present, and what the practical lighting/weather/permit note is.
- **Produces a `quality_notes` field** with a continuity risk summary and an explicit scheduling-readiness verdict so the coordinator knows what to resolve before a first pass.
- **Layers optional LLM enrichment** on top of the deterministic skeleton: Gemini improves character/prop extraction; IBM watsonx.ai Granite adds an independent continuity review. Both fail safely — the breakdown is still useful without them.

**Limitations — what it does not do (yet):**

- **Prop detection is verb-pattern only.** A prop described in action (`A gun lies on the table`) without a handling verb will be missed. Gemini enrichment helps when a key is present.
- **No wardrobe or physical-state continuity.** A character who gets soaked in Scene 3 is not automatically flagged as needing to be wet at the start of Scene 4.
- **No page-count or screen-time estimates.** The breakdown cannot yet tell a coordinator how many eighths of a page each scene is, which is needed for day-estimate arithmetic.
- **No cast-based scheduling groups.** Scenes are grouped by location and time of day, not by which actors they share. A 1st AD would still need to manually cluster scenes by actor availability to build a shooting schedule.
- **Character detection is heuristic, not semantic.** All-caps lines that are not characters (e.g. `FADE OUT`, `TITLE CARD`) are filtered by a skip-cue list, but unusual production text could still produce false positives.
- **PDF extraction depends on pypdf text layer.** Scanned PDFs without a text layer will produce no output.
- **The agent does not write a shooting schedule.** It produces a breakdown — the structured data that a scheduler uses as input. Translating that into a day-by-day schedule with locations, transport, and crew still requires a human or a dedicated scheduling tool.

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

IBM Bob is IBM's agentic SDLC coding partner ([bob.ibm.com](https://www.ibm.com/products/bob), [IBM track resources](https://agentic-cinema.devpost.com/details/ibm-resources)). Two development sessions have been completed in Bob on this repository. See [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for the factual session record.

watsonx.ai (below) is a real IBM Cloud API call at runtime. It is a separate IBM product from Bob and does **not** replace Bob session usage.

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

1. Set watsonx credentials and confirm a live Granite continuity review (no keys in git).
2. Public repo + license for judging.
3. Deploy Agent Engine on a real GCP project and record the resource name.
4. Export IBM Bob session report for judges.

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
