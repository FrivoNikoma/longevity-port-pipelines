"""Validate and expose TP53/MDM2 Gate 7 coverage-repair resolutions."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import polars as pl

DEFAULT_RESOLUTIONS_PATH = Path("data/input/tp53_mdm2_gate7_coverage_repair_resolutions.csv")
DEFAULT_REPAIR_DECISIONS_PATH = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")
DEFAULT_INTAKE_PATH = Path("data/input/ortholog_evidence_intake.csv")
DEFAULT_REVIEW_PATH = Path("data/input/ortholog_evidence_review_decisions.csv")
DEFAULT_GATE45_PATH = Path("data/input/ortholog_evidence_gate45_policy_updates.csv")

EXPECTED_SOURCE_HASHES = {
    DEFAULT_REPAIR_DECISIONS_PATH: "4769a9f8a772d07a3cde2178e27ca009386823ce0d2d874e8cf292e8a87d7946",
    DEFAULT_INTAKE_PATH: "11b3f0b0cf27473ef34a1ab1a22725f94c6507173d576dd1557332cf8786dd85",
    DEFAULT_REVIEW_PATH: "ce666e25ee492fff0286422ce3baab3154238a15c72d0bb4f1ae1c1899e7de31",
    DEFAULT_GATE45_PATH: "ba4eed31cd63b0ce62cc0459692b2de7d104bb31d0289f51f48cddff24195f94",
}

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "source_uniprot",
    "target_species",
    "chain",
    "resolution_id",
    "resolution_status",
    "coverage_repair_outcome",
    "source_repair_decision_table",
    "source_repair_decision_row_index",
    "source_repair_decision_table_canonical_sha256",
    "source_evidence_table",
    "source_evidence_row_index",
    "source_evidence_table_canonical_sha256",
    "secondary_source_table",
    "secondary_source_row_index",
    "secondary_source_table_canonical_sha256",
    "target_uniprot_after_resolution",
    "source_ortholog_status_after_resolution",
    "local_candidate_row_status_after_resolution",
    "coverage_status_after_resolution",
    "provenance_status_after_resolution",
    "repair_decision_after_resolution",
    "repair_status_after_resolution",
    "coverage_preflight_status_after_resolution",
    "recommended_next_action_after_resolution",
    "generic_coverage_preflight_status_after_resolution",
    "strict_panel_allowed_after_resolution",
    "contrast_dry_run_allowed_after_resolution",
    "concrete_source_blocker",
    "gate7_entry_allowed",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_approval_granted",
    "live_calls_performed",
    "biohub_called",
    "embeddings_generated",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
    "resolution_note",
]
RESOLUTION_KEY_COLUMNS = (
    "candidate_id",
    "source_uniprot",
    "target_species",
    "chain",
)
ALLOWED_OUTCOMES = {
    "coverage_repaired_and_ready",
    "deferred_pending_source",
    "excluded",
    "needs_manual_review",
}


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def read_resolutions(path: Path = DEFAULT_RESOLUTIONS_PATH) -> pl.DataFrame:
    return pl.read_csv(path, infer_schema_length=0)


def _source_row(frame: pl.DataFrame, row_index: int) -> dict[str, Any]:
    if row_index < 1 or row_index > frame.height:
        raise ValueError(f"Source row index out of range: {row_index}")
    return frame.row(row_index - 1, named=True)


def validate_resolutions(rows: pl.DataFrame, *, root: Path = Path(".")) -> None:
    if list(rows.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Unexpected resolution columns: {rows.columns}")
    if rows.height != 2:
        raise ValueError(f"Expected two resolution rows, got {rows.height}")
    if rows.select(list(RESOLUTION_KEY_COLUMNS)).is_duplicated().any():
        raise ValueError("Duplicate TP53/MDM2 resolution keys")

    outcomes = set(rows.get_column("coverage_repair_outcome").to_list())
    if not outcomes.issubset(ALLOWED_OUTCOMES):
        raise ValueError(f"Unexpected resolution outcomes: {sorted(outcomes)}")

    for path, expected_hash in EXPECTED_SOURCE_HASHES.items():
        if canonical_text_sha256(root / path) != expected_hash:
            raise ValueError(f"Source SHA256 changed: {path}")

    repair = pl.read_csv(root / DEFAULT_REPAIR_DECISIONS_PATH)
    intake = pl.read_csv(root / DEFAULT_INTAKE_PATH)
    review = pl.read_csv(root / DEFAULT_REVIEW_PATH)
    gate45 = pl.read_csv(root / DEFAULT_GATE45_PATH)

    by_candidate = {str(row["candidate_id"]): row for row in rows.iter_rows(named=True)}
    expected_ids = {
        "tp53_mdm2_elephant_seed_mdm2_chain",
        "tp53_mdm2_elephant_seed_tp53_chain",
    }
    if set(by_candidate) != expected_ids:
        raise ValueError("Unexpected resolution candidate ids")

    mdm2 = by_candidate["tp53_mdm2_elephant_seed_mdm2_chain"]
    tp53 = by_candidate["tp53_mdm2_elephant_seed_tp53_chain"]

    mdm2_repair = _source_row(repair, int(str(mdm2["source_repair_decision_row_index"])))
    mdm2_review = _source_row(review, int(str(mdm2["source_evidence_row_index"])))
    mdm2_policy = _source_row(gate45, int(str(mdm2["secondary_source_row_index"])))
    if mdm2_repair["candidate_id"] != mdm2["candidate_id"]:
        raise ValueError("MDM2 repair source linkage mismatch")
    if mdm2_review["review_decision"] != "accepted_for_planning_after_review":
        raise ValueError("MDM2 review source is not planning-accepted")
    if mdm2_review["reviewed_target_uniprot"] != "G3SX30":
        raise ValueError("MDM2 reviewed accession changed")
    if mdm2_policy["policy_update_decision"] != ("approve_gate45_policy_update_for_planning"):
        raise ValueError("MDM2 Gate 4/5 policy source changed")

    tp53_repair = _source_row(repair, int(str(tp53["source_repair_decision_row_index"])))
    tp53_intake = _source_row(intake, int(str(tp53["source_evidence_row_index"])))
    if tp53_repair["candidate_id"] != tp53["candidate_id"]:
        raise ValueError("TP53 repair source linkage mismatch")
    if tp53_intake["intake_outcome"] != "evidence_insufficient_defer":
        raise ValueError("TP53 intake no longer supports defer")
    if tp53_intake["target_protein_accession"] != "unresolved":
        raise ValueError("TP53 target accession is no longer unresolved")

    expected_mdm2 = {
        "coverage_repair_outcome": "coverage_repaired_and_ready",
        "target_uniprot_after_resolution": "G3SX30",
        "repair_status_after_resolution": "accepted_for_planning_after_review",
        "generic_coverage_preflight_status_after_resolution": ("coverage_preflight_ready"),
        "strict_panel_allowed_after_resolution": "true",
    }
    for key, value in expected_mdm2.items():
        if str(mdm2[key]) != value:
            raise ValueError(f"Unexpected MDM2 resolution {key}")

    expected_tp53 = {
        "coverage_repair_outcome": "deferred_pending_source",
        "target_uniprot_after_resolution": "unresolved",
        "repair_status_after_resolution": "deferred_pending_source",
        "generic_coverage_preflight_status_after_resolution": ("blocked_deferred_pending_source"),
        "strict_panel_allowed_after_resolution": "false",
        "concrete_source_blocker": ("no_accepted_accession_level_elephant_tp53_ortholog_evidence"),
    }
    for key, value in expected_tp53.items():
        if str(tp53[key]) != value:
            raise ValueError(f"Unexpected TP53 resolution {key}")

    forbidden_fields = [
        "gate7_entry_allowed",
        "gate8_entry_allowed",
        "gate8_promoted",
        "gate9_promoted",
        "biological_approval_granted",
        "live_calls_performed",
        "biohub_called",
        "embeddings_generated",
        "npy_artifact_committed",
        "data_output_artifact_committed",
        "boltz_called",
        "af3_called",
        "chai_called",
        "biological_claim_made",
    ]
    for row in rows.iter_rows(named=True):
        for field in forbidden_fields:
            if str(row[field]) != "false":
                raise ValueError(f"Forbidden boundary opened: {field}")


def resolution_lookup(
    rows: pl.DataFrame,
) -> dict[tuple[str, str, str, str], dict[str, str]]:
    validate_resolutions(rows)
    lookup: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in rows.iter_rows(named=True):
        key = (
            str(row["candidate_id"]),
            str(row["source_uniprot"]),
            str(row["target_species"]),
            str(row["chain"]),
        )
        lookup[key] = {str(name): str(value) for name, value in row.items()}
    return lookup
