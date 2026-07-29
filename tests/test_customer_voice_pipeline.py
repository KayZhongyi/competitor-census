from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class CustomerVoicePipelineTest(unittest.TestCase):
    def make_bundle(self, root: Path) -> Path:
        bundle = root / "bundle"
        bundle.mkdir()
        shutil.copy(ROOT / "demo/input/content.csv", bundle / "content.csv")
        shutil.copy(ROOT / "demo/input/comments.csv", bundle / "comments.csv")
        shutil.copy(ROOT / "demo/input/platform_census.csv", bundle / "platform_census.csv")
        (bundle / "run_manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "0.4",
                    "research_mode": "customer_voice",
                    "target": {"company": "Northstar"},
                }
            ),
            encoding="utf-8",
        )
        return bundle

    def complete_packet(self, bundle: Path) -> None:
        customer_rows = [
            row
            for row in read_csv(bundle / "comments.csv")
            if row["is_official"].lower() != "true"
        ]
        grouped: dict[str, list[str]] = defaultdict(list)
        for row in customer_rows:
            grouped[row["topic"]].append(row["comment_id"])
        taxonomy = {
            "schema_version": "0.4",
            "target_language": "English",
            "derivation_notes": "Issues emerged after reading every fictional customer signal.",
            "issues": [
                {
                    "id": issue,
                    "label": issue.replace("_", " ").title(),
                    "definition": f"Customer signals primarily about {issue.replace('_', ' ')}.",
                    "inclusion_criteria": [f"The main ask concerns {issue.replace('_', ' ')}."],
                    "exclusion_criteria": ["The issue is only incidental."],
                    "representative_comment_ids": ids[:2],
                }
                for issue, ids in grouped.items()
            ],
        }
        (bundle / "voice/voice_taxonomy.json").write_text(
            json.dumps(taxonomy, indent=2) + "\n", encoding="utf-8"
        )
        results = []
        for row in customer_rows:
            severity = "high" if row["topic"] == "compatibility" else "low"
            results.append(
                {
                    "comment_id": row["comment_id"],
                    "text_translation": row["text_translation"],
                    "issue_type": row["topic"],
                    "signal_type": "question",
                    "sentiment": "neutral",
                    "severity": severity,
                    "analysis_confidence": "high",
                    "analysis_notes": (
                        "Compatibility uncertainty can block installation."
                        if severity == "high"
                        else "The customer asks a concrete informational question."
                    ),
                }
            )
        write_csv(
            bundle / "voice/voice_results.csv",
            [
                "comment_id",
                "text_translation",
                "issue_type",
                "signal_type",
                "sentiment",
                "severity",
                "analysis_confidence",
                "analysis_notes",
            ],
            results,
        )

    def test_prepares_validates_redacts_and_reports_without_mutating_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.make_bundle(Path(tmp))
            comments_before = (bundle / "comments.csv").read_bytes()
            content_before = (bundle / "content.csv").read_bytes()
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/prepare_customer_voice.py"),
                    "--bundle",
                    str(bundle),
                ],
                check=True,
                cwd=ROOT,
            )
            self.complete_packet(bundle)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/apply_customer_voice.py"),
                    "--bundle",
                    str(bundle),
                ],
                check=True,
                cwd=ROOT,
            )

            self.assertEqual((bundle / "comments.csv").read_bytes(), comments_before)
            self.assertEqual((bundle / "content.csv").read_bytes(), content_before)
            analyzed = read_csv(bundle / "analyzed_voice.csv")
            validation = json.loads(
                (bundle / "voice/validation_report.json").read_text(encoding="utf-8")
            )
            summary = json.loads(
                (bundle / "customer_voice_summary.json").read_text(encoding="utf-8")
            )
            report = (bundle / "customer_voice_report.html").read_text(encoding="utf-8")

            self.assertEqual(len(analyzed), 12)
            self.assertNotIn("commenter", analyzed[0])
            self.assertTrue(analyzed[0]["commenter_alias"].startswith("voice-"))
            self.assertEqual(validation["status"], "passed")
            self.assertEqual(summary["visible_response_count"], 4)
            self.assertEqual(summary["useful_response_count"], 1)
            self.assertIn("Redacted evidence ledger", report)
            self.assertNotIn("user_001", report)
            self.assertIn("https://example.com/comment/C-001", report)

    def test_rejects_stale_comment_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self.make_bundle(Path(tmp))
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/prepare_customer_voice.py"),
                    "--bundle",
                    str(bundle),
                ],
                check=True,
                cwd=ROOT,
            )
            self.complete_packet(bundle)
            with (bundle / "comments.csv").open("a", encoding="utf-8") as handle:
                handle.write("\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/apply_customer_voice.py"),
                    "--bundle",
                    str(bundle),
                    "--no-report",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            validation = json.loads(
                (bundle / "voice/validation_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(validation["status"], "failed")
            self.assertIn("comments.csv changed", result.stdout)
            self.assertFalse((bundle / "analyzed_voice.csv").exists())


if __name__ == "__main__":
    unittest.main()
