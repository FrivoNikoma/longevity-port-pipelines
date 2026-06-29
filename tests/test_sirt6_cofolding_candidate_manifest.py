from __future__ import annotations

from pathlib import Path

import polars as pl

MANIFEST = Path("data/input/sirt6_cofolding_candidate_manifest.csv")

EXPECTED_CANDIDATE_IDS = {
    "1nfi__A1_Q04206--1nfi__F1_P25963",
    "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
    "7s68__D1_P09874--7s68__C1_P09874",
    "8f86__K1_Q8N6T7--8f86__D1_P02281",
    "8bhv__N1_P12956--8bhv__I1_Q9H9Q4",
    "8bhv__P1_P13010--8bhv__J1_Q9H9Q4",
}

REQUIRED_PREFLIGHT_COLUMNS = {
    "candidate_id",
    "chain",
    "source_uniprot",
}


def test_sirt6_cofolding_candidate_manifest_exists() -> None:
    assert MANIFEST.exists()


def test_sirt6_cofolding_candidate_manifest_has_required_columns() -> None:
    manifest = pl.read_csv(MANIFEST)

    assert REQUIRED_PREFLIGHT_COLUMNS.issubset(set(manifest.columns))
    assert "priority" in manifest.columns
    assert "baseline_status" in manifest.columns
    assert "biological_role" in manifest.columns
    assert "notes" in manifest.columns


def test_sirt6_cofolding_candidate_manifest_contains_expected_shortlist() -> None:
    manifest = pl.read_csv(MANIFEST)

    assert set(manifest["candidate_id"].to_list()) == EXPECTED_CANDIDATE_IDS


def test_sirt6_cofolding_candidate_manifest_candidate_ids_are_unique() -> None:
    manifest = pl.read_csv(MANIFEST)

    assert manifest["candidate_id"].n_unique() == manifest.height


def test_sirt6_cofolding_candidate_manifest_core_fields_are_populated() -> None:
    manifest = pl.read_csv(MANIFEST)

    for column in ["candidate_id", "chain", "source_uniprot", "priority"]:
        assert manifest.filter(
            pl.col(column).is_null() | (pl.col(column).cast(pl.Utf8).str.len_chars() == 0)
        ).is_empty()
