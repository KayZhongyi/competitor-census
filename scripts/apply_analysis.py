#!/usr/bin/env python3
"""Validate Agent analysis, merge it without changing raw evidence, and render a report."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from prepare_analysis import RESULT_FIELDS, file_sha256


ROOT = Path(__file__).resolve().parents[1]
CONFIDENCE_VALUES = {"high", "medium", "low"}
CATEGORY_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        return fields, list(reader)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def duplicate_values(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_taxonomy(
    taxonomy: object, source_ids: set[str], result_by_id: dict[str, dict[str, str]]
) -> tuple[set[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(taxonomy, dict):
        return set(), ["taxonomy.json must contain a JSON object"], warnings
    if taxonomy.get("schema_version") != "0.3":
        errors.append("taxonomy.json schema_version must be 0.3")
    if not nonempty_string(taxonomy.get("target_language")):
        errors.append("taxonomy.json target_language is required")
    if not nonempty_string(taxonomy.get("derivation_notes")):
        errors.append("taxonomy.json derivation_notes must explain how categories emerged")

    categories = taxonomy.get("categories")
    if not isinstance(categories, list) or not categories:
        return set(), errors + ["taxonomy.json must define at least one category"], warnings

    category_ids: list[str] = []
    representatives: dict[str, list[str]] = {}
    for index, category in enumerate(categories, start=1):
        prefix = f"taxonomy category {index}"
        if not isinstance(category, dict):
            errors.append(f"{prefix} must be an object")
            continue
        category_id = str(category.get("id", "")).strip()
        category_ids.append(category_id)
        if not CATEGORY_ID_PATTERN.fullmatch(category_id):
            errors.append(f"{prefix} id must use lowercase letters, numbers, hyphens, or underscores")
        for field in ("label", "definition"):
            if not nonempty_string(category.get(field)):
                errors.append(f"{prefix} {field} is required")
        for field in ("inclusion_criteria", "exclusion_criteria", "representative_record_ids"):
            value = category.get(field)
            if not isinstance(value, list) or not value or not all(nonempty_string(item) for item in value):
                errors.append(f"{prefix} {field} must be a non-empty string list")
        representative_ids = category.get("representative_record_ids", [])
        if isinstance(representative_ids, list):
            clean_ids = [str(value).strip() for value in representative_ids]
            representatives[category_id] = clean_ids
            unknown = sorted(set(clean_ids) - source_ids)
            if unknown:
                errors.append(f"{prefix} has unknown representative IDs: {', '.join(unknown)}")

    duplicates = duplicate_values(category_ids)
    if duplicates:
        errors.append(f"taxonomy has duplicate category IDs: {', '.join(duplicates)}")
    category_set = set(category_ids)

    used = Counter(row.get("content_type", "").strip() for row in result_by_id.values())
    unused = sorted(category_set - set(used))
    if unused:
        warnings.append(f"taxonomy categories have no assigned records: {', '.join(unused)}")
    for category_id, ids in representatives.items():
        mismatched = [
            record_id
            for record_id in ids
            if record_id in result_by_id
            and result_by_id[record_id].get("content_type", "").strip() != category_id
        ]
        if mismatched:
            errors.append(
                f"representative IDs assigned to a different category for {category_id}: "
                + ", ".join(mismatched)
            )
    return category_set, errors, warnings


def validate(
    bundle: Path,
) -> tuple[list[str], list[dict[str, str]], list[dict[str, str]], dict[str, object], dict[str, object]]:
    content_path = bundle / "content.csv"
    analysis_dir = bundle / "analysis"
    source_fields, source_rows = load_csv(content_path)
    result_fields, result_rows = load_csv(analysis_dir / "analysis_results.csv")
    manifest = load_json(analysis_dir / "analysis_manifest.json")
    taxonomy = load_json(analysis_dir / "taxonomy.json")
    if not isinstance(manifest, dict):
        raise ValueError("analysis_manifest.json must contain a JSON object")

    errors: list[str] = []
    warnings: list[str] = []
    source_ids = [row.get("record_id", "").strip() for row in source_rows]
    result_ids = [row.get("record_id", "").strip() for row in result_rows]
    if duplicates := duplicate_values(source_ids):
        errors.append(f"content.csv has duplicate record IDs: {', '.join(duplicates)}")
    if duplicates := duplicate_values(result_ids):
        errors.append(f"analysis_results.csv has duplicate record IDs: {', '.join(duplicates)}")

    if result_fields != RESULT_FIELDS:
        errors.append("analysis_results.csv columns or order changed; regenerate the analysis packet")
    source_id_set = set(source_ids)
    result_id_set = set(result_ids)
    if missing := sorted(source_id_set - result_id_set):
        errors.append(f"analysis_results.csv is missing record IDs: {', '.join(missing)}")
    if unknown := sorted(result_id_set - source_id_set):
        errors.append(f"analysis_results.csv has unknown record IDs: {', '.join(unknown)}")
    if len(result_rows) != len(source_rows):
        errors.append(
            f"analysis row count {len(result_rows)} does not match source row count {len(source_rows)}"
        )

    current_hash = file_sha256(content_path)
    if manifest.get("schema_version") != "0.3":
        errors.append("analysis_manifest.json schema_version must be 0.3")
    if manifest.get("source_sha256") != current_hash:
        errors.append("content.csv changed after the analysis packet was prepared; prepare a new packet")
    if manifest.get("source_rows") != len(source_rows):
        errors.append("analysis manifest row count does not match content.csv")

    result_by_id = {row.get("record_id", "").strip(): row for row in result_rows}
    category_ids, taxonomy_errors, taxonomy_warnings = validate_taxonomy(
        taxonomy, source_id_set, result_by_id
    )
    errors.extend(taxonomy_errors)
    warnings.extend(taxonomy_warnings)
    if isinstance(taxonomy, dict) and (
        taxonomy.get("target_language") != manifest.get("target_language")
    ):
        errors.append("taxonomy target_language does not match the prepared analysis manifest")

    for row_number, row in enumerate(result_rows, start=2):
        record_id = row.get("record_id", "").strip() or f"row {row_number}"
        if not row.get("text_translation", "").strip():
            errors.append(f"{record_id}: text_translation is required")
        category = row.get("content_type", "").strip()
        if not category or category == "unclassified":
            errors.append(f"{record_id}: content_type must be classified")
        elif category not in category_ids:
            errors.append(f"{record_id}: unknown content_type {category}")
        confidence = row.get("classification_confidence", "").strip().lower()
        if confidence not in CONFIDENCE_VALUES:
            errors.append(f"{record_id}: confidence must be high, medium, or low")
        if confidence == "low" and not row.get("classification_notes", "").strip():
            errors.append(f"{record_id}: low confidence requires classification_notes")

    report = {
        "schema_version": "0.3",
        "validated_at": utc_now(),
        "status": "failed" if errors else "passed",
        "source_file": "content.csv",
        "source_sha256": current_hash,
        "source_rows": len(source_rows),
        "analysis_rows": len(result_rows),
        "translation_coverage": (
            sum(bool(row.get("text_translation", "").strip()) for row in result_rows) / len(source_rows)
            if source_rows
            else 0
        ),
        "classification_coverage": (
            sum(
                bool(row.get("content_type", "").strip())
                and row.get("content_type", "").strip() != "unclassified"
                for row in result_rows
            )
            / len(source_rows)
            if source_rows
            else 0
        ),
        "categories": dict(sorted(Counter(row.get("content_type", "").strip() for row in result_rows).items())),
        "errors": errors,
        "warnings": warnings,
    }
    if errors:
        raise AnalysisValidationError(report)
    return source_fields, source_rows, result_rows, report, taxonomy


class AnalysisValidationError(ValueError):
    def __init__(self, report: dict[str, object]):
        self.report = report
        super().__init__("Agent analysis did not pass validation")


def write_json_atomic(path: Path, value: object) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def write_merged(
    path: Path,
    source_fields: list[str],
    source_rows: list[dict[str, str]],
    result_rows: list[dict[str, str]],
) -> None:
    result_by_id = {row["record_id"].strip(): row for row in result_rows}
    output_fields = [*source_fields]
    for field in ("classification_confidence", "classification_notes"):
        if field not in output_fields:
            output_fields.append(field)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        for source in source_rows:
            result = result_by_id[source["record_id"].strip()]
            merged = dict(source)
            for field in RESULT_FIELDS[1:]:
                merged[field] = result[field].strip()
            writer.writerow(merged)
    os.replace(temp, path)


def dataset_label(bundle: Path) -> str:
    manifest_path = bundle / "run_manifest.json"
    if manifest_path.exists():
        manifest = load_json(manifest_path)
        if isinstance(manifest, dict):
            target = manifest.get("target")
            if isinstance(target, dict) and nonempty_string(target.get("company")):
                return f"{target['company']} analyzed census"
    return f"{bundle.name} analyzed census"


def render_report(bundle: Path, analyzed_content: Path) -> None:
    census = bundle / "platform_census.csv"
    comments = bundle / "comments.csv"
    if not census.exists() or not comments.exists():
        return
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_demo.py"),
            "--census",
            str(census),
            "--content",
            str(analyzed_content),
            "--comments",
            str(comments),
            "--output",
            str(bundle / "analysis_report.html"),
            "--json",
            str(bundle / "analysis_summary.json"),
            "--dataset-label",
            dataset_label(bundle),
            "--dataset-kind",
            "live",
            "--quiet",
        ],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True, help="Census bundle with analysis files")
    parser.add_argument("--no-report", action="store_true", help="Validate and merge without HTML output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = args.bundle.resolve()
    validation_path = bundle / "analysis" / "validation_report.json"
    try:
        source_fields, source_rows, result_rows, report, _taxonomy = validate(bundle)
    except AnalysisValidationError as exc:
        write_json_atomic(validation_path, exc.report)
        for error in exc.report["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation report: {validation_path}", file=sys.stderr)
        return 1
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    analyzed_content = bundle / "analyzed_content.csv"
    write_merged(analyzed_content, source_fields, source_rows, result_rows)
    write_json_atomic(validation_path, report)
    if not args.no_report:
        render_report(bundle, analyzed_content)

    print(f"Validated {len(source_rows)} analysis rows across {len(report['categories'])} categories.")
    print(f"Analyzed dataset: {analyzed_content}")
    print(f"Validation report: {validation_path}")
    if not args.no_report and (bundle / "analysis_report.html").exists():
        print(f"Analysis report: {bundle / 'analysis_report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
