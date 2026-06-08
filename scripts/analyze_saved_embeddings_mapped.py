from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal

import numpy as np
import polars as pl
import requests
from Bio.PDB import MMCIFParser, NeighborSearch, PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

from longevity_port_pipelines.config import REFERENCE_SPECIES, TARGET_SPECIES, PipelineConfig
from longevity_port_pipelines.models import OrthologMapping
from longevity_port_pipelines.stages.analyze import analyze_pair
from longevity_port_pipelines.stages.embed import PerResidueEmbedding

StructureFormat = Literal["pdb", "cif"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze saved embeddings using sequence-mapped PDB/mmCIF interface extraction."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Selection CSV path.",
    )
    parser.add_argument(
        "--coverage",
        default="data/output/sirt6_mini_pilot_ortholog_coverage.csv",
        help="Ortholog coverage CSV path.",
    )
    parser.add_argument(
        "--output",
        default="data/output/sirt6_mini_pilot_enrichment_mapped.parquet",
        help="Output enrichment parquet path.",
    )
    parser.add_argument(
        "--distance-cutoff",
        type=float,
        default=8.0,
        help="Heavy-atom distance cutoff for interface residues.",
    )
    return parser.parse_args()


def species_name(taxid: int) -> str:
    if taxid == REFERENCE_SPECIES.taxid:
        return REFERENCE_SPECIES.name

    for species in TARGET_SPECIES:
        if species.taxid == taxid:
            return species.name

    return str(taxid)


def embedding_path(
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    taxid: int,
) -> Path:
    return output_dir / "embeddings" / model_name / f"{complex_id}_{chain}_{taxid}.npy"


def download_structure(pdb_id: str, output_dir: Path) -> tuple[Path, StructureFormat]:
    output_dir.mkdir(parents=True, exist_ok=True)

    pdb_id_upper = pdb_id.upper()
    pdb_path = output_dir / f"{pdb_id.lower()}.pdb"
    cif_path = output_dir / f"{pdb_id.lower()}.cif"

    if pdb_path.exists():
        return pdb_path, "pdb"
    if cif_path.exists():
        return cif_path, "cif"

    pdb_url = f"https://files.rcsb.org/download/{pdb_id_upper}.pdb"
    pdb_resp = requests.get(pdb_url, timeout=30)
    if pdb_resp.ok and pdb_resp.text.strip():
        pdb_path.write_text(pdb_resp.text, encoding="utf-8")
        return pdb_path, "pdb"

    cif_url = f"https://files.rcsb.org/download/{pdb_id_upper}.cif"
    cif_resp = requests.get(cif_url, timeout=30)
    cif_resp.raise_for_status()
    cif_path.write_text(cif_resp.text, encoding="utf-8")
    return cif_path, "cif"


def load_structure(path: Path, fmt: StructureFormat):
    parser = PDBParser(QUIET=True) if fmt == "pdb" else MMCIFParser(QUIET=True)
    return parser.get_structure(path.stem, str(path))


def chain_sequences(path: Path, fmt: StructureFormat) -> dict[str, str]:
    structure = load_structure(path, fmt)
    result: dict[str, str] = {}

    for model in structure:
        for chain in model:
            letters: list[str] = []
            for residue in chain:
                if not is_aa(residue, standard=False):
                    continue
                try:
                    letters.append(seq1(residue.get_resname()))
                except KeyError:
                    letters.append("X")
            if letters:
                result[chain.id] = "".join(letters)
        break

    return result


def longest_common_substring_len(a: str, b: str) -> int:
    if not a or not b:
        return 0

    previous = [0] * (len(b) + 1)
    best = 0

    for char_a in a:
        current = [0] * (len(b) + 1)
        for j, char_b in enumerate(b, start=1):
            if char_a == char_b:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current

    return best


def score_chain(query_sequence: str, chain_sequence: str) -> float:
    query = query_sequence.replace("-", "").replace("X", "")
    chain = chain_sequence.replace("-", "").replace("X", "")

    if not query or not chain:
        return 0.0

    if chain in query:
        return 1.0

    if query in chain:
        return len(query) / len(chain)

    lcs = longest_common_substring_len(query, chain)
    return lcs / max(1, min(len(query), len(chain)))


def best_chain_match(query_sequence: str, chains: dict[str, str]) -> tuple[str | None, float]:
    best_chain: str | None = None
    best_score = 0.0

    for chain_id, sequence in chains.items():
        score = score_chain(query_sequence, sequence)
        if score > best_score:
            best_chain = chain_id
            best_score = score

    return best_chain, best_score


def residue_index_map(chain) -> dict[object, int]:
    mapping: dict[object, int] = {}
    index = 0

    for residue in chain:
        if not is_aa(residue, standard=False):
            continue
        mapping[residue.id] = index
        index += 1

    return mapping


def extract_interface_residues_mapped(
    structure_path: Path,
    fmt: StructureFormat,
    chain_id_r: str,
    chain_id_l: str,
    distance_cutoff: float,
) -> tuple[list[int], list[int]]:
    structure = load_structure(structure_path, fmt)
    model = next(iter(structure))

    chain_r = model[chain_id_r]
    chain_l = model[chain_id_l]

    residue_map_r = residue_index_map(chain_r)
    residue_map_l = residue_index_map(chain_l)

    atoms_r = [
        atom
        for residue in chain_r
        if residue.id in residue_map_r
        for atom in residue
        if atom.element != "H"
    ]
    atoms_l = [
        atom
        for residue in chain_l
        if residue.id in residue_map_l
        for atom in residue
        if atom.element != "H"
    ]

    neighbor_search = NeighborSearch(atoms_l)

    interface_r: set[int] = set()
    interface_l: set[int] = set()

    atom_to_ligand_residue_index = {atom: residue_map_l[atom.get_parent().id] for atom in atoms_l}

    for atom_r in atoms_r:
        nearby_atoms = neighbor_search.search(atom_r.coord, distance_cutoff, level="A")
        if not nearby_atoms:
            continue

        residue_r = atom_r.get_parent()
        interface_r.add(residue_map_r[residue_r.id])

        for atom_l in nearby_atoms:
            interface_l.add(atom_to_ligand_residue_index[atom_l])

    return sorted(interface_r), sorted(interface_l)


def resolve_interfaces_for_row(
    row: dict[str, object],
    cfg: PipelineConfig,
    distance_cutoff: float,
) -> tuple[list[int], list[int], str, str, StructureFormat]:
    pdb_id = str(row["pdb_id"])
    structure_path, fmt = download_structure(pdb_id, cfg.interim_dir / "pdb")
    chains = chain_sequences(structure_path, fmt)

    best_r, score_r = best_chain_match(str(row["receptor_sequence"]), chains)
    best_l, score_l = best_chain_match(str(row["ligand_sequence"]), chains)

    if best_r is None or best_l is None:
        raise ValueError(f"Could not resolve chains for {row['id']}")

    if score_r < 0.8 or score_l < 0.8:
        raise ValueError(
            f"Low chain match score for {row['id']}: "
            f"receptor={best_r}/{score_r:.3f}, ligand={best_l}/{score_l:.3f}"
        )

    interface_r, interface_l = extract_interface_residues_mapped(
        structure_path,
        fmt,
        best_r,
        best_l,
        distance_cutoff,
    )

    return interface_r, interface_l, best_r, best_l, fmt


def main() -> None:
    args = parse_args()
    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection_path = Path(args.selection)
    coverage_path = Path(args.coverage)
    output_path = Path(args.output)

    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")
    if not coverage_path.exists():
        raise FileNotFoundError(f"Missing ortholog coverage CSV: {coverage_path}")

    selection = pl.read_csv(selection_path)
    coverage_df = pl.read_csv(coverage_path)

    mappings = [OrthologMapping(**row) for row in coverage_df.to_dicts()]
    mapping_by_source: dict[str, list[OrthologMapping]] = {}
    for mapping in mappings:
        mapping_by_source.setdefault(mapping.source_uniprot, []).append(mapping)

    results = []
    skipped_no_interface = 0
    skipped_no_mapping = 0
    skipped_missing_embedding = 0

    for row in selection.iter_rows(named=True):
        complex_id = str(row["id"])

        try:
            interface_r, interface_l, resolved_r, resolved_l, fmt = resolve_interfaces_for_row(
                row,
                cfg,
                args.distance_cutoff,
            )
            print(
                f"[INTERFACE] {complex_id}: {fmt} chains "
                f"{row['chain_R']}/{row['chain_L']} -> {resolved_r}/{resolved_l}; "
                f"R={len(interface_r)} L={len(interface_l)}"
            )
        except Exception as exc:
            skipped_no_interface += 2
            print(f"[SKIP] {complex_id}: could not resolve/extract interface: {exc}")
            continue

        for chain_label, up_col, seq_col, interface_residues in [
            ("receptor", "uniprot_R", "receptor_sequence", interface_r),
            ("ligand", "uniprot_L", "ligand_sequence", interface_l),
        ]:
            source_uniprot = row.get(up_col)
            ref_sequence = row.get(seq_col)

            if not source_uniprot or not ref_sequence:
                continue

            if not interface_residues:
                skipped_no_interface += 1
                print(f"[SKIP] {complex_id}/{chain_label}: no interface residues")
                continue

            chain_mappings = mapping_by_source.get(str(source_uniprot), [])
            if not chain_mappings:
                skipped_no_mapping += 1
                print(f"[SKIP] {complex_id}/{chain_label}/{source_uniprot}: no ortholog mappings")
                continue

            ref_path = embedding_path(
                cfg.output_dir,
                cfg.esmc_model,
                complex_id,
                chain_label,
                REFERENCE_SPECIES.taxid,
            )

            if not ref_path.exists():
                skipped_missing_embedding += 1
                print(f"[SKIP] Missing reference embedding: {ref_path}")
                continue

            ref_embedding_array = np.load(ref_path)

            ref_embedding = PerResidueEmbedding(
                complex_id=complex_id,
                chain=chain_label,
                species_taxid=REFERENCE_SPECIES.taxid,
                model_name=cfg.esmc_model,
                sequence=str(ref_sequence),
                embeddings=ref_embedding_array,
                is_predicted_structure=bool(row.get("predicted_R"))
                if chain_label == "receptor"
                else bool(row.get("predicted_L")),
            )

            for mapping in chain_mappings:
                orth_path = embedding_path(
                    cfg.output_dir,
                    cfg.esmc_model,
                    complex_id,
                    chain_label,
                    mapping.target_species_taxid,
                )

                if not orth_path.exists():
                    skipped_missing_embedding += 1
                    print(f"[SKIP] Missing ortholog embedding: {orth_path}")
                    continue

                orth_embedding_array = np.load(orth_path)

                orth_embedding = PerResidueEmbedding(
                    complex_id=complex_id,
                    chain=chain_label,
                    species_taxid=mapping.target_species_taxid,
                    model_name=cfg.esmc_model,
                    sequence=mapping.target_sequence,
                    embeddings=orth_embedding_array,
                    is_predicted_structure=not mapping.is_reviewed,
                )

                result = analyze_pair(
                    ref=ref_embedding,
                    orth=orth_embedding,
                    interface_residues=interface_residues,
                    source_species_name=species_name(REFERENCE_SPECIES.taxid),
                    target_species_name=species_name(mapping.target_species_taxid),
                    n_permutations=cfg.n_permutations,
                )
                results.append(result)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df = (
        pl.DataFrame([result.model_dump() for result in results]) if results else pl.DataFrame()
    )
    out_df.write_parquet(output_path)

    print()
    print(f"Wrote {len(results)} enrichment results -> {output_path}")
    print(f"Skipped no interface: {skipped_no_interface}")
    print(f"Skipped no mapping: {skipped_no_mapping}")
    print(f"Skipped missing embedding: {skipped_missing_embedding}")

    if results:
        print()
        print(
            out_df.select(
                [
                    "complex_id",
                    "chain",
                    "target_species",
                    "interface_mean_delta",
                    "noninterface_mean_delta",
                    "enrichment_ratio",
                    "mann_whitney_p",
                    "effect_size_cohens_d",
                ]
            )
            .sort("enrichment_ratio", descending=True)
            .head(30)
        )


if __name__ == "__main__":
    main()
