"""IBM watsonx.ai hook (IBM track product call).

Uses IBM Cloud IAM + watsonx text generation. No secrets in code.
If WATSONX_API_KEY or WATSONX_PROJECT_ID is missing, does not call the network.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

IAM_URL = "https://iam.cloud.ibm.com/identity/token"
DEFAULT_URL = "https://us-south.ml.cloud.ibm.com"
DEFAULT_MODEL = "ibm/granite-3-8b-instruct"


class WatsonxClient:
    def __init__(
        self,
        api_key: str | None = None,
        project_id: str | None = None,
        url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = (api_key or os.environ.get("WATSONX_API_KEY") or os.environ.get("WATSONX_APIKEY") or "").strip()
        self.project_id = (project_id or os.environ.get("WATSONX_PROJECT_ID") or "").strip()
        self.url = (url or os.environ.get("WATSONX_URL") or DEFAULT_URL).rstrip("/")
        self.model = (model or os.environ.get("WATSONX_MODEL") or DEFAULT_MODEL).strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.project_id)

    def missing(self) -> list[str]:
        miss = []
        if not self.api_key:
            miss.append("WATSONX_API_KEY")
        if not self.project_id:
            miss.append("WATSONX_PROJECT_ID")
        return miss

    def review_continuity(self, payload: dict[str, Any]) -> dict[str, Any]:
        notes = list(payload.get("notes") or [])
        if not self.enabled:
            notes.append(
                "IBM watsonx.ai skipped: set WATSONX_API_KEY and WATSONX_PROJECT_ID to call Granite."
            )
            payload["notes"] = notes
            return payload
        try:
            extra = self._generate(_prompt(payload))
            flags = _flags_from_text(extra)
            if flags:
                payload["continuity_flags"] = list(payload.get("continuity_flags") or []) + flags
            notes.append(f"IBM watsonx.ai ({self.model}) reviewed continuity flags.")
        except Exception as exc:
            notes.append(f"IBM watsonx.ai call failed ({type(exc).__name__}). Local/Gemini breakdown kept.")
        payload["notes"] = notes
        return payload

    def _iam_token(self) -> str:
        body = urllib.parse.urlencode(
            {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key,
            }
        ).encode()
        req = urllib.request.Request(
            IAM_URL,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        token = data.get("access_token")
        if not token:
            raise RuntimeError("IAM token response had no access_token")
        return str(token)

    def _generate(self, prompt: str) -> str:
        token = self._iam_token()
        endpoint = f"{self.url}/ml/v1/text/generation?version=2024-05-31"
        payload = {
            "model_id": self.model,
            "input": prompt,
            "project_id": self.project_id,
            "parameters": {"max_new_tokens": 400, "temperature": 0.1},
        }
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"watsonx HTTP {exc.code}") from exc
        results = data.get("results") or []
        if not results:
            raise RuntimeError("watsonx returned no results")
        return str(results[0].get("generated_text") or "")


def _prompt(payload: dict[str, Any]) -> str:
    slim = {
        "scenes": [
            {
                "number": s.get("number"),
                "heading": s.get("heading"),
                "characters": s.get("characters"),
            }
            for s in (payload.get("scenes") or [])
        ],
        "continuity_flags": payload.get("continuity_flags") or [],
    }
    return (
        "You are a script supervisor. Given this breakdown JSON, list extra continuity risks "
        "as JSON array only: [{\"severity\":\"warn|info\",\"scene_numbers\":[1],\"message\":\"...\"}]. "
        "If none, return []. Do not invent cast or vendors.\n"
        + json.dumps(slim)
    )


def _flags_from_text(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    try:
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end < start:
            return []
        raw = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return []
    out = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if not isinstance(item, dict) or not item.get("message"):
            continue
        nums = []
        for n in item.get("scene_numbers") or []:
            try:
                nums.append(int(n))
            except (TypeError, ValueError):
                continue
        sev = item.get("severity") if item.get("severity") in {"info", "warn"} else "info"
        out.append({"severity": sev, "scene_numbers": nums, "message": str(item["message"])})
    return out
