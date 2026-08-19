from __future__ import annotations

from collections import defaultdict

from agentic_cinema.models import Scene, ShootingGroup


def shooting_groups(scenes: list[Scene]) -> list[ShootingGroup]:
    buckets: dict[tuple[str, str], list[int]] = defaultdict(list)
    for scene in scenes:
        buckets[(scene.location, scene.time_of_day)].append(scene.number)
    groups: list[ShootingGroup] = []
    for (location, tod), nums in sorted(buckets.items(), key=lambda kv: kv[1][0]):
        groups.append(
            ShootingGroup(
                location=location,
                time_of_day=tod,
                scene_numbers=nums,
                reason=f"Same location + {tod.lower()} — typical one-move company move.",
            )
        )
    return groups
