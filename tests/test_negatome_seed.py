from __future__ import annotations

import polars as pl
import pytest

from longevity_port_pipelines.stages.negatome_seed import (
    NEGATOME_CANDIDATE_COLUMNS,
    build_negatome_control_pair_candidates,
)


def residue_delta_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": ["c1", "c1", "c1", "c2"],
            "chain": ["receptor", "receptor", "receptor", "ligand"],
            "target_species": ["mouse", "mouse", "naked_mole_rat", "mouse"],
            "source_uniprot": ["P1", "P1", "P1", "P2"],
            "target_uniprot": ["T1", "T1", "T2", "T3"],
            "residue_number_1based": [1, 2, 1, 1],
            "delta": [0.1, 0.2, 0.3, 0.4],
        }
    )


def test_build_negatome_control_pair_candidates_deduplicates_candidate_rows() -> None:
    candidates = build_negatome_control_pair_candidates(residue_delta_rows())

    assert candidates.height == 3
    assert candidates.columns == NEGATOME_CANDIDATE_COLUMNS


def test_build_negatome_control_pair_candidates_marks_rows_as_not_ready() -> None:
    candidates = build_negatome_control_pair_candidates(residue_delta_rows())

    assert candidates["ready_for_input_contract"].to_list() == [False, False, False]
    assert set(candidates["negative_partner_source"].to_list()) == {"curation_required"}
    assert set(candidates["control_type"].to_list()) == {"negatome_style_curation_required"}


def test_build_negatome_control_pair_candidates_leaves_negative_partner_fields_empty() -> None:
    candidates = build_negatome_control_pair_candidates(residue_delta_rows())

    assert set(candidates["negative_partner_uniprot"].to_list()) == {""}
    assert set(candidates["negative_partner_sequence"].to_list()) == {""}


def test_build_negatome_control_pair_candidates_requires_residue_delta_columns() -> None:
    with pytest.raises(ValueError, match="Residue delta table is missing required columns"):
        build_negatome_control_pair_candidates(pl.DataFrame({"complex_id": ["c1"]}))
