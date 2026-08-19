from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.gemini_client import GeminiClient
from agents.watsonx_client import WatsonxClient
from agentic_cinema.continuity import flag_continuity
from agentic_cinema.groups import shooting_groups
from agentic_cinema.models import Breakdown, ContinuityFlag, Scene, ShootingGroup
from agentic_cinema.parser import load_script, parse_scenes


class BreakdownAgent:
    """Accept a screenplay path or raw text. Return a structured breakdown."""

    def __init__(self, gemini: GeminiClient | None = None, watsonx: WatsonxClient | None = None) -> None:
        self.gemini = gemini or GeminiClient()
        self.watsonx = watsonx or WatsonxClient()

    def run(self, source: str | Path, *, raw_text: str | None = None) -> Breakdown:
        if raw_text is None:
            text = load_script(source)
            source_name = str(source)
        else:
            text = raw_text
            source_name = str(source)
        title, scenes = parse_scenes(text)
        characters = sorted({c for s in scenes for c in s.characters})
        locations: list[str] = []
        for s in scenes:
            if s.location not in locations:
                locations.append(s.location)
        props: list[str] = []
        for s in scenes:
            for p in s.props:
                if p not in props:
                    props.append(p)
        notes = [
            "Engine is a local heading/character/prop heuristic until Gemini runs.",
        ]
        if self.gemini.enabled:
            notes = []
        if not scenes:
            notes.append("No INT./EXT. scene headings found. Use a production-format script.")
        quality_notes = _build_quality_notes(scenes, self.gemini, self.watsonx)
        bd = Breakdown(
            title=title,
            source=source_name,
            engine="local-heuristic",
            characters=characters,
            locations=locations,
            props=props,
            scenes=scenes,
            continuity_flags=flag_continuity(scenes),
            shooting_groups=shooting_groups(scenes),
            notes=notes,
            quality_notes=quality_notes,
        )
        refined = self.gemini.refine_breakdown(text, bd.to_dict())
        refined = self.watsonx.review_continuity(refined)
        return _hydrate(refined, source_name=source_name, original_scenes=scenes)

    def run_json(self, source: str | Path, **kwargs: Any) -> dict[str, Any]:
        return self.run(source, **kwargs).to_dict()


def _hydrate(data: dict[str, Any], *, source_name: str, original_scenes: list[Scene]) -> Breakdown:
    bodies = {s.number: s.body for s in original_scenes}
    scenes: list[Scene] = []
    for raw in data.get("scenes") or []:
        try:
            num = int(raw.get("number"))
        except (TypeError, ValueError):
            continue
        scenes.append(
            Scene(
                number=num,
                heading=str(raw.get("heading") or ""),
                int_ext=str(raw.get("int_ext") or ""),
                location=str(raw.get("location") or ""),
                time_of_day=str(raw.get("time_of_day") or ""),
                characters=list(raw.get("characters") or []),
                props=list(raw.get("props") or []),
                vfx_notes=list(raw.get("vfx_notes") or []),
                body=str(raw.get("body") or bodies.get(num, "")),
            )
        )
    if not scenes:
        scenes = original_scenes
    flags = [
        ContinuityFlag(
            severity=str(f.get("severity") or "info"),
            scene_numbers=[int(n) for n in (f.get("scene_numbers") or [])],
            message=str(f.get("message") or ""),
        )
        for f in (data.get("continuity_flags") or [])
        if isinstance(f, dict)
    ]
    groups = [
        ShootingGroup(
            location=str(g.get("location") or ""),
            time_of_day=str(g.get("time_of_day") or ""),
            scene_numbers=[int(n) for n in (g.get("scene_numbers") or [])],
            reason=str(g.get("reason") or ""),
        )
        for g in (data.get("shooting_groups") or [])
        if isinstance(g, dict)
    ]
    return Breakdown(
        title=str(data.get("title") or "Untitled"),
        source=str(data.get("source") or source_name),
        engine=str(data.get("engine") or "local-heuristic"),
        characters=list(data.get("characters") or []),
        locations=list(data.get("locations") or []),
        props=list(data.get("props") or []),
        scenes=scenes,
        continuity_flags=flags,
        shooting_groups=groups,
        notes=list(data.get("notes") or []),
        quality_notes=list(data.get("quality_notes") or []),
    )


def _build_quality_notes(
    scenes: list[Scene],
    gemini: "GeminiClient",
    watsonx: "WatsonxClient",
) -> list[str]:
    """Summarise analysis completeness for the coordinator."""
    qn: list[str] = []
    n = len(scenes)
    if n == 0:
        qn.append("No scenes parsed — check that the script uses INT./EXT. headings.")
        return qn
    qn.append(f"{n} scene{'s' if n != 1 else ''} parsed.")
    chars_with_props = sum(1 for s in scenes if s.props)
    qn.append(
        f"Props extracted from {chars_with_props} of {n} scene{'s' if n != 1 else ''} "
        f"using verb-pattern heuristic (picks up / grabs / holds etc.)."
    )
    vfx_scenes = [s.number for s in scenes if s.vfx_notes]
    if vfx_scenes:
        qn.append(f"VFX keywords detected in scene{'s' if len(vfx_scenes) != 1 else ''} {vfx_scenes}.")
    else:
        qn.append("No VFX keywords detected.")
    if gemini.enabled:
        qn.append(f"Gemini ({gemini.model}) will refine characters, props, and flags.")
    else:
        qn.append("Gemini not active (GEMINI_API_KEY not set) — using local heuristic only.")
    if watsonx.enabled:
        qn.append(f"IBM watsonx.ai ({watsonx.model}) will review continuity flags.")
    else:
        qn.append("IBM watsonx.ai not active (WATSONX_API_KEY / WATSONX_PROJECT_ID not set).")
    qn.append(
        "Prop detection uses verb patterns only — props mentioned without a handling verb may be missed."
    )
    return qn
