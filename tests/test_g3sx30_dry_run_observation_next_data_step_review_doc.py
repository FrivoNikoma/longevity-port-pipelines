from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_dry_run_observation_next_data_step_review.md"


def test_g3sx30_dry_run_observation_next_data_step_review_doc_records_source() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert (
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json"
    ) in text
    assert "external JSON observation remains outside the repository and is not committed" in text
    assert "docs/g3sx30_wrapper_dry_run_observation_checkpoint.md" in text
    assert "It does not rerun the dry-run." in text


def test_g3sx30_dry_run_observation_next_data_step_review_doc_records_review() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "dry_run_observation_reviewed = true",
        "dry_run_observation_blocker_found = false",
        "dry_run_executed = true",
        "manifest_row_index = 1",
        "target_accession = G3SX30",
        "target_taxid = 9785",
        "reviewed_sequence_length = 492",
        "reviewed_sequence_sha256 = e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "manifest_row_read = true",
        "manifest_row_validated = true",
        "biohub_esmc_called = false",
        "embedding_generation_performed = false",
        "npy_artifact_created = false",
        "data_output_artifact_created = false",
        "ready_for_preflight_promoted = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "No concrete blocker is recorded in the observed dry-run JSON.",
    ]:
        assert required in text


def test_g3sx30_dry_run_observation_next_data_step_review_doc_records_decision() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "next_data_step_decision = approve_one_row_live_embedding_for_next_pr",
        "live_embedding_authorized_for_next_pr = true",
        "live_embedding_authorized_in_this_pr = false",
        "max_live_batch_size_for_next_pr = 1",
        "ready_for_preflight_authorized = false",
        "gate8_promotion_authorized = false",
        "gate9_promotion_authorized = false",
        "biological_claim_authorized = false",
        "allowed_next_action_after_review = execute_one_row_g3sx30_live_embedding_with_strict_guardrails",
        "claim_status = technical_checkpoint",
        "This is a direct approval for the next PR",
        "It is not approval for live execution in this PR.",
    ]:
        assert required in text


def test_g3sx30_dry_run_observation_next_data_step_review_doc_records_next_pr_guardrails() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "Execute one-row G3SX30 live embedding with strict guardrails",
        "one row only",
        "manifest row #1 only",
        "explicit live opt-in required",
        "max_live_batch_size = 1",
        "local runtime artifact only",
        "no committed .npy artifact",
        "no committed data/output artifact",
        "no ready_for_preflight promotion",
        "no Gate 8 promotion",
        "no Gate 9 promotion",
        "no Boltz / AF3 / Chai call",
        "no enrichment rerun",
        "no contrast rerun",
        "no biological claim",
    ]:
        assert required in text


def test_g3sx30_dry_run_observation_next_data_step_review_doc_keeps_current_pr_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for forbidden in [
        "rerun `g3sx30-wrapper-dry-run`",
        "call Biohub / ESMC",
        "generate embeddings",
        "create `.npy` artifacts",
        "create or commit `data/output` artifacts",
        "run a live path",
        "promote `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make biological claims",
    ]:
        assert forbidden in text

    assert "Brandt's bat live embedding precedent" in text
    assert "local runtime artifact" in text
