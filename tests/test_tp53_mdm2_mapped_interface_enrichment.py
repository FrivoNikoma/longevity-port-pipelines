"""Ground-truth and committed-result tests for scoped MDM2 enrichment."""

import copy
from pathlib import Path

import numpy as np
import pytest

from longevity_port_pipelines.stages.embed import PerResidueEmbedding
from longevity_port_pipelines.stages.reference_coordinate_mapping import (
    AlignedResiduePair,
    ReferenceTargetAlignment,
)
from longevity_port_pipelines.stages.tp53_mdm2_mapped_interface_enrichment import (
    compute_mapped_interface_metrics,
    load_and_validate_result,
    validate_result_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def _embedding(sequence: str, values: np.ndarray, taxid: int) -> PerResidueEmbedding:
    return PerResidueEmbedding(
        complex_id="synthetic",
        chain="mdm2",
        species_taxid=taxid,
        model_name="synthetic-model",
        sequence=sequence,
        embeddings=values.astype(np.float32),
    )


def test_mapped_interface_metrics_detect_known_interface_shift() -> None:
    sequence = "ACDEFGHIKLMN"
    reference_values = np.zeros((len(sequence), 3), dtype=np.float32)
    target_values = np.full((len(sequence), 3), 0.1, dtype=np.float32)
    target_values[:3] = 2.0

    result = compute_mapped_interface_metrics(
        reference=_embedding(sequence, reference_values, 9606),
        target=_embedding(sequence, target_values, 9785),
        interface_reference_indices=(0, 1, 2),
        shuffle_seed=9,
        shuffle_control_count=50,
    )

    assert result.aligned_residue_count == len(sequence)
    assert result.mapped_interface_count == 3
    assert result.noninterface_count == len(sequence) - 3
    assert result.interface_mean_delta > result.noninterface_mean_delta
    assert result.enrichment_ratio > 10.0
    assert result.p_interface_greater < 0.01
    assert result.shuffle_ratios.shape == (50,)
    assert result.shuffle_empirical_p_greater == 1 / 51


def test_mapped_interface_metrics_uses_only_aligned_interface_positions() -> None:
    reference_sequence = "ACDEFGHIK"
    target_sequence = "ACDFGHIK"
    reference_values = np.zeros((len(reference_sequence), 2), dtype=np.float32)
    target_values = np.ones((len(target_sequence), 2), dtype=np.float32)

    result = compute_mapped_interface_metrics(
        reference=_embedding(reference_sequence, reference_values, 9606),
        target=_embedding(target_sequence, target_values, 10090),
        interface_reference_indices=(0, 3, 4),
        shuffle_control_count=20,
    )

    assert result.aligned_residue_count == 8
    assert result.mapped_interface_count == 2
    assert result.noninterface_count == 6


def test_mapped_interface_metrics_uses_the_supplied_alignment_trace() -> None:
    sequence = "AAAA"
    reference_values = np.zeros((4, 1), dtype=np.float32)
    target_values = np.asarray([[10.0], [1.0], [1.0], [1.0]], dtype=np.float32)
    pairs = tuple(
        AlignedResiduePair(
            reference_index=index,
            target_index=target_index,
            reference_residue="A",
            target_residue="A",
        )
        for index, target_index in enumerate((1, 0, 2, 3))
    )
    explicit = ReferenceTargetAlignment(
        aligned_pairs=pairs,
        trace_length=4,
        optimal_alignment_count=1,
        trace=tuple((pair.reference_index, pair.target_index) for pair in pairs),
        trace_sha256="synthetic-explicit-trace",
    )

    result = compute_mapped_interface_metrics(
        reference=_embedding(sequence, reference_values, 9606),
        target=_embedding(sequence, target_values, 9785),
        interface_reference_indices=(0,),
        alignment=explicit,
        shuffle_control_count=20,
    )

    assert result.interface_mean_delta == 1.0
    assert result.noninterface_mean_delta == 4.0
    assert result.enrichment_ratio == 0.25


def test_committed_result_has_exact_three_row_panel() -> None:
    rows = load_and_validate_result(ROOT)

    assert [row["target_accession"] for row in rows] == [
        "G3SX30",
        "P23804",
        "A0ABM2YB85",
    ]
    assert [row["lifespan_category"] for row in rows] == [
        "long_lived",
        "short_lived",
        "short_lived",
    ]
    assert [row["aligned_residue_count"] for row in rows] == ["490", "483", "481"]
    assert [row["alignment_optimal_count"] for row in rows] == ["9", "8", "2"]


def test_committed_mapping_is_complete_but_records_target_substitutions() -> None:
    rows = load_and_validate_result(ROOT)

    assert {row["source_interface_residue_count"] for row in rows} == {"47"}
    assert {row["mapped_interface_count"] for row in rows} == {"47"}
    assert {row["dropped_interface_count"] for row in rows} == {"0"}
    assert {row["dropped_reference_zero_based_indices"] for row in rows} == {"none"}
    assert [row["mapped_interface_identity_count"] for row in rows] == ["43", "42", "42"]


def test_committed_primary_and_shuffled_results_are_exact() -> None:
    rows = load_and_validate_result(ROOT)
    expected_ratios = {
        "G3SX30": "0.59271069444374358",
        "P23804": "0.51464311118804662",
        "A0ABM2YB85": "0.59823664002011123",
    }

    for row in rows:
        assert row["enrichment_ratio"] == expected_ratios[row["target_accession"]]
        assert float(row["interface_mean_delta"]) < float(row["noninterface_mean_delta"])
        assert float(row["effect_size_cohens_d"]) < 0.0
        assert row["shuffle_seed"] == "42"
        assert row["shuffle_control_count"] == "1000"
        assert row["shuffle_valid_control_count"] == "1000"
        assert row["shuffle_ge_observed_count"] == "1000"
        assert row["shuffle_le_observed_count"] == "0"
        assert row["shuffle_empirical_p_less"] == "0.000999000999000999"


def test_committed_result_preserves_gate_and_claim_boundaries() -> None:
    rows = load_and_validate_result(ROOT)

    for row in rows:
        assert row["mapped_interface_enrichment_run"] == "true"
        assert row["single_long_lived_lineage_limitation"] == "true"
        assert row["negatome_metric_included"] == "false"
        assert (
            row["negatome_metric_compatibility_status"]
            == "not_applied_pending_separate_metric_compatibility_audit"
        )
        assert row["gate8_input_status"] == "created_pending_a2_a3_and_gate8_disposition"
        assert row["allowed_next_action"] == "run_mapping_cutoff_and_alignment_sensitivity"

        for field in (
            "gate8_contrast_run",
            "mapping_cutoff_alignment_sensitivity_run",
            "leave_one_control_out_run",
            "residue_block_jackknife_run",
            "gate8_disposition_run",
            "gate8_promoted",
            "gate9_promoted",
            "biological_claim_made",
        ):
            assert row[field] == "false"


def test_gate_promotion_mutation_is_rejected() -> None:
    rows = load_and_validate_result(ROOT)
    bad = copy.deepcopy(rows)
    bad[0]["gate8_promoted"] = "true"

    with pytest.raises(ValueError, match="gate8_promoted"):
        validate_result_rows(bad)


def test_mapping_count_mutation_is_rejected() -> None:
    rows = load_and_validate_result(ROOT)
    bad = copy.deepcopy(rows)
    bad[1]["mapped_interface_count"] = "46"

    with pytest.raises(ValueError, match="sum to 47"):
        validate_result_rows(bad)


def test_schema_and_docs_record_result_boundaries() -> None:
    schema = (
        ROOT / "data/config/tp53_mdm2_mdm2_mapped_interface_enrichment_result_schema.yaml"
    ).read_text(encoding="utf-8")
    documentation = (ROOT / "docs/tp53_mdm2_mdm2_mapped_interface_enrichment_result.md").read_text(
        encoding="utf-8"
    )

    assert "gate8_input_preparation_only" in schema
    assert "legacy_geometric_shuffled_result_reuse_forbidden: true" in schema
    assert "0.59271069444374358" in documentation
    assert "0.51464311118804662" in documentation
    assert "0.59823664002011123" in documentation
    assert "It is not a\nlong-lived-vs-short-lived contrast" in documentation
    assert "run_mapping_cutoff_and_alignment_sensitivity" in documentation
