from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.gemini_client import GeminiClient
from agentic_cinema.continuity import flag_continuity
from agentic_cinema.groups import shooting_groups
from agentic_cinema.models import Breakdown
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
        locations = []
        for s in scenes:
            if s.location not in locations:
                locations.append(s.location)
        props = []
        for s in scenes:
            for p in s.props:
                if p not in props:
                    props.append(p)
        notes = [
            "Engine is a local heading/character/prop heuristic, not Gemini.",
            "Partner tool is not integrated.",
        ]
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
        refined = self.gemini.refine_breakdown(bd.to_dict())
        if refined.get("notes") and refined["notes"] != bd.notes:
            bd.notes = list(refined["notes"])
        return bd

    def run_json(self, source: str | Path, **kwargs: Any) -> dict[str, Any]:
        return self.run(source, **kwargs).to_dict()
