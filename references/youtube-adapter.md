# YouTube adapter

Use `scripts/collect_youtube.py` for a real, public-metadata vertical slice. It invokes `yt-dlp`, does not download media, and writes the standard Competitor Census evidence bundle.

## Install the collector dependency

Use a current official release:

```bash
python3 -m pip install -U "yt-dlp[default]"
```

If an extractor breaks, update yt-dlp before debugging the adapter.

## Trial run

```bash
python3 scripts/collect_youtube.py \
  --company "Example Company" \
  --channel "https://www.youtube.com/@ExampleCompany" \
  --tabs videos \
  --max-items-per-tab 10
```

## Best-effort selected-tab census

```bash
python3 scripts/collect_youtube.py \
  --company "Example Company" \
  --channel "https://www.youtube.com/@ExampleCompany" \
  --tabs videos,shorts,streams \
  --max-items-per-tab 0
```

Rich mode opens each public video page to obtain publication date, description, views, likes, and visible comment count where available. A large history can therefore take time. The adapter sleeps between metadata requests by default; increase `--sleep-requests` when appropriate.

## Outputs

The default directory is `runs/<company-slug>/`:

- `platform_census.csv`: one unverified YouTube account row for human identity review;
- `content.csv`: normalized point-in-time video metadata;
- `comments.csv`: header only in v0.2;
- `run_manifest.json`: scope, cutoff, selected tabs, tool version, counts, field limitations, and warnings;
- `summary.json`: deterministic descriptive statistics;
- `report.html`: baseline evidence-linked report.

## Interpretation boundary

The collector leaves `text_translation` blank and `content_type` as `unclassified`. After collection, use the Agent workflow to translate and derive categories from the actual corpus. Rebuild the report only after validating row counts and account identity.

Do not describe a limited run as a census. Even with `--max-items-per-tab 0`, use “best-effort selected-tab census at the cutoff” because deleted, private, members-only, personalized, age-restricted, and region-restricted content may be unavailable.
