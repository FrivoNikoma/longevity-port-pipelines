# Validate the rat MDM2 accession review result.

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import polars as pl

DEFAULT_RESULTS_PATH = Path("data/input/tp53_mdm2_rat_mdm2_accession_review_results.csv")
DEFAULT_CONTROL_RESULTS_PATH = Path("data/input/tp53_mdm2_mdm2_short_lived_control_results.csv")
REVIEW_SOURCE_CONTROL_SHA256 = "769d0006f72a86d55f61eaa810c517d437750e39478c6fbacfa9fb3dc923be12"
EXPECTED_BLOCKER = "no_unambiguous_canonical_rat_mdm2_sequence"

REQUIRED_COLUMNS = [
    "candidate_set",
    "lane_name",
    "candidate_id",
    "selected_control_species",
    "selected_control_species_name",
    "selected_control_species_taxid",
    "gene_symbol",
    "reference_accession",
    "candidate_accession",
    "source_database",
    "source_record_status",
    "sequence_length",
    "sequence_sha256",
    "exact_match_to_reference",
    "length_delta_vs_reference",
    "reference_exact_subsequence_of_candidate",
    "candidate_exact_subsequence_of_reference",
    "candidate_disposition",
    "disposition_reason",
    "canonical_project_accession_accepted",
    "blocker_code",
    "evidence_source_reference",
    "evidence_checked_date",
    "review_source_type",
    "short_lived_control_results_canonical_sha256",
    "repository_live_calls_performed",
    "contrast_run",
    "biohub_called",
    "esmc_called",
    "embeddings_generated",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate8_entry_allowed",
    "gate9_promoted",
    "biological_claim_made",
]
FALSE_FIELDS = [
    "canonical_project_accession_accepted",
    "repository_live_calls_performed",
    "contrast_run",
    "biohub_called",
    "esmc_called",
    "embeddings_generated",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate8_entry_allowed",
    "gate9_promoted",
    "biological_claim_made",
]


def canonical_text_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def read_results(
    path: Path = DEFAULT_RESULTS_PATH,
) -> pl.DataFrame:
    rows = pl.read_csv(path, infer_schema_length=0)
    validate_results(rows)
    return rows


def _false(value: Any) -> bool:
    return str(value).strip().lower() == "false"


def _validate_current_rat_control_row(root: Path) -> None:
    controls = pl.read_csv(
        root / DEFAULT_CONTROL_RESULTS_PATH,
        infer_schema_length=0,
    )
    rat_rows = controls.filter(pl.col("selected_control_species") == "rat")
    if rat_rows.height != 1:
        raise ValueError(f"Expected one current rat control row, got {rat_rows.height}")

    rat = rat_rows.row(0, named=True)
    expected = {
        "selected_control_species_name": "Rattus norvegicus",
        "selected_control_species_taxid": "10116",
        "target_protein_accession": "NP_001426446.1",
        "evidence_source_accession": ("GeneID:314856|NP_001426446.1|A0A0G2JVC1|A6IGT1|D3ZVH5"),
        "review_decision": ("defer_rat_pending_unambiguous_canonical_sequence_source"),
        "selection_outcome": "deferred_pending_source",
        "blocker_code": EXPECTED_BLOCKER,
        "claim_status": "terminal_source_blocker",
        "strict_panel_row_allowed": "false",
    }
    for column, expected_value in expected.items():
        if str(rat[column]) != expected_value:
            raise ValueError(f"Current rat control row changed: {column}")


def validate_results(
    rows: pl.DataFrame,
    *,
    root: Path = Path("."),
) -> None:
    if list(rows.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Unexpected review columns: {rows.columns}")
    if rows.height != 4:
        raise ValueError(f"Expected four accession rows, got {rows.height}")
    _validate_current_rat_control_row(root)

    expected = {
        "NP_001426446.1": (
            "validated",
            "434",
            "true",
            "evidence_anchor_not_canonical_project_accession",
        ),
        "A0A0G2JVC1": (
            "active_unreviewed",
            "483",
            "false",
            "not_exact_accession_level_match",
        ),
        "A6IGT1": (
            "inactive",
            "0",
            "false",
            "excluded_inactive_accession",
        ),
        "D3ZVH5": (
            "active_unreviewed",
            "458",
            "false",
            "distinct_unreviewed_sequence_not_exact_match",
        ),
    }
    by_accession = {str(row["candidate_accession"]): row for row in rows.iter_rows(named=True)}
    if set(by_accession) != set(expected):
        raise ValueError(f"Unexpected accessions: {sorted(by_accession)}")

    for accession, values in expected.items():
        row = by_accession[accession]
        status, length, exact, disposition = values
        checks = {
            "selected_control_species": "rat",
            "selected_control_species_taxid": "10116",
            "reference_accession": "NP_001426446.1",
            "source_record_status": status,
            "sequence_length": length,
            "exact_match_to_reference": exact,
            "candidate_disposition": disposition,
            "blocker_code": EXPECTED_BLOCKER,
            "short_lived_control_results_canonical_sha256": (REVIEW_SOURCE_CONTROL_SHA256),
        }
        for column, value in checks.items():
            if str(row[column]) != value:
                raise ValueError(f"Unexpected {accession}:{column}")
        for field in FALSE_FIELDS:
            if not _false(row[field]):
                raise ValueError(f"Forbidden boundary opened: {accession}:{field}")

    a0 = by_accession["A0A0G2JVC1"]
    if str(a0["length_delta_vs_reference"]) != "49":
        raise ValueError("Unexpected A0A0G2JVC1 length delta")
    if str(a0["reference_exact_subsequence_of_candidate"]) != "true":
        raise ValueError("RefSeq subsequence relation changed")

    a6 = by_accession["A6IGT1"]
    if str(a6["candidate_disposition"]) != ("excluded_inactive_accession"):
        raise ValueError("A6IGT1 is no longer excluded")

    d3 = by_accession["D3ZVH5"]
    for field in (
        "reference_exact_subsequence_of_candidate",
        "candidate_exact_subsequence_of_reference",
    ):
        if str(d3[field]) != "false":
            raise ValueError("D3ZVH5 sequence relation changed")
