from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import polars as pl
import typer

from longevity_port_pipelines.config import SPECIES_REGISTRY
from longevity_port_pipelines.stages import strict_contrast_panel as strict_panel
from longevity_port_pipelines.stages.coverage_preflight import (
    CONSERVATIVE_CLAIM_POLICY,
    coverage_preflight_for_statuses,
)
from longevity_port_pipelines.stages.tp53_mdm2_gate7_coverage_repair_resolutions import (
    DEFAULT_RESOLUTIONS_PATH,
    read_resolutions,
    resolution_lookup,
)
from longevity_port_pipelines.stages.tp53_mdm2_ortholog_repair_decisions import (
    DEFAULT_REPAIR_DECISIONS_PATH,
    read_repair_decisions,
    validate_repair_decisions,
)
from longevity_port_pipelines.stages.tp53_mdm2_pilot_manifest_validator import (
    DEFAULT_INPUT,
    EXPECTED_CLAIM_POLICY,
    validate_tp53_mdm2_pilot_manifest,
)

DEFAULT_OUTPUT = Path("data/interim/tp53_mdm2_pilot_coverage_preflight.csv")
DEFAULT_STRICT_PANEL_OUTPUT = Path("data/interim/tp53_mdm2_pilot_generic_strict_panel_summary.csv")

TP53_MDM2_LANE_NAME = "tp53_mdm2_elephant"
TP53_MDM2_DEFAULT_PRIORITY = "1"
TP53_MDM2_CONTROL_READINESS_STATUS = "controls_not_evaluated_coverage_blocked"
TP53_MDM2_SPECIES_GROUP_BY_TARGET = {
    "elephant": "long_lived_large_body",
}

REPAIR_KEY_COLUMNS = (
    "candidate_id",
    "source_uniprot",
    "target_species",
    "chain",
)

COVERAGE_PREFLIGHT_SCHEMA = {
    "candidate_set": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "partner_uniprot": pl.Utf8,
    "target_species": pl.Utf8,
    "strict_contrast_gate_status": pl.Utf8,
    "coverage_preflight_status": pl.Utf8,
    "source_ortholog_status": pl.Utf8,
    "local_candidate_row_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "repair_decision": pl.Utf8,
    "repair_priority": pl.Utf8,
    "repair_claim_policy": pl.Utf8,
    "repair_note": pl.Utf8,
    "resolution_status": pl.Utf8,
    "coverage_repair_outcome": pl.Utf8,
    "resolution_blocker_code": pl.Utf8,
    "resolution_source_table": pl.Utf8,
    "resolution_source_row_index": pl.Utf8,
    "claim_policy": pl.Utf8,
    "coverage_preflight_note": pl.Utf8,
    "generic_coverage_status": pl.Utf8,
    "generic_provenance_status": pl.Utf8,
    "generic_repair_status": pl.Utf8,
    "generic_coverage_preflight_status": pl.Utf8,
    "generic_recommended_next_action": pl.Utf8,
    "strict_panel_allowed": pl.Boolean,
    "contrast_dry_run_allowed": pl.Boolean,
    "generic_claim_policy": pl.Utf8,
    "generic_claim_status": pl.Utf8,
    "generic_coverage_preflight_note": pl.Utf8,
}

app = typer.Typer(
    help=(
        "Build a TP53/MDM2 pilot coverage preflight table without live API calls "
        "or biological claims."
    )
)


def _as_str(row: dict[str, Any], column: str) -> str:
    value = row.get(column)
    if value is None:
        return ""
    return str(value).strip()


def _repair_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _as_str(row, "candidate_id"),
        _as_str(row, "source_uniprot"),
        _as_str(row, "target_species"),
        _as_str(row, "chain"),
    )


def _target_species_taxid(target_species: str) -> int | str:
    species = SPECIES_REGISTRY.get(target_species)
    if species is not None:
        return species.taxid

    for registered_species in SPECIES_REGISTRY.values():
        if registered_species.name == target_species:
            return registered_species.taxid

    return ""


def _species_group_for_target_species(target_species: str) -> str:
    return TP53_MDM2_SPECIES_GROUP_BY_TARGET.get(
        target_species,
        "unresolved_species_group",
    )


def _validate_preflight_columns(preflight: pl.DataFrame, required: set[str]) -> None:
    missing = required - set(preflight.columns)
    if missing:
        raise ValueError(f"TP53/MDM2 coverage preflight is missing columns: {sorted(missing)}")


def _empty_preflight() -> pl.DataFrame:
    return pl.DataFrame(schema=COVERAGE_PREFLIGHT_SCHEMA)


def _preflight_from_rows(rows: list[dict[str, Any]]) -> pl.DataFrame:
    if not rows:
        return _empty_preflight()

    return pl.DataFrame(rows).select(
        [
            pl.col(column).cast(dtype).alias(column)
            for column, dtype in COVERAGE_PREFLIGHT_SCHEMA.items()
        ]
    )


def _repair_lookup(
    repair_decisions: pl.DataFrame | None,
) -> dict[tuple[str, str, str, str], dict[str, str]]:
    if repair_decisions is None:
        return {}

    validate_repair_decisions(repair_decisions)

    lookup: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in repair_decisions.iter_rows(named=True):
        lookup[_repair_key(row)] = {
            "repair_decision": _as_str(row, "repair_decision"),
            "repair_priority": _as_str(row, "repair_priority"),
            "repair_claim_policy": _as_str(row, "claim_policy"),
            "repair_note": _as_str(row, "repair_note"),
        }

    return lookup


def coverage_preflight_status(strict_contrast_gate_status: str) -> str:
    if strict_contrast_gate_status == "blocked_contrast_coverage":
        return "blocked_pending_coverage_repair"
    if strict_contrast_gate_status == "eligible_for_contrast_dry_run":
        return "coverage_marked_ready_in_manifest"
    return "blocked_by_noncoverage_gate"


def recommended_next_action(coverage_status: str) -> str:
    if coverage_status == "blocked_pending_coverage_repair":
        return "curate_or_fetch_tp53_mdm2_source_ortholog_coverage"
    if coverage_status == "coverage_marked_ready_in_manifest":
        return "run_contrast_gate_before_cofolding"
    return "resolve_manifest_gate_blocker_before_coverage_preflight"


def generic_coverage_status_for_gate(strict_contrast_gate_status: str) -> str:
    if strict_contrast_gate_status == "eligible_for_contrast_dry_run":
        return "coverage_ready"
    if strict_contrast_gate_status == "blocked_contrast_coverage":
        return "missing_source_ortholog"
    return "unresolved_downstream_provenance"


def generic_provenance_status_for_source_ortholog_status(
    source_ortholog_status: str,
) -> str:
    if source_ortholog_status == "present_source_ortholog":
        return "standard_source_present"
    if source_ortholog_status == "manual_review_required":
        return "manual_review_required"
    return "unresolved"


def generic_repair_status_for_decision(
    *,
    repair_decision: str,
    generic_coverage_status: str,
) -> str:
    if repair_decision == "coverage_ready":
        return "repaired_for_planning"
    if repair_decision == "fetch_or_curate_source_ortholog":
        return "pending"
    if repair_decision in {
        "defer_until_manual_review",
        "review_local_rows_without_source_ortholog",
    }:
        return "needs_manual_review"
    if generic_coverage_status == "coverage_ready":
        return "not_needed"
    return ""


def build_tp53_mdm2_pilot_coverage_preflight(
    manifest: pl.DataFrame,
    *,
    repair_decisions: pl.DataFrame | None = None,
    repair_resolutions: pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Build conservative TP53/MDM2 coverage preflight rows."""

    validate_tp53_mdm2_pilot_manifest(manifest)
    repair_by_key = _repair_lookup(repair_decisions)
    resolution_by_key = (
        resolution_lookup(repair_resolutions) if repair_resolutions is not None else {}
    )

    rows: list[dict[str, Any]] = []
    for row in manifest.iter_rows(named=True):
        gate_status = _as_str(row, "strict_contrast_gate_status")
        key = _repair_key(row)
        repair = repair_by_key.get(key, {})
        resolution = resolution_by_key.get(key, {})

        legacy_status = coverage_preflight_status(gate_status)
        legacy_action = recommended_next_action(legacy_status)
        source_ortholog_status = "not_checked"
        local_candidate_row_status = "not_checked"
        repair_decision = repair.get("repair_decision", "")
        repair_priority = repair.get("repair_priority", "")
        repair_claim_policy = repair.get("repair_claim_policy", "")
        repair_note = repair.get("repair_note", "")
        resolution_status = ""
        coverage_repair_outcome = ""
        resolution_blocker_code = ""
        resolution_source_table = ""
        resolution_source_row_index = ""

        if resolution:
            source_ortholog_status = resolution["source_ortholog_status_after_resolution"]
            local_candidate_row_status = resolution["local_candidate_row_status_after_resolution"]
            repair_decision = resolution["repair_decision_after_resolution"]
            legacy_status = resolution["coverage_preflight_status_after_resolution"]
            legacy_action = resolution["recommended_next_action_after_resolution"]
            resolution_status = resolution["resolution_status"]
            coverage_repair_outcome = resolution["coverage_repair_outcome"]
            resolution_blocker_code = resolution["concrete_source_blocker"]
            resolution_source_table = resolution["source_evidence_table"]
            resolution_source_row_index = resolution["source_evidence_row_index"]
            generic_coverage_status = resolution["coverage_status_after_resolution"]
            generic_provenance_status = resolution["provenance_status_after_resolution"]
            generic_repair_status = resolution["repair_status_after_resolution"]
        else:
            generic_coverage_status = generic_coverage_status_for_gate(gate_status)
            generic_provenance_status = generic_provenance_status_for_source_ortholog_status(
                source_ortholog_status
            )
            generic_repair_status = generic_repair_status_for_decision(
                repair_decision=repair_decision,
                generic_coverage_status=generic_coverage_status,
            )

        generic_preflight = coverage_preflight_for_statuses(
            coverage_status=generic_coverage_status,
            provenance_status=generic_provenance_status,
            repair_status=generic_repair_status,
            claim_policy=CONSERVATIVE_CLAIM_POLICY,
        )

        rows.append(
            {
                "candidate_set": _as_str(row, "candidate_set"),
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "partner_uniprot": _as_str(row, "partner_uniprot"),
                "target_species": _as_str(row, "target_species"),
                "strict_contrast_gate_status": gate_status,
                "coverage_preflight_status": legacy_status,
                "source_ortholog_status": source_ortholog_status,
                "local_candidate_row_status": local_candidate_row_status,
                "recommended_next_action": legacy_action,
                "repair_decision": repair_decision,
                "repair_priority": repair_priority,
                "repair_claim_policy": repair_claim_policy,
                "repair_note": repair_note,
                "resolution_status": resolution_status,
                "coverage_repair_outcome": coverage_repair_outcome,
                "resolution_blocker_code": resolution_blocker_code,
                "resolution_source_table": resolution_source_table,
                "resolution_source_row_index": resolution_source_row_index,
                "claim_policy": _as_str(row, "claim_policy"),
                "coverage_preflight_note": (
                    "Coverage preflight uses committed manifest fields, "
                    "repair-decision rows, and optional decision-bearing coverage "
                    "resolutions only; no Biohub, Boltz, embeddings, cofolding "
                    "jobs, or biological claims are introduced."
                ),
                "generic_coverage_status": generic_coverage_status,
                "generic_provenance_status": generic_provenance_status,
                "generic_repair_status": generic_repair_status,
                "generic_coverage_preflight_status": (generic_preflight.coverage_preflight_status),
                "generic_recommended_next_action": (generic_preflight.recommended_next_action),
                "strict_panel_allowed": generic_preflight.strict_panel_allowed,
                "contrast_dry_run_allowed": (generic_preflight.contrast_dry_run_allowed),
                "generic_claim_policy": generic_preflight.claim_policy,
                "generic_claim_status": generic_preflight.claim_status,
                "generic_coverage_preflight_note": generic_preflight.notes,
            }
        )

    return _preflight_from_rows(rows).sort(["coverage_preflight_status", "candidate_id", "chain"])


def build_tp53_mdm2_generic_strict_panel_input(preflight: pl.DataFrame) -> pl.DataFrame:
    """Map TP53/MDM2 coverage preflight rows into the generic Gate 7 input schema."""

    _validate_preflight_columns(
        preflight,
        {
            "candidate_set",
            "candidate_id",
            "pdb_id",
            "chain",
            "source_uniprot",
            "target_species",
            "strict_contrast_gate_status",
            "generic_coverage_preflight_status",
            "generic_claim_policy",
        },
    )

    rows: list[dict[str, Any]] = []
    for row in preflight.iter_rows(named=True):
        target_species = _as_str(row, "target_species")
        rows.append(
            {
                "candidate_set": _as_str(row, "candidate_set"),
                "lane_name": TP53_MDM2_LANE_NAME,
                "candidate_id": _as_str(row, "candidate_id"),
                "pdb_id": _as_str(row, "pdb_id"),
                "chain": _as_str(row, "chain"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "priority": TP53_MDM2_DEFAULT_PRIORITY,
                "target_species": target_species,
                "target_species_taxid": _target_species_taxid(target_species),
                "species_group": _species_group_for_target_species(target_species),
                "coverage_preflight_status": _as_str(
                    row,
                    "generic_coverage_preflight_status",
                ),
                "control_readiness_status": (
                    "controls_ready"
                    if _as_str(row, "generic_coverage_preflight_status")
                    == "coverage_preflight_ready"
                    else TP53_MDM2_CONTROL_READINESS_STATUS
                ),
                "contrast_readiness_status": _as_str(row, "strict_contrast_gate_status"),
                "claim_policy": (_as_str(row, "generic_claim_policy") or CONSERVATIVE_CLAIM_POLICY),
            }
        )

    if not rows:
        return pl.DataFrame(schema={column: pl.Utf8 for column in strict_panel.REQUIRED_COLUMNS})

    return pl.DataFrame(rows).select(
        [
            "candidate_set",
            "lane_name",
            "candidate_id",
            "pdb_id",
            "chain",
            "source_uniprot",
            "priority",
            "target_species",
            "target_species_taxid",
            "species_group",
            "coverage_preflight_status",
            "control_readiness_status",
            "contrast_readiness_status",
            "claim_policy",
        ]
    )


def build_tp53_mdm2_generic_strict_panel_summary(preflight: pl.DataFrame) -> pl.DataFrame:
    """Build the TP53/MDM2 generic strict panel summary from coverage preflight rows."""

    return strict_panel.build_generic_strict_panel_summary(
        build_tp53_mdm2_generic_strict_panel_input(preflight)
    )


def status_counts(preflight: pl.DataFrame) -> dict[str, int]:
    if preflight.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in preflight.group_by("coverage_preflight_status").len().iter_rows(named=True):
        counts[str(row["coverage_preflight_status"])] = int(row["len"])

    return counts


@app.command()
def main(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            help="TP53/MDM2 pilot manifest CSV to preflight.",
        ),
    ] = DEFAULT_INPUT,
    repair_decisions_path: Annotated[
        Path,
        typer.Option(
            "--repair-decisions",
            help="TP53/MDM2 ortholog repair decision CSV to apply.",
        ),
    ] = DEFAULT_REPAIR_DECISIONS_PATH,
    repair_resolutions_path: Annotated[
        Path,
        typer.Option(
            "--repair-resolutions",
            help="Decision-bearing TP53/MDM2 coverage-repair resolution CSV.",
        ),
    ] = DEFAULT_RESOLUTIONS_PATH,
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            help="Output CSV path for the TP53/MDM2 coverage preflight table.",
        ),
    ] = DEFAULT_OUTPUT,
    strict_panel_output: Annotated[
        Path,
        typer.Option(
            "--strict-panel-output",
            help="Output CSV path for the TP53/MDM2 generic strict panel summary.",
        ),
    ] = DEFAULT_STRICT_PANEL_OUTPUT,
) -> dict[str, Any]:
    """Build a TP53/MDM2 pilot coverage preflight table."""

    manifest = pl.read_csv(input_path)
    repair_decisions = read_repair_decisions(repair_decisions_path)
    repair_resolutions = read_resolutions(repair_resolutions_path)
    preflight = build_tp53_mdm2_pilot_coverage_preflight(
        manifest,
        repair_decisions=repair_decisions,
        repair_resolutions=repair_resolutions,
    )

    strict_panel_summary = build_tp53_mdm2_generic_strict_panel_summary(preflight)

    output.parent.mkdir(parents=True, exist_ok=True)
    preflight.write_csv(output)

    strict_panel_output.parent.mkdir(parents=True, exist_ok=True)
    strict_panel_summary.write_csv(strict_panel_output)

    typer.echo(f"TP53/MDM2 pilot coverage preflight rows: {preflight.height}")
    for status, count in sorted(status_counts(preflight).items()):
        typer.echo(f"{status}: {count}")

    typer.echo(f"Wrote TP53/MDM2 pilot coverage preflight -> {output}")
    typer.echo(f"Wrote TP53/MDM2 generic strict panel summary -> {strict_panel_output}")
    for status, count in sorted(
        strict_panel.strict_panel_status_counts(strict_panel_summary).items()
    ):
        typer.echo(f"strict panel {status}: {count}")
    typer.echo(f"Applied TP53/MDM2 repair decisions from -> {repair_decisions_path}")
    typer.echo(f"Applied TP53/MDM2 coverage-repair resolutions from -> {repair_resolutions_path}")
    typer.echo("No Biohub API calls were made.")
    typer.echo("No Boltz API calls were made.")
    typer.echo("No orthologs were fetched.")
    typer.echo("No embeddings were generated.")
    typer.echo("No cofolding jobs were submitted.")
    typer.echo("No Boltz credits were spent.")
    typer.echo("No biological validation claim was made.")

    return {
        "input": str(input_path),
        "repair_decisions": str(repair_decisions_path),
        "repair_resolutions": str(repair_resolutions_path),
        "output": str(output),
        "strict_panel_output": str(strict_panel_output),
        "rows": preflight.height,
        "strict_panel_rows": strict_panel_summary.height,
        "claim_policy": EXPECTED_CLAIM_POLICY,
        "no_live_actions": True,
    }


if __name__ == "__main__":
    app()
