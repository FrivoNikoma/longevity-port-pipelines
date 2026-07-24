"""Run scoped MDM2 leave-one-control-out and residue-block robustness.

A3 consumes the exact committed A1/A2 evidence and existing ignored embeddings.
It separates shared interface-depletion robustness from a longevity-specific
contrast.  It never performs Gate 8 disposition, Gate 9 promotion, or a
biological claim.
"""

from __future__ import annotations

import csv
import io
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_external_exact_sequence_binding_results as bindings,
)
from longevity_port_pipelines.stages.contrast_robustness import (
    ContrastMetric,
    ContrastScenario,
    ResidueBlock,
    balanced_ordered_blocks,
    build_contrast_scenario,
    build_leave_one_control_out_scenarios,
    sign_flip_count,
)
from longevity_port_pipelines.stages.tp53_mdm2_embedding_based_negatome_control_repair_result import (
    DEFAULT_MAPPING_TABLE,
    EXPECTED_MAPPING_SHA256,
    canonical_text_sha256,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    DEFAULT_RESULT_TABLE as A1_RESULT_TABLE,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    METRIC_FAMILY,
    REFERENCE_SEQUENCE_ROOT_ENV,
    SHUFFLE_CONTROL_COUNT,
    SHUFFLE_POLICY,
    SHUFFLE_SEED,
    MappedInterfaceMetrics,
    PreparedPanel,
    PreparedTarget,
    compute_mapped_interface_metrics,
    prepare_panel,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    load_and_validate_result as load_a1_result,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapping_cutoff_alignment_sensitivity import (
    DEFAULT_SUMMARY_TABLE as A2_SUMMARY_TABLE,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapping_cutoff_alignment_sensitivity import (
    EXPECTED_A1_RESULT_SHA256,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapping_cutoff_alignment_sensitivity import (
    EXPECTED_SUMMARY_RESULT_SHA256 as EXPECTED_A2_SUMMARY_SHA256,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapping_cutoff_alignment_sensitivity import (
    load_and_validate_result as load_a2_result,
)

RESULT_DATE = "2026-07-20"
BLOCK_COUNT = 5
EXPECTED_SOURCE_INTERFACE_COUNT = 47
EXPECTED_SPECIES_RESULT_COUNT = 15
EXPECTED_CONTRAST_RESULT_COUNT = 8
EXPECTED_SPECIES_RESULT_SHA256 = "ac27176b72e691e50ca3daf55ec69ee0d386c01242e6a5ad7c50f7326e9bd90b"
EXPECTED_CONTRAST_RESULT_SHA256 = "2b83c153f729f19f82cd657af30fb4c9d9f29bddeaa79e4c78e37bcae96b6762"
EXPECTED_SUMMARY_RESULT_SHA256 = "90158dd18a67dd509df82f25bd30137979b879809a77fbbc702b8d09b576bcb3"

DEFAULT_SPECIES_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_residue_block_jackknife_species_results.csv"
)
DEFAULT_CONTRAST_RESULT_TABLE = Path("data/input/tp53_mdm2_mdm2_contrast_robustness_results.csv")
DEFAULT_SUMMARY_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_loco_residue_block_jackknife_summary.csv"
)

SPECIES_RESULT_FIELDS = (
    "result_contract_version",
    "row_id",
    "block_id",
    "block_index",
    "block_count",
    "removed_reference_residue_count",
    "removed_reference_zero_based_indices",
    "removed_reference_first_zero_based_index",
    "removed_reference_last_zero_based_index",
    "removed_residues_excluded_entirely",
    "removed_residues_reclassified_as_noninterface",
    "source_interface_residue_count",
    "remaining_interface_residue_count",
    "target_species",
    "target_species_name",
    "target_accession",
    "target_taxid",
    "lifespan_category",
    "mapping_table",
    "mapping_table_canonical_text_sha256",
    "a1_result_table",
    "a1_result_canonical_text_sha256",
    "a2_summary_table",
    "a2_summary_canonical_text_sha256",
    "aligned_residue_count_after_exclusion",
    "mapped_interface_count",
    "noninterface_count",
    "dropped_remaining_interface_count",
    "mapping_status",
    "metric_family",
    "interface_mean_delta",
    "noninterface_mean_delta",
    "enrichment_ratio",
    "effect_size_cohens_d",
    "p_interface_greater",
    "p_interface_less",
    "p_two_sided",
    "shuffle_mask_policy",
    "shuffle_seed",
    "shuffle_control_count",
    "shuffle_ge_observed_count",
    "shuffle_le_observed_count",
    "shuffle_empirical_p_greater",
    "shuffle_empirical_p_less",
    "shuffle_empirical_p_two_sided",
    "a1_enrichment_ratio",
    "direction_vs_one",
    "direction_matches_a1",
    "lower_tail_significant_at_0_05",
    "residue_block_jackknife_run",
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "result_date",
)

CONTRAST_RESULT_FIELDS = (
    "result_contract_version",
    "scenario_id",
    "scenario_kind",
    "omitted_short_lived_species",
    "block_id",
    "block_index",
    "block_size",
    "removed_reference_zero_based_indices",
    "long_lived_species",
    "short_lived_species",
    "short_lived_control_count",
    "long_enrichment_ratio",
    "short_enrichment_ratio",
    "long_effect_size_cohens_d",
    "short_effect_size_cohens_d",
    "enrichment_delta",
    "enrichment_log2_ratio",
    "contrast_sign",
    "full_baseline_contrast_sign",
    "sign_matches_full_baseline",
    "contrast_class",
    "contrast_note",
    "generic_contrast_classification_reused",
    "source_metric_scope",
    "leave_one_control_out_run",
    "residue_block_jackknife_run",
    "single_long_lived_lineage_limitation",
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "result_date",
)

SUMMARY_RESULT_FIELDS = (
    "summary_contract_version",
    "result_id",
    "source_interface_residue_count",
    "block_count",
    "block_sizes",
    "species_jackknife_row_count",
    "contrast_scenario_row_count",
    "full_contrast_scenario_count",
    "loco_contrast_scenario_count",
    "block_contrast_scenario_count",
    "all_a1_species_ratios_below_one",
    "all_jackknife_species_ratios_below_one",
    "all_jackknife_lower_tail_significant_at_0_05",
    "shared_interface_depletion_robustness",
    "block_jackknife_robustness",
    "full_contrast_sign",
    "loco_sign_flip_count",
    "control_identity_robustness",
    "block_contrast_sign_flip_count",
    "block_contrast_sign_robustness",
    "generic_contrast_class_stable",
    "full_contrast_class",
    "longevity_contrast_interpretation_status",
    "leave_one_control_out_run",
    "residue_block_jackknife_run",
    "single_long_lived_lineage_limitation",
    "negatome_metric_included",
    "negatome_metric_compatibility_status",
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "allowed_next_action",
    "claim_status",
    "result_date",
)

FALSE_BOUNDARY_FIELDS = (
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)


@dataclass(frozen=True)
class A3Audit:
    panel: PreparedPanel
    a1_rows_by_accession: dict[str, dict[str, str]]
    blocks: tuple[ResidueBlock, ...]


def _float_text(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("Expected a finite A3 metric")
    return format(value, ".17g")


def _indices_text(indices: tuple[int, ...]) -> str:
    return "|".join(str(index) for index in indices) if indices else "none"


def _direction(value: float) -> str:
    if value < 1.0:
        return "below_one"
    if value > 1.0:
        return "above_one"
    return "equal_one"


def _required_root(explicit: Path | None, env_name: str) -> Path:
    if explicit is None:
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            raise ValueError(f"{env_name} is not configured")
        root = Path(raw)
    else:
        root = explicit
    if not root.exists() or not root.is_dir():
        raise ValueError(f"{env_name} must point to an existing directory")
    return root


def _csv_text(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_csv_text(fields, rows), encoding="utf-8", newline="")


def prepare_audit(
    *,
    repo_root: Path,
    reference_sequence_root: Path,
    binding_root: Path,
) -> A3Audit:
    """Validate committed A1/A2 inputs and construct the deterministic block plan."""
    _, _, a2_summary_rows = load_a2_result(repo_root)
    if any(
        row["sensitivity_status"] != "stable_under_predeclared_a2_grid"
        or row["allowed_next_action"] != "run_leave_one_control_out_and_residue_block_jackknife"
        for row in a2_summary_rows
    ):
        raise ValueError("Committed A2 evidence does not allow A3")

    a1_rows = load_a1_result(repo_root)
    panel = prepare_panel(
        repo_root=repo_root,
        reference_sequence_root=reference_sequence_root,
        binding_root=binding_root,
    )
    if len(panel.interface_reference_indices) != EXPECTED_SOURCE_INTERFACE_COUNT:
        raise ValueError("A3 requires exactly 47 committed A1 interface positions")

    ordered_interface_indices = tuple(sorted(panel.interface_reference_indices))
    blocks = balanced_ordered_blocks(
        ordered_interface_indices,
        block_count=BLOCK_COUNT,
    )
    if tuple(len(block.indices) for block in blocks) != (10, 10, 9, 9, 9):
        raise ValueError("A3 block sizes must be 10/10/9/9/9")

    source_set = set(panel.interface_reference_indices)
    for target in panel.targets:
        aligned_set = {pair.reference_index for pair in target.alignment.aligned_pairs}
        if not source_set.issubset(aligned_set):
            raise ValueError(f"{target.contract.accession}: A3 source mapping is incomplete")

    return A3Audit(
        panel=panel,
        a1_rows_by_accession={row["target_accession"]: row for row in a1_rows},
        blocks=blocks,
    )


def _baseline_metrics(audit: A3Audit) -> dict[str, MappedInterfaceMetrics]:
    metrics_by_accession: dict[str, MappedInterfaceMetrics] = {}
    fields = (
        "aligned_residue_count",
        "mapped_interface_count",
        "interface_mean_delta",
        "noninterface_mean_delta",
        "enrichment_ratio",
        "effect_size_cohens_d",
        "shuffle_ge_observed_count",
        "shuffle_le_observed_count",
        "shuffle_empirical_p_less",
    )
    for target in audit.panel.targets:
        metrics = compute_mapped_interface_metrics(
            reference=audit.panel.reference_embedding.embedding,
            target=target.embedding.embedding,
            interface_reference_indices=audit.panel.interface_reference_indices,
            alignment=target.alignment,
            shuffle_seed=SHUFFLE_SEED,
            shuffle_control_count=SHUFFLE_CONTROL_COUNT,
        )
        observed = {
            "aligned_residue_count": str(metrics.aligned_residue_count),
            "mapped_interface_count": str(metrics.mapped_interface_count),
            "interface_mean_delta": _float_text(metrics.interface_mean_delta),
            "noninterface_mean_delta": _float_text(metrics.noninterface_mean_delta),
            "enrichment_ratio": _float_text(metrics.enrichment_ratio),
            "effect_size_cohens_d": _float_text(metrics.effect_size_cohens_d),
            "shuffle_ge_observed_count": str(metrics.shuffle_ge_observed_count),
            "shuffle_le_observed_count": str(metrics.shuffle_le_observed_count),
            "shuffle_empirical_p_less": _float_text(metrics.shuffle_empirical_p_less),
        }
        expected = audit.a1_rows_by_accession[target.contract.accession]
        if any(observed[field] != expected[field] for field in fields):
            raise ValueError(f"{target.contract.accession}: A3 did not reproduce A1")
        metrics_by_accession[target.contract.accession] = metrics
    return metrics_by_accession


def _as_contrast_metric(
    target: PreparedTarget,
    metrics: MappedInterfaceMetrics,
) -> ContrastMetric:
    return ContrastMetric(
        target_species=target.contract.species,
        target_accession=target.contract.accession,
        lifespan_category=target.contract.lifespan_category,
        enrichment_ratio=metrics.enrichment_ratio,
        effect_size=metrics.effect_size_cohens_d,
    )


def build_species_result_rows(
    audit: A3Audit,
) -> tuple[list[dict[str, str]], dict[tuple[str, str], MappedInterfaceMetrics]]:
    """Compute 5 blocks x 3 species while excluding each block entirely."""
    rows: list[dict[str, str]] = []
    metrics_by_block_accession: dict[tuple[str, str], MappedInterfaceMetrics] = {}
    source_indices = audit.panel.interface_reference_indices

    for block in audit.blocks:
        remaining = tuple(index for index in source_indices if index not in set(block.indices))
        for target in audit.panel.targets:
            metrics = compute_mapped_interface_metrics(
                reference=audit.panel.reference_embedding.embedding,
                target=target.embedding.embedding,
                interface_reference_indices=remaining,
                alignment=target.alignment,
                excluded_reference_indices=block.indices,
                shuffle_seed=SHUFFLE_SEED,
                shuffle_control_count=SHUFFLE_CONTROL_COUNT,
            )
            if metrics.mapped_interface_count != len(remaining):
                raise ValueError("A3 jackknife dropped a remaining interface residue")
            a1_ratio = float(
                audit.a1_rows_by_accession[target.contract.accession]["enrichment_ratio"]
            )
            row = {
                "result_contract_version": "1",
                "row_id": f"{target.contract.accession.lower()}_{block.block_id}",
                "block_id": block.block_id,
                "block_index": str(block.block_index),
                "block_count": str(BLOCK_COUNT),
                "removed_reference_residue_count": str(len(block.indices)),
                "removed_reference_zero_based_indices": _indices_text(block.indices),
                "removed_reference_first_zero_based_index": str(block.first_index),
                "removed_reference_last_zero_based_index": str(block.last_index),
                "removed_residues_excluded_entirely": "true",
                "removed_residues_reclassified_as_noninterface": "false",
                "source_interface_residue_count": str(len(source_indices)),
                "remaining_interface_residue_count": str(len(remaining)),
                "target_species": target.contract.species,
                "target_species_name": target.contract.species_name,
                "target_accession": target.contract.accession,
                "target_taxid": str(target.contract.taxid),
                "lifespan_category": target.contract.lifespan_category,
                "mapping_table": DEFAULT_MAPPING_TABLE.as_posix(),
                "mapping_table_canonical_text_sha256": EXPECTED_MAPPING_SHA256,
                "a1_result_table": A1_RESULT_TABLE.as_posix(),
                "a1_result_canonical_text_sha256": EXPECTED_A1_RESULT_SHA256,
                "a2_summary_table": A2_SUMMARY_TABLE.as_posix(),
                "a2_summary_canonical_text_sha256": EXPECTED_A2_SUMMARY_SHA256,
                "aligned_residue_count_after_exclusion": str(metrics.aligned_residue_count),
                "mapped_interface_count": str(metrics.mapped_interface_count),
                "noninterface_count": str(metrics.noninterface_count),
                "dropped_remaining_interface_count": "0",
                "mapping_status": "complete_after_block_exclusion",
                "metric_family": METRIC_FAMILY,
                "interface_mean_delta": _float_text(metrics.interface_mean_delta),
                "noninterface_mean_delta": _float_text(metrics.noninterface_mean_delta),
                "enrichment_ratio": _float_text(metrics.enrichment_ratio),
                "effect_size_cohens_d": _float_text(metrics.effect_size_cohens_d),
                "p_interface_greater": _float_text(metrics.p_interface_greater),
                "p_interface_less": _float_text(metrics.p_interface_less),
                "p_two_sided": _float_text(metrics.p_two_sided),
                "shuffle_mask_policy": SHUFFLE_POLICY,
                "shuffle_seed": str(SHUFFLE_SEED),
                "shuffle_control_count": str(SHUFFLE_CONTROL_COUNT),
                "shuffle_ge_observed_count": str(metrics.shuffle_ge_observed_count),
                "shuffle_le_observed_count": str(metrics.shuffle_le_observed_count),
                "shuffle_empirical_p_greater": _float_text(metrics.shuffle_empirical_p_greater),
                "shuffle_empirical_p_less": _float_text(metrics.shuffle_empirical_p_less),
                "shuffle_empirical_p_two_sided": _float_text(metrics.shuffle_empirical_p_two_sided),
                "a1_enrichment_ratio": _float_text(a1_ratio),
                "direction_vs_one": _direction(metrics.enrichment_ratio),
                "direction_matches_a1": str(
                    _direction(metrics.enrichment_ratio) == _direction(a1_ratio)
                ).lower(),
                "lower_tail_significant_at_0_05": str(
                    metrics.shuffle_empirical_p_less <= 0.05
                ).lower(),
                "residue_block_jackknife_run": "true",
                "gate8_disposition_run": "false",
                "gate8_promoted": "false",
                "gate9_promoted": "false",
                "biological_claim_made": "false",
                "result_date": RESULT_DATE,
            }
            rows.append(row)
            metrics_by_block_accession[(block.block_id, target.contract.accession)] = metrics

    validate_species_result_rows(rows)
    return rows, metrics_by_block_accession


def _serialize_contrast(
    scenario: ContrastScenario,
    *,
    full_sign: str,
    block: ResidueBlock | None,
) -> dict[str, str]:
    is_loco = scenario.scenario_kind == "leave_one_control_out"
    is_block = scenario.scenario_kind == "residue_block_jackknife"
    return {
        "result_contract_version": "1",
        "scenario_id": scenario.scenario_id,
        "scenario_kind": scenario.scenario_kind,
        "omitted_short_lived_species": scenario.omitted_short_lived_species or "none",
        "block_id": scenario.block_id or "none",
        "block_index": str(block.block_index) if block else "none",
        "block_size": str(len(block.indices)) if block else "none",
        "removed_reference_zero_based_indices": (_indices_text(block.indices) if block else "none"),
        "long_lived_species": scenario.long_lived_species,
        "short_lived_species": "|".join(scenario.short_lived_species),
        "short_lived_control_count": str(scenario.short_lived_control_count),
        "long_enrichment_ratio": _float_text(scenario.long_enrichment_ratio),
        "short_enrichment_ratio": _float_text(scenario.short_enrichment_ratio),
        "long_effect_size_cohens_d": _float_text(scenario.long_effect_size),
        "short_effect_size_cohens_d": _float_text(scenario.short_effect_size),
        "enrichment_delta": _float_text(scenario.enrichment_delta),
        "enrichment_log2_ratio": _float_text(scenario.enrichment_log2_ratio),
        "contrast_sign": scenario.contrast_sign,
        "full_baseline_contrast_sign": full_sign,
        "sign_matches_full_baseline": str(scenario.contrast_sign == full_sign).lower(),
        "contrast_class": scenario.contrast_class,
        "contrast_note": scenario.contrast_note,
        "generic_contrast_classification_reused": "true",
        "source_metric_scope": "a3_block_jackknife" if is_block else "a1_reproduced_baseline",
        "leave_one_control_out_run": str(is_loco).lower(),
        "residue_block_jackknife_run": str(is_block).lower(),
        "single_long_lived_lineage_limitation": "true",
        "gate8_disposition_run": "false",
        "gate8_promoted": "false",
        "gate9_promoted": "false",
        "biological_claim_made": "false",
        "result_date": RESULT_DATE,
    }


def build_contrast_result_rows(
    audit: A3Audit,
    *,
    baseline_metrics: dict[str, MappedInterfaceMetrics],
    block_metrics: dict[tuple[str, str], MappedInterfaceMetrics],
) -> tuple[list[dict[str, str]], tuple[ContrastScenario, ...]]:
    """Build the full, two LOCO, and five block-jackknife contrasts."""
    long_target = next(
        target
        for target in audit.panel.targets
        if target.contract.lifespan_category == "long_lived"
    )
    short_targets = tuple(
        target
        for target in audit.panel.targets
        if target.contract.lifespan_category == "short_lived"
    )
    baseline_scenarios = build_leave_one_control_out_scenarios(
        long_metric=_as_contrast_metric(
            long_target,
            baseline_metrics[long_target.contract.accession],
        ),
        short_metrics=tuple(
            _as_contrast_metric(target, baseline_metrics[target.contract.accession])
            for target in short_targets
        ),
    )
    full_sign = baseline_scenarios[0].contrast_sign
    scenarios: list[ContrastScenario] = list(baseline_scenarios)
    block_by_id: dict[str, ResidueBlock] = {}

    for block in audit.blocks:
        scenario = build_contrast_scenario(
            scenario_id=f"{block.block_id}_short_lived_baseline",
            scenario_kind="residue_block_jackknife",
            block_id=block.block_id,
            long_metric=_as_contrast_metric(
                long_target,
                block_metrics[(block.block_id, long_target.contract.accession)],
            ),
            short_metrics=tuple(
                _as_contrast_metric(
                    target,
                    block_metrics[(block.block_id, target.contract.accession)],
                )
                for target in short_targets
            ),
        )
        scenarios.append(scenario)
        block_by_id[block.block_id] = block

    rows = [
        _serialize_contrast(
            scenario,
            full_sign=full_sign,
            block=block_by_id.get(scenario.block_id or ""),
        )
        for scenario in scenarios
    ]
    validate_contrast_result_rows(rows)
    return rows, tuple(scenarios)


def build_summary_result_rows(
    audit: A3Audit,
    species_rows: list[dict[str, str]],
    scenarios: tuple[ContrastScenario, ...],
) -> list[dict[str, str]]:
    """Separate shared-depletion robustness from longevity interpretation."""
    full = scenarios[0]
    loco = tuple(
        scenario for scenario in scenarios if scenario.scenario_kind == "leave_one_control_out"
    )
    block_scenarios = tuple(
        scenario for scenario in scenarios if scenario.scenario_kind == "residue_block_jackknife"
    )
    all_a1_below = all(
        float(row["enrichment_ratio"]) < 1.0 for row in audit.a1_rows_by_accession.values()
    )
    all_blocks_below = all(float(row["enrichment_ratio"]) < 1.0 for row in species_rows)
    all_blocks_lower_tail = all(
        row["lower_tail_significant_at_0_05"] == "true" for row in species_rows
    )
    shared_robust = all_a1_below and all_blocks_below
    block_robust = shared_robust and all_blocks_lower_tail
    loco_flips = sign_flip_count(loco, baseline_sign=full.contrast_sign)
    block_flips = sign_flip_count(block_scenarios, baseline_sign=full.contrast_sign)
    control_robust = loco_flips == 0
    block_contrast_robust = block_flips == 0
    class_stable = all(scenario.contrast_class == full.contrast_class for scenario in scenarios)
    longevity_robust = block_robust and control_robust and block_contrast_robust and class_stable

    if longevity_robust:
        interpretation = "longevity_contrast_robust_under_predeclared_a3_checks"
        next_action = "review_scoped_gate8_disposition_prerequisites"
    elif shared_robust:
        interpretation = "shared_interface_constraint_robust_but_longevity_contrast_not_robust"
        next_action = "add_independent_short_lived_controls_or_limit_to_shared_interface_constraint"
    else:
        interpretation = "shared_interface_depletion_not_robust_under_a3"
        next_action = "resolve_a3_residue_block_sensitivity"

    rows = [
        {
            "summary_contract_version": "1",
            "result_id": "tp53_mdm2_mdm2_a3_robustness_summary",
            "source_interface_residue_count": str(EXPECTED_SOURCE_INTERFACE_COUNT),
            "block_count": str(BLOCK_COUNT),
            "block_sizes": "|".join(str(len(block.indices)) for block in audit.blocks),
            "species_jackknife_row_count": str(len(species_rows)),
            "contrast_scenario_row_count": str(len(scenarios)),
            "full_contrast_scenario_count": "1",
            "loco_contrast_scenario_count": str(len(loco)),
            "block_contrast_scenario_count": str(len(block_scenarios)),
            "all_a1_species_ratios_below_one": str(all_a1_below).lower(),
            "all_jackknife_species_ratios_below_one": str(all_blocks_below).lower(),
            "all_jackknife_lower_tail_significant_at_0_05": str(all_blocks_lower_tail).lower(),
            "shared_interface_depletion_robustness": ("robust" if shared_robust else "sensitive"),
            "block_jackknife_robustness": "robust" if block_robust else "sensitive",
            "full_contrast_sign": full.contrast_sign,
            "loco_sign_flip_count": str(loco_flips),
            "control_identity_robustness": (
                "robust" if control_robust else "control_identity_sensitive"
            ),
            "block_contrast_sign_flip_count": str(block_flips),
            "block_contrast_sign_robustness": (
                "robust" if block_contrast_robust else "block_sensitive"
            ),
            "generic_contrast_class_stable": str(class_stable).lower(),
            "full_contrast_class": full.contrast_class,
            "longevity_contrast_interpretation_status": interpretation,
            "leave_one_control_out_run": "true",
            "residue_block_jackknife_run": "true",
            "single_long_lived_lineage_limitation": "true",
            "negatome_metric_included": "false",
            "negatome_metric_compatibility_status": (
                "not_applied_pending_separate_metric_compatibility_audit"
            ),
            "gate8_disposition_run": "false",
            "gate8_promoted": "false",
            "gate9_promoted": "false",
            "biological_claim_made": "false",
            "allowed_next_action": next_action,
            "claim_status": "technical_a3_robustness_result_no_gate8_disposition",
            "result_date": RESULT_DATE,
        }
    ]
    validate_summary_result_rows(rows)
    return rows


def validate_species_result_rows(rows: list[dict[str, str]]) -> None:
    if len(rows) != EXPECTED_SPECIES_RESULT_COUNT:
        raise ValueError("Expected exactly 15 A3 species jackknife rows")
    if len({row.get("row_id") for row in rows}) != len(rows):
        raise ValueError("A3 species row identifiers must be unique")
    for row in rows:
        if tuple(row) != SPECIES_RESULT_FIELDS:
            raise ValueError("A3 species fields or field order changed")
        if row["removed_residues_excluded_entirely"] != "true":
            raise ValueError("A3 removed residues were not excluded")
        if row["removed_residues_reclassified_as_noninterface"] != "false":
            raise ValueError("A3 removed residues entered the non-interface background")
        if int(row["mapped_interface_count"]) != int(row["remaining_interface_residue_count"]):
            raise ValueError("A3 remaining interface mapping is incomplete")
        for field in FALSE_BOUNDARY_FIELDS:
            if row[field] != "false":
                raise ValueError(f"Forbidden A3 boundary changed: {field}")


def validate_contrast_result_rows(rows: list[dict[str, str]]) -> None:
    if len(rows) != EXPECTED_CONTRAST_RESULT_COUNT:
        raise ValueError("Expected exactly eight A3 contrast rows")
    if len({row.get("scenario_id") for row in rows}) != len(rows):
        raise ValueError("A3 contrast identifiers must be unique")
    kinds = [row.get("scenario_kind") for row in rows]
    if kinds.count("full") != 1:
        raise ValueError("A3 requires one full contrast")
    if kinds.count("leave_one_control_out") != 2:
        raise ValueError("A3 requires two LOCO contrasts")
    if kinds.count("residue_block_jackknife") != 5:
        raise ValueError("A3 requires five block contrasts")
    for row in rows:
        if tuple(row) != CONTRAST_RESULT_FIELDS:
            raise ValueError("A3 contrast fields or field order changed")
        if row["generic_contrast_classification_reused"] != "true":
            raise ValueError("A3 did not reuse generic contrast classification")
        for field in FALSE_BOUNDARY_FIELDS:
            if row[field] != "false":
                raise ValueError(f"Forbidden A3 boundary changed: {field}")


def validate_summary_result_rows(rows: list[dict[str, str]]) -> None:
    if len(rows) != 1 or tuple(rows[0]) != SUMMARY_RESULT_FIELDS:
        raise ValueError("A3 requires exactly one ordered summary row")
    row = rows[0]
    if row["leave_one_control_out_run"] != "true":
        raise ValueError("A3 summary does not record LOCO")
    if row["residue_block_jackknife_run"] != "true":
        raise ValueError("A3 summary does not record block jackknife")
    for field in FALSE_BOUNDARY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"Forbidden A3 boundary changed: {field}")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _require_canonical_text_sha256(path: Path, expected: str) -> None:
    observed = canonical_text_sha256(path)
    if observed != expected:
        raise ValueError(f"{path.as_posix()}: canonical text SHA-256 changed")


def load_and_validate_result(
    root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Load and fail-closed validate the three committed A3 result tables."""
    species_path = root / DEFAULT_SPECIES_RESULT_TABLE
    contrast_path = root / DEFAULT_CONTRAST_RESULT_TABLE
    summary_path = root / DEFAULT_SUMMARY_RESULT_TABLE

    _require_canonical_text_sha256(species_path, EXPECTED_SPECIES_RESULT_SHA256)
    _require_canonical_text_sha256(contrast_path, EXPECTED_CONTRAST_RESULT_SHA256)
    _require_canonical_text_sha256(summary_path, EXPECTED_SUMMARY_RESULT_SHA256)

    species_rows = _read_csv_rows(species_path)
    contrast_rows = _read_csv_rows(contrast_path)
    summary_rows = _read_csv_rows(summary_path)
    validate_species_result_rows(species_rows)
    validate_contrast_result_rows(contrast_rows)
    validate_summary_result_rows(summary_rows)

    expected_accessions = {"G3SX30", "P23804", "A0ABM2YB85"}
    expected_blocks = {
        "block_1": ("0", "10"),
        "block_2": ("1", "10"),
        "block_3": ("2", "9"),
        "block_4": ("3", "9"),
        "block_5": ("4", "9"),
    }
    expected_grid = {
        (block_id, accession) for block_id in expected_blocks for accession in expected_accessions
    }
    observed_grid = {(row["block_id"], row["target_accession"]) for row in species_rows}
    if observed_grid != expected_grid:
        raise ValueError("Committed A3 species block/accession grid changed")

    for block_id, (block_index, block_size) in expected_blocks.items():
        block_rows = [row for row in species_rows if row["block_id"] == block_id]
        if {row["block_index"] for row in block_rows} != {block_index}:
            raise ValueError(f"{block_id}: block index changed")
        if {row["removed_reference_residue_count"] for row in block_rows} != {block_size}:
            raise ValueError(f"{block_id}: block size changed")
        if len({row["removed_reference_zero_based_indices"] for row in block_rows}) != 1:
            raise ValueError(f"{block_id}: species rows disagree on removed residues")

    expected_scenario_ids = [
        "full_short_lived_baseline",
        "leave_mouse_out",
        "leave_hamster_out",
        "block_1_short_lived_baseline",
        "block_2_short_lived_baseline",
        "block_3_short_lived_baseline",
        "block_4_short_lived_baseline",
        "block_5_short_lived_baseline",
    ]
    if [row["scenario_id"] for row in contrast_rows] != expected_scenario_ids:
        raise ValueError("Committed A3 contrast scenario order or identity changed")
    if {row["contrast_class"] for row in contrast_rows} != {"shared_interface_constraint"}:
        raise ValueError("Committed A3 generic contrast classification changed")

    expected_provenance = {
        "mapping_table_canonical_text_sha256": EXPECTED_MAPPING_SHA256,
        "a1_result_canonical_text_sha256": EXPECTED_A1_RESULT_SHA256,
        "a2_summary_canonical_text_sha256": EXPECTED_A2_SUMMARY_SHA256,
    }
    for field, expected in expected_provenance.items():
        if {row[field] for row in species_rows} != {expected}:
            raise ValueError(f"Committed A3 species provenance changed: {field}")

    a1_rows = load_a1_result(root)
    a1_by_accession = {row["target_accession"]: row for row in a1_rows}
    if set(a1_by_accession) != expected_accessions:
        raise ValueError("Committed A1 accession set changed below A3")
    for row in species_rows:
        expected_ratio = a1_by_accession[row["target_accession"]]["enrichment_ratio"]
        if row["a1_enrichment_ratio"] != expected_ratio:
            raise ValueError(f"{row['row_id']}: A1 enrichment binding changed")

    _, _, a2_summary_rows = load_a2_result(root)
    if any(
        row["sensitivity_status"] != "stable_under_predeclared_a2_grid"
        or row["allowed_next_action"] != "run_leave_one_control_out_and_residue_block_jackknife"
        for row in a2_summary_rows
    ):
        raise ValueError("Committed A2 evidence no longer allows the recorded A3 result")

    summary = summary_rows[0]
    expected_summary = {
        "block_sizes": "10|10|9|9|9",
        "species_jackknife_row_count": "15",
        "contrast_scenario_row_count": "8",
        "shared_interface_depletion_robustness": "robust",
        "block_jackknife_robustness": "robust",
        "full_contrast_sign": "positive",
        "loco_sign_flip_count": "1",
        "control_identity_robustness": "control_identity_sensitive",
        "block_contrast_sign_flip_count": "1",
        "block_contrast_sign_robustness": "block_sensitive",
        "generic_contrast_class_stable": "true",
        "full_contrast_class": "shared_interface_constraint",
        "longevity_contrast_interpretation_status": (
            "shared_interface_constraint_robust_but_longevity_contrast_not_robust"
        ),
        "allowed_next_action": (
            "add_independent_short_lived_controls_or_limit_to_shared_interface_constraint"
        ),
    }
    for field, expected in expected_summary.items():
        if summary[field] != expected:
            raise ValueError(
                f"Committed A3 summary changed: expected {field}={expected!r}, "
                f"got {summary[field]!r}"
            )

    return species_rows, contrast_rows, summary_rows


def _resolved_output(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


app = typer.Typer(add_completion=False)


@app.command()
def main(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    reference_sequence_root: Annotated[
        Path | None,
        typer.Option(help="External exact Q00987/G3SX30 FASTA root."),
    ] = None,
    binding_root: Annotated[
        Path | None,
        typer.Option(help="External exact P23804/A0ABM2YB85 binding root."),
    ] = None,
    species_output: Annotated[
        Path,
        typer.Option(help="Long-form 15-row species jackknife table."),
    ] = DEFAULT_SPECIES_RESULT_TABLE,
    contrast_output: Annotated[
        Path,
        typer.Option(help="Eight-row full/LOCO/block contrast table."),
    ] = DEFAULT_CONTRAST_RESULT_TABLE,
    summary_output: Annotated[
        Path,
        typer.Option(help="One-row A3 robustness summary."),
    ] = DEFAULT_SUMMARY_RESULT_TABLE,
    yes_run: Annotated[
        bool,
        typer.Option("--yes-run", help="Compute and write all local A3 results."),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Explicitly replace all three A3 outputs."),
    ] = False,
) -> None:
    """Validate A3 inputs or explicitly run local robustness calculations."""
    load_dotenv()
    root = repo_root.resolve()
    try:
        reference_root = _required_root(
            reference_sequence_root,
            REFERENCE_SEQUENCE_ROOT_ENV,
        )
        exact_binding_root = _required_root(
            binding_root,
            bindings.BINDING_ROOT_ENV,
        )
        audit = prepare_audit(
            repo_root=root,
            reference_sequence_root=reference_root,
            binding_root=exact_binding_root,
        )
    except (OSError, ValueError) as exc:
        typer.echo(f"BLOCKED: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("A3 scoped MDM2 LOCO/residue-block input audit: ready")
    typer.echo(
        f"source_interface_rows={len(audit.panel.interface_reference_indices)} "
        f"blocks={'|'.join(str(len(block.indices)) for block in audit.blocks)}"
    )
    typer.echo("planned_rows: species_jackknife=15 contrast_robustness=8 summary=1")
    outputs = (
        _resolved_output(root, species_output),
        _resolved_output(root, contrast_output),
        _resolved_output(root, summary_output),
    )

    if not yes_run:
        typer.echo("DRY RUN: no A3 robustness metrics were computed and no file was written.")
    else:
        existing = [path for path in outputs if path.exists()]
        if existing and not overwrite:
            typer.echo(
                "BLOCKED: an A3 output already exists; use --overwrite only after auditing all three.",
                err=True,
            )
            raise typer.Exit(code=1)
        try:
            baseline_metrics = _baseline_metrics(audit)
            species_rows, block_metrics = build_species_result_rows(audit)
            contrast_rows, scenarios = build_contrast_result_rows(
                audit,
                baseline_metrics=baseline_metrics,
                block_metrics=block_metrics,
            )
            summary_rows = build_summary_result_rows(
                audit,
                species_rows,
                scenarios,
            )
        except ValueError as exc:
            typer.echo(f"BLOCKED: {exc}", err=True)
            raise typer.Exit(code=1) from exc

        _write_csv(outputs[0], SPECIES_RESULT_FIELDS, species_rows)
        _write_csv(outputs[1], CONTRAST_RESULT_FIELDS, contrast_rows)
        _write_csv(outputs[2], SUMMARY_RESULT_FIELDS, summary_rows)
        typer.echo("Wrote 15 species, 8 contrast, and 1 summary A3 rows.")

    typer.echo("No network, Biohub/ESMC, or structural-model calls were made.")
    typer.echo("No new embeddings or data/output artifacts were written.")
    typer.echo("No Gate 8 disposition or Gate 8/Gate 9 promotion was performed.")
    typer.echo("No biological claim was made.")


if __name__ == "__main__":
    app()
