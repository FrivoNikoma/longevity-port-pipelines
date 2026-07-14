"""Validate the first human TP53/MDM2 interface-residue extraction result.

The module reads committed CSV rows only. It validates the exact geometric
contact masks extracted from experimental RCSB PDB 1YCR and keeps interface
scoring, shuffled controls, NEGATOME controls, elephant comparison, and
biological interpretation explicitly out of scope.
"""

from __future__ import annotations

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path

from longevity_port_pipelines.stages import (
    tp53_mdm2_first_interface_ready_manifest_result as manifest_source,
)

DEFAULT_SUMMARY_TABLE = Path(
    "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv"
)
DEFAULT_RESIDUE_TABLE = Path(
    "data/input/tp53_mdm2_first_human_reference_interface_residue_records.csv"
)

EXPECTED_SUMMARY_VALUES: dict[str, str] = {
    "candidate_set": "tp53_mdm2_elephant",
    "lane_name": "tp53_mdm2_elephant",
    "result_id": "tp53_mdm2_first_human_reference_interface_residue_extraction_result",
    "result_status": "first_tp53_mdm2_human_reference_interface_residue_extraction_result_created",
    "result_scope": "human_1YCR_interface_residue_lists_extracted_no_interface_score_no_biological_claim",
    "source_manifest_table": "data/input/tp53_mdm2_first_interface_ready_manifest_results.csv",
    "source_manifest_row_index": "1",
    "source_manifest_status": "first_tp53_mdm2_interface_ready_manifest_result_created",
    "source_manifest_required_next_step": "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result",
    "source_runtime_observation_type": "first_tp53_mdm2_human_reference_interface_residue_extraction",
    "source_runtime_observation_canonical_sha256": "43fcec2cfe5e04f3353578c192ab4975bfb75f5918b6419eb8b05d1aa749e3aa",
    "source_runtime_observation_committed": "false",
    "source_repository_base_sha": "3d657509beba4f68e0e7121ff82414e77b98c0dd",
    "structure_database": "RCSB_PDB",
    "structure_id": "1YCR",
    "structure_model": "1",
    "pdb_download_url": "https://files.rcsb.org/download/1YCR.pdb",
    "pdb_size_bytes": "95202",
    "pdb_sha256": "7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493",
    "pdb_file_committed": "false",
    "extractor_reference": "src/longevity_port_pipelines/stages/interface.py::extract_interface_residues",
    "extractor_repository_commit": "3d657509beba4f68e0e7121ff82414e77b98c0dd",
    "interface_method": "inter_chain_amino_acid_atom_distance",
    "interface_distance_cutoff_angstrom": "8.0",
    "interface_atom_policy": "amino_acid_inter_chain_coordinate_atom_contacts_in_downloaded_1YCR_pdb",
    "interface_residue_indexing_policy": "zero_based_chain_local_residue_indices",
    "mdm2_uniprot": "Q00987",
    "mdm2_chain_id": "A",
    "mdm2_chain_residue_count": "85",
    "mdm2_interface_residue_count": "47",
    "mdm2_non_interface_residue_count": "38",
    "mdm2_interface_fraction": "0.5529411764705883",
    "mdm2_interface_indices": "0|1|2|3|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|41|42|43|44|45|46|47|48|49|50|57|61|66|67|68|69|70|71|72|73|74|75|76|78|79|82|84",
    "mdm2_interface_pdb_residue_labels": "GLU25|THR26|LEU27|VAL28|TYR48|THR49|MET50|LYS51|GLU52|VAL53|LEU54|PHE55|TYR56|LEU57|GLY58|GLN59|TYR60|ILE61|MET62|THR63|LEU66|TYR67|ASP68|GLU69|LYS70|GLN71|GLN72|HIS73|ILE74|VAL75|LEU82|PHE86|PHE91|SER92|VAL93|LYS94|GLU95|HIS96|ARG97|LYS98|ILE99|TYR100|THR101|ILE103|TYR104|LEU107|VAL109",
    "mdm2_within_chain_shuffle_possible": "true",
    "tp53_uniprot": "P04637",
    "tp53_chain_id": "B",
    "tp53_chain_residue_count": "13",
    "tp53_interface_residue_count": "13",
    "tp53_non_interface_residue_count": "0",
    "tp53_interface_fraction": "1.0000000000000000",
    "tp53_interface_indices": "0|1|2|3|4|5|6|7|8|9|10|11|12",
    "tp53_interface_pdb_residue_labels": "GLU17|THR18|PHE19|SER20|ASP21|LEU22|TRP23|LYS24|LEU25|LEU26|PRO27|GLU28|ASN29",
    "tp53_within_chain_shuffle_possible": "false",
    "tp53_within_chain_shuffle_degenerate": "true",
    "tp53_shuffle_blocking_reason": "interface_mask_covers_all_13_observed_chain_B_residues",
    "required_shuffled_control_scope": "mdm2_chain_A_only_until_non_degenerate_tp53_background_is_defined",
    "residue_record_table": "data/input/tp53_mdm2_first_human_reference_interface_residue_records.csv",
    "residue_record_count": "60",
    "residue_records_complete": "true",
    "interface_residues_extracted": "true",
    "interface_score_computed": "false",
    "shuffled_interface_control_computed": "false",
    "curated_negatome_control_computed": "false",
    "elephant_tp53_mapping_resolved": "false",
    "comparative_elephant_interface_scoring_performed": "false",
    "rcsb_pdb_download_performed": "true",
    "predicted_structure_call_performed": "false",
    "committed_validation_requires_network": "false",
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
    "result_created": "true",
    "next_step": "add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result",
    "result_date": "2026-07-14",
    "claim_note": "Geometric interface-residue extraction from experimental human 1YCR "
    "only. The 8.0 angstrom mask is not a binding-hotspot map, not an "
    "interface score, not a shuffled or NEGATOME control, not an elephant "
    "comparison, and not a biological claim. TP53 chain B is fully covered, "
    "so a within-chain TP53 shuffle would be degenerate; the next control "
    "result is restricted to MDM2 chain A.",
}

EXPECTED_INTERFACE_RESIDUES: dict[str, tuple[tuple[int, str, int], ...]] = {
    "mdm2": (
        (0, "GLU", 25),
        (1, "THR", 26),
        (2, "LEU", 27),
        (3, "VAL", 28),
        (23, "TYR", 48),
        (24, "THR", 49),
        (25, "MET", 50),
        (26, "LYS", 51),
        (27, "GLU", 52),
        (28, "VAL", 53),
        (29, "LEU", 54),
        (30, "PHE", 55),
        (31, "TYR", 56),
        (32, "LEU", 57),
        (33, "GLY", 58),
        (34, "GLN", 59),
        (35, "TYR", 60),
        (36, "ILE", 61),
        (37, "MET", 62),
        (38, "THR", 63),
        (41, "LEU", 66),
        (42, "TYR", 67),
        (43, "ASP", 68),
        (44, "GLU", 69),
        (45, "LYS", 70),
        (46, "GLN", 71),
        (47, "GLN", 72),
        (48, "HIS", 73),
        (49, "ILE", 74),
        (50, "VAL", 75),
        (57, "LEU", 82),
        (61, "PHE", 86),
        (66, "PHE", 91),
        (67, "SER", 92),
        (68, "VAL", 93),
        (69, "LYS", 94),
        (70, "GLU", 95),
        (71, "HIS", 96),
        (72, "ARG", 97),
        (73, "LYS", 98),
        (74, "ILE", 99),
        (75, "TYR", 100),
        (76, "THR", 101),
        (78, "ILE", 103),
        (79, "TYR", 104),
        (82, "LEU", 107),
        (84, "VAL", 109),
    ),
    "tp53": (
        (0, "GLU", 17),
        (1, "THR", 18),
        (2, "PHE", 19),
        (3, "SER", 20),
        (4, "ASP", 21),
        (5, "LEU", 22),
        (6, "TRP", 23),
        (7, "LYS", 24),
        (8, "LEU", 25),
        (9, "LEU", 26),
        (10, "PRO", 27),
        (11, "GLU", 28),
        (12, "ASN", 29),
    ),
}

ROLE_METADATA: dict[str, dict[str, str]] = {
    "mdm2": {
        "uniprot": "Q00987",
        "chain_id": "A",
        "chain_residue_count": "85",
        "interface_residue_count": "47",
    },
    "tp53": {
        "uniprot": "P04637",
        "chain_id": "B",
        "chain_residue_count": "13",
        "interface_residue_count": "13",
    },
}

FALSE_ONLY_FIELDS = (
    "source_runtime_observation_committed",
    "pdb_file_committed",
    "tp53_within_chain_shuffle_possible",
    "interface_score_computed",
    "shuffled_interface_control_computed",
    "curated_negatome_control_computed",
    "elephant_tp53_mapping_resolved",
    "comparative_elephant_interface_scoring_performed",
    "predicted_structure_call_performed",
    "committed_validation_requires_network",
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
    "mdm2_within_chain_shuffle_possible",
    "tp53_within_chain_shuffle_degenerate",
    "residue_records_complete",
    "interface_residues_extracted",
    "rcsb_pdb_download_performed",
    "result_created",
)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one committed row in {path}, got {len(rows)}")
    return rows[0]


def _validate_source_manifest() -> dict[str, str]:
    row = manifest_source.load_and_validate_interface_ready_manifest()
    if row["manifest_status"] != "first_tp53_mdm2_interface_ready_manifest_result_created":
        raise ValueError("Source manifest has an unexpected status.")
    if (
        row["next_step"]
        != "add_first_tp53_mdm2_human_reference_interface_residue_extraction_result"
    ):
        raise ValueError("Source manifest does not require this extraction result.")
    if row["human_reference_structure_id"] != "1YCR":
        raise ValueError("Source manifest does not fix 1YCR.")
    if row["human_mdm2_chain_id"] != "A" or row["human_tp53_chain_id"] != "B":
        raise ValueError("Source manifest does not fix chains A/B.")
    return row


def _expected_residue_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    record_index = 1
    for role in ("mdm2", "tp53"):
        metadata = ROLE_METADATA[role]
        for chain_local_index, res_name, pdb_res_id in EXPECTED_INTERFACE_RESIDUES[role]:
            rows.append(
                {
                    "result_id": "tp53_mdm2_first_human_reference_interface_residue_extraction_result",
                    "record_index": str(record_index),
                    "protein_role": role,
                    "uniprot": metadata["uniprot"],
                    "chain_id": metadata["chain_id"],
                    "chain_residue_count": metadata["chain_residue_count"],
                    "interface_residue_count": metadata["interface_residue_count"],
                    "chain_local_index": str(chain_local_index),
                    "pdb_res_name": res_name,
                    "pdb_res_id": str(pdb_res_id),
                    "insertion_code": "",
                    "pdb_residue_label": f"{res_name}{pdb_res_id}",
                    "structure_id": "1YCR",
                    "structure_model": "1",
                    "distance_cutoff_angstrom": "8.0",
                    "source_pdb_sha256": "7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493",
                    "result_date": "2026-07-14",
                }
            )
            record_index += 1
    return rows


def validate_summary_row(row: Mapping[str, str]) -> None:
    missing = [field for field in EXPECTED_SUMMARY_VALUES if field not in row]
    if missing:
        raise ValueError("Missing extraction-result summary fields: " + ", ".join(missing))

    unexpected = [field for field in row if field not in EXPECTED_SUMMARY_VALUES]
    if unexpected:
        raise ValueError("Unexpected extraction-result summary fields: " + ", ".join(unexpected))

    mismatches = [
        f"{field}={row.get(field)!r} expected {expected!r}"
        for field, expected in EXPECTED_SUMMARY_VALUES.items()
        if row.get(field) != expected
    ]
    if mismatches:
        raise ValueError("Extraction-result summary value mismatch: " + "; ".join(mismatches))

    for field in FALSE_ONLY_FIELDS:
        if row[field] != "false":
            raise ValueError(f"{field} must remain false")

    for field in TRUE_ONLY_FIELDS:
        if row[field] != "true":
            raise ValueError(f"{field} must remain true")

    if int(row["mdm2_interface_residue_count"]) + int(
        row["mdm2_non_interface_residue_count"]
    ) != int(row["mdm2_chain_residue_count"]):
        raise ValueError("MDM2 interface and non-interface counts do not close.")

    if int(row["tp53_interface_residue_count"]) + int(
        row["tp53_non_interface_residue_count"]
    ) != int(row["tp53_chain_residue_count"]):
        raise ValueError("TP53 interface and non-interface counts do not close.")

    if row["tp53_non_interface_residue_count"] != "0":
        raise ValueError("Observed TP53 chain B must have zero non-interface residues.")

    if row["required_shuffled_control_scope"] != (
        "mdm2_chain_A_only_until_non_degenerate_tp53_background_is_defined"
    ):
        raise ValueError("The next shuffled control must remain MDM2-side only.")


def validate_residue_rows(rows: Sequence[Mapping[str, str]]) -> None:
    expected_rows = _expected_residue_rows()
    if len(rows) != len(expected_rows):
        raise ValueError(f"Expected {len(expected_rows)} interface-residue rows, got {len(rows)}")

    for index, (actual, expected) in enumerate(
        zip(rows, expected_rows, strict=True),
        start=1,
    ):
        if dict(actual) != expected:
            raise ValueError(
                f"Interface-residue row {index} mismatch: "
                f"actual={dict(actual)!r} expected={expected!r}"
            )


def validate_cross_table_contract(
    summary: Mapping[str, str],
    residue_rows: Sequence[Mapping[str, str]],
) -> None:
    by_role = {
        role: [row for row in residue_rows if row["protein_role"] == role]
        for role in ("mdm2", "tp53")
    }

    if len(residue_rows) != int(summary["residue_record_count"]):
        raise ValueError("Summary residue_record_count does not match the residue table.")

    for role in ("mdm2", "tp53"):
        rows = by_role[role]
        expected_count = int(summary[f"{role}_interface_residue_count"])
        if len(rows) != expected_count:
            raise ValueError(f"{role} residue count does not match the summary.")

        indices = "|".join(row["chain_local_index"] for row in rows)
        labels = "|".join(row["pdb_residue_label"] for row in rows)

        if indices != summary[f"{role}_interface_indices"]:
            raise ValueError(f"{role} serialized interface indices do not match.")
        if labels != summary[f"{role}_interface_pdb_residue_labels"]:
            raise ValueError(f"{role} serialized residue labels do not match.")

    tp53_indices = [int(row["chain_local_index"]) for row in by_role["tp53"]]
    if tp53_indices != list(range(int(summary["tp53_chain_residue_count"]))):
        raise ValueError("TP53 chain B is expected to be fully covered by the mask.")


def load_and_validate_human_reference_interface_residue_extraction_result(
    summary_path: Path = DEFAULT_SUMMARY_TABLE,
    residue_path: Path = DEFAULT_RESIDUE_TABLE,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    _validate_source_manifest()
    summary = require_single_row(summary_path)
    residue_rows = read_csv_rows(residue_path)
    validate_summary_row(summary)
    validate_residue_rows(residue_rows)
    validate_cross_table_contract(summary, residue_rows)
    return summary, residue_rows
