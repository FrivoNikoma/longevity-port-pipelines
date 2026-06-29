from __future__ import annotations

from pathlib import Path

import polars as pl

from longevity_port_pipelines.models import LifespanCategory, Species
from longevity_port_pipelines.stages.species_coverage_audit import (
    SpeciesCoverageAuditSpec,
    build_species_coverage_audit,
    coverage_gap_status,
    output_prefix_for,
    target_species_rows,
    write_species_coverage_audit_outputs,
)

COMPLEX_ID = "4xhu__A1_P09874--4xhu__B1_Q9UNS1"


def test_target_species_rows_excludes_reference_and_orders_groups() -> None:
    rows = target_species_rows(
        {
            "human": Species(
                name="human",
                taxid=9606,
                category=LifespanCategory.REFERENCE,
            ),
            "mouse": Species(
                name="mouse",
                taxid=10090,
                category=LifespanCategory.SHORT_LIVED,
            ),
            "brandts_bat": Species(
                name="brandts_bat",
                taxid=109478,
                category=LifespanCategory.LONG_LIVED,
            ),
        }
    )

    assert rows == [
        {
            "target_species": "brandts_bat",
            "target_species_taxid": 109478,
            "group": "long-lived",
        },
        {
            "target_species": "mouse",
            "target_species_taxid": 10090,
            "group": "short-lived",
        },
    ]


def test_coverage_gap_status_labels_missing_cases() -> None:
    assert (
        coverage_gap_status(
            has_source_ortholog=True,
            has_local_candidate_file_rows=True,
        )
        == "ortholog_and_local_rows_present"
    )
    assert (
        coverage_gap_status(
            has_source_ortholog=False,
            has_local_candidate_file_rows=True,
        )
        == "missing_ortholog_but_local_rows_present"
    )
    assert (
        coverage_gap_status(
            has_source_ortholog=True,
            has_local_candidate_file_rows=False,
        )
        == "ortholog_present_but_missing_local_rows"
    )
    assert (
        coverage_gap_status(
            has_source_ortholog=False,
            has_local_candidate_file_rows=False,
        )
        == "missing_ortholog_and_local_rows"
    )


def test_species_coverage_audit_finds_ortholog_and_local_candidate_rows(tmp_path: Path) -> None:
    data_output = tmp_path / "output"
    data_output.mkdir()

    pl.DataFrame(
        {
            "source_uniprot": ["P09874", "OTHER"],
            "target_species_taxid": [109478, 10090],
            "target_uniprot": ["S7NG06", "OTHER_MOUSE"],
            "target_sequence": ["M" * 1024, "M" * 10],
            "is_reviewed": [False, False],
            "source_db": ["uniprot", "uniprot"],
        }
    ).write_csv(data_output / "example_ortholog_coverage.csv")

    pl.DataFrame(
        {
            "complex_id": [COMPLEX_ID],
            "chain": ["receptor"],
            "source_uniprot": ["P09874"],
            "target_species": ["brandts_bat"],
        }
    ).write_csv(data_output / "candidate_results.csv")

    species_rows = [
        {
            "target_species": "brandts_bat",
            "target_species_taxid": 109478,
            "group": "long-lived",
        },
        {
            "target_species": "mouse",
            "target_species_taxid": 10090,
            "group": "short-lived",
        },
    ]

    result = build_species_coverage_audit(
        spec=SpeciesCoverageAuditSpec(
            complex_id=COMPLEX_ID,
            pdb_id="4xhu",
            chain="receptor",
            source_uniprot="P09874",
        ),
        data_output=data_output,
        species_rows=species_rows,
    )

    brandts_bat = result.summary.filter(pl.col("target_species") == "brandts_bat").row(
        0, named=True
    )
    mouse = result.summary.filter(pl.col("target_species") == "mouse").row(0, named=True)

    assert brandts_bat["has_source_ortholog"] is True
    assert brandts_bat["n_ortholog_candidate_rows"] == 1
    assert brandts_bat["candidate_target_uniprots"] == "S7NG06"
    assert brandts_bat["candidate_sequence_lengths"] == "1024"
    assert brandts_bat["has_local_candidate_file_rows"] is True
    assert brandts_bat["n_local_candidate_file_rows"] == 1
    assert brandts_bat["coverage_gap_status"] == "ortholog_and_local_rows_present"

    assert mouse["has_source_ortholog"] is False
    assert mouse["has_local_candidate_file_rows"] is False
    assert mouse["coverage_gap_status"] == "missing_ortholog_and_local_rows"


def test_species_coverage_audit_writes_expected_outputs(tmp_path: Path) -> None:
    data_output = tmp_path / "output"
    data_output.mkdir()

    species_rows = [
        {
            "target_species": "brandts_bat",
            "target_species_taxid": 109478,
            "group": "long-lived",
        },
    ]

    result = build_species_coverage_audit(
        spec=SpeciesCoverageAuditSpec(
            complex_id=COMPLEX_ID,
            pdb_id="4xhu",
            chain="receptor",
            source_uniprot="P09874",
        ),
        data_output=data_output,
        species_rows=species_rows,
    )

    outputs = write_species_coverage_audit_outputs(
        result=result,
        output_dir=tmp_path / "interim",
        output_prefix="4xhu_p09874",
    )

    assert outputs.ortholog_raw.exists()
    assert outputs.local_file_raw.exists()
    assert outputs.summary.exists()
    assert outputs.summary.name == "4xhu_p09874_species_coverage_audit.csv"


def test_output_prefix_for_uses_pdb_and_uniprot() -> None:
    assert (
        output_prefix_for(
            SpeciesCoverageAuditSpec(
                complex_id=COMPLEX_ID,
                pdb_id="4xhu",
                chain="receptor",
                source_uniprot="P09874",
            )
        )
        == "4xhu_p09874"
    )
