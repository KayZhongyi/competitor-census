# Incremental updates

Use a new run directory for every capture. Never overwrite the previous evidence bundle before validation.

## Date-bounded YouTube capture

```bash
python3 scripts/collect_youtube.py \
  --company "Target Company" \
  --channel "https://www.youtube.com/@TargetHandle" \
  --tabs videos,shorts,streams \
  --since 2026-07-01 \
  --output runs/target-2026-07
```

The adapter passes the date boundary to the collector and records it in `run_manifest.json`.

## Stable-ID merge

```bash
python3 scripts/merge_incremental.py \
  --base runs/target-baseline/content.csv \
  --incoming runs/target-2026-07/content.csv \
  --output runs/target-current/content.csv
```

For comments, add `--id-field comment_id`. The tool requires identical CSV schemas, ignores `collected_at` only when detecting changes, keeps the incoming row for a known ID, retains base rows absent from the incoming scope, and writes a JSON report containing new, updated, unchanged, and absent counts. Each updated record also lists the changed fields and whether the difference is `content`, `engagement`, or `metadata`, so a notification layer can suppress harmless metric drift and route material changes for review.

Absence from a bounded incoming run is not proof of deletion. Verify the source separately before marking a record removed or unavailable.

Read [monitoring-playbook.md](monitoring-playbook.md) before turning a repeat run into an alert or group notification.
