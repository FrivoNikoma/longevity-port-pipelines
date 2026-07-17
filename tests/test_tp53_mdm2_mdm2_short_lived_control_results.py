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


def test_mouse_remains_ready_control() -> None:
    row = row_for_species(
        short_lived.read_results(),
        "mouse",
    )
    assert row["selection_outcome"] == ("ready_for_gate7_strict_panel_planning")
    assert row["blocker_code"] == "none"
    assert row["strict_panel_row_allowed"] == "true"


def test_rat_records_terminal_source_deferral() -> None:
    row = row_for_species(
        short_lived.read_results(),
        "rat",
    )
    assert row["target_protein_accession"] == ("NP_001426446.1")
    assert row["sequence_length"] == "434"
    assert row["review_decision"] == ("defer_rat_pending_unambiguous_canonical_sequence_source")
    assert row["selection_outcome"] == ("deferred_pending_source")
    assert row["blocker_code"] == ("no_unambiguous_canonical_rat_mdm2_sequence")
    assert row["claim_status"] == ("terminal_source_blocker")
    assert row["strict_panel_row_allowed"] == "false"


def test_hamster_records_complete_sequence_group() -> None:
    row = row_for_species(
        short_lived.read_results(),
        "hamster",
    )
    assert row["target_protein_accession"] == ("A0ABM2YB85")
    assert row["evidence_source_accession"] == (
        "GeneID:101833011|A0ABM2YB85|XP_040610761.1|Q60524|AAC52425.1"
    )
    assert row["sequence_length"] == "510"
    assert row["review_decision"] == (
        "accept_complete_hamster_mdm2_uniprot_refseq_sequence_group_for_gate7_technical_planning"
    )
    assert row["selection_outcome"] == ("ready_for_gate7_strict_panel_planning")
    assert row["blocker_code"] == "none"
    assert row["claim_status"] == ("strict_panel_readiness")
    assert row["strict_panel_row_allowed"] == "true"


def test_boundaries_remain_closed() -> None:
    for row in short_lived.read_results().iter_rows(named=True):
        for field in short_lived.FALSE_BOUNDARY_FIELDS:
            assert row[field] == "false"


def test_mouse_and_hamster_enter_strict_panel() -> None:
    strict_input = build_tp53_mdm2_generic_strict_panel_input(
        load_preflight(),
        short_lived_control_results=(short_lived.read_results()),
    )
    controls = strict_input.filter(pl.col("species_group") == "short_lived_control")
    assert controls.height == 2
    assert set(controls["target_species"].to_list()) == {"mouse", "hamster"}


def test_hamster_resolution_expands_panel_counts() -> None:
    summary = build_tp53_mdm2_generic_strict_panel_summary(
        load_preflight(),
        short_lived_control_results=(short_lived.read_results()),
    )
    by_candidate = {row["candidate_id"]: row for row in summary.iter_rows(named=True)}
    mdm2 = by_candidate["tp53_mdm2_elephant_seed_mdm2_chain"]
    assert mdm2["n_strict_long_lived_ready"] == 1
    assert mdm2["n_strict_short_lived_ready"] == 2
    assert mdm2["strict_long_lived_species"] == ("elephant")
    assert mdm2["strict_short_lived_species"] == ("hamster,mouse")
    assert mdm2["strict_panel_status"] == ("strict_panel_ready")
    assert mdm2["contrast_dry_run_allowed"] is True
    assert mdm2["controlled_claim_allowed"] is False

    tp53 = by_candidate["tp53_mdm2_elephant_seed_tp53_chain"]
    assert tp53["strict_panel_status"] == ("deferred_pending_source")
    assert tp53["contrast_dry_run_allowed"] is False
