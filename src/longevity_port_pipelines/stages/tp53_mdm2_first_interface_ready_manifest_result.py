"""Validate the first result-bearing TP53/MDM2 interface-ready manifest.

The module reads committed CSV rows only. It fixes the exact human reference
chains and interface extraction policy while keeping comparative elephant
interface scoring blocked until elephant TP53 ortholog provenance is resolved.
It performs no structure call, interface extraction, interface scoring, or
biological interpretation.
"""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path

DEFAULT_MANIFEST_TABLE = Path("data/input/tp53_mdm2_first_interface_ready_manifest_results.csv")
THREE_COMPARATOR_SUMMARY_TABLE = Path(
    "data/input/g3sx30_first_three_comparator_pairwise_embedding_control_summaries.csv"
)
HUMAN_REFERENCE_MANIFEST_TABLE = Path("data/input/tp53_mdm2_pilot_manifest.csv")
ELEPHANT_MDM2_MAPPING_TABLE = Path("data/input/reviewed_target_sequence_provenance.csv")
ELEPHANT_TP53_REPAIR_TABLE = Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")

EXPECTED_VALUES: dict[str, str] = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "manifest_id": "tp53_mdm2_first_interface_ready_manifest_result",
    "manifest_status": "first_tp53_mdm2_interface_ready_manifest_result_created",
    "manifest_scope": "human_reference_interface_extraction_ready_elephant_comparative_scoring_blocked",
    "source_three_comparator_summary_table": "data/input/g3sx30_first_three_comparator_pairwise_embedding_control_summaries.csv",
    "source_three_comparator_summary_row_index": "1",
    "source_three_comparator_required_next_step": "add_first_tp53_mdm2_interface_ready_manifest_result",
    "source_human_reference_manifest_table": "data/input/tp53_mdm2_pilot_manifest.csv",
    "source_human_tp53_row_index": "1",
    "source_human_mdm2_row_index": "2",
    "human_reference_structure_database": "RCSB_PDB",
    "human_reference_structure_id": "1YCR",
    "human_reference_structure_method_policy": "committed_experimental_structure_reference_only",
    "human_reference_model_policy": "model_1_only",
    "human_mdm2_candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "human_mdm2_chain_id": "A",
    "human_mdm2_uniprot": "Q00987",
    "human_tp53_candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
    "human_tp53_chain_id": "B",
    "human_tp53_uniprot": "P04637",
    "partner_context": "human_mdm2_chain_A_bound_to_human_tp53_chain_B_in_1YCR",
    "interface_residue_source_type": "inter_chain_heavy_atom_distance_from_human_reference_structure",
    "interface_residue_extractor_reference": "src/longevity_port_pipelines/stages/interface.py::extract_interface_residues",
    "interface_distance_cutoff_angstrom": "8.0",
    "interface_atom_policy": "amino_acid_inter_chain_heavy_atom_contacts",
    "interface_residue_indexing_policy": "zero_based_chain_local_residue_indices",
    "interface_residue_extraction_ready": "true",
    "interface_residues_extracted": "false",
    "interface_scoring_performed": "false",
    "structure_confidence_policy": "use_experimental_1YCR_coordinates_for_human_reference_only;do_not_use_predicted_confidence_metrics;treat_ortholog_mapping_confidence_as_separate_provenance;block_comparative_scoring_while_elephant_TP53_is_unresolved",
    "prediction_confidence_metrics_used": "false",
    "elephant_target_species": "Loxodonta africana",
    "elephant_target_taxid": "9785",
    "elephant_mdm2_candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
    "elephant_mdm2_target_accession": "G3SX30",
    "elephant_mdm2_target_database": "UniProtKB TrEMBL",
    "elephant_mdm2_sequence_length": "492",
    "elephant_mdm2_sequence_sha256": "e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
    "elephant_mdm2_mapping_source": "data/input/reviewed_target_sequence_provenance.csv#2",
    "elephant_mdm2_mapping_status": "reviewed_sequence_provenance",
    "elephant_tp53_candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
    "elephant_tp53_target_accession": "unresolved",
    "elephant_tp53_target_database": "unresolved",
    "elephant_tp53_mapping_source": "data/input/tp53_mdm2_ortholog_repair_decisions.csv#1",
    "elephant_tp53_mapping_status": "blocked_pending_source_ortholog_provenance",
    "elephant_pairwise_mapping_complete": "false",
    "comparative_elephant_interface_scoring_ready": "false",
    "blocking_reason": "elephant_tp53_target_accession_and_provenance_unresolved",
    "breakage_interpretation_policy": "do_not_auto_classify_breakage_as_incompatibility",
    "claim_policy": "technical_checkpoint_no_claim",
    "human_interface_extraction_manifest_ready": "true",
    "result_created": "true",
    "structure_call_performed": "false",
    "npy_artifact_read": "false",
    "npy_artifact_committed": "false",
    "data_output_artifact_committed": "false",
    "biohub_esmc_called": "false",
    "boltz_called": "false",
    "af3_called": "false",
    "chai_called": "false",
    "gate8_promoted": "false",
    "gate9_promoted": "false",
    "biological_claim_made": "false",
    "next_step": "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result",
    "result_date": "2026-07-14",
    "claim_note": "Result-bearing manifest bookkeeping only. Exact human chains, "
    "interface-residue source, partner context, reviewed elephant MDM2 "
    "mapping, unresolved elephant TP53 blocker, and structure-confidence "
    "policy are fixed before extraction. No interface residues are "
    "extracted, no interface score is computed, and no biological claim is "
    "made.",
}

FALSE_ONLY_FIELDS = (
    "interface_residues_extracted",
    "interface_scoring_performed",
    "prediction_confidence_metrics_used",
    "elephant_pairwise_mapping_complete",
    "comparative_elephant_interface_scoring_ready",
    "structure_call_performed",
    "npy_artifact_read",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "biohub_esmc_called",
    "boltz_called",
    "af3_called",
    "chai_called",
    "gate8_promoted",
    "gate9_promoted",
    "biological_claim_made",
)
TRUE_ONLY_FIELDS = (
    "interface_residue_extraction_ready",
    "human_interface_extraction_manifest_ready",
    "result_created",
)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _require_one_row(path: Path) -> dict[str, str]:
    rows = _read_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one committed row in {path}, got {len(rows)}")
    return rows[0]


def _find_one_row(path: Path, required: Mapping[str, str]) -> dict[str, str]:
    matches = [
        row
        for row in _read_rows(path)
        if all(row.get(field) == value for field, value in required.items())
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one source row in {path} matching {dict(required)!r}, got {len(matches)}"
        )
    return matches[0]


def _validate_source_rows() -> None:
    summary = _require_one_row(THREE_COMPARATOR_SUMMARY_TABLE)
    if summary.get("next_step") != "add_first_tp53_mdm2_interface_ready_manifest_result":
        raise ValueError(
            "Three-comparator summary does not require the interface-ready manifest result."
        )

    tp53 = _find_one_row(
        HUMAN_REFERENCE_MANIFEST_TABLE,
        {
            "candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
            "pdb_id": "1ycr",
            "chain": "B",
            "source_uniprot": "P04637",
            "partner_uniprot": "Q00987",
        },
    )
    mdm2 = _find_one_row(
        HUMAN_REFERENCE_MANIFEST_TABLE,
        {
            "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
            "pdb_id": "1ycr",
            "chain": "A",
            "source_uniprot": "Q00987",
            "partner_uniprot": "P04637",
        },
    )
    if tp53.get("claim_policy") != "technical_checkpoint_no_claim":
        raise ValueError("Human TP53 source row has an unexpected claim policy.")
    if mdm2.get("claim_policy") != "technical_checkpoint_no_claim":
        raise ValueError("Human MDM2 source row has an unexpected claim policy.")

    _find_one_row(
        ELEPHANT_MDM2_MAPPING_TABLE,
        {
            "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
            "target_accession": "G3SX30",
            "target_taxid": "9785",
            "gene_symbol": "MDM2",
            "reviewed_sequence_length": "492",
            "sequence_length_status": "matches",
            "sequence_review_status": "reviewed_sequence_provenance",
            "provenance_review_status": "reviewed",
        },
    )

    _find_one_row(
        ELEPHANT_TP53_REPAIR_TABLE,
        {
            "candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
            "gene_symbol": "TP53",
            "target_uniprot": "unresolved",
            "source_ortholog_status": "not_checked",
            "coverage_status": "unresolved_downstream_provenance",
            "repair_status": "pending",
        },
    )


def validate_interface_ready_manifest_row(row: Mapping[str, str]) -> None:
    missing = [field for field in EXPECTED_VALUES if field not in row]
    if missing:
        raise ValueError("Missing required interface-ready manifest fields: " + ", ".join(missing))

    unexpected = [field for field in row if field not in EXPECTED_VALUES]
    if unexpected:
        raise ValueError("Unexpected interface-ready manifest fields: " + ", ".join(unexpected))

    mismatches = [
        f"{field}={row.get(field)!r} expected {expected!r}"
        for field, expected in EXPECTED_VALUES.items()
        if row.get(field) != expected
    ]
    if mismatches:
        raise ValueError("Interface-ready manifest value mismatch: " + "; ".join(mismatches))

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"{field} must remain false")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"{field} must remain true")

    if row["human_mdm2_chain_id"] == row["human_tp53_chain_id"]:
        raise ValueError("Human MDM2 and TP53 chains must be distinct.")

    if row["elephant_tp53_target_accession"] != "unresolved":
        raise ValueError("This result must not invent an elephant TP53 accession.")

    if row["comparative_elephant_interface_scoring_ready"] != "false":
        raise ValueError("Comparative elephant interface scoring must remain blocked.")


def load_and_validate_interface_ready_manifest(
    path: Path = DEFAULT_MANIFEST_TABLE,
) -> dict[str, str]:
    _validate_source_rows()
    row = _require_one_row(path)
    validate_interface_ready_manifest_row(row)
    return row
