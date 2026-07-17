from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages import (
    tp53_mdm2_gate7_coverage_repair_resolutions as resolutions,
)
from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_short_lived_control_results as short_lived,
)
from longevity_port_pipelines.stages import (
    tp53_mdm2_ortholog_repair_decisions as repair,
)
from longevity_port_pipelines.stages.tp53_mdm2_pilot_coverage_preflight import (
    build_tp53_mdm2_generic_strict_panel_input,
    build_tp53_mdm2_generic_strict_panel_summary,
    build_tp53_mdm2_pilot_coverage_preflight,
)

MANIFEST_PATH = Path("data/input/tp53_mdm2_pilot_manifest.csv")


def load_preflight() -> pl.DataFrame:
    return build_tp53_mdm2_pilot_coverage_preflight(
        pl.read_csv(MANIFEST_PATH),
        repair_decisions=repair.read_repair_decisions(),
        repair_resolutions=resolutions.read_resolutions(),
    )


def test_short_lived_control_result_validates() -> None:
    rows = short_lived.read_results()
    short_lived.validate_results(rows)
    assert rows.height == 1


def test_short_lived_control_records_reviewed_mouse_mdm2() -> None:
    row = short_lived.read_results().row(0, named=True)

    assert row["selected_control_species"] == "mouse"
    assert row["selected_control_species_taxid"] == "10090"
    assert row["target_protein_accession"] == "P23804"
    assert row["evidence_source_database"] == "UniProtKB Swiss-Prot"
    assert row["evidence_source_review_status"] == "reviewed"
    assert row["sequence_status"] == "complete"
    assert row["sequence_length"] == "489"


def test_short_lived_control_preserves_boundaries() -> None:
    row = short_lived.read_results().row(0, named=True)

    for field in short_lived.FALSE_BOUNDARY_FIELDS:
        assert row[field] == "false"

    assert row["aggregate_gate7_blocker_code"] == ("tp53_deferred_pending_source")


def test_short_lived_control_adds_mouse_strict_panel_row() -> None:
    strict_input = build_tp53_mdm2_generic_strict_panel_input(
        load_preflight(),
        short_lived_control_results=short_lived.read_results(),
    )

    mouse = strict_input.filter(
        (pl.col("candidate_id") == "tp53_mdm2_elephant_seed_mdm2_chain")
        & (pl.col("target_species") == "mouse")
    )
    assert mouse.height == 1

    row = mouse.row(0, named=True)
    assert row["target_species_taxid"] == 10090
    assert row["species_group"] == "short_lived_control"
    assert row["coverage_preflight_status"] == "coverage_preflight_ready"
    assert row["control_readiness_status"] == "controls_ready"


def test_short_lived_control_recomputes_mdm2_gate7_only() -> None:
    summary = build_tp53_mdm2_generic_strict_panel_summary(
        load_preflight(),
        short_lived_control_results=short_lived.read_results(),
    )
    by_candidate = {row["candidate_id"]: row for row in summary.iter_rows(named=True)}

    mdm2 = by_candidate["tp53_mdm2_elephant_seed_mdm2_chain"]
    assert mdm2["strict_panel_status"] == "strict_panel_ready"
    assert mdm2["n_strict_long_lived_ready"] == 1
    assert mdm2["n_strict_short_lived_ready"] == 1
    assert mdm2["strict_long_lived_species"] == "elephant"
    assert mdm2["strict_short_lived_species"] == "mouse"
    assert mdm2["contrast_dry_run_allowed"] is True
    assert mdm2["controlled_claim_allowed"] is False

    tp53 = by_candidate["tp53_mdm2_elephant_seed_tp53_chain"]
    assert tp53["strict_panel_status"] == "deferred_pending_source"
    assert tp53["contrast_dry_run_allowed"] is False
