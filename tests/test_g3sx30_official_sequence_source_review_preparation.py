from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/g3sx30_official_sequence_source_review_preparation.md"
SOURCE_PROVENANCE_PATH = ROOT / "data/input/reviewed_target_sequence_provenance.csv"
DECISION_PATH = ROOT / "data/input/target_sequence_review_decisions.csv"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_g3sx30_official_sequence_source_review_preparation_doc_exists() -> None:
    text = read_doc()

    assert text.startswith("# G3SX30 official sequence source review preparation")
    assert "later possible G3SX30 reviewed target sequence provenance PR" in text
    assert "It does not perform the review itself." in text


def test_g3sx30_official_sequence_source_review_preparation_records_current_state() -> None:
    text = read_doc()

    for required in [
        "target accession: `G3SX30`",
        "accession database: `UniProtKB TrEMBL`",
        "target species: `Loxodonta africana`",
        "target taxid: `9785`",
        "gene symbol: `MDM2`",
        "expected metadata length from the Gate 4 / Gate 5 policy row: `492`",
        "source sequence provenance row: `data/input/reviewed_target_sequence_provenance.csv#1`",
        "target sequence review decision row: `data/input/target_sequence_review_decisions.csv#1`",
        "current sequence source type: `deferred_pending_review`",
        "current sequence length status: `not_fetched`",
        "current sequence review status: `deferred_pending_review`",
        "current provenance review status: `deferred`",
        "current sequence review decision: `defer_pending_sequence_review`",
        "current downstream block status after decision: `sequence_review_deferred_still_blocked`",
    ]:
        assert required in text


def test_g3sx30_official_sequence_source_review_preparation_requires_identity_checks() -> None:
    text = read_doc()

    for required in [
        "accession is exactly `G3SX30`",
        "accession database is exactly `UniProtKB TrEMBL`",
        "organism is elephant / `Loxodonta africana`",
        "taxid is exactly `9785`",
        "gene symbol is exactly `MDM2`",
        "not a paralog",
        "unrelated isoform",
        "wrong species record",
        "fragment-only artifact",
        "source record can be re-opened",
    ]:
        assert required in text

    assert "does not assert that the official source record has already been reviewed" in text


def test_g3sx30_official_sequence_source_review_preparation_requires_hash_and_length_checks() -> (
    None
):
    text = read_doc()

    for required in [
        "compute length and hash from the reviewed amino-acid sequence itself",
        "must not rely on metadata length alone",
        "explicit source reference",
        "stable `reviewed_sequence_sha256`",
        "`reviewed_sequence_length` computed directly",
        "direct length comparison to expected metadata length `492`",
        "explicit mismatch handling",
        "does not compute a hash",
        "does not compute a length",
        "does not record `sequence_length_status=matches`",
    ]:
        assert required in text


def test_g3sx30_official_sequence_source_review_preparation_records_mismatch_handling() -> None:
    text = read_doc()

    for required in [
        "`sequence_length_status=mismatch`",
        "`sequence_review_status=deferred_pending_review`",
        "`sequence_review_status=rejected_sequence_provenance`",
        "`provenance_review_status=needs_review`",
        "`provenance_review_status=rejected`",
        "`allowed_next_action_after_sequence_review=keep_blocked`",
        "`allowed_next_action_after_sequence_review=reject_or_exclude_sequence_source`",
        "`sequence_review_decision=keep_blocked_after_mismatch`",
        "`sequence_review_decision=reject_sequence_provenance`",
        "must not become `reviewed_sequence_provenance`",
        "`sequence_length_status=matches`",
        "`consider_later_dry_run_preflight_decision_pr`",
    ]:
        assert required in text


def test_g3sx30_official_sequence_source_review_preparation_forbids_runtime_side_effects() -> None:
    text = read_doc()

    for required in [
        "does not approve reviewed sequence provenance",
        "does not record `reviewed_sequence_provenance`",
        "does not record `sequence_length_status=matches`",
        "does not fetch sequences inside the repository",
        "does not commit a raw sequence artifact",
        "does not mutate `data/input/reviewed_target_sequence_provenance.csv`",
        "does not mutate `data/input/target_sequence_review_decisions.csv`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not run `curated_embedding_preflight`",
        "does not run `curated_embedding_single`",
        "does not change the G3SX30 controlled embedding-fill worklist row",
        "does not mark anything `ready_for_preflight`",
        "does not create or commit `.npy` artifacts",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_g3sx30_official_sequence_source_review_preparation_does_not_mutate_csv_rows() -> None:
    text = read_doc()

    source_provenance = SOURCE_PROVENANCE_PATH.read_text(encoding="utf-8")
    decisions = DECISION_PATH.read_text(encoding="utf-8")

    assert "deferred_pending_review" in source_provenance
    assert "not_fetched" in source_provenance
    assert "defer_pending_sequence_review" in decisions
    assert "sequence_review_deferred_still_blocked" in decisions
    assert "does not mutate `data/input/reviewed_target_sequence_provenance.csv`" in text
    assert "does not mutate `data/input/target_sequence_review_decisions.csv`" in text
