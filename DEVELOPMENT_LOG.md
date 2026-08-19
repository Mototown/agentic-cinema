# Development log (factual)

## Ready for IBM Bob

**Status (2026-08-19):** IBM Bob has **not** been used on this repository. There is no Bob session, plan, or export. Do not invent one.

**What already works without Bob, IBM keys, or Google keys:**

- `python3 examples/run_breakdown.py` — sample script “Dust On The Glass”: 4 scenes, 3 continuity flags, 4 shooting groups.
- `python3 -m unittest discover -s tests` — locks that demo shape so later edits cannot silently break it.
- `scripts/ibm_watsonx_check.py` — exits 1 unless `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set (fail closed). watsonx.ai Granite is a runtime hook, not a substitute for Bob.

**How to open this project in Bob:** clone or open `Mototown/agentic-cinema`, run the two commands above, then do the three tasks below **inside IBM Bob** so judges get a real session history.

**First three tasks for this Bob session**

1. Add unit tests for `src/agentic_cinema/parser.py`, `continuity.py`, and `groups.py` using `examples/sample_script.txt`. Do not change the sample demo output: title `Dust On The Glass`, 4 scenes, 3 continuity flags, 4 shooting groups.
2. Update the screenplay parser so cues like `JULES (O.S.)` and `NAME (V.O.)` count as characters in that scene. Keep INT./EXT. heading parse the same. Do not drop or renumber the four sample scenes.
3. Review `agents/watsonx_client.py`: keep fail-closed (no network without `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`), tighten error notes, and add a test that `scripts/ibm_watsonx_check.py` exits 1 when those vars are unset.

When those are done, export the Bob session / report for judges. watsonx credentials and a public repo can wait until after this first real Bob session.

---

IBM track rule: the project must be built using **IBM Bob** as part of development. Projects that do not demonstrate IBM Bob will not meet the IBM track. This file records what actually happened. It is not a Bob session export.

## 2026-08-19 — repo created (not IBM Bob)

- Private repo `Mototown/agentic-cinema` created.
- Local heuristic parser, continuity flags, shooting groups, sample script “Dust On The Glass”.
- Optional Gemini (`google-genai`) when `GEMINI_API_KEY` is set.
- ADK `root_agent` + `scripts/deploy_agent_engine.py` that prints `NOT DEPLOYED` without GCP project/ADC.
- This work was done in Cursor / Grok Bot on a local checkout. **IBM Bob was not used.** There is no Bob session, plan, or export for these commits.

## 2026-08-19 — IBM track chosen; watsonx.ai hook added (still not IBM Bob)

- Partner track: IBM ([official IBM resources](https://agentic-cinema.devpost.com/details/ibm-resources)).
- Added `agents/watsonx_client.py`: real IBM Cloud IAM token + watsonx.ai text generation (Granite). No secrets in the repo. Without `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`, the client does not call the network; `scripts/ibm_watsonx_check.py` exits 1.
- Sample demo `python3 examples/run_breakdown.py` still runs with no IBM or Google keys.
- **IBM Bob still has not opened this repo.** watsonx.ai is an IBM *runtime* product call. Bob is the required *development* partner. Those are not the same thing. Judges still need Bob usage (planning / code / tests / export) on this project.

## 2026-08-19 — prepared for a first IBM Bob session (still not IBM Bob)

- Added `tests/test_sample_demo.py` (stdlib `unittest`) to lock the sample demo.
- README and this log now tell Bob how to open the repo and what to do first.
- **IBM Bob has still not been used.** The next development on parser tests, O.S./V.O. characters, and watsonx hardening should happen in Bob.

## Planned IBM Bob use (not done)

1. Open this repo in IBM Bob at bob.ibm.com (or the IDE Bob plugin).
2. Use Bob for planning, code generation or refactor, tests, and review on this breakdown agent.
3. Keep developing in Bob so the session history is real.
4. Export the Bob session / report for judges. Do not invent sessions.

Until that happens, this project does **not** meet the IBM track Bob requirement. The watsonx hook is necessary but not sufficient.
