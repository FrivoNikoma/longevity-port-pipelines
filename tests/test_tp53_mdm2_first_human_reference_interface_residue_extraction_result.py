"""Tests for the first TP53/MDM2 human-reference interface extraction result."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_human_reference_interface_residue_extraction_result as result,
)

SUMMARY_TABLE = Path(
    "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv"
)
RESIDUE_TABLE = Path("data/input/tp53_mdm2_first_human_reference_interface_residue_records.csv")
SCHEMA_PATH = Path(
    "data/config/tp53_mdm2_first_human_reference_interface_residue_extraction_result_schema.yaml"
)


def _write_rows(
    path: Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_load_and_validate_interface_extraction_result() -> None:
    summary, rows = result.load_and_validate_human_reference_interface_residue_extraction_result()

    assert summary["structure_id"] == "1YCR"
    assert (
        summary["pdb_sha256"] == "7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493"
    )
    assert summary["mdm2_interface_residue_count"] == "47"
    assert summary["mdm2_non_interface_residue_count"] == "38"
    assert summary["tp53_interface_residue_count"] == "13"
    assert summary["tp53_non_interface_residue_count"] == "0"
    assert summary["tp53_within_chain_shuffle_degenerate"] == "true"
    assert summary["required_shuffled_control_scope"] == (
        "mdm2_chain_A_only_until_non_degenerate_tp53_background_is_defined"
    )
    assert summary["next_step"] == "add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result"
    assert len(rows) == 60


def test_committed_interface_residue_lists_are_exact() -> None:
    summary, rows = result.load_and_validate_human_reference_interface_residue_extraction_result()

    mdm2_rows = [row for row in rows if row["protein_role"] == "mdm2"]
    tp53_rows = [row for row in rows if row["protein_role"] == "tp53"]

    assert [int(row["chain_local_index"]) for row in mdm2_rows] == [
        0,
        1,
        2,
        3,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        57,
        61,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        78,
        79,
        82,
        84,
    ]
    assert [row["pdb_residue_label"] for row in mdm2_rows] == [
        "GLU25",
        "THR26",
        "LEU27",
        "VAL28",
        "TYR48",
        "THR49",
        "MET50",
        "LYS51",
        "GLU52",
        "VAL53",
        "LEU54",
        "PHE55",
        "TYR56",
        "LEU57",
        "GLY58",
        "GLN59",
        "TYR60",
        "ILE61",
        "MET62",
        "THR63",
        "LEU66",
        "TYR67",
        "ASP68",
        "GLU69",
        "LYS70",
        "GLN71",
        "GLN72",
        "HIS73",
        "ILE74",
        "VAL75",
        "LEU82",
        "PHE86",
        "PHE91",
        "SER92",
        "VAL93",
        "LYS94",
        "GLU95",
        "HIS96",
        "ARG97",
        "LYS98",
        "ILE99",
        "TYR100",
        "THR101",
        "ILE103",
        "TYR104",
        "LEU107",
        "VAL109",
    ]
    assert [int(row["chain_local_index"]) for row in tp53_rows] == [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    assert [row["pdb_residue_label"] for row in tp53_rows] == [
        "GLU17",
        "THR18",
        "PHE19",
        "SER20",
        "ASP21",
        "LEU22",
        "TRP23",
        "LYS24",
        "LEU25",
        "LEU26",
        "PRO27",
        "GLU28",
        "ASN29",
    ]

    assert summary["mdm2_interface_indices"] == "|".join(
        row["chain_local_index"] for row in mdm2_rows
    )
    assert summary["tp53_interface_indices"] == "|".join(
        row["chain_local_index"] for row in tp53_rows
    )


def test_schema_matches_committed_tables() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    summary_rows = result.read_csv_rows(SUMMARY_TABLE)
    residue_rows = result.read_csv_rows(RESIDUE_TABLE)

    assert schema["name"] == "tp53_mdm2_first_human_reference_interface_residue_extraction_result"
    assert schema["version"] == 1
    assert list(summary_rows[0]) == schema["summary_required_fields"]
    assert list(residue_rows[0]) == schema["residue_required_fields"]
    assert schema["result"]["residue_record_count"] == 60
    assert schema["result"]["mdm2"]["interface_residue_count"] == 47
    assert schema["result"]["tp53"]["interface_residue_count"] == 13
    assert schema["result"]["tp53"]["within_chain_shuffle_degenerate"] is True


def test_summary_validator_rejects_tp53_shuffle_claim() -> None:
    row = result.require_single_row(SUMMARY_TABLE)
    row["tp53_within_chain_shuffle_possible"] = "true"

    with pytest.raises(ValueError, match="value mismatch"):
        result.validate_summary_row(row)


def test_summary_validator_rejects_interface_score_claim() -> None:
    row = result.require_single_row(SUMMARY_TABLE)
    row["interface_score_computed"] = "true"

    with pytest.raises(ValueError, match="value mismatch"):
        result.validate_summary_row(row)


def test_residue_validator_rejects_changed_record(tmp_path: Path) -> None:
    rows = result.read_csv_rows(RESIDUE_TABLE)
    rows[0]["pdb_residue_label"] = "ALA25"
    path = tmp_path / "changed_residues.csv"
    _write_rows(path, rows, list(rows[0]))

    with pytest.raises(ValueError, match="row 1 mismatch"):
        result.validate_residue_rows(result.read_csv_rows(path))


def test_loader_rejects_cross_table_record_count(
    tmp_path: Path,
) -> None:
    summary = result.require_single_row(SUMMARY_TABLE)
    summary["residue_record_count"] = "59"
    summary_path = tmp_path / "changed_summary.csv"
    _write_rows(summary_path, [summary], list(summary))

    with pytest.raises(ValueError, match="value mismatch"):
        result.load_and_validate_human_reference_interface_residue_extraction_result(
            summary_path=summary_path,
            residue_path=RESIDUE_TABLE,
        )
