from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.negatome_inputs import (
    build_negative_control_coverage,
    build_negatome_input_validation,
    empty_validation,
    filter_nonempty_negative_control_pairs,
    find_duplicate_negative_control_rows,
    validate_schema,
)


def expected_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["c1", "c1", "c2"],
            "chain": ["receptor", "ligand", "receptor"],
            "target_species": ["mouse", "mouse", "mouse"],
        }
    )


def pair_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["c1", "c1", "c2", "c2"],
            "chain": ["receptor", "receptor", "receptor", "receptor"],
            "target_species": ["mouse", "mouse", "mouse", "mouse"],
            "source_uniprot": ["P1", "P1", "P2", "P2"],
            "negative_partner_uniprot": ["N1", "N2", "N3", "N4"],
            "negative_partner_source": [
                "manual_curation",
                "literature_curation",
                "manual_curation",
                "manual_curation",
            ],
            "negative_partner_sequence": ["AAAA", "BBBB", "", None],
            "control_type": [
                "curated_non_interactor",
                "literature_supported_non_interactor",
                "curated_non_interactor",
                "curated_non_interactor",
            ],
        }
    )


def test_validate_schema_accepts_required_columns() -> None:
    validate_schema(pair_rows())


def test_validate_schema_rejects_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_schema(pl.DataFrame({"complex_id": ["c1"]}))


def test_empty_validation_marks_all_expected_rows_missing_input_file() -> None:
    validation = empty_validation(expected_rows())

    assert validation.height == 3
    assert set(validation["input_status"].to_list()) == {"missing_input_file"}
    assert set(validation["has_negative_control_input"].to_list()) == {False}


def test_filter_nonempty_negative_control_pairs_requires_sequence() -> None:
    nonempty = filter_nonempty_negative_control_pairs(pair_rows())

    assert nonempty.height == 2
    assert nonempty["negative_partner_uniprot"].to_list() == ["N1", "N2"]


def test_build_negative_control_coverage_counts_only_nonempty_pairs() -> None:
    coverage = build_negative_control_coverage(pair_rows())

    row = coverage.filter(
        (pl.col("complex_id") == "c1")
        & (pl.col("chain") == "receptor")
        & (pl.col("target_species") == "mouse")
    ).row(0, named=True)

    assert row["n_negative_control_pairs"] == 2
    assert row["negative_partner_uniprots"] == "N1;N2"
    assert row["control_types"] == "curated_non_interactor;literature_supported_non_interactor"


def test_build_negatome_input_validation_marks_present_and_missing_rows() -> None:
    validation = build_negatome_input_validation(expected_rows(), pair_rows())

    c1_receptor = validation.filter(
        (pl.col("complex_id") == "c1") & (pl.col("chain") == "receptor")
    ).row(0, named=True)
    c1_ligand = validation.filter(
        (pl.col("complex_id") == "c1") & (pl.col("chain") == "ligand")
    ).row(0, named=True)

    assert c1_receptor["n_negative_control_pairs"] == 2
    assert c1_receptor["has_negative_control_input"] is True
    assert c1_receptor["input_status"] == "has_negative_control_input"

    assert c1_ligand["n_negative_control_pairs"] == 0
    assert c1_ligand["has_negative_control_input"] is False
    assert c1_ligand["input_status"] == "missing_negative_control_input"


def test_build_negatome_input_validation_handles_missing_pair_file() -> None:
    validation = build_negatome_input_validation(expected_rows(), None)

    assert set(validation["input_status"].to_list()) == {"missing_input_file"}


def test_find_duplicate_negative_control_rows() -> None:
    pairs = pl.concat([pair_rows(), pair_rows().head(1)], how="vertical")
    duplicates = find_duplicate_negative_control_rows(pairs)

    assert duplicates.height == 1
    assert duplicates.row(0, named=True)["negative_partner_uniprot"] == "N1"
    assert duplicates.row(0, named=True)["len"] == 2
