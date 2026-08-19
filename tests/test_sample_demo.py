"""Lock the local sample demo. IBM Bob / later edits must not change this output.

2026-08-19 (IBM Bob session 1, change 1): parser fix for O.S./V.O. cues correctly
identifies JULES in Scene 1 via 'JULES (O.S.)'. The previous count of 3 continuity
flags included a false-positive "JULES appears in only one scene" flag caused by the
buggy parser missing that cue. Correct count became 2.

2026-08-19 (IBM Bob session 1, change 2): prop continuity cross-checking added.
'tablet' (Scene 1 only) and 'thermos' (Scene 3 only) are each flagged as introduced
but never referenced again — both are correct observations on this script. Flag count
updated from 2 → 4.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from agents.breakdown_agent import BreakdownAgent


class SampleDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        script = ROOT / "examples" / "sample_script.txt"
        cls.data = BreakdownAgent().run_json(script)

    def test_shape(self) -> None:
        d = self.data
        self.assertEqual(d["title"], "Dust On The Glass")
        self.assertEqual(d["engine"], "local-heuristic")
        self.assertEqual(len(d["scenes"]), 4)
        self.assertEqual(len(d["continuity_flags"]), 4)
        self.assertEqual(len(d["shooting_groups"]), 4)
        self.assertEqual(d["characters"], ["ELENA", "JULES", "MARA"])
        self.assertEqual(d["locations"], ["SOLAR FARM", "CONTROL SHED", "ACCESS ROAD"])
        self.assertEqual(d["props"], ["radio", "tablet", "thermos"])

    def test_watsonx_skipped_without_creds(self) -> None:
        notes = " ".join(self.data.get("notes") or [])
        self.assertIn("watsonx.ai skipped", notes)


class WatsonxFailClosedTest(unittest.TestCase):
    def test_disabled_without_env(self) -> None:
        from agents.watsonx_client import WatsonxClient

        client = WatsonxClient(api_key="", project_id="")
        self.assertFalse(client.enabled)
        self.assertEqual(client.missing(), ["WATSONX_API_KEY", "WATSONX_PROJECT_ID"])
        out = client.review_continuity({"notes": []})
        self.assertTrue(any("skipped" in n for n in out["notes"]))


if __name__ == "__main__":
    unittest.main()
