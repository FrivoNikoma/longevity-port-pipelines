"""Validate the TP53/MDM2 Gate 6 NEGATOME integration result."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_gate6_negatome_integration_results.csv")
DEFAULT_CLOSURE_TABLE = Path("data/input/tp53_mdm2_first_control_closure_results.csv")
DEFAULT_DISPOSITION_TABLE = Path("data/input/tp53_mdm2_first_gate6_blocker_disposition_results.csv")
DEFAULT_ACTUAL_TABLE = Path("data/input/tp53_mdm2_embedding_based_negatome_control_results.csv")
DEFAULT_SHUFFLED_TABLE = Path(
    "data/input/tp53_mdm2_first_mdm2_side_shuffled_interface_control_results.csv"
)

EXPECTED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "integration_id",
    "integration_status",
    "integration_scope",
    "runtime_commit",
    "source_control_closure_table",
    "source_control_closure_row_index",
    "source_control_closure_status",
    "source_control_closure_evidence_sha256",
    "source_control_closure_table_canonical_sha256",
    "source_gate6_blocker_disposition_table",
    "source_gate6_blocker_disposition_row_index",
    "source_gate6_blocker_disposition_status",
    "source_gate6_blocker_disposition_metadata_sha256",
    "source_gate6_blocker_disposition_table_canonical_sha256",
    "source_actual_negatome_result_table",
    "source_actual_negatome_result_row_index",
    "source_actual_negatome_result_status",
    "source_actual_negatome_result_metadata_sha256",
    "source_actual_negatome_result_table_canonical_sha256",
    "source_geometric_shuffled_control_table",
    "source_geometric_shuffled_control_row_index",
    "source_geometric_shuffled_control_status",
    "source_geometric_shuffled_control_table_canonical_sha256",
    "required_embedding_control_repair_completed",
    "embedding_based_negatome_control_computed",
    "negatome_control_ratio_available",
    "negatome_control_ratio",
    "negatome_runtime_blocker",
    "geometric_shuffled_control_computed",
    "geometric_shuffled_metric_family",
    "geometric_shuffled_n_permutations",
    "true_adjacent_pair_count",
    "shuffled_adjacent_pair_count_mean",
    "adjacent_pair_empirical_upper_p_add_one",
    "metric_families_directly_comparable",
    "numerical_controlled_pass_fail_evaluated",
    "controlled_pass",
    "controlled_fail",
    "integration_decision_basis",
    "generic_control_repair_status_after",
    "generic_control_readiness_status_after",
    "gate6_control_readiness_status_after",
    "gate6_control_readiness_resolved_after",
    "gate6_control_closure_blocked_after",
    "gate7_entry_allowed_after",
    "gate7_strict_panel_promoted",
    "gate7_blocker_reason",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_approval_granted",
    "evidence_recomputed",
    "interface_scoring_performed",
    "comparative_elephant_interface_scoring_performed",
    "new_embeddings_generated_by_integration",
    "biohub_esmc_called_by_integration",
    "npy_artifact_read_by_integration",
    "npy_artifact_written_by_integration",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "binding_claim_made",
    "non_binding_claim_made",
    "binding_strength_claim_made",
    "functional_significance_claim_made",
    "biological_specificity_claim_made",
    "adaptation_claim_made",
    "elephant_compatibility_claim_made",
    "beneficial_breakage_claim_made",
    "longevity_evidence_claim_made",
    "biological_claim_made",
    "integration_metadata_canonical",
    "integration_metadata_sha256",
    "integration_result_created",
    "next_step",
    "result_date",
    "claim_note",
]
METADATA_KEYS = [
    "source_control_closure_evidence_sha256",
    "source_gate6_blocker_disposition_metadata_sha256",
    "source_actual_negatome_result_metadata_sha256",
    "source_geometric_shuffled_control_table_canonical_sha256",
    "required_embedding_control_repair_completed",
    "negatome_control_ratio",
    "metric_families_directly_comparable",
    "numerical_controlled_pass_fail_evaluated",
    "generic_control_repair_status_after",
    "generic_control_readiness_status_after",
    "gate6_control_readiness_status_after",
    "gate6_control_readiness_resolved_after",
    "gate6_control_closure_blocked_after",
    "gate7_entry_allowed_after",
    "integration_status",
]
EXPECTED_METADATA_SHA256 = "d121b1fbcc28116c26bebe7db9e34cc6722a183d069c5bc51310b32d112b8341"
EXPECTED_CLOSURE_TABLE_SHA256 = "ca9ecb2dbe940ef547a39e2543d5b1ef9d9b725c02a02b426d53deae1d3011f6"
EXPECTED_DISPOSITION_TABLE_SHA256 = (
    "144cbd9636e5515f5c9231f2a99028b4b1b8224caa37e51269fb2d71078fe49a"
)
EXPECTED_ACTUAL_TABLE_SHA256 = "a7f733b00a4ffa1415bbc6c66193c515f9bdf37d022a174f7be7bc8bade4d184"
EXPECTED_SHUFFLED_TABLE_SHA256 = "c2b36006abadd1d53017be824738b68567e2b98382ded8c7b07f7a220de553e3"
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7"
)
EXPECTED_DISPOSITION_METADATA_SHA256 = (
    "1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4"
)
EXPECTED_ACTUAL_METADATA_SHA256 = "d253e79b5bb345c66494347cb0858e54672151cf8406c370b97c70480ba19bc8"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_text(normalized)


def read_one_row(path: Path) -> tuple[list[str], dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        rows = list(reader)

    if not columns:
        raise ValueError(f"CSV has no header: {path}")
    if len(rows) != 1:
        raise ValueError(f"Expected one row in {path}, got {len(rows)}")

    row: dict[str, str] = {}
    for key, value in rows[0].items():
        if key is None or value is None:
            raise ValueError(f"Malformed CSV row in {path}")
        row[key] = value

    return columns, row


def metadata_canonical(row: dict[str, str]) -> str:
    return "|".join(f"{key}:{row[key]}" for key in METADATA_KEYS)


def validate_source_rows(root: Path) -> dict[str, dict[str, str]]:
    source_contracts = (
        (DEFAULT_CLOSURE_TABLE, EXPECTED_CLOSURE_TABLE_SHA256),
        (DEFAULT_DISPOSITION_TABLE, EXPECTED_DISPOSITION_TABLE_SHA256),
        (DEFAULT_ACTUAL_TABLE, EXPECTED_ACTUAL_TABLE_SHA256),
        (DEFAULT_SHUFFLED_TABLE, EXPECTED_SHUFFLED_TABLE_SHA256),
    )
    for relative_path, expected_hash in source_contracts:
        if canonical_text_sha256(root / relative_path) != expected_hash:
            raise ValueError(f"Canonical source table SHA256 changed: {relative_path}")

    _, closure = read_one_row(root / DEFAULT_CLOSURE_TABLE)
    _, disposition = read_one_row(root / DEFAULT_DISPOSITION_TABLE)
    _, actual = read_one_row(root / DEFAULT_ACTUAL_TABLE)
    _, shuffled = read_one_row(root / DEFAULT_SHUFFLED_TABLE)

    if closure["closure_evidence_sha256"] != EXPECTED_CLOSURE_EVIDENCE_SHA256:
        raise ValueError("Closure evidence SHA256 changed")
    if disposition["disposition_metadata_sha256"] != EXPECTED_DISPOSITION_METADATA_SHA256:
        raise ValueError("Disposition metadata SHA256 changed")
    if actual["result_metadata_sha256"] != EXPECTED_ACTUAL_METADATA_SHA256:
        raise ValueError("Actual result metadata SHA256 changed")

    if disposition["disposition_action"] != "require_embedding_based_control":
        raise ValueError("Unexpected disposition action")
    if disposition["generic_control_repair_status"] != "pending":
        raise ValueError("Unexpected source repair status")
    if actual["result_status"] != "actual_negatome_control_ratio_computed":
        raise ValueError("Unexpected actual NEGATOME result status")
    if actual["negatome_control_ratio"] != "1.2482765910897506":
        raise ValueError("Unexpected actual NEGATOME ratio")
    if actual["runtime_blocker"] != "none":
        raise ValueError("Actual NEGATOME result contains a blocker")
    if shuffled["metric_family"] != ("sequence_adjacency_contiguous_runs_and_longest_run"):
        raise ValueError("Unexpected shuffled metric family")
    if shuffled["embedding_interface_score_computed"] != "false":
        raise ValueError("Shuffled control unexpectedly includes embedding score")

    return {
        "closure": closure,
        "disposition": disposition,
        "actual": actual,
        "shuffled": shuffled,
    }


def validate_result_table(root: Path) -> dict[str, str]:
    sources = validate_source_rows(root)
    columns, row = read_one_row(root / DEFAULT_RESULT_TABLE)

    if columns != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected result columns: {columns}")

    expected = {
        "integration_status": ("actual_negatome_result_integrated_gate6_readiness_resolved"),
        "required_embedding_control_repair_completed": "true",
        "embedding_based_negatome_control_computed": "true",
        "negatome_control_ratio_available": "true",
        "negatome_control_ratio": "1.2482765910897506",
        "negatome_runtime_blocker": "none",
        "geometric_shuffled_control_computed": "true",
        "geometric_shuffled_metric_family": ("sequence_adjacency_contiguous_runs_and_longest_run"),
        "metric_families_directly_comparable": "false",
        "numerical_controlled_pass_fail_evaluated": "false",
        "controlled_pass": "false",
        "controlled_fail": "false",
        "generic_control_repair_status_after": "completed",
        "generic_control_readiness_status_after": "ready",
        "gate6_control_readiness_status_after": "ready",
        "gate6_control_readiness_resolved_after": "true",
        "gate6_control_closure_blocked_after": "false",
        "gate7_entry_allowed_after": "false",
        "gate7_strict_panel_promoted": "false",
        "gate8_entry_allowed": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_approval_granted": "false",
        "evidence_recomputed": "false",
        "new_embeddings_generated_by_integration": "false",
        "biohub_esmc_called_by_integration": "false",
        "npy_artifact_read_by_integration": "false",
        "npy_artifact_written_by_integration": "false",
        "npy_artifact_committed": "false",
        "data_output_artifact_committed": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "biological_claim_made": "false",
        "integration_result_created": "true",
    }
    for key, value in expected.items():
        if row[key] != value:
            raise ValueError(f"Unexpected {key}={row[key]!r}")

    if (
        row["source_control_closure_evidence_sha256"]
        != sources["closure"]["closure_evidence_sha256"]
    ):
        raise ValueError("Closure source linkage mismatch")
    if (
        row["source_gate6_blocker_disposition_metadata_sha256"]
        != sources["disposition"]["disposition_metadata_sha256"]
    ):
        raise ValueError("Disposition source linkage mismatch")
    if (
        row["source_actual_negatome_result_metadata_sha256"]
        != sources["actual"]["result_metadata_sha256"]
    ):
        raise ValueError("Actual result source linkage mismatch")

    canonical = metadata_canonical(row)
    if row["integration_metadata_canonical"] != canonical:
        raise ValueError("Integration metadata canonical mismatch")
    if sha256_text(canonical) != EXPECTED_METADATA_SHA256:
        raise ValueError("Computed integration metadata SHA256 mismatch")
    if row["integration_metadata_sha256"] != EXPECTED_METADATA_SHA256:
        raise ValueError("Recorded integration metadata SHA256 mismatch")

    return row
