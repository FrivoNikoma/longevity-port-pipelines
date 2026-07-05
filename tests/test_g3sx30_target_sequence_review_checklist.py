from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST_PATH = ROOT / "docs/g3sx30_target_sequence_review_checklist.md"


def read_checklist() -> str:
    return CHECKLIST_PATH.read_text(encoding="utf-8")


def test_g3sx30_target_sequence_review_checklist_records_current_blocked_state() -> None:
    text = read_checklist()

    assert "G3SX30 target sequence review checklist" in text
    assert "deferred_pending_review" in text
    assert "reviewed_sequence_length=0" in text
    assert "sequence_length_status=not_fetched" in text
    assert "sequence_review_status=deferred_pending_review" in text
    assert "provenance_review_status=deferred" in text
    assert "allowed_next_action_after_sequence_review=defer_pending_sequence_review" in text
    assert "claim_status=repair_worklist" in text


def test_g3sx30_target_sequence_review_checklist_requires_source_traceability() -> None:
    text = read_checklist()

    assert "data/input/ortholog_evidence_gate45_policy_updates.csv" in text
    assert "source row index: `1`" in text
    assert "candidate set: `tp53_mdm2_elephant`" in text
    assert "lane name: `tp53_mdm2_elephant`" in text
    assert "candidate id: `tp53_mdm2_elephant_seed_mdm2_chain`" in text
    assert "still runtime-blocked" in text


def test_g3sx30_target_sequence_review_checklist_requires_identity_checks() -> None:
    text = read_checklist()

    assert "target accession is exactly `G3SX30`" in text
    assert "accession database is exactly `UniProtKB TrEMBL`" in text
    assert "target species is elephant / `Loxodonta africana`" in text
    assert "target taxid is exactly `9785`" in text
    assert "gene symbol is exactly `MDM2`" in text
    assert "not a paralog" in text
    assert "wrong species record" in text


def test_g3sx30_target_sequence_review_checklist_requires_sequence_artifact_checks() -> None:
    text = read_checklist()

    assert "must not rely on metadata length alone" in text
    assert "concrete reviewed sequence artifact" in text
    assert "sequence source reference is explicit and reproducible" in text
    assert "reviewed_sequence_sha256" in text
    assert "reviewed_sequence_length` is computed from the reviewed sequence itself" in text
    assert "sequence_length_status=matches" in text
    assert "expected metadata length from the Gate 4 / Gate 5 policy row is `492`" in text
    assert "not a reviewed sequence artifact" in text


def test_g3sx30_target_sequence_review_checklist_requires_mismatch_handling() -> None:
    text = read_checklist()

    assert "Required mismatch handling" in text
    assert "sequence_length_status=mismatch" in text
    assert "sequence_review_status=rejected_sequence_provenance" in text
    assert "provenance_review_status=needs_review" in text
    assert "allowed_next_action_after_sequence_review=keep_blocked" in text
    assert "allowed_next_action_after_sequence_review=reject_or_exclude_sequence_source" in text
    assert "must not be converted into `consider_later_dry_run_preflight_decision_pr`" in text


def test_g3sx30_target_sequence_review_checklist_preserves_later_preflight_boundary() -> None:
    text = read_checklist()

    assert "dry-run embedding preflight" in text
    assert "separate from dry-run embedding preflight" in text
    assert "consider_later_dry_run_preflight_decision_pr" in text
    assert "does not authorize live calls or embedding generation" in text


def test_g3sx30_target_sequence_review_checklist_forbids_runtime_side_effects() -> None:
    text = read_checklist()

    for forbidden in [
        "sequence fetch",
        "Biohub calls",
        "ESMC calls",
        "embedding generation",
        "`curated_embedding_preflight`",
        "`curated_embedding_single`",
        "data/output commits",
        "`.npy` artifacts",
        "Gate 8 eligibility",
        "Gate 9 eligibility",
        "Boltz calls",
        "AF3 calls",
        "Chai calls",
        "enrichment rerun",
        "contrast rerun",
        "biological claims",
    ]:
        assert forbidden in text


def test_g3sx30_target_sequence_review_checklist_records_allowed_and_disallowed_language() -> None:
    text = read_checklist()

    assert "target sequence review checklist" in text
    assert "sequence provenance pending review" in text
    assert "still blocked pending explicit later sequence review" in text
    assert "ready for preflight" in text
    assert "validated longevity signal" in text
    assert "confirmed functional effect" in text
    assert "safe to port" in text
