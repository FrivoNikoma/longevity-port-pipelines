"""Validate and reproduce the first human-elephant MDM2 pairwise embedding summary.

The committed row is a numerical embedding-space comparison only. It uses
independent mean pooling over the residue axis and does not perform residue
alignment or claim an interface, binding, orthology, functional equivalence,
longevity evidence, or any other biological result.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DEFAULT_SOURCE_COMPARATOR_TABLE = Path(
    "data/input/g3sx30_source_backed_human_mdm2_comparator_paths.csv"
)
DEFAULT_PAIRWISE_SUMMARY_TABLE = Path(
    "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
)

EXPECTED_HUMAN_EMBEDDING_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy"
)
EXPECTED_ELEPHANT_EMBEDDING_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_comparator_table": ("data/input/g3sx30_source_backed_human_mdm2_comparator_paths.csv"),
    "source_comparator_row_index": "1",
    "source_comparator_status": "source_backed_human_mdm2_comparator_path_created",
    "source_comparator_blocker": "source_backed_human_mdm2_embedding_not_available",
    "source_elephant_scalar_summary_table": (
        "data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv"
    ),
    "source_elephant_scalar_summary_row_index": "1",
    "human_runtime_input_role": ("human_MDM2_Q00987_reference_self_embedding_runtime_input"),
    "human_runtime_input_storage_scope": ("external_non_committed_runtime_csv_outside_repo"),
    "human_runtime_input_csv_sha256": (
        "d86bf792c538a066d6085e69d3d0f0a1744e7dc5de2a7f179c3198d2e828b8fd"
    ),
    "human_fasta_storage_scope": "external_non_committed_fasta_outside_repo",
    "human_fasta_file_sha256": ("75573e90db2ef66e0acb952bd29883e8f04c98d5828405fc4fe8368420fd0496"),
    "human_sequence_fetch_scope": ("public_uniprot_q00987_fasta_outside_repo_before_live_step"),
    "human_sequence_fetch_performed_before_live_step": "true",
    "human_sequence_fetch_performed_by_live_step": "false",
    "human_accession": "Q00987",
    "human_accession_db": "UniProtKB Swiss-Prot",
    "human_species": "Homo sapiens",
    "human_taxid": "9606",
    "human_gene_symbol": "MDM2",
    "human_sequence_length": "491",
    "human_sequence_sha256": ("77ed25650e717b3f610e42ef8e5c1c88d50e7485725032f8535448a0ca8b61b1"),
    "human_embedding_generated": "true",
    "human_embedding_artifact_reference": EXPECTED_HUMAN_EMBEDDING_REFERENCE,
    "human_embedding_shape": "491x960",
    "human_embedding_dtype": "float32",
    "human_embedding_finite": "true",
    "human_embedding_artifact_committed": "false",
    "elephant_accession": "G3SX30",
    "elephant_accession_db": "UniProtKB TrEMBL",
    "elephant_species": "Loxodonta africana",
    "elephant_taxid": "9785",
    "elephant_gene_symbol": "MDM2",
    "elephant_sequence_length": "492",
    "elephant_embedding_reused": "true",
    "elephant_embedding_artifact_reference": EXPECTED_ELEPHANT_EMBEDDING_REFERENCE,
    "elephant_embedding_shape": "492x960",
    "elephant_embedding_dtype": "float32",
    "elephant_embedding_finite": "true",
    "elephant_embedding_artifact_committed": "false",
    "embedding_dimension_matches": "true",
    "mean_pooling_used": "true",
    "mean_pooling_axis": "residue_axis",
    "mean_pooled_vector_dimension": "960",
    "metric_calculation_dtype": "float64",
    "metric_decimal_places": "16",
    "human_mean_vector_l2_norm": "0.8317611517806080",
    "elephant_mean_vector_l2_norm": "0.8347860929210978",
    "mean_pooled_cosine_similarity": "0.9973314302339468",
    "mean_pooled_cosine_distance": "0.0026685697660532",
    "mean_pooled_euclidean_distance": "0.0609504211067301",
    "pairwise_summary_status": ("first_human_elephant_mdm2_mean_pooled_embedding_summary_created"),
    "pairwise_summary_type": ("human_elephant_mdm2_mean_pooled_embedding_space_comparison"),
    "pairwise_summary_scope": ("numerical_embedding_space_comparison_only_no_biological_claim"),
    "pairwise_summary_created": "true",
    "pairwise_blocker": "none_first_pairwise_summary_created",
    "external_pairwise_result_sha256": (
        "e54a31e9aafa7d09c496007a0b4e8fdabc665f5582f1d3978b5d46849e581687"
    ),
    "biohub_esmc_live_execution_count": "1",
    "live_execution_status": "live_completed",
    "live_scope_accession_count": "1",
    "additional_accessions_embedded": "false",
    "batch_run_performed": "false",
    "residue_alignment_performed": "false",
    "interface_analysis_performed": "false",
    "binding_analysis_performed": "false",
    "orthology_proof_created": "false",
    "functional_equivalence_claimed": "false",
    "longevity_evidence_claimed": "false",
    "raw_sequence_committed": "false",
    "fasta_committed": "false",
    "runtime_csv_committed": "false",
    "npy_artifact_committed": "false",
    "raw_embedding_values_committed": "false",
    "data_output_artifact_committed": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "enrichment_rerun": "false",
    "contrast_rerun": "false",
    "next_step": ("add_first_controlled_pairwise_embedding_robustness_check_before_interpretation"),
    "no_biological_interpretation_before_control": "true",
    "no_additional_runtime_approval_layer": "true",
    "no_additional_embedding_generation_only_layer": "true",
    "result_date": "2026-07-12",
}

FALSE_ONLY_FIELDS = (
    "human_sequence_fetch_performed_by_live_step",
    "human_embedding_artifact_committed",
    "elephant_embedding_artifact_committed",
    "additional_accessions_embedded",
    "batch_run_performed",
    "residue_alignment_performed",
    "interface_analysis_performed",
    "binding_analysis_performed",
    "orthology_proof_created",
    "functional_equivalence_claimed",
    "longevity_evidence_claimed",
    "raw_sequence_committed",
    "fasta_committed",
    "runtime_csv_committed",
    "npy_artifact_committed",
    "raw_embedding_values_committed",
    "data_output_artifact_committed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "boltz_called",
    "af3_called",
    "chai_called",
    "enrichment_rerun",
    "contrast_rerun",
)

METRIC_FIELDS = (
    "human_mean_vector_l2_norm",
    "elephant_mean_vector_l2_norm",
    "mean_pooled_cosine_similarity",
    "mean_pooled_cosine_distance",
    "mean_pooled_euclidean_distance",
)


@dataclass(frozen=True)
class MeanPooledPairwiseMetrics:
    human_mean_vector_l2_norm: float
    elephant_mean_vector_l2_norm: float
    mean_pooled_cosine_similarity: float
    mean_pooled_cosine_distance: float
    mean_pooled_euclidean_distance: float


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def _validate_embedding(
    array: np.ndarray,
    *,
    expected_rows: int,
    expected_columns: int = 960,
) -> None:
    if array.ndim != 2:
        raise ValueError(f"Expected a 2D embedding matrix, got {array.shape}")
    if array.shape != (expected_rows, expected_columns):
        raise ValueError(
            f"Expected embedding shape {(expected_rows, expected_columns)}, got {array.shape}"
        )
    if array.dtype != np.float32:
        raise ValueError(f"Expected embedding dtype float32, got {array.dtype}")
    if not np.isfinite(array).all():
        raise ValueError("Embedding contains non-finite values")


def compute_mean_pooled_metrics(
    human: np.ndarray,
    elephant: np.ndarray,
) -> MeanPooledPairwiseMetrics:
    """Compute length-independent metrics after separate residue-axis mean pooling."""

    _validate_embedding(human, expected_rows=491)
    _validate_embedding(elephant, expected_rows=492)

    human_mean = human.mean(axis=0, dtype=np.float64)
    elephant_mean = elephant.mean(axis=0, dtype=np.float64)

    human_norm = float(np.linalg.norm(human_mean))
    elephant_norm = float(np.linalg.norm(elephant_mean))
    if human_norm <= 0.0 or elephant_norm <= 0.0:
        raise ValueError("Mean-pooled embedding vector must have positive norm")

    cosine_similarity = float(np.dot(human_mean, elephant_mean) / (human_norm * elephant_norm))
    cosine_distance = float(1.0 - cosine_similarity)
    euclidean_distance = float(np.linalg.norm(human_mean - elephant_mean))

    values = (
        human_norm,
        elephant_norm,
        cosine_similarity,
        cosine_distance,
        euclidean_distance,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Mean-pooled pairwise metrics must all be finite")

    return MeanPooledPairwiseMetrics(
        human_mean_vector_l2_norm=human_norm,
        elephant_mean_vector_l2_norm=elephant_norm,
        mean_pooled_cosine_similarity=cosine_similarity,
        mean_pooled_cosine_distance=cosine_distance,
        mean_pooled_euclidean_distance=euclidean_distance,
    )


def format_metric(value: float) -> str:
    return f"{value:.16f}"


def validate_source_comparator(item: dict[str, str]) -> None:
    source = require_single_row(DEFAULT_SOURCE_COMPARATOR_TABLE)
    expected = {
        "comparator_status": item["source_comparator_status"],
        "pairwise_blocker": item["source_comparator_blocker"],
        "human_reference_accession": "Q00987",
        "human_embedding_available": "false",
        "elephant_target_accession": "G3SX30",
        "elephant_embedding_available": "true",
        "pairwise_summary_created": "false",
        "biological_claim_made": "false",
    }
    for field, expected_value in expected.items():
        actual = source.get(field)
        if actual != expected_value:
            raise ValueError(
                f"Source comparator expected {field}={expected_value!r}, got {actual!r}"
            )


def validate_pairwise_summary_row(item: dict[str, str]) -> None:
    for field, expected in EXPECTED_VALUES.items():
        actual = item.get(field)
        if actual != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")

    for field in FALSE_ONLY_FIELDS:
        if item[field] != "false":
            raise ValueError(f"Expected {field}='false'")

    for field in METRIC_FIELDS:
        value = float(item[field])
        if not math.isfinite(value):
            raise ValueError(f"Expected finite metric {field}, got {item[field]!r}")

    if float(item["human_mean_vector_l2_norm"]) <= 0.0:
        raise ValueError("Human mean-pooled vector norm must be positive")
    if float(item["elephant_mean_vector_l2_norm"]) <= 0.0:
        raise ValueError("Elephant mean-pooled vector norm must be positive")

    similarity = float(item["mean_pooled_cosine_similarity"])
    distance = float(item["mean_pooled_cosine_distance"])
    if not -1.0 <= similarity <= 1.0:
        raise ValueError("Cosine similarity must be in [-1, 1]")
    if not 0.0 <= distance <= 2.0:
        raise ValueError("Cosine distance must be in [0, 2]")
    if not math.isclose(similarity + distance, 1.0, abs_tol=1e-15):
        raise ValueError("Cosine distance must equal 1 - cosine similarity")

    if item["human_embedding_artifact_reference"] == item["elephant_embedding_artifact_reference"]:
        raise ValueError("Human and elephant embedding references must differ")

    claim_note = item.get("claim_note", "")
    for required in [
        "not residue alignment",
        "not interface analysis",
        "not binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
    ]:
        if required not in claim_note:
            raise ValueError(f"Missing claim boundary phrase: {required}")


def load_and_validate_pairwise_summary(
    path: Path = DEFAULT_PAIRWISE_SUMMARY_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_pairwise_summary_row(item)
    validate_source_comparator(item)
    return item
