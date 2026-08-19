from __future__ import annotations

from collections import defaultdict

from agentic_cinema.models import ContinuityFlag, Scene

# Maximum scene gap within which a same-time-of-day location jump is flagged as
# a potential teleportation. Increase for feature-length scripts.
_DEFAULT_TELEPORT_WINDOW = 5


def flag_continuity(scenes: list[Scene], *, max_scene_gap: int = _DEFAULT_TELEPORT_WINDOW) -> list[ContinuityFlag]:
    flags: list[ContinuityFlag] = []
    # Maps character name → (scene_index, location) of their most recent appearance
    last_loc: dict[str, tuple[int, str]] = {}

    for i, scene in enumerate(scenes):
        for name in scene.characters:
            prev = last_loc.get(name)
            if prev is not None:
                prev_idx, prev_location = prev
                gap = i - prev_idx
                if prev_location != scene.location:
                    prev_scene = scenes[prev_idx]
                    same_tod = prev_scene.time_of_day == scene.time_of_day
                    # Flag if same time-of-day and within the scene window.
                    # Consecutive scenes are flagged regardless of gap (gap==1 always qualifies).
                    if same_tod and gap <= max_scene_gap:
                        if gap == 1:
                            msg = (
                                f"{name} is at {prev_location} then {scene.location} "
                                f"in consecutive {scene.time_of_day} scenes with no time flag."
                            )
                        else:
                            msg = (
                                f"{name} moves from {prev_location} (Scene {prev_scene.number}) "
                                f"to {scene.location} (Scene {scene.number}) "
                                f"across {gap} scenes with no location transition — check travel time."
                            )
                        flags.append(
                            ContinuityFlag(
                                severity="warn",
                                scene_numbers=[prev_scene.number, scene.number],
                                message=msg,
                            )
                        )
            last_loc[name] = (i, scene.location)

        if i > 0:
            prev = scenes[i - 1]
            if (
                prev.location == scene.location
                and prev.time_of_day in {"DAY", "NIGHT"}
                and scene.time_of_day in {"DAY", "NIGHT"}
                and prev.time_of_day != scene.time_of_day
            ):
                flags.append(
                    ContinuityFlag(
                        severity="warn",
                        scene_numbers=[prev.number, scene.number],
                        message=f"{scene.location} flips {prev.time_of_day} → {scene.time_of_day} in consecutive scenes. Confirm a time cut.",
                    )
                )

        if scene.int_ext.startswith("INT") and scene.time_of_day == "UNSPECIFIED":
            flags.append(
                ContinuityFlag(
                    severity="info",
                    scene_numbers=[scene.number],
                    message=f"Scene {scene.number} heading has no DAY/NIGHT. Breakdown will group it as UNSPECIFIED.",
                )
            )

    mentioned = {n for s in scenes for n in s.characters}
    if len(mentioned) >= 2:
        only_once = [n for n in mentioned if sum(1 for s in scenes if n in s.characters) == 1]
        for name in only_once:
            sc = next(s.number for s in scenes if name in s.characters)
            flags.append(
                ContinuityFlag(
                    severity="info",
                    scene_numbers=[sc],
                    message=f"{name} appears in only one scene. Easy to drop from a shooting day by accident.",
                )
            )

    flags.extend(_prop_continuity(scenes))
    return flags


def _prop_continuity(scenes: list[Scene]) -> list[ContinuityFlag]:
    """Flag props that appear in only one non-final scene (introduced and never seen again)
    and props that reappear after a gap of more than 3 scenes without re-introduction."""
    if not scenes:
        return []

    # Build prop → sorted list of scene indices (0-based) where the prop is present
    prop_scene_indices: dict[str, list[int]] = defaultdict(list)
    for i, scene in enumerate(scenes):
        for prop in scene.props:
            prop_scene_indices[prop].append(i)

    last_idx = len(scenes) - 1
    flags: list[ContinuityFlag] = []

    for prop, indices in sorted(prop_scene_indices.items()):
        # Only flag props that appear in at least one non-final scene
        non_final = [idx for idx in indices if idx != last_idx]
        if not non_final:
            continue

        # Case 1: prop appears in exactly one scene and it is not the final scene —
        # it was introduced but never referenced again.
        if len(indices) == 1:
            sc_num = scenes[indices[0]].number
            flags.append(
                ContinuityFlag(
                    severity="info",
                    scene_numbers=[sc_num],
                    message=(
                        f"Prop '{prop}' appears in Scene {sc_num} only. "
                        f"Confirm it is intentionally dropped or add a later reference."
                    ),
                )
            )
            continue

        # Case 2: prop reappears after a gap of more than 3 scenes — possible magic-prop error.
        for a, b in zip(indices, indices[1:]):
            gap = b - a
            if gap > 3:
                sc_a = scenes[a].number
                sc_b = scenes[b].number
                flags.append(
                    ContinuityFlag(
                        severity="info",
                        scene_numbers=[sc_a, sc_b],
                        message=(
                            f"Prop '{prop}' seen in Scene {sc_a}, "
                            f"absent for {gap} scenes, then reappears in Scene {sc_b}. "
                            f"Confirm it was not left behind."
                        ),
                    )
                )

    return flags
