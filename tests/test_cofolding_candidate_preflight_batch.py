from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import polars as pl
import pytest

from longevity_port_pipelines.stages import cofolding_candidate_preflight_batch as batch


def manifest_rows(source_uniprot: str = "P09874") -> pl.DataFrame:
    return pl.DataFrame(
        {
            "candidate_id": ["4xhu__A1_P09874--4xhu__B1_Q9UNS1"],
            "chain": ["receptor"],
            "source_uniprot": [source_uniprot],
            "priority": ["1"],
        }
    )


def complete_coverage_summary() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "target_species": ["mouse", "naked_mole_rat"],
            "has_source_ortholog": [True, True],
            "has_local_candidate_file_rows": [True, True],
        }
    )


def missing_coverage_summary() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "target_species": ["mouse", "bowhead_whale"],
            "has_source_ortholog": [True, False],
            "has_local_candidate_file_rows": [True, True],
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


def existing_negatome_pairs() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "complex_id": [
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
            ],
            "chain": ["receptor", "receptor"],
            "target_species": ["mouse", "naked_mole_rat"],
            "source_uniprot": ["P09874", "P09874"],
            "negative_partner_uniprot": ["O60907", "O60907"],
            "negative_partner_source": ["negatome_database", "negatome_database"],
            "negative_partner_sequence": ["ACDE", "ACDE"],
            "control_type": ["curated_negative", "curated_negative"],
        }
    )


def test_manifest_candidates_requires_core_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        batch.manifest_candidates(pl.DataFrame({"candidate_id": ["c1"]}))


def test_manifest_candidates_rejects_duplicate_ids() -> None:
    manifest = pl.DataFrame(
        {
            "candidate_id": ["c1", "c1"],
            "chain": ["receptor", "receptor"],
            "source_uniprot": ["P1", "P1"],
        }
    )

    with pytest.raises(ValueError, match="Duplicate candidate_id"):
        batch.manifest_candidates(manifest)


def test_negatome_readiness_marks_missing_curated_partner() -> None:
    readiness = batch.negatome_readiness(
        candidate=batch.ManifestCandidate(
            candidate_id="c1",
            chain="receptor",
            source_uniprot="UNKNOWN",
        ),
        expected_species=["mouse", "rat"],
        existing_pairs=None,
    )

    assert readiness.status == "missing_curated_negative_partner"
    assert readiness.negative_partner_uniprot == ""
    assert readiness.missing_species == "mouse, rat"


def test_build_scorecard_ready_for_human_baseline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        batch,
        "prepare_candidate_baseline_input",
        lambda _pinder_data_dir, candidate_id: fake_baseline(candidate_id),
    )
    monkeypatch.setattr(
        batch,
        "build_species_coverage_audit",
        lambda **_kwargs: SimpleNamespace(summary=complete_coverage_summary()),
    )

    scorecard = batch.build_candidate_preflight_scorecard(
        manifest=manifest_rows(),
        existing_negatome_pairs=existing_negatome_pairs(),
    )

    row = scorecard.row(0, named=True)
    assert row["baseline_input_status"] == "input_prepared"
    assert row["species_coverage_status"] == "complete_species_coverage"
    assert row["negatome_status"] == "present_existing"
    assert row["recommended_next_action"] == "ready_for_human_baseline"
    assert row["negative_partner_uniprot"] == "O60907"


def test_build_scorecard_blocks_missing_species_coverage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        batch,
        "prepare_candidate_baseline_input",
        lambda _pinder_data_dir, candidate_id: fake_baseline(candidate_id),
    )
    monkeypatch.setattr(
        batch,
        "build_species_coverage_audit",
        lambda **_kwargs: SimpleNamespace(summary=missing_coverage_summary()),
    )

    scorecard = batch.build_candidate_preflight_scorecard(
        manifest=manifest_rows(),
        existing_negatome_pairs=existing_negatome_pairs(),
    )

    row = scorecard.row(0, named=True)
    assert row["species_coverage_status"] == "missing_source_ortholog"
    assert row["missing_source_ortholog_species"] == "bowhead_whale"
    assert row["recommended_next_action"] == "fix_species_coverage"


def test_build_scorecard_blocks_missing_negatome_export(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        batch,
        "prepare_candidate_baseline_input",
        lambda _pinder_data_dir, candidate_id: fake_baseline(candidate_id),
    )
    monkeypatch.setattr(
        batch,
        "build_species_coverage_audit",
        lambda **_kwargs: SimpleNamespace(summary=complete_coverage_summary()),
    )

    scorecard = batch.build_candidate_preflight_scorecard(
        manifest=manifest_rows(),
        existing_negatome_pairs=None,
    )

    row = scorecard.row(0, named=True)
    assert row["species_coverage_status"] == "complete_species_coverage"
    assert row["negatome_status"] == "missing_export_ready"
    assert row["missing_negatome_species"] == "mouse, naked_mole_rat"
    assert row["recommended_next_action"] == "fix_negatome_controls"


def test_build_scorecard_records_missing_baseline_input(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_missing(_pinder_data_dir: Path, _candidate_id: str) -> dict[str, object]:
        raise RuntimeError("missing PINDER sequences")

    monkeypatch.setattr(batch, "prepare_candidate_baseline_input", raise_missing)

    scorecard = batch.build_candidate_preflight_scorecard(
        manifest=manifest_rows(),
        existing_negatome_pairs=None,
    )

    row = scorecard.row(0, named=True)
    assert row["baseline_input_status"] == "missing_baseline_input"
    assert row["recommended_next_action"] == "fix_baseline_input"
    assert "missing PINDER sequences" in row["preflight_note"]
