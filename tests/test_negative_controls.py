from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.negative_controls import build_negative_control_audit


def base_rows() -> dict[str, list[object]]:
    return {
        "complex_id": ["c1", "c2", "c3", "c4"],
        "chain": ["receptor", "receptor", "ligand", "ligand"],
        "target_species": ["mouse", "mouse", "mouse", "mouse"],
        "enrichment_ratio": [2.0, 2.0, 2.0, 2.0],
        "shuffled_control_ratio": [1.0, 1.0, None, None],
        "negatome_control_ratio": [0.5, None, 0.5, None],
        "mann_whitney_p": [0.01, 0.02, 0.03, 0.04],
        "p_interface_greater": [0.01, 0.02, 0.03, 0.04],
        "p_interface_less": [0.99, 0.98, 0.97, 0.96],
        "p_two_sided": [0.02, 0.04, 0.06, 0.08],
        "effect_size_cohens_d": [0.5, 0.4, -0.3, 0.0],
    }


def test_build_negative_control_audit_classifies_all_control_statuses() -> None:
    audit = build_negative_control_audit(pl.DataFrame(base_rows()))

    statuses = {
        row["complex_id"]: row["control_status"]
        for row in audit.select(["complex_id", "control_status"]).iter_rows(named=True)
    }

    assert statuses == {
        "c1": "has_shuffled_and_negatome",
        "c2": "missing_negatome",
        "c3": "missing_shuffled",
        "c4": "missing_all_controls",
    }


def test_build_negative_control_audit_computes_ratio_columns() -> None:
    audit = build_negative_control_audit(pl.DataFrame(base_rows()))

    row = audit.filter(pl.col("complex_id") == "c1").row(0, named=True)

    assert row["ratio_vs_shuffled_control"] == pytest.approx(2.0)
    assert row["ratio_vs_negatome_control"] == pytest.approx(4.0)


def test_build_negative_control_audit_missing_negatome_ratio_is_null() -> None:
    audit = build_negative_control_audit(pl.DataFrame(base_rows()))

    row = audit.filter(pl.col("complex_id") == "c2").row(0, named=True)

    assert row["control_status"] == "missing_negatome"
    assert row["ratio_vs_negatome_control"] is None


def test_build_negative_control_audit_rejects_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="Input is missing required columns"):
        build_negative_control_audit(pl.DataFrame({"complex_id": ["c1"]}))


def test_build_negative_control_audit_treats_zero_controls_as_missing() -> None:
    df = pl.DataFrame(
        {
            **base_rows(),
            "complex_id": ["c1", "c2", "c3", "c4"],
            "shuffled_control_ratio": [0.0, 1.0, 0.0, None],
            "negatome_control_ratio": [0.5, 0.0, 0.0, None],
        }
    )

    audit = build_negative_control_audit(df)

    statuses = {
        row["complex_id"]: row["control_status"]
        for row in audit.select(["complex_id", "control_status"]).iter_rows(named=True)
    }

    assert statuses == {
        "c1": "missing_shuffled",
        "c2": "missing_negatome",
        "c3": "missing_all_controls",
        "c4": "missing_all_controls",
    }
