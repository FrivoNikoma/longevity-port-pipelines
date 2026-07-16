from pathlib import Path

from longevity_port_pipelines.stages import (
    tp53_mdm2_gate7_coverage_repair_resolutions as resolutions,
)

ROOT = Path(__file__).resolve().parents[1]


def test_resolution_table_validates_against_committed_sources() -> None:
    rows = resolutions.read_resolutions(ROOT / resolutions.DEFAULT_RESOLUTIONS_PATH)
    resolutions.validate_resolutions(rows, root=ROOT)

    assert rows.height == 2
    assert set(rows.get_column("coverage_repair_outcome").to_list()) == {
        "coverage_repaired_and_ready",
        "deferred_pending_source",
    }


def test_resolution_lookup_records_mdm2_and_tp53_outcomes() -> None:
    rows = resolutions.read_resolutions(ROOT / resolutions.DEFAULT_RESOLUTIONS_PATH)
    lookup = resolutions.resolution_lookup(rows)

    mdm2 = lookup[
        (
            "tp53_mdm2_elephant_seed_mdm2_chain",
            "Q00987",
            "elephant",
            "A",
        )
    ]
    assert mdm2["target_uniprot_after_resolution"] == "G3SX30"
    assert mdm2["repair_status_after_resolution"] == ("accepted_for_planning_after_review")
    assert mdm2["strict_panel_allowed_after_resolution"] == "true"
    assert mdm2["gate7_entry_allowed"] == "false"

    tp53 = lookup[
        (
            "tp53_mdm2_elephant_seed_tp53_chain",
            "P04637",
            "elephant",
            "B",
        )
    ]
    assert tp53["target_uniprot_after_resolution"] == "unresolved"
    assert tp53["repair_status_after_resolution"] == ("deferred_pending_source")
    assert tp53["concrete_source_blocker"] == (
        "no_accepted_accession_level_elephant_tp53_ortholog_evidence"
    )


def test_resolution_rows_keep_downstream_and_claim_boundaries_closed() -> None:
    rows = resolutions.read_resolutions(ROOT / resolutions.DEFAULT_RESOLUTIONS_PATH)
    for field in [
        "gate7_entry_allowed",
        "gate8_entry_allowed",
        "gate8_promoted",
        "gate9_promoted",
        "biological_approval_granted",
        "live_calls_performed",
        "biohub_called",
        "embeddings_generated",
        "npy_artifact_committed",
        "data_output_artifact_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "biological_claim_made",
    ]:
        assert set(rows.get_column(field).to_list()) == {"false"}
