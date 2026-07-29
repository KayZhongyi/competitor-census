#!/usr/bin/env python3
"""Merge a new CSV capture into an existing evidence table by stable ID."""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        return fields, list(reader)


def validate_rows(path: Path, fields: list[str], rows: list[dict[str, str]], id_field: str) -> None:
    if id_field not in fields:
        raise ValueError(f"{path}: missing ID column {id_field}")
    ids = [row.get(id_field, "").strip() for row in rows]
    if any(not value for value in ids):
        raise ValueError(f"{path}: blank {id_field}")
    duplicates = sorted(value for value, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"{path}: duplicate {id_field}: {', '.join(duplicates)}")


def comparable(row: dict[str, str], fields: list[str], ignored: set[str]) -> tuple[str, ...]:
    return tuple(row.get(field, "") for field in fields if field not in ignored)


def merge(
    base_path: Path,
    incoming_path: Path,
    id_field: str,
    ignored_fields: set[str],
) -> tuple[list[str], list[dict[str, str]], dict[str, object]]:
    base_fields, base_rows = load_csv(base_path)
    incoming_fields, incoming_rows = load_csv(incoming_path)
    if base_fields != incoming_fields:
        raise ValueError("Base and incoming CSV columns or order do not match")
    validate_rows(base_path, base_fields, base_rows, id_field)
    validate_rows(incoming_path, incoming_fields, incoming_rows, id_field)
    unknown_ignored = sorted(ignored_fields - set(base_fields))
    if unknown_ignored:
        raise ValueError(f"Unknown ignored fields: {', '.join(unknown_ignored)}")

    base_by_id = {row[id_field].strip(): row for row in base_rows}
    incoming_by_id = {row[id_field].strip(): row for row in incoming_rows}
    new_ids: list[str] = []
    updated_ids: list[str] = []
    unchanged_ids: list[str] = []
    merged_by_id = dict(base_by_id)

    for record_id, incoming in incoming_by_id.items():
        previous = base_by_id.get(record_id)
        if previous is None:
            new_ids.append(record_id)
        elif comparable(previous, base_fields, ignored_fields) != comparable(
            incoming, base_fields, ignored_fields
        ):
            updated_ids.append(record_id)
        else:
            unchanged_ids.append(record_id)
        merged_by_id[record_id] = incoming

    merged_rows = [
        merged_by_id[row[id_field].strip()]
        for row in base_rows
        if row[id_field].strip() in merged_by_id
    ]
    merged_rows.extend(
        incoming_by_id[record_id]
        for record_id in incoming_by_id
        if record_id not in base_by_id
    )
    absent_ids = [record_id for record_id in base_by_id if record_id not in incoming_by_id]
    report = {
        "schema_version": "0.4",
        "merged_at": utc_now(),
        "id_field": id_field,
        "ignored_for_change_detection": sorted(ignored_fields),
        "base_rows": len(base_rows),
        "incoming_rows": len(incoming_rows),
        "merged_rows": len(merged_rows),
        "new": len(new_ids),
        "updated": len(updated_ids),
        "unchanged": len(unchanged_ids),
        "absent_from_incoming": len(absent_ids),
        "new_ids": new_ids,
        "updated_ids": updated_ids,
        "absent_from_incoming_ids": absent_ids,
        "note": (
            "Absent records are retained. Absence may reflect the incoming scope and is not treated "
            "as deletion without separate verification."
        ),
    }
    return base_fields, merged_rows, report


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="Existing evidence CSV")
    parser.add_argument("--incoming", type=Path, required=True, help="New capture CSV")
    parser.add_argument("--output", type=Path, required=True, help="Merged CSV; must differ from inputs")
    parser.add_argument("--report", type=Path, help="JSON merge report")
    parser.add_argument("--id-field", default="record_id", help="Stable ID column")
    parser.add_argument(
        "--ignore-fields",
        default="collected_at",
        help="Comma-separated fields ignored only for change detection",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base = args.base.resolve()
    incoming = args.incoming.resolve()
    output = args.output.resolve()
    if output in {base, incoming}:
        raise SystemExit("--output must not overwrite either source CSV")
    ignored = {field.strip() for field in args.ignore_fields.split(",") if field.strip()}
    try:
        fields, rows, report = merge(base, incoming, args.id_field.strip(), ignored)
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
    report_path = (
        args.report.resolve()
        if args.report
        else output.with_name(f"{output.stem}_merge_report.json")
    )
    write_csv_atomic(output, fields, rows)
    write_json_atomic(report_path, report)
    print(
        f"Merged {report['merged_rows']} rows: {report['new']} new, "
        f"{report['updated']} updated, {report['unchanged']} unchanged."
    )
    print(f"Merged CSV: {output}")
    print(f"Merge report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
