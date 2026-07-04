from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/g3sx30_blocked_embedding_fill_exit_criteria.md"
CSV_PATH = ROOT / "data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_g3sx30_blocked_embedding_fill_exit_criteria_doc_exists() -> None:
    text = read_doc()

    assert "G3SX30 blocked embedding-fill exit criteria" in text
    assert "data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv" in text
    assert "data/input/ortholog_evidence_gate45_policy_updates.csv#1" in text
    assert "docs-only review protocol" in text
    assert "does not change the committed G3SX30 row" in text
    assert "does not run any embedding-fill workflow" in text


def test_g3sx30_exit_criteria_preserve_current_blocked_row() -> None:
    text = read_doc()
    worklist = pl.read_csv(CSV_PATH)
    row = worklist.row(0, named=True)

    assert worklist.height == 1
    assert row["fill_status"] == "planning_policy_updated_runtime_blocked"
    assert row["allowed_next_action"] == "keep_blocked"
    assert row["dry_run_required"] is False
    assert row["max_live_batch_size"] == 0
    assert row["sequence_length_status"] == "not_fetched"
    assert row["embedding_path"] == "not_applicable_runtime_blocked"
    assert ".npy" not in row["embedding_path"]

    assert f"fill_status={row['fill_status']}" in text
    assert f"allowed_next_action={row['allowed_next_action']}" in text
    assert f"dry_run_required={str(row['dry_run_required']).lower()}" in text
    assert f"max_live_batch_size={row['max_live_batch_size']}" in text
    assert f"sequence_length_status={row['sequence_length_status']}" in text
    assert f"embedding_path={row['embedding_path']}" in text


def test_g3sx30_exit_criteria_reject_non_exit_signals() -> None:
    text = read_doc()

    for phrase in [
        "a metadata-only UniProtKB row",
        "a raw metadata response row",
        "a stronger-source collection row",
        "a reviewed-for-planning provenance decision by itself",
        "a Gate 4 / Gate 5 planning-policy update by itself",
        "a blocked controlled embedding-fill worklist row by itself",
        "target_sequence_length=492",
        "sequence_length_status=not_fetched",
        "an ordinary preflight row emitted without explicit policy context",
        "a desire to spend compute credits",
    ]:
        assert phrase in text

    assert "None of those signals make G3SX30 embedding-ready" in text
    assert "Gate 8 eligible" in text
    assert "Gate 9 eligible" in text
    assert "Boltz-ready" in text
    assert "claim-ready" in text


def test_g3sx30_exit_criteria_require_later_reviewed_sequence_provenance() -> None:
    text = read_doc()

    for phrase in [
        "A later PR may only consider moving G3SX30 toward a dry-run preflight decision",
        "A reviewed target sequence provenance artifact exists for G3SX30",
        "reviewed target sequence source, accession, species, taxid, and length",
        "sequence_length_status=matches",
        "keeps live Biohub / ESMC calls disabled by default",
        "keeps `curated_embedding_single` and any live fill out of scope",
        "no Gate 8 promotion",
        "no Gate 9 promotion",
        "no Boltz readiness",
        "no biological claim",
    ]:
        assert phrase in text


def test_g3sx30_exit_criteria_forbid_runtime_side_effects() -> None:
    text = read_doc()

    for phrase in [
        "change the G3SX30 worklist row to `ready_for_preflight`",
        "change the G3SX30 worklist row to `reviewed_for_single_live_fill`",
        "run `curated_embedding_preflight`",
        "run `curated_embedding_single`",
        "fetch sequences",
        "call Biohub / ESMC",
        "generate embeddings",
        "create or commit `.npy` artifacts",
        "promote Gate 8",
        "promote Gate 9",
        "call Boltz, AF3, or Chai",
        "rerun enrichment or contrast",
        "make biological claims",
    ]:
        assert phrase in text

    assert "maximum claim status for this checkpoint is `technical_checkpoint`" in text
