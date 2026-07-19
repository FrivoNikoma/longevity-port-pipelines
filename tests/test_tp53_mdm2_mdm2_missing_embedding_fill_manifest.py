import copy
from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_missing_embedding_fill_manifest as contract,
)

ROOT = Path(__file__).resolve().parents[1]


def load_contract() -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
]:
    return contract.load_and_validate_committed_contract(
        ROOT / contract.DEFAULT_MANIFEST_TABLE,
        ROOT / contract.DEFAULT_VALIDATION_RESULT_TABLE,
        ROOT / contract.DEFAULT_EXTERNAL_BINDING_TABLE,
        ROOT / contract.DEFAULT_LOCAL_PREREQUISITE_TABLE,
    )


def test_manifest_has_exactly_two_expected_rows() -> None:
    manifest, _ = load_contract()
    assert [row["target_accession"] for row in manifest] == [
        "P23804",
        "A0ABM2YB85",
    ]


def test_manifest_binds_exact_taxids_lengths_and_hashes() -> None:
    manifest, _ = load_contract()
    by_accession = {row["target_accession"]: row for row in manifest}
    for accession, expected in contract.EXPECTED_ACCESSIONS.items():
        row = by_accession[accession]
        assert row["target_taxid"] == expected["target_taxid"]
        assert row["expected_sequence_length"] == expected["expected_sequence_length"]
        assert (
            row["exact_normalized_sequence_sha256"] == expected["exact_normalized_sequence_sha256"]
        )


def test_manifest_binds_passed_external_sources() -> None:
    manifest, _ = load_contract()
    for row in manifest:
        assert row["external_binding_status"] == ("passed_exact_external_non_committed_binding")
        assert row["external_binding_root_env"] == contract.BINDING_ROOT_ENV
        assert row["external_binding_root_required_for_ci"] == "false"


def test_manifest_binds_missing_local_prerequisites() -> None:
    manifest, _ = load_contract()
    for row in manifest:
        assert row["local_prerequisite_status"] == "missing"
        assert row["existing_local_embedding_status"] == "missing"
        assert row["existing_local_embedding_exists"] == "false"
        assert row["existing_local_embedding_tracked"] == "false"
        assert row["existing_local_embedding_committed"] == "false"


def test_declared_embedding_paths_are_portable_and_ignored() -> None:
    manifest, _ = load_contract()
    for row in manifest:
        path = row["expected_local_embedding_path"]
        assert path.startswith("data/output/embeddings/esmc-300m-2024-12/")
        assert path.endswith(".npy")
        assert not Path(path).is_absolute()
        assert "\\" not in path
        assert ".." not in Path(path).parts
        assert row["expected_local_embedding_path_policy_status"] == ("data_output_ignored")
        assert row["embedding_path_declared_only"] == "true"


def test_manifest_blocks_live_fill_and_execution() -> None:
    manifest, _ = load_contract()
    for row in manifest:
        assert row["fill_status"] == ("planning_policy_updated_runtime_blocked")
        assert row["live_fill_allowed"] == "false"
        assert row["fill_execution_allowed"] == "false"
        assert row["live_opt_in_required"] == "true"
        assert row["max_live_batch_size"] == "0"
        assert row["authorization_status"] == ("pending_explicit_scoped_live_fill_authorization")


def test_contract_validation_does_not_require_external_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(contract.BINDING_ROOT_ENV, raising=False)
    manifest, validation = load_contract()
    assert len(manifest) == 2
    assert len(validation) == 2


def test_validation_result_records_execution_contract_only() -> None:
    _, validation = load_contract()
    for row in validation:
        assert row["manifest_validation_status"] == ("passed_table_only_validation")
        assert row["scoped_missing_embedding_fill_manifest_status"] == (
            "prepared_execution_contract_only"
        )
        assert row["embedding_artifact_status"] == "missing_not_created"
        assert row["allowed_next_action"] == ("request_explicit_scoped_live_fill_authorization")


def test_all_runtime_and_downstream_flags_remain_false() -> None:
    manifest, validation = load_contract()
    for row in manifest:
        for field in contract.MANIFEST_FALSE_FIELDS:
            assert row[field] == "false"
    for row in validation:
        for field in contract.VALIDATION_FALSE_FIELDS:
            assert row[field] == "false"


def test_manifest_rejects_live_fill_authorization() -> None:
    manifest, _ = load_contract()
    external = contract.read_csv_rows(ROOT / contract.DEFAULT_EXTERNAL_BINDING_TABLE)
    local = contract.read_csv_rows(ROOT / contract.DEFAULT_LOCAL_PREREQUISITE_TABLE)
    bad = copy.deepcopy(manifest)
    bad[0]["live_fill_allowed"] = "true"
    with pytest.raises(ValueError, match="live_fill_allowed"):
        contract.validate_manifest_rows(bad, external, local)


def test_manifest_rejects_wrong_embedding_path() -> None:
    manifest, _ = load_contract()
    external = contract.read_csv_rows(ROOT / contract.DEFAULT_EXTERNAL_BINDING_TABLE)
    local = contract.read_csv_rows(ROOT / contract.DEFAULT_LOCAL_PREREQUISITE_TABLE)
    bad = copy.deepcopy(manifest)
    bad[0]["expected_local_embedding_path"] = "D:/external/P23804.npy"
    with pytest.raises(ValueError, match="embedding path"):
        contract.validate_manifest_rows(bad, external, local)


def test_raw_sequence_artifacts_are_not_committed_here() -> None:
    forbidden_names = {
        "P23804.fasta",
        "P23804.sequence.txt",
        "A0ABM2YB85.fasta",
        "A0ABM2YB85.sequence.txt",
        "tp53_mdm2_mdm2_external_exact_sequence_bindings.json",
    }
    found = {
        path.name for path in ROOT.rglob("*") if path.is_file() and path.name in forbidden_names
    }
    assert found == set()
