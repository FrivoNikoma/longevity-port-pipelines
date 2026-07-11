from __future__ import annotations

import csv
from pathlib import Path

import pytest

from longevity_port_pipelines.stages import (
    g3sx30_source_backed_human_mdm2_comparator_path as comparator,
)

ROOT = Path(__file__).resolve().parents[1]
COMPARATOR_TABLE = ROOT / comparator.DEFAULT_COMPARATOR_TABLE


def read_one_row(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        data = list(csv.DictReader(handle))
    assert len(data) == 1
    return data[0]


def test_comparator_table_has_one_valid_result_row() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["comparator_status"] == "source_backed_human_mdm2_comparator_path_created"
    assert item["comparator_type"] == (
        "human_elephant_mdm2_reference_identity_comparator_for_pairwise_embedding"
    )


def test_comparator_consumes_exact_human_reference_row() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["source_human_reference_table"] == "data/input/tp53_mdm2_pilot_manifest.csv"
    assert item["source_human_reference_row_index"] == "2"
    assert item["human_reference_accession"] == "Q00987"
    assert item["human_reference_pdb_id"] == "1ycr"
    assert item["human_reference_chain"] == "A"
    assert item["human_reference_partner_uniprot"] == "P04637"


def test_comparator_preserves_historical_repair_state() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["source_candidate_provenance_row_index"] == "2"
    assert item["source_historical_target_uniprot"] == "unresolved"
    assert item["source_historical_provenance_status"] == "unresolved"
    assert item["source_historical_repair_status"] == "pending"


def test_comparator_uses_later_g3sx30_reviewed_planning_row() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["source_elephant_review_decision_row_index"] == "1"
    assert item["source_elephant_review_decision"] == "accepted_for_planning_after_review"
    assert item["source_elephant_reviewed_target_uniprot"] == "G3SX30"
    assert item["source_elephant_reviewed_sequence_length"] == "492"
    assert item["source_elephant_review_downstream_status"] == (
        "reviewed_for_planning_still_policy_blocked"
    )


def test_comparator_traces_elephant_embedding_to_scalar_summary() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["source_elephant_scalar_summary_row_index"] == "1"
    assert item["source_elephant_summary_status"] == (
        "first_analysis_adjacent_controlled_embedding_summary_created"
    )
    assert item["elephant_embedding_available"] == "true"
    assert item["elephant_embedding_shape"] == "492x960"
    assert item["elephant_embedding_dtype"] == "float32"
    assert item["elephant_embedding_finite"] == "true"


def test_comparator_records_exact_human_embedding_blocker() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["human_reference_source_backed"] == "true"
    assert item["human_embedding_inspection_query"] == "Q00987_or_1ycr_exact_aliases"
    assert item["human_embedding_inspection_status"] == (
        "no_matching_local_runtime_embedding_found"
    )
    assert item["human_embedding_available"] == "false"
    assert item["pairwise_summary_created"] == "false"
    assert item["pairwise_blocker"] == "source_backed_human_mdm2_embedding_not_available"


def test_comparator_keeps_forbidden_side_effects_false() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    for field in comparator.FALSE_ONLY_FIELDS:
        assert item[field] == "false"


def test_comparator_points_directly_to_runtime_result_or_pairwise_summary() -> None:
    item = comparator.load_and_validate_comparator_path(COMPARATOR_TABLE)
    assert item["next_step"] == (
        "generate_source_backed_human_mdm2_embedding_and_create_first_pairwise_summary"
    )
    assert item["explicit_runtime_scope_required_for_next_step"] == "true"
    assert item["runtime_scope_must_be_encoded_in_result_bearing_step"] == "true"
    assert item["no_additional_comparator_approval_before_pairwise_result"] == "true"
    assert item["no_additional_comparator_review_before_pairwise_result"] == "true"
    assert item["no_additional_non_result_layer_before_next_concrete_step"] == "true"


def test_validator_rejects_human_embedding_available_without_result() -> None:
    item = read_one_row(COMPARATOR_TABLE)
    item["human_embedding_available"] = "true"
    with pytest.raises(ValueError, match="human_embedding_available"):
        comparator.validate_comparator_row(item)


def test_validator_rejects_pairwise_summary_creation_claim() -> None:
    item = read_one_row(COMPARATOR_TABLE)
    item["pairwise_summary_created"] = "true"
    with pytest.raises(ValueError, match="pairwise_summary_created"):
        comparator.validate_comparator_row(item)


def test_validator_rejects_biological_claim_promotion() -> None:
    item = read_one_row(COMPARATOR_TABLE)
    item["biological_claim_made"] = "true"
    with pytest.raises(ValueError, match="biological_claim_made"):
        comparator.validate_comparator_row(item)
