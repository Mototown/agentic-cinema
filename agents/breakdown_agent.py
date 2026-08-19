from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.gemini_client import GeminiClient
from agentic_cinema.continuity import flag_continuity
from agentic_cinema.groups import shooting_groups
from agentic_cinema.models import Breakdown, ContinuityFlag, Scene, ShootingGroup
from agentic_cinema.parser import load_script, parse_scenes


class BreakdownAgent:
    """Accept a screenplay path or raw text. Return a structured breakdown."""

    def __init__(self, gemini: GeminiClient | None = None) -> None:
        self.gemini = gemini or GeminiClient()

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
            "Partner tool is not integrated.",
        ]
        if self.gemini.enabled:
            notes = ["Partner tool is not integrated."]
        if not scenes:
            notes.append("No INT./EXT. scene headings found. Use a production-format script.")
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
        )
        refined = self.gemini.refine_breakdown(text, bd.to_dict())
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
    )
