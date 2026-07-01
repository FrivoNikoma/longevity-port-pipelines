from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import polars as pl
import yaml  # type: ignore[import-untyped]

DEFAULT_LANE_MANIFEST_SCHEMA_PATH = Path("data/config/lane_manifest_schema.yaml")
DEFAULT_CANDIDATE_LANES_PATH = Path("data/config/candidate_lanes.yaml")

MANIFEST_IDENTITY_COLUMNS = [
    "candidate_set",
    "candidate_id",
    "lane_name",
    "source_species",
    "target_species",
    "gene_symbol",
    "source_uniprot",
    "target_uniprot",
]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing YAML file: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")

    return cast(dict[str, Any], data)


def load_lane_manifest_schema(
    path: Path = DEFAULT_LANE_MANIFEST_SCHEMA_PATH,
) -> dict[str, Any]:
    return load_yaml(path)


def load_candidate_lanes(path: Path = DEFAULT_CANDIDATE_LANES_PATH) -> dict[str, Any]:
    return load_yaml(path)


def required_manifest_fields(schema: dict[str, Any]) -> list[str]:
    fields = schema.get("required_manifest_fields")
    if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
        raise ValueError("lane manifest schema must list required_manifest_fields")

    return fields


def empty_lane_manifest(schema: dict[str, Any] | None = None) -> pl.DataFrame:
    if schema is None:
        schema = load_lane_manifest_schema()

    return pl.DataFrame(schema={field: pl.Utf8 for field in required_manifest_fields(schema)})


def _as_text(row: dict[str, Any], column: str) -> str:
    value = row.get(column)
    if value is None:
        return ""
    return str(value).strip()


def _as_set(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}

    if isinstance(value, str):
        return {item.strip() for item in value.replace(";", ",").split(",") if item.strip()}

    return set()


def _validate_required_columns(
    manifest: pl.DataFrame,
    schema: dict[str, Any],
) -> None:
    required = set(required_manifest_fields(schema))
    missing = required - set(manifest.columns)

    if missing:
        raise ValueError(f"lane manifest is missing required columns: {sorted(missing)}")


def _validate_nonblank_required_fields(
    row: dict[str, Any],
    *,
    required_fields: list[str],
    row_number: int,
) -> None:
    blank_fields = [field for field in required_fields if not _as_text(row, field)]

    if blank_fields:
        raise ValueError(
            f"lane manifest row {row_number} has blank required fields: {sorted(blank_fields)}"
        )


def _validate_unique_manifest_keys(manifest: pl.DataFrame) -> None:
    if manifest.is_empty():
        return

    missing_key_columns = set(MANIFEST_IDENTITY_COLUMNS) - set(manifest.columns)
    if missing_key_columns:
        raise ValueError(
            f"lane manifest is missing identity columns: {sorted(missing_key_columns)}"
        )

    duplicate_rows = manifest.group_by(MANIFEST_IDENTITY_COLUMNS).len().filter(pl.col("len") > 1)

    if duplicate_rows.height:
        raise ValueError("lane manifest contains duplicate manifest identity rows")


def _validate_gate_sequence(row: dict[str, Any], schema: dict[str, Any]) -> None:
    required_gate_status_fields = schema.get("required_gate_status_fields")
    if not isinstance(required_gate_status_fields, dict):
        raise ValueError("lane manifest schema must define required_gate_status_fields")

    required_gates = set(required_gate_status_fields)
    row_gates = _as_set(row.get("gate_sequence"))

    if not required_gates <= row_gates:
        missing = sorted(required_gates - row_gates)
        raise ValueError(f"lane manifest gate_sequence is missing gates: {missing}")


def _validate_row_against_schema(
    row: dict[str, Any],
    *,
    schema: dict[str, Any],
    row_number: int,
) -> None:
    allowed_lifecycle_statuses = _as_set(schema.get("allowed_lane_lifecycle_statuses"))
    allowed_biological_modes = _as_set(schema.get("allowed_biological_modes"))
    allowed_manifest_statuses = _as_set(schema.get("allowed_manifest_statuses"))
    allowed_claim_statuses = _as_set(schema.get("allowed_claim_statuses"))

    lane_lifecycle_status = _as_text(row, "lane_lifecycle_status")
    biological_mode = _as_text(row, "biological_mode")
    manifest_status = _as_text(row, "manifest_status")
    claim_policy = _as_text(row, "claim_policy")
    claim_status = _as_text(row, "claim_status")

    if lane_lifecycle_status not in allowed_lifecycle_statuses:
        raise ValueError(
            f"lane manifest row {row_number} has invalid lane_lifecycle_status: "
            f"{lane_lifecycle_status}"
        )

    if biological_mode not in allowed_biological_modes:
        raise ValueError(
            f"lane manifest row {row_number} has invalid biological_mode: {biological_mode}"
        )

    if manifest_status not in allowed_manifest_statuses:
        raise ValueError(
            f"lane manifest row {row_number} has invalid manifest_status: {manifest_status}"
        )

    if claim_policy != schema["claim_policy"]:
        raise ValueError(f"lane manifest row {row_number} has invalid claim_policy: {claim_policy}")

    if claim_status not in allowed_claim_statuses:
        raise ValueError(f"lane manifest row {row_number} has invalid claim_status: {claim_status}")

    _validate_gate_sequence(row, schema)


def _validate_row_against_lane_registry(
    row: dict[str, Any],
    *,
    candidate_lanes: dict[str, Any],
    row_number: int,
) -> None:
    lane_name = _as_text(row, "lane_name")
    lanes = candidate_lanes.get("lanes")

    if not isinstance(lanes, dict):
        raise ValueError("candidate lane registry must define lanes")

    if lane_name not in lanes:
        raise ValueError(
            f"lane manifest row {row_number} references unknown lane_name: {lane_name}"
        )

    lane = lanes[lane_name]
    if not isinstance(lane, dict):
        raise ValueError(f"candidate lane registry entry is not a mapping: {lane_name}")

    candidate_set = _as_text(row, "candidate_set")
    registry_candidate_set = lane.get("candidate_set")
    if registry_candidate_set is not None and candidate_set != registry_candidate_set:
        raise ValueError(
            f"lane manifest row {row_number} candidate_set does not match "
            f"lane registry for {lane_name}: {candidate_set} != "
            f"{registry_candidate_set}"
        )

    biological_mode = _as_text(row, "biological_mode")
    registry_biological_mode = lane.get("biological_mode")
    if registry_biological_mode is not None and biological_mode != registry_biological_mode:
        raise ValueError(
            f"lane manifest row {row_number} biological_mode does not match "
            f"lane registry for {lane_name}: {biological_mode} != "
            f"{registry_biological_mode}"
        )


def validate_lane_manifest(
    manifest: pl.DataFrame,
    *,
    schema: dict[str, Any] | None = None,
    candidate_lanes: dict[str, Any] | None = None,
) -> None:
    if schema is None:
        schema = load_lane_manifest_schema()

    if candidate_lanes is None:
        candidate_lanes = load_candidate_lanes()

    _validate_required_columns(manifest, schema)
    _validate_unique_manifest_keys(manifest)

    required_fields = required_manifest_fields(schema)

    for row_number, row in enumerate(manifest.iter_rows(named=True), start=1):
        _validate_nonblank_required_fields(
            row,
            required_fields=required_fields,
            row_number=row_number,
        )
        _validate_row_against_schema(row, schema=schema, row_number=row_number)
        _validate_row_against_lane_registry(
            row,
            candidate_lanes=candidate_lanes,
            row_number=row_number,
        )


def _unique_text_values(manifest: pl.DataFrame, column: str) -> list[str]:
    if manifest.is_empty() or column not in manifest.columns:
        return []

    values = set()
    for value in manifest.get_column(column).to_list():
        if value is None:
            continue

        text = str(value).strip()
        if text:
            values.add(text)

    return sorted(values)


def _value_counts(manifest: pl.DataFrame, column: str) -> dict[str, int]:
    if manifest.is_empty() or column not in manifest.columns:
        return {}

    counts = manifest.group_by(column).len().sort(column)

    result: dict[str, int] = {}
    for row in counts.iter_rows(named=True):
        value = row[column]
        if value is None:
            continue

        text = str(value).strip()
        if text:
            result[text] = int(row["len"])

    return result


def _count_rows_with_value(
    manifest: pl.DataFrame,
    *,
    column: str,
    value: str,
) -> int:
    if manifest.is_empty() or column not in manifest.columns:
        return 0

    return manifest.filter(pl.col(column) == value).height


def summarize_lane_manifest_status(manifest: pl.DataFrame) -> dict[str, Any]:
    return {
        "row_count": manifest.height,
        "lane_names": _unique_text_values(manifest, "lane_name"),
        "candidate_sets": _unique_text_values(manifest, "candidate_set"),
        "manifest_status_counts": _value_counts(manifest, "manifest_status"),
        "claim_status_counts": _value_counts(manifest, "claim_status"),
        "lane_name_counts": _value_counts(manifest, "lane_name"),
        "candidate_set_counts": _value_counts(manifest, "candidate_set"),
        "planning_only_rows": _count_rows_with_value(
            manifest,
            column="manifest_status",
            value="planning_only",
        ),
        "validation_required_rows": _count_rows_with_value(
            manifest,
            column="manifest_status",
            value="validation_required",
        ),
    }


def _render_count_block(title: str, counts: dict[str, int]) -> list[str]:
    lines = [f"## {title}", ""]

    if not counts:
        lines.extend(["No rows.", ""])
        return lines

    lines.extend(["| Value | Count |", "| --- | ---: |"])
    for value, count in sorted(counts.items()):
        lines.append(f"| {value} | {count} |")

    lines.append("")
    return lines


def render_lane_manifest_status_summary_markdown(
    summary: dict[str, Any],
) -> str:
    lines = [
        "# Lane manifest status summary",
        "",
        "This is a planning-only technical summary.",
        "",
        "It does not make biological validation claims.",
        "",
        "## Overview",
        "",
        f"- Row count: {summary['row_count']}",
        f"- Lane names: {', '.join(summary['lane_names']) or 'none'}",
        f"- Candidate sets: {', '.join(summary['candidate_sets']) or 'none'}",
        f"- Planning-only rows: {summary['planning_only_rows']}",
        f"- Validation-required rows: {summary['validation_required_rows']}",
        "",
    ]

    lines.extend(
        _render_count_block(
            "Manifest status counts",
            summary["manifest_status_counts"],
        )
    )
    lines.extend(
        _render_count_block(
            "Claim status counts",
            summary["claim_status_counts"],
        )
    )
    lines.extend(
        _render_count_block(
            "Lane name counts",
            summary["lane_name_counts"],
        )
    )
    lines.extend(
        _render_count_block(
            "Candidate set counts",
            summary["candidate_set_counts"],
        )
    )

    lines.extend(
        [
            "## Guardrails",
            "",
            "- No live Biohub calls.",
            "- No live Boltz calls.",
            "- No embedding generation.",
            "- No cofolding input generation.",
            "- No biological validation claims.",
            "",
        ]
    )

    return "\n".join(lines)


def write_lane_manifest_status_summary(
    manifest: pl.DataFrame,
    output_path: Path,
) -> dict[str, Any]:
    summary = summarize_lane_manifest_status(manifest)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_lane_manifest_status_summary_markdown(summary),
        encoding="utf-8",
    )
    return summary


def load_lane_manifest_csv(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing lane manifest CSV: {path}")

    return pl.read_csv(path)


def build_lane_manifest_status_summary_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a generic lane manifest CSV and write a planning-only "
            "Markdown status summary."
        ),
    )
    parser.add_argument(
        "manifest_path",
        help="Path to a lane manifest CSV.",
    )
    parser.add_argument(
        "--output-path",
        required=True,
        help="Path where the Markdown summary should be written.",
    )
    parser.add_argument(
        "--schema-path",
        default=str(DEFAULT_LANE_MANIFEST_SCHEMA_PATH),
        help="Path to the generic lane manifest schema YAML.",
    )
    parser.add_argument(
        "--candidate-lanes-path",
        default=str(DEFAULT_CANDIDATE_LANES_PATH),
        help="Path to the candidate lane registry YAML.",
    )
    return parser


def run_lane_manifest_status_summary_cli(
    argv: Sequence[str] | None = None,
) -> dict[str, Any]:
    parser = build_lane_manifest_status_summary_parser()
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest_path)
    output_path = Path(args.output_path)
    schema_path = Path(args.schema_path)
    candidate_lanes_path = Path(args.candidate_lanes_path)

    manifest = load_lane_manifest_csv(manifest_path)
    schema = load_lane_manifest_schema(schema_path)
    candidate_lanes = load_candidate_lanes(candidate_lanes_path)

    validate_lane_manifest(
        manifest,
        schema=schema,
        candidate_lanes=candidate_lanes,
    )
    summary = write_lane_manifest_status_summary(manifest, output_path)

    print(f"Wrote lane manifest status summary: {output_path}")
    return summary


def main(argv: Sequence[str] | None = None) -> None:
    run_lane_manifest_status_summary_cli(argv)


if __name__ == "__main__":
    main()
