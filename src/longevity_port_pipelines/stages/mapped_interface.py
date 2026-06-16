"""Sequence-mapped interface extraction from PDB/mmCIF for saved-embedding analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypedDict

import requests
from Bio.PDB import MMCIFParser, NeighborSearch, PDBParser  # type: ignore[attr-defined]
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

from longevity_port_pipelines.config import PipelineConfig

StructureFormat = Literal["pdb", "cif"]


class ChainPairRow(TypedDict):
    receptor_chain: str
    ligand_chain: str
    receptor_score: float
    ligand_score: float
    interface_r_count: int
    interface_l_count: int
    atom_contacts: int


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


def load_structure(path: Path, fmt: StructureFormat) -> Any:
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


def chain_match_candidates(
    query_sequence: str,
    chains: dict[str, str],
    min_score: float = 0.8,
) -> list[tuple[str, float]]:
    candidates = []
    for chain_id, sequence in chains.items():
        score = score_chain(query_sequence, sequence)
        if score >= min_score:
            candidates.append((chain_id, score))

    return sorted(candidates, key=lambda item: (-item[1], item[0]))


def residue_index_map(chain: Any) -> dict[object, int]:
    mapping: dict[object, int] = {}
    index = 0

    for residue in chain:
        if not is_aa(residue, standard=False):
            continue
        mapping[residue.id] = index
        index += 1

    return mapping


def count_interface_atom_contacts(
    structure_path: Path,
    fmt: StructureFormat,
    chain_id_r: str,
    chain_id_l: str,
    distance_cutoff: float,
) -> tuple[int, int, int]:
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

    if not atoms_r or not atoms_l:
        return 0, 0, 0

    neighbor_search = NeighborSearch(atoms_l)
    interface_r: set[int] = set()
    interface_l: set[int] = set()
    atom_contacts = 0
    atom_to_ligand_residue_index = {atom: residue_map_l[atom.get_parent().id] for atom in atoms_l}

    for atom_r in atoms_r:
        nearby_atoms = neighbor_search.search(atom_r.coord, distance_cutoff, level="A")
        if not nearby_atoms:
            continue

        residue_r = atom_r.get_parent()
        interface_r.add(residue_map_r[residue_r.id])

        for atom_l in nearby_atoms:
            interface_l.add(atom_to_ligand_residue_index[atom_l])
            atom_contacts += 1

    return len(interface_r), len(interface_l), atom_contacts


def best_spatial_chain_pair(
    structure_path: Path,
    fmt: StructureFormat,
    chains: dict[str, str],
    receptor_sequence: str,
    ligand_sequence: str,
    distance_cutoff: float,
    min_score: float = 0.8,
) -> tuple[str, str, float, float, int, int, int]:
    receptor_candidates = chain_match_candidates(receptor_sequence, chains, min_score=min_score)
    ligand_candidates = chain_match_candidates(ligand_sequence, chains, min_score=min_score)

    if not receptor_candidates or not ligand_candidates:
        raise ValueError(
            "Could not find sequence-compatible chains: "
            f"receptor_candidates={receptor_candidates}, ligand_candidates={ligand_candidates}"
        )

    pair_rows: list[ChainPairRow] = []
    for receptor_chain, receptor_score in receptor_candidates:
        for ligand_chain, ligand_score in ligand_candidates:
            if receptor_chain == ligand_chain:
                continue

            interface_r_count, interface_l_count, atom_contacts = count_interface_atom_contacts(
                structure_path=structure_path,
                fmt=fmt,
                chain_id_r=receptor_chain,
                chain_id_l=ligand_chain,
                distance_cutoff=distance_cutoff,
            )

            pair_rows.append(
                {
                    "receptor_chain": receptor_chain,
                    "ligand_chain": ligand_chain,
                    "receptor_score": receptor_score,
                    "ligand_score": ligand_score,
                    "interface_r_count": interface_r_count,
                    "interface_l_count": interface_l_count,
                    "atom_contacts": atom_contacts,
                }
            )

    if not pair_rows:
        raise ValueError("No valid receptor/ligand chain pairs after excluding identical chains")

    best = max(
        pair_rows,
        key=lambda row: (
            row["atom_contacts"],
            row["interface_r_count"] + row["interface_l_count"],
            row["receptor_score"] + row["ligand_score"],
        ),
    )

    return (
        str(best["receptor_chain"]),
        str(best["ligand_chain"]),
        float(best["receptor_score"]),
        float(best["ligand_score"]),
        int(best["interface_r_count"]),
        int(best["interface_l_count"]),
        int(best["atom_contacts"]),
    )


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

    best_r, best_l, score_r, score_l, interface_r_count, interface_l_count, atom_contacts = (
        best_spatial_chain_pair(
            structure_path=structure_path,
            fmt=fmt,
            chains=chains,
            receptor_sequence=str(row["receptor_sequence"]),
            ligand_sequence=str(row["ligand_sequence"]),
            distance_cutoff=distance_cutoff,
        )
    )

    if atom_contacts == 0:
        raise ValueError(
            f"No spatial contacts found for sequence-compatible chain pairs in {row['id']}"
        )

    interface_r, interface_l = extract_interface_residues_mapped(
        structure_path,
        fmt,
        best_r,
        best_l,
        distance_cutoff,
    )

    print(
        f"[CHAIN_PAIR] {row['id']}: selected {best_r}/{best_l}; "
        f"seq_scores={score_r:.3f}/{score_l:.3f}; "
        f"contact_counts=R{interface_r_count}/L{interface_l_count}/atoms{atom_contacts}"
    )

    return interface_r, interface_l, best_r, best_l, fmt
