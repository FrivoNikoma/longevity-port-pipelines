from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import cofolding_candidate_baseline as runner


def write_pinder_data(path: Path) -> None:
    pl.DataFrame(
        [
            {
                "id": "1nfi__A1_Q04206--1nfi__F1_P25963",
                "receptor_sequence": "A" * 70,
                "ligand_sequence": "C" * 91,
            },
            {
                "id": "7s68__D1_P09874--7s68__C1_P09874",
                "receptor_sequence": "D" * 25,
                "ligand_sequence": "E" * 53,
            },
        ]
    ).write_parquet(path)


def test_parse_pinder_candidate_id() -> None:
    parsed = runner.parse_pinder_candidate_id("1nfi__A1_Q04206--1nfi__F1_P25963")

    assert parsed == {
        "pdb_id": "1nfi",
        "receptor_chain": "A1",
        "receptor_uniprot": "Q04206",
        "ligand_chain": "F1",
        "ligand_uniprot": "P25963",
    }


def test_parse_pinder_candidate_id_rejects_invalid_id() -> None:
    with pytest.raises(ValueError, match="Invalid PINDER candidate id"):
        runner.parse_pinder_candidate_id("not_a_pinder_id")


def test_prepare_candidate_baseline_input_selects_exact_id(tmp_path: Path) -> None:
    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    row = runner.prepare_candidate_baseline_input(
        pinder_dir,
        "1nfi__A1_Q04206--1nfi__F1_P25963",
    )

    assert row["id"] == "1nfi__A1_Q04206--1nfi__F1_P25963"
    assert row["pdb_id"] == "1nfi"
    assert row["receptor_uniprot"] == "Q04206"
    assert row["ligand_uniprot"] == "P25963"
    assert row["receptor_sequence"] == "A" * 70
    assert row["ligand_sequence"] == "C" * 91
    assert row["pinder_receptor_len"] == 70
    assert row["pinder_ligand_len"] == 91


def test_prepare_candidate_baseline_input_rejects_missing_id(tmp_path: Path) -> None:
    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    with pytest.raises(RuntimeError, match="Missing PINDER sequences"):
        runner.prepare_candidate_baseline_input(
            pinder_dir,
            "missing__A1_P00000--missing__B1_P00001",
        )


def test_print_dry_run_reports_ids_lengths_and_no_live_actions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = {
        "id": "1nfi__A1_Q04206--1nfi__F1_P25963",
        "pdb_id": "1nfi",
        "receptor_chain": "A1",
        "receptor_uniprot": "Q04206",
        "ligand_chain": "F1",
        "ligand_uniprot": "P25963",
        "pinder_receptor_len": 70,
        "pinder_ligand_len": 91,
    }

    runner.print_dry_run(row, short_fragment_threshold=30)

    out = capsys.readouterr().out
    assert "[DRY RUN] Prepared 1 PINDER candidate baseline." in out
    assert "id: 1nfi__A1_Q04206--1nfi__F1_P25963" in out
    assert "receptor: Q04206 chain=A1" in out
    assert "ligand: P25963 chain=F1" in out
    assert "receptor_length: 70" in out
    assert "ligand_length: 91" in out
    assert "No Boltz API calls were made." in out
    assert "No runtime output files were written." in out
    assert "structure_url" not in out


def test_print_dry_run_warns_for_short_fragments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = {
        "id": "7s68__D1_P09874--7s68__C1_P09874",
        "pdb_id": "7s68",
        "receptor_chain": "D1",
        "receptor_uniprot": "P09874",
        "ligand_chain": "C1",
        "ligand_uniprot": "P09874",
        "pinder_receptor_len": 25,
        "pinder_ligand_len": 53,
    }

    runner.print_dry_run(row, short_fragment_threshold=30)

    out = capsys.readouterr().out
    assert "WARNING: receptor fragment is short" in out
    assert "No Boltz API calls were made." in out


def test_load_existing_candidate_ids_reads_csv(tmp_path: Path) -> None:
    output = tmp_path / "candidate_results.parquet"
    output.with_suffix(".csv").write_text(
        "id,boltz_classification\n1nfi__A1_Q04206--1nfi__F1_P25963,maintained\n",
        encoding="utf-8",
    )

    assert runner.load_existing_candidate_ids(output) == {"1nfi__A1_Q04206--1nfi__F1_P25963"}


def test_merge_candidate_baseline_results_keeps_latest_row(tmp_path: Path) -> None:
    output = tmp_path / "candidate_results.parquet"
    pl.DataFrame(
        [
            {
                "id": "1nfi__A1_Q04206--1nfi__F1_P25963",
                "boltz_classification": "uncertain",
                "iptm": 0.50,
            }
        ]
    ).write_parquet(output)

    new_results = pl.DataFrame(
        [
            {
                "id": "1nfi__A1_Q04206--1nfi__F1_P25963",
                "boltz_classification": "maintained",
                "iptm": 0.82,
            }
        ]
    )

    merged = runner.merge_candidate_baseline_results(new_results, output)

    assert merged.height == 1
    row = merged.row(0, named=True)
    assert row["boltz_classification"] == "maintained"
    assert row["iptm"] == 0.82


def test_run_live_candidate_baseline_submits_and_saves_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}

    class FakeClient:
        pass

    def fake_get_boltz_client() -> FakeClient:
        calls["client_created"] = True
        return FakeClient()

    def fake_submit_ppi_prediction(
        client: FakeClient,
        seq_a: str,
        seq_b: str,
        num_samples: int,
    ) -> dict[str, object]:
        calls["client_type"] = type(client).__name__
        calls["seq_a"] = seq_a
        calls["seq_b"] = seq_b
        calls["num_samples"] = num_samples
        return {
            "prediction_id": "pred_candidate_1nfi",
            "structure_confidence": 0.91,
            "ptm": 0.86,
            "iptm": 0.82,
            "complex_plddt": 0.88,
            "complex_iplddt": 0.80,
            "complex_pde": 1.20,
            "complex_ipde": 1.60,
            "binding_confidence": 0.74,
            "structure_url": "https://example.test/structure.cif",
        }

    monkeypatch.setattr(runner.cofolding, "get_boltz_client", fake_get_boltz_client)
    monkeypatch.setattr(
        runner.cofolding,
        "submit_ppi_prediction",
        fake_submit_ppi_prediction,
    )

    output = tmp_path / "candidate_results.parquet"
    row = {
        "id": "1nfi__A1_Q04206--1nfi__F1_P25963",
        "pdb_id": "1nfi",
        "receptor_chain": "A1",
        "receptor_uniprot": "Q04206",
        "ligand_chain": "F1",
        "ligand_uniprot": "P25963",
        "receptor_sequence": "AAAA",
        "ligand_sequence": "CCCC",
        "pinder_receptor_len": 4,
        "pinder_ligand_len": 4,
    }

    result = runner.run_live_candidate_baseline(row, output=output, num_samples=2)

    assert calls == {
        "client_created": True,
        "client_type": "FakeClient",
        "seq_a": "AAAA",
        "seq_b": "CCCC",
        "num_samples": 2,
    }
    assert output.exists()
    assert output.with_suffix(".csv").exists()

    saved = pl.read_parquet(output)
    assert result.height == 1
    assert saved.height == 1

    saved_row = saved.row(0, named=True)
    assert saved_row["id"] == "1nfi__A1_Q04206--1nfi__F1_P25963"
    assert saved_row["baseline_type"] == "pinder_fragment_candidate_human_baseline"
    assert saved_row["prediction_id"] == "pred_candidate_1nfi"
    assert saved_row["boltz_classification"] == "maintained"
    assert saved_row["num_samples"] == 2
