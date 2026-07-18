"""Validate the MDM2 Gate 8 local embedding prerequisite audit result.

The committed result is a three-row execution-readiness checkpoint for the
Gate 7-ready MDM2 source panel. It validates committed source-panel decisions
and the recorded local observation without reading ignored ``data/output``
artifacts in CI.

This module does not call Biohub/ESMC, generate embeddings, run contrast,
promote Gate 8 or Gate 9, or make biological claims.
"""

from __future__ import annotations

import csv
from pathlib import Path

DEFAULT_ELEPHANT_SOURCE_TABLE = Path("data/input/tp53_mdm2_gate7_coverage_repair_resolutions.csv")
DEFAULT_SHORT_LIVED_SOURCE_TABLE = Path("data/input/tp53_mdm2_mdm2_short_lived_control_results.csv")
DEFAULT_G3SX30_PREFLIGHT_RESULT_TABLE = Path(
    "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv"
)
DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_mdm2_gate8_local_prerequisite_audit_results.csv")

MODEL_NAME = "esmc-300m-2024-12"
CANDIDATE_SET = "tp53_mdm2_elephant"
LANE_NAME = "tp53_mdm2_elephant"
CANDIDATE_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
GENE_SYMBOL = "MDM2"
EXTERNAL_OBSERVATION_JSON = (
    "D:/biohub_projects/_chatgpt_observations/tp53_mdm2_mdm2_gate8_local_prerequisite_audit.json"
)
AUDIT_DATE = "2026-07-18"

PANEL_VALID_ACCESSIONS = "G3SX30"
PANEL_MISSING_ACCESSIONS = "P23804|A0ABM2YB85"
PANEL_STATUS = "blocked_missing_exact_local_embeddings"
PANEL_BLOCKER = "missing_exact_local_embeddings_for_ready_mdm2_controls"
NEXT_ACTION = "prepare_separate_scoped_missing_embedding_fill"

FALSE_FIELDS = (
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "later_mdm2_dry_run_manifest_allowed",
    "controlled_claim_allowed",
    "aggregate_gate7_entry_allowed",
    "aggregate_gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "contrast_run",
    "live_calls_performed",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created_by_audit",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "external_observation_json_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
)

RESULT_FIELDS = (
    "audit_id",
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "target_species",
    "target_species_taxid",
    "target_accession",
    "target_accession_db",
    "expected_sequence_length",
    "model_name",
    "source_gate7_table",
    "source_gate7_row_index",
    "source_gate7_status",
    "source_gate7_strict_panel_row_allowed",
    "source_gate7_contrast_dry_run_allowed",
    "local_embedding_path",
    "git_ignore_rule_status",
    "local_runtime_embedding_exists",
    "local_runtime_embedding_tracked",
    "local_runtime_embedding_committed",
    "embedding_load_status",
    "embedding_shape",
    "embedding_dtype",
    "embedding_numeric",
    "embedding_finite",
    "embedding_sequence_length_matches",
    "embedding_accession_provenance_status",
    "local_embedding_status",
    "runtime_blocker_code",
    "panel_valid_accessions",
    "panel_missing_accessions",
    "panel_local_prerequisites_status",
    "panel_runtime_blocker_code",
    "later_mdm2_dry_run_manifest_allowed",
    "allowed_next_action",
    "mdm2_gate7_strict_panel_status",
    "mdm2_gate7_contrast_dry_run_allowed",
    "controlled_claim_allowed",
    "tp53_status",
    "aggregate_gate7_entry_allowed",
    "aggregate_gate7_blocker_code",
    "aggregate_gate8_entry_allowed",
    "gate8_promoted",
    "gate9_promoted",
    "contrast_run",
    "live_calls_performed",
    "biohub_called",
    "esmc_called",
    "embedding_generated",
    "npy_artifact_created_by_audit",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "external_observation_json",
    "external_observation_json_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
    "audit_date",
    "audit_note",
)

TARGETS = (
    {
        "audit_id": "mdm2_gate8_local_prerequisite_elephant_g3sx30",
        "target_species": "elephant",
        "target_species_name": "Loxodonta africana",
        "target_species_taxid": "9785",
        "target_accession": "G3SX30",
        "target_accession_db": "UniProtKB TrEMBL",
        "expected_sequence_length": "492",
        "source_gate7_table": str(DEFAULT_ELEPHANT_SOURCE_TABLE).replace("\\", "/"),
        "source_gate7_row_index": "2",
        "source_gate7_status": "coverage_repaired_and_ready",
        "local_runtime_embedding_exists": "true",
        "embedding_load_status": "loaded",
        "embedding_shape": "492x960",
        "embedding_dtype": "float32",
        "embedding_numeric": "true",
        "embedding_finite": "true",
        "embedding_sequence_length_matches": "true",
        "embedding_accession_provenance_status": (
            "confirmed_by_existing_g3sx30_one_row_preflight_result"
        ),
        "local_embedding_status": "present_valid",
        "runtime_blocker_code": "none",
    },
    {
        "audit_id": "mdm2_gate8_local_prerequisite_mouse_p23804",
        "target_species": "mouse",
        "target_species_name": "Mus musculus",
        "target_species_taxid": "10090",
        "target_accession": "P23804",
        "target_accession_db": "UniProtKB Swiss-Prot",
        "expected_sequence_length": "489",
        "source_gate7_table": str(DEFAULT_SHORT_LIVED_SOURCE_TABLE).replace("\\", "/"),
        "source_gate7_row_index": "1",
        "source_gate7_status": "ready_for_gate7_strict_panel_planning",
        "local_runtime_embedding_exists": "false",
        "embedding_load_status": "not_attempted_missing",
        "embedding_shape": "not_applicable",
        "embedding_dtype": "not_applicable",
        "embedding_numeric": "not_applicable",
        "embedding_finite": "not_applicable",
        "embedding_sequence_length_matches": "not_applicable",
        "embedding_accession_provenance_status": ("not_applicable_embedding_missing"),
        "local_embedding_status": "missing",
        "runtime_blocker_code": "missing_exact_local_embedding",
    },
    {
        "audit_id": "mdm2_gate8_local_prerequisite_hamster_a0abm2yb85",
        "target_species": "hamster",
        "target_species_name": "Mesocricetus auratus",
        "target_species_taxid": "10036",
        "target_accession": "A0ABM2YB85",
        "target_accession_db": "UniProtKB TrEMBL",
        "expected_sequence_length": "510",
        "source_gate7_table": str(DEFAULT_SHORT_LIVED_SOURCE_TABLE).replace("\\", "/"),
        "source_gate7_row_index": "3",
        "source_gate7_status": "ready_for_gate7_strict_panel_planning",
        "local_runtime_embedding_exists": "false",
        "embedding_load_status": "not_attempted_missing",
        "embedding_shape": "not_applicable",
        "embedding_dtype": "not_applicable",
        "embedding_numeric": "not_applicable",
        "embedding_finite": "not_applicable",
        "embedding_sequence_length_matches": "not_applicable",
        "embedding_accession_provenance_status": ("not_applicable_embedding_missing"),
        "local_embedding_status": "missing",
        "runtime_blocker_code": "missing_exact_local_embedding",
    },
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _require_fields(row: dict[str, str], fields: tuple[str, ...]) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


def _require_value(row: dict[str, str], field: str, expected: str) -> None:
    actual = row.get(field)
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def _select_one(
    rows: list[dict[str, str]],
    *,
    field: str,
    value: str,
    source: Path,
) -> dict[str, str]:
    matches = [row for row in rows if row.get(field) == value]
    if len(matches) != 1:
        raise ValueError(f"Expected one {field}={value!r} row in {source}, found {len(matches)}")
    return matches[0]


def validate_elephant_source(rows: list[dict[str, str]]) -> dict[str, str]:
    """Validate the committed elephant MDM2 Gate 7 resolution."""

    row = _select_one(
        rows,
        field="candidate_id",
        value=CANDIDATE_ID,
        source=DEFAULT_ELEPHANT_SOURCE_TABLE,
    )
    expected = {
        "gene_symbol": GENE_SYMBOL,
        "target_uniprot_after_resolution": "G3SX30",
        "coverage_repair_outcome": "coverage_repaired_and_ready",
        "coverage_preflight_status_after_resolution": ("coverage_repaired_and_ready"),
        "strict_panel_allowed_after_resolution": "true",
        "contrast_dry_run_allowed_after_resolution": "true",
        "concrete_source_blocker": "none",
        "gate7_entry_allowed": "false",
        "gate8_entry_allowed": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, value in expected.items():
        _require_value(row, field, value)
    return row


def validate_short_lived_sources(
    rows: list[dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Validate ready mouse/hamster rows and excluded rat row."""

    by_species = {
        row["selected_control_species"]: row
        for row in rows
        if row.get("candidate_id") == CANDIDATE_ID and row.get("gene_symbol") == GENE_SYMBOL
    }
    if set(by_species) != {"mouse", "rat", "hamster"}:
        raise ValueError(
            f"Expected mouse, rat, and hamster MDM2 control rows; got {sorted(by_species)}"
        )

    expected_ready = {
        "mouse": {
            "target_protein_accession": "P23804",
            "selected_control_species_name": "Mus musculus",
            "selected_control_species_taxid": "10090",
            "sequence_length": "489",
        },
        "hamster": {
            "target_protein_accession": "A0ABM2YB85",
            "selected_control_species_name": "Mesocricetus auratus",
            "selected_control_species_taxid": "10036",
            "sequence_length": "510",
        },
    }
    for species, species_expected in expected_ready.items():
        row = by_species[species]
        common = {
            "selection_outcome": "ready_for_gate7_strict_panel_planning",
            "blocker_code": "none",
            "strict_panel_row_allowed": "true",
            "gate7_mdm2_strict_panel_status_after_selection": ("strict_panel_ready"),
            "gate7_mdm2_contrast_dry_run_allowed_after_selection": "true",
            "aggregate_gate7_entry_allowed": "false",
            "aggregate_gate7_blocker_code": "tp53_deferred_pending_source",
            "gate8_entry_allowed": "false",
            "gate8_promoted": "false",
            "gate9_promoted": "false",
            "biological_claim_made": "false",
        }
        for field, value in {**species_expected, **common}.items():
            _require_value(row, field, value)

    rat = by_species["rat"]
    _require_value(rat, "selection_outcome", "deferred_pending_source")
    _require_value(
        rat,
        "blocker_code",
        "no_unambiguous_canonical_rat_mdm2_sequence",
    )
    _require_value(rat, "strict_panel_row_allowed", "false")
    return by_species


def validate_g3sx30_preflight(rows: list[dict[str, str]]) -> dict[str, str]:
    """Validate the existing accession-bound G3SX30 local preflight result."""

    if len(rows) != 1:
        raise ValueError(f"Expected one G3SX30 local preflight result row, found {len(rows)}")
    row = rows[0]
    expected = {
        "candidate_id": CANDIDATE_ID,
        "target_accession": "G3SX30",
        "target_taxid": "9785",
        "check_status": "local_preflight_pass",
        "local_embedding_path": (
            "data/output/embeddings/esmc-300m-2024-12/"
            "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
        ),
        "local_runtime_embedding_exists": "true",
        "local_runtime_embedding_tracked": "false",
        "local_runtime_embedding_committed": "false",
        "embedding_shape": "492x960",
        "embedding_dtype": "float32",
        "embedding_finite": "true",
        "sequence_length": "492",
        "sequence_length_matches": "true",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
    }
    for field, value in expected.items():
        _require_value(row, field, value)
    return row


def _embedding_path(taxid: str) -> str:
    return f"data/output/embeddings/{MODEL_NAME}/{CANDIDATE_ID}_mdm2_{taxid}.npy"


def build_expected_rows(
    elephant_rows: list[dict[str, str]],
    short_lived_rows: list[dict[str, str]],
    g3sx30_preflight_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build the expected three-row committed audit result."""

    validate_elephant_source(elephant_rows)
    short_lived = validate_short_lived_sources(short_lived_rows)
    preflight = validate_g3sx30_preflight(g3sx30_preflight_rows)

    rows: list[dict[str, str]] = []
    for target in TARGETS:
        species = target["target_species"]
        if species == "elephant":
            shape = preflight["embedding_shape"]
            dtype = preflight["embedding_dtype"]
        else:
            source_row = short_lived[species]
            _require_value(
                source_row,
                "target_protein_accession",
                target["target_accession"],
            )
            shape = target["embedding_shape"]
            dtype = target["embedding_dtype"]

        row = {
            "audit_id": target["audit_id"],
            "candidate_set": CANDIDATE_SET,
            "lane_name": LANE_NAME,
            "candidate_id": CANDIDATE_ID,
            "gene_symbol": GENE_SYMBOL,
            "target_species": species,
            "target_species_taxid": target["target_species_taxid"],
            "target_accession": target["target_accession"],
            "target_accession_db": target["target_accession_db"],
            "expected_sequence_length": target["expected_sequence_length"],
            "model_name": MODEL_NAME,
            "source_gate7_table": target["source_gate7_table"],
            "source_gate7_row_index": target["source_gate7_row_index"],
            "source_gate7_status": target["source_gate7_status"],
            "source_gate7_strict_panel_row_allowed": "true",
            "source_gate7_contrast_dry_run_allowed": "true",
            "local_embedding_path": _embedding_path(target["target_species_taxid"]),
            "git_ignore_rule_status": "data_output_ignored",
            "local_runtime_embedding_exists": target["local_runtime_embedding_exists"],
            "local_runtime_embedding_tracked": "false",
            "local_runtime_embedding_committed": "false",
            "embedding_load_status": target["embedding_load_status"],
            "embedding_shape": shape,
            "embedding_dtype": dtype,
            "embedding_numeric": target["embedding_numeric"],
            "embedding_finite": target["embedding_finite"],
            "embedding_sequence_length_matches": target["embedding_sequence_length_matches"],
            "embedding_accession_provenance_status": target[
                "embedding_accession_provenance_status"
            ],
            "local_embedding_status": target["local_embedding_status"],
            "runtime_blocker_code": target["runtime_blocker_code"],
            "panel_valid_accessions": PANEL_VALID_ACCESSIONS,
            "panel_missing_accessions": PANEL_MISSING_ACCESSIONS,
            "panel_local_prerequisites_status": PANEL_STATUS,
            "panel_runtime_blocker_code": PANEL_BLOCKER,
            "later_mdm2_dry_run_manifest_allowed": "false",
            "allowed_next_action": NEXT_ACTION,
            "mdm2_gate7_strict_panel_status": "strict_panel_ready",
            "mdm2_gate7_contrast_dry_run_allowed": "true",
            "controlled_claim_allowed": "false",
            "tp53_status": "deferred_pending_source",
            "aggregate_gate7_entry_allowed": "false",
            "aggregate_gate7_blocker_code": "tp53_deferred_pending_source",
            "aggregate_gate8_entry_allowed": "false",
            "gate8_promoted": "false",
            "gate9_promoted": "false",
            "contrast_run": "false",
            "live_calls_performed": "false",
            "biohub_called": "false",
            "esmc_called": "false",
            "embedding_generated": "false",
            "npy_artifact_created_by_audit": "false",
            "npy_artifact_committed": "false",
            "data_output_artifact_committed": "false",
            "external_observation_json": EXTERNAL_OBSERVATION_JSON,
            "external_observation_json_committed": "false",
            "boltz_called": "false",
            "af3_called": "false",
            "chai_called": "false",
            "biological_claim_made": "false",
            "audit_date": AUDIT_DATE,
            "audit_note": (
                "Existing accession-bound G3SX30 local artifact passes "
                "shape, dtype, finite-value, and sequence-length checks."
                if species == "elephant"
                else (
                    f"Exact local {target['target_accession']} embedding is "
                    "missing at the canonical MDM2 path; the panel remains "
                    "blocked before any later dry-run manifest."
                )
            ),
        }
        rows.append(row)

    return rows


def validate_result_rows(
    rows: list[dict[str, str]],
    *,
    elephant_rows: list[dict[str, str]],
    short_lived_rows: list[dict[str, str]],
    g3sx30_preflight_rows: list[dict[str, str]],
) -> None:
    """Validate committed rows against source decisions and recorded outcomes."""

    if len(rows) != 3:
        raise ValueError(f"Expected three audit rows, found {len(rows)}")
    for row in rows:
        _require_fields(row, RESULT_FIELDS)

    expected = build_expected_rows(
        elephant_rows,
        short_lived_rows,
        g3sx30_preflight_rows,
    )
    if rows != expected:
        for index, (actual_row, expected_row) in enumerate(
            zip(rows, expected, strict=True),
            start=1,
        ):
            for field in RESULT_FIELDS:
                if actual_row.get(field) != expected_row.get(field):
                    raise ValueError(
                        f"Audit row {index} changed at {field}: "
                        f"expected {expected_row.get(field)!r}, "
                        f"got {actual_row.get(field)!r}"
                    )
        raise ValueError("Audit result rows changed")

    for row in rows:
        for field in FALSE_FIELDS:
            _require_value(row, field, "false")


def load_and_validate_result(
    root: Path,
    *,
    result_table: Path = DEFAULT_RESULT_TABLE,
) -> list[dict[str, str]]:
    """Load and validate the committed panel audit result."""

    elephant_rows = read_csv_rows(root / DEFAULT_ELEPHANT_SOURCE_TABLE)
    short_lived_rows = read_csv_rows(root / DEFAULT_SHORT_LIVED_SOURCE_TABLE)
    g3sx30_rows = read_csv_rows(root / DEFAULT_G3SX30_PREFLIGHT_RESULT_TABLE)
    result_rows = read_csv_rows(root / result_table)
    validate_result_rows(
        result_rows,
        elephant_rows=elephant_rows,
        short_lived_rows=short_lived_rows,
        g3sx30_preflight_rows=g3sx30_rows,
    )
    return result_rows
