from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import polars as pl
import pytest

from longevity_port_pipelines.stages import candidate_species_coverage_matrix as matrix


def manifest_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "candidate_id": ["4xhu__A1_P09874--4xhu__B1_Q9UNS1"],
            "chain": ["receptor"],
            "source_uniprot": ["P09874"],
            "priority": ["1"],
        }
    )


def fake_baseline(candidate_id: str) -> dict[str, object]:
    return {
        "id": candidate_id,
        "pdb_id": "4xhu",
        "receptor_uniprot": "P09874",
        "ligand_uniprot": "Q9UNS1",
        "pinder_receptor_len": 333,
        "pinder_ligand_len": 83,
    }


def coverage_summary() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "target_species": ["mouse", "bowhead_whale", "naked_mole_rat"],
            "target_species_taxid": [10090, 27622, 10181],
            "group": ["short-lived", "long-lived", "long-lived"],
            "has_source_ortholog": [True, False, True],
            "n_ortholog_candidate_rows": [1, 0, 1],
            "candidate_target_uniprots": ["P11111", "", "Q22222"],
            "candidate_sequence_lengths": ["333", "", "333"],
            "ortholog_source_dbs": ["ortholog_db", "", "ortholog_db"],
            "ortholog_source_files": [
                "data/output/example_ortholog_coverage.csv",
                "",
                "data/output/example_ortholog_coverage.csv",
            ],
            "has_local_candidate_file_rows": [True, False, False],
            "n_local_candidate_file_rows": [2, 0, 0],
            "local_files": ["data/output/example_rows.csv", "", ""],
            "coverage_gap_status": [
                "ortholog_and_local_rows_present",
                "missing_ortholog_and_local_rows",
                "ortholog_present_but_missing_local_rows",
            ],
        }
    )


@pytest.mark.parametrize(
    ("coverage_gap_status", "expected_action"),
    [
        ("ortholog_and_local_rows_present", "coverage_ready"),
        ("ortholog_present_but_missing_local_rows", "generate_local_candidate_rows"),
        ("missing_ortholog_but_local_rows_present", "review_local_rows_without_source_ortholog"),
        ("missing_ortholog_and_local_rows", "fetch_or_curate_source_ortholog"),
        ("unexpected_status", "review_coverage_status"),
    ],
)
def test_recommended_coverage_action(
    coverage_gap_status: str,
    expected_action: str,
) -> None:
    assert matrix.recommended_coverage_action(coverage_gap_status) == expected_action


def test_build_candidate_species_coverage_matrix_flattens_candidate_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        matrix,
        "prepare_candidate_baseline_input",
        lambda _pinder_data_dir, candidate_id: fake_baseline(candidate_id),
    )
    monkeypatch.setattr(
        matrix,
        "build_species_coverage_audit",
        lambda **_kwargs: SimpleNamespace(summary=coverage_summary()),
    )

    result = matrix.build_candidate_species_coverage_matrix(manifest=manifest_rows())

    assert result.height == 3
    assert set(result["target_species"].to_list()) == {
        "mouse",
        "bowhead_whale",
        "naked_mole_rat",
    }

    mouse = result.filter(pl.col("target_species") == "mouse").row(0, named=True)
    assert mouse["candidate_id"] == "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
    assert mouse["pdb_id"] == "4xhu"
    assert mouse["chain"] == "receptor"
    assert mouse["source_uniprot"] == "P09874"
    assert mouse["priority"] == "1"
    assert mouse["has_source_ortholog"] is True
    assert mouse["has_local_candidate_file_rows"] is True
    assert mouse["coverage_gap_status"] == "ortholog_and_local_rows_present"
    assert mouse["recommended_coverage_action"] == "coverage_ready"

    bowhead = result.filter(pl.col("target_species") == "bowhead_whale").row(0, named=True)
    assert bowhead["has_source_ortholog"] is False
    assert bowhead["has_local_candidate_file_rows"] is False
    assert bowhead["recommended_coverage_action"] == "fetch_or_curate_source_ortholog"

    nmr = result.filter(pl.col("target_species") == "naked_mole_rat").row(0, named=True)
    assert nmr["has_source_ortholog"] is True
    assert nmr["has_local_candidate_file_rows"] is False
    assert nmr["recommended_coverage_action"] == "generate_local_candidate_rows"


def test_build_candidate_species_coverage_matrix_records_missing_baseline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_missing(_pinder_data_dir: Path, _candidate_id: str) -> dict[str, object]:
        raise RuntimeError("missing PINDER baseline")

    monkeypatch.setattr(matrix, "prepare_candidate_baseline_input", raise_missing)

    result = matrix.build_candidate_species_coverage_matrix(manifest=manifest_rows())

    assert result.height == 1
    row = result.row(0, named=True)
    assert row["candidate_id"] == "4xhu__A1_P09874--4xhu__B1_Q9UNS1"
    assert row["coverage_gap_status"] == "not_audited"
    assert row["recommended_coverage_action"] == "fix_baseline_input"
    assert "missing PINDER baseline" in row["coverage_note"]


def test_action_counts_counts_recommended_actions() -> None:
    result = pl.DataFrame(
        {
            "recommended_coverage_action": [
                "coverage_ready",
                "coverage_ready",
                "fetch_or_curate_source_ortholog",
            ]
        }
    )

    assert matrix.action_counts(result) == {
        "coverage_ready": 2,
        "fetch_or_curate_source_ortholog": 1,
    }
