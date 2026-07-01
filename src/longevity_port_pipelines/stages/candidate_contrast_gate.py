from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.stages import (
    candidate_coverage_repair_decisions as repair,
)
from longevity_port_pipelines.stages import (
    candidate_negatome_repair_decisions as negatome_repair,
)
from longevity_port_pipelines.stages import strict_sirt6_contrast_panel as strict_panel
from longevity_port_pipelines.stages.control_readiness import (
    ControlReadinessResult,
    control_readiness_for_statuses,
)
from longevity_port_pipelines.stages.coverage_preflight import (
    CoveragePreflightResult,
    coverage_preflight_for_statuses,
)

DEFAULT_CONTRAST_READY_INPUT = Path("data/interim/sirt6_contrast_ready_subset.csv")
DEFAULT_NEGATOME_READINESS_INPUT = Path(
    "data/interim/sirt6_candidate_negatome_readiness_matrix.csv"
)
DEFAULT_OUTPUT = Path("data/interim/sirt6_candidate_contrast_gate.csv")
DEFAULT_COVERAGE_REPAIR_DECISIONS_INPUT = repair.DEFAULT_REPAIR_DECISIONS_PATH
DEFAULT_STRICT_PANEL_SUMMARY_INPUT = strict_panel.DEFAULT_SUMMARY_OUTPUT
DEFAULT_NEGATOME_REPAIR_DECISIONS_INPUT = negatome_repair.DEFAULT_REPAIR_DECISIONS_PATH

KEY_COLUMNS = ["candidate_id", "pdb_id", "chain", "source_uniprot", "priority"]

CONTRAST_REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "n_coverage_ready_species",
    "n_long_lived_ready",
    "n_short_lived_ready",
    "ready_long_lived_species",
    "ready_short_lived_species",
    "contrast_readiness_status",
}

NEGATOME_REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "baseline_input_status",
    "species_coverage_status",
    "negatome_status",
    "negative_partner_uniprot",
    "missing_negatome_species",
}

STRICT_PANEL_REQUIRED_COLUMNS = set(strict_panel.STRICT_PANEL_SUMMARY_SCHEMA)

CONTRAST_GATE_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "contrast_readiness_status": pl.Utf8,
    "n_coverage_ready_species": pl.Int64,
    "n_long_lived_ready": pl.Int64,
    "n_short_lived_ready": pl.Int64,
    "ready_long_lived_species": pl.Utf8,
    "ready_short_lived_species": pl.Utf8,
    "baseline_input_status": pl.Utf8,
    "species_coverage_status": pl.Utf8,
    "coverage_repair_decision_status": pl.Utf8,
    "n_coverage_repair_decision_rows": pl.Int64,
    "coverage_repair_target_species": pl.Utf8,
    "coverage_repair_decisions": pl.Utf8,
    "coverage_repair_priorities": pl.Utf8,
    "coverage_repair_claim_policies": pl.Utf8,
    "strict_panel_status": pl.Utf8,
    "n_strict_panel_ready_species": pl.Int64,
    "n_strict_panel_blocked_species": pl.Int64,
    "n_strict_long_lived_ready": pl.Int64,
    "n_strict_short_lived_ready": pl.Int64,
    "strict_long_lived_species": pl.Utf8,
    "strict_short_lived_species": pl.Utf8,
    "blocked_target_species": pl.Utf8,
    "strict_panel_recommended_next_action": pl.Utf8,
    "negatome_status": pl.Utf8,
    "negative_partner_uniprot": pl.Utf8,
    "missing_negatome_species": pl.Utf8,
    "negatome_repair_decision_status": pl.Utf8,
    "n_negatome_repair_decision_rows": pl.Int64,
    "negatome_repair_missing_species": pl.Utf8,
    "negatome_repair_decisions": pl.Utf8,
    "negatome_repair_priorities": pl.Utf8,
    "negatome_repair_claim_policies": pl.Utf8,
    "generic_control_readiness_status": pl.Utf8,
    "generic_control_recommended_next_action": pl.Utf8,
    "generic_control_contrast_dry_run_allowed": pl.Boolean,
    "generic_controlled_claim_allowed": pl.Boolean,
    "generic_control_claim_policy": pl.Utf8,
    "generic_control_claim_status": pl.Utf8,
    "generic_control_readiness_note": pl.Utf8,
    "strict_contrast_gate_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "gate_note": pl.Utf8,
}

app = typer.Typer(add_completion=False)


def read_table(path: Path) -> pl.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")

    if path.suffix.lower() == ".parquet":
        return pl.read_parquet(path)

    return pl.read_csv(path, infer_schema_length=10000)


def validate_required_columns(df: pl.DataFrame, required: set[str], label: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def _as_str(row: dict[str, Any], column: str, default: str = "") -> str:
    value = row.get(column)
    if value is None:
        return default
    return str(value).strip()


def _as_int(row: dict[str, Any], column: str) -> int:
    value = row.get(column)
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value).strip()
    if not text:
        return 0

    return int(text)


def _key(row: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        _as_str(row, "candidate_id"),
        _as_str(row, "pdb_id"),
        _as_str(row, "chain"),
        _as_str(row, "source_uniprot"),
        _as_str(row, "priority"),
    )


def empty_contrast_gate() -> pl.DataFrame:
    return pl.DataFrame(schema=CONTRAST_GATE_SCHEMA)


def _coverage_preflight_from_species_status(
    species_coverage_status: str,
) -> CoveragePreflightResult:
    if species_coverage_status == "complete_species_coverage":
        return coverage_preflight_for_statuses(
            coverage_status="coverage_ready",
            provenance_status="standard_source_present",
            repair_status="not_needed",
        )

    if species_coverage_status == "not_audited":
        return coverage_preflight_for_statuses(
            coverage_status="unresolved_downstream_provenance",
            provenance_status="unresolved",
            repair_status="pending",
        )

    return coverage_preflight_for_statuses(
        coverage_status="missing_source_ortholog",
        provenance_status="unresolved",
        repair_status="pending",
    )


def _control_repair_status_from_negatome_repair_status(negatome_repair_status: str) -> str:
    if negatome_repair_status in {"not_audited", "not_required"}:
        return "not_needed"

    if negatome_repair_status == "missing_repair_decision":
        return "pending"

    if negatome_repair_status == "negatome_repair_required_deferred_no_claim":
        return "deferred_pending_source"

    if negatome_repair_status == "mixed_deferred_negatome_repair_policy":
        return "in_review"

    if negatome_repair_status == "excluded_from_controlled_claim":
        return "excluded_from_controlled_claims"

    if negatome_repair_status == "limited_dry_run_only":
        return "accepted_for_planning_after_review"

    if negatome_repair_status == "negatome_repair_policy_review_required":
        return "needs_manual_review"

    return negatome_repair_status


def _control_readiness_from_gate_inputs(
    *,
    negatome_status: str,
    negative_partner_uniprot: str,
    negatome_repair_status: str,
) -> ControlReadinessResult:
    return control_readiness_for_statuses(
        shuffled_control_status="not_needed",
        negatome_control_status="present" if negatome_status == "present_existing" else "missing",
        curated_negative_partner_status="present" if negative_partner_uniprot else "missing",
        control_repair_status=_control_repair_status_from_negatome_repair_status(
            negatome_repair_status
        ),
    )


def _gate_status(
    *,
    contrast_readiness_status: str,
    baseline_input_status: str,
    species_coverage_status: str,
    negatome_status: str,
    strict_panel_status: str = "not_audited",
    negatome_repair_status: str = "not_required",
) -> str:
    species_preflight = _coverage_preflight_from_species_status(species_coverage_status)

    if contrast_readiness_status != "contrast_ready":
        return "blocked_contrast_coverage"
    if baseline_input_status != "input_prepared":
        return "blocked_baseline_input"
    if not species_preflight.contrast_dry_run_allowed:
        return "blocked_species_coverage"
    if strict_panel_status not in {"not_audited", "strict_panel_ready"}:
        return "blocked_strict_panel"
    if negatome_status != "present_existing" and negatome_repair_status.startswith(
        "negatome_repair_required_"
    ):
        return "blocked_negatome_repair_policy"
    if negatome_status != "present_existing":
        return "blocked_negatome_controls"
    return "eligible_for_contrast_dry_run"


def _joined_unique_values(rows: list[dict[str, Any]], column: str) -> str:
    values = {_as_str(row, column) for row in rows}
    return ",".join(sorted(value for value in values if value))


def _negatome_repair_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _as_str(row, "candidate_id"),
        _as_str(row, "chain"),
        _as_str(row, "source_uniprot"),
        _as_str(row, "negative_partner_uniprot"),
    )


def _negatome_repair_decision_rows_by_key(
    negatome_repair_decisions: pl.DataFrame | None,
) -> dict[tuple[str, str, str, str], list[dict[str, Any]]] | None:
    if negatome_repair_decisions is None:
        return None

    negatome_repair.validate_repair_decisions(negatome_repair_decisions)

    rows_by_key: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in negatome_repair_decisions.iter_rows(named=True):
        rows_by_key.setdefault(_negatome_repair_key(row), []).append(row)

    return rows_by_key


def _repair_decision_rows_by_key(
    coverage_repair_decisions: pl.DataFrame | None,
) -> dict[tuple[str, str, str, str, str], list[dict[str, Any]]] | None:
    if coverage_repair_decisions is None:
        return None

    repair.validate_repair_decisions(coverage_repair_decisions)

    rows_by_key: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = {}
    for row in coverage_repair_decisions.iter_rows(named=True):
        rows_by_key.setdefault(_key(row), []).append(row)

    return rows_by_key


def _strict_panel_summary_by_key(
    strict_panel_summary: pl.DataFrame | None,
) -> dict[tuple[str, str, str, str, str], dict[str, Any]] | None:
    if strict_panel_summary is None:
        return None

    validate_required_columns(
        strict_panel_summary,
        STRICT_PANEL_REQUIRED_COLUMNS,
        "strict_panel_summary",
    )

    return {_key(row): row for row in strict_panel_summary.iter_rows(named=True)}


def _negatome_repair_decision_status(
    *,
    repair_rows: list[dict[str, Any]],
    repair_table_provided: bool,
    negatome_status: str,
) -> str:
    if not repair_table_provided:
        return "not_audited"

    if negatome_status == "present_existing":
        return "not_required"

    if not repair_rows:
        return "missing_repair_decision"

    claim_policies = {
        _as_str(row, "claim_policy") for row in repair_rows if _as_str(row, "claim_policy")
    }

    if claim_policies == {"deferred_no_claim"}:
        return "negatome_repair_required_deferred_no_claim"

    if "deferred_no_claim" in claim_policies:
        return "mixed_deferred_negatome_repair_policy"

    if "excluded_from_controlled_claim" in claim_policies:
        return "excluded_from_controlled_claim"

    if "allowed_for_limited_dry_run_only" in claim_policies:
        return "limited_dry_run_only"

    return "negatome_repair_policy_review_required"


def _negatome_repair_summary(
    *,
    repair_rows: list[dict[str, Any]],
    repair_table_provided: bool,
    negatome_status: str,
) -> dict[str, Any]:
    return {
        "negatome_repair_decision_status": _negatome_repair_decision_status(
            repair_rows=repair_rows,
            repair_table_provided=repair_table_provided,
            negatome_status=negatome_status,
        ),
        "n_negatome_repair_decision_rows": len(repair_rows),
        "negatome_repair_missing_species": _joined_unique_values(
            repair_rows,
            "missing_negatome_species",
        ),
        "negatome_repair_decisions": _joined_unique_values(
            repair_rows,
            "repair_decision",
        ),
        "negatome_repair_priorities": _joined_unique_values(
            repair_rows,
            "repair_priority",
        ),
        "negatome_repair_claim_policies": _joined_unique_values(
            repair_rows,
            "claim_policy",
        ),
    }


def _coverage_repair_decision_status(
    *,
    repair_rows: list[dict[str, Any]],
    repair_table_provided: bool,
    species_coverage_status: str,
) -> str:
    if not repair_table_provided:
        return "not_audited"

    if species_coverage_status == "complete_species_coverage":
        return "not_required"

    if not repair_rows:
        return "missing_repair_decision"

    repair_decisions = {
        _as_str(row, "repair_decision") for row in repair_rows if _as_str(row, "repair_decision")
    }
    claim_policies = {
        _as_str(row, "claim_policy") for row in repair_rows if _as_str(row, "claim_policy")
    }

    if repair_decisions == {"needs_external_manual_sequence_review"} and claim_policies == {
        "deferred_no_claim"
    }:
        return "manual_review_required_deferred_no_claim"

    if "deferred_no_claim" in claim_policies:
        return "mixed_deferred_repair_policy"

    return "repair_policy_review_required"


def _coverage_repair_summary(
    *,
    repair_rows: list[dict[str, Any]],
    repair_table_provided: bool,
    species_coverage_status: str,
) -> dict[str, Any]:
    return {
        "coverage_repair_decision_status": _coverage_repair_decision_status(
            repair_rows=repair_rows,
            repair_table_provided=repair_table_provided,
            species_coverage_status=species_coverage_status,
        ),
        "n_coverage_repair_decision_rows": len(repair_rows),
        "coverage_repair_target_species": _joined_unique_values(
            repair_rows,
            "target_species",
        ),
        "coverage_repair_decisions": _joined_unique_values(
            repair_rows,
            "repair_decision",
        ),
        "coverage_repair_priorities": _joined_unique_values(
            repair_rows,
            "repair_priority",
        ),
        "coverage_repair_claim_policies": _joined_unique_values(
            repair_rows,
            "claim_policy",
        ),
    }


def _recommended_next_action(
    gate_status: str,
    coverage_repair_status: str = "not_audited",
    strict_panel_status: str = "not_audited",
    negatome_repair_status: str = "not_audited",
) -> str:
    if gate_status == "blocked_contrast_coverage":
        return "repair_contrast_species_coverage"
    if gate_status == "blocked_baseline_input":
        return "fix_baseline_input"
    if gate_status == "blocked_species_coverage":
        if coverage_repair_status == "manual_review_required_deferred_no_claim":
            return "review_manual_coverage_repair_decisions"
        if coverage_repair_status == "missing_repair_decision":
            return "add_coverage_repair_decision"
        if coverage_repair_status in {
            "mixed_deferred_repair_policy",
            "repair_policy_review_required",
        }:
            return "resolve_coverage_repair_policy"
        return "fix_species_coverage"
    if gate_status == "blocked_strict_panel":
        if strict_panel_status == "blocked_species_coverage_repair":
            return "resolve_strict_panel_coverage_repairs"
        if strict_panel_status == "missing_strict_panel_summary_row":
            return "build_strict_panel_summary"
        if strict_panel_status.startswith("insufficient_strict_"):
            return "repair_strict_panel_species_coverage"
        return "resolve_strict_panel_status"
    if gate_status == "blocked_negatome_controls":
        if negatome_repair_status == "missing_repair_decision":
            return "add_negatome_repair_decision"
        return "fix_negatome_controls"
    if gate_status == "blocked_negatome_repair_policy":
        if negatome_repair_status == "negatome_repair_required_deferred_no_claim":
            return "complete_negatome_repair_before_controlled_claim"
        if negatome_repair_status == "excluded_from_controlled_claim":
            return "do_not_use_for_controlled_claim"
        if negatome_repair_status == "limited_dry_run_only":
            return "keep_as_limited_dry_run_only"
        return "resolve_negatome_repair_policy"
    return "prepare_contrast_dry_run"


def _gate_note(
    gate_status: str,
    coverage_repair_status: str = "not_audited",
    strict_panel_status: str = "not_audited",
    negatome_repair_status: str = "not_audited",
) -> str:
    if gate_status == "blocked_contrast_coverage":
        return (
            "Coverage-only long-lived vs short-lived contrast readiness is incomplete; "
            "do not run or claim contrast results."
        )

    if gate_status == "blocked_baseline_input":
        return "Baseline PINDER input is not prepared; candidate contrast cannot proceed."

    if gate_status == "blocked_species_coverage":
        if coverage_repair_status == "manual_review_required_deferred_no_claim":
            return (
                "Strict species provenance coverage is incomplete; coverage repair "
                "decisions require manual sequence/provenance review and remain "
                "deferred_no_claim. Contrast remains a dry-run planning layer only."
            )

        if coverage_repair_status == "missing_repair_decision":
            return (
                "Strict species provenance coverage is incomplete and no coverage repair "
                "decision is available yet; contrast remains a dry-run planning layer only."
            )

        return (
            "Strict species provenance coverage is incomplete; contrast remains a "
            "dry-run planning layer only."
        )

    if gate_status == "blocked_strict_panel":
        if strict_panel_status == "blocked_species_coverage_repair":
            return (
                "Strict panel summary has unresolved coverage repair rows; strict "
                "contrast remains blocked and no biological claim can be made."
            )

        if strict_panel_status == "missing_strict_panel_summary_row":
            return (
                "Strict panel summary is missing for this candidate; build the strict "
                "panel summary before contrast dry-run planning."
            )

        if strict_panel_status.startswith("insufficient_strict_"):
            return (
                "Strict panel summary does not contain enough long-lived and short-lived "
                "ready species for strict contrast planning."
            )

        return (
            "Strict panel status is not ready; resolve strict panel diagnostics before "
            "contrast dry-run planning."
        )

    if gate_status == "blocked_negatome_controls":
        if negatome_repair_status == "missing_repair_decision":
            return (
                "NEGATOME-style controls are incomplete and no NEGATOME repair "
                "decision is available yet; controlled enrichment cannot be claimed."
            )
        return "NEGATOME-style controls are incomplete; controlled enrichment cannot be claimed."

    if gate_status == "blocked_negatome_repair_policy":
        if negatome_repair_status == "negatome_repair_required_deferred_no_claim":
            return (
                "NEGATOME repair decision remains deferred_no_claim; complete or "
                "export missing controls before controlled contrast claims."
            )
        if negatome_repair_status == "excluded_from_controlled_claim":
            return "NEGATOME repair policy excludes this candidate from controlled claims."
        if negatome_repair_status == "limited_dry_run_only":
            return (
                "NEGATOME repair policy allows limited dry-run planning only; "
                "controlled enrichment cannot be claimed."
            )
        return "NEGATOME repair policy is unresolved; controlled enrichment cannot be claimed."

    return (
        "Candidate passes dry-run gate checks, but no enrichment statistic or biological "
        "claim is computed here."
    )


def _gate_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return empty_contrast_gate()

    return pl.DataFrame(rows).select(
        [pl.col(column).cast(dtype).alias(column) for column, dtype in CONTRAST_GATE_SCHEMA.items()]
    )


def build_candidate_contrast_gate(
    *,
    contrast_ready: pl.DataFrame,
    negatome_readiness: pl.DataFrame,
    coverage_repair_decisions: pl.DataFrame | None = None,
    strict_panel_summary: pl.DataFrame | None = None,
    negatome_repair_decisions: pl.DataFrame | None = None,
) -> pl.DataFrame:
    validate_required_columns(contrast_ready, CONTRAST_REQUIRED_COLUMNS, "contrast_ready")
    validate_required_columns(
        negatome_readiness,
        NEGATOME_REQUIRED_COLUMNS,
        "negatome_readiness",
    )

    contrast_by_key = {_key(row): row for row in contrast_ready.iter_rows(named=True)}
    negatome_by_key = {_key(row): row for row in negatome_readiness.iter_rows(named=True)}
    repair_by_key = _repair_decision_rows_by_key(coverage_repair_decisions)
    strict_panel_by_key = _strict_panel_summary_by_key(strict_panel_summary)
    negatome_repair_by_key = _negatome_repair_decision_rows_by_key(negatome_repair_decisions)

    rows: list[dict[str, Any]] = []

    key_union = set(contrast_by_key) | set(negatome_by_key)
    if strict_panel_by_key is not None:
        key_union |= set(strict_panel_by_key)

    for key in sorted(key_union):
        contrast = contrast_by_key.get(key, {})
        negatome = negatome_by_key.get(key, {})
        repair_rows = [] if repair_by_key is None else repair_by_key.get(key, [])
        strict_panel = {} if strict_panel_by_key is None else strict_panel_by_key.get(key, {})
        strict_panel_status = (
            "not_audited"
            if strict_panel_by_key is None
            else _as_str(
                strict_panel,
                "strict_panel_status",
                "missing_strict_panel_summary_row",
            )
        )

        contrast_status = _as_str(
            contrast,
            "contrast_readiness_status",
            "missing_contrast_readiness_row",
        )
        baseline_status = _as_str(negatome, "baseline_input_status", "not_audited")
        species_status = _as_str(negatome, "species_coverage_status", "not_audited")
        negatome_status = _as_str(negatome, "negatome_status", "not_audited")
        negative_partner_uniprot = _as_str(negatome, "negative_partner_uniprot")
        negatome_repair_rows = (
            []
            if negatome_repair_by_key is None
            else negatome_repair_by_key.get(
                _negatome_repair_key(
                    {
                        "candidate_id": key[0],
                        "chain": key[2],
                        "source_uniprot": key[3],
                        "negative_partner_uniprot": negative_partner_uniprot,
                    }
                ),
                [],
            )
        )

        coverage_repair = _coverage_repair_summary(
            repair_rows=repair_rows,
            repair_table_provided=repair_by_key is not None,
            species_coverage_status=species_status,
        )

        negatome_repair_summary = _negatome_repair_summary(
            repair_rows=negatome_repair_rows,
            repair_table_provided=negatome_repair_by_key is not None,
            negatome_status=negatome_status,
        )

        negatome_repair_status = _as_str(
            negatome_repair_summary,
            "negatome_repair_decision_status",
        )

        generic_control_readiness = _control_readiness_from_gate_inputs(
            negatome_status=negatome_status,
            negative_partner_uniprot=negative_partner_uniprot,
            negatome_repair_status=negatome_repair_status,
        )

        gate_status = _gate_status(
            contrast_readiness_status=contrast_status,
            baseline_input_status=baseline_status,
            species_coverage_status=species_status,
            negatome_status=negatome_status,
            strict_panel_status=strict_panel_status,
            negatome_repair_status=negatome_repair_status,
        )

        rows.append(
            {
                "candidate_id": key[0],
                "pdb_id": key[1],
                "chain": key[2],
                "source_uniprot": key[3],
                "priority": key[4],
                "contrast_readiness_status": contrast_status,
                "n_coverage_ready_species": _as_int(
                    contrast,
                    "n_coverage_ready_species",
                ),
                "n_long_lived_ready": _as_int(contrast, "n_long_lived_ready"),
                "n_short_lived_ready": _as_int(contrast, "n_short_lived_ready"),
                "ready_long_lived_species": _as_str(
                    contrast,
                    "ready_long_lived_species",
                ),
                "ready_short_lived_species": _as_str(
                    contrast,
                    "ready_short_lived_species",
                ),
                "baseline_input_status": baseline_status,
                "species_coverage_status": species_status,
                "coverage_repair_decision_status": _as_str(
                    coverage_repair,
                    "coverage_repair_decision_status",
                ),
                "n_coverage_repair_decision_rows": _as_int(
                    coverage_repair,
                    "n_coverage_repair_decision_rows",
                ),
                "coverage_repair_target_species": _as_str(
                    coverage_repair,
                    "coverage_repair_target_species",
                ),
                "coverage_repair_decisions": _as_str(
                    coverage_repair,
                    "coverage_repair_decisions",
                ),
                "coverage_repair_priorities": _as_str(
                    coverage_repair,
                    "coverage_repair_priorities",
                ),
                "coverage_repair_claim_policies": _as_str(
                    coverage_repair,
                    "coverage_repair_claim_policies",
                ),
                "strict_panel_status": strict_panel_status,
                "n_strict_panel_ready_species": _as_int(
                    strict_panel,
                    "n_strict_panel_ready_species",
                ),
                "n_strict_panel_blocked_species": _as_int(
                    strict_panel,
                    "n_strict_panel_blocked_species",
                ),
                "n_strict_long_lived_ready": _as_int(
                    strict_panel,
                    "n_strict_long_lived_ready",
                ),
                "n_strict_short_lived_ready": _as_int(
                    strict_panel,
                    "n_strict_short_lived_ready",
                ),
                "strict_long_lived_species": _as_str(
                    strict_panel,
                    "strict_long_lived_species",
                ),
                "strict_short_lived_species": _as_str(
                    strict_panel,
                    "strict_short_lived_species",
                ),
                "blocked_target_species": _as_str(
                    strict_panel,
                    "blocked_target_species",
                ),
                "strict_panel_recommended_next_action": _as_str(
                    strict_panel,
                    "recommended_next_action",
                ),
                "negatome_status": negatome_status,
                "negative_partner_uniprot": negative_partner_uniprot,
                "missing_negatome_species": _as_str(
                    negatome,
                    "missing_negatome_species",
                ),
                "negatome_repair_decision_status": negatome_repair_status,
                "n_negatome_repair_decision_rows": _as_int(
                    negatome_repair_summary,
                    "n_negatome_repair_decision_rows",
                ),
                "negatome_repair_missing_species": _as_str(
                    negatome_repair_summary,
                    "negatome_repair_missing_species",
                ),
                "negatome_repair_decisions": _as_str(
                    negatome_repair_summary,
                    "negatome_repair_decisions",
                ),
                "negatome_repair_priorities": _as_str(
                    negatome_repair_summary,
                    "negatome_repair_priorities",
                ),
                "negatome_repair_claim_policies": _as_str(
                    negatome_repair_summary,
                    "negatome_repair_claim_policies",
                ),
                "generic_control_readiness_status": (
                    generic_control_readiness.control_readiness_status
                ),
                "generic_control_recommended_next_action": (
                    generic_control_readiness.recommended_next_action
                ),
                "generic_control_contrast_dry_run_allowed": (
                    generic_control_readiness.contrast_dry_run_allowed
                ),
                "generic_controlled_claim_allowed": (
                    generic_control_readiness.controlled_claim_allowed
                ),
                "generic_control_claim_policy": generic_control_readiness.claim_policy,
                "generic_control_claim_status": generic_control_readiness.claim_status,
                "generic_control_readiness_note": generic_control_readiness.notes,
                "strict_contrast_gate_status": gate_status,
                "recommended_next_action": _recommended_next_action(
                    gate_status,
                    _as_str(coverage_repair, "coverage_repair_decision_status"),
                    strict_panel_status,
                    negatome_repair_status,
                ),
                "gate_note": _gate_note(
                    gate_status,
                    _as_str(coverage_repair, "coverage_repair_decision_status"),
                    strict_panel_status,
                    negatome_repair_status,
                ),
            }
        )

    return _gate_from_rows(rows).sort(["strict_contrast_gate_status", "priority", "candidate_id"])


def gate_status_counts(gate: pl.DataFrame) -> dict[str, int]:
    if gate.is_empty():
        return {}

    counts: dict[str, int] = {}
    grouped = gate.group_by("strict_contrast_gate_status").len()

    for row in grouped.iter_rows(named=True):
        counts[str(row["strict_contrast_gate_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    contrast_ready_input: Annotated[
        Path,
        typer.Option(
            help=(
                "CSV/parquet contrast-ready subset produced by candidate-species-coverage-matrix."
            )
        ),
    ] = DEFAULT_CONTRAST_READY_INPUT,
    negatome_readiness_input: Annotated[
        Path,
        typer.Option(
            help=(
                "CSV/parquet NEGATOME readiness matrix produced by "
                "cofolding-candidate-preflight-batch."
            )
        ),
    ] = DEFAULT_NEGATOME_READINESS_INPUT,
    coverage_repair_decisions_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet coverage repair decision table."),
    ] = DEFAULT_COVERAGE_REPAIR_DECISIONS_INPUT,
    strict_panel_summary_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet strict SIRT6 contrast panel summary."),
    ] = DEFAULT_STRICT_PANEL_SUMMARY_INPUT,
    negatome_repair_decisions_input: Annotated[
        Path,
        typer.Option(help="CSV/parquet NEGATOME repair decision table."),
    ] = DEFAULT_NEGATOME_REPAIR_DECISIONS_INPUT,
    output: Annotated[
        Path,
        typer.Option(help="Output CSV path for the candidate contrast gate table."),
    ] = DEFAULT_OUTPUT,
) -> None:
    """Join coverage, strict panel, and NEGATOME diagnostics into a no-claims gate."""
    contrast_ready = read_table(contrast_ready_input)
    negatome_readiness = read_table(negatome_readiness_input)
    coverage_repair_decisions = read_table(coverage_repair_decisions_input)
    strict_panel_summary = read_table(strict_panel_summary_input)
    negatome_repair_decisions = read_table(negatome_repair_decisions_input)

    gate = build_candidate_contrast_gate(
        contrast_ready=contrast_ready,
        negatome_readiness=negatome_readiness,
        coverage_repair_decisions=coverage_repair_decisions,
        strict_panel_summary=strict_panel_summary,
        negatome_repair_decisions=negatome_repair_decisions,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    gate.write_csv(output)

    typer.echo(f"candidate contrast gate rows: {gate.height}")
    for status, count in sorted(gate_status_counts(gate).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote candidate contrast gate -> {output}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No enrichment statistics or biological claims were computed.")


if __name__ == "__main__":
    app()
