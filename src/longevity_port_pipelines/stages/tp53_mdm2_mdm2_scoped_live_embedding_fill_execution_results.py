"""Validate the scoped TP53/MDM2 MDM2 live-fill execution result.

The committed result records the completed sequential execution for mouse
P23804 and hamster A0ABM2YB85. It validates the recorded runtime outcome
without reading ignored ``data/output`` artifacts in CI.

This module performs no BioHub/ESMC call, creates no embedding, runs no
contrast, promotes no gate, and makes no biological claim.
"""

from __future__ import annotations

import csv
from pathlib import Path

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_scoped_live_embedding_fill_authorizations as authorization,
)

RESULT_TABLE = Path("data/input/tp53_mdm2_mdm2_scoped_live_embedding_fill_execution_results.csv")
RESULT_SCHEMA = Path(
    "data/config/tp53_mdm2_mdm2_scoped_live_embedding_fill_execution_result_schema.yaml"
)

CONTRACT_VERSION = "1"
MODEL_NAME = "esmc-300m-2024-12"
RUNNER = "curated_embedding_single"
LIVE_FLAG = "--yes-live"
COMPLETED_ACCESSIONS = "P23804|A0ABM2YB85"
PANEL_STATUS = "ready_both_scoped_mdm2_embeddings_present_valid"
PANEL_BLOCKER = "none_for_scoped_mdm2_contrast_dry_run"
NEXT_ACTION = "prepare_and_execute_scoped_mdm2_contrast_dry_run"
EVIDENCE_ROOT_ENV = "LONGEVITY_PORT_EXTERNAL_SEQUENCE_BINDING_ROOT"
EVIDENCE_RELATIVE_PATH = "tp53_mdm2_mdm2_scoped_live_fill_execution_evidence.json"
EXECUTION_DATE = "2026-07-19"

EXPECTED = {
    "P23804": {
        "order": "1",
        "species": "mouse",
        "taxid": "10090",
        "db": "UniProtKB Swiss-Prot",
        "length": "489",
        "sequence_sha256": ("0841e7c8ebd6a4a9e9e051538600d8f201c6682b3246dfb95ba301ab6233a3e3"),
        "path": (
            "data/output/embeddings/esmc-300m-2024-12/"
            "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_10090.npy"
        ),
        "shape": "489x960",
        "embedding_sha256": ("23c92fc3ceeb9b9141d502c0b3a0c47f9aa442f5fd9659030dc88502eee6c88e"),
    },
    "A0ABM2YB85": {
        "order": "2",
        "species": "hamster",
        "taxid": "10036",
        "db": "UniProtKB TrEMBL and NCBI RefSeq",
        "length": "510",
        "sequence_sha256": ("77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5"),
        "path": (
            "data/output/embeddings/esmc-300m-2024-12/"
            "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_10036.npy"
        ),
        "shape": "510x960",
        "embedding_sha256": ("36387d8ca76f764542225832f5146e524d615ec9c1fcc16c0523fe9c20b6de5a"),
    },
}

RESULT_FIELDS = (
    "execution_result_contract_version",
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "execution_order",
    "target_species",
    "target_taxid",
    "target_accession",
    "target_accession_db",
    "expected_sequence_length",
    "exact_normalized_sequence_sha256",
    "source_authorization_table",
    "source_authorization_file_sha256",
    "source_authorization_row_index",
    "source_authorization_validation_table",
    "source_authorization_validation_file_sha256",
    "source_authorization_validation_row_index",
    "source_authorization_validation_status",
    "allowed_model",
    "required_runner",
    "required_live_flag",
    "human_opt_in_scope",
    "explicit_human_opt_in_confirmed",
    "max_live_batch_size",
    "execution_mode",
    "live_invocation_count",
    "pre_live_single_dry_run_status",
    "pre_live_sequence_length_status",
    "pre_live_embedding_exists",
    "skip_existing_used",
    "live_status",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created",
    "local_embedding_path",
    "embedding_shape",
    "embedding_dtype",
    "embedding_numeric",
    "embedding_finite",
    "embedding_sequence_length_matches",
    "embedding_sha256",
    "embedding_ignored",
    "embedding_tracked",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "follow_up_single_dry_run_status",
    "follow_up_preflight_status",
    "local_embedding_status",
    "execution_status",
    "panel_completed_accessions",
    "panel_local_prerequisites_status",
    "panel_runtime_blocker_code",
    "tp53_status",
    "aggregate_tp53_mdm2_lane_status",
    "aggregate_gate7_entry_allowed",
    "aggregate_gate8_entry_allowed",
    "contrast_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "external_evidence_root_env",
    "external_evidence_relative_path",
    "external_evidence_committed",
    "allowed_next_action",
    "claim_policy",
    "claim_status",
    "execution_date",
    "execution_note",
)

TRUE_FIELDS = (
    "explicit_human_opt_in_confirmed",
    "skip_existing_used",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created",
    "embedding_numeric",
    "embedding_finite",
    "embedding_sequence_length_matches",
    "embedding_ignored",
)

FALSE_FIELDS = (
    "pre_live_embedding_exists",
    "embedding_tracked",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "aggregate_gate7_entry_allowed",
    "aggregate_gate8_entry_allowed",
    "contrast_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "external_evidence_committed",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv_rows(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    """Write rows with the exact execution-result field order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(RESULT_FIELDS),
        )
        writer.writeheader()
        writer.writerows(rows)


def require(
    row: dict[str, str],
    field: str,
    expected: str,
) -> None:
    """Require one exact field value."""
    actual = row.get(field, "").strip()
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def unique_row(
    rows: list[dict[str, str]],
    accession: str,
) -> tuple[int, dict[str, str]]:
    """Return the one row for an accession and its one-based index."""
    matches = [
        (index, row)
        for index, row in enumerate(rows, start=1)
        if row.get("target_accession") == accession
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one row for {accession}, found {len(matches)}")
    return matches[0]


def load_authorization(
    root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Load and validate the committed live-fill authorization."""
    return authorization.load_and_validate_committed_authorization(
        root / authorization.AUTH_TABLE,
        root / authorization.AUTH_VALIDATION,
        root / authorization.SOURCE_MANIFEST,
        root / authorization.SOURCE_VALIDATION,
    )


def build_expected_rows(
    auth_rows: list[dict[str, str]],
    auth_validation_rows: list[dict[str, str]],
    auth_sha256: str,
    auth_validation_sha256: str,
) -> list[dict[str, str]]:
    """Build the exact two-row execution-result snapshot."""
    expected_order = ["P23804", "A0ABM2YB85"]

    if [row.get("target_accession") for row in auth_rows] != expected_order:
        raise ValueError("Authorization accession order changed")

    if [row.get("target_accession") for row in auth_validation_rows] != expected_order:
        raise ValueError("Authorization validation accession order changed")

    rows: list[dict[str, str]] = []

    for accession in expected_order:
        expected = EXPECTED[accession]
        auth_index, auth = unique_row(auth_rows, accession)
        validation_index, validation = unique_row(
            auth_validation_rows,
            accession,
        )

        require(
            auth,
            "authorization_status",
            "explicit_scoped_live_fill_authorized",
        )
        require(auth, "authorization_effective", "true")
        require(auth, "live_fill_allowed", "true")
        require(auth, "fill_execution_allowed", "true")
        require(auth, "required_runner", RUNNER)
        require(auth, "required_live_flag", LIVE_FLAG)
        require(
            auth,
            "human_opt_in_scope",
            "per_accession_per_invocation",
        )
        require(auth, "max_live_batch_size", "1")
        require(
            validation,
            "authorization_validation_status",
            "passed_policy_only_validation",
        )

        row = {
            "execution_result_contract_version": CONTRACT_VERSION,
            "candidate_set": auth["candidate_set"],
            "lane_name": auth["lane_name"],
            "candidate_id": auth["candidate_id"],
            "gene_symbol": "MDM2",
            "execution_order": expected["order"],
            "target_species": expected["species"],
            "target_taxid": expected["taxid"],
            "target_accession": accession,
            "target_accession_db": expected["db"],
            "expected_sequence_length": expected["length"],
            "exact_normalized_sequence_sha256": (expected["sequence_sha256"]),
            "source_authorization_table": (authorization.AUTH_TABLE.as_posix()),
            "source_authorization_file_sha256": auth_sha256,
            "source_authorization_row_index": str(auth_index),
            "source_authorization_validation_table": (authorization.AUTH_VALIDATION.as_posix()),
            "source_authorization_validation_file_sha256": (auth_validation_sha256),
            "source_authorization_validation_row_index": str(validation_index),
            "source_authorization_validation_status": (
                validation["authorization_validation_status"]
            ),
            "allowed_model": MODEL_NAME,
            "required_runner": RUNNER,
            "required_live_flag": LIVE_FLAG,
            "human_opt_in_scope": ("per_accession_per_invocation"),
            "explicit_human_opt_in_confirmed": "true",
            "max_live_batch_size": "1",
            "execution_mode": ("sequential_one_accession_at_a_time"),
            "live_invocation_count": "1",
            "pre_live_single_dry_run_status": "dry_run_missing",
            "pre_live_sequence_length_status": "matches",
            "pre_live_embedding_exists": "false",
            "skip_existing_used": "true",
            "live_status": "live_completed",
            "biohub_called": "true",
            "esmc_called": "true",
            "embedding_generated": "true",
            "npy_artifact_created": "true",
            "local_embedding_path": expected["path"],
            "embedding_shape": expected["shape"],
            "embedding_dtype": "float32",
            "embedding_numeric": "true",
            "embedding_finite": "true",
            "embedding_sequence_length_matches": "true",
            "embedding_sha256": expected["embedding_sha256"],
            "embedding_ignored": "true",
            "embedding_tracked": "false",
            "npy_artifact_committed": "false",
            "data_output_artifact_committed": "false",
            "follow_up_single_dry_run_status": ("dry_run_present"),
            "follow_up_preflight_status": "present_valid",
            "local_embedding_status": "present_valid",
            "execution_status": "completed_and_audited",
            "panel_completed_accessions": COMPLETED_ACCESSIONS,
            "panel_local_prerequisites_status": PANEL_STATUS,
            "panel_runtime_blocker_code": PANEL_BLOCKER,
            "tp53_status": "deferred_pending_source",
            "aggregate_tp53_mdm2_lane_status": ("closed_tp53_deferred_pending_source"),
            "aggregate_gate7_entry_allowed": "false",
            "aggregate_gate8_entry_allowed": "false",
            "contrast_run": "false",
            "gate8_promoted": "false",
            "gate9_promoted": "false",
            "biological_claim_made": "false",
            "external_evidence_root_env": EVIDENCE_ROOT_ENV,
            "external_evidence_relative_path": (EVIDENCE_RELATIVE_PATH),
            "external_evidence_committed": "false",
            "allowed_next_action": NEXT_ACTION,
            "claim_policy": ("no_biological_claims_until_validation"),
            "claim_status": "technical_execution_result",
            "execution_date": EXECUTION_DATE,
            "execution_note": (
                f"{accession} completed one explicitly authorized "
                "single-row live invocation after dry_run_missing. "
                "The local embedding passed immediate shape, dtype, "
                "numeric, finite-value, sequence-length, ignored, and "
                "untracked checks, followed by dry_run_present and "
                "present_valid confirmation."
            ),
        }
        rows.append(row)

    return rows


def validate_result_rows(
    rows: list[dict[str, str]],
    *,
    auth_rows: list[dict[str, str]],
    auth_validation_rows: list[dict[str, str]],
    auth_sha256: str,
    auth_validation_sha256: str,
) -> None:
    """Validate the committed execution-result snapshot."""
    if len(rows) != 2:
        raise ValueError(f"Expected two execution-result rows, found {len(rows)}")

    if [row.get("target_accession") for row in rows] != ["P23804", "A0ABM2YB85"]:
        raise ValueError("Execution-result scope must be exactly P23804 then A0ABM2YB85")

    for row in rows:
        if tuple(row) != RESULT_FIELDS:
            raise ValueError("Execution-result fields or field order changed")

    expected_rows = build_expected_rows(
        auth_rows,
        auth_validation_rows,
        auth_sha256,
        auth_validation_sha256,
    )

    if rows != expected_rows:
        for index, (
            actual_row,
            expected_row,
        ) in enumerate(
            zip(rows, expected_rows, strict=True),
            start=1,
        ):
            for field in RESULT_FIELDS:
                if actual_row.get(field) != expected_row.get(field):
                    raise ValueError(
                        f"Execution-result row {index} changed at "
                        f"{field}: expected "
                        f"{expected_row.get(field)!r}, got "
                        f"{actual_row.get(field)!r}"
                    )
        raise ValueError("Execution-result rows changed")

    for row in rows:
        require(row, "max_live_batch_size", "1")
        require(row, "live_invocation_count", "1")
        require(row, "live_status", "live_completed")
        require(
            row,
            "pre_live_single_dry_run_status",
            "dry_run_missing",
        )
        require(
            row,
            "follow_up_single_dry_run_status",
            "dry_run_present",
        )
        require(
            row,
            "follow_up_preflight_status",
            "present_valid",
        )
        require(
            row,
            "local_embedding_status",
            "present_valid",
        )
        require(row, "allowed_next_action", NEXT_ACTION)

        for field in TRUE_FIELDS:
            require(row, field, "true")

        for field in FALSE_FIELDS:
            require(row, field, "false")


def load_and_validate_result(
    root: Path,
    *,
    result_table: Path = RESULT_TABLE,
) -> list[dict[str, str]]:
    """Load and validate the committed execution-result table."""
    auth_rows, auth_validation_rows = load_authorization(root)

    auth_path = root / authorization.AUTH_TABLE
    auth_validation_path = root / authorization.AUTH_VALIDATION

    rows = read_csv_rows(root / result_table)

    validate_result_rows(
        rows,
        auth_rows=auth_rows,
        auth_validation_rows=auth_validation_rows,
        auth_sha256=authorization.file_sha256(auth_path),
        auth_validation_sha256=authorization.file_sha256(auth_validation_path),
    )
    return rows


def main() -> None:
    """Regenerate and validate the committed result table."""
    root = Path.cwd()
    auth_rows, auth_validation_rows = load_authorization(root)

    auth_sha256 = authorization.file_sha256(root / authorization.AUTH_TABLE)
    auth_validation_sha256 = authorization.file_sha256(root / authorization.AUTH_VALIDATION)

    rows = build_expected_rows(
        auth_rows,
        auth_validation_rows,
        auth_sha256,
        auth_validation_sha256,
    )

    output = root / RESULT_TABLE
    write_csv_rows(output, rows)

    load_and_validate_result(root)

    print(f"Wrote scoped live-fill execution results -> {output}")
    print(f"execution_result_count={len(rows)}")
    print(f"panel_local_prerequisites_status={PANEL_STATUS}")
    print(f"allowed_next_action={NEXT_ACTION}")


if __name__ == "__main__":
    main()
