#!/usr/bin/env python3
"""Validate a Competitor Census evidence bundle and render a static report."""

from __future__ import annotations

import argparse
import csv
import html
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CONTENT_FIELDS = {
    "record_id",
    "platform",
    "account",
    "published_at",
    "language",
    "text_original",
    "text_translation",
    "views",
    "likes",
    "comments_count",
    "shares",
    "url",
    "content_type",
    "brand",
}
COMMENT_FIELDS = {
    "comment_id",
    "content_id",
    "parent_comment_id",
    "commenter",
    "commenter_type",
    "is_official",
    "text_original",
    "text_translation",
    "likes",
    "topic",
    "response_mode",
    "url",
}
CENSUS_FIELDS = {
    "platform",
    "handle",
    "url",
    "identity_status",
    "identity_evidence",
    "followers",
    "visible_items",
    "last_active_at",
    "deep_dive",
    "notes",
}


def load_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = sorted(required - fields)
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: dataset is empty")
    return rows


def number(value: str | None) -> int:
    if value is None or not value.strip():
        return 0
    return int(float(value.replace(",", "").strip()))


def ensure_unique(rows: Iterable[dict[str, str]], key: str, label: str) -> None:
    values = [row[key] for row in rows]
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise ValueError(f"{label}: duplicate {key}: {', '.join(duplicates)}")


def analyze(
    census: list[dict[str, str]],
    content: list[dict[str, str]],
    comments: list[dict[str, str]],
) -> dict[str, object]:
    ensure_unique(content, "record_id", "content")
    ensure_unique(comments, "comment_id", "comments")

    content_ids = {row["record_id"] for row in content}
    orphaned = sorted({row["content_id"] for row in comments} - content_ids)
    if orphaned:
        raise ValueError(f"comments: unknown content_id: {', '.join(orphaned)}")

    by_type: dict[str, list[int]] = defaultdict(list)
    for row in content:
        by_type[row["content_type"]].append(number(row["views"]))

    category_stats = []
    for category, values in by_type.items():
        category_stats.append(
            {
                "category": category,
                "count": len(values),
                "share": len(values) / len(content),
                "mean_views": round(statistics.mean(values)),
                "median_views": round(statistics.median(values)),
            }
        )
    category_stats.sort(key=lambda item: (-int(item["mean_views"]), str(item["category"])))

    user_comments = [row for row in comments if row["is_official"].lower() != "true"]
    official_replies = [row for row in comments if row["is_official"].lower() == "true"]
    topic_counts = Counter(row["topic"] for row in user_comments if row["topic"])
    response_counts = Counter(row["response_mode"] for row in official_replies if row["response_mode"])
    platforms = Counter(row["platform"] for row in content)
    selected_channels = [row for row in census if row["deep_dive"].lower() == "yes"]
    evidence = sorted(content, key=lambda row: number(row["views"]), reverse=True)[:6]

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "dataset": "Fictional Northstar Home Energy demo",
        "census_channels": len(census),
        "deep_dive_channels": len(selected_channels),
        "content_rows": len(content),
        "comment_rows": len(comments),
        "user_comments": len(user_comments),
        "official_replies": len(official_replies),
        "total_views": sum(number(row["views"]) for row in content),
        "platforms": dict(sorted(platforms.items())),
        "category_stats": category_stats,
        "topic_counts": dict(topic_counts.most_common()),
        "response_counts": dict(response_counts.most_common()),
        "top_topic": topic_counts.most_common(1)[0][0] if topic_counts else None,
        "evidence": [
            {
                "record_id": row["record_id"],
                "platform": row["platform"],
                "published_at": row["published_at"],
                "translation": row["text_translation"],
                "views": number(row["views"]),
                "url": row["url"],
            }
            for row in evidence
        ],
    }


def pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def render_report(summary: dict[str, object]) -> str:
    categories = summary["category_stats"]
    assert isinstance(categories, list)
    max_views = max(int(item["mean_views"]) for item in categories) or 1

    category_rows = "\n".join(
        f"""
        <tr>
          <td><strong>{html.escape(str(item['category']).replace('_', ' ').title())}</strong></td>
          <td>{item['count']}</td>
          <td>{pct(float(item['share']))}</td>
          <td>{int(item['mean_views']):,}</td>
          <td>{int(item['median_views']):,}</td>
          <td><div class="bar"><i style="width:{int(item['mean_views']) / max_views * 100:.1f}%"></i></div></td>
        </tr>"""
        for item in categories
    )

    topic_counts = summary["topic_counts"]
    assert isinstance(topic_counts, dict)
    user_comments = int(summary["user_comments"])
    topic_chips = "".join(
        f"<span class='chip'><b>{html.escape(str(topic).replace('_', ' ').title())}</b> {count}/{user_comments}</span>"
        for topic, count in topic_counts.items()
    )

    response_counts = summary["response_counts"]
    assert isinstance(response_counts, dict)
    official_replies = int(summary["official_replies"])
    response_text = ", ".join(
        f"{str(mode).replace('_', ' ')} {count}/{official_replies}"
        for mode, count in response_counts.items()
    )

    evidence = summary["evidence"]
    assert isinstance(evidence, list)
    evidence_rows = "\n".join(
        f"""
        <tr>
          <td><code>{html.escape(str(row['record_id']))}</code></td>
          <td>{html.escape(str(row['platform']))}</td>
          <td>{html.escape(str(row['published_at']))}</td>
          <td>{html.escape(str(row['translation']))}</td>
          <td>{int(row['views']):,}</td>
          <td><a href="{html.escape(str(row['url']), quote=True)}">source ↗</a></td>
        </tr>"""
        for row in evidence
    )

    best = categories[0]
    most_published = max(categories, key=lambda item: int(item["count"]))
    top_topic = str(summary["top_topic"] or "none").replace("_", " ")
    platforms = summary["platforms"]
    assert isinstance(platforms, dict)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Competitor Census — Fictional Demo</title>
  <style>
    :root {{ --ink:#0b2239; --blue:#163c5c; --gold:#d49a43; --paper:#f4f7f9; --muted:#637485; --line:#d9e2e8; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; color:var(--ink); background:var(--paper); font:15px/1.6 Inter, ui-sans-serif, system-ui, sans-serif; }}
    a {{ color:#0e668c; text-decoration:none; }}
    .hero {{ background:linear-gradient(120deg,#081d31,#173e5d); color:white; padding:72px 7vw 64px; border-bottom:4px solid var(--gold); }}
    .eyebrow {{ color:#e9b45f; text-transform:uppercase; letter-spacing:.18em; font-size:12px; font-weight:800; }}
    h1 {{ max-width:900px; margin:14px 0 12px; font-size:clamp(38px,6vw,72px); line-height:1.02; letter-spacing:-.04em; }}
    .hero p {{ max-width:850px; color:#d7e1e8; font-size:18px; }}
    .scope {{ display:flex; flex-wrap:wrap; gap:9px; margin-top:24px; }}
    .scope span {{ border:1px solid #537088; border-radius:999px; padding:6px 12px; color:#e8eff4; font-size:13px; }}
    main {{ max-width:1180px; margin:auto; padding:42px 24px 80px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-top:-72px; position:relative; }}
    .metric {{ background:white; border:1px solid var(--line); border-radius:16px; padding:20px; box-shadow:0 12px 30px #09233b14; }}
    .metric b {{ display:block; font-size:30px; letter-spacing:-.04em; }}
    .metric span {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; }}
    section {{ background:white; border:1px solid var(--line); border-radius:18px; padding:28px; margin-top:20px; }}
    h2 {{ margin:0 0 6px; font-size:24px; letter-spacing:-.02em; }}
    .sub {{ color:var(--muted); margin:0 0 22px; }}
    .finding {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:18px; }}
    .finding article {{ background:#f7f9fb; border-left:4px solid var(--gold); border-radius:9px; padding:16px; }}
    .finding b {{ display:block; font-size:21px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ color:var(--muted); text-transform:uppercase; letter-spacing:.06em; font-size:11px; text-align:left; }}
    th, td {{ border-bottom:1px solid var(--line); padding:11px 9px; vertical-align:top; }}
    .bar {{ width:130px; height:8px; background:#e8eef2; border-radius:9px; overflow:hidden; }}
    .bar i {{ display:block; height:100%; background:linear-gradient(90deg,var(--gold),#f1c272); }}
    .chips {{ display:flex; flex-wrap:wrap; gap:9px; }}
    .chip {{ background:#edf3f6; border-radius:999px; padding:7px 12px; }}
    .note {{ border:1px solid #ecd09e; background:#fff9ef; padding:14px 16px; border-radius:10px; margin-top:18px; color:#6c4a18; }}
    footer {{ color:var(--muted); text-align:center; padding:28px; }}
    @media (max-width:820px) {{ .metrics {{ grid-template-columns:repeat(2,1fr); margin-top:-40px; }} .finding {{ grid-template-columns:1fr; }} section {{ overflow-x:auto; }} }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="eyebrow">Competitor Census · public-safe offline demo</div>
    <h1>Evidence before conclusions.</h1>
    <p>A fictional example showing how public channel records become a validated evidence bundle, quantitative findings, and source-linked strategy notes.</p>
    <div class="scope"><span>Fictional company</span><span>5 channels audited</span><span>3 channels deep-dived</span><span>No API key</span><span>No live scraping</span></div>
  </header>
  <main>
    <div class="metrics">
      <div class="metric"><b>{summary['census_channels']}</b><span>channels audited</span></div>
      <div class="metric"><b>{summary['content_rows']}</b><span>content records</span></div>
      <div class="metric"><b>{summary['comment_rows']}</b><span>comments + replies</span></div>
      <div class="metric"><b>{int(summary['total_views']):,}</b><span>visible views</span></div>
      <div class="metric"><b>{len(platforms)}</b><span>active platforms</span></div>
    </div>

    <section>
      <h2>What the evidence says</h2>
      <p class="sub">Observations are separated from interpretation. Counts and denominators remain visible.</p>
      <div class="finding">
        <article><b>{str(best['category']).replace('_',' ').title()}</b>Highest mean reach at {int(best['mean_views']):,} views across {best['count']} records.</article>
        <article><b>{str(most_published['category']).replace('_',' ').title()}</b>Largest publishing share at {pct(float(most_published['share']))}, creating a visible supply–performance gap.</article>
        <article><b>{top_topic.title()}</b>Most frequent user topic: {topic_counts.get(summary['top_topic'], 0)}/{summary['user_comments']} non-official comments.</article>
      </div>
      <div class="note"><b>Interpretation:</b> the fictional competitor publishes most often about products, while educational and price content earns stronger reach. Treat this as a testable content hypothesis—not proof of sales impact.</div>
    </section>

    <section>
      <h2>Content supply vs. performance</h2>
      <p class="sub">Mean and median are shown together to reduce distortion from outliers.</p>
      <table><thead><tr><th>Category</th><th>n</th><th>Share</th><th>Mean views</th><th>Median</th><th>Relative reach</th></tr></thead><tbody>{category_rows}</tbody></table>
    </section>

    <section>
      <h2>Voice of customer</h2>
      <p class="sub">Official replies are excluded from demand counts.</p>
      <div class="chips">{topic_chips}</div>
      <p class="note"><b>Visible official response modes:</b> {html.escape(response_text)}. A redirect to DM/support is counted separately from a useful public answer.</p>
    </section>

    <section>
      <h2>Evidence ledger</h2>
      <p class="sub">The report keeps row IDs, dates, metrics, translations, and links together.</p>
      <table><thead><tr><th>ID</th><th>Platform</th><th>Date</th><th>Translated text</th><th>Views</th><th>Evidence</th></tr></thead><tbody>{evidence_rows}</tbody></table>
    </section>

    <section>
      <h2>Scope and limitations</h2>
      <p>This is a deliberately small, fictional dataset used to demonstrate the workflow. Real runs must state platform scope, cutoff time, visible-versus-captured totals, comment selection rules, unavailable records, authentication state, and known personalization effects. Public visibility does not authorize bypassing platform controls or unrestricted republication.</p>
    </section>
  </main>
  <footer>Generated by Competitor Census · {html.escape(str(summary['generated_at']))}</footer>
</body>
</html>"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, default=ROOT / "demo/input/platform_census.csv")
    parser.add_argument("--content", type=Path, default=ROOT / "demo/input/content.csv")
    parser.add_argument("--comments", type=Path, default=ROOT / "demo/input/comments.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "demo/output/report.html")
    parser.add_argument("--json", dest="json_output", type=Path, default=ROOT / "demo/output/summary.json")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    census = load_csv(args.census, CENSUS_FIELDS)
    content = load_csv(args.content, CONTENT_FIELDS)
    comments = load_csv(args.comments, COMMENT_FIELDS)
    summary = analyze(census, content, comments)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(summary), encoding="utf-8")
    args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.quiet:
        print(f"Validated {summary['content_rows']} content rows and {summary['comment_rows']} comment rows.")
        print(f"Report: {args.output}")
        print(f"Summary: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
