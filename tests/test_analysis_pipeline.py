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


class AnalysisPipelineTest(unittest.TestCase):
    def make_bundle(self, root: Path) -> tuple[Path, list[dict[str, str]]]:
        bundle = root / "bundle"
        bundle.mkdir()
        analyzed_rows = read_csv(ROOT / "demo/input/content.csv")
        fields = list(analyzed_rows[0])
        raw_rows = []
        for row in analyzed_rows:
            raw = dict(row)
            raw["text_translation"] = ""
            raw["content_type"] = "unclassified"
            raw_rows.append(raw)
        write_csv(bundle / "content.csv", fields, raw_rows)
        shutil.copy(ROOT / "demo/input/platform_census.csv", bundle / "platform_census.csv")
        shutil.copy(ROOT / "demo/input/comments.csv", bundle / "comments.csv")
        (bundle / "run_manifest.json").write_text(
            json.dumps({"target": {"company": "Northstar"}}), encoding="utf-8"
        )
        return bundle, analyzed_rows

    def complete_packet(self, bundle: Path, analyzed_rows: list[dict[str, str]]) -> None:
        grouped: dict[str, list[str]] = defaultdict(list)
        for row in analyzed_rows:
            grouped[row["content_type"]].append(row["record_id"])
        taxonomy = {
            "schema_version": "0.3",
            "target_language": "English",
            "derivation_notes": "Categories were derived after reading the complete fictional corpus.",
            "categories": [
                {
                    "id": category,
                    "label": category.replace("_", " ").title(),
                    "definition": f"Records whose main purpose is {category.replace('_', ' ')}.",
                    "inclusion_criteria": [f"The primary message is {category.replace('_', ' ')}."],
                    "exclusion_criteria": ["The theme is only incidental."],
                    "representative_record_ids": ids[:2],
                }
                for category, ids in grouped.items()
            ],
        }
        (bundle / "analysis/taxonomy.json").write_text(
            json.dumps(taxonomy, indent=2) + "\n", encoding="utf-8"
        )
        fields = [
            "record_id",
            "text_translation",
            "content_type",
            "classification_confidence",
            "classification_notes",
        ]
        results = [
            {
                "record_id": row["record_id"],
                "text_translation": row["text_translation"],
                "content_type": row["content_type"],
                "classification_confidence": "high",
                "classification_notes": "Primary intent is explicit.",
            }
            for row in analyzed_rows
        ]
        write_csv(bundle / "analysis/analysis_results.csv", fields, results)

    def test_prepares_validates_merges_and_reports_without_mutating_raw_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle, analyzed_rows = self.make_bundle(Path(tmp))
            raw_before = (bundle / "content.csv").read_bytes()
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/prepare_analysis.py"),
                    "--bundle",
                    str(bundle),
                ],
                check=True,
                cwd=ROOT,
            )
            self.complete_packet(bundle, analyzed_rows)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/apply_analysis.py"),
                    "--bundle",
                    str(bundle),
                ],
                check=True,
                cwd=ROOT,
            )

            self.assertEqual((bundle / "content.csv").read_bytes(), raw_before)
            merged = read_csv(bundle / "analyzed_content.csv")
            validation = json.loads(
                (bundle / "analysis/validation_report.json").read_text(encoding="utf-8")
            )
            report = (bundle / "analysis_report.html").read_text(encoding="utf-8")
            self.assertEqual(merged[0]["text_translation"], analyzed_rows[0]["text_translation"])
            self.assertEqual(merged[0]["content_type"], analyzed_rows[0]["content_type"])
            self.assertEqual(validation["status"], "passed")
            self.assertEqual(validation["translation_coverage"], 1)
            self.assertIn("Evidence IDs", report)
            self.assertIn("NS-010", report)

    def test_rejects_analysis_when_source_changes_after_packet_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle, analyzed_rows = self.make_bundle(Path(tmp))
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/prepare_analysis.py"),
                    "--bundle",
                    str(bundle),
                ],
                check=True,
                cwd=ROOT,
            )
            self.complete_packet(bundle, analyzed_rows)
            with (bundle / "content.csv").open("a", encoding="utf-8") as handle:
                handle.write("\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/apply_analysis.py"),
                    "--bundle",
                    str(bundle),
                    "--no-report",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            validation = json.loads(
                (bundle / "analysis/validation_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(validation["status"], "failed")
            self.assertIn("content.csv changed", result.stderr)
            self.assertFalse((bundle / "analyzed_content.csv").exists())


if __name__ == "__main__":
    unittest.main()
