"""Gemini hook. Not called unless GEMINI_API_KEY is set.

Agent Builder / Vertex wiring is not in this version.
"""

from __future__ import annotations

import os
from typing import Any


class GeminiClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def refine_breakdown(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return payload
        # Placeholder: first working version does not call the network.
        # Next priority is a real generateContent pass, then Agent Builder.
        payload.setdefault("notes", []).append(
            "GEMINI_API_KEY is set but Gemini refine is not wired yet. Local breakdown returned as-is."
        )
        return payload
