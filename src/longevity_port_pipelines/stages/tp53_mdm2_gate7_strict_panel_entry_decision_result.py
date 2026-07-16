"""Validate the TP53/MDM2 Gate 7 strict-panel entry decision result."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

import polars as pl

from longevity_port_pipelines.stages.tp53_mdm2_ortholog_repair_decisions import (
    DEFAULT_REPAIR_DECISIONS_PATH,
    read_repair_decisions,
)
from longevity_port_pipelines.stages.tp53_mdm2_pilot_coverage_preflight import (
    build_tp53_mdm2_generic_strict_panel_summary,
    build_tp53_mdm2_pilot_coverage_preflight,
)
from longevity_port_pipelines.stages.tp53_mdm2_pilot_manifest_validator import (
    DEFAULT_INPUT as DEFAULT_MANIFEST,
)

DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_gate7_strict_panel_entry_decision_results.csv")
DEFAULT_GATE6_TABLE = Path("data/input/tp53_mdm2_gate6_negatome_integration_results.csv")
DEFAULT_GENERIC_CONTRACT = Path("data/config/generic_strict_contrast_panel_schema.yaml")

EXPECTED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "decision_id",
    "decision_status",
    "decision_scope",
    "runtime_commit",
    "source_gate6_integration_table",
    "source_gate6_integration_row_index",
    "source_gate6_integration_status",
    "source_gate6_integration_table_canonical_sha256",
    "source_generic_gate7_contract",
    "source_generic_gate7_contract_schema_id",
    "source_generic_gate7_contract_canonical_sha256",
    "source_strict_panel_builder",
    "source_strict_panel_summary_path",
    "source_strict_panel_summary_canonical_sha256",
    "source_strict_panel_summary_row_count",
    "source_strict_panel_candidate_ids",
    "source_strict_panel_statuses",
    "source_coverage_preflight_statuses",
    "source_control_readiness_statuses",
    "source_recommended_next_actions",
    "source_blocked_target_species",
    "source_total_strict_panel_ready_species",
    "source_total_strict_panel_blocked_species",
    "source_total_strict_long_lived_ready",
    "source_total_strict_short_lived_ready",
    "source_contrast_dry_run_allowed",
    "source_controlled_claim_allowed",
    "source_claim_policy",
    "source_claim_status",
    "gate6_control_readiness_status",
    "gate6_control_readiness_resolved",
    "gate6_control_closure_blocked",
    "gate7_decision_status",
    "gate7_entry_allowed",
    "gate7_strict_panel_promoted",
    "strict_panel_status",
    "contrast_dry_run_allowed",
    "controlled_claim_allowed",
    "gate7_blocker_code",
    "gate7_blocker_reason",
    "recommended_next_action",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_approval_granted",
    "strict_panel_summary_rebuilt_from_committed_inputs",
    "interim_summary_required_for_validation",
    "interim_summary_file_committed",
    "biological_evidence_recomputed",
    "live_calls_performed",
    "biohub_called",
    "embeddings_generated",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
    "decision_metadata_canonical",
    "decision_metadata_sha256",
    "decision_result_created",
    "next_step",
    "result_date",
    "claim_note",
]
METADATA_KEYS = [
    "source_gate6_integration_table_canonical_sha256",
    "source_generic_gate7_contract_canonical_sha256",
    "source_strict_panel_summary_canonical_sha256",
    "source_strict_panel_candidate_ids",
    "source_strict_panel_statuses",
    "source_coverage_preflight_statuses",
    "source_total_strict_panel_ready_species",
    "source_total_strict_panel_blocked_species",
    "gate6_control_readiness_status",
    "gate6_control_readiness_resolved",
    "gate6_control_closure_blocked",
    "gate7_decision_status",
    "gate7_entry_allowed",
    "gate7_blocker_code",
    "recommended_next_action",
    "gate8_entry_allowed",
    "gate9_promoted",
    "decision_status",
]

EXPECTED_GATE6_HASH = "eeee7b8aab59095a50098f66090e1252f366ff2188492876fe61a0cede610213"
EXPECTED_GENERIC_CONTRACT_HASH = "13153244ead84d4f920e8350132e223ad9d7693a6efb326ef2b705922b434d83"
EXPECTED_SUMMARY_HASH = "670f5a6d00b8d2d7081563dc0952c02bc8bb05c514c3da27191e2c749acadc05"
EXPECTED_METADATA_SHA256 = "2e07b1620c02882ea8c227911774ae1c4ea7705981a785394ed1d530207337f7"

EXPECTED_CANDIDATE_IDS = [
    "tp53_mdm2_elephant_seed_mdm2_chain",
    "tp53_mdm2_elephant_seed_tp53_chain",
]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    return sha256_text(canonical_text(text))


def canonical_frame_csv(frame: pl.DataFrame) -> str:
    value = frame.write_csv()
    if not isinstance(value, str):
        raise ValueError("Polars did not return CSV text")
    return canonical_text(value)


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


def rebuild_source_summary(root: Path) -> pl.DataFrame:
    manifest = pl.read_csv(root / DEFAULT_MANIFEST)
    repair_decisions = read_repair_decisions(root / DEFAULT_REPAIR_DECISIONS_PATH)
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        manifest,
        repair_decisions=repair_decisions,
    )
    return build_tp53_mdm2_generic_strict_panel_summary(preflight)


def validate_source_summary(root: Path) -> pl.DataFrame:
    summary = rebuild_source_summary(root)
    if summary.height != 2:
        raise ValueError(f"Expected two strict-panel rows, got {summary.height}")

    rows = list(summary.iter_rows(named=True))
    candidate_ids = sorted(str(row["candidate_id"]) for row in rows)
    if candidate_ids != EXPECTED_CANDIDATE_IDS:
        raise ValueError(f"Unexpected candidate ids: {candidate_ids}")

    expected_strings = {
        "strict_panel_status": "blocked_species_coverage_repair",
        "coverage_preflight_statuses": "blocked_pending_repair_review",
        "control_readiness_statuses": "controls_not_evaluated_coverage_blocked",
        "recommended_next_action": "resolve_coverage_repair_decisions",
        "blocked_target_species": "elephant",
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "strict_panel_readiness",
    }
    for row in rows:
        for key, expected in expected_strings.items():
            if str(row[key]) != expected:
                raise ValueError(f"Unexpected summary {key}={row[key]!r}")
        if int(row["n_strict_panel_ready_species"]) != 0:
            raise ValueError("Strict-panel-ready species must remain zero")
        if int(row["n_strict_panel_blocked_species"]) != 1:
            raise ValueError("Each row must retain one blocked species")
        if int(row["n_strict_long_lived_ready"]) != 0:
            raise ValueError("Long-lived-ready species must remain zero")
        if int(row["n_strict_short_lived_ready"]) != 0:
            raise ValueError("Short-lived-ready species must remain zero")
        if bool(row["contrast_dry_run_allowed"]):
            raise ValueError("Source summary unexpectedly permits dry run")
        if bool(row["controlled_claim_allowed"]):
            raise ValueError("Source summary unexpectedly permits controlled claim")

    summary_hash = sha256_text(canonical_frame_csv(summary))
    if summary_hash != EXPECTED_SUMMARY_HASH:
        raise ValueError("Deterministic strict-panel summary SHA256 changed")
    return summary


def validate_source_contracts(root: Path) -> dict[str, Any]:
    if canonical_text_sha256(root / DEFAULT_GATE6_TABLE) != EXPECTED_GATE6_HASH:
        raise ValueError("Gate 6 integration source SHA256 changed")
    if canonical_text_sha256(root / DEFAULT_GENERIC_CONTRACT) != (EXPECTED_GENERIC_CONTRACT_HASH):
        raise ValueError("Generic Gate 7 contract SHA256 changed")

    _, gate6 = read_one_row(root / DEFAULT_GATE6_TABLE)
    expected_gate6 = {
        "integration_status": ("actual_negatome_result_integrated_gate6_readiness_resolved"),
        "gate6_control_readiness_status_after": "ready",
        "gate6_control_readiness_resolved_after": "true",
        "gate6_control_closure_blocked_after": "false",
    }
    for key, expected in expected_gate6.items():
        if gate6[key] != expected:
            raise ValueError(f"Unexpected Gate 6 source {key}")

    contract = (root / DEFAULT_GENERIC_CONTRACT).read_text(encoding="utf-8-sig")
    required_fragments = [
        "schema_id: generic_strict_contrast_panel_schema",
        "- blocked_species_coverage_repair",
        "recommended_next_action: resolve_coverage_repair_decisions",
        "contrast_dry_run_allowed: false",
        "controlled_claim_allowed: false",
    ]
    for fragment in required_fragments:
        if fragment not in contract:
            raise ValueError(f"Generic Gate 7 contract missing {fragment!r}")

    summary = validate_source_summary(root)
    return {"gate6": gate6, "summary": summary}


def validate_result_table(root: Path) -> dict[str, str]:
    sources = validate_source_contracts(root)
    columns, row = read_one_row(root / DEFAULT_RESULT_TABLE)

    if columns != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected result columns: {columns}")

    expected = {
        "decision_status": "gate7_entry_blocked_by_species_coverage_repair",
        "source_strict_panel_summary_row_count": "2",
        "source_strict_panel_statuses": "blocked_species_coverage_repair",
        "source_coverage_preflight_statuses": "blocked_pending_repair_review",
        "source_control_readiness_statuses": ("controls_not_evaluated_coverage_blocked"),
        "source_total_strict_panel_ready_species": "0",
        "source_total_strict_panel_blocked_species": "2",
        "source_total_strict_long_lived_ready": "0",
        "source_total_strict_short_lived_ready": "0",
        "source_contrast_dry_run_allowed": "false",
        "source_controlled_claim_allowed": "false",
        "gate6_control_readiness_status": "ready",
        "gate6_control_readiness_resolved": "true",
        "gate6_control_closure_blocked": "false",
        "gate7_decision_status": "terminal_blocked_decision_recorded",
        "gate7_entry_allowed": "false",
        "gate7_strict_panel_promoted": "false",
        "strict_panel_status": "blocked_species_coverage_repair",
        "contrast_dry_run_allowed": "false",
        "controlled_claim_allowed": "false",
        "gate7_blocker_code": "blocked_species_coverage_repair",
        "recommended_next_action": "resolve_coverage_repair_decisions",
        "gate8_entry_allowed": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_approval_granted": "false",
        "strict_panel_summary_rebuilt_from_committed_inputs": "true",
        "interim_summary_required_for_validation": "false",
        "interim_summary_file_committed": "false",
        "biological_evidence_recomputed": "false",
        "live_calls_performed": "false",
        "biohub_called": "false",
        "embeddings_generated": "false",
        "npy_artifact_committed": "false",
        "data_output_artifact_committed": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "biological_claim_made": "false",
        "decision_result_created": "true",
        "next_step": "resolve_coverage_repair_decisions",
    }
    for key, expected_value in expected.items():
        if row[key] != expected_value:
            raise ValueError(f"Unexpected {key}={row[key]!r}")

    if row["source_gate6_integration_table_canonical_sha256"] != (EXPECTED_GATE6_HASH):
        raise ValueError("Gate 6 source linkage mismatch")
    if row["source_generic_gate7_contract_canonical_sha256"] != (EXPECTED_GENERIC_CONTRACT_HASH):
        raise ValueError("Generic Gate 7 contract linkage mismatch")
    if row["source_strict_panel_summary_canonical_sha256"] != EXPECTED_SUMMARY_HASH:
        raise ValueError("Strict-panel summary linkage mismatch")

    source_rows = list(sources["summary"].iter_rows(named=True))
    expected_candidates = ",".join(sorted(str(source["candidate_id"]) for source in source_rows))
    if row["source_strict_panel_candidate_ids"] != expected_candidates:
        raise ValueError("Strict-panel candidate linkage mismatch")

    canonical = metadata_canonical(row)
    if row["decision_metadata_canonical"] != canonical:
        raise ValueError("Decision metadata canonical mismatch")
    if sha256_text(canonical) != EXPECTED_METADATA_SHA256:
        raise ValueError("Computed decision metadata SHA256 mismatch")
    if row["decision_metadata_sha256"] != EXPECTED_METADATA_SHA256:
        raise ValueError("Recorded decision metadata SHA256 mismatch")
    return row
