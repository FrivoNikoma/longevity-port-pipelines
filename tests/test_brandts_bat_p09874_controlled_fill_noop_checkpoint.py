from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
WORKLIST_PATH = (
    ROOT / "data/interim/controlled_embedding_fill_worklist_brandts_bat_p09874_checkpoint.csv"
)
DOC_PATH = ROOT / "docs/brandts_bat_p09874_controlled_fill_noop_checkpoint.md"


def read_worklist() -> pl.DataFrame:
    return pl.read_csv(WORKLIST_PATH)


def test_brandts_bat_p09874_noop_checkpoint_exists() -> None:
    assert WORKLIST_PATH.exists()
    assert DOC_PATH.exists()


def test_brandts_bat_p09874_noop_checkpoint_has_one_present_embedding_row() -> None:
    worklist = read_worklist()

    assert worklist.height == 1

    row = worklist.row(0, named=True)

    assert row["candidate_set"] == "sirt6_dna_repair"
    assert row["lane_name"] == "SIRT6/core3"
    assert row["source_uniprot"] == "P09874"
    assert row["target_species"] == "brandts_bat"
    assert row["target_species_taxid"] == 109478
    assert row["target_accession"] == "EPQ16369.1"
    assert row["sequence_length_status"] == "matches"
    assert row["embedding_exists"] is True
    assert row["embedding_status"] == "present"


def test_brandts_bat_p09874_noop_checkpoint_does_not_select_live_fill() -> None:
    row = read_worklist().row(0, named=True)

    assert row["fill_status"] == "do_not_fill"
    assert row["allowed_next_action"] == "do_not_fill"
    assert row["dry_run_required"] is False
    assert row["live_opt_in_required"] is True
    assert row["max_live_batch_size"] == 0
    assert row["claim_policy"] == "no_biological_claims_until_validation"
    assert row["claim_status"] == "technical_checkpoint"


def test_brandts_bat_p09874_noop_checkpoint_records_forbidden_actions() -> None:
    row = read_worklist().row(0, named=True)

    assert "Biohub call" in row["forbidden_actions"]
    assert "embedding generation" in row["forbidden_actions"]
    assert "data/output commit" in row["forbidden_actions"]
    assert "Boltz call" in row["forbidden_actions"]
    assert "enrichment rerun" in row["forbidden_actions"]
    assert "contrast rerun" in row["forbidden_actions"]
    assert "biological claim" in row["forbidden_actions"]


def test_brandts_bat_p09874_noop_checkpoint_doc_records_no_live_claims() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "no-op fill checkpoint" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not commit `data/output/` artifacts" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment/contrast" in text
    assert "does not make biological claims" in text
    assert "does not select a missing embedding for fill" in text
