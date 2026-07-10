"""Validate the first G3SX30 analysis-adjacent embedding scalar summary.

The committed row contains scalar statistics derived from the ignored local
runtime embedding. It is a pipeline integration result only, not a biological
comparison, interface result, binding result, or longevity evidence.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

DEFAULT_SOURCE_MINIMAL_OUTPUT_TABLE = Path(
    "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv"
)
DEFAULT_SUMMARY_TABLE = Path(
    "data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv"
)

EXPECTED_READY_ARTIFACT_REFERENCE = (
    "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
)
EXPECTED_NEXT_STEP = "add_first_controlled_comparator_or_pairwise_embedding_summary"

REQUIRED_SCALAR_FIELDS = (
    "embedding_value_mean",
    "embedding_value_std",
    "embedding_value_min",
    "embedding_value_max",
    "embedding_value_l2_norm",
    "token_l2_norm_mean",
    "token_l2_norm_std",
)

EXPECTED_VALUES = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "target_accession": "G3SX30",
    "target_accession_db": "UniProtKB TrEMBL",
    "target_species": "Loxodonta africana",
    "target_taxid": "9785",
    "gene_symbol": "MDM2",
    "source_minimal_output_table": (
        "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv"
    ),
    "source_minimal_output_row_index": "1",
    "source_output_status": "first_minimal_controlled_downstream_output_created",
    "source_output_type": "one_row_artifact_identity_and_embedding_health_summary",
    "source_ready_artifact_reference": EXPECTED_READY_ARTIFACT_REFERENCE,
    "source_embedding_shape": "492x960",
    "source_embedding_dtype": "float32",
    "source_embedding_finite": "true",
    "source_sequence_length": "492",
    "source_sequence_length_matches": "true",
    "source_one_row_only": "true",
    "source_ready_scope": "one_row_g3sx30_elephant_mdm2_only",
    "summary_status": "first_analysis_adjacent_controlled_embedding_summary_created",
    "summary_type": "one_row_embedding_scalar_summary_statistics",
    "summary_scope": "scalar_embedding_statistics_only_no_biological_claim",
    "scalar_summary_generated_from_local_runtime_embedding": "true",
    "raw_embedding_values_committed": "false",
    "token_count": "492",
    "embedding_dim": "960",
    "total_values": "472320",
    "finite_value_count": "472320",
    "finite_fraction": "1.0000000000",
    "one_row_only": "true",
    "ready_scope": "one_row_g3sx30_elephant_mdm2_only",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "data_output_artifact_committed": "false",
    "biohub_esmc_called_by_summary": "false",
    "live_embedding_rerun_by_summary": "false",
    "embedding_generation_performed_by_summary": "false",
    "npy_artifact_created_by_summary": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "enrichment_rerun": "false",
    "contrast_rerun": "false",
    "next_step": EXPECTED_NEXT_STEP,
    "next_pr_should_add_controlled_comparator_or_pairwise_embedding_summary": "true",
    "no_additional_scalar_summary_approval_before_comparator": "true",
    "no_additional_non_result_layer_before_next_concrete_step": "true",
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    """Read exactly one CSV row."""

    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, found {len(rows)}")
    return rows[0]


def validate_summary_row(row: dict[str, str]) -> None:
    """Validate identity, scalar statistics, boundaries, and next-step guard."""

    for field, expected in EXPECTED_VALUES.items():
        actual = row.get(field)
        if actual != expected:
            raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")

    for field in REQUIRED_SCALAR_FIELDS:
        text = row.get(field)
        if text is None:
            raise ValueError(f"Missing scalar field: {field}")
        value = float(text)
        if not math.isfinite(value):
            raise ValueError(f"Expected finite {field}, got {text!r}")

    token_count = int(row["token_count"])
    embedding_dim = int(row["embedding_dim"])
    total_values = int(row["total_values"])
    finite_value_count = int(row["finite_value_count"])
    if total_values != token_count * embedding_dim:
        raise ValueError("total_values must equal token_count * embedding_dim")
    if finite_value_count != total_values:
        raise ValueError("finite_value_count must equal total_values")
    if float(row["embedding_value_std"]) < 0.0:
        raise ValueError("embedding_value_std must be non-negative")
    if float(row["embedding_value_l2_norm"]) <= 0.0:
        raise ValueError("embedding_value_l2_norm must be positive")
    if float(row["token_l2_norm_mean"]) <= 0.0:
        raise ValueError("token_l2_norm_mean must be positive")
    if float(row["token_l2_norm_std"]) < 0.0:
        raise ValueError("token_l2_norm_std must be non-negative")

    forbidden = row.get("forbidden_actions", "")
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


def load_and_validate_summary(
    path: Path = DEFAULT_SUMMARY_TABLE,
) -> dict[str, str]:
    """Load and validate the committed one-row scalar summary."""

    row = require_single_row(path)
    validate_summary_row(row)
    return row
