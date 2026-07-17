# Validate the hamster MDM2 complete-sequence source review result.

from __future__ import annotations

from pathlib import Path

import polars as pl

DEFAULT_RESULTS_PATH = Path(
    "data/input/tp53_mdm2_hamster_mdm2_complete_sequence_review_results.csv"
)
DEFAULT_SHORT_LIVED_RESULTS_PATH = Path("data/input/tp53_mdm2_mdm2_short_lived_control_results.csv")

SELECTED_SHA256 = "77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5"
Q60524_SHA256 = "f5e0b35c24cf9ce7c11d9290214930b3787da380112024a37b9ce41909ba5d35"

REQUIRED_COLUMNS = [
    "review_id",
    "candidate_accession",
    "source_database",
    "source_record_status",
    "organism",
    "taxid",
    "gene_symbol",
    "source_gene_id",
    "protein_name",
    "sequence_length",
    "sequence_sha256",
    "sequence_status",
    "protein_existence",
    "cross_references",
    "exact_match_to_q60524",
    "length_delta_vs_q60524",
    "q60524_exact_subsequence_of_candidate",
    "candidate_exact_subsequence_of_q60524",
    "identity_status",
    "identity_problem",
    "sequence_group_id",
    "candidate_disposition",
    "project_accession_accepted",
    "sequence_group_accepted",
    "canonical_biological_isoform_claimed",
    "strict_panel_row_allowed_after_decision",
    "evidence_checked_date",
    "raw_sequence_committed",
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
    "source_reference",
    "review_note",
]

FALSE_BOUNDARY_FIELDS = [
    "canonical_biological_isoform_claimed",
    "raw_sequence_committed",
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


def read_results(
    path: Path = DEFAULT_RESULTS_PATH,
) -> pl.DataFrame:
    rows = pl.read_csv(path, infer_schema_length=0)
    validate_results(rows)
    return rows


def _row(
    rows: pl.DataFrame,
    accession: str,
) -> dict[str, object]:
    selected = rows.filter(pl.col("candidate_accession") == accession)
    if selected.height != 1:
        raise ValueError(f"Expected one row for {accession}, got {selected.height}")
    return selected.row(0, named=True)


def _is_true(value: object) -> bool:
    return str(value).strip().lower() == "true"


def validate_results(
    rows: pl.DataFrame,
    *,
    short_lived_results_path: Path = (DEFAULT_SHORT_LIVED_RESULTS_PATH),
) -> None:
    if list(rows.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Unexpected review columns: {rows.columns}")
    if rows.height != 20:
        raise ValueError(f"Expected 20 review rows, got {rows.height}")
    if rows["review_id"].n_unique() != rows.height:
        raise ValueError("Review IDs must be unique")
    if rows["candidate_accession"].n_unique() != rows.height:
        raise ValueError("Candidate accessions must be unique")

    for row in rows.iter_rows(named=True):
        if str(row["organism"]) != "Mesocricetus auratus":
            raise ValueError("Unexpected review organism")
        if str(row["taxid"]) != "10036":
            raise ValueError("Unexpected review taxid")
        for field in FALSE_BOUNDARY_FIELDS:
            if _is_true(row[field]):
                raise ValueError(f"Forbidden boundary opened: {row['candidate_accession']}:{field}")

    selected_group = rows.filter(pl.col("sequence_group_accepted") == "true")
    if set(selected_group["candidate_accession"].to_list()) != {"A0ABM2YB85", "XP_040610761.1"}:
        raise ValueError("Unexpected accepted complete sequence group")
    if set(selected_group["sequence_sha256"].to_list()) != {SELECTED_SHA256}:
        raise ValueError("Accepted accessions do not share one sequence")
    if set(selected_group["sequence_length"].to_list()) != {"510"}:
        raise ValueError("Accepted sequence length must be 510")
    if set(selected_group["source_gene_id"].to_list()) != {"101833011"}:
        raise ValueError("Accepted sequence group must resolve to GeneID 101833011")

    primary = rows.filter(pl.col("project_accession_accepted") == "true")
    if primary.height != 1:
        raise ValueError("Expected one accepted project accession")
    if primary.row(0, named=True)["candidate_accession"] != "A0ABM2YB85":
        raise ValueError("A0ABM2YB85 must be the project accession")
    if primary.row(0, named=True)["strict_panel_row_allowed_after_decision"] != "true":
        raise ValueError("Accepted project accession must enter the strict panel")

    refseq = _row(rows, "XP_040610761.1")
    if refseq["candidate_disposition"] != ("selected_complete_sequence_group_corroborating_refseq"):
        raise ValueError("RefSeq corroboration disposition changed")

    q60524 = _row(rows, "Q60524")
    if q60524["sequence_length"] != "466":
        raise ValueError("Q60524 length changed")
    if q60524["sequence_sha256"] != Q60524_SHA256:
        raise ValueError("Q60524 sequence hash changed")
    if q60524["sequence_status"] != ("fragment_non_terminal_positions_1,466"):
        raise ValueError("Q60524 must remain a fragment")
    if q60524["candidate_disposition"] != ("reviewed_fragment_evidence_anchor_not_selected"):
        raise ValueError("Q60524 evidence-anchor disposition changed")

    legacy = _row(rows, "AAC52425.1")
    if legacy["sequence_sha256"] != Q60524_SHA256:
        raise ValueError("AAC52425.1 must match the Q60524 fragment")
    if legacy["exact_match_to_q60524"] != "true":
        raise ValueError("AAC52425.1 must exactly match Q60524")

    for accession in (
        "A0ABM2YB85",
        "XP_040610761.1",
    ):
        candidate = _row(rows, accession)
        if candidate["exact_match_to_q60524"] != "false":
            raise ValueError("Selected group must remain distinct from Q60524")
        if candidate["q60524_exact_subsequence_of_candidate"] != "false":
            raise ValueError(
                "Q60524 must not be recorded as an exact subsequence of the selected group"
            )

    accepted_accessions = {
        "A0ABM2YB85",
        "XP_040610761.1",
    }
    for row in rows.iter_rows(named=True):
        accession = str(row["candidate_accession"])
        if accession in accepted_accessions:
            continue
        if _is_true(row["sequence_group_accepted"]):
            raise ValueError(f"Unexpected accepted sequence: {accession}")
        if _is_true(row["project_accession_accepted"]):
            raise ValueError(f"Unexpected project accession: {accession}")
        if _is_true(row["strict_panel_row_allowed_after_decision"]):
            raise ValueError(f"Unexpected strict-panel row: {accession}")

    short_lived = pl.read_csv(
        short_lived_results_path,
        infer_schema_length=0,
    )
    hamster = short_lived.filter(pl.col("selected_control_species") == "hamster")
    if hamster.height != 1:
        raise ValueError("Expected one integrated hamster result")
    integrated = hamster.row(0, named=True)
    expected_integrated = {
        "target_protein_accession": "A0ABM2YB85",
        "selection_outcome": ("ready_for_gate7_strict_panel_planning"),
        "blocker_code": "none",
        "strict_panel_row_allowed": "true",
    }
    for column, expected in expected_integrated.items():
        if str(integrated[column]) != expected:
            raise ValueError(f"Unexpected integrated hamster {column}")
