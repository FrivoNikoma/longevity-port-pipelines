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
