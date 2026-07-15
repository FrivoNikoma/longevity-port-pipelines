# Validate the first TP53/MDM2 curated NEGATOME-style interface-control result.
#
# This result-specific module validates one peer-reviewed manual negative
# co-immunoprecipitation context without embeddings. The existing embedding-based
# NEGATOME runtime remains valid and is intentionally not reused here.
# No surrogate MDM2-side interface metric is invented when the curated record
# lacks a negative-complex structure or MDM2-side residue mask.

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping
from pathlib import Path

from longevity_port_pipelines.stages import (
    negatome_curation,
)
from longevity_port_pipelines.stages import (
    tp53_mdm2_first_mdm2_side_shuffled_interface_control_result as shuffled_source,
)

DEFAULT_RESULT_TABLE = Path(
    "data/input/tp53_mdm2_first_curated_negatome_interface_control_results.csv"
)

ALLOWED_RESULT_STATUSES = (
    "curated_negatome_interface_control_computed",
    "curated_negatome_record_reviewed_no_computable_interface_control",
)

EXPECTED_VALUES: dict[str, str] = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "result_id": "tp53_mdm2_first_curated_negatome_interface_control_result",
    "result_status": "curated_negatome_record_reviewed_no_computable_interface_control",
    "result_scope": "human_1YCR_MDM2_chain_A_manual_curated_noninteraction_context_review_no_embedding",
    "source_shuffled_control_table": "data/input/tp53_mdm2_first_mdm2_side_shuffled_interface_control_results.csv",
    "source_shuffled_control_row_index": "1",
    "source_shuffled_control_status": "first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created",
    "source_shuffled_control_required_next_step": "add_first_tp53_mdm2_curated_negatome_interface_control_result",
    "structure_id": "1YCR",
    "structure_model": "1",
    "mdm2_uniprot": "Q00987",
    "mdm2_chain_id": "A",
    "mdm2_chain_residue_count": "85",
    "true_interface_residue_count": "47",
    "curated_negative_record_found": "true",
    "curated_negative_record_class": "manual_literature_curated_negatome_style_noninteraction_observation",
    "curated_negative_record_id": "doi:10.7554/eLife.11994#figure-10E",
    "curated_negative_source": "Sulak_et_al_eLife_2016",
    "curated_negative_source_type": "peer_reviewed_primary_research_manual_curated_negatome_style",
    "curated_negative_source_version": "eLife_2016_5_e11994_published_2016-09-19",
    "curated_negative_source_doi": "10.7554/eLife.11994",
    "curated_negative_source_figure": "Figure_10E",
    "curated_negative_source_publication_date": "2016-09-19",
    "curated_negative_provenance_reviewed": "true",
    "curated_negative_review_date": "2026-07-15",
    "curated_negative_record_metadata_canonical": "doi:10.7554/eLife.11994|figure_10E|human_MDM2_Q00987|African_elephant_TP53RTG12_ENSLAFG00000028299|HEK-293|anti-MDM2_immunoprecipitation|TP53_positive_control_detected|TP53RTG12_not_detected|W23G_reported",
    "curated_negative_record_metadata_sha256": "5c9b77284294997ad5067be4a6991a54892bf883f9d91c0e334004d9068089c0",
    "negative_context_evidence_type": "negative_co_immunoprecipitation_observation_with_positive_internal_control",
    "negative_context_definition": "endogenous_human_MDM2_Q00987_immunoprecipitation_with_transiently_expressed_African_elephant_TP53RTG12_in_HEK293_cells",
    "negative_context_source_protein": "MDM2",
    "negative_context_source_uniprot": "Q00987",
    "negative_partner_name": "TP53RTG12",
    "negative_partner_identifier": "ENSLAFG00000028299",
    "negative_partner_identifier_database": "Ensembl_gene_identifier_reported_in_article_Table_1",
    "negative_partner_species": "Loxodonta_africana",
    "negative_partner_species_taxid": "9785",
    "assay_system": "HEK_293_cells_transient_TP53RTG12_myc_His_expression",
    "assay_method": "anti_MDM2_immunoprecipitation_followed_by_Western_blot",
    "assay_positive_internal_control": "endogenous_human_TP53_co_immunoprecipitated",
    "assay_negative_observation": "Myc_tagged_TP53RTG12_not_co_immunoprecipitated",
    "reported_partner_side_anchor_residues": "F19|W23|L26",
    "reported_partner_side_anchor_substitution": "W23G",
    "partner_side_sequence_context_reported": "true",
    "mdm2_side_negative_residue_mask_available": "false",
    "residue_level_context_available": "false",
    "deterministic_sequence_context_available": "false",
    "interface_control_metric_computed": "false",
    "deterministic_metric_definition": "not_applicable_no_MDM2_side_negative_residue_context",
    "real_interface_metric": "not_computed",
    "negative_context_metric": "not_computed",
    "real_minus_negative": "not_computed",
    "real_over_negative": "not_computed",
    "empirical_tail_count": "not_computed",
    "empirical_p_add_one": "not_computed",
    "empirical_null_available": "false",
    "no_computable_control_reason": "curated_record_does_not_define_residue_level_or_deterministic_sequence_context",
    "no_computable_control_reason_detail": "record_reports_partner_side_W23G_and_negative_coIP_but_no_negative_complex_structure_or_MDM2_side_residue_mask_for_the_existing_47_of_85_geometric_mask",
    "prohibited_surrogate_metrics_used": "false",
    "existing_repo_curated_negative_mapping_for_q00987_present": "false",
    "existing_repo_curated_negative_mapping_status": "Q00987_not_configured_in_CURATED_NEGATIVE_PARTNERS_at_source_main_05b6695",
    "existing_runtime_negatome_path_reused": "false",
    "existing_runtime_negatome_path_not_reused_reason": "requires_embed_sequence_npy_and_per_residue_embeddings",
    "existing_runtime_negatome_path_status": "valid_for_embedding_based_negatome_control_ratio",
    "embedding_control_ratio_computed": "false",
    "new_embeddings_generated": "false",
    "biohub_esmc_called": "false",
    "npy_artifact_read": "false",
    "npy_artifact_written": "false",
    "data_output_artifact_committed": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "binding_claim_made": "false",
    "non_binding_claim_made": "false",
    "binding_strength_claim_made": "false",
    "functional_significance_claim_made": "false",
    "biological_specificity_claim_made": "false",
    "adaptation_claim_made": "false",
    "elephant_compatibility_claim_made": "false",
    "beneficial_breakage_claim_made": "false",
    "longevity_evidence_claim_made": "false",
    "biological_claim_made": "false",
    "curated_negatome_control_computed": "false",
    "curated_negatome_control_closed": "false",
    "result_created": "true",
    "next_step": "add_first_tp53_mdm2_control_closure_result",
    "result_date": "2026-07-15",
    "claim_note": "Concrete review result for one peer-reviewed manual NEGATOME-style noninteraction "
    "observation. The record reports partner-side W23G context and a negative TP53RTG12 "
    "co-immunoprecipitation observation with an internal TP53 positive control, but it "
    "provides no negative-complex structure or MDM2-side residue mask that can be "
    "compared with the existing 47-of-85 geometric MDM2 mask without inventing a "
    "surrogate metric. This result does not establish binding, non-binding, binding "
    "strength, functional significance, biological specificity, adaptation, elephant "
    "compatibility, beneficial breakage, longevity evidence, or a biological claim.",
}

FALSE_ONLY_FIELDS = (
    "mdm2_side_negative_residue_mask_available",
    "residue_level_context_available",
    "deterministic_sequence_context_available",
    "interface_control_metric_computed",
    "empirical_null_available",
    "prohibited_surrogate_metrics_used",
    "existing_repo_curated_negative_mapping_for_q00987_present",
    "existing_runtime_negatome_path_reused",
    "embedding_control_ratio_computed",
    "new_embeddings_generated",
    "biohub_esmc_called",
    "npy_artifact_read",
    "npy_artifact_written",
    "data_output_artifact_committed",
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
    "curated_negatome_control_computed",
    "curated_negatome_control_closed",
)

TRUE_ONLY_FIELDS = (
    "curated_negative_record_found",
    "curated_negative_provenance_reviewed",
    "partner_side_sequence_context_reported",
    "result_created",
)

NOT_COMPUTED_FIELDS = (
    "real_interface_metric",
    "negative_context_metric",
    "real_minus_negative",
    "real_over_negative",
    "empirical_tail_count",
    "empirical_p_add_one",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(
            f"Expected exactly one curated NEGATOME result row in {path}, got {len(rows)}."
        )
    return rows[0]


def canonical_record_metadata() -> str:
    return (
        "doi:10.7554/eLife.11994|figure_10E|human_MDM2_Q00987|"
        "African_elephant_TP53RTG12_ENSLAFG00000028299|HEK-293|"
        "anti-MDM2_immunoprecipitation|TP53_positive_control_detected|"
        "TP53RTG12_not_detected|W23G_reported"
    )


def record_metadata_sha256() -> str:
    return hashlib.sha256(canonical_record_metadata().encode("utf-8")).hexdigest()


def validate_source_shuffled_control_result() -> dict[str, str]:
    source = shuffled_source.load_and_validate_mdm2_side_shuffled_interface_control_result()

    required = {
        "result_status": ("first_tp53_mdm2_mdm2_side_shuffled_interface_control_result_created"),
        "next_step": "add_first_tp53_mdm2_curated_negatome_interface_control_result",
        "structure_id": "1YCR",
        "structure_model": "1",
        "mdm2_uniprot": "Q00987",
        "mdm2_chain_id": "A",
        "mdm2_chain_residue_count": "85",
        "true_interface_residue_count": "47",
        "shuffled_interface_control_computed": "true",
        "curated_negatome_control_computed": "false",
    }

    for field, expected in required.items():
        actual = source.get(field)
        if actual != expected:
            raise ValueError(
                f"Source shuffled-control {field} expected {expected!r}, got {actual!r}."
            )

    return source


def validate_existing_runtime_layer() -> None:
    if "Q00987" in negatome_curation.CURATED_NEGATIVE_PARTNERS:
        raise ValueError(
            "Committed result expects Q00987 to remain absent from the existing "
            "CURATED_NEGATIVE_PARTNERS mapping at this source checkpoint."
        )


def validate_result_row(row: Mapping[str, str]) -> None:
    expected_fields = list(EXPECTED_VALUES)
    actual_fields = list(row)

    if actual_fields != expected_fields:
        raise ValueError(
            "Curated NEGATOME result header differs from the committed result contract."
        )

    if row.get("result_status") not in ALLOWED_RESULT_STATUSES:
        raise ValueError(f"Unsupported result_status: {row.get('result_status')!r}.")

    for field, expected in EXPECTED_VALUES.items():
        actual = row.get(field)
        if actual != expected:
            raise ValueError(
                f"Curated NEGATOME result {field} expected {expected!r}, got {actual!r}."
            )

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"Boundary field {field} must be false.")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"Result field {field} must be true.")

    for field in NOT_COMPUTED_FIELDS:
        if row[field] != "not_computed":
            raise ValueError(f"Metric field {field} must remain not_computed.")

    if row["deterministic_metric_definition"] != (
        "not_applicable_no_MDM2_side_negative_residue_context"
    ):
        raise ValueError("Unexpected deterministic metric sentinel.")

    if row["no_computable_control_reason"] != (
        "curated_record_does_not_define_residue_level_or_deterministic_sequence_context"
    ):
        raise ValueError("Unexpected no-computable-control reason.")

    if row["existing_runtime_negatome_path_not_reused_reason"] != (
        "requires_embed_sequence_npy_and_per_residue_embeddings"
    ):
        raise ValueError("Unexpected existing-runtime non-reuse reason.")

    if row["existing_runtime_negatome_path_status"] != (
        "valid_for_embedding_based_negatome_control_ratio"
    ):
        raise ValueError("Existing embedding-based NEGATOME runtime status changed.")

    if row["curated_negative_record_metadata_canonical"] != canonical_record_metadata():
        raise ValueError("Canonical curated-record metadata differs from the contract.")

    if row["curated_negative_record_metadata_sha256"] != record_metadata_sha256():
        raise ValueError("Curated-record metadata SHA256 differs from the recomputed digest.")


def load_and_validate_curated_negatome_interface_control_result(
    path: Path = DEFAULT_RESULT_TABLE,
) -> dict[str, str]:
    validate_source_shuffled_control_result()
    validate_existing_runtime_layer()
    row = require_single_row(path)
    validate_result_row(row)
    return row
