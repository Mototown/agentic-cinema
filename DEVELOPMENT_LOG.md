# Development log (factual)

IBM track rule: the project must be built using **IBM Bob** as part of development. Projects that do not demonstrate IBM Bob will not meet the IBM track. This file records what actually happened; entries are not invented.

---

## 2026-08-19 — first IBM Bob session ✓

**This is the first real IBM Bob development session on this repository.**

**Goal:** Full architecture analysis of the existing codebase, identify the highest-impact weaknesses in continuity and grouping logic, then implement the top fixes while keeping the locked sample demo stable.

**What Bob did:**

1. **Architecture analysis** — read every file (`parser.py`, `continuity.py`, `groups.py`, `models.py`, `breakdown_agent.py`, `gemini_client.py`, `watsonx_client.py`, `adk_agent/agent.py`, tests, scripts). Produced a prioritized 10-item improvement plan covering parser correctness, continuity depth, grouping logic, Watsonx prompt quality, and scheduling metadata.

2. **O.S./V.O./CONT'D character parsing fix** (`src/agentic_cinema/parser.py`) — added `_PAREN` regex to strip trailing parentheticals before the all-caps CHARACTER match. `JULES (O.S.)`, `NAME (V.O.)`, `NAME (CONT'D)` now correctly resolve as characters. Removed the broken `"V.O"` / `"O.S"` substring guards from `SKIP_CUES` (could false-match legitimate names). `JULES` is now correctly detected in Scene 1 of the sample script via `JULES (O.S.)`.

3. **Non-consecutive teleportation continuity check** (`src/agentic_cinema/continuity.py`) — removed the `prev[0] == i - 1` consecutive-only guard. Replaced with a configurable `max_scene_gap` window (default 5 scenes). The `same_tod` condition is preserved — a DAY→NIGHT gap is a legitimate time cut, not a teleportation. `flag_continuity()` accepts `max_scene_gap` as a keyword argument.

4. **Richer Watsonx / Granite prompt** (`agents/watsonx_client.py`) — `_prompt()` now passes `time_of_day`, `props`, and `vfx_notes` per scene in addition to heading and characters. System instruction extended with four specific focus areas: prop consistency, VFX adjacency effects, time-of-day conflicts, character state (wardrobe/injuries). Fail-closed behaviour (no network without both env vars) is unchanged.

**Sample demo after all three changes:**

| Field | Before | After | Reason |
|---|---|---|---|
| title | Dust On The Glass | Dust On The Glass | unchanged |
| scenes | 4 | 4 | unchanged |
| continuity\_flags | 3 | 2 | one flag removed: "JULES in only one scene" was a false positive produced by the parser bug |
| shooting\_groups | 4 | 4 | unchanged |
| characters | ELENA, JULES, MARA | ELENA, JULES, MARA | unchanged |
| props | radio, tablet, thermos | radio, tablet, thermos | unchanged |
| engine | local-heuristic | local-heuristic | unchanged |

All 3 tests pass (`python3 -m unittest discover -s tests`). The locked test assertion was updated from 3 → 2 continuity flags with a comment documenting why.

---

## 2026-08-19 — second IBM Bob session ✓

**Goal:** Three focused improvements to grouping logic, continuity depth, and output completeness.

**What Bob did:**

1. **INT/EXT separation in shooting groups** (`src/agentic_cinema/groups.py`) — bucket key extended from `(location, time_of_day)` to `(int_ext, location, time_of_day)`. INT and EXT at the same location are now separate groups (different lighting rig, permits, weather). Reason string now encodes setup type, time-of-day, and scene count. Interior groups carry an explicit note to separate setup from any EXT counterpart.

2. **Prop continuity cross-checking** (`src/agentic_cinema/continuity.py`) — new `_prop_continuity()` helper, two `info`-severity rules: (a) prop appears in exactly one non-final scene — introduced and never referenced again; (b) prop reappears after a gap of more than 3 scenes — possible magic-prop error.

3. **`quality_notes` field** (`src/agentic_cinema/models.py`, `agents/breakdown_agent.py`) — new `list[str]` field on `Breakdown`, default empty. `_build_quality_notes()` populates it at parse time with: scene count, prop extraction coverage, VFX detection results, Gemini status, watsonx status, and a prop-detection limitation note. Field is carried through `to_dict()` and `_hydrate()`. Gemini `_merge()` does not touch it.

**Sample demo after all three changes:**

| Field | Before | After | Reason |
|---|---|---|---|
| scenes | 4 | 4 | unchanged |
| continuity\_flags | 2 | 4 | `tablet` (Scene 1 only) and `thermos` (Scene 3 only) correctly flagged as single-appearance props |
| shooting\_groups | 4 | 4 | sample has no INT/EXT collision at same location; count unchanged |
| quality\_notes | — | 6 items | new field; does not affect any existing field |

All 3 tests pass. Locked test assertion updated from 2 → 4 continuity flags with comment.

---

## 2026-08-19 — repo created (not IBM Bob)

- Private repo `Mototown/agentic-cinema` created.
- Local heuristic parser, continuity flags, shooting groups, sample script "Dust On The Glass".
- Optional Gemini (`google-genai`) when `GEMINI_API_KEY` is set.
- ADK `root_agent` + `scripts/deploy_agent_engine.py` that prints `NOT DEPLOYED` without GCP project/ADC.
- This work was done in Cursor / Grok Bot on a local checkout. **IBM Bob was not used.** There is no Bob session, plan, or export for these commits.

## 2026-08-19 — IBM track chosen; watsonx.ai hook added (still not IBM Bob)

- Partner track: IBM ([official IBM resources](https://agentic-cinema.devpost.com/details/ibm-resources)).
- Added `agents/watsonx_client.py`: real IBM Cloud IAM token + watsonx.ai text generation (Granite). No secrets in the repo. Without `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`, the client does not call the network; `scripts/ibm_watsonx_check.py` exits 1.
- Sample demo `python3 examples/run_breakdown.py` still runs with no IBM or Google keys.
- **IBM Bob still had not opened this repo.** watsonx.ai is an IBM *runtime* product call. Bob is the required *development* partner. Those are not the same thing.

## 2026-08-19 — prepared for a first IBM Bob session (still not IBM Bob)

- Added `tests/test_sample_demo.py` (stdlib `unittest`) to lock the sample demo.
- README and this log now tell Bob how to open the repo and what to do first.
- **IBM Bob had still not been used.** The next development on parser tests, O.S./V.O. characters, and watsonx hardening should happen in Bob.

---

## Remaining IBM track items

- Set `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` and run a live Granite continuity review.
- Public repo + license file for judging submission.
- Deploy Agent Engine on a real GCP project and record the resource name.
- Continue development in IBM Bob; export session report for judges.
