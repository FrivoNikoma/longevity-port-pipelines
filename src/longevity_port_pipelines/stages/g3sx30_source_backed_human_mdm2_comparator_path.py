"""Validate the first source-backed human MDM2 comparator/blocker result.

The committed row records reference identity and embedding availability only.
It does not claim orthology, functional equivalence, an interface or binding
result, beneficial breakage, or longevity evidence.
"""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_HUMAN_REFERENCE_TABLE = Path("data/input/tp53_mdm2_pilot_manifest.csv")
DEFAULT_HISTORICAL_REPAIR_TABLE = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")
DEFAULT_ELEPHANT_REVIEW_TABLE = Path("data/input/ortholog_evidence_review_decisions.csv")
DEFAULT_ELEPHANT_SUMMARY_TABLE = Path(
    "data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv"
)
DEFAULT_COMPARATOR_TABLE = Path("data/input/g3sx30_source_backed_human_mdm2_comparator_paths.csv")
EXPECTED_ELEPHANT_EMBEDDING_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_NEXT_STEP = "generate_source_backed_human_mdm2_embedding_and_create_first_pairwise_summary"

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_human_reference_table": "data/input/tp53_mdm2_pilot_manifest.csv",
    "source_human_reference_row_index": "2",
    "source_human_reference_pdb_id": "1ycr",
    "source_human_reference_chain": "A",
    "source_human_reference_accession": "Q00987",
    "source_human_reference_partner_uniprot": "P04637",
    "source_candidate_provenance_table": "data/input/tp53_mdm2_ortholog_repair_decisions.csv",
    "source_candidate_provenance_row_index": "2",
    "source_historical_target_uniprot": "unresolved",
    "source_historical_provenance_status": "unresolved",
    "source_historical_repair_status": "pending",
    "source_elephant_review_decision_table": "data/input/ortholog_evidence_review_decisions.csv",
    "source_elephant_review_decision_row_index": "1",
    "source_elephant_review_decision": "accepted_for_planning_after_review",
    "source_elephant_reviewed_target_uniprot": "G3SX30",
    "source_elephant_reviewed_source_database": "UniProtKB TrEMBL",
    "source_elephant_reviewed_sequence_length": "492",
    "source_elephant_reviewed_taxid": "9785",
    "source_elephant_review_downstream_status": "reviewed_for_planning_still_policy_blocked",
    "source_elephant_review_claim_status": "repair_worklist",
    "source_elephant_scalar_summary_table": (
        "data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv"
    ),
    "source_elephant_scalar_summary_row_index": "1",
    "source_elephant_summary_status": "first_analysis_adjacent_controlled_embedding_summary_created",
    "source_elephant_summary_type": "one_row_embedding_scalar_summary_statistics",
    "source_elephant_embedding_artifact_reference": EXPECTED_ELEPHANT_EMBEDDING_REFERENCE,
    "source_elephant_embedding_shape": "492x960",
    "source_elephant_embedding_dtype": "float32",
    "source_elephant_embedding_finite": "true",
    "comparator_status": "source_backed_human_mdm2_comparator_path_created",
    "comparator_type": "human_elephant_mdm2_reference_identity_comparator_for_pairwise_embedding",
    "comparator_scope": "reference_identity_and_embedding_availability_only_no_biological_claim",
    "human_reference_source_backed": "true",
    "human_reference_source_scope": "committed_pilot_manifest_reference_identity",
    "human_reference_accession": "Q00987",
    "human_reference_species": "Homo sapiens",
    "human_reference_taxid": "9606",
    "human_reference_gene_symbol": "MDM2",
    "human_reference_pdb_id": "1ycr",
    "human_reference_chain": "A",
    "human_reference_partner_uniprot": "P04637",
    "human_reference_sequence_provenance_status": "not_consumed_by_this_comparator_result",
    "human_embedding_inspection_method": "manual_local_data_output_recursive_npy_filename_search",
    "human_embedding_inspection_query": "Q00987_or_1ycr_exact_aliases",
    "human_embedding_inspection_status": "no_matching_local_runtime_embedding_found",
    "human_embedding_available": "false",
    "human_embedding_artifact_reference": "not_available_no_q00987_or_1ycr_local_runtime_embedding_found",
    "elephant_target_accession": "G3SX30",
    "elephant_target_database": "UniProtKB TrEMBL",
    "elephant_target_species": "Loxodonta africana",
    "elephant_target_taxid": "9785",
    "elephant_target_gene_symbol": "MDM2",
    "elephant_embedding_available": "true",
    "elephant_embedding_artifact_reference": EXPECTED_ELEPHANT_EMBEDDING_REFERENCE,
    "elephant_embedding_shape": "492x960",
    "elephant_embedding_dtype": "float32",
    "elephant_embedding_finite": "true",
    "pairwise_summary_created": "false",
    "pairwise_blocker": "source_backed_human_mdm2_embedding_not_available",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "data_output_artifact_committed": "false",
    "biohub_esmc_called_by_comparator_path": "false",
    "live_embedding_rerun_by_comparator_path": "false",
    "embedding_generation_performed_by_comparator_path": "false",
    "npy_artifact_created_by_comparator_path": "false",
    "raw_embedding_values_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "enrichment_rerun": "false",
    "contrast_rerun": "false",
    "next_step": EXPECTED_NEXT_STEP,
    "explicit_runtime_scope_required_for_next_step": "true",
    "runtime_scope_must_be_encoded_in_result_bearing_step": "true",
    "no_additional_comparator_approval_before_pairwise_result": "true",
    "no_additional_comparator_review_before_pairwise_result": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
}

FALSE_ONLY_FIELDS = (
    "human_embedding_available",
    "pairwise_summary_created",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "data_output_artifact_committed",
    "biohub_esmc_called_by_comparator_path",
    "live_embedding_rerun_by_comparator_path",
    "embedding_generation_performed_by_comparator_path",
    "npy_artifact_created_by_comparator_path",
    "raw_embedding_values_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "enrichment_rerun",
    "contrast_rerun",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_row(path: Path, one_based_index: int) -> dict[str, str]:
    data = read_csv_rows(path)
    if not 1 <= one_based_index <= len(data):
        raise ValueError(f"Expected row {one_based_index} in {path}, found {len(data)} rows")
    return data[one_based_index - 1]


def require_single_row(path: Path) -> dict[str, str]:
    data = read_csv_rows(path)
    if len(data) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(data)}")
    return data[0]


def validate_source_rows(item: dict[str, str]) -> None:
    human = require_row(
        DEFAULT_HUMAN_REFERENCE_TABLE, int(item["source_human_reference_row_index"])
    )
    for field, expected in {
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "pdb_id": "1ycr",
        "chain": "A",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "claim_policy": "technical_checkpoint_no_claim",
    }.items():
        if human.get(field) != expected:
            raise ValueError(
                f"Human source row expected {field}={expected!r}, got {human.get(field)!r}"
            )

    repair = require_row(
        DEFAULT_HISTORICAL_REPAIR_TABLE, int(item["source_candidate_provenance_row_index"])
    )
    for field, expected in {
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "source_uniprot": "Q00987",
        "target_uniprot": "unresolved",
        "provenance_status": "unresolved",
        "repair_status": "pending",
    }.items():
        if repair.get(field) != expected:
            raise ValueError(
                f"Historical source row expected {field}={expected!r}, got {repair.get(field)!r}"
            )

    review = require_row(
        DEFAULT_ELEPHANT_REVIEW_TABLE, int(item["source_elephant_review_decision_row_index"])
    )
    for field, expected in {
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "source_uniprot": "Q00987",
        "review_decision": "accepted_for_planning_after_review",
        "reviewed_target_uniprot": "G3SX30",
        "reviewed_source_database": "UniProtKB TrEMBL",
        "reviewed_sequence_length": "492",
        "reviewed_taxid": "9785",
        "downstream_block_status_after_review": "reviewed_for_planning_still_policy_blocked",
    }.items():
        if review.get(field) != expected:
            raise ValueError(
                f"Elephant review row expected {field}={expected!r}, got {review.get(field)!r}"
            )

    summary = require_row(
        DEFAULT_ELEPHANT_SUMMARY_TABLE, int(item["source_elephant_scalar_summary_row_index"])
    )
    for field, expected in {
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession": "G3SX30",
        "summary_status": "first_analysis_adjacent_controlled_embedding_summary_created",
        "source_ready_artifact_reference": EXPECTED_ELEPHANT_EMBEDDING_REFERENCE,
        "source_embedding_shape": "492x960",
        "source_embedding_dtype": "float32",
        "source_embedding_finite": "true",
        "biological_claim_made": "false",
    }.items():
        if summary.get(field) != expected:
            raise ValueError(
                f"Elephant summary row expected {field}={expected!r}, got {summary.get(field)!r}"
            )


def validate_comparator_row(item: dict[str, str]) -> None:
    for field, expected in EXPECTED_VALUES.items():
        if item.get(field) != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {item.get(field)!r}")
    for field in FALSE_ONLY_FIELDS:
        if item.get(field) != "false":
            raise ValueError(f"Expected {field}='false'")
    if item["human_embedding_artifact_reference"].lower().endswith(".npy"):
        raise ValueError("Human embedding artifact reference must remain unavailable")
    if (
        item["elephant_embedding_artifact_reference"]
        != item["source_elephant_embedding_artifact_reference"]
    ):
        raise ValueError("Elephant embedding reference must trace to scalar-summary source")
    forbidden = item.get("forbidden_actions", "")
    for required in [
        "Biohub call",
        "ESMC call",
        "live embedding rerun",
        "embedding generation",
        ".npy commit",
        "raw embedding value commit",
        "data/output commit",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "Boltz call",
        "AF3 call",
        "Chai call",
        "enrichment rerun",
        "contrast rerun",
        "biological claim",
    ]:
        if required not in forbidden:
            raise ValueError(f"Missing forbidden action: {required}")


def load_and_validate_comparator_path(path: Path = DEFAULT_COMPARATOR_TABLE) -> dict[str, str]:
    item = require_single_row(path)
    validate_comparator_row(item)
    validate_source_rows(item)
    return item
