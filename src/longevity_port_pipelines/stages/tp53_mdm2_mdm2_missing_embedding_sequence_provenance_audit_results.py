"""TP53/MDM2 missing-embedding exact-sequence provenance audit helpers.

This module validates committed provenance for the two MDM2 strict-panel
accessions whose exact local ESMC embeddings are missing: mouse P23804 and
hamster A0ABM2YB85.

It reads committed tables only. It does not fetch sequences, call BioHub/ESMC,
generate embeddings, write data/output, promote gates, run contrast, or make
biological claims.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

DEFAULT_SHORT_LIVED_SOURCE_TABLE = Path("data/input/tp53_mdm2_mdm2_short_lived_control_results.csv")
DEFAULT_HAMSTER_REVIEW_TABLE = Path(
    "data/input/tp53_mdm2_hamster_mdm2_complete_sequence_review_results.csv"
)
DEFAULT_GATE8_LOCAL_AUDIT_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_gate8_local_prerequisite_audit_results.csv"
)
DEFAULT_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_missing_embedding_sequence_provenance_audit_results.csv"
)
DEFAULT_DATA_INPUT_DIR = Path("data/input")

EXPECTED_HAMSTER_SHA256 = "77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

ACCESSION_FIELDS = (
    "candidate_accession",
    "target_accession",
    "target_protein_accession",
    "evidence_source_accession",
    "source_accession",
    "accession",
)
SHA256_FIELDS = (
    "sequence_sha256",
    "reviewed_sequence_sha256",
)

RESULT_FIELDS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "target_species",
    "target_species_name",
    "target_taxid",
    "target_accession",
    "target_accession_db",
    "expected_sequence_length",
    "source_gate7_table",
    "source_gate7_row_index",
    "source_gate7_selection_outcome",
    "source_gate7_strict_panel_row_allowed",
    "source_gate8_local_audit_table",
    "source_gate8_local_audit_row_index",
    "source_gate8_local_embedding_status",
    "source_identity_provenance",
    "source_identity_provenance_ready",
    "source_identity_reference",
    "committed_exact_sequence_sha256",
    "committed_exact_sequence_sha256_status",
    "committed_exact_sequence_sha256_reference",
    "exact_sequence_bytes_committed",
    "exact_sequence_bytes_local_binding_status",
    "external_exact_sequence_endpoint",
    "external_exact_sequence_endpoint_status",
    "external_exact_sequence_bytes_bindable",
    "external_exact_sequence_bytes_bound",
    "controlled_fill_sequence_input_status",
    "runtime_blocker_code",
    "later_controlled_embedding_fill_input_allowed",
    "allowed_next_action",
    "panel_source_identity_ready_accessions",
    "panel_sha256_ready_accessions",
    "panel_sha256_missing_accessions",
    "panel_exact_sequence_bytes_bound_accessions",
    "panel_sequence_provenance_status",
    "panel_runtime_blocker_code",
    "later_missing_embedding_fill_manifest_allowed",
    "panel_allowed_next_action",
    "sequence_fetch_performed",
    "biohub_called",
    "esmc_called",
    "embeddings_generated",
    "npy_artifact_created",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "contrast_run",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "claim_policy",
    "claim_status",
    "audit_note",
)

NO_SIDE_EFFECT_FIELDS = (
    "sequence_fetch_performed",
    "biohub_called",
    "esmc_called",
    "embeddings_generated",
    "npy_artifact_created",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "contrast_run",
    "gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file as dictionaries."""

    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _find_single(
    rows: list[dict[str, str]],
    *,
    field: str,
    value: str,
    source: Path,
) -> tuple[int, dict[str, str]]:
    matches = [
        (index, row)
        for index, row in enumerate(rows, start=1)
        if row.get(field, "").strip() == value
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {field}={value!r} row in {source}, found {len(matches)}"
        )
    return matches[0]


def _require(row: dict[str, str], field: str, expected: str) -> None:
    actual = row.get(field, "").strip()
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def _repo_relative(path: Path) -> str:
    return path.as_posix()


def discover_committed_accession_hashes(
    data_input_dir: Path,
    accession: str,
) -> list[tuple[str, int, str, str]]:
    """Find committed exact SHA-256 values on rows keyed to an exact accession."""

    findings: list[tuple[str, int, str, str]] = []
    for path in sorted(data_input_dir.rglob("*.csv")):
        try:
            rows = read_csv_rows(path)
        except (OSError, UnicodeError, csv.Error):
            continue

        for index, row in enumerate(rows, start=1):
            exact_accession_match = any(
                row.get(field, "").strip() == accession for field in ACCESSION_FIELDS
            )
            if not exact_accession_match:
                continue

            for hash_field in SHA256_FIELDS:
                value = row.get(hash_field, "").strip().lower()
                if SHA256_PATTERN.fullmatch(value):
                    canonical_path = (
                        DEFAULT_DATA_INPUT_DIR / path.relative_to(data_input_dir)
                    ).as_posix()
                    findings.append(
                        (
                            canonical_path,
                            index,
                            hash_field,
                            value,
                        )
                    )

    return findings


def _hash_reference(
    findings: list[tuple[str, int, str, str]],
) -> str:
    if not findings:
        return "not_applicable_no_committed_exact_sequence_sha256"
    return "|".join(f"{path}#{index}:{field}" for path, index, field, _value in findings)


def build_expected_rows(
    short_lived_rows: list[dict[str, str]],
    hamster_review_rows: list[dict[str, str]],
    gate8_local_audit_rows: list[dict[str, str]],
    *,
    data_input_dir: Path = DEFAULT_DATA_INPUT_DIR,
) -> list[dict[str, str]]:
    """Build the two committed provenance-audit rows from committed sources."""

    mouse_index, mouse = _find_single(
        short_lived_rows,
        field="selected_control_species",
        value="mouse",
        source=DEFAULT_SHORT_LIVED_SOURCE_TABLE,
    )
    hamster_index, hamster = _find_single(
        short_lived_rows,
        field="selected_control_species",
        value="hamster",
        source=DEFAULT_SHORT_LIVED_SOURCE_TABLE,
    )
    hamster_review_index, hamster_review = _find_single(
        hamster_review_rows,
        field="candidate_accession",
        value="A0ABM2YB85",
        source=DEFAULT_HAMSTER_REVIEW_TABLE,
    )
    mouse_audit_index, mouse_audit = _find_single(
        gate8_local_audit_rows,
        field="target_accession",
        value="P23804",
        source=DEFAULT_GATE8_LOCAL_AUDIT_TABLE,
    )
    hamster_audit_index, hamster_audit = _find_single(
        gate8_local_audit_rows,
        field="target_accession",
        value="A0ABM2YB85",
        source=DEFAULT_GATE8_LOCAL_AUDIT_TABLE,
    )

    for row, accession, species, taxid, length in [
        (mouse, "P23804", "mouse", "10090", "489"),
        (hamster, "A0ABM2YB85", "hamster", "10036", "510"),
    ]:
        _require(row, "target_protein_accession", accession)
        _require(row, "selected_control_species", species)
        _require(row, "selected_control_species_taxid", taxid)
        _require(row, "sequence_length", length)
        _require(row, "selection_outcome", "ready_for_gate7_strict_panel_planning")
        _require(row, "strict_panel_row_allowed", "true")
        _require(row, "gate7_mdm2_strict_panel_status_after_selection", "strict_panel_ready")
        _require(
            row,
            "gate7_mdm2_contrast_dry_run_allowed_after_selection",
            "true",
        )
        _require(row, "gate8_entry_allowed", "false")
        _require(row, "gate9_promoted", "false")
        _require(row, "biological_claim_made", "false")

    _require(mouse, "evidence_source_database", "UniProtKB Swiss-Prot")
    _require(mouse, "evidence_source_review_status", "reviewed")
    _require(mouse, "sequence_status", "complete")

    _require(hamster_review, "candidate_accession", "A0ABM2YB85")
    _require(hamster_review, "source_database", "UniProtKB TrEMBL")
    _require(hamster_review, "source_record_status", "active_unreviewed")
    _require(hamster_review, "sequence_length", "510")
    _require(hamster_review, "sequence_sha256", EXPECTED_HAMSTER_SHA256)
    _require(hamster_review, "identity_status", "pass")
    _require(hamster_review, "project_accession_accepted", "true")
    _require(hamster_review, "sequence_group_accepted", "true")
    _require(
        hamster_review,
        "canonical_biological_isoform_claimed",
        "false",
    )
    _require(
        hamster_review,
        "strict_panel_row_allowed_after_decision",
        "true",
    )
    _require(hamster_review, "raw_sequence_committed", "false")

    _require(mouse_audit, "local_embedding_status", "missing")
    _require(mouse_audit, "runtime_blocker_code", "missing_exact_local_embedding")
    _require(hamster_audit, "local_embedding_status", "missing")
    _require(
        hamster_audit,
        "runtime_blocker_code",
        "missing_exact_local_embedding",
    )

    mouse_hashes = discover_committed_accession_hashes(
        data_input_dir,
        "P23804",
    )
    hamster_hashes = discover_committed_accession_hashes(
        data_input_dir,
        "A0ABM2YB85",
    )

    if mouse_hashes:
        raise ValueError(
            "P23804 unexpectedly has a committed exact sequence SHA-256; "
            "the audit result must be recomputed."
        )

    hamster_values = {value for *_prefix, value in hamster_hashes}
    if hamster_values != {EXPECTED_HAMSTER_SHA256}:
        raise ValueError(
            "Expected exactly the accepted A0ABM2YB85 SHA-256 value in "
            f"committed provenance rows, got {sorted(hamster_values)}"
        )

    common = {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "gene_symbol": "MDM2",
        "source_gate7_table": _repo_relative(DEFAULT_SHORT_LIVED_SOURCE_TABLE),
        "source_gate8_local_audit_table": _repo_relative(DEFAULT_GATE8_LOCAL_AUDIT_TABLE),
        "source_gate8_local_embedding_status": "missing",
        "exact_sequence_bytes_committed": "false",
        "exact_sequence_bytes_local_binding_status": ("not_bound_no_committed_sequence_bytes"),
        "external_exact_sequence_endpoint_status": (
            "official_accession_endpoint_identified_not_fetched"
        ),
        "external_exact_sequence_bytes_bindable": "true",
        "external_exact_sequence_bytes_bound": "false",
        "panel_source_identity_ready_accessions": ("P23804|A0ABM2YB85"),
        "panel_sha256_ready_accessions": "A0ABM2YB85",
        "panel_sha256_missing_accessions": "P23804",
        "panel_exact_sequence_bytes_bound_accessions": "none",
        "panel_sequence_provenance_status": (
            "blocked_pending_exact_sequence_bindings_and_mouse_hash"
        ),
        "panel_runtime_blocker_code": (
            "missing_p23804_exact_sequence_sha256_and_both_non_committed_sequence_bindings"
        ),
        "later_missing_embedding_fill_manifest_allowed": "false",
        "panel_allowed_next_action": (
            "prepare_external_non_committed_exact_sequence_bindings_and_mouse_hash_review"
        ),
        "sequence_fetch_performed": "false",
        "biohub_called": "false",
        "esmc_called": "false",
        "embeddings_generated": "false",
        "npy_artifact_created": "false",
        "npy_artifact_committed": "false",
        "data_output_artifact_committed": "false",
        "contrast_run": "false",
        "gate8_entry_allowed": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_sequence_provenance_audit",
    }

    mouse_row = {
        **common,
        "target_species": "mouse",
        "target_species_name": mouse["selected_control_species_name"],
        "target_taxid": mouse["selected_control_species_taxid"],
        "target_accession": "P23804",
        "target_accession_db": mouse["evidence_source_database"],
        "expected_sequence_length": "489",
        "source_gate7_row_index": str(mouse_index),
        "source_gate7_selection_outcome": mouse["selection_outcome"],
        "source_gate7_strict_panel_row_allowed": mouse["strict_panel_row_allowed"],
        "source_gate8_local_audit_row_index": str(mouse_audit_index),
        "source_identity_provenance": (
            "reviewed_swissprot_accession_identity_confirmed_for_gate7_technical_planning"
        ),
        "source_identity_provenance_ready": "true",
        "source_identity_reference": mouse["evidence_reference"],
        "committed_exact_sequence_sha256": "not_committed",
        "committed_exact_sequence_sha256_status": ("missing_not_committed"),
        "committed_exact_sequence_sha256_reference": (
            "not_applicable_no_committed_exact_sequence_sha256"
        ),
        "external_exact_sequence_endpoint": ("https://rest.uniprot.org/uniprotkb/P23804.fasta"),
        "controlled_fill_sequence_input_status": (
            "blocked_missing_committed_sha256_and_non_committed_exact_sequence_binding"
        ),
        "runtime_blocker_code": (
            "missing_exact_sequence_sha256_and_non_committed_sequence_bytes_binding"
        ),
        "later_controlled_embedding_fill_input_allowed": "false",
        "allowed_next_action": (
            "prepare_external_non_committed_p23804_sequence_binding_and_hash_review"
        ),
        "audit_note": (
            "Reviewed Swiss-Prot identity and complete 489-aa metadata are "
            "committed for P23804, but no exact sequence SHA-256 or sequence "
            "bytes binding is committed. The official accession endpoint is "
            "identified for a later external non-committed materialization "
            "and hash-review step."
        ),
    }

    hamster_row = {
        **common,
        "target_species": "hamster",
        "target_species_name": hamster["selected_control_species_name"],
        "target_taxid": hamster["selected_control_species_taxid"],
        "target_accession": "A0ABM2YB85",
        "target_accession_db": hamster["evidence_source_database"],
        "expected_sequence_length": "510",
        "source_gate7_row_index": str(hamster_index),
        "source_gate7_selection_outcome": hamster["selection_outcome"],
        "source_gate7_strict_panel_row_allowed": hamster["strict_panel_row_allowed"],
        "source_gate8_local_audit_row_index": str(hamster_audit_index),
        "source_identity_provenance": (
            "accepted_complete_uniprot_refseq_sequence_group_identity_"
            "confirmed_for_gate7_technical_planning"
        ),
        "source_identity_provenance_ready": "true",
        "source_identity_reference": (
            f"{_repo_relative(DEFAULT_HAMSTER_REVIEW_TABLE)}#{hamster_review_index}"
        ),
        "committed_exact_sequence_sha256": EXPECTED_HAMSTER_SHA256,
        "committed_exact_sequence_sha256_status": "present_committed",
        "committed_exact_sequence_sha256_reference": _hash_reference(hamster_hashes),
        "external_exact_sequence_endpoint": ("https://rest.uniprot.org/uniprotkb/A0ABM2YB85.fasta"),
        "controlled_fill_sequence_input_status": (
            "blocked_pending_non_committed_exact_sequence_binding"
        ),
        "runtime_blocker_code": ("missing_non_committed_sequence_bytes_binding"),
        "later_controlled_embedding_fill_input_allowed": "false",
        "allowed_next_action": (
            "prepare_external_non_committed_a0abm2yb85_sequence_binding_and_verify_committed_hash"
        ),
        "audit_note": (
            "A0ABM2YB85 has accepted complete-sequence identity, a committed "
            "510-aa exact sequence SHA-256 corroborated by XP_040610761.1, "
            "and an official accession endpoint. Exact sequence bytes remain "
            "unbound and must be materialized externally without committing "
            "raw sequence bytes before a later controlled embedding fill."
        ),
    }

    rows = [mouse_row, hamster_row]
    return [{field: row[field] for field in RESULT_FIELDS} for row in rows]


def validate_result_rows(
    rows: list[dict[str, str]],
    short_lived_rows: list[dict[str, str]],
    hamster_review_rows: list[dict[str, str]],
    gate8_local_audit_rows: list[dict[str, str]],
    *,
    data_input_dir: Path = DEFAULT_DATA_INPUT_DIR,
) -> None:
    """Validate the committed two-row result against committed sources."""

    if len(rows) != 2:
        raise ValueError(f"Expected exactly two result rows, found {len(rows)}")

    for row in rows:
        missing = [field for field in RESULT_FIELDS if field not in row]
        if missing:
            raise ValueError(f"Missing result fields: {missing}")
        for field in NO_SIDE_EFFECT_FIELDS:
            _require(row, field, "false")

    expected = build_expected_rows(
        short_lived_rows,
        hamster_review_rows,
        gate8_local_audit_rows,
        data_input_dir=data_input_dir,
    )
    if rows != expected:
        raise ValueError("Committed sequence-provenance audit rows differ from expected rows")


def load_and_validate_result(
    result_table: Path = DEFAULT_RESULT_TABLE,
    short_lived_table: Path = DEFAULT_SHORT_LIVED_SOURCE_TABLE,
    hamster_review_table: Path = DEFAULT_HAMSTER_REVIEW_TABLE,
    gate8_local_audit_table: Path = DEFAULT_GATE8_LOCAL_AUDIT_TABLE,
    *,
    data_input_dir: Path = DEFAULT_DATA_INPUT_DIR,
) -> list[dict[str, str]]:
    """Load and validate the committed result table."""

    rows = read_csv_rows(result_table)
    validate_result_rows(
        rows,
        read_csv_rows(short_lived_table),
        read_csv_rows(hamster_review_table),
        read_csv_rows(gate8_local_audit_table),
        data_input_dir=data_input_dir,
    )
    return rows
