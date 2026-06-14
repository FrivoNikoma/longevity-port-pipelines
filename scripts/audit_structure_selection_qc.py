from __future__ import annotations

import argparse
import statistics
from pathlib import Path
from typing import Any

import polars as pl
from Bio.Align import PairwiseAligner
from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

DEFAULT_SELECTION_SUMMARY = (
    "data/output/sirt6_mini_pilot_v2_structure_selections/"
    "sirt6_mini_pilot_candidate_selection_summary.csv"
)
DEFAULT_RESIDUE_DELTAS = "data/output/sirt6_mini_pilot_v2_residue_deltas_mapped.parquet"
DEFAULT_PDB_DIR = "data/interim/pdb"
DEFAULT_OUTPUT_CSV = "data/output/sirt6_mini_pilot_v2_structure_selection_qc.csv"
DEFAULT_OUTPUT_MD = "data/output/sirt6_mini_pilot_v2_structure_selection_qc.md"

ROLE_TO_STRUCTURE_CHAIN = {
    "8bot": {"receptor": "U", "ligand": "T"},
    "1h2k": {"receptor": "A", "ligand": "S"},
    "1nfi": {"receptor": "C", "ligand": "E"},
    "8bhy": {"receptor": "T", "ligand": "M"},
    "7s68": {"receptor": "A", "ligand": "B"},
    "4xhu": {"receptor": "C", "ligand": "D"},
    "8bhv": {"receptor": "j", "ligand": "R"},
    "8f86": {"receptor": "K", "ligand": "A"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit contrast-informed structure selections against local PDB/mmCIF structures."
        )
    )
    parser.add_argument(
        "--selection-summary",
        default=DEFAULT_SELECTION_SUMMARY,
        help="Structure candidate selection summary CSV.",
    )
    parser.add_argument(
        "--residue-deltas",
        default=DEFAULT_RESIDUE_DELTAS,
        help="Full residue-level delta parquet used for reference sequences.",
    )
    parser.add_argument(
        "--pdb-dir",
        default=DEFAULT_PDB_DIR,
        help="Directory containing local PDB/mmCIF files.",
    )
    parser.add_argument(
        "--output-csv",
        default=DEFAULT_OUTPUT_CSV,
        help="Output QC CSV path.",
    )
    parser.add_argument(
        "--output-md",
        default=DEFAULT_OUTPUT_MD,
        help="Output QC Markdown path.",
    )
    parser.add_argument(
        "--near-cutoff",
        type=float,
        default=5.0,
        help="Distance cutoff in Angstroms for direct contact-like proximity.",
    )
    parser.add_argument(
        "--interface-cutoff",
        type=float,
        default=8.0,
        help="Distance cutoff in Angstroms for interface-proximal support.",
    )
    return parser.parse_args()


def required_columns(frame: pl.DataFrame, columns: set[str], path: Path) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def partner_role(chain_role: str) -> str:
    if chain_role == "receptor":
        return "ligand"
    if chain_role == "ligand":
        return "receptor"
    raise ValueError(f"Unexpected chain role: {chain_role}")


def structure_chain_for_role(pdb_id: str, chain_role: str) -> str:
    return ROLE_TO_STRUCTURE_CHAIN.get(pdb_id, {}).get(chain_role, chain_role)


def partner_structure_chain(pdb_id: str, chain_role: str) -> str:
    return structure_chain_for_role(pdb_id, partner_role(chain_role))


def find_structure_file(pdb_dir: Path, pdb_id: str) -> Path:
    candidates = [
        pdb_dir / f"{pdb_id}.pdb",
        pdb_dir / f"{pdb_id}.cif",
        pdb_dir / f"{pdb_id.upper()}.pdb",
        pdb_dir / f"{pdb_id.upper()}.cif",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find structure file for {pdb_id} in {pdb_dir}")


def load_model(structure_path: Path) -> Any:
    suffix = structure_path.suffix.lower()
    if suffix == ".pdb":
        structure = PDBParser(QUIET=True).get_structure(structure_path.stem, structure_path)
    elif suffix == ".cif":
        structure = MMCIFParser(QUIET=True).get_structure(structure_path.stem, structure_path)
    else:
        raise ValueError(f"Unsupported structure format: {structure_path}")

    return next(structure.get_models())


def is_hydrogen_atom(atom: Any) -> bool:
    element = getattr(atom, "element", "") or ""
    if element.upper() == "H":
        return True
    return atom.get_name().upper().startswith("H")


def heavy_atoms_for_residue(residue: Any) -> list[Any]:
    return [atom for atom in residue.get_atoms() if not is_hydrogen_atom(atom)]


def chain_residue_map(model: Any, chain_id: str) -> dict[int, Any]:
    if chain_id not in model:
        return {}

    residues = {}
    for residue in model[chain_id].get_residues():
        hetero_flag, residue_number, _insertion_code = residue.id
        if hetero_flag == " " and is_aa(residue, standard=False):
            residues[int(residue_number)] = residue
    return residues


def chain_sequence_and_numbers(model: Any, chain_id: str) -> tuple[str, list[int]]:
    residue_map = chain_residue_map(model, chain_id)
    numbers = sorted(residue_map)
    sequence = "".join(
        seq1(residue_map[number].get_resname(), undef_code="X") for number in numbers
    )
    return sequence, numbers


def residue_atoms_by_number(model: Any, chain_id: str, residue_number: int) -> list[Any]:
    residues = chain_residue_map(model, chain_id)
    residue = residues.get(int(residue_number))
    if residue is None:
        return []
    return heavy_atoms_for_residue(residue)


def partner_atoms(model: Any, chain_id: str) -> list[Any]:
    if chain_id not in model:
        return []

    atoms = []
    for residue in model[chain_id].get_residues():
        if residue.id[0] == " " and is_aa(residue, standard=False):
            atoms.extend(heavy_atoms_for_residue(residue))
    return atoms


def min_atom_distance(atoms: list[Any], partners: list[Any]) -> float | None:
    if not atoms or not partners:
        return None

    best = float("inf")
    for atom in atoms:
        for partner in partners:
            distance = float(atom - partner)
            if distance < best:
                best = distance

    return best


def summarize_distances(
    distances: list[float], cutoff: float
) -> tuple[float | None, float | None, int, float]:
    if not distances:
        return None, None, 0, 0.0

    within = sum(distance <= cutoff for distance in distances)
    return (
        min(distances),
        statistics.median(distances),
        within,
        within / len(distances),
    )


def build_aligner() -> PairwiseAligner:
    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2.0
    aligner.mismatch_score = -1.0
    aligner.open_gap_score = -10.0
    aligner.extend_gap_score = -0.5
    return aligner


def alignment_index_map(reference_sequence: str, structure_sequence: str) -> dict[int, int]:
    if not reference_sequence or not structure_sequence:
        return {}

    alignments = build_aligner().align(reference_sequence, structure_sequence)
    if not alignments:
        return {}

    alignment = alignments[0]
    reference_blocks, structure_blocks = alignment.aligned

    mapping: dict[int, int] = {}
    for reference_block, structure_block in zip(reference_blocks, structure_blocks, strict=True):
        reference_start, reference_end = int(reference_block[0]), int(reference_block[1])
        structure_start, structure_end = int(structure_block[0]), int(structure_block[1])
        block_length = min(reference_end - reference_start, structure_end - structure_start)

        for offset in range(block_length):
            mapping[reference_start + offset] = structure_start + offset

    return mapping


def reference_sequence_for_group(
    residue_deltas: pl.DataFrame,
    complex_id: str,
    chain: str,
    target_species: str,
) -> tuple[str, list[int]]:
    group = (
        residue_deltas.filter(
            (pl.col("complex_id") == complex_id)
            & (pl.col("chain") == chain)
            & (pl.col("target_species") == target_species)
        )
        .sort("residue_number_1based")
        .select(["residue_number_1based", "residue_aa"])
    )

    if group.is_empty():
        return "", []

    positions = [int(value) for value in group["residue_number_1based"].to_list()]
    sequence = "".join(str(value) for value in group["residue_aa"].to_list())
    return sequence, positions


def remap_reference_residues(
    selected_reference_residues: list[int],
    reference_sequence: str,
    reference_positions: list[int],
    structure_sequence: str,
    structure_numbers: list[int],
) -> dict[int, int]:
    reference_position_to_index = {
        int(reference_position): index
        for index, reference_position in enumerate(reference_positions)
    }
    ref_index_to_structure_index = alignment_index_map(reference_sequence, structure_sequence)

    remapped: dict[int, int] = {}
    for reference_residue in selected_reference_residues:
        reference_index = reference_position_to_index.get(int(reference_residue))
        if reference_index is None:
            continue

        structure_index = ref_index_to_structure_index.get(reference_index)
        if structure_index is None:
            continue

        if 0 <= structure_index < len(structure_numbers):
            remapped[int(reference_residue)] = int(structure_numbers[structure_index])

    return remapped


def joined_residue_list(values: list[int]) -> str:
    return ";".join(str(value) for value in values)


def joined_float_pairs(values: list[tuple[int, float]]) -> str:
    return ";".join(f"{residue}:{distance:.3f}" for residue, distance in values)


def joined_mapping(values: dict[int, int]) -> str:
    return ";".join(f"{reference}:{structure}" for reference, structure in sorted(values.items()))


def qc_status(
    exact_fraction_found: float,
    exact_fraction_within_interface: float,
    remapped_fraction_found: float,
    remapped_fraction_within_interface: float,
) -> str:
    if remapped_fraction_found >= 0.8 and remapped_fraction_within_interface >= 0.7:
        return "remapped_interface_supported"

    if remapped_fraction_found >= 0.8 and remapped_fraction_within_interface >= 0.3:
        return "remapped_partial_interface_support"

    if exact_fraction_found >= 0.7 and exact_fraction_within_interface >= 0.3:
        return "exact_partial_interface_support"

    if remapped_fraction_found >= 0.5:
        return "remapped_numbering_available_but_not_interface_proximal"

    return "numbering_or_interface_qc_failed"


def group_selection_summary(selection_summary: pl.DataFrame) -> pl.DataFrame:
    required = {
        "candidate_type",
        "complex_id",
        "pdb_id",
        "chain",
        "structure_chain",
        "target_species",
        "source_uniprot",
        "target_uniprot",
        "reference_sequence_residue_number",
        "residue_aa",
        "delta",
        "candidate_rank",
    }
    missing = required - set(selection_summary.columns)
    if missing:
        raise ValueError(f"Selection summary is missing required columns: {sorted(missing)}")

    group_columns = [
        "candidate_type",
        "complex_id",
        "pdb_id",
        "chain",
        "structure_chain",
        "target_species",
        "source_uniprot",
        "target_uniprot",
    ]

    for optional in [
        "partner_structure_chain",
        "short_lived_species",
        "contrast_class",
        "contrast_priority",
        "long_enrichment_ratio",
        "short_enrichment_ratio",
        "enrichment_delta",
        "enrichment_log2_ratio",
        "long_effect_size",
        "short_effect_size",
        "effect_size_delta",
    ]:
        if optional in selection_summary.columns:
            group_columns.append(optional)

    return (
        selection_summary.sort(
            [
                "candidate_type",
                "pdb_id",
                "chain",
                "target_species",
                "candidate_rank",
            ]
        )
        .group_by(group_columns, maintain_order=True)
        .agg(
            [
                pl.col("reference_sequence_residue_number").alias("selected_reference_residues"),
                pl.col("residue_aa").alias("selected_residue_aas"),
                pl.col("delta").alias("selected_deltas"),
            ]
        )
    )


def audit_group(
    row: dict[str, Any],
    residue_deltas: pl.DataFrame,
    pdb_dir: Path,
    near_cutoff: float,
    interface_cutoff: float,
) -> dict[str, Any]:
    pdb_id = str(row["pdb_id"])
    chain_role = str(row["chain"])
    structure_chain = str(row["structure_chain"])
    partner_chain = (
        str(row["partner_structure_chain"])
        if "partner_structure_chain" in row and row["partner_structure_chain"] is not None
        else partner_structure_chain(pdb_id, chain_role)
    )
    selected_reference_residues = [int(value) for value in row["selected_reference_residues"]]

    structure_path = find_structure_file(pdb_dir, pdb_id)
    model = load_model(structure_path)

    selected_chain_residues = chain_residue_map(model, structure_chain)
    selected_chain_numbers = sorted(selected_chain_residues)
    selected_partners = partner_atoms(model, partner_chain)

    exact_found = [
        residue for residue in selected_reference_residues if residue in selected_chain_residues
    ]
    exact_missing = [
        residue for residue in selected_reference_residues if residue not in selected_chain_residues
    ]

    exact_distances = []
    for residue in exact_found:
        atoms = residue_atoms_by_number(model, structure_chain, residue)
        distance = min_atom_distance(atoms, selected_partners)
        if distance is not None:
            exact_distances.append((residue, distance))

    reference_sequence, reference_positions = reference_sequence_for_group(
        residue_deltas=residue_deltas,
        complex_id=str(row["complex_id"]),
        chain=chain_role,
        target_species=str(row["target_species"]),
    )
    structure_sequence, structure_numbers = chain_sequence_and_numbers(model, structure_chain)

    remapped = remap_reference_residues(
        selected_reference_residues=selected_reference_residues,
        reference_sequence=reference_sequence,
        reference_positions=reference_positions,
        structure_sequence=structure_sequence,
        structure_numbers=structure_numbers,
    )
    remapped_missing = [
        residue for residue in selected_reference_residues if residue not in remapped
    ]

    remapped_distances = []
    for reference_residue, structure_residue in sorted(remapped.items()):
        atoms = residue_atoms_by_number(model, structure_chain, structure_residue)
        distance = min_atom_distance(atoms, selected_partners)
        if distance is not None:
            remapped_distances.append((reference_residue, distance))

    exact_distance_values = [distance for _, distance in exact_distances]
    remapped_distance_values = [distance for _, distance in remapped_distances]

    exact_min, exact_median, exact_within_near, exact_fraction_near = summarize_distances(
        exact_distance_values,
        near_cutoff,
    )
    _, _, exact_within_interface, exact_fraction_interface = summarize_distances(
        exact_distance_values,
        interface_cutoff,
    )
    remapped_min, remapped_median, remapped_within_near, remapped_fraction_near = (
        summarize_distances(
            remapped_distance_values,
            near_cutoff,
        )
    )
    _, _, remapped_within_interface, remapped_fraction_interface = summarize_distances(
        remapped_distance_values,
        interface_cutoff,
    )

    n_selected = len(selected_reference_residues)
    exact_fraction_found = len(exact_found) / n_selected if n_selected else 0.0
    remapped_fraction_found = len(remapped) / n_selected if n_selected else 0.0

    output = {
        "candidate_type": row["candidate_type"],
        "complex_id": row["complex_id"],
        "pdb_id": pdb_id,
        "chain": chain_role,
        "structure_chain": structure_chain,
        "partner_structure_chain": partner_chain,
        "target_species": row["target_species"],
        "source_uniprot": row["source_uniprot"],
        "target_uniprot": row["target_uniprot"],
        "structure_file": str(structure_path),
        "n_selected_residues": n_selected,
        "selected_reference_residues": joined_residue_list(selected_reference_residues),
        "structure_chain_residue_min": min(selected_chain_numbers)
        if selected_chain_numbers
        else None,
        "structure_chain_residue_max": max(selected_chain_numbers)
        if selected_chain_numbers
        else None,
        "exact_found_residues": joined_residue_list(exact_found),
        "exact_missing_residues": joined_residue_list(exact_missing),
        "exact_n_found": len(exact_found),
        "exact_fraction_found": exact_fraction_found,
        "exact_min_distance_to_partner": exact_min,
        "exact_median_distance_to_partner": exact_median,
        "exact_n_within_near_cutoff": exact_within_near,
        "exact_fraction_within_near_cutoff": exact_fraction_near,
        "exact_n_within_interface_cutoff": exact_within_interface,
        "exact_fraction_within_interface_cutoff": exact_fraction_interface,
        "exact_distance_by_reference_residue": joined_float_pairs(exact_distances),
        "remapped_reference_to_structure_residue": joined_mapping(remapped),
        "remapped_missing_reference_residues": joined_residue_list(remapped_missing),
        "remapped_n_found": len(remapped),
        "remapped_fraction_found": remapped_fraction_found,
        "remapped_min_distance_to_partner": remapped_min,
        "remapped_median_distance_to_partner": remapped_median,
        "remapped_n_within_near_cutoff": remapped_within_near,
        "remapped_fraction_within_near_cutoff": remapped_fraction_near,
        "remapped_n_within_interface_cutoff": remapped_within_interface,
        "remapped_fraction_within_interface_cutoff": remapped_fraction_interface,
        "remapped_distance_by_reference_residue": joined_float_pairs(remapped_distances),
        "qc_status": qc_status(
            exact_fraction_found=exact_fraction_found,
            exact_fraction_within_interface=exact_fraction_interface,
            remapped_fraction_found=remapped_fraction_found,
            remapped_fraction_within_interface=remapped_fraction_interface,
        ),
        "qc_note": (
            "QC compares exact reference-number selections and alignment-remapped selections. "
            "Manual structure review is still recommended for final figures."
        ),
    }

    for optional in [
        "short_lived_species",
        "contrast_class",
        "contrast_priority",
        "long_enrichment_ratio",
        "short_enrichment_ratio",
        "enrichment_delta",
        "enrichment_log2_ratio",
        "long_effect_size",
        "short_effect_size",
        "effect_size_delta",
    ]:
        if optional in row:
            output[optional] = row[optional]

    return output


def markdown_table(frame: pl.DataFrame) -> str:
    columns = frame.columns
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]

    for row in frame.iter_rows(named=True):
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append(f"{value:.4g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def write_markdown_report(
    qc: pl.DataFrame,
    output_md: Path,
    near_cutoff: float,
    interface_cutoff: float,
) -> None:
    overview = (
        qc.select(
            [
                "pdb_id",
                "chain",
                "structure_chain",
                "partner_structure_chain",
                "target_species",
                "contrast_class",
                "n_selected_residues",
                "exact_n_found",
                "exact_fraction_within_interface_cutoff",
                "remapped_n_found",
                "remapped_fraction_within_interface_cutoff",
                "qc_status",
            ]
        )
        if "contrast_class" in qc.columns
        else qc.select(
            [
                "pdb_id",
                "chain",
                "structure_chain",
                "partner_structure_chain",
                "target_species",
                "n_selected_residues",
                "exact_n_found",
                "exact_fraction_within_interface_cutoff",
                "remapped_n_found",
                "remapped_fraction_within_interface_cutoff",
                "qc_status",
            ]
        )
    )

    status_counts = qc.group_by("qc_status").len().sort("len", descending=True)

    lines = [
        "# SIRT6 mini-pilot v2 structure selection QC",
        "",
        "This report audits contrast-informed structure selections against local PDB/mmCIF structures.",
        "",
        "It reports both exact residue-number matches and sequence-alignment-remapped matches.",
        "",
        "Important caveat: this is a structural QC screen, not a replacement for final manual structure review.",
        "",
        "## Cutoffs",
        "",
        f"- near cutoff: {near_cutoff:.1f} A",
        f"- interface-proximal cutoff: {interface_cutoff:.1f} A",
        "",
        "## QC status counts",
        "",
        markdown_table(status_counts),
        "",
        "## Overview",
        "",
        markdown_table(overview),
        "",
        "## Interpretation notes",
        "",
        "- `exact_*` fields assume reference residue numbering equals structure residue numbering.",
        "- `remapped_*` fields align the residue-delta reference sequence to the structure chain sequence.",
        "- Low exact support with better remapped support indicates residue-numbering mismatch rather than necessarily a biological failure.",
        "- Low remapped proximity suggests that selections need manual review or that the candidate is not interface-proximal in the inspected structure.",
        "",
    ]

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    selection_path = Path(args.selection_summary)
    residue_deltas_path = Path(args.residue_deltas)
    pdb_dir = Path(args.pdb_dir)
    output_csv = Path(args.output_csv)
    output_md = Path(args.output_md)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection summary CSV: {selection_path}")

    if not residue_deltas_path.exists():
        raise FileNotFoundError(f"Missing residue deltas parquet: {residue_deltas_path}")

    if not pdb_dir.exists():
        raise FileNotFoundError(f"Missing PDB directory: {pdb_dir}")

    selection_summary = pl.read_csv(selection_path)
    residue_deltas = pl.read_parquet(residue_deltas_path)

    required_columns(
        residue_deltas,
        {"complex_id", "chain", "target_species", "residue_number_1based", "residue_aa"},
        residue_deltas_path,
    )

    groups = group_selection_summary(selection_summary)
    rows = [
        audit_group(
            row=row,
            residue_deltas=residue_deltas,
            pdb_dir=pdb_dir,
            near_cutoff=float(args.near_cutoff),
            interface_cutoff=float(args.interface_cutoff),
        )
        for row in groups.iter_rows(named=True)
    ]

    qc = pl.DataFrame(rows)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    qc.write_csv(output_csv)
    write_markdown_report(
        qc=qc,
        output_md=output_md,
        near_cutoff=float(args.near_cutoff),
        interface_cutoff=float(args.interface_cutoff),
    )

    print(f"Wrote structure selection QC CSV -> {output_csv}")
    print(f"Wrote structure selection QC Markdown -> {output_md}")
    print()
    print("QC status counts:")
    print(qc.group_by("qc_status").len().sort("len", descending=True))
    print()
    print("QC overview:")
    preview_columns = [
        "pdb_id",
        "chain",
        "structure_chain",
        "partner_structure_chain",
        "target_species",
        "n_selected_residues",
        "exact_n_found",
        "exact_fraction_within_interface_cutoff",
        "remapped_n_found",
        "remapped_fraction_within_interface_cutoff",
        "qc_status",
    ]
    if "contrast_class" in qc.columns:
        preview_columns.insert(5, "contrast_class")
    print(qc.select(preview_columns))


if __name__ == "__main__":
    main()
