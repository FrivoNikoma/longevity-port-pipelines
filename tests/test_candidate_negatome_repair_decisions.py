from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages import candidate_negatome_repair_decisions as repair


def valid_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_id": "candidate_a",
                "pdb_id": "4xhu",
                "chain": "receptor",
                "source_uniprot": "P09874",
                "priority": "1",
                "negatome_status": "partial_existing",
                "negative_partner_uniprot": "O60907",
                "missing_negatome_species": "bowhead_whale",
                "repair_decision": "complete_missing_negatome_species",
                "repair_priority": "high",
                "claim_policy": "deferred_no_claim",
                "repair_note": (
                    "Complete missing NEGATOME-style controls before controlled claims."
                ),
            }
        ]
    )


def test_committed_sirt6_negatome_repair_decision_table_is_valid() -> None:
    rows = repair.read_repair_decisions()

    assert rows.height >= 1
    repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_accepts_valid_rows() -> None:
    repair.validate_repair_decisions(valid_rows())


def test_validate_repair_decisions_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        repair.validate_repair_decisions(valid_rows().drop("repair_note"))


def test_validate_repair_decisions_rejects_duplicate_keys() -> None:
    rows = pl.concat([valid_rows(), valid_rows()])

    with pytest.raises(ValueError, match="duplicate candidate/source/partner keys"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_values() -> None:
    rows = valid_rows().with_columns(pl.lit("claim_now").alias("claim_policy"))

    with pytest.raises(ValueError, match="invalid values in claim_policy"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_blank_decision_fields() -> None:
    rows = valid_rows().with_columns(pl.lit("").alias("repair_decision"))

    with pytest.raises(ValueError, match="blank required decision fields"):
        repair.validate_repair_decisions(rows)


def test_default_repair_decision_path_points_to_committed_input() -> None:
    assert (
        repair.DEFAULT_REPAIR_DECISIONS_PATH.as_posix()
        == "data/input/sirt6_candidate_negatome_repair_decisions.csv"
    )
