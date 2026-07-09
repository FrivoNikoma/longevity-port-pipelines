from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_one_row_non_committed_preflight_input_binding as binding,
)

ROOT = Path(__file__).resolve().parents[1]
DECISION_TABLE = ROOT / binding.DEFAULT_DECISION_TABLE
BINDING_TABLE = ROOT / binding.DEFAULT_BINDING_TABLE


def test_g3sx30_binding_table_has_one_valid_row() -> None:
    row = binding.load_and_validate_binding(BINDING_TABLE)

    assert row["candidate_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert row["target_accession"] == "G3SX30"
    assert row["target_species"] == "Loxodonta africana"
    assert row["target_taxid"] == "9785"
    assert row["gene_symbol"] == "MDM2"


def test_g3sx30_binding_can_be_rebuilt_from_decision_row() -> None:
    expected = binding.load_decision_and_build_binding(DECISION_TABLE)
    expected["source_decision_table"] = str(binding.DEFAULT_DECISION_TABLE).replace("\\", "/")
    actual = binding.load_and_validate_binding(BINDING_TABLE)

    assert actual == expected


def test_g3sx30_binding_records_non_committed_artifact_reference_only() -> None:
    row = binding.load_and_validate_binding(BINDING_TABLE)

    assert row["local_embedding_path"] == binding.EXPECTED_LOCAL_EMBEDDING_PATH
    assert row["artifact_location"] == "local_runtime_data_output_ignored_by_git"
    assert row["local_runtime_embedding_tracked"] == "false"
    assert row["local_runtime_embedding_committed"] == "false"
    assert row["non_committed_preflight_input_reference_created"] == "true"


def test_g3sx30_binding_keeps_downstream_gates_blocked() -> None:
    row = binding.load_and_validate_binding(BINDING_TABLE)

    assert row["approved_for_one_row_readiness_preflight_input"] == "true"
    assert row["ready_for_preflight"] == "false"
    assert row["gate8_promoted"] == "false"
    assert row["gate9_promoted"] == "false"
    assert row["biological_claim_made"] == "false"


def test_g3sx30_binding_names_next_concrete_check() -> None:
    row = binding.load_and_validate_binding(BINDING_TABLE)

    assert row["next_concrete_check"] == (
        "run_record_g3sx30_one_row_local_embedding_preflight_check"
    )
    assert row["next_check_scope"] == (
        "local_artifact_shape_dtype_finiteness_sequence_length_path_policy_only"
    )
    assert row["next_check_input"] == (
        "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1"
    )
    assert row["next_check_output_policy"] == "external_non_committed_observation_only"


def test_g3sx30_binding_rejects_unapproved_source_decision() -> None:
    decision_row = binding.read_one_row(DECISION_TABLE)
    bad_row = dict(decision_row)
    bad_row["approved_for_one_row_readiness_preflight_input"] = "false"

    with pytest.raises(ValueError, match="approved_for_one_row_readiness_preflight_input"):
        binding.build_binding_row(bad_row)


def test_g3sx30_binding_rejects_ready_for_preflight_promotion() -> None:
    row = binding.read_one_row(BINDING_TABLE)
    bad_row = dict(row)
    bad_row["ready_for_preflight"] = "true"

    with pytest.raises(ValueError, match="ready_for_preflight"):
        binding.validate_binding_row(bad_row)


def test_g3sx30_binding_rejects_gate_or_claim_promotion() -> None:
    row = binding.read_one_row(BINDING_TABLE)

    for field in ["gate8_promoted", "gate9_promoted", "biological_claim_made"]:
        bad_row = dict(row)
        bad_row[field] = "true"

        with pytest.raises(ValueError, match=field):
            binding.validate_binding_row(bad_row)


def test_g3sx30_binding_forbidden_actions_cover_runtime_and_claim_boundaries() -> None:
    row = binding.load_and_validate_binding(BINDING_TABLE)

    for forbidden in binding.EXPECTED_FORBIDDEN_ACTIONS:
        assert forbidden in row["forbidden_actions"]
