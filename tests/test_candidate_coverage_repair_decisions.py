from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import candidate_coverage_repair_decisions as repair


def repair_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "target_species": "bowhead_whale",
                "target_species_taxid": "27622",
                "group": "long-lived",
                "coverage_gap_status": "missing_ortholog_but_local_rows_present",
                "recommended_coverage_action": "local_downstream_evidence_without_source_ortholog",
                "candidate_target_uniprots": "",
                "ortholog_source_dbs": "",
                "ortholog_source_files": "",
                "local_files": "data/output/example.csv",
                "repair_decision": "needs_external_manual_sequence_review",
                "repair_priority": "high",
                "claim_policy": "deferred_no_claim",
                "repair_note": "Local downstream rows exist, but source ortholog provenance is missing.",
            }
        ]
    )


def test_committed_sirt6_repair_decision_table_is_valid() -> None:
    rows = repair.read_repair_decisions()

    repair.validate_repair_decisions(rows)

    assert rows.height == 11
    assert set(rows.get_column("coverage_gap_status").to_list()) == {
        "missing_ortholog_but_local_rows_present"
    }
    assert set(rows.get_column("claim_policy").to_list()) == {"deferred_no_claim"}


def test_validate_repair_decisions_accepts_valid_rows() -> None:
    repair.validate_repair_decisions(repair_rows())


def test_validate_repair_decisions_rejects_missing_columns() -> None:
    rows = repair_rows().drop("claim_policy")

    with pytest.raises(ValueError, match="missing required columns"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_duplicate_keys() -> None:
    rows = pl.concat([repair_rows(), repair_rows()])

    with pytest.raises(ValueError, match="duplicate candidate/source/species keys"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_values() -> None:
    rows = repair_rows().with_columns(pl.lit("unsafe_claim_allowed").alias("claim_policy"))

    with pytest.raises(ValueError, match="invalid values in claim_policy"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_blank_decision_fields() -> None:
    rows = repair_rows().with_columns(pl.lit("").alias("repair_note"))

    with pytest.raises(ValueError, match="blank required decision fields"):
        repair.validate_repair_decisions(rows)


def test_default_repair_decision_path_points_to_committed_input() -> None:
    assert (
        Path("data/input/sirt6_candidate_coverage_repair_decisions.csv")
        == repair.DEFAULT_REPAIR_DECISIONS_PATH
    )
