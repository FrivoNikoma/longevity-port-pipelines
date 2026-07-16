"""Validate the TP53/MDM2 actual embedding-based NEGATOME control result."""

from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_embedding_based_negatome_control_results.csv")
DEFAULT_SOURCE_REPAIR_TABLE = Path(
    "data/input/tp53_mdm2_embedding_based_negatome_control_repair_results.csv"
)
DEFAULT_MAPPING_TABLE = Path("data/input/tp53_mdm2_1ycr_q00987_interface_mapping.csv")
DEFAULT_PAIR_TABLE = Path("data/input/tp53_mdm2_repaired_negatome_control_pairs.csv")

EXPECTED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "result_id",
    "result_status",
    "result_scope",
    "source_repair_result_table",
    "source_repair_result_row_index",
    "source_repair_result_status",
    "source_repair_result_metadata_sha256",
    "runtime_commit",
    "live_result_timestamp_utc",
    "biohub_authorization_scope",
    "model_name",
    "negative_partner_uniprot",
    "negative_partner_sequence_length",
    "negative_partner_sequence_sha256",
    "negative_partner_embedding_path",
    "negative_partner_embedding_shape",
    "negative_partner_embedding_dtype",
    "negative_partner_embedding_finite",
    "negative_partner_embedding_sha256",
    "negative_partner_embedding_tracked",
    "negative_partner_embedding_ignored",
    "negative_partner_embedding_staged",
    "human_reference_accession",
    "human_reference_taxid",
    "human_embedding_path",
    "human_embedding_shape",
    "human_embedding_sha256",
    "elephant_target_accession",
    "elephant_target_taxid",
    "elephant_embedding_path",
    "elephant_embedding_shape",
    "elephant_embedding_sha256",
    "interface_mapping_table",
    "interface_mapping_canonical_utf8_lf_sha256",
    "interface_mapping_raw_worktree_sha256",
    "interface_mapping_raw_differs_from_canonical",
    "mapped_interface_count",
    "mapped_full_length_zero_based_indices",
    "pair_table",
    "pair_table_canonical_utf8_lf_sha256",
    "pair_table_raw_worktree_sha256",
    "pair_table_raw_differs_from_canonical",
    "exact_negatome_lookup_key",
    "external_live_report_sha256",
    "external_live_guard_sha256",
    "biohub_esmc_called",
    "new_embeddings_generated",
    "npy_artifact_written",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "control_ratio_runtime_function",
    "control_ratio_runtime_executed",
    "embedding_based_negatome_control_computed",
    "negatome_control_ratio_available",
    "negatome_control_ratio",
    "technical_ratio_interpretation",
    "runtime_blocker",
    "checked_blocker_count",
    "checked_blocker",
    "gate6_control_readiness_status_after",
    "gate6_control_readiness_resolved_after",
    "gate6_control_closure_blocked_after",
    "gate7_entry_allowed_after",
    "gate8_promoted",
    "gate9_promoted",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
    "result_metadata_canonical",
    "result_metadata_sha256",
    "result_created",
    "next_step",
    "result_date",
    "claim_note",
]
METADATA_KEYS = [
    "source_repair_result_metadata_sha256",
    "runtime_commit",
    "model_name",
    "negative_partner_uniprot",
    "negative_partner_sequence_sha256",
    "negative_partner_embedding_sha256",
    "human_embedding_sha256",
    "elephant_embedding_sha256",
    "interface_mapping_canonical_utf8_lf_sha256",
    "pair_table_canonical_utf8_lf_sha256",
    "external_live_report_sha256",
    "external_live_guard_sha256",
    "negatome_control_ratio",
    "result_status",
    "gate6_control_readiness_status_after",
    "gate7_entry_allowed_after",
]
EXPECTED_METADATA_SHA256 = "d253e79b5bb345c66494347cb0858e54672151cf8406c370b97c70480ba19bc8"
EXPECTED_SOURCE_REPAIR_METADATA_SHA256 = (
    "412763e453ff99d4271fff95839dbf38e1d636f9ebfab497cb2f3b41862de068"
)
EXPECTED_MAPPING_SHA256 = "73cc5548869e537cd90d78a3cf1a417097f85b9dde99818d8c09f96cce8aa325"
EXPECTED_PAIR_SHA256 = "3a97680c46914b468cf1ef1de72bf5da9e51109a31f4d2ba5ee3cdc3af61eb73"
EXPECTED_RATIO = 1.2482765910897506


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_text(text)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        rows = list(reader)

    if not columns:
        raise ValueError(f"CSV has no header: {path}")

    normalized: list[dict[str, str]] = []
    for raw_row in rows:
        row: dict[str, str] = {}
        for key, value in raw_row.items():
            if key is None or value is None:
                raise ValueError(f"Malformed CSV row: {path}")
            row[key] = value
        normalized.append(row)

    return columns, normalized


def metadata_canonical(row: dict[str, str]) -> str:
    return "|".join(f"{key}:{row[key]}" for key in METADATA_KEYS)


def validate_result_table(root: Path) -> dict[str, str]:
    _, source_rows = read_rows(root / DEFAULT_SOURCE_REPAIR_TABLE)
    if len(source_rows) != 1:
        raise ValueError("Expected one source repair result")
    source_row = source_rows[0]

    if source_row["result_metadata_sha256"] != EXPECTED_SOURCE_REPAIR_METADATA_SHA256:
        raise ValueError("Source repair metadata SHA256 changed")

    if canonical_text_sha256(root / DEFAULT_MAPPING_TABLE) != EXPECTED_MAPPING_SHA256:
        raise ValueError("Canonical mapping-table SHA256 changed")

    if canonical_text_sha256(root / DEFAULT_PAIR_TABLE) != EXPECTED_PAIR_SHA256:
        raise ValueError("Canonical pair-table SHA256 changed")

    columns, rows = read_rows(root / DEFAULT_RESULT_TABLE)
    if columns != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected result columns: {columns}")
    if len(rows) != 1:
        raise ValueError(f"Expected one result row, got {len(rows)}")

    row = rows[0]
    expected = {
        "result_status": "actual_negatome_control_ratio_computed",
        "model_name": "esmc-300m-2024-12",
        "negative_partner_uniprot": "G3UAZ0",
        "negative_partner_sequence_length": "364",
        "negative_partner_embedding_shape": "364x960",
        "negative_partner_embedding_dtype": "float32",
        "negative_partner_embedding_finite": "true",
        "negative_partner_embedding_tracked": "false",
        "negative_partner_embedding_ignored": "true",
        "negative_partner_embedding_staged": "false",
        "mapped_interface_count": "47",
        "biohub_esmc_called": "true",
        "new_embeddings_generated": "1",
        "npy_artifact_written": "true",
        "npy_artifact_committed": "false",
        "data_output_artifact_committed": "false",
        "control_ratio_runtime_executed": "true",
        "embedding_based_negatome_control_computed": "true",
        "negatome_control_ratio_available": "true",
        "runtime_blocker": "none",
        "checked_blocker_count": "0",
        "checked_blocker": "none",
        "gate6_control_readiness_status_after": ("blocked_pending_control_result_integration"),
        "gate6_control_readiness_resolved_after": "false",
        "gate6_control_closure_blocked_after": "true",
        "gate7_entry_allowed_after": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "biological_claim_made": "false",
        "result_created": "true",
    }

    for key, value in expected.items():
        if row[key] != value:
            raise ValueError(f"Unexpected {key}={row[key]!r}")

    if not math.isclose(
        float(row["negatome_control_ratio"]),
        EXPECTED_RATIO,
        rel_tol=0.0,
        abs_tol=1e-15,
    ):
        raise ValueError("Unexpected NEGATOME control ratio")

    indices = [int(value) for value in row["mapped_full_length_zero_based_indices"].split("|")]
    if len(indices) != 47 or len(set(indices)) != 47:
        raise ValueError("Mapped interface contract failed")
    if min(indices) < 0 or max(indices) >= 491:
        raise ValueError("Mapped interface index out of bounds")

    if row["source_repair_result_metadata_sha256"] != source_row["result_metadata_sha256"]:
        raise ValueError("Source repair linkage mismatch")

    canonical = metadata_canonical(row)
    if row["result_metadata_canonical"] != canonical:
        raise ValueError("Metadata canonical string mismatch")
    if sha256_text(canonical) != EXPECTED_METADATA_SHA256:
        raise ValueError("Computed metadata SHA256 mismatch")
    if row["result_metadata_sha256"] != EXPECTED_METADATA_SHA256:
        raise ValueError("Recorded metadata SHA256 mismatch")

    return row
