from __future__ import annotations

import polars as pl

from longevity_port_pipelines.stages.curated_negatome_controls import (
    build_curated_negatome_control_preflight,
    empty_curated_negatome_control_preflight,
    merge_curated_negatome_control_pairs,
)

COMPLEX_ID = "4xhu__A1_P09874--4xhu__B1_Q9UNS1"


def curated_candidates() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [COMPLEX_ID],
            "chain": ["receptor"],
            "target_species": ["brandts_bat"],
            "source_uniprot": ["P09874"],
            "source_species_taxid": [9606],
            "target_species_taxid": [109478],
            "target_accession": ["EPQ16369.1"],
            "target_accession_db": ["NCBI Protein"],
            "target_sequence": ["AAAA"],
            "target_sequence_length": [4],
            "curation_status": ["primary_candidate"],
            "evidence_source": ["manual"],
            "curation_note": ["primary"],
        }
    )


def unsupported_candidates() -> pl.DataFrame:
    return curated_candidates().with_columns(
        [
            pl.lit("unknown__A1_Q99999--unknown__B1_Q9UNS1").alias("complex_id"),
            pl.lit("Q99999").alias("source_uniprot"),
        ]
    )


def negative_pair(target_species: str) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [COMPLEX_ID],
            "chain": ["receptor"],
            "target_species": [target_species],
            "source_uniprot": ["P09874"],
            "negative_partner_uniprot": ["O60907"],
            "negative_partner_source": ["negatome_database"],
            "negative_partner_sequence": ["MTELAGASSS"],
            "control_type": ["curated_negative"],
        }
    )


def test_empty_curated_negatome_control_preflight_has_expected_columns() -> None:
    preflight = empty_curated_negatome_control_preflight()

    assert preflight.is_empty()
    assert "export_status" in preflight.columns
    assert "existing_negative_control_row" in preflight.columns


def test_preflight_marks_missing_and_unsupported_rows() -> None:
    preflight = build_curated_negatome_control_preflight(
        curated_candidates=pl.concat([curated_candidates(), unsupported_candidates()]),
        existing_pairs=negative_pair("mouse"),
    )

    ready = preflight.filter(pl.col("export_status") == "missing_export_ready")
    unsupported = preflight.filter(pl.col("export_status") == "missing_curated_negative_partner")

    assert ready.height == 1
    assert ready.row(0, named=True)["negative_partner_uniprot"] == "O60907"

    assert unsupported.height == 1
    assert unsupported.row(0, named=True)["source_uniprot"] == "Q99999"


def test_preflight_marks_existing_row_present() -> None:
    preflight = build_curated_negatome_control_preflight(
        curated_candidates=curated_candidates(),
        existing_pairs=pl.concat([negative_pair("mouse"), negative_pair("brandts_bat")]),
    )

    present = preflight.filter(pl.col("export_status") == "present_existing")

    assert present.height == 1
    assert present.row(0, named=True)["existing_negative_control_row"] is True


def test_merge_curated_negatome_control_pairs_adds_missing_rows_once() -> None:
    merged = merge_curated_negatome_control_pairs(
        existing_pairs=negative_pair("mouse"),
        curated_pairs=negative_pair("brandts_bat"),
    )

    assert merged.height == 2
    assert set(merged["target_species"]) == {"mouse", "brandts_bat"}

    merged_again = merge_curated_negatome_control_pairs(
        existing_pairs=merged,
        curated_pairs=negative_pair("brandts_bat"),
    )

    assert merged_again.height == 2
