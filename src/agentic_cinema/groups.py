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

# Practical notes appended to reason strings based on setup type and time of day.
_PRACTICAL: dict[tuple[str, str], str] = {
    ("EXT.", "DAY"):        "Natural light — schedule around golden hour if needed. Weather cover required.",
    ("EXT.", "NIGHT"):      "Artificial lighting package needed. Generator + night permits likely.",
    ("EXT.", "DAWN"):       "Narrow shooting window (~30 min). Needs precise call time.",
    ("EXT.", "DUSK"):       "Narrow shooting window (~30 min). Needs precise call time.",
    ("INT.", "DAY"):        "Controlled interior — lighting rig needed if windows are in frame.",
    ("INT.", "NIGHT"):      "Controlled interior — full lighting rig, no daylight continuity risk.",
    ("INT.", "DAWN"):       "Controlled interior — match exterior dawn light through windows if practical.",
    ("INT.", "DUSK"):       "Controlled interior — match exterior dusk light through windows if practical.",
    ("INT./EXT.", "DAY"):   "Mixed setup — coordinate interior rig with exterior natural light.",
    ("INT./EXT.", "NIGHT"): "Mixed setup — full artificial rig for both sides of threshold.",
    ("EXT./INT.", "DAY"):   "Mixed setup — coordinate interior rig with exterior natural light.",
    ("EXT./INT.", "NIGHT"): "Mixed setup — full artificial rig for both sides of threshold.",
}
_PRACTICAL_DEFAULT = "Check lighting, permits, and weather cover for this setup."


def shooting_groups(scenes: list[Scene]) -> list[ShootingGroup]:
    # Key includes int_ext so that INT and EXT at the same location are
    # treated as separate setups (different lighting rig, permits, weather).
    buckets: dict[tuple[str, str, str], list[Scene]] = defaultdict(list)
    for scene in scenes:
        buckets[(scene.int_ext, scene.location, scene.time_of_day)].append(scene)
    groups: list[ShootingGroup] = []
    # Sort by first scene number so output order is script order
    for (int_ext, location, tod), group_scenes in sorted(
        buckets.items(), key=lambda kv: kv[1][0].number
    ):
        nums = [s.number for s in group_scenes]
        setup = _SETUP_LABEL.get(int_ext, int_ext.rstrip(".").lower())
        n = len(nums)
        scene_word = "scene" if n == 1 else "scenes"

        # Collect cast and VFX flags across the group's scenes
        cast: list[str] = []
        for s in group_scenes:
            for c in s.characters:
                if c not in cast:
                    cast.append(c)
        has_vfx = any(s.vfx_notes for s in group_scenes)

        cast_note = f"Cast: {', '.join(cast)}." if cast else "No characters identified."
        vfx_note = " VFX elements present — check rig/post requirements." if has_vfx else ""
        practical = _PRACTICAL.get((int_ext, tod), _PRACTICAL_DEFAULT)

        reason = (
            f"{n} {scene_word}, {setup}, {tod.lower()}. "
            f"{cast_note}"
            f"{vfx_note} "
            f"{practical}"
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
