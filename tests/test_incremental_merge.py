from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["record_id", "text", "views", "collected_at"]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


class IncrementalMergeTest(unittest.TestCase):
    def test_merges_by_stable_id_and_reports_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.csv"
            incoming = root / "incoming.csv"
            output = root / "merged.csv"
            write_csv(
                base,
                [
                    {"record_id": "A", "text": "one", "views": "10", "collected_at": "t1"},
                    {"record_id": "B", "text": "two", "views": "20", "collected_at": "t1"},
                    {"record_id": "C", "text": "three", "views": "30", "collected_at": "t1"},
                ],
            )
            write_csv(
                incoming,
                [
                    {"record_id": "A", "text": "one", "views": "10", "collected_at": "t2"},
                    {"record_id": "B", "text": "two", "views": "25", "collected_at": "t2"},
                    {"record_id": "D", "text": "four", "views": "40", "collected_at": "t2"},
                ],
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/merge_incremental.py"),
                    "--base",
                    str(base),
                    "--incoming",
                    str(incoming),
                    "--output",
                    str(output),
                ],
                check=True,
                cwd=ROOT,
            )
            with output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            report = json.loads(
                (root / "merged_merge_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual([row["record_id"] for row in rows], ["A", "B", "C", "D"])
            self.assertEqual(rows[1]["views"], "25")
            self.assertEqual(rows[0]["collected_at"], "t2")
            self.assertEqual(report["new"], 1)
            self.assertEqual(report["updated"], 1)
            self.assertEqual(report["unchanged"], 1)
            self.assertEqual(report["absent_from_incoming"], 1)
            self.assertEqual(
                report["updated_records"],
                [{"id": "B", "changed_fields": ["views"], "change_kinds": ["engagement"]}],
            )

    def test_refuses_to_overwrite_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.csv"
            write_csv(
                path,
                [{"record_id": "A", "text": "one", "views": "10", "collected_at": "t1"}],
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/merge_incremental.py"),
                    "--base",
                    str(path),
                    "--incoming",
                    str(path),
                    "--output",
                    str(path),
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)


if __name__ == "__main__":
    unittest.main()
