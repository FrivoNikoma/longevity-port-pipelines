# Validate the TP53/MDM2 MDM2-side short-lived control result.

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import polars as pl

DEFAULT_RESULTS_PATH = Path("data/input/tp53_mdm2_mdm2_short_lived_control_results.csv")
DEFAULT_SPECIES_GROUPS_PATH = Path("data/config/species_groups.yaml")
DEFAULT_MANIFEST_PATH = Path("data/input/tp53_mdm2_pilot_manifest.csv")
DEFAULT_COVERAGE_RESOLUTIONS_PATH = Path(
    "data/input/tp53_mdm2_gate7_coverage_repair_resolutions.csv"
)

EXPECTED_SOURCE_HASHES = {
    DEFAULT_SPECIES_GROUPS_PATH: "3da055452049295543c162a3a6ae5ff518a48ce59d7636d07d9f7ec4e10a0a60",
    DEFAULT_MANIFEST_PATH: "d3d256f0319a7a3b8b4d5a832dcab9b52c3d48c2d7046e88b132019d7abdb35f",
    DEFAULT_COVERAGE_RESOLUTIONS_PATH: "5e9c6e8195da41ada864fbf82d790f40bcb33e230fc3954f051972bdccc7a792",
}

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "partner_uniprot",
    "priority",
    "gene_symbol",
    "selected_control_species",
    "selected_control_species_name",
    "selected_control_species_taxid",
    "species_group",
    "target_protein_accession",
    "evidence_source_database",
    "evidence_source_accession",
    "evidence_source_review_status",
    "sequence_status",
    "sequence_length",
    "protein_existence_status",
    "evidence_reference",
    "evidence_checked_date",
    "species_policy_table_canonical_sha256",
    "manifest_source_table_canonical_sha256",
    "coverage_resolution_source_table_canonical_sha256",
    "review_decision",
    "selection_outcome",
    "coverage_preflight_status_after_selection",
    "control_readiness_status_after_selection",
    "contrast_readiness_status_after_selection",
    "claim_policy",
    "claim_status",
    "strict_panel_row_allowed",
    "gate7_mdm2_strict_panel_status_after_selection",
    "gate7_mdm2_contrast_dry_run_allowed_after_selection",
    "aggregate_gate7_entry_allowed",
    "aggregate_gate7_blocker_code",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "exact_local_embedding_status",
    "embedding_generation_allowed",
    "live_calls_performed",
    "biohub_called",
    "embeddings_generated",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
    "result_note",
]

FALSE_BOUNDARY_FIELDS = [
    "aggregate_gate7_entry_allowed",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "embedding_generation_allowed",
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


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def read_results(path: Path = DEFAULT_RESULTS_PATH) -> pl.DataFrame:
    rows = pl.read_csv(path, infer_schema_length=0)
    validate_results(rows)
    return rows


def _single_row(frame: pl.DataFrame, label: str) -> dict[str, Any]:
    if frame.height != 1:
        raise ValueError(f"Expected one {label} row, got {frame.height}")
    return frame.row(0, named=True)


def validate_results(
    rows: pl.DataFrame,
    *,
    root: Path = Path("."),
) -> None:
    if list(rows.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Unexpected result columns: {rows.columns}")
    if rows.height != 1:
        raise ValueError(f"Expected one result row, got {rows.height}")

    row = _single_row(rows, "short-lived control result")

    for source_path, expected_hash in EXPECTED_SOURCE_HASHES.items():
        if canonical_text_sha256(root / source_path) != expected_hash:
            raise ValueError(f"Source SHA256 changed: {source_path}")

    expected_hash_columns = {
        "species_policy_table_canonical_sha256": EXPECTED_SOURCE_HASHES[
            DEFAULT_SPECIES_GROUPS_PATH
        ],
        "manifest_source_table_canonical_sha256": EXPECTED_SOURCE_HASHES[DEFAULT_MANIFEST_PATH],
        "coverage_resolution_source_table_canonical_sha256": EXPECTED_SOURCE_HASHES[
            DEFAULT_COVERAGE_RESOLUTIONS_PATH
        ],
    }
    for column, expected_hash in expected_hash_columns.items():
        if str(row[column]) != expected_hash:
            raise ValueError(f"Unexpected source hash in {column}")

    policy_text = (root / DEFAULT_SPECIES_GROUPS_PATH).read_text(encoding="utf-8-sig")
    for fragment in (
        "short_lived_controls:",
        "  mouse:",
        "      - Mus musculus",
        "    group: short_lived_control",
    ):
        if fragment not in policy_text:
            raise ValueError(f"Mouse policy fragment missing: {fragment}")

    manifest = pl.read_csv(root / DEFAULT_MANIFEST_PATH)
    manifest_row = _single_row(
        manifest.filter(pl.col("candidate_id") == "tp53_mdm2_elephant_seed_mdm2_chain"),
        "MDM2 manifest",
    )
    for column, expected_value in {
        "pdb_id": "1ycr",
        "chain": "A",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "target_species": "elephant",
    }.items():
        if str(manifest_row[column]) != expected_value:
            raise ValueError(f"MDM2 manifest {column} changed")

    resolutions = pl.read_csv(root / DEFAULT_COVERAGE_RESOLUTIONS_PATH)
    resolution_row = _single_row(
        resolutions.filter(pl.col("candidate_id") == "tp53_mdm2_elephant_seed_mdm2_chain"),
        "MDM2 coverage resolution",
    )
    if str(resolution_row["coverage_repair_outcome"]) != ("coverage_repaired_and_ready"):
        raise ValueError("MDM2 coverage is no longer ready")
    if str(resolution_row["target_uniprot_after_resolution"]) != "G3SX30":
        raise ValueError("Elephant MDM2 accession changed")
    strict_panel_allowed = resolution_row["strict_panel_allowed_after_resolution"]
    if not (strict_panel_allowed is True or str(strict_panel_allowed).strip().lower() == "true"):
        raise ValueError("MDM2 strict-panel planning is no longer allowed")

    expected_result = {
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "pdb_id": "1ycr",
        "chain": "A",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "gene_symbol": "MDM2",
        "selected_control_species": "mouse",
        "selected_control_species_name": "Mus musculus",
        "selected_control_species_taxid": "10090",
        "species_group": "short_lived_control",
        "target_protein_accession": "P23804",
        "evidence_source_database": "UniProtKB Swiss-Prot",
        "evidence_source_accession": "P23804",
        "evidence_source_review_status": "reviewed",
        "sequence_status": "complete",
        "sequence_length": "489",
        "protein_existence_status": "evidence_at_protein_level",
        "review_decision": ("accept_reviewed_swissprot_for_gate7_technical_planning"),
        "selection_outcome": "ready_for_gate7_strict_panel_planning",
        "coverage_preflight_status_after_selection": ("coverage_preflight_ready"),
        "control_readiness_status_after_selection": "controls_ready",
        "contrast_readiness_status_after_selection": ("eligible_for_contrast_dry_run"),
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "strict_panel_readiness",
        "strict_panel_row_allowed": "true",
        "gate7_mdm2_strict_panel_status_after_selection": ("strict_panel_ready"),
        "gate7_mdm2_contrast_dry_run_allowed_after_selection": "true",
        "aggregate_gate7_blocker_code": "tp53_deferred_pending_source",
        "exact_local_embedding_status": ("not_evaluated_not_required_for_gate7_source_selection"),
    }
    for column, expected_value in expected_result.items():
        if str(row[column]) != expected_value:
            raise ValueError(f"Unexpected result {column}")

    for field in FALSE_BOUNDARY_FIELDS:
        if str(row[field]) != "false":
            raise ValueError(f"Forbidden boundary opened: {field}")


def strict_panel_rows(results: pl.DataFrame) -> pl.DataFrame:
    validate_results(results)
    row = _single_row(results, "short-lived control result")

    return pl.DataFrame(
        [
            {
                "candidate_set": str(row["candidate_set"]),
                "lane_name": str(row["lane_name"]),
                "candidate_id": str(row["candidate_id"]),
                "pdb_id": str(row["pdb_id"]),
                "chain": str(row["chain"]),
                "source_uniprot": str(row["source_uniprot"]),
                "priority": str(row["priority"]),
                "target_species": str(row["selected_control_species"]),
                "target_species_taxid": int(str(row["selected_control_species_taxid"])),
                "species_group": str(row["species_group"]),
                "coverage_preflight_status": str(row["coverage_preflight_status_after_selection"]),
                "control_readiness_status": str(row["control_readiness_status_after_selection"]),
                "contrast_readiness_status": str(row["contrast_readiness_status_after_selection"]),
                "claim_policy": str(row["claim_policy"]),
            }
        ]
    )
