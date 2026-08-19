from __future__ import annotations

from agentic_cinema.models import ContinuityFlag, Scene


def flag_continuity(scenes: list[Scene]) -> list[ContinuityFlag]:
    flags: list[ContinuityFlag] = []
    last_loc: dict[str, tuple[int, str]] = {}

    for i, scene in enumerate(scenes):
        for name in scene.characters:
            prev = last_loc.get(name)
            if prev and prev[1] != scene.location:
                prev_scene = scenes[prev[0]]
                same_tod = prev_scene.time_of_day == scene.time_of_day
                if prev[0] == i - 1 and same_tod:
                    flags.append(
                        ContinuityFlag(
                            severity="warn",
                            scene_numbers=[prev_scene.number, scene.number],
                            message=f"{name} is at {prev_scene.location} then {scene.location} in consecutive {scene.time_of_day} scenes with no time flag.",
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
