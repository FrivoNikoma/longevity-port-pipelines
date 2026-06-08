from __future__ import annotations

from pathlib import Path

import polars as pl
from Bio.PDB import MMCIFParser, NeighborSearch
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1
from scripts.analyze_saved_embeddings_mapped import (
    best_chain_match,
    chain_sequences,
    download_structure,
)

from longevity_port_pipelines.config import PipelineConfig


def residue_count(chain) -> int:
    return sum(1 for residue in chain if is_aa(residue, standard=False))


def heavy_atoms(chain):
    return [
        atom
        for residue in chain
        if is_aa(residue, standard=False)
        for atom in residue
        if atom.element != "H"
    ]


def interface_counts(chain_r, chain_l, distance_cutoff: float = 8.0) -> tuple[int, int, int]:
    atoms_r = heavy_atoms(chain_r)
    atoms_l = heavy_atoms(chain_l)

    if not atoms_r or not atoms_l:
        return 0, 0, 0

    ns = NeighborSearch(atoms_l)

    residues_r = set()
    residues_l = set()
    atom_contacts = 0

    for atom_r in atoms_r:
        nearby_atoms = ns.search(atom_r.coord, distance_cutoff, level="A")
        if not nearby_atoms:
            continue

        residues_r.add(atom_r.get_parent().id)
        for atom_l in nearby_atoms:
            residues_l.add(atom_l.get_parent().id)
            atom_contacts += 1

    return len(residues_r), len(residues_l), atom_contacts


def seq_preview(chain) -> str:
    letters = []
    for residue in chain:
        if not is_aa(residue, standard=False):
            continue
        try:
            letters.append(seq1(residue.get_resname()))
        except KeyError:
            letters.append("X")
    return "".join(letters)[:60]


def main() -> None:
    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection = pl.read_csv("data/output/sirt6_mini_pilot_selection.csv")
    row = selection.filter(pl.col("pdb_id") == "8bot").row(0, named=True)

    receptor_sequence = str(row["receptor_sequence"])
    ligand_sequence = str(row["ligand_sequence"])

    structure_path, fmt = download_structure("8bot", cfg.interim_dir / "pdb")
    if fmt != "cif":
        raise ValueError(f"Expected mmCIF for 8bot, got {fmt}: {structure_path}")

    chains = chain_sequences(structure_path, fmt)

    print("structure:", structure_path)
    print("format:", fmt)
    print("PINDER chains:", row["chain_R"], row["chain_L"])
    print("UniProt:", row["uniprot_R"], row["uniprot_L"])
    print("available chains:", sorted(chains))
    print()

    receptor_candidates = []
    ligand_candidates = []

    for chain_id, sequence in chains.items():
        r_match, r_score = best_chain_match(receptor_sequence, {chain_id: sequence})
        l_match, l_score = best_chain_match(ligand_sequence, {chain_id: sequence})

        if r_match is not None and r_score >= 0.8:
            receptor_candidates.append((chain_id, r_score, len(sequence)))
        if l_match is not None and l_score >= 0.8:
            ligand_candidates.append((chain_id, l_score, len(sequence)))

    print("receptor-like chains:")
    for item in sorted(receptor_candidates):
        print(item)

    print()
    print("ligand-like chains:")
    for item in sorted(ligand_candidates):
        print(item)

    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("8bot", str(structure_path))
    model = next(iter(structure))

    rows = []
    for r_chain_id, r_score, r_len in receptor_candidates:
        for l_chain_id, l_score, l_len in ligand_candidates:
            if r_chain_id == l_chain_id:
                continue

            chain_r = model[r_chain_id]
            chain_l = model[l_chain_id]

            n_r, n_l, atom_contacts = interface_counts(chain_r, chain_l)

            rows.append(
                {
                    "receptor_chain": r_chain_id,
                    "ligand_chain": l_chain_id,
                    "receptor_score": r_score,
                    "ligand_score": l_score,
                    "receptor_len": r_len,
                    "ligand_len": l_len,
                    "interface_R": n_r,
                    "interface_L": n_l,
                    "atom_contacts": atom_contacts,
                    "receptor_preview": seq_preview(chain_r),
                    "ligand_preview": seq_preview(chain_l),
                }
            )

    df = pl.DataFrame(rows).sort(
        ["atom_contacts", "interface_R", "interface_L"],
        descending=[True, True, True],
    )

    print()
    print("candidate chain pairs ranked by contacts:")
    print(
        df.select(
            [
                "receptor_chain",
                "ligand_chain",
                "receptor_score",
                "ligand_score",
                "receptor_len",
                "ligand_len",
                "interface_R",
                "interface_L",
                "atom_contacts",
            ]
        )
    )

    out_path = Path("data/output/8bot_chain_pair_audit.csv")
    df.write_csv(out_path)
    print()
    print(f"Wrote audit table -> {out_path}")


if __name__ == "__main__":
    main()
