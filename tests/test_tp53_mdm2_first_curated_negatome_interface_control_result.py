from __future__ import annotations

import csv
from pathlib import Path

import yaml

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_curated_negatome_interface_control_result as result,
)

SCHEMA_PATH = Path(
    "data/config/tp53_mdm2_first_curated_negatome_interface_control_result_schema.yaml"
)
RESULT_PATH = Path("data/input/tp53_mdm2_first_curated_negatome_interface_control_results.csv")
MODULE_PATH = Path(
    "src/longevity_port_pipelines/stages/"
    "tp53_mdm2_first_curated_negatome_interface_control_result.py"
)


def test_schema_and_csv_header_match_exact_result_contract() -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))

    with RESULT_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert list(rows[0]) == schema["required_fields"]
    assert schema["allowed_result_statuses"] == [
        "curated_negatome_interface_control_computed",
        "curated_negatome_record_reviewed_no_computable_interface_control",
    ]


def test_result_loader_validates_reviewed_no_computable_outcome() -> None:
    row = result.load_and_validate_curated_negatome_interface_control_result()

    assert (
        row["result_status"] == "curated_negatome_record_reviewed_no_computable_interface_control"
    )
    assert row["curated_negative_record_found"] == "true"
    assert row["curated_negative_provenance_reviewed"] == "true"
    assert row["interface_control_metric_computed"] == "false"
    assert (
        row["no_computable_control_reason"]
        == "curated_record_does_not_define_residue_level_or_deterministic_sequence_context"
    )
    assert row["curated_negatome_control_computed"] == "false"
    assert row["curated_negatome_control_closed"] == "false"
    assert row["result_created"] == "true"


def test_curated_record_provenance_is_exact() -> None:
    row = result.load_and_validate_curated_negatome_interface_control_result()

    assert row["curated_negative_record_id"] == "doi:10.7554/eLife.11994#figure-10E"
    assert row["curated_negative_source"] == "Sulak_et_al_eLife_2016"
    assert row["curated_negative_source_doi"] == "10.7554/eLife.11994"
    assert row["curated_negative_source_figure"] == "Figure_10E"
    assert row["curated_negative_source_publication_date"] == "2016-09-19"
    assert row["negative_context_source_uniprot"] == "Q00987"
    assert row["negative_partner_name"] == "TP53RTG12"
    assert row["negative_partner_identifier"] == "ENSLAFG00000028299"
    assert row["negative_partner_species_taxid"] == "9785"
    assert (
        row["negative_context_evidence_type"]
        == "negative_co_immunoprecipitation_observation_with_positive_internal_control"
    )
    assert row["assay_positive_internal_control"] == "endogenous_human_TP53_co_immunoprecipitated"
    assert row["assay_negative_observation"] == "Myc_tagged_TP53RTG12_not_co_immunoprecipitated"
    assert row["reported_partner_side_anchor_residues"] == "F19|W23|L26"
    assert row["reported_partner_side_anchor_substitution"] == "W23G"
    assert row["partner_side_sequence_context_reported"] == "true"
    assert (
        row["curated_negative_record_metadata_sha256"]
        == "5c9b77284294997ad5067be4a6991a54892bf883f9d91c0e334004d9068089c0"
    )
    assert result.record_metadata_sha256() == row["curated_negative_record_metadata_sha256"]


def test_no_mdm2_side_context_means_no_surrogate_metric() -> None:
    row = result.load_and_validate_curated_negatome_interface_control_result()

    assert row["mdm2_side_negative_residue_mask_available"] == "false"
    assert row["residue_level_context_available"] == "false"
    assert row["deterministic_sequence_context_available"] == "false"
    assert row["deterministic_metric_definition"] == (
        "not_applicable_no_MDM2_side_negative_residue_context"
    )
    assert row["empirical_null_available"] == "false"
    assert row["prohibited_surrogate_metrics_used"] == "false"

    for field in (
        "real_interface_metric",
        "negative_context_metric",
        "real_minus_negative",
        "real_over_negative",
        "empirical_tail_count",
        "empirical_p_add_one",
    ):
        assert row[field] == "not_computed"


def test_existing_embedding_runtime_layer_remains_valid_but_unused() -> None:
    row = result.load_and_validate_curated_negatome_interface_control_result()

    assert row["existing_runtime_negatome_path_reused"] == "false"
    assert row["existing_runtime_negatome_path_not_reused_reason"] == (
        "requires_embed_sequence_npy_and_per_residue_embeddings"
    )
    assert row["existing_runtime_negatome_path_status"] == (
        "valid_for_embedding_based_negatome_control_ratio"
    )
    assert row["existing_repo_curated_negative_mapping_for_q00987_present"] == "false"
    assert row["embedding_control_ratio_computed"] == "false"
    assert row["new_embeddings_generated"] == "false"
    assert row["biohub_esmc_called"] == "false"
    assert row["npy_artifact_read"] == "false"
    assert row["npy_artifact_written"] == "false"
    assert row["data_output_artifact_committed"] == "false"


def test_result_preserves_all_claim_and_gate_boundaries() -> None:
    row = result.load_and_validate_curated_negatome_interface_control_result()

    for field in (
        "boltz_called",
        "af3_called",
        "chai_called",
        "gate8_promoted",
        "gate9_promoted",
        "binding_claim_made",
        "non_binding_claim_made",
        "binding_strength_claim_made",
        "functional_significance_claim_made",
        "biological_specificity_claim_made",
        "adaptation_claim_made",
        "elephant_compatibility_claim_made",
        "beneficial_breakage_claim_made",
        "longevity_evidence_claim_made",
        "biological_claim_made",
    ):
        assert row[field] == "false"

    assert row["next_step"] == "add_first_tp53_mdm2_control_closure_result"


def test_result_module_does_not_call_embedding_or_npy_runtime() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")

    for forbidden in (
        "embed_sequence(",
        "PerResidueEmbedding",
        "compute_negatome_control_ratio(",
        "np.load(",
        "np.save(",
        "import numpy",
        "from numpy",
    ):
        assert forbidden not in text
