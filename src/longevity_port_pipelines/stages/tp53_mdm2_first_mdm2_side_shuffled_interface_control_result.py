# Validate the first TP53/MDM2 MDM2-side shuffled-interface control.
#
# This result-specific module reads committed CSV rows, validates the source
# human 1YCR interface mask, and deterministically recomputes same-size MDM2
# chain-A mask compactness metrics. It is not a generic shuffle framework and
# does not read embeddings or make biological interpretations.

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_human_reference_interface_residue_extraction_result as extraction_source,
)

DEFAULT_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_first_mdm2_side_shuffled_interface_control_results.csv"
)

RNG_SEED = 42
N_PERMUTATIONS = 1000
CHAIN_LENGTH = 85
MASK_SIZE = 47

EXPECTED_VALUES: dict[str, str] = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "result_id": "tp53_mdm2_first_mdm2_side_shuffled_interface_control_result",
    "result_status": "first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created",
    "result_scope": "human_1YCR_mdm2_chain_A_same_size_deterministic_mask_compactness_control_only",
    "source_extraction_table": "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv",
    "source_extraction_row_index": "1",
    "source_extraction_status": "first_tp53_mdm2_human_reference_interface_residue_extraction_result_created",
    "source_extraction_required_next_step": "add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result",
    "source_residue_table": "data/input/tp53_mdm2_first_human_reference_interface_residue_records.csv",
    "source_residue_record_count": "60",
    "structure_id": "1YCR",
    "structure_model": "1",
    "mdm2_uniprot": "Q00987",
    "mdm2_chain_id": "A",
    "mdm2_chain_residue_count": "85",
    "true_interface_residue_count": "47",
    "true_interface_indices": "0|1|2|3|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|41|42|43|44|45|46|47|48|49|50|57|61|66|67|68|69|70|71|72|73|74|75|76|78|79|82|84",
    "tp53_within_chain_shuffle_degenerate": "true",
    "control_scope": "mdm2_chain_A_only_same_size_masks_within_observed_85_residue_chain",
    "control_method": "deterministic_uniform_without_replacement_same_size_chain_local_mask_sampling",
    "rng_library": "numpy",
    "rng_algorithm": "numpy.random.default_rng",
    "rng_seed": "42",
    "n_permutations": "1000",
    "sampling_without_replacement": "true",
    "control_mask_size": "47",
    "control_mask_sort_policy": "ascending_chain_local_indices",
    "control_mask_stream_sha256": "6ebc3aea77388a9929d945acdb1962fe8eed148feecac7326fcbeceefbe2015c",
    "unique_control_mask_count": "1000",
    "metric_family": "sequence_adjacency_contiguous_runs_and_longest_run",
    "true_adjacent_pair_count": "38",
    "shuffled_adjacent_pair_count_mean": "25.4239999999999995",
    "shuffled_adjacent_pair_count_std_population": "2.3315711441000468",
    "shuffled_adjacent_pair_count_min": "18",
    "shuffled_adjacent_pair_count_max": "33",
    "shuffled_adjacent_pair_count_ge_true_count": "0",
    "adjacent_pair_empirical_upper_p_add_one": "0.0009990009990010",
    "adjacent_pair_z_score": "5.3937878034831135",
    "true_contiguous_run_count": "9",
    "shuffled_contiguous_run_count_mean": "21.5760000000000005",
    "shuffled_contiguous_run_count_std_population": "2.3315711441000468",
    "shuffled_contiguous_run_count_min": "14",
    "shuffled_contiguous_run_count_max": "29",
    "shuffled_contiguous_run_count_le_true_count": "0",
    "contiguous_run_empirical_lower_p_add_one": "0.0009990009990010",
    "contiguous_run_z_score": "-5.3937878034831135",
    "true_longest_run_length": "16",
    "shuffled_longest_run_length_mean": "6.6260000000000003",
    "shuffled_longest_run_length_std_population": "1.8243146658402984",
    "shuffled_longest_run_length_min": "3",
    "shuffled_longest_run_length_max": "18",
    "shuffled_longest_run_length_ge_true_count": "1",
    "longest_run_empirical_upper_p_add_one": "0.0019980019980020",
    "longest_run_z_score": "5.1383679447000645",
    "real_mask_more_adjacent_than_all_controls": "true",
    "real_mask_fewer_runs_than_all_controls": "true",
    "shuffled_interface_control_computed": "true",
    "embedding_interface_score_computed": "false",
    "binding_score_computed": "false",
    "curated_negatome_control_computed": "false",
    "comparative_elephant_interface_scoring_performed": "false",
    "biohub_esmc_called": "false",
    "npy_artifact_read": "false",
    "npy_artifact_committed": "false",
    "data_output_artifact_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "result_created": "true",
    "next_step": "add_first_tp53_mdm2_curated_negatome_interface_control_result",
    "result_date": "2026-07-15",
    "claim_note": "Deterministic same-size mask compactness control for human 1YCR MDM2 chain A only. The numerical result describes sequence adjacency and run structure of the geometric contact mask relative to random same-size masks. It is not a binding score, not functional-significance evidence, not longevity evidence, not a curated NEGATOME control, and not a biological claim.",
}

FALSE_ONLY_FIELDS = (
    "embedding_interface_score_computed",
    "binding_score_computed",
    "curated_negatome_control_computed",
    "comparative_elephant_interface_scoring_performed",
    "biohub_esmc_called",
    "npy_artifact_read",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)

TRUE_ONLY_FIELDS = (
    "tp53_within_chain_shuffle_degenerate",
    "sampling_without_replacement",
    "real_mask_more_adjacent_than_all_controls",
    "real_mask_fewer_runs_than_all_controls",
    "shuffled_interface_control_computed",
    "result_created",
)


@dataclass(frozen=True)
class MaskCompactnessMetrics:
    adjacent_pair_count: int
    contiguous_run_count: int
    longest_run_length: int


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one shuffled-control row in {path}, got {len(rows)}")
    return rows[0]


def format_metric(value: float) -> str:
    return f"{value:.16f}"


def compute_mask_compactness_metrics(
    indices: Sequence[int],
) -> MaskCompactnessMetrics:
    ordered = sorted(int(index) for index in indices)
    if not ordered:
        raise ValueError("Mask must not be empty.")
    if len(ordered) != len(set(ordered)):
        raise ValueError("Mask indices must be unique.")

    adjacent_pairs = sum(
        right == left + 1 for left, right in zip(ordered, ordered[1:], strict=False)
    )
    contiguous_runs = len(ordered) - adjacent_pairs

    longest_run = 1
    current_run = 1
    for left, right in zip(ordered, ordered[1:], strict=False):
        if right == left + 1:
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 1

    return MaskCompactnessMetrics(
        adjacent_pair_count=adjacent_pairs,
        contiguous_run_count=contiguous_runs,
        longest_run_length=longest_run,
    )


def _source_mdm2_indices() -> list[int]:
    summary, residue_rows = (
        extraction_source.load_and_validate_human_reference_interface_residue_extraction_result()
    )

    if summary["next_step"] != ("add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result"):
        raise ValueError("Source extraction result does not require this control.")
    if summary["tp53_within_chain_shuffle_degenerate"] != "true":
        raise ValueError("TP53 chain-B shuffle must remain degenerate.")
    if summary["mdm2_chain_id"] != "A":
        raise ValueError("Source MDM2 chain must be A.")

    indices = [
        int(row["chain_local_index"]) for row in residue_rows if row["protein_role"] == "mdm2"
    ]
    if len(indices) != MASK_SIZE:
        raise ValueError(f"Expected {MASK_SIZE} source MDM2 indices, got {len(indices)}.")
    if indices != sorted(set(indices)):
        raise ValueError("Source MDM2 indices are not sorted and unique.")
    if min(indices) < 0 or max(indices) >= CHAIN_LENGTH:
        raise ValueError("Source MDM2 index is out of bounds.")
    return indices


def recompute_expected_values() -> dict[str, str]:
    true_indices = _source_mdm2_indices()
    true_metrics = compute_mask_compactness_metrics(true_indices)

    rng = np.random.default_rng(seed=RNG_SEED)
    masks: list[list[int]] = []
    adjacent_values: list[int] = []
    run_values: list[int] = []
    longest_values: list[int] = []

    for _ in range(N_PERMUTATIONS):
        mask = sorted(
            int(index)
            for index in rng.choice(
                CHAIN_LENGTH,
                size=MASK_SIZE,
                replace=False,
            )
        )
        masks.append(mask)
        metrics = compute_mask_compactness_metrics(mask)
        adjacent_values.append(metrics.adjacent_pair_count)
        run_values.append(metrics.contiguous_run_count)
        longest_values.append(metrics.longest_run_length)

    mask_stream = "\n".join("|".join(str(index) for index in mask) for mask in masks) + "\n"

    adjacent = np.asarray(adjacent_values, dtype=np.float64)
    runs = np.asarray(run_values, dtype=np.float64)
    longest = np.asarray(longest_values, dtype=np.float64)

    adjacent_mean = float(np.mean(adjacent))
    adjacent_std = float(np.std(adjacent, ddof=0))
    runs_mean = float(np.mean(runs))
    runs_std = float(np.std(runs, ddof=0))
    longest_mean = float(np.mean(longest))
    longest_std = float(np.std(longest, ddof=0))

    adjacent_ge = int(np.sum(adjacent >= true_metrics.adjacent_pair_count))
    runs_le = int(np.sum(runs <= true_metrics.contiguous_run_count))
    longest_ge = int(np.sum(longest >= true_metrics.longest_run_length))

    values = dict(EXPECTED_VALUES)
    values.update(
        {
            "true_interface_indices": "|".join(str(index) for index in true_indices),
            "control_mask_stream_sha256": hashlib.sha256(mask_stream.encode("utf-8")).hexdigest(),
            "unique_control_mask_count": str(len({tuple(mask) for mask in masks})),
            "true_adjacent_pair_count": str(true_metrics.adjacent_pair_count),
            "shuffled_adjacent_pair_count_mean": format_metric(adjacent_mean),
            "shuffled_adjacent_pair_count_std_population": format_metric(adjacent_std),
            "shuffled_adjacent_pair_count_min": str(int(np.min(adjacent))),
            "shuffled_adjacent_pair_count_max": str(int(np.max(adjacent))),
            "shuffled_adjacent_pair_count_ge_true_count": str(adjacent_ge),
            "adjacent_pair_empirical_upper_p_add_one": format_metric(
                (adjacent_ge + 1) / (N_PERMUTATIONS + 1)
            ),
            "adjacent_pair_z_score": format_metric(
                (true_metrics.adjacent_pair_count - adjacent_mean) / adjacent_std
            ),
            "true_contiguous_run_count": str(true_metrics.contiguous_run_count),
            "shuffled_contiguous_run_count_mean": format_metric(runs_mean),
            "shuffled_contiguous_run_count_std_population": format_metric(runs_std),
            "shuffled_contiguous_run_count_min": str(int(np.min(runs))),
            "shuffled_contiguous_run_count_max": str(int(np.max(runs))),
            "shuffled_contiguous_run_count_le_true_count": str(runs_le),
            "contiguous_run_empirical_lower_p_add_one": format_metric(
                (runs_le + 1) / (N_PERMUTATIONS + 1)
            ),
            "contiguous_run_z_score": format_metric(
                (true_metrics.contiguous_run_count - runs_mean) / runs_std
            ),
            "true_longest_run_length": str(true_metrics.longest_run_length),
            "shuffled_longest_run_length_mean": format_metric(longest_mean),
            "shuffled_longest_run_length_std_population": format_metric(longest_std),
            "shuffled_longest_run_length_min": str(int(np.min(longest))),
            "shuffled_longest_run_length_max": str(int(np.max(longest))),
            "shuffled_longest_run_length_ge_true_count": str(longest_ge),
            "longest_run_empirical_upper_p_add_one": format_metric(
                (longest_ge + 1) / (N_PERMUTATIONS + 1)
            ),
            "longest_run_z_score": format_metric(
                (true_metrics.longest_run_length - longest_mean) / longest_std
            ),
            "real_mask_more_adjacent_than_all_controls": ("true" if adjacent_ge == 0 else "false"),
            "real_mask_fewer_runs_than_all_controls": ("true" if runs_le == 0 else "false"),
        }
    )
    return values


def validate_result_row(row: Mapping[str, str]) -> None:
    missing = [field for field in EXPECTED_VALUES if field not in row]
    if missing:
        raise ValueError("Missing shuffled-control fields: " + ", ".join(missing))

    unexpected = [field for field in row if field not in EXPECTED_VALUES]
    if unexpected:
        raise ValueError("Unexpected shuffled-control fields: " + ", ".join(unexpected))

    mismatches = [
        f"{field}={row.get(field)!r} expected {expected!r}"
        for field, expected in EXPECTED_VALUES.items()
        if row.get(field) != expected
    ]
    if mismatches:
        raise ValueError("Shuffled-control value mismatch: " + "; ".join(mismatches))

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"{field} must remain false")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"{field} must remain true")


def validate_recomputed_contract(row: Mapping[str, str]) -> None:
    recomputed = recompute_expected_values()
    mismatches = [
        f"{field}={row.get(field)!r} recomputed {expected!r}"
        for field, expected in recomputed.items()
        if row.get(field) != expected
    ]
    if mismatches:
        raise ValueError("Recomputed shuffled-control mismatch: " + "; ".join(mismatches))


def load_and_validate_mdm2_side_shuffled_interface_control_result(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    row = require_single_row(path)
    validate_result_row(row)
    validate_recomputed_contract(row)
    return row
