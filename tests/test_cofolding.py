from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import polars as pl
import pytest
import typer

from longevity_port_pipelines.stages import cofolding


def test_species_taxid_by_name_uses_species_names() -> None:
    mapping = cofolding.species_taxid_by_name()

    assert mapping["human"] == 9606
    assert mapping["mouse"] == 10090
    assert mapping["myotis_lucifugus"] == 59463
    assert mapping["brandts_bat"] == 109478
    assert "bat" not in mapping


def test_parse_complex_id_valid() -> None:
    complex_id = "6b2e__A1_P54646--6b2e__B1_O43741"

    assert cofolding.parse_complex_id(complex_id) == ("P54646", "O43741")


def test_parse_complex_id_invalid() -> None:
    assert cofolding.parse_complex_id("not-a-complex") == (None, None)
    assert cofolding.parse_complex_id("left--middle--right") == (None, None)
    assert cofolding.parse_complex_id("6b2e__A1_BAD--6b2e__B1_O43741") == (None, "O43741")


def test_classify_interaction_maintained() -> None:
    assert cofolding.classify_interaction(0.80, 0.20) == "maintained"


def test_classify_interaction_functionally_broken() -> None:
    assert cofolding.classify_interaction(0.40, 0.80) == "functionally_broken"
    assert cofolding.classify_interaction(0.40, None) == "functionally_broken"


def test_classify_interaction_incompatible() -> None:
    assert cofolding.classify_interaction(0.40, 0.40) == "incompatible"


def test_classify_interaction_uncertain() -> None:
    assert cofolding.classify_interaction(0.60, 0.80) == "uncertain"


def test_build_cross_species_pair_receptor(monkeypatch: pytest.MonkeyPatch) -> None:
    ortholog_df = pl.DataFrame(
        [
            {
                "source_uniprot": "P54646",
                "target_species_taxid": 10181,
                "target_sequence": "ORTHOLOG_RECEPTOR",
            }
        ]
    )

    def fake_fetch_sequence(uniprot_id: str) -> str:
        assert uniprot_id == "O43741"
        return "HUMAN_LIGAND"

    monkeypatch.setattr(cofolding, "fetch_sequence_uniprot", fake_fetch_sequence)

    pair = cofolding.build_cross_species_pair(
        "6b2e__A1_P54646--6b2e__B1_O43741",
        "receptor",
        "naked_mole_rat",
        ortholog_df,
    )

    assert pair == ("HUMAN_LIGAND", "ORTHOLOG_RECEPTOR")


def test_build_cross_species_pair_ligand(monkeypatch: pytest.MonkeyPatch) -> None:
    ortholog_df = pl.DataFrame(
        [
            {
                "source_uniprot": "O43741",
                "target_species_taxid": 10181,
                "target_sequence": "ORTHOLOG_LIGAND",
            }
        ]
    )

    def fake_fetch_sequence(uniprot_id: str) -> str:
        assert uniprot_id == "P54646"
        return "HUMAN_RECEPTOR"

    monkeypatch.setattr(cofolding, "fetch_sequence_uniprot", fake_fetch_sequence)

    pair = cofolding.build_cross_species_pair(
        "6b2e__A1_P54646--6b2e__B1_O43741",
        "ligand",
        "naked_mole_rat",
        ortholog_df,
    )

    assert pair == ("HUMAN_RECEPTOR", "ORTHOLOG_LIGAND")


def test_build_cross_species_pair_unknown_species(monkeypatch: pytest.MonkeyPatch) -> None:
    ortholog_df = pl.DataFrame(
        [
            {
                "source_uniprot": "P54646",
                "target_species_taxid": 10181,
                "target_sequence": "ORTHOLOG_RECEPTOR",
            }
        ]
    )

    def fail_fetch_sequence(uniprot_id: str) -> str:
        raise AssertionError(f"fetch_sequence_uniprot should not be called for {uniprot_id}")

    monkeypatch.setattr(cofolding, "fetch_sequence_uniprot", fail_fetch_sequence)

    pair = cofolding.build_cross_species_pair(
        "6b2e__A1_P54646--6b2e__B1_O43741",
        "receptor",
        "not_a_species",
        ortholog_df,
    )

    assert pair is None


def test_retrieve_prediction_with_retry_succeeds_after_transient_failures() -> None:
    calls = {"count": 0}

    def fake_retrieve(prediction_id: str) -> dict[str, str]:
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("temporary retrieve failure")
        return {"prediction_id": prediction_id, "status": "succeeded"}

    client = SimpleNamespace(
        predictions=SimpleNamespace(structure_and_binding=SimpleNamespace(retrieve=fake_retrieve))
    )

    result = cofolding.retrieve_prediction_with_retry(
        client,
        "pred_123",
        attempts=3,
        sleep_seconds=0,
    )

    assert result == {"prediction_id": "pred_123", "status": "succeeded"}
    assert calls["count"] == 3


def test_retrieve_prediction_with_retry_raises_after_exhaustion() -> None:
    calls = {"count": 0}

    def fake_retrieve(prediction_id: str) -> None:
        calls["count"] += 1
        raise RuntimeError(f"temporary retrieve failure for {prediction_id}")

    client = SimpleNamespace(
        predictions=SimpleNamespace(structure_and_binding=SimpleNamespace(retrieve=fake_retrieve))
    )

    with pytest.raises(RuntimeError, match="failed after 2 attempts"):
        cofolding.retrieve_prediction_with_retry(
            client,
            "pred_123",
            attempts=2,
            sleep_seconds=0,
        )

    assert calls["count"] == 2


def test_live_without_yes_live_does_not_create_boltz_client(
    tmp_path: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    enrichment_path = tmp_path / "enrichment.parquet"

    pl.DataFrame(
        [
            {
                "complex_id": "6b2e__A1_P54646--6b2e__B1_O43741",
                "chain": "receptor",
                "source_species": "human",
                "target_species": "naked_mole_rat",
                "enrichment_ratio": 1.5,
            }
        ]
    ).write_parquet(enrichment_path)

    client_created = {"value": False}

    def fake_get_boltz_client() -> None:
        client_created["value"] = True
        raise AssertionError("get_boltz_client should not be called without --yes-live")

    monkeypatch.setattr(cofolding, "get_boltz_client", fake_get_boltz_client)

    with pytest.raises(typer.Exit) as exc_info:
        cofolding.main(
            top_n=1,
            complex_id=None,
            species=None,
            test=False,
            num_samples=1,
            output_path=tmp_path / "cofolding_results.parquet",
            enrichment_input=enrichment_path,
            ortholog_input=tmp_path / "ortholog_coverage.csv",
            yes_live=False,
            dry_run_inputs=False,
            retrieve_prediction=None,
            cif_output=None,
        )

    assert exc_info.value.exit_code == 1
    assert client_created["value"] is False


def test_load_ortholog_table_uses_custom_path(tmp_path: Any) -> None:
    custom_path = tmp_path / "custom_ortholog_coverage.csv"

    pl.DataFrame(
        [
            {
                "source_uniprot": "P54646",
                "target_species_taxid": 10181,
                "target_sequence": "ORTHOLOG_RECEPTOR",
            }
        ]
    ).write_csv(custom_path)

    loaded = cofolding.load_ortholog_table(custom_path)

    assert loaded is not None
    assert loaded.to_dicts() == [
        {
            "source_uniprot": "P54646",
            "target_species_taxid": 10181,
            "target_sequence": "ORTHOLOG_RECEPTOR",
        }
    ]


def test_load_ortholog_table_returns_none_for_missing_custom_path(tmp_path: Any) -> None:
    missing_path = tmp_path / "missing_ortholog_coverage.csv"

    assert cofolding.load_ortholog_table(missing_path) is None
