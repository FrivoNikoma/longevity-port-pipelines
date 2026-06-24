from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import cofolding_baseline_controls as runner


def write_audit(path: Path) -> None:
    pl.DataFrame(
        [
            {
                "id": "3lqz__B1_P04440--3lqz__A1_P20036",
                "probability": 1.0,
                "buried_sasa": 6368.0,
                "intermolecular_contacts": 220,
                "receptor_len": 198,
                "ligand_len": 181,
                "receptor_uniprot": "P04440",
                "ligand_uniprot": "P20036",
                "human_heterodimer_control": True,
                "technical_homomer_control": False,
            },
            {
                "id": "1abc__A1_P12345--1abc__B1_P12345",
                "probability": 0.95,
                "buried_sasa": 2500.0,
                "intermolecular_contacts": 100,
                "receptor_len": 100,
                "ligand_len": 100,
                "receptor_uniprot": "P12345",
                "ligand_uniprot": "P12345",
                "human_heterodimer_control": False,
                "technical_homomer_control": True,
            },
        ]
    ).write_csv(path)


def write_pinder_data(path: Path) -> None:
    pl.DataFrame(
        [
            {
                "id": "3lqz__B1_P04440--3lqz__A1_P20036",
                "receptor_sequence": "A" * 198,
                "ligand_sequence": "C" * 181,
            },
            {
                "id": "1abc__A1_P12345--1abc__B1_P12345",
                "receptor_sequence": "D" * 100,
                "ligand_sequence": "E" * 100,
            },
        ]
    ).write_parquet(path)


def test_filter_control_candidates_human_heterodimer(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    audit = runner.load_audit(audit_path)
    controls = runner.filter_control_candidates(
        audit,
        control_kind="human_heterodimer",
    )

    assert controls.height == 1
    assert controls.row(0, named=True)["id"] == "3lqz__B1_P04440--3lqz__A1_P20036"


def test_filter_control_candidates_technical_homomer(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    audit = runner.load_audit(audit_path)
    controls = runner.filter_control_candidates(
        audit,
        control_kind="technical_homomer",
    )

    assert controls.height == 1
    assert controls.row(0, named=True)["id"] == "1abc__A1_P12345--1abc__B1_P12345"


def test_filter_control_candidates_rejects_unknown_kind(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    audit = runner.load_audit(audit_path)

    with pytest.raises(ValueError, match="Unknown control kind"):
        runner.filter_control_candidates(audit, control_kind="mystery")


def test_load_pinder_fragment_sequences(tmp_path: Path) -> None:
    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    sequences = runner.load_pinder_fragment_sequences(
        pinder_dir,
        ["3lqz__B1_P04440--3lqz__A1_P20036"],
    )

    assert set(sequences) == {"3lqz__B1_P04440--3lqz__A1_P20036"}
    record = sequences["3lqz__B1_P04440--3lqz__A1_P20036"]
    assert record["receptor_sequence"] == "A" * 198
    assert record["ligand_sequence"] == "C" * 181
    assert record["pinder_receptor_len"] == 198
    assert record["pinder_ligand_len"] == 181


def test_prepare_baseline_inputs(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    inputs = runner.prepare_baseline_inputs(
        audit_path,
        pinder_dir,
        control_kind="human_heterodimer",
        top_n=1,
    )

    assert len(inputs) == 1
    row = inputs[0]
    assert row["id"] == "3lqz__B1_P04440--3lqz__A1_P20036"
    assert row["control_kind"] == "human_heterodimer"
    assert row["baseline_type"] == "pinder_fragment_human_heterodimer"
    assert row["receptor_sequence"] == "A" * 198
    assert row["ligand_sequence"] == "C" * 181


def test_prepare_baseline_inputs_returns_empty_for_missing_kind(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    pl.DataFrame(
        [
            {
                "id": "3lqz__B1_P04440--3lqz__A1_P20036",
                "probability": 1.0,
                "buried_sasa": 6368.0,
                "intermolecular_contacts": 220,
                "receptor_len": 198,
                "ligand_len": 181,
                "receptor_uniprot": "P04440",
                "ligand_uniprot": "P20036",
                "human_heterodimer_control": False,
                "technical_homomer_control": False,
            }
        ]
    ).write_csv(audit_path)

    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    inputs = runner.prepare_baseline_inputs(
        audit_path,
        pinder_dir,
        control_kind="human_heterodimer",
        top_n=1,
    )

    assert inputs == []


def test_prepare_baseline_inputs_raises_for_missing_pinder_sequence(
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    pl.DataFrame(
        [
            {
                "id": "some_other_id",
                "receptor_sequence": "A",
                "ligand_sequence": "C",
            }
        ]
    ).write_parquet(pinder_dir / "part.parquet")

    with pytest.raises(RuntimeError, match="Missing PINDER sequences"):
        runner.prepare_baseline_inputs(
            audit_path,
            pinder_dir,
            control_kind="human_heterodimer",
            top_n=1,
        )


def test_prepare_baseline_inputs_can_select_control_id(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    inputs = runner.prepare_baseline_inputs(
        audit_path,
        pinder_dir,
        control_kind="human_heterodimer",
        top_n=1,
        control_id="1abc__A1_P12345--1abc__B1_P12345",
    )

    assert len(inputs) == 1
    assert inputs[0]["id"] == "1abc__A1_P12345--1abc__B1_P12345"
    assert inputs[0]["control_kind"] == "human_heterodimer"


def test_prepare_baseline_inputs_rejects_missing_control_id(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.csv"
    write_audit(audit_path)

    pinder_dir = tmp_path / "pinder"
    pinder_dir.mkdir()
    write_pinder_data(pinder_dir / "part.parquet")

    with pytest.raises(ValueError, match="Control id not found"):
        runner.prepare_baseline_inputs(
            audit_path,
            pinder_dir,
            control_kind="human_heterodimer",
            top_n=1,
            control_id="missing_id",
        )


def test_load_existing_ids_reads_csv(tmp_path: Path) -> None:
    output = tmp_path / "results.parquet"
    pl.DataFrame([{"id": "already_done"}]).write_csv(output.with_suffix(".csv"))

    assert runner.load_existing_ids(output) == {"already_done"}


def test_drop_existing_inputs() -> None:
    inputs = [{"id": "keep"}, {"id": "skip"}]

    kept = runner.drop_existing_inputs(inputs, {"skip"})

    assert kept == [{"id": "keep"}]
