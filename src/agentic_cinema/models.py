from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Scene:
    number: int
    heading: str
    int_ext: str
    location: str
    time_of_day: str
    characters: list[str]
    props: list[str]
    vfx_notes: list[str]
    body: str


@dataclass
class ContinuityFlag:
    severity: str  # info | warn
    scene_numbers: list[int]
    message: str


@dataclass
class ShootingGroup:
    location: str
    time_of_day: str
    scene_numbers: list[int]
    reason: str


@dataclass
class Breakdown:
    title: str
    source: str
    engine: str
    characters: list[str]
    locations: list[str]
    props: list[str]
    scenes: list[Scene]
    continuity_flags: list[ContinuityFlag]
    shooting_groups: list[ShootingGroup]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
