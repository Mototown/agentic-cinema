# Development log (factual)

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

## Planned IBM Bob use (not done)

1. Open this repo in IBM Bob at bob.ibm.com (or the IDE Bob plugin).
2. Use Bob for planning, code generation or refactor, tests, and review on this breakdown agent.
3. Keep developing in Bob so the session history is real.
4. Export the Bob session / report for judges. Do not invent sessions.

Until that happens, this project does **not** meet the IBM track Bob requirement. The watsonx hook is necessary but not sufficient.
