"""Real Gemini calls via the official Google Gen AI SDK (`google-genai`).

Uses GEMINI_API_KEY. Does not run unless the key is set, so the sample
demo still works offline. Agent Builder is not used here.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM = """You are a script supervisor helping an AD break down a screenplay.
Return ONLY valid JSON matching this schema (no markdown):
{
  "title": string,
  "characters": [string],
  "locations": [string],
  "props": [string],
  "scenes": [{
    "number": int,
    "heading": string,
    "int_ext": string,
    "location": string,
    "time_of_day": string,
    "characters": [string],
    "props": [string],
    "vfx_notes": [string]
  }],
  "continuity_flags": [{
    "severity": "info" | "warn",
    "scene_numbers": [int],
    "message": string
  }],
  "shooting_groups": [{
    "location": string,
    "time_of_day": string,
    "scene_numbers": [int],
    "reason": string
  }]
}
Rules:
- Use the local skeleton as the scene list. Do not drop or renumber scenes.
- Improve characters, props, VFX notes, continuity flags, and shooting groups.
- Continuity flags must be grounded in the text (time jumps, wardrobe/prop, geography).
- Do not invent cast, vendors, or production companies.
"""


class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = (api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
        self.model = (model or os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL).strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def refine_breakdown(self, script_text: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return payload
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            payload.setdefault("notes", []).append(
                "GEMINI_API_KEY is set but google-genai is not installed. pip install google-genai"
            )
            return payload

        slim = {
            "title": payload.get("title"),
            "scenes": [
                {
                    "number": s.get("number"),
                    "heading": s.get("heading"),
                    "int_ext": s.get("int_ext"),
                    "location": s.get("location"),
                    "time_of_day": s.get("time_of_day"),
                    "characters": s.get("characters"),
                    "props": s.get("props"),
                    "vfx_notes": s.get("vfx_notes"),
                }
                for s in payload.get("scenes", [])
            ],
            "continuity_flags": payload.get("continuity_flags", []),
            "shooting_groups": payload.get("shooting_groups", []),
        }
        prompt = (
            SYSTEM
            + "\n\nLOCAL SKELETON JSON:\n"
            + json.dumps(slim, indent=2)
            + "\n\nSCREENPLAY:\n"
            + script_text[:24000]
        )
        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            text = (response.text or "").strip()
            parsed = _parse_json(text)
            if not isinstance(parsed, dict):
                raise ValueError("Gemini did not return a JSON object")
            return _merge(payload, parsed, self.model)
        except Exception as exc:
            payload.setdefault("notes", []).append(
                f"Gemini call failed ({type(exc).__name__}). Local heuristic breakdown returned."
            )
            return payload


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _merge(local: dict[str, Any], remote: dict[str, Any], model: str) -> dict[str, Any]:
    out = dict(local)
    out["engine"] = f"local-heuristic+{model}"
    for key in ("title", "characters", "locations", "props"):
        val = remote.get(key)
        if val:
            out[key] = val
    if isinstance(remote.get("continuity_flags"), list) and remote["continuity_flags"]:
        out["continuity_flags"] = remote["continuity_flags"]
    if isinstance(remote.get("shooting_groups"), list) and remote["shooting_groups"]:
        out["shooting_groups"] = remote["shooting_groups"]
    local_scenes = {int(s["number"]): s for s in local.get("scenes", []) if "number" in s}
    if isinstance(remote.get("scenes"), list):
        merged_scenes = []
        for rs in remote["scenes"]:
            try:
                num = int(rs.get("number"))
            except (TypeError, ValueError):
                continue
            base = dict(local_scenes.get(num, {}))
            for field in ("heading", "int_ext", "location", "time_of_day", "characters", "props", "vfx_notes"):
                if rs.get(field) not in (None, "", []):
                    base[field] = rs[field]
            if base:
                merged_scenes.append(base)
        if len(merged_scenes) == len(local.get("scenes", [])):
            out["scenes"] = merged_scenes
    notes = list(local.get("notes") or [])
    notes = [n for n in notes if "not Gemini" not in n and "local heading" not in n.lower()]
    notes.insert(0, f"Gemini ({model}) refined the local skeleton.")
    out["notes"] = notes
    return out
