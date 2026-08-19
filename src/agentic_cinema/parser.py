"""Heuristic screenplay parser. Fountain / production-heading conventions.

This is the local fallback. Gemini can replace or refine it later.
It does not understand every format. It is good enough to return a real breakdown
from a typical INT./EXT. script.
"""

from __future__ import annotations

import re
from pathlib import Path

from agentic_cinema.models import Scene

HEADING = re.compile(
    r"^(INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.)\s+(.+?)(?:\s+[-–—]\s+(DAY|NIGHT|DAWN|DUSK|CONTINUOUS|LATER))?\s*$",
    re.I,
)
CHARACTER = re.compile(r"^([A-Z][A-Z0-9 '\-]{1,30})$")
# Parenthetical extensions that follow a character name cue (stripped before matching)
_PAREN = re.compile(r"\s*\([^)]*\)\s*$")
SKIP_CUES = {"CONT'D", "CONTINUED", "FADE IN", "FADE OUT", "CUT TO", "THE END"}
PROP_VERBS = re.compile(
    r"\b(?:picks? up|grabs?|holds?|puts? down|sets? down|pulls? out|draws?|wields?|checks?)\s+(?:the|a|an|his|her|their)\s+([a-z][a-z0-9 \-]{2,40})",
    re.I,
)
VFX_WORDS = re.compile(
    r"\b(CGI|VFX|visual effects?|explode|explosion|hologram|spaceship|laser|morph|disappear(?:s|ing)?)\b",
    re.I,
)


def load_script(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        return _load_pdf(path)
    return path.read_text(encoding="utf-8", errors="replace")


def _load_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF support needs pypdf. pip install '.[pdf]' or pass a .txt script.") from exc
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def parse_scenes(text: str) -> tuple[str, list[Scene]]:
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    title = "Untitled"
    for ln in lines[:12]:
        stripped = ln.strip()
        if stripped and stripped.upper() not in {"FADE IN:", "FADE IN"} and not HEADING.match(stripped):
            title = stripped.title() if stripped.isupper() else stripped
            break

    scenes: list[Scene] = []
    current: dict | None = None
    body: list[str] = []

    def flush() -> None:
        nonlocal current, body
        if not current:
            return
        blob = "\n".join(body).strip()
        chars = _characters(body)
        props = _props(blob)
        vfx = _vfx(blob)
        scenes.append(
            Scene(
                number=len(scenes) + 1,
                heading=current["heading"],
                int_ext=current["int_ext"],
                location=current["location"],
                time_of_day=current["time_of_day"],
                characters=chars,
                props=props,
                vfx_notes=vfx,
                body=blob,
            )
        )
        current = None
        body = []

    for ln in lines:
        stripped = ln.strip()
        m = HEADING.match(stripped)
        if m:
            flush()
            loc = re.sub(r"\s+", " ", m.group(2)).strip(" .")
            tod = (m.group(3) or "UNSPECIFIED").upper()
            current = {
                "heading": stripped,
                "int_ext": m.group(1).upper(),
                "location": loc.upper(),
                "time_of_day": tod,
            }
            body = []
            continue
        if current is not None:
            body.append(ln)
    flush()
    return title, scenes


def _characters(body_lines: list[str]) -> list[str]:
    found: list[str] = []
    for ln in body_lines:
        s = ln.strip()
        if not s:
            continue
        # Strip trailing parentheticals like (O.S.), (V.O.), (CONT'D) before matching
        name = _PAREN.sub("", s).strip()
        if not CHARACTER.match(name):
            continue
        if any(tok in name for tok in SKIP_CUES):
            continue
        if name not in found:
            found.append(name)
    return found


def _props(blob: str) -> list[str]:
    found: list[str] = []
    for m in PROP_VERBS.finditer(blob):
        prop = re.sub(r"\s+", " ", m.group(1)).strip(" .,").lower()
        if prop and prop not in found:
            found.append(prop)
    return found[:12]


def _vfx(blob: str) -> list[str]:
    hits = sorted({m.group(0).lower() for m in VFX_WORDS.finditer(blob)})
    return [f"Possible VFX cue: {h}" for h in hits]
