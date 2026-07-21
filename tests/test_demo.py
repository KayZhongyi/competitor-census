from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DemoTest(unittest.TestCase):
    def test_demo_builds_evidence_linked_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.html"
            summary_path = Path(tmp) / "summary.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/run_demo.py"),
                    "--output",
                    str(report),
                    "--json",
                    str(summary_path),
                    "--quiet",
                ],
                check=True,
                cwd=ROOT,
            )

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            rendered = report.read_text(encoding="utf-8")

            self.assertEqual(summary["content_rows"], 18)
            self.assertEqual(summary["comment_rows"], 16)
            self.assertEqual(summary["top_topic"], "price")
            self.assertEqual(summary["deep_dive_channels"], 3)
            self.assertIn("Evidence ledger", rendered)
            self.assertIn("Fictional", rendered)
            self.assertIn("NS-010", rendered)


if __name__ == "__main__":
    unittest.main()
