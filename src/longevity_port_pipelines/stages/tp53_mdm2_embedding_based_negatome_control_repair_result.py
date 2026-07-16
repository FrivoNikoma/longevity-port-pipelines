"""Validate the TP53/MDM2 embedding-based NEGATOME repair/retry result."""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

DEFAULT_MAPPING_TABLE = Path("data/input/tp53_mdm2_1ycr_q00987_interface_mapping.csv")
DEFAULT_PAIR_TABLE = Path("data/input/tp53_mdm2_repaired_negatome_control_pairs.csv")
DEFAULT_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_embedding_based_negatome_control_repair_results.csv"
)

EXPECTED_MAPPING_COLUMNS = [
    "structure_id",
    "structure_model",
    "chain",
    "source_uniprot",
    "chain_local_zero_based_index",
    "pdb_residue_label",
    "pdb_residue_number",
    "full_length_zero_based_index",
    "full_length_one_based_position",
    "residue_one_letter",
    "residue_identity_consistent",
    "mapping_offset",
    "mapping_source",
]
EXPECTED_PAIR_COLUMNS = [
    "complex_id",
    "chain",
    "target_species",
    "source_uniprot",
    "negative_partner_uniprot",
    "negative_partner_source",
    "negative_partner_sequence",
    "control_type",
]
EXPECTED_RESULT_COLUMNS = [
    "candidate_set",
    "lane_name",
    "result_id",
    "result_status",
    "result_scope",
    "source_first_attempt_table",
    "source_first_attempt_row_index",
    "source_first_attempt_status",
    "source_first_attempt_metadata_sha256",
    "audit_helper_name",
    "audit_helper_sha256",
    "audit_report_sha256",
    "audit_summary_sha256",
    "audit_candidate_pair_sha256",
    "audit_outcome",
    "audit_timestamp_utc",
    "audit_read_only",
    "official_retrieval_performed",
    "rcsb_structure_id",
    "rcsb_model",
    "rcsb_pdb_url",
    "rcsb_pdb_sha256",
    "rcsb_cif_url",
    "rcsb_cif_sha256",
    "committed_interface_table",
    "committed_interface_row_index",
    "committed_pdb_sha256",
    "current_pdb_sha256",
    "pdb_sha_matches_committed_extraction",
    "committed_interface_contract_revalidated",
    "human_reference_accession",
    "human_reference_taxid",
    "human_sequence_length",
    "human_sequence_sha256",
    "human_embedding_path",
    "human_embedding_shape",
    "human_embedding_dtype",
    "human_embedding_finite",
    "human_embedding_sha256",
    "human_embedding_invariant_pass",
    "elephant_target_accession",
    "elephant_target_taxid",
    "elephant_sequence_length",
    "elephant_sequence_sha256",
    "elephant_embedding_path",
    "elephant_embedding_shape",
    "elephant_embedding_dtype",
    "elephant_embedding_finite",
    "elephant_embedding_sha256",
    "elephant_embedding_invariant_pass",
    "mapping_table",
    "mapping_table_sha256",
    "mapping_row_count",
    "mapping_offset",
    "mapping_unique",
    "mapped_interface_count",
    "mapped_indices_unique",
    "mapped_indices_in_bounds",
    "residue_identity_consistent",
    "mapped_full_length_zero_based_indices",
    "mapping_invariants_pass",
    "negative_partner_gene_id",
    "negative_partner_transcript_id",
    "negative_partner_translation_id",
    "negative_partner_uniprot",
    "negative_partner_taxid",
    "negative_partner_sequence_length",
    "negative_partner_sequence_sha256",
    "negative_partner_cross_source_sequence_exact_match",
    "negative_partner_sequence_deterministic",
    "reported_w23g_alignment_consistent",
    "protein_level_negative_partner_resolved",
    "negative_partner_uniprot_source_reference",
    "negative_partner_ensembl_gene_source_reference",
    "negative_partner_ensembl_translation_source_reference",
    "repaired_pair_table",
    "repaired_pair_table_sha256",
    "repaired_pair_runtime_loadable",
    "exact_negatome_lookup_key",
    "exact_pair_schema_valid",
    "exact_pair_row_count",
    "negative_partner_embedding_path",
    "negative_partner_embedding_exists",
    "negative_partner_embedding_shape",
    "negative_partner_embedding_dtype",
    "negative_partner_embedding_finite",
    "negative_partner_embedding_sha256",
    "negative_partner_embedding_invariant_pass",
    "checked_blocker_count",
    "checked_blocker",
    "control_retry_attempted",
    "control_ratio_runtime_executed",
    "control_ratio_runtime_function",
    "control_ratio_runtime_skip_reason",
    "embedding_based_negatome_control_computed",
    "negatome_control_ratio_available",
    "negatome_control_ratio",
    "proposed_gate6_repair_status",
    "gate6_control_readiness_resolved_after",
    "gate6_control_closure_blocked_after",
    "gate7_entry_allowed_after",
    "gate8_promoted",
    "gate9_promoted",
    "biohub_esmc_called",
    "new_embeddings_generated",
    "npy_artifact_written",
    "npy_artifact_committed",
    "data_output_artifact_committed",
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

EXPECTED_CHAIN_LOCAL_INDICES = [
    0,
    1,
    2,
    3,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    57,
    61,
    66,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    78,
    79,
    82,
    84,
]
EXPECTED_PDB_LABELS = [
    "GLU25",
    "THR26",
    "LEU27",
    "VAL28",
    "TYR48",
    "THR49",
    "MET50",
    "LYS51",
    "GLU52",
    "VAL53",
    "LEU54",
    "PHE55",
    "TYR56",
    "LEU57",
    "GLY58",
    "GLN59",
    "TYR60",
    "ILE61",
    "MET62",
    "THR63",
    "LEU66",
    "TYR67",
    "ASP68",
    "GLU69",
    "LYS70",
    "GLN71",
    "GLN72",
    "HIS73",
    "ILE74",
    "VAL75",
    "LEU82",
    "PHE86",
    "PHE91",
    "SER92",
    "VAL93",
    "LYS94",
    "GLU95",
    "HIS96",
    "ARG97",
    "LYS98",
    "ILE99",
    "TYR100",
    "THR101",
    "ILE103",
    "TYR104",
    "LEU107",
    "VAL109",
]
EXPECTED_MAPPING_SHA256 = "73cc5548869e537cd90d78a3cf1a417097f85b9dde99818d8c09f96cce8aa325"
EXPECTED_PAIR_SHA256 = "3a97680c46914b468cf1ef1de72bf5da9e51109a31f4d2ba5ee3cdc3af61eb73"
EXPECTED_RESULT_METADATA_SHA256 = "412763e453ff99d4271fff95839dbf38e1d636f9ebfab497cb2f3b41862de068"
EXPECTED_NEGATIVE_PARTNER_SEQUENCE_SHA256 = (
    "29fff7f2b98f31a8b3efc8aed0f9498206086e556950c818d1004ad41231bff7"
)

AA3_TO_AA1 = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        raw_columns = reader.fieldnames
        raw_rows = list(reader)

    if raw_columns is None:
        raise ValueError(f"CSV has no header: {path}")

    columns = list(raw_columns)
    rows: list[dict[str, str]] = []

    for raw_row in raw_rows:
        row: dict[str, str] = {}

        for key, value in raw_row.items():
            if not isinstance(key, str):
                raise ValueError(f"CSV row contains a non-string column name: {path}")
            if not isinstance(value, str):
                raise ValueError(
                    f"CSV row contains a missing or non-string value for {key}: {path}"
                )

            row[key] = value

        rows.append(row)

    return columns, rows


def validate_mapping_table(root: Path) -> list[dict[str, str]]:
    path = root / DEFAULT_MAPPING_TABLE
    columns, rows = read_csv_rows(path)
    if columns != EXPECTED_MAPPING_COLUMNS:
        raise ValueError(f"Unexpected mapping columns: {columns}")
    if len(rows) != 47:
        raise ValueError(f"Expected 47 mapping rows, got {len(rows)}")
    if sha256_file(path) != EXPECTED_MAPPING_SHA256:
        raise ValueError("Mapping table SHA256 mismatch")

    local_indices = [int(row["chain_local_zero_based_index"]) for row in rows]
    labels = [row["pdb_residue_label"] for row in rows]
    full_indices = [int(row["full_length_zero_based_index"]) for row in rows]

    if local_indices != EXPECTED_CHAIN_LOCAL_INDICES:
        raise ValueError("Chain-local interface indices changed")
    if labels != EXPECTED_PDB_LABELS:
        raise ValueError("PDB interface labels changed")
    if len(set(full_indices)) != 47:
        raise ValueError("Mapped indices are not unique")

    for row in rows:
        local_index = int(row["chain_local_zero_based_index"])
        full_zero = int(row["full_length_zero_based_index"])
        full_one = int(row["full_length_one_based_position"])
        if full_zero != local_index + 24:
            raise ValueError("Mapping offset is not 24")
        if full_one != full_zero + 1:
            raise ValueError("One-based mapping is inconsistent")
        if not 0 <= full_zero < 491:
            raise ValueError("Mapped index is out of Q00987 bounds")
        if row["residue_identity_consistent"] != "true":
            raise ValueError("Residue identity consistency is false")
        if row["mapping_offset"] != "24":
            raise ValueError("Mapping offset field is not 24")

        match = re.fullmatch(r"([A-Z]{3})(\d+)", row["pdb_residue_label"])
        if match is None:
            raise ValueError("Malformed PDB residue label")
        residue_name, residue_number_text = match.groups()
        if int(residue_number_text) != full_one:
            raise ValueError("PDB residue number does not equal full-length position")
        if AA3_TO_AA1[residue_name] != row["residue_one_letter"]:
            raise ValueError("One-letter residue identity mismatch")

    return rows


def validate_pair_table(root: Path) -> dict[str, str]:
    path = root / DEFAULT_PAIR_TABLE
    columns, rows = read_csv_rows(path)
    if columns != EXPECTED_PAIR_COLUMNS:
        raise ValueError(f"Unexpected pair columns: {columns}")
    if len(rows) != 1:
        raise ValueError(f"Expected one repaired pair row, got {len(rows)}")
    if sha256_file(path) != EXPECTED_PAIR_SHA256:
        raise ValueError("Pair table SHA256 mismatch")

    row = rows[0]
    expected = {
        "complex_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "chain": "mdm2",
        "target_species": "elephant",
        "source_uniprot": "Q00987",
        "negative_partner_uniprot": "G3UAZ0",
        "control_type": "negative_coimmunoprecipitation_partner_context",
    }
    for key, value in expected.items():
        if row[key] != value:
            raise ValueError(f"Unexpected pair value {key}={row[key]!r}")

    sequence = row["negative_partner_sequence"]
    if len(sequence) != 364:
        raise ValueError("G3UAZ0 sequence length is not 364")
    if sha256_text(sequence) != EXPECTED_NEGATIVE_PARTNER_SEQUENCE_SHA256:
        raise ValueError("G3UAZ0 sequence SHA256 mismatch")
    if "ENSLAFG00000028299" not in row["negative_partner_source"]:
        raise ValueError("Missing Ensembl gene provenance")
    if "ENSLAFP00000024998" not in row["negative_partner_source"]:
        raise ValueError("Missing Ensembl translation provenance")
    if "UniProtKB:G3UAZ0" not in row["negative_partner_source"]:
        raise ValueError("Missing UniProt provenance")

    return row


def validate_result_table(root: Path) -> dict[str, str]:
    mapping_rows = validate_mapping_table(root)
    pair_row = validate_pair_table(root)

    path = root / DEFAULT_RESULT_TABLE
    columns, rows = read_csv_rows(path)
    if columns != EXPECTED_RESULT_COLUMNS:
        raise ValueError(f"Unexpected result columns: {columns}")
    if len(rows) != 1:
        raise ValueError(f"Expected one repair result row, got {len(rows)}")

    row = rows[0]
    expected = {
        "result_status": (
            "embedding_based_negatome_control_retry_blocked_by_missing_negative_partner_embedding"
        ),
        "audit_outcome": "negative_partner_embedding_missing_or_invalid",
        "mapping_unique": "true",
        "mapped_interface_count": "47",
        "mapped_indices_unique": "true",
        "mapped_indices_in_bounds": "true",
        "residue_identity_consistent": "true",
        "mapping_invariants_pass": "true",
        "protein_level_negative_partner_resolved": "true",
        "negative_partner_uniprot": "G3UAZ0",
        "negative_partner_sequence_length": "364",
        "negative_partner_sequence_deterministic": "true",
        "negative_partner_cross_source_sequence_exact_match": "true",
        "reported_w23g_alignment_consistent": "true",
        "exact_pair_schema_valid": "true",
        "exact_pair_row_count": "1",
        "repaired_pair_runtime_loadable": "true",
        "negative_partner_embedding_exists": "false",
        "negative_partner_embedding_invariant_pass": "false",
        "checked_blocker_count": "1",
        "checked_blocker": "negative_partner_embedding_missing_or_invalid",
        "control_retry_attempted": "true",
        "control_ratio_runtime_executed": "false",
        "embedding_based_negatome_control_computed": "false",
        "negatome_control_ratio_available": "false",
        "negatome_control_ratio": "not_computed",
        "proposed_gate6_repair_status": "blocked_pending_control_repair",
        "gate6_control_readiness_resolved_after": "false",
        "gate6_control_closure_blocked_after": "true",
        "gate7_entry_allowed_after": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biohub_esmc_called": "false",
        "new_embeddings_generated": "false",
        "npy_artifact_written": "false",
        "npy_artifact_committed": "false",
        "data_output_artifact_committed": "false",
        "boltz_called": "false",
        "af3_called": "false",
        "chai_called": "false",
        "biological_claim_made": "false",
    }
    for key, value in expected.items():
        if row[key] != value:
            raise ValueError(f"Unexpected result value {key}={row[key]!r}")

    if row["mapping_table_sha256"] != EXPECTED_MAPPING_SHA256:
        raise ValueError("Result mapping SHA256 mismatch")
    if row["repaired_pair_table_sha256"] != EXPECTED_PAIR_SHA256:
        raise ValueError("Result pair SHA256 mismatch")
    if row["result_metadata_sha256"] != EXPECTED_RESULT_METADATA_SHA256:
        raise ValueError("Result metadata SHA256 field mismatch")
    if sha256_text(row["result_metadata_canonical"]) != EXPECTED_RESULT_METADATA_SHA256:
        raise ValueError("Result metadata canonical hash mismatch")
    if len(mapping_rows) != 47:
        raise ValueError("Mapping validator did not return 47 rows")
    if pair_row["negative_partner_uniprot"] != "G3UAZ0":
        raise ValueError("Pair validator did not resolve G3UAZ0")

    return row
