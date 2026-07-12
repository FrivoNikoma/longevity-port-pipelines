"""Validate and reproduce the first independent pairwise embedding control.

The comparator was selected before similarity inspection using a frozen rule
over existing local ignored ESMC artifacts and committed provenance. This is a
numerical embedding-space comparator only, not a biological negative control.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from longevity_port_pipelines.stages import (
    g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_check as robustness,
)
from longevity_port_pipelines.stages import (
    g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summary as pairwise,
)

DEFAULT_SOURCE_PAIRWISE_TABLE = Path(
    "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
)
DEFAULT_SOURCE_ROBUSTNESS_TABLE = Path(
    "data/input/"
    "g3sx30_first_controlled_human_elephant_mdm2_pairwise_embedding_robustness_checks.csv"
)
DEFAULT_INDEPENDENT_CONTROL_TABLE = Path(
    "data/input/g3sx30_first_independent_pairwise_embedding_control_results.csv"
)

EXPECTED_ANCHOR_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9606.npy"
)
EXPECTED_COMPARATOR_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/4xhu__A1_P09874--4xhu__B1_Q9UNS1_receptor_109478.npy"
)

PROVENANCE_DOCS = (
    Path("docs/brandts_bat_p09874_curated_embedding_preflight.md"),
    Path("docs/brandts_bat_p09874_live_embedding_generation.md"),
    Path("docs/brandts_bat_p09874_downstream_readiness.md"),
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "source_pairwise_summary_table": (
        "data/input/g3sx30_first_human_elephant_mdm2_mean_pooled_pairwise_summaries.csv"
    ),
    "source_pairwise_summary_row_index": "1",
    "source_pairwise_summary_status": (
        "first_human_elephant_mdm2_mean_pooled_embedding_summary_created"
    ),
    "source_robustness_table": (
        "data/input/g3sx30_first_controlled_human_elephant_mdm2_"
        "pairwise_embedding_robustness_checks.csv"
    ),
    "source_robustness_row_index": "1",
    "source_robustness_status": ("first_controlled_pairwise_embedding_robustness_check_created"),
    "baseline_mdm2_cosine_similarity": "0.9973314302339468",
    "independent_control_status": ("first_independent_pairwise_embedding_control_result_created"),
    "independent_control_type": (
        "human_mdm2_to_preselected_non_mdm2_non_tp53_source_backed_embedding_comparator"
    ),
    "independent_control_scope": (
        "numerical_embedding_space_independent_control_only_no_biological_claim"
    ),
    "control_selection_rule": (
        "existing_same_model_finite_float32_source_backed_non_mdm2_"
        "non_tp53_pre_similarity_ranked_comparator"
    ),
    "selection_rule_frozen_before_similarity": "true",
    "inventory_similarity_computed": "false",
    "inventory_embedding_file_count": "216",
    "inventory_technical_candidate_count": "1",
    "anchor_accession": "Q00987",
    "anchor_species": "Homo sapiens",
    "anchor_taxid": "9606",
    "anchor_gene_symbol": "MDM2",
    "anchor_artifact_reference": EXPECTED_ANCHOR_REFERENCE,
    "anchor_shape": "491x960",
    "anchor_dtype": "float32",
    "anchor_finite": "true",
    "anchor_artifact_committed": "false",
    "independent_comparator_source_accession": "P09874",
    "independent_comparator_target_accession": "EPQ16369.1",
    "independent_comparator_target_accession_db": "NCBI Protein",
    "independent_comparator_species": "brandts_bat",
    "independent_comparator_taxid": "109478",
    "independent_comparator_complex_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
    "independent_comparator_chain": "receptor",
    "independent_comparator_artifact_reference": EXPECTED_COMPARATOR_REFERENCE,
    "independent_comparator_shape": "1024x960",
    "independent_comparator_dtype": "float32",
    "independent_comparator_finite": "true",
    "independent_comparator_artifact_committed": "false",
    "model": "esmc-300m-2024-12",
    "pooling": "independent_mean_pooling_over_residue_axis",
    "metric_calculation_dtype": "float64",
    "metric_decimal_places": "16",
    "independent_control_cosine_similarity": "0.8316190559481323",
    "baseline_minus_control_delta": "0.1657123742858144",
    "baseline_greater_than_independent_control": "true",
    "external_independent_control_result_sha256": (
        "577b0b24c6a0657c78e0db2ab8b71499cf8dd2a5dd72b6ee33c241058bdbcf23"
    ),
    "control_result_created": "true",
    "residue_alignment_performed": "false",
    "biohub_esmc_called": "false",
    "new_embedding_generated": "false",
    "npy_artifact_committed": "false",
    "raw_embedding_vectors_committed": "false",
    "data_output_artifact_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "enrichment_rerun": "false",
    "contrast_rerun": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "next_step": (
        "add_first_matched_elephant_mdm2_independent_control_result_before_interpretation"
    ),
    "comparator_must_remain_frozen": "true",
    "no_biological_interpretation_from_single_independent_control": "true",
    "no_additional_control_plan_only_layer": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
    "result_date": "2026-07-12",
    "claim_note": (
        "Numerical embedding-space independent comparator only; not a biological "
        "negative control; not residue alignment; not interface analysis; not "
        "binding result; not orthology proof; not functional-equivalence evidence; "
        "not longevity evidence."
    ),
}

FALSE_ONLY_FIELDS = (
    "inventory_similarity_computed",
    "anchor_artifact_committed",
    "independent_comparator_artifact_committed",
    "residue_alignment_performed",
    "biohub_esmc_called",
    "new_embedding_generated",
    "npy_artifact_committed",
    "raw_embedding_vectors_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "enrichment_rerun",
    "contrast_rerun",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)

METRIC_FIELDS = (
    "baseline_mdm2_cosine_similarity",
    "independent_control_cosine_similarity",
    "baseline_minus_control_delta",
)

COMPARISON_ABS_TOL = 5e-16


@dataclass(frozen=True)
class IndependentControlMetrics:
    baseline_mdm2_cosine_similarity: float
    independent_control_cosine_similarity: float
    baseline_minus_control_delta: float
    baseline_greater_than_independent_control: bool


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


def compute_independent_control_metrics(
    anchor: np.ndarray,
    comparator: np.ndarray,
    *,
    baseline_mdm2_cosine_similarity: float,
) -> IndependentControlMetrics:
    _validate_embedding(anchor, expected_rows=491)
    _validate_embedding(comparator, expected_rows=1024)

    anchor_mean = anchor.mean(axis=0, dtype=np.float64)
    comparator_mean = comparator.mean(axis=0, dtype=np.float64)

    anchor_norm = float(np.linalg.norm(anchor_mean))
    comparator_norm = float(np.linalg.norm(comparator_mean))
    if anchor_norm <= 0.0 or comparator_norm <= 0.0:
        raise ValueError("Mean-pooled embedding vectors must have positive norm")

    control_similarity = float(
        np.dot(anchor_mean, comparator_mean) / (anchor_norm * comparator_norm)
    )
    delta = float(baseline_mdm2_cosine_similarity - control_similarity)

    values = (
        baseline_mdm2_cosine_similarity,
        control_similarity,
        delta,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Independent control metrics must all be finite")
    if not -1.0 <= baseline_mdm2_cosine_similarity <= 1.0:
        raise ValueError("Baseline cosine similarity must be in [-1, 1]")
    if not -1.0 <= control_similarity <= 1.0:
        raise ValueError("Independent control cosine similarity must be in [-1, 1]")

    return IndependentControlMetrics(
        baseline_mdm2_cosine_similarity=baseline_mdm2_cosine_similarity,
        independent_control_cosine_similarity=control_similarity,
        baseline_minus_control_delta=delta,
        baseline_greater_than_independent_control=(delta > COMPARISON_ABS_TOL),
    )


def reproduce_independent_control(
    anchor_path: Path,
    comparator_path: Path,
    *,
    baseline_mdm2_cosine_similarity: float,
) -> IndependentControlMetrics:
    anchor = np.load(anchor_path, allow_pickle=False)
    comparator = np.load(comparator_path, allow_pickle=False)
    return compute_independent_control_metrics(
        anchor,
        comparator,
        baseline_mdm2_cosine_similarity=baseline_mdm2_cosine_similarity,
    )


def format_metric(value: float) -> str:
    return f"{value:.16f}"


def validate_source_rows(item: dict[str, str]) -> None:
    source_pairwise = pairwise.load_and_validate_pairwise_summary(DEFAULT_SOURCE_PAIRWISE_TABLE)
    source_robustness = robustness.load_and_validate_robustness_check(
        DEFAULT_SOURCE_ROBUSTNESS_TABLE
    )

    pairwise_expected = {
        "pairwise_summary_status": item["source_pairwise_summary_status"],
        "mean_pooled_cosine_similarity": item["baseline_mdm2_cosine_similarity"],
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, expected in pairwise_expected.items():
        actual = source_pairwise.get(field)
        if actual != expected:
            raise ValueError(f"Source pairwise expected {field}={expected!r}, got {actual!r}")

    robustness_expected = {
        "robustness_check_status": item["source_robustness_status"],
        "baseline_cosine_similarity": item["baseline_mdm2_cosine_similarity"],
        "next_step": (
            "add_first_independent_pairwise_embedding_control_result_before_interpretation"
        ),
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, expected in robustness_expected.items():
        actual = source_robustness.get(field)
        if actual != expected:
            raise ValueError(f"Source robustness expected {field}={expected!r}, got {actual!r}")


def validate_provenance_docs(item: dict[str, str]) -> None:
    required_by_doc = {
        PROVENANCE_DOCS[0]: (
            "target_species: brandts_bat",
            "target_species_taxid: 109478",
            "target_accession: EPQ16369.1",
            "target_accession_db: NCBI Protein",
            "model_name: esmc-300m-2024-12",
            item["independent_comparator_artifact_reference"],
        ),
        PROVENANCE_DOCS[1]: (
            "target_species: brandts_bat",
            "target_species_taxid: 109478",
            "target_accession: EPQ16369.1",
            "target_accession_db: NCBI Protein",
            "status: live_completed",
            "embedding_shape: 1024x960",
            "dtype: float32",
            "finite: True",
            item["independent_comparator_artifact_reference"],
        ),
        PROVENANCE_DOCS[2]: (
            "source_uniprot: P09874",
            "source_species_taxid: 9606",
            "target_species: brandts_bat",
            "target_species_taxid: 109478",
            "target_accession: EPQ16369.1",
            "curated status: primary_candidate",
            "coverage matching rows: 1",
            "embedding exists: True",
            item["independent_comparator_artifact_reference"],
        ),
    }

    for path, required_phrases in required_by_doc.items():
        text = path.read_text(encoding="utf-8-sig")
        for phrase in required_phrases:
            if phrase not in text:
                raise ValueError(f"Missing provenance phrase {phrase!r} in {path}")


def validate_independent_control_row(item: dict[str, str]) -> None:
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
            raise ValueError(f"Expected finite metric {field}")

    baseline = float(item["baseline_mdm2_cosine_similarity"])
    control = float(item["independent_control_cosine_similarity"])
    delta = float(item["baseline_minus_control_delta"])

    if not -1.0 <= baseline <= 1.0:
        raise ValueError("Baseline cosine similarity must be in [-1, 1]")
    if not -1.0 <= control <= 1.0:
        raise ValueError("Independent control cosine similarity must be in [-1, 1]")
    if not math.isclose(
        delta,
        baseline - control,
        abs_tol=COMPARISON_ABS_TOL,
    ):
        raise ValueError("baseline_minus_control_delta is inconsistent")

    expected_baseline_greater = delta > COMPARISON_ABS_TOL
    if expected_baseline_greater != (item["baseline_greater_than_independent_control"] == "true"):
        raise ValueError("Baseline/control ordering field is inconsistent")

    if "mdm2" in item["independent_comparator_artifact_reference"].lower():
        raise ValueError("Independent comparator path must not contain MDM2")
    if "tp53" in item["independent_comparator_artifact_reference"].lower():
        raise ValueError("Independent comparator path must not contain TP53")
    if item["anchor_artifact_reference"] == item["independent_comparator_artifact_reference"]:
        raise ValueError("Anchor and independent comparator paths must differ")

    claim_note = item.get("claim_note", "")
    for required in [
        "not a biological negative control",
        "not residue alignment",
        "not interface analysis",
        "not binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
    ]:
        if required not in claim_note:
            raise ValueError(f"Missing claim boundary phrase: {required}")


def load_and_validate_independent_control(
    path: Path = DEFAULT_INDEPENDENT_CONTROL_TABLE,
) -> dict[str, str]:
    item = require_single_row(path)
    validate_independent_control_row(item)
    validate_source_rows(item)
    validate_provenance_docs(item)
    return item
