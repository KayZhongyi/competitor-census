from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_youtube  # noqa: E402


class YouTubeCollectorTest(unittest.TestCase):
    def test_normalizes_supported_channel_urls(self) -> None:
        self.assertEqual(
            collect_youtube.normalize_channel_base("https://m.youtube.com/@Example/videos?view=0"),
            "https://www.youtube.com/@Example",
        )
        self.assertEqual(
            collect_youtube.normalize_channel_base("https://youtube.com/channel/UC123/shorts"),
            "https://www.youtube.com/channel/UC123",
        )
        with self.assertRaises(ValueError):
            collect_youtube.normalize_channel_base("https://www.youtube.com/watch?v=abc")
        with self.assertRaises(ValueError):
            collect_youtube.normalize_channel_base("https://www.youtube.com/@Example/featured")
        self.assertEqual(collect_youtube.parse_since("2026-01-02"), "20260102")
        with self.assertRaises(ValueError):
            collect_youtube.parse_since("02/01/2026")

    def test_live_cli_writes_a_deduplicated_bundle_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            fake_ytdlp = temp / "yt-dlp"
            fake_ytdlp.write_text(
                """#!/usr/bin/env python3
import json
import sys

if "--version" in sys.argv:
    print("2099.01.01-test")
    raise SystemExit(0)

tab = sys.argv[-1].rstrip("/").split("/")[-1]
video_id = "video-1" if tab == "videos" else "short-1"
record = {
    "id": video_id,
    "title": "Public title " + tab,
    "description": "Public description",
    "upload_date": "20260102",
    "timestamp": 1767312000,
    "view_count": 1200 if tab == "videos" else 800,
    "like_count": 80,
    "comment_count": 9,
    "duration": 60,
    "language": "en",
    "channel": "Example Company",
    "channel_id": "UC-EXAMPLE",
    "channel_follower_count": 5000,
    "uploader_id": "@ExampleCompany",
    "uploader_url": "https://www.youtube.com/@ExampleCompany",
    "webpage_url": "https://www.youtube.com/watch?v=" + video_id,
    "availability": "public",
}
print(json.dumps(record))
""",
                encoding="utf-8",
            )
            fake_ytdlp.chmod(0o755)
            output = temp / "bundle"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/collect_youtube.py"),
                    "--company",
                    "Example Company",
                    "--channel",
                    "https://www.youtube.com/@ExampleCompany",
                    "--tabs",
                    "videos,shorts",
                    "--max-items-per-tab",
                    "1",
                    "--since",
                    "2026-01-01",
                    "--yt-dlp",
                    str(fake_ytdlp),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            with (output / "content.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
            report = (output / "report.html").read_text(encoding="utf-8")

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["content_type"], "unclassified")
            self.assertEqual(rows[0]["text_translation"], "")
            self.assertEqual(manifest["collector"]["version"], "2099.01.01-test")
            self.assertEqual(manifest["since"], "2026-01-01")
            self.assertEqual(manifest["counts"]["unique_content"], 2)
            self.assertIn("Comments not included", report)
            self.assertIn("content classification are intentionally pending", report)
            self.assertTrue((output / "analysis/analysis_task.md").exists())
            self.assertTrue((output / "analysis/analysis_results.csv").exists())
            self.assertIn("Captured 2 unique public video records", result.stdout)
            self.assertIn("Next Agent task", result.stdout)


if __name__ == "__main__":
    unittest.main()
