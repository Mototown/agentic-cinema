from __future__ import annotations

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
    return flags
