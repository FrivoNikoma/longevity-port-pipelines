import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv"


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_g3sx30_local_embedding_readiness_input_decision_has_one_row() -> None:
    rows = read_rows()

    assert len(rows) == 1
    assert rows[0]["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"


def test_g3sx30_local_embedding_readiness_input_decision_approves_input_reference_only() -> None:
    row = read_rows()[0]

    assert row["approved_for_one_row_readiness_preflight_input"] == "true"
    assert (
        row["readiness_preflight_input_record_status"]
        == "approved_local_runtime_artifact_as_one_row_readiness_preflight_input"
    )
    assert row["ready_for_preflight"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["biological_claim_made"] == "false"


def test_g3sx30_local_embedding_readiness_input_decision_records_artifact_status() -> None:
    row = read_rows()[0]

    assert row["local_runtime_embedding_exists"] == "true"
    assert row["local_runtime_embedding_tracked"] == "false"
    assert row["local_runtime_embedding_committed"] == "false"
    assert row["artifact_location"] == "local_runtime_data_output_ignored_by_git"
    assert (
        row["local_embedding_path"] == "data/output/embeddings/esmc-300m-2024-12/"
        "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
    )


def test_g3sx30_local_embedding_readiness_input_decision_records_validation_summary() -> None:
    row = read_rows()[0]

    assert row["embedding_shape"] == "492x960"
    assert row["embedding_dtype"] == "float32"
    assert row["embedding_finite"] == "true"
    assert row["sequence_length_matches"] == "true"
    assert row["validation_ready_for_preflight_promoted"] == "false"
    assert row["validation_gate8_promoted"] == "false"
    assert row["validation_gate9_promoted"] == "false"
    assert row["validation_biological_claim_made"] == "false"


def test_g3sx30_local_embedding_readiness_input_decision_keeps_forbidden_actions_blocked() -> None:
    row = read_rows()[0]

    forbidden = row["forbidden_actions"]
    for required in [
        "Biohub call",
        "ESMC call",
        "live embedding rerun",
        "embedding generation",
        ".npy commit",
        "data/output commit",
        "external FASTA commit",
        "external live log commit",
        "external validation JSON commit",
        "ready_for_preflight promotion",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "Boltz call",
        "AF3 call",
        "Chai call",
        "enrichment rerun",
        "contrast rerun",
        "biological claim",
    ]:
        assert required in forbidden
