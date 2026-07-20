"""Audit MDM2 interface enrichment across mapping, cutoff, and alignment choices.

The A2 stage is dry-run-first and entirely local.  It binds one exact 1YCR PDB,
the exact A1 sequences and ignored embeddings, then evaluates the same A1
residue-level metric over a predeclared Cartesian grid.  It prepares robustness
evidence for Gate 8; it does not perform a Gate 8 disposition or open Gate 9.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import os
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from statistics import median
from typing import Annotated

import typer
from Bio.PDB import PDBParser  # type: ignore[attr-defined]
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from dotenv import load_dotenv

from longevity_port_pipelines.stages.interface import extract_interface_residues
from longevity_port_pipelines.stages.reference_coordinate_mapping import (
    AlignmentPolicy,
    ReferenceTargetAlignment,
    align_reference_to_target,
    enumerate_reference_to_target_alignments,
)
from longevity_port_pipelines.stages.tp53_mdm2_embedding_based_negatome_control_repair_result import (
    canonical_text_sha256,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    DEFAULT_RESULT_TABLE as A1_RESULT_TABLE,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    MAPPING_SOURCE,
    METRIC_FAMILY,
    REFERENCE_CONTRACT,
    SHUFFLE_CONTROL_COUNT,
    SHUFFLE_POLICY,
    SHUFFLE_SEED,
    TARGETS,
    MappedInterfaceMetrics,
    PreparedPanel,
    PreparedTarget,
    _float_text,
    _indices_text,
    compute_mapped_interface_metrics,
    prepare_panel,
)

PDB_PATH_ENV = "MDM2_A2_PDB_PATH"
EXPECTED_PDB_SHA256 = "7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493"
EXPECTED_A1_RESULT_SHA256 = "bcf4075b428c4bf1494a3247357a8c1736c761f9c1a8bdbf2f0b789b51823ebb"
EXPECTED_FULL_MAPPING_SHA256 = "2794c3adabb69ff739e24af6179d587424acab293407d44b536bf0a8111dbb5f"
EXPECTED_SCENARIO_RESULT_SHA256 = "33ec3211de227cab56367528019f7a17041759e29a8cf16795dd41db5ae26c07"
EXPECTED_SUMMARY_RESULT_SHA256 = "db58d84a53b2a891eb80d5e065457355c48d6a198cea7a84b47d44b392895ba4"
RESULT_DATE = "2026-07-20"

DEFAULT_FULL_MAPPING_TABLE = Path("data/input/tp53_mdm2_1ycr_q00987_full_chain_mapping.csv")
DEFAULT_SCENARIO_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_mapping_cutoff_alignment_sensitivity_results.csv"
)
DEFAULT_SUMMARY_TABLE = Path(
    "data/input/tp53_mdm2_mdm2_mapping_cutoff_alignment_sensitivity_summary.csv"
)

CUTOFFS_ANGSTROM = (6.0, 7.0, 8.0, 9.0, 10.0)
EXPECTED_INTERFACE_COUNTS = {
    6.0: (30, 12),
    7.0: (42, 13),
    8.0: (47, 13),
    9.0: (54, 13),
    10.0: (56, 13),
}
ALIGNMENT_POLICIES = (
    AlignmentPolicy("canonical_free_terminal", -10, -1, False),
    AlignmentPolicy("canonical_penalized_terminal", -10, -1, True),
    AlignmentPolicy("looser_gap_open", -8, -1, False),
    AlignmentPolicy("stricter_gap_open", -12, -1, False),
    AlignmentPolicy("stricter_gap_extension", -10, -2, False),
)
EXPECTED_OPTIMAL_COUNTS = {
    "G3SX30": {
        "canonical_free_terminal": 9,
        "canonical_penalized_terminal": 9,
        "looser_gap_open": 9,
        "stricter_gap_open": 9,
        "stricter_gap_extension": 9,
    },
    "P23804": {
        "canonical_free_terminal": 8,
        "canonical_penalized_terminal": 8,
        "looser_gap_open": 8,
        "stricter_gap_open": 8,
        "stricter_gap_extension": 8,
    },
    "A0ABM2YB85": {
        "canonical_free_terminal": 2,
        "canonical_penalized_terminal": 4,
        "looser_gap_open": 2,
        "stricter_gap_open": 2,
        "stricter_gap_extension": 2,
    },
}
EXPECTED_SCENARIO_COUNTS = {"G3SX30": 225, "P23804": 200, "A0ABM2YB85": 60}
EXPECTED_TOTAL_SCENARIOS = 485

FULL_MAPPING_FIELDS = (
    "mapping_contract_version",
    "pdb_id",
    "pdb_model",
    "pdb_chain",
    "pdb_sha256",
    "chain_local_zero_based_index",
    "pdb_residue_name",
    "pdb_residue_number",
    "pdb_insertion_code",
    "pdb_residue_label",
    "residue_one_letter",
    "direct_full_length_zero_based_index",
    "sequence_alignment_full_length_zero_based_index",
    "full_length_one_based_position",
    "q00987_sequence_sha256",
    "direct_residue_identity_consistent",
    "sequence_mapping_agrees_with_direct",
    "mapping_source",
    "mapping_status",
)

SCENARIO_FIELDS = (
    "result_contract_version",
    "scenario_id",
    "target_species",
    "target_accession",
    "lifespan_category",
    "pdb_id",
    "pdb_sha256",
    "full_chain_mapping_table",
    "full_chain_mapping_sha256",
    "a1_result_table",
    "a1_result_sha256",
    "interface_distance_cutoff_angstrom",
    "source_interface_count",
    "source_interface_reference_zero_based_indices",
    "alignment_policy_id",
    "alignment_gap_open",
    "alignment_gap_extend",
    "alignment_terminal_penalty",
    "alignment_optimal_index",
    "alignment_optimal_count",
    "alignment_trace_sha256",
    "alignment_trace_length",
    "aligned_residue_count",
    "mapped_interface_count",
    "dropped_interface_count",
    "dropped_reference_zero_based_indices",
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
    "direction_vs_one",
    "lower_tail_significant_at_0_05",
    "is_a1_baseline_scenario",
    "a1_baseline_reproduced",
    "mapping_cutoff_alignment_sensitivity_run",
    "gate8_disposition_run",
    "gate9_promoted",
    "biological_claim_made",
    "result_date",
)

SUMMARY_FIELDS = (
    "summary_contract_version",
    "target_species",
    "target_accession",
    "lifespan_category",
    "scenario_count",
    "expected_scenario_count",
    "cutoff_count",
    "alignment_policy_count",
    "unique_alignment_trace_count",
    "baseline_enrichment_ratio",
    "minimum_enrichment_ratio",
    "median_enrichment_ratio",
    "maximum_enrichment_ratio",
    "minimum_effect_size_cohens_d",
    "maximum_effect_size_cohens_d",
    "ratio_below_one_count",
    "ratio_equal_one_count",
    "ratio_above_one_count",
    "direction_flip_count_vs_a1",
    "lower_tail_significant_count_at_0_05",
    "mapping_complete_scenario_count",
    "a1_baseline_reproduced",
    "predeclared_stability_criteria",
    "sensitivity_status",
    "mapping_cutoff_alignment_sensitivity_run",
    "leave_one_control_out_run",
    "residue_block_jackknife_run",
    "single_long_lived_lineage_limitation",
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
    "allowed_next_action",
    "claim_status",
    "result_date",
)

STABILITY_CRITERIA = (
    "all_scenarios_preserve_a1_ratio_side_of_one|"
    "all_scenarios_shuffle_lower_tail_p_le_0.05|"
    "all_source_interface_residues_mapped|a1_baseline_exactly_reproduced"
)

app = typer.Typer(add_completion=False)


@dataclass(frozen=True)
class InterfaceMask:
    cutoff: float
    chain_local_indices: tuple[int, ...]
    reference_indices: tuple[int, ...]
    tp53_chain_local_indices: tuple[int, ...]


@dataclass(frozen=True)
class ScenarioSpec:
    target: PreparedTarget
    mask: InterfaceMask
    policy: AlignmentPolicy
    alignment: ReferenceTargetAlignment


@dataclass(frozen=True)
class A2Audit:
    panel: PreparedPanel
    full_mapping_rows: tuple[dict[str, str], ...]
    masks: tuple[InterfaceMask, ...]
    scenarios: tuple[ScenarioSpec, ...]
    a1_rows_by_accession: dict[str, dict[str, str]]


def _csv_text(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_csv_text(fields, rows), encoding="utf-8", newline="")


def _canonical_rows_sha256(fields: tuple[str, ...], rows: list[dict[str, str]]) -> str:
    return hashlib.sha256(_csv_text(fields, rows).encode("utf-8")).hexdigest()


def _required_path(explicit: Path | None, env_name: str, *, directory: bool) -> Path:
    value = explicit
    if value is None:
        raw = os.environ.get(env_name, "").strip()
        if not raw:
            raise ValueError(f"{env_name} is not configured")
        value = Path(raw)
    if (
        not value.exists()
        or (directory and not value.is_dir())
        or (not directory and not value.is_file())
    ):
        kind = "directory" if directory else "file"
        raise ValueError(f"{env_name} must point to an existing {kind}")
    return value


def load_a1_rows(repo_root: Path) -> dict[str, dict[str, str]]:
    """Load the exact A1 checkpoint used as the 8 A canonical baseline."""
    path = repo_root / A1_RESULT_TABLE
    if canonical_text_sha256(path) != EXPECTED_A1_RESULT_SHA256:
        raise ValueError("Committed A1 result table SHA-256 changed")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if [row.get("target_accession") for row in rows] != [target.accession for target in TARGETS]:
        raise ValueError("Committed A1 target panel or order changed")
    return {row["target_accession"]: row for row in rows}


def build_full_chain_mapping_rows(
    *,
    pdb_path: Path,
    q00987_sequence: str,
) -> list[dict[str, str]]:
    """Audit every resolved 1YCR:A residue against full-length Q00987."""
    observed_pdb_sha256 = hashlib.sha256(pdb_path.read_bytes()).hexdigest()
    if observed_pdb_sha256 != EXPECTED_PDB_SHA256:
        raise ValueError("1YCR PDB SHA-256 mismatch")
    if len(q00987_sequence) != REFERENCE_CONTRACT.length:
        raise ValueError("Q00987 sequence length changed")
    q00987_sha256 = hashlib.sha256(q00987_sequence.encode("ascii")).hexdigest()
    if q00987_sha256 != REFERENCE_CONTRACT.sequence_sha256:
        raise ValueError("Q00987 sequence SHA-256 changed")

    parser = PDBParser(QUIET=True)  # type: ignore[no-untyped-call]
    structure = parser.get_structure(  # type: ignore[no-untyped-call]
        "1YCR",
        str(pdb_path),
    )
    model = next(iter(structure))
    if "A" not in model:
        raise ValueError("1YCR model 1 has no chain A")
    residues = [
        residue
        for residue in model["A"]
        if is_aa(residue, standard=False)  # type: ignore[no-untyped-call]
    ]
    if len(residues) != 85:
        raise ValueError(f"Expected 85 resolved 1YCR:A residues, got {len(residues)}")

    chain_sequence = "".join(
        seq1(residue.get_resname())  # type: ignore[no-untyped-call]
        for residue in residues
    )
    sequence_alignment = align_reference_to_target(q00987_sequence, chain_sequence)
    if sequence_alignment.optimal_alignment_count != 1:
        raise ValueError("Full 1YCR:A-to-Q00987 sequence mapping is not unique")
    chain_to_reference = {
        pair.target_index: pair.reference_index for pair in sequence_alignment.aligned_pairs
    }

    rows: list[dict[str, str]] = []
    for chain_local_index, residue in enumerate(residues):
        hetero_flag, pdb_number, insertion_code = residue.id
        insertion = str(insertion_code).strip()
        if str(hetero_flag).strip() or insertion:
            raise ValueError("1YCR:A contains an unsupported hetero residue or insertion code")
        letter = seq1(residue.get_resname())  # type: ignore[no-untyped-call]
        direct_reference_index = int(pdb_number) - 1
        sequence_reference_index = chain_to_reference.get(chain_local_index)
        if sequence_reference_index is None:
            raise ValueError("A resolved 1YCR:A residue was dropped by sequence alignment")
        direct_identity = q00987_sequence[direct_reference_index] == letter
        mappings_agree = sequence_reference_index == direct_reference_index
        if not direct_identity or not mappings_agree:
            raise ValueError(
                "1YCR DBREF numbering, residue identity, and sequence mapping disagree"
            )

        rows.append(
            {
                "mapping_contract_version": "1",
                "pdb_id": "1YCR",
                "pdb_model": "1",
                "pdb_chain": "A",
                "pdb_sha256": observed_pdb_sha256,
                "chain_local_zero_based_index": str(chain_local_index),
                "pdb_residue_name": residue.get_resname(),
                "pdb_residue_number": str(pdb_number),
                "pdb_insertion_code": "none",
                "pdb_residue_label": f"{residue.get_resname()}{pdb_number}",
                "residue_one_letter": letter,
                "direct_full_length_zero_based_index": str(direct_reference_index),
                "sequence_alignment_full_length_zero_based_index": str(sequence_reference_index),
                "full_length_one_based_position": str(direct_reference_index + 1),
                "q00987_sequence_sha256": q00987_sha256,
                "direct_residue_identity_consistent": "true",
                "sequence_mapping_agrees_with_direct": "true",
                "mapping_source": MAPPING_SOURCE,
                "mapping_status": "audited_direct_dbref_and_unique_sequence_alignment_agree",
            }
        )

    if [int(row["pdb_residue_number"]) for row in rows] != list(range(25, 110)):
        raise ValueError("Expected contiguous 1YCR:A PDB residue numbers 25..109")
    return rows


def build_interface_masks(
    *,
    repo_root: Path,
    pdb_path: Path,
    full_mapping_rows: list[dict[str, str]],
) -> tuple[InterfaceMask, ...]:
    """Extract and map the predeclared nested interface cutoff masks."""
    local_to_reference = {
        int(row["chain_local_zero_based_index"]): int(row["direct_full_length_zero_based_index"])
        for row in full_mapping_rows
    }
    masks: list[InterfaceMask] = []
    previous_mdm2: set[int] | None = None
    previous_tp53: set[int] | None = None
    for cutoff in CUTOFFS_ANGSTROM:
        mdm2, tp53 = extract_interface_residues(
            pdb_path,
            "A",
            "B",
            distance_cutoff=cutoff,
        )
        expected_mdm2, expected_tp53 = EXPECTED_INTERFACE_COUNTS[cutoff]
        if (len(mdm2), len(tp53)) != (expected_mdm2, expected_tp53):
            raise ValueError(f"Unexpected interface counts at {cutoff:.1f} A")
        mdm2_set = set(mdm2)
        tp53_set = set(tp53)
        if previous_mdm2 is not None and not previous_mdm2 <= mdm2_set:
            raise ValueError("MDM2 interface masks are not nested across cutoffs")
        if previous_tp53 is not None and not previous_tp53 <= tp53_set:
            raise ValueError("TP53 interface masks are not nested across cutoffs")
        try:
            reference_indices = tuple(local_to_reference[index] for index in mdm2)
        except KeyError as exc:
            raise ValueError("Interface residue is absent from full-chain mapping") from exc
        masks.append(
            InterfaceMask(
                cutoff=cutoff,
                chain_local_indices=tuple(mdm2),
                reference_indices=reference_indices,
                tp53_chain_local_indices=tuple(tp53),
            )
        )
        previous_mdm2 = mdm2_set
        previous_tp53 = tp53_set

    a1_mapping_path = repo_root / "data/input/tp53_mdm2_1ycr_q00987_interface_mapping.csv"
    with a1_mapping_path.open(encoding="utf-8-sig", newline="") as handle:
        a1_reference_indices = tuple(
            int(row["full_length_zero_based_index"]) for row in csv.DictReader(handle)
        )
    if next(mask for mask in masks if mask.cutoff == 8.0).reference_indices != a1_reference_indices:
        raise ValueError("Extracted 8 A mask differs from the committed A1 mapping")
    return tuple(masks)


def build_scenario_specs(
    panel: PreparedPanel, masks: tuple[InterfaceMask, ...]
) -> tuple[ScenarioSpec, ...]:
    """Enumerate the full predeclared target x cutoff x policy x trace grid."""
    scenarios: list[ScenarioSpec] = []
    for target in panel.targets:
        canonical_first_hash = target.alignment.trace_sha256
        for policy in ALIGNMENT_POLICIES:
            alignments = enumerate_reference_to_target_alignments(
                panel.reference_sequence.sequence,
                target.sequence.sequence,
                policy,
            )
            expected = EXPECTED_OPTIMAL_COUNTS[target.contract.accession][policy.policy_id]
            if len(alignments) != expected:
                raise ValueError(
                    f"{target.contract.accession}/{policy.policy_id}: optimal count changed"
                )
            if policy.policy_id == "canonical_free_terminal" and (
                alignments[0].trace_sha256 != canonical_first_hash
            ):
                raise ValueError("Canonical first alignment differs from A1")
            for mask in masks:
                for alignment in alignments:
                    scenarios.append(
                        ScenarioSpec(
                            target=target,
                            mask=mask,
                            policy=policy,
                            alignment=alignment,
                        )
                    )

    counts = {
        target.accession: sum(
            scenario.target.contract.accession == target.accession for scenario in scenarios
        )
        for target in TARGETS
    }
    if counts != EXPECTED_SCENARIO_COUNTS or len(scenarios) != EXPECTED_TOTAL_SCENARIOS:
        raise ValueError("A2 Cartesian scenario count changed")
    return tuple(scenarios)


def prepare_audit(
    *,
    repo_root: Path,
    pdb_path: Path,
    reference_sequence_root: Path,
    binding_root: Path,
) -> A2Audit:
    """Validate every A2 input and enumerate all scenarios without metrics."""
    panel = prepare_panel(
        repo_root=repo_root,
        reference_sequence_root=reference_sequence_root,
        binding_root=binding_root,
    )
    a1_rows = load_a1_rows(repo_root)
    full_mapping_rows = build_full_chain_mapping_rows(
        pdb_path=pdb_path,
        q00987_sequence=panel.reference_sequence.sequence,
    )
    masks = build_interface_masks(
        repo_root=repo_root,
        pdb_path=pdb_path,
        full_mapping_rows=full_mapping_rows,
    )
    scenarios = build_scenario_specs(panel, masks)
    return A2Audit(
        panel=panel,
        full_mapping_rows=tuple(full_mapping_rows),
        masks=masks,
        scenarios=scenarios,
        a1_rows_by_accession=a1_rows,
    )


def _direction(value: float) -> str:
    if value < 1.0:
        return "below_one"
    if value > 1.0:
        return "above_one"
    return "equal_one"


def _baseline_matches_a1(metrics: MappedInterfaceMetrics, a1_row: dict[str, str]) -> bool:
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
    return all(a1_row[field] == value for field, value in observed.items())


def build_scenario_rows(
    audit: A2Audit,
    *,
    full_mapping_sha256: str,
) -> list[dict[str, str]]:
    """Compute all 485 explicit-trace A2 scenarios."""
    rows: list[dict[str, str]] = []
    for scenario in audit.scenarios:
        target = scenario.target
        alignment = scenario.alignment
        source_indices = scenario.mask.reference_indices
        by_reference = {pair.reference_index: pair for pair in alignment.aligned_pairs}
        dropped = tuple(index for index in source_indices if index not in by_reference)
        if dropped:
            raise ValueError("An A2 scenario dropped source interface residues")
        metrics = compute_mapped_interface_metrics(
            reference=audit.panel.reference_embedding.embedding,
            target=target.embedding.embedding,
            interface_reference_indices=source_indices,
            alignment=alignment,
            shuffle_seed=SHUFFLE_SEED,
            shuffle_control_count=SHUFFLE_CONTROL_COUNT,
        )
        finite = (
            metrics.interface_mean_delta,
            metrics.noninterface_mean_delta,
            metrics.enrichment_ratio,
            metrics.effect_size_cohens_d,
            metrics.shuffle_empirical_p_less,
        )
        if not all(math.isfinite(value) for value in finite):
            raise ValueError("A2 scenario produced a non-finite metric")
        is_baseline = (
            scenario.mask.cutoff == 8.0
            and scenario.policy.policy_id == "canonical_free_terminal"
            and alignment.optimal_alignment_index == 0
        )
        baseline_reproduced = (
            _baseline_matches_a1(
                metrics,
                audit.a1_rows_by_accession[target.contract.accession],
            )
            if is_baseline
            else False
        )
        if is_baseline and not baseline_reproduced:
            raise ValueError(f"{target.contract.accession}: A1 baseline was not reproduced")

        rows.append(
            {
                "result_contract_version": "1",
                "scenario_id": (
                    f"{target.contract.accession.lower()}_cutoff_{scenario.mask.cutoff:.1f}_"
                    f"{scenario.policy.policy_id}_trace_{alignment.optimal_alignment_index}"
                ),
                "target_species": target.contract.species,
                "target_accession": target.contract.accession,
                "lifespan_category": target.contract.lifespan_category,
                "pdb_id": "1YCR",
                "pdb_sha256": EXPECTED_PDB_SHA256,
                "full_chain_mapping_table": DEFAULT_FULL_MAPPING_TABLE.as_posix(),
                "full_chain_mapping_sha256": full_mapping_sha256,
                "a1_result_table": A1_RESULT_TABLE.as_posix(),
                "a1_result_sha256": EXPECTED_A1_RESULT_SHA256,
                "interface_distance_cutoff_angstrom": f"{scenario.mask.cutoff:.1f}",
                "source_interface_count": str(len(source_indices)),
                "source_interface_reference_zero_based_indices": _indices_text(source_indices),
                "alignment_policy_id": scenario.policy.policy_id,
                "alignment_gap_open": str(scenario.policy.gap_open),
                "alignment_gap_extend": str(scenario.policy.gap_extend),
                "alignment_terminal_penalty": str(scenario.policy.terminal_penalty).lower(),
                "alignment_optimal_index": str(alignment.optimal_alignment_index),
                "alignment_optimal_count": str(alignment.optimal_alignment_count),
                "alignment_trace_sha256": alignment.trace_sha256,
                "alignment_trace_length": str(alignment.trace_length),
                "aligned_residue_count": str(metrics.aligned_residue_count),
                "mapped_interface_count": str(metrics.mapped_interface_count),
                "dropped_interface_count": "0",
                "dropped_reference_zero_based_indices": "none",
                "mapping_status": "complete_all_source_interface_residues_aligned",
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
                "direction_vs_one": _direction(metrics.enrichment_ratio),
                "lower_tail_significant_at_0_05": str(
                    metrics.shuffle_empirical_p_less <= 0.05
                ).lower(),
                "is_a1_baseline_scenario": str(is_baseline).lower(),
                "a1_baseline_reproduced": str(baseline_reproduced).lower(),
                "mapping_cutoff_alignment_sensitivity_run": "true",
                "gate8_disposition_run": "false",
                "gate9_promoted": "false",
                "biological_claim_made": "false",
                "result_date": RESULT_DATE,
            }
        )

    validate_scenario_rows(rows)
    return rows


def validate_scenario_rows(rows: list[dict[str, str]]) -> None:
    """Validate row count, provenance, numerical bounds, and claim boundaries."""
    if len(rows) != EXPECTED_TOTAL_SCENARIOS:
        raise ValueError("Expected exactly 485 A2 scenario rows")
    if len({row.get("scenario_id") for row in rows}) != len(rows):
        raise ValueError("A2 scenario identifiers are not unique")
    counts = {
        accession: sum(row.get("target_accession") == accession for row in rows)
        for accession in EXPECTED_SCENARIO_COUNTS
    }
    if counts != EXPECTED_SCENARIO_COUNTS:
        raise ValueError("A2 target scenario counts changed")
    for row in rows:
        if tuple(row) != SCENARIO_FIELDS:
            raise ValueError("A2 scenario fields or field order changed")
        if row["mapping_status"] != "complete_all_source_interface_residues_aligned":
            raise ValueError("A2 scenario mapping is incomplete")
        if row["dropped_interface_count"] != "0":
            raise ValueError("A2 scenario records a dropped interface residue")
        if row["mapping_cutoff_alignment_sensitivity_run"] != "true":
            raise ValueError("A2 scenario is not marked as run")
        for field in ("gate8_disposition_run", "gate9_promoted", "biological_claim_made"):
            if row[field] != "false":
                raise ValueError(f"Forbidden A2 boundary changed: {field}")
        for field in (
            "enrichment_ratio",
            "effect_size_cohens_d",
            "p_interface_greater",
            "p_interface_less",
            "p_two_sided",
            "shuffle_empirical_p_greater",
            "shuffle_empirical_p_less",
            "shuffle_empirical_p_two_sided",
        ):
            if not math.isfinite(float(row[field])):
                raise ValueError(f"Non-finite A2 field: {field}")
        for field in (
            "p_interface_greater",
            "p_interface_less",
            "p_two_sided",
            "shuffle_empirical_p_greater",
            "shuffle_empirical_p_less",
            "shuffle_empirical_p_two_sided",
        ):
            if not 0.0 <= float(row[field]) <= 1.0:
                raise ValueError(f"Out-of-range probability: {field}")
    baselines = [row for row in rows if row["is_a1_baseline_scenario"] == "true"]
    if len(baselines) != 3 or any(row["a1_baseline_reproduced"] != "true" for row in baselines):
        raise ValueError("Expected three exactly reproduced A1 baselines")


def build_summary_rows(
    scenario_rows: list[dict[str, str]],
    a1_rows_by_accession: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    """Summarize sensitivity and choose the conditional, fail-closed next action."""
    summaries: list[dict[str, str]] = []
    for contract in TARGETS:
        target_rows = [
            row for row in scenario_rows if row["target_accession"] == contract.accession
        ]
        ratios = [float(row["enrichment_ratio"]) for row in target_rows]
        effect_sizes = [float(row["effect_size_cohens_d"]) for row in target_rows]
        baseline_direction = _direction(
            float(a1_rows_by_accession[contract.accession]["enrichment_ratio"])
        )
        direction_flip_count = sum(
            row["direction_vs_one"] != baseline_direction for row in target_rows
        )
        significant_count = sum(
            row["lower_tail_significant_at_0_05"] == "true" for row in target_rows
        )
        mapping_complete_count = sum(
            row["mapping_status"] == "complete_all_source_interface_residues_aligned"
            for row in target_rows
        )
        baseline_reproduced = any(
            row["is_a1_baseline_scenario"] == "true" and row["a1_baseline_reproduced"] == "true"
            for row in target_rows
        )
        stable = (
            direction_flip_count == 0
            and significant_count == len(target_rows)
            and mapping_complete_count == len(target_rows)
            and baseline_reproduced
        )
        next_action = (
            "run_leave_one_control_out_and_residue_block_jackknife"
            if stable
            else "resolve_mapping_cutoff_alignment_sensitivity"
        )
        summaries.append(
            {
                "summary_contract_version": "1",
                "target_species": contract.species,
                "target_accession": contract.accession,
                "lifespan_category": contract.lifespan_category,
                "scenario_count": str(len(target_rows)),
                "expected_scenario_count": str(EXPECTED_SCENARIO_COUNTS[contract.accession]),
                "cutoff_count": str(
                    len({row["interface_distance_cutoff_angstrom"] for row in target_rows})
                ),
                "alignment_policy_count": str(
                    len({row["alignment_policy_id"] for row in target_rows})
                ),
                "unique_alignment_trace_count": str(
                    len({row["alignment_trace_sha256"] for row in target_rows})
                ),
                "baseline_enrichment_ratio": a1_rows_by_accession[contract.accession][
                    "enrichment_ratio"
                ],
                "minimum_enrichment_ratio": _float_text(min(ratios)),
                "median_enrichment_ratio": _float_text(median(ratios)),
                "maximum_enrichment_ratio": _float_text(max(ratios)),
                "minimum_effect_size_cohens_d": _float_text(min(effect_sizes)),
                "maximum_effect_size_cohens_d": _float_text(max(effect_sizes)),
                "ratio_below_one_count": str(sum(value < 1.0 for value in ratios)),
                "ratio_equal_one_count": str(sum(value == 1.0 for value in ratios)),
                "ratio_above_one_count": str(sum(value > 1.0 for value in ratios)),
                "direction_flip_count_vs_a1": str(direction_flip_count),
                "lower_tail_significant_count_at_0_05": str(significant_count),
                "mapping_complete_scenario_count": str(mapping_complete_count),
                "a1_baseline_reproduced": str(baseline_reproduced).lower(),
                "predeclared_stability_criteria": STABILITY_CRITERIA,
                "sensitivity_status": (
                    "stable_under_predeclared_a2_grid" if stable else "sensitive_or_incomplete"
                ),
                "mapping_cutoff_alignment_sensitivity_run": "true",
                "leave_one_control_out_run": "false",
                "residue_block_jackknife_run": "false",
                "single_long_lived_lineage_limitation": "true",
                "gate8_disposition_run": "false",
                "gate8_promoted": "false",
                "gate9_promoted": "false",
                "biological_claim_made": "false",
                "allowed_next_action": next_action,
                "claim_status": "technical_a2_sensitivity_result_no_gate8_disposition",
                "result_date": RESULT_DATE,
            }
        )
    return summaries


def validate_full_mapping_rows(rows: list[dict[str, str]]) -> None:
    """Validate the committed 85-row 1YCR:A-to-Q00987 mapping."""
    if len(rows) != 85:
        raise ValueError("Expected exactly 85 full-chain mapping rows")
    if any(tuple(row) != FULL_MAPPING_FIELDS for row in rows):
        raise ValueError("Full-chain mapping fields or field order changed")

    chain_indices = [int(row["chain_local_zero_based_index"]) for row in rows]
    pdb_numbers = [int(row["pdb_residue_number"]) for row in rows]
    reference_indices = [int(row["direct_full_length_zero_based_index"]) for row in rows]
    if chain_indices != list(range(85)):
        raise ValueError("Full-chain mapping indices must be 0..84")
    if pdb_numbers != list(range(25, 110)):
        raise ValueError("Full-chain PDB residue numbers must be 25..109")
    if reference_indices != list(range(24, 109)):
        raise ValueError("Full-chain Q00987 indices must be 24..108")

    for row in rows:
        if row["pdb_sha256"] != EXPECTED_PDB_SHA256:
            raise ValueError("Full-chain mapping PDB SHA-256 changed")
        if row["q00987_sequence_sha256"] != REFERENCE_CONTRACT.sequence_sha256:
            raise ValueError("Full-chain mapping Q00987 SHA-256 changed")
        if row["direct_residue_identity_consistent"] != "true":
            raise ValueError("Full-chain direct residue identity is inconsistent")
        if row["sequence_mapping_agrees_with_direct"] != "true":
            raise ValueError("Full-chain sequence and DBREF mappings disagree")
        if (
            row["direct_full_length_zero_based_index"]
            != row["sequence_alignment_full_length_zero_based_index"]
        ):
            raise ValueError("Full-chain mapping coordinate methods disagree")


def validate_summary_rows(rows: list[dict[str, str]]) -> None:
    """Validate the committed stable A2 summary and its claim boundaries."""
    if [row.get("target_accession") for row in rows] != [target.accession for target in TARGETS]:
        raise ValueError("Expected elephant, mouse, hamster A2 summary order")

    for row, contract in zip(rows, TARGETS, strict=True):
        if tuple(row) != SUMMARY_FIELDS:
            raise ValueError("A2 summary fields or field order changed")
        scenario_count = EXPECTED_SCENARIO_COUNTS[contract.accession]
        required = {
            "summary_contract_version": "1",
            "target_species": contract.species,
            "target_accession": contract.accession,
            "lifespan_category": contract.lifespan_category,
            "scenario_count": str(scenario_count),
            "expected_scenario_count": str(scenario_count),
            "direction_flip_count_vs_a1": "0",
            "lower_tail_significant_count_at_0_05": str(scenario_count),
            "mapping_complete_scenario_count": str(scenario_count),
            "a1_baseline_reproduced": "true",
            "predeclared_stability_criteria": STABILITY_CRITERIA,
            "sensitivity_status": "stable_under_predeclared_a2_grid",
            "mapping_cutoff_alignment_sensitivity_run": "true",
            "leave_one_control_out_run": "false",
            "residue_block_jackknife_run": "false",
            "single_long_lived_lineage_limitation": "true",
            "gate8_disposition_run": "false",
            "gate8_promoted": "false",
            "gate9_promoted": "false",
            "biological_claim_made": "false",
            "allowed_next_action": ("run_leave_one_control_out_and_residue_block_jackknife"),
            "claim_status": "technical_a2_sensitivity_result_no_gate8_disposition",
            "result_date": RESULT_DATE,
        }
        for field, expected in required.items():
            if row[field] != expected:
                raise ValueError(
                    f"{contract.accession}: expected {field}={expected!r}, got {row[field]!r}"
                )

        minimum = float(row["minimum_enrichment_ratio"])
        midpoint = float(row["median_enrichment_ratio"])
        maximum = float(row["maximum_enrichment_ratio"])
        if not all(math.isfinite(value) for value in (minimum, midpoint, maximum)):
            raise ValueError("A2 summary enrichment range is non-finite")
        if not 0.0 < minimum <= midpoint <= maximum < 1.0:
            raise ValueError("A2 summary no longer preserves the below-one direction")
        if float(row["maximum_effect_size_cohens_d"]) >= 0.0:
            raise ValueError("A2 summary effect-size direction changed")
        if int(row["ratio_below_one_count"]) != scenario_count:
            raise ValueError("A2 summary below-one scenario count changed")
        if row["ratio_equal_one_count"] != "0" or row["ratio_above_one_count"] != "0":
            raise ValueError("A2 summary contains a direction boundary or flip")


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
    """Load and validate the three committed A2 tables without runtime artifacts."""
    mapping_path = root / DEFAULT_FULL_MAPPING_TABLE
    scenario_path = root / DEFAULT_SCENARIO_TABLE
    summary_path = root / DEFAULT_SUMMARY_TABLE
    _require_canonical_text_sha256(mapping_path, EXPECTED_FULL_MAPPING_SHA256)
    _require_canonical_text_sha256(scenario_path, EXPECTED_SCENARIO_RESULT_SHA256)
    _require_canonical_text_sha256(summary_path, EXPECTED_SUMMARY_RESULT_SHA256)

    mapping_rows = _read_csv_rows(mapping_path)
    scenario_rows = _read_csv_rows(scenario_path)
    summary_rows = _read_csv_rows(summary_path)
    validate_full_mapping_rows(mapping_rows)
    validate_scenario_rows(scenario_rows)
    validate_summary_rows(summary_rows)

    if {row["full_chain_mapping_sha256"] for row in scenario_rows} != {
        EXPECTED_FULL_MAPPING_SHA256
    }:
        raise ValueError("Scenario rows are not bound to the committed full mapping")
    if {row["a1_result_sha256"] for row in scenario_rows} != {EXPECTED_A1_RESULT_SHA256}:
        raise ValueError("Scenario rows are not bound to the committed A1 result")

    a1_rows = load_a1_rows(root)
    baseline_fields = (
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
    for accession, a1_row in a1_rows.items():
        baselines = [
            row
            for row in scenario_rows
            if row["target_accession"] == accession and row["is_a1_baseline_scenario"] == "true"
        ]
        if len(baselines) != 1:
            raise ValueError(f"{accession}: expected one A1 baseline scenario")
        if any(baselines[0][field] != a1_row[field] for field in baseline_fields):
            raise ValueError(f"{accession}: A1 baseline fields changed")

    if build_summary_rows(scenario_rows, a1_rows) != summary_rows:
        raise ValueError("Committed A2 summary does not reproduce from scenarios")
    return mapping_rows, scenario_rows, summary_rows


def _resolved_output(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


@app.command()
def main(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    pdb_path: Annotated[
        Path | None,
        typer.Option(help=f"Exact local 1YCR PDB; defaults to {PDB_PATH_ENV}."),
    ] = None,
    reference_sequence_root: Annotated[
        Path | None,
        typer.Option(help="External exact Q00987/G3SX30 FASTA root."),
    ] = None,
    binding_root: Annotated[
        Path | None,
        typer.Option(help="External exact P23804/A0ABM2YB85 binding root."),
    ] = None,
    full_mapping_output: Annotated[
        Path,
        typer.Option(help="Audited full-chain coordinate mapping table."),
    ] = DEFAULT_FULL_MAPPING_TABLE,
    scenario_output: Annotated[
        Path,
        typer.Option(help="Long-form A2 scenario result table."),
    ] = DEFAULT_SCENARIO_TABLE,
    summary_output: Annotated[
        Path,
        typer.Option(help="Compact per-target A2 summary table."),
    ] = DEFAULT_SUMMARY_TABLE,
    yes_run: Annotated[
        bool,
        typer.Option("--yes-run", help="Compute and write all 485 local A2 scenarios."),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option("--overwrite", help="Replace all three outputs explicitly."),
    ] = False,
) -> None:
    """Validate A2 inputs or explicitly run the complete local sensitivity grid."""
    load_dotenv()
    resolved_repo_root = repo_root.resolve()
    try:
        resolved_pdb = _required_path(pdb_path, PDB_PATH_ENV, directory=False)
        resolved_reference_root = _required_path(
            reference_sequence_root,
            "MDM2_REFERENCE_SEQUENCE_ROOT",
            directory=True,
        )
        resolved_binding_root = _required_path(
            binding_root,
            "LONGEVITY_PORT_EXTERNAL_SEQUENCE_BINDING_ROOT",
            directory=True,
        )
        audit = prepare_audit(
            repo_root=resolved_repo_root,
            pdb_path=resolved_pdb,
            reference_sequence_root=resolved_reference_root,
            binding_root=resolved_binding_root,
        )
    except (OSError, ValueError) as exc:
        typer.echo(f"BLOCKED: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("A2 scoped MDM2 mapping/cutoff/alignment input audit: ready")
    typer.echo(f"1YCR sha256={EXPECTED_PDB_SHA256} full_chain_rows={len(audit.full_mapping_rows)}")
    typer.echo(
        f"cutoffs={'|'.join(f'{cutoff:.1f}' for cutoff in CUTOFFS_ANGSTROM)} "
        f"scenarios={len(audit.scenarios)}"
    )
    for contract in TARGETS:
        typer.echo(
            f"{contract.species}/{contract.accession}: "
            f"scenarios={EXPECTED_SCENARIO_COUNTS[contract.accession]}"
        )

    outputs = (
        _resolved_output(resolved_repo_root, full_mapping_output),
        _resolved_output(resolved_repo_root, scenario_output),
        _resolved_output(resolved_repo_root, summary_output),
    )
    if not yes_run:
        typer.echo("DRY RUN: no sensitivity metrics were computed and no file was written.")
    else:
        existing = [path for path in outputs if path.exists()]
        if existing and not overwrite:
            typer.echo(
                "BLOCKED: A2 output already exists; use --overwrite only after auditing all three.",
                err=True,
            )
            raise typer.Exit(code=1)
        mapping_rows = list(audit.full_mapping_rows)
        mapping_sha256 = _canonical_rows_sha256(FULL_MAPPING_FIELDS, mapping_rows)
        scenario_rows = build_scenario_rows(
            audit,
            full_mapping_sha256=mapping_sha256,
        )
        summary_rows = build_summary_rows(
            scenario_rows,
            audit.a1_rows_by_accession,
        )
        _write_csv(outputs[0], FULL_MAPPING_FIELDS, mapping_rows)
        _write_csv(outputs[1], SCENARIO_FIELDS, scenario_rows)
        _write_csv(outputs[2], SUMMARY_FIELDS, summary_rows)
        typer.echo(f"Wrote {len(mapping_rows)} full-chain mapping rows -> {outputs[0]}")
        typer.echo(f"Wrote {len(scenario_rows)} A2 scenario rows -> {outputs[1]}")
        typer.echo(f"Wrote {len(summary_rows)} A2 summary rows -> {outputs[2]}")

    typer.echo(f"biotite_version={version('biotite')}")
    typer.echo("No network, Biohub/ESMC, or structural-model calls were made.")
    typer.echo("No Gate 8 disposition or Gate 9 promotion was performed.")
    typer.echo("No biological claim was made.")


if __name__ == "__main__":
    app()
