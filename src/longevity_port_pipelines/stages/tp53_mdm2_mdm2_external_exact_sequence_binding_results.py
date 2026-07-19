"""TP53/MDM2 external exact-sequence binding result helpers.

This module validates metadata-only committed bindings for the exact external,
non-committed P23804 and A0ABM2YB85 sequence inputs. Raw FASTA and normalized
sequence bytes remain outside the repository.

No BioHub/ESMC calls, embedding generation, .npy creation, contrast execution,
gate promotion, or biological claims are performed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_SOURCE_PROVENANCE_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_missing_embedding_sequence_provenance_audit_results.csv"
)
DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_mdm2_external_exact_sequence_binding_results.csv")

BINDING_ROOT_ENV = "LONGEVITY_PORT_EXTERNAL_SEQUENCE_BINDING_ROOT"
EXTERNAL_MANIFEST_RELATIVE_PATH = "tp53_mdm2_mdm2_external_exact_sequence_bindings.json"

P23804_SHA256 = "0841e7c8ebd6a4a9e9e051538600d8f201c6682b3246dfb95ba301ab6233a3e3"
A0ABM2YB85_SHA256 = "77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5"

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
FASTA_ACCESSION_PATTERN = re.compile(r"^(?:sp|tr)\|([^|]+)\|")

EXPECTED_BINDINGS = {
    "P23804": {
        "target_species": "mouse",
        "target_species_name": "Mus musculus",
        "target_taxid": "10090",
        "target_accession_db": "UniProtKB Swiss-Prot",
        "expected_sequence_length": "489",
        "expected_sequence_sha256": P23804_SHA256,
        "source_previous_sha256_status": "missing_not_committed",
        "source_previous_sha256": "not_committed",
        "raw_fasta_relative_path": "P23804.fasta",
        "normalized_sequence_relative_path": "P23804.sequence.txt",
        "source_url": "https://rest.uniprot.org/uniprotkb/P23804.fasta",
    },
    "A0ABM2YB85": {
        "target_species": "hamster",
        "target_species_name": "Mesocricetus auratus",
        "target_taxid": "10036",
        "target_accession_db": "UniProtKB TrEMBL and NCBI RefSeq",
        "expected_sequence_length": "510",
        "expected_sequence_sha256": A0ABM2YB85_SHA256,
        "source_previous_sha256_status": "present_committed",
        "source_previous_sha256": A0ABM2YB85_SHA256,
        "raw_fasta_relative_path": "A0ABM2YB85.fasta",
        "normalized_sequence_relative_path": "A0ABM2YB85.sequence.txt",
        "source_url": "https://rest.uniprot.org/uniprotkb/A0ABM2YB85.fasta",
    },
}

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
    "source_sequence_provenance_table",
    "source_sequence_provenance_row_index",
    "source_identity_provenance_ready",
    "source_previous_sha256_status",
    "source_previous_sha256",
    "external_binding_root_env",
    "external_binding_manifest_relative_path",
    "external_raw_fasta_relative_path",
    "external_raw_fasta_sha256",
    "external_normalized_sequence_relative_path",
    "external_normalized_sequence_sha256",
    "external_source_provider",
    "external_source_url",
    "external_fasta_header",
    "external_accession_verified",
    "external_taxid_verified",
    "external_length_verified",
    "external_sha256_verified",
    "external_binding_status",
    "raw_sequence_committed",
    "later_missing_embedding_fill_manifest_allowed",
    "allowed_next_action",
    "panel_binding_ready_accessions",
    "panel_binding_status",
    "panel_runtime_blocker_code",
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
    "binding_note",
)

NO_SIDE_EFFECT_FIELDS = (
    "raw_sequence_committed",
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
    """Read a UTF-8 CSV file."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(path: Path, rows: list[dict[str, str]]) -> None:
    """Write rows using the committed result field order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def sha256_bytes(data: bytes) -> str:
    """Return lowercase SHA-256."""
    return hashlib.sha256(data).hexdigest()


def _require(row: dict[str, str], field: str, expected: str) -> None:
    actual = row.get(field, "").strip()
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def _find_source_row(
    rows: list[dict[str, str]],
    accession: str,
) -> tuple[int, dict[str, str]]:
    matches = [
        (index, row)
        for index, row in enumerate(rows, start=1)
        if row.get("target_accession", "").strip() == accession
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one source provenance row for {accession}, found {len(matches)}"
        )
    return matches[0]


def _safe_relative_file(value: str, expected_name: str) -> str:
    path = Path(value)
    if (
        not value
        or path.is_absolute()
        or len(path.parts) != 1
        or path.name != expected_name
        or ".." in path.parts
        or "\\" in value
    ):
        raise ValueError(f"Expected safe relative filename {expected_name!r}, got {value!r}")
    return value


def parse_single_fasta(raw_bytes: bytes) -> tuple[str, str]:
    """Parse exactly one FASTA record."""
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("External FASTA is not UTF-8") from exc

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith(">"):
        raise ValueError("External FASTA has no header")
    if any(line.startswith(">") for line in lines[1:]):
        raise ValueError("Expected one external FASTA record")

    header = lines[0][1:]
    sequence = "".join(lines[1:]).upper()
    if not sequence:
        raise ValueError("External FASTA sequence is empty")
    if not sequence.isalpha() or not sequence.isascii():
        raise ValueError("External FASTA sequence contains invalid symbols")
    return header, sequence


def validate_external_binding_observation(
    *,
    binding_root: Path,
    manifest_row: dict[str, Any],
    accession: str,
) -> dict[str, str]:
    """Validate one external manifest row and its non-committed files."""
    expected = EXPECTED_BINDINGS[accession]

    if str(manifest_row.get("accession", "")) != accession:
        raise ValueError(f"Manifest accession mismatch for {accession}")

    raw_name = _safe_relative_file(
        str(manifest_row.get("raw_fasta_relative_path", "")),
        str(expected["raw_fasta_relative_path"]),
    )
    sequence_name = _safe_relative_file(
        str(manifest_row.get("normalized_sequence_relative_path", "")),
        str(expected["normalized_sequence_relative_path"]),
    )

    raw_path = binding_root / raw_name
    sequence_path = binding_root / sequence_name

    raw_bytes = raw_path.read_bytes()
    sequence_file_bytes = sequence_path.read_bytes()
    header, fasta_sequence = parse_single_fasta(raw_bytes)

    try:
        sequence_text = sequence_file_bytes.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{accession}: normalized sequence file is not ASCII") from exc

    if "\n" in sequence_text or "\r" in sequence_text:
        raise ValueError(f"{accession}: normalized sequence file contains line breaks")
    if sequence_text != fasta_sequence:
        raise ValueError(f"{accession}: normalized bytes differ from FASTA sequence")

    header_match = FASTA_ACCESSION_PATTERN.match(header)
    header_accession = header_match.group(1) if header_match else ""
    if header_accession != accession:
        raise ValueError(f"{accession}: FASTA header accession mismatch: {header!r}")

    expected_taxid = str(expected["target_taxid"])
    if f"OX={expected_taxid}" not in header:
        raise ValueError(f"{accession}: FASTA header lacks OX={expected_taxid}")

    expected_length = int(str(expected["expected_sequence_length"]))
    observed_length = len(sequence_text)
    if observed_length != expected_length:
        raise ValueError(
            f"{accession}: expected length {expected_length}, observed {observed_length}"
        )

    sequence_hash = sha256_bytes(sequence_file_bytes)
    expected_hash = str(expected["expected_sequence_sha256"])
    if sequence_hash != expected_hash:
        raise ValueError(
            f"{accession}: expected sequence SHA-256 {expected_hash}, observed {sequence_hash}"
        )

    raw_hash = sha256_bytes(raw_bytes)

    manifest_checks = {
        "source_provider": "UniProtKB REST API",
        "source_url": str(expected["source_url"]),
        "fasta_header": header,
        "expected_taxid": expected_taxid,
        "header_accession_verified": True,
        "header_taxid_verified": True,
        "expected_sequence_length": expected_length,
        "observed_sequence_length": expected_length,
        "sequence_length_verified": True,
        "expected_sequence_sha256": expected_hash,
        "observed_sequence_sha256": expected_hash,
        "sequence_sha256_verified": True,
        "raw_fasta_sha256": raw_hash,
        "normalized_sequence_file_sha256": expected_hash,
        "raw_sequence_committed": False,
        "biohub_called": False,
        "esmc_called": False,
        "embeddings_generated": False,
        "npy_artifact_created": False,
        "contrast_run": False,
        "gate8_promoted": False,
        "gate9_promoted": False,
        "biological_claim_made": False,
        "binding_status": ("passed_exact_external_non_committed_binding"),
    }
    for field, expected_value in manifest_checks.items():
        actual = manifest_row.get(field)
        if actual != expected_value:
            raise ValueError(
                f"{accession}: manifest {field} expected {expected_value!r}, got {actual!r}"
            )

    return {
        "external_raw_fasta_relative_path": raw_name,
        "external_raw_fasta_sha256": raw_hash,
        "external_normalized_sequence_relative_path": sequence_name,
        "external_normalized_sequence_sha256": sequence_hash,
        "external_source_provider": "UniProtKB REST API",
        "external_source_url": str(expected["source_url"]),
        "external_fasta_header": header,
        "external_accession_verified": "true",
        "external_taxid_verified": "true",
        "external_length_verified": "true",
        "external_sha256_verified": "true",
        "external_binding_status": ("passed_exact_external_non_committed_binding"),
    }


def load_external_manifest(path: Path) -> dict[str, Any]:
    """Read the external materialization manifest."""
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("External manifest must be a JSON object")
    return payload


def build_rows_from_external(
    *,
    source_rows: list[dict[str, str]],
    binding_root: Path,
    manifest_path: Path,
) -> list[dict[str, str]]:
    """Build two metadata-only result rows after external validation."""
    manifest = load_external_manifest(manifest_path)

    top_level_false = (
        "repository_files_written",
        "raw_sequence_committed",
        "biohub_called",
        "esmc_called",
        "embeddings_generated",
        "npy_artifact_created",
        "data_output_artifact_committed",
        "contrast_run",
        "gate8_promoted",
        "gate9_promoted",
        "biological_claim_made",
    )
    for field in top_level_false:
        if manifest.get(field) is not False:
            raise ValueError(f"External manifest requires {field}=false")

    manifest_rows = manifest.get("rows")
    if not isinstance(manifest_rows, list):
        raise ValueError("External manifest rows must be a list")

    by_accession: dict[str, dict[str, Any]] = {}
    for item in manifest_rows:
        if not isinstance(item, dict):
            raise ValueError("External manifest row must be an object")
        accession = str(item.get("accession", ""))
        if accession in by_accession:
            raise ValueError(f"Duplicate external manifest accession {accession}")
        by_accession[accession] = item

    if set(by_accession) != set(EXPECTED_BINDINGS):
        raise ValueError("External manifest must contain exactly P23804 and A0ABM2YB85")

    rows: list[dict[str, str]] = []
    for accession in ("P23804", "A0ABM2YB85"):
        expected = EXPECTED_BINDINGS[accession]
        source_index, source = _find_source_row(source_rows, accession)

        _require(source, "source_identity_provenance_ready", "true")
        _require(
            source,
            "expected_sequence_length",
            str(expected["expected_sequence_length"]),
        )
        _require(
            source,
            "committed_exact_sequence_sha256_status",
            str(expected["source_previous_sha256_status"]),
        )
        _require(
            source,
            "committed_exact_sequence_sha256",
            str(expected["source_previous_sha256"]),
        )
        _require(
            source,
            "external_exact_sequence_bytes_bound",
            "false",
        )
        _require(
            source,
            "later_missing_embedding_fill_manifest_allowed",
            "false",
        )

        observation = validate_external_binding_observation(
            binding_root=binding_root,
            manifest_row=by_accession[accession],
            accession=accession,
        )

        row = {
            "candidate_set": source["candidate_set"],
            "lane_name": source["lane_name"],
            "candidate_id": source["candidate_id"],
            "gene_symbol": "MDM2",
            "target_species": str(expected["target_species"]),
            "target_species_name": str(expected["target_species_name"]),
            "target_taxid": str(expected["target_taxid"]),
            "target_accession": accession,
            "target_accession_db": str(expected["target_accession_db"]),
            "expected_sequence_length": str(expected["expected_sequence_length"]),
            "source_sequence_provenance_table": (DEFAULT_SOURCE_PROVENANCE_TABLE.as_posix()),
            "source_sequence_provenance_row_index": str(source_index),
            "source_identity_provenance_ready": "true",
            "source_previous_sha256_status": str(expected["source_previous_sha256_status"]),
            "source_previous_sha256": str(expected["source_previous_sha256"]),
            "external_binding_root_env": BINDING_ROOT_ENV,
            "external_binding_manifest_relative_path": (EXTERNAL_MANIFEST_RELATIVE_PATH),
            **observation,
            "raw_sequence_committed": "false",
            "later_missing_embedding_fill_manifest_allowed": "true",
            "allowed_next_action": ("prepare_scoped_missing_embedding_fill_manifest_dry_run"),
            "panel_binding_ready_accessions": ("P23804|A0ABM2YB85"),
            "panel_binding_status": ("ready_for_scoped_missing_embedding_fill_manifest"),
            "panel_runtime_blocker_code": "none",
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
            "claim_policy": ("no_biological_claims_until_validation"),
            "claim_status": ("technical_external_sequence_binding_result"),
            "binding_note": (
                f"{accession} exact sequence bytes are externally "
                "materialized, accession/taxid/length/SHA-256 verified, "
                "and remain outside the repository. Permission applies "
                "only to a later scoped missing-embedding fill manifest "
                "dry run."
            ),
        }
        rows.append(row)

    validate_result_rows(rows, source_rows)
    return rows


def validate_result_rows(
    rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> None:
    """Validate committed metadata without requiring external files."""
    if len(rows) != 2:
        raise ValueError(f"Expected two binding result rows, got {len(rows)}")
    if [row.get("target_accession") for row in rows] != [
        "P23804",
        "A0ABM2YB85",
    ]:
        raise ValueError("Unexpected binding-result accession order")

    for row in rows:
        if set(row) != set(RESULT_FIELDS):
            missing = sorted(set(RESULT_FIELDS) - set(row))
            extra = sorted(set(row) - set(RESULT_FIELDS))
            raise ValueError(f"Result fields differ; missing={missing}, extra={extra}")

        accession = row["target_accession"]
        expected = EXPECTED_BINDINGS[accession]
        source_index, source = _find_source_row(source_rows, accession)

        _require(
            row,
            "source_sequence_provenance_table",
            DEFAULT_SOURCE_PROVENANCE_TABLE.as_posix(),
        )
        _require(
            row,
            "source_sequence_provenance_row_index",
            str(source_index),
        )
        _require(row, "source_identity_provenance_ready", "true")
        _require(source, "source_identity_provenance_ready", "true")
        _require(
            row,
            "expected_sequence_length",
            str(expected["expected_sequence_length"]),
        )
        _require(
            row,
            "source_previous_sha256_status",
            str(expected["source_previous_sha256_status"]),
        )
        _require(
            row,
            "source_previous_sha256",
            str(expected["source_previous_sha256"]),
        )

        _require(
            row,
            "external_binding_root_env",
            BINDING_ROOT_ENV,
        )
        _require(
            row,
            "external_binding_manifest_relative_path",
            EXTERNAL_MANIFEST_RELATIVE_PATH,
        )
        _safe_relative_file(
            row["external_raw_fasta_relative_path"],
            str(expected["raw_fasta_relative_path"]),
        )
        _safe_relative_file(
            row["external_normalized_sequence_relative_path"],
            str(expected["normalized_sequence_relative_path"]),
        )

        for hash_field in (
            "external_raw_fasta_sha256",
            "external_normalized_sequence_sha256",
        ):
            if not SHA256_PATTERN.fullmatch(row[hash_field]):
                raise ValueError(f"{accession}: invalid {hash_field}")

        _require(
            row,
            "external_normalized_sequence_sha256",
            str(expected["expected_sequence_sha256"]),
        )
        _require(
            row,
            "external_source_url",
            str(expected["source_url"]),
        )
        _require(
            row,
            "external_binding_status",
            "passed_exact_external_non_committed_binding",
        )
        for field in (
            "external_accession_verified",
            "external_taxid_verified",
            "external_length_verified",
            "external_sha256_verified",
            "later_missing_embedding_fill_manifest_allowed",
        ):
            _require(row, field, "true")

        _require(
            row,
            "allowed_next_action",
            "prepare_scoped_missing_embedding_fill_manifest_dry_run",
        )
        _require(
            row,
            "panel_binding_ready_accessions",
            "P23804|A0ABM2YB85",
        )
        _require(
            row,
            "panel_binding_status",
            "ready_for_scoped_missing_embedding_fill_manifest",
        )
        _require(row, "panel_runtime_blocker_code", "none")

        for field in NO_SIDE_EFFECT_FIELDS:
            _require(row, field, "false")


def load_and_validate_result(
    result_path: Path = DEFAULT_RESULT_TABLE,
    source_path: Path = DEFAULT_SOURCE_PROVENANCE_TABLE,
) -> list[dict[str, str]]:
    """Load and validate the committed result."""
    rows = read_csv_rows(result_path)
    source_rows = read_csv_rows(source_path)
    validate_result_rows(rows, source_rows)
    return rows
