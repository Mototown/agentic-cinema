from __future__ import annotations

from collections import defaultdict

from agentic_cinema.models import Scene, ShootingGroup

# Human-readable labels for the INT/EXT prefix used in reason strings.
_SETUP_LABEL: dict[str, str] = {
    "INT.": "interior",
    "EXT.": "exterior",
    "INT./EXT.": "interior/exterior",
    "EXT./INT.": "exterior/interior",
}


def shooting_groups(scenes: list[Scene]) -> list[ShootingGroup]:
    # Key includes int_ext so that INT and EXT at the same location are
    # treated as separate setups (different lighting rig, permits, weather).
    buckets: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for scene in scenes:
        buckets[(scene.int_ext, scene.location, scene.time_of_day)].append(scene.number)
    groups: list[ShootingGroup] = []
    for (int_ext, location, tod), nums in sorted(buckets.items(), key=lambda kv: kv[1][0]):
        setup = _SETUP_LABEL.get(int_ext, int_ext.rstrip(".").lower())
        n = len(nums)
        scene_word = "scene" if n == 1 else "scenes"
        reason = (
            f"{int_ext} {location} — {setup}, {tod.lower()}, {n} {scene_word}. "
            f"Separate setup from any EXT/INT counterpart at this location."
            if int_ext in ("INT.", "INT./EXT.", "EXT./INT.")
            else f"{int_ext} {location} — {setup}, {tod.lower()}, {n} {scene_word}."
        )
        groups.append(
            ShootingGroup(
                location=location,
                time_of_day=tod,
                scene_numbers=nums,
                reason=reason,
            )
        )
    return groups
