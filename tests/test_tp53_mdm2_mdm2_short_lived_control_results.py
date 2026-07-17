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


def row_for_species(
    rows: pl.DataFrame,
    species: str,
) -> dict[str, object]:
    selected = rows.filter(pl.col("selected_control_species") == species)
    assert selected.height == 1
    return selected.row(0, named=True)


def test_short_lived_control_results_validate() -> None:
    rows = short_lived.read_results()
    short_lived.validate_results(rows)

    assert rows.height == 3
    assert set(rows["selected_control_species"].to_list()) == {
        "mouse",
        "rat",
        "hamster",
    }


def test_short_lived_control_records_mouse_ready() -> None:
    row = row_for_species(short_lived.read_results(), "mouse")

    assert row["selected_control_species_taxid"] == "10090"
    assert row["target_protein_accession"] == "P23804"
    assert row["sequence_status"] == "complete"
    assert row["selection_outcome"] == ("ready_for_gate7_strict_panel_planning")
    assert row["strict_panel_row_allowed"] == "true"


def test_short_lived_control_records_rat_manual_review() -> None:
    row = row_for_species(short_lived.read_results(), "rat")

    assert row["selected_control_species_taxid"] == "10116"
    assert row["target_protein_accession"] == "NP_001426446.1"
    assert row["evidence_source_accession"] == (
        "GeneID:314856|NP_001426446.1|A0A0G2JVC1|A6IGT1|D3ZVH5"
    )
    assert row["review_decision"] == ("needs_manual_review_choose_canonical_uniprot_accession")
    assert row["selection_outcome"] == "needs_manual_review"
    assert row["strict_panel_row_allowed"] == "false"


def test_short_lived_control_records_hamster_deferral() -> None:
    row = row_for_species(short_lived.read_results(), "hamster")

    assert row["selected_control_species_taxid"] == "10036"
    assert row["target_protein_accession"] == "Q60524"
    assert row["evidence_source_review_status"] == "reviewed"
    assert row["sequence_status"] == "fragment"
    assert row["sequence_length"] == "466"
    assert row["protein_existence_status"] == ("evidence_at_transcript_level")
    assert row["selection_outcome"] == "deferred_pending_source"
    assert row["strict_panel_row_allowed"] == "false"


def test_short_lived_controls_preserve_boundaries() -> None:
    for row in short_lived.read_results().iter_rows(named=True):
        for field in short_lived.FALSE_BOUNDARY_FIELDS:
            assert row[field] == "false"
        assert row["aggregate_gate7_blocker_code"] == ("tp53_deferred_pending_source")


def test_only_mouse_enters_short_lived_strict_panel() -> None:
    strict_input = build_tp53_mdm2_generic_strict_panel_input(
        load_preflight(),
        short_lived_control_results=short_lived.read_results(),
    )

    controls = strict_input.filter(pl.col("species_group") == "short_lived_control")
    assert controls.height == 1

    row = controls.row(0, named=True)
    assert row["target_species"] == "mouse"
    assert row["target_species_taxid"] == 10090
    assert row["coverage_preflight_status"] == ("coverage_preflight_ready")
    assert row["control_readiness_status"] == "controls_ready"


def test_evaluations_do_not_change_mdm2_counts() -> None:
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
    assert tp53["strict_panel_status"] == ("deferred_pending_source")
    assert tp53["contrast_dry_run_allowed"] is False
