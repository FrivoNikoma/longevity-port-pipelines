from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.curated_control_closure import (
    build_curated_control_closure,
    empty_curated_control_closure_report,
    render_curated_control_closure_markdown,
    validate_enrichment_schema,
)

COMPLEX_ID = "4xhu__A1_P09874--4xhu__B1_Q9UNS1"


def enrichment_rows(
    *,
    enrichment_ratio: float | None = 0.677237056501874,
    shuffled_control_ratio: float | None = 1.0033325630610515,
    negatome_control_ratio: float | None = 0.6695075860259664,
    p_interface_greater: float | None = 0.9999914826151858,
    p_interface_less: float | None = 8.582229941793972e-06,
    control_status: str = "has_shuffled_and_negatome",
    interpretation_status: str = "controlled_fail",
    status: str = "enrichment_completed",
) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [COMPLEX_ID],
            "chain": ["receptor"],
            "target_species": ["brandts_bat"],
            "target_species_taxid": [109478],
            "source_uniprot": ["P09874"],
            "status": [status],
            "control_status": [control_status],
            "interpretation_status": [interpretation_status],
            "enrichment_ratio": [enrichment_ratio],
            "shuffled_control_ratio": [shuffled_control_ratio],
            "negatome_control_ratio": [negatome_control_ratio],
            "p_interface_greater": [p_interface_greater],
            "p_interface_less": [p_interface_less],
            "effect_size_cohens_d": [-0.7583319109593206],
        }
    )


def test_empty_curated_control_closure_report_has_expected_columns() -> None:
    report = empty_curated_control_closure_report()

    assert report.is_empty()
    assert "closure_status" in report.columns
    assert "passes_negatome_gate" in report.columns
    assert "closure_note" in report.columns


def test_validate_enrichment_schema_reports_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_enrichment_schema(pl.DataFrame({"complex_id": ["x"]}))


def test_curated_control_closure_identifies_negatome_not_specific_case() -> None:
    closure = build_curated_control_closure(enrichment_rows())

    row = closure.row(0, named=True)
    assert row["signal_direction"] == "constraint"
    assert row["control_status"] == "has_shuffled_and_negatome"
    assert row["interpretation_status"] == "controlled_fail"
    assert row["passes_shuffled_gate"] is True
    assert row["passes_negatome_gate"] is False
    assert row["passes_directional_p_gate"] is True
    assert row["closure_status"] == "controlled_fail_negatome_not_specific"
    assert "not specific enough" in row["closure_note"]


def test_curated_control_closure_identifies_controlled_pass() -> None:
    closure = build_curated_control_closure(
        enrichment_rows(
            negatome_control_ratio=1.1,
            interpretation_status="controlled_pass",
        )
    )

    row = closure.row(0, named=True)
    assert row["signal_direction"] == "constraint"
    assert row["passes_shuffled_gate"] is True
    assert row["passes_negatome_gate"] is True
    assert row["passes_directional_p_gate"] is True
    assert row["closure_status"] == "controlled_pass"


def test_curated_control_closure_keeps_missing_negatome_preliminary() -> None:
    closure = build_curated_control_closure(
        enrichment_rows(
            negatome_control_ratio=None,
            control_status="missing_negatome",
            interpretation_status="preliminary_shuffled_only",
        )
    )

    row = closure.row(0, named=True)
    assert row["passes_shuffled_gate"] is True
    assert row["passes_negatome_gate"] is False
    assert row["closure_status"] == "preliminary_shuffled_only"
    assert "preliminary evidence only" in row["closure_note"]


def test_render_curated_control_closure_markdown_summarizes_rows() -> None:
    closure = build_curated_control_closure(enrichment_rows())

    markdown = render_curated_control_closure_markdown(closure)

    assert "# Curated ortholog control closure" in markdown
    assert COMPLEX_ID in markdown
    assert "controlled_fail_negatome_not_specific" in markdown
    assert "passes_negatome_gate" in markdown
