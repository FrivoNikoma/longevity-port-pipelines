"""Extract per-residue interface annotations from PDB structures."""

from __future__ import annotations

import logging
from pathlib import Path

import biotite.structure as struc
import biotite.structure.io.pdb as pdb
import numpy as np
import requests

logger = logging.getLogger(__name__)

RCSB_URL = "https://files.rcsb.org/download/{pdb_id}.pdb"


def download_pdb(pdb_id: str, dest_dir: Path) -> Path:
    """Download a PDB file from RCSB if not already present."""
    dest = dest_dir / f"{pdb_id.lower()}.pdb"
    if dest.exists():
        return dest

    url = RCSB_URL.format(pdb_id=pdb_id.upper())
    logger.info("Downloading PDB %s", pdb_id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_text(resp.text)
    return dest


def _per_atom_residue_index(chain: struc.AtomArray) -> np.ndarray:
    """Map each atom to a contiguous zero-based residue index within the chain."""
    starts = struc.get_residue_starts(chain)
    return np.searchsorted(starts, np.arange(chain.array_length()), side="right") - 1


def extract_interface_residues(
    pdb_path: Path,
    chain_id_r: str,
    chain_id_l: str,
    distance_cutoff: float = 8.0,
) -> tuple[list[int], list[int]]:
    """Identify interface residues by inter-chain heavy-atom distance.

    Returns (receptor_interface_indices, ligand_interface_indices) as
    zero-based residue indices within each chain.
    """
    pdb_file = pdb.PDBFile.read(str(pdb_path))
    structure = pdb.get_structure(pdb_file, model=1)

    amino = struc.filter_amino_acids(structure)
    chain_r = structure[amino & (structure.chain_id == chain_id_r)]
    chain_l = structure[amino & (structure.chain_id == chain_id_l)]

    if chain_r.array_length() == 0 or chain_l.array_length() == 0:
        logger.warning(
            "Chain(s) %s/%s empty or absent in %s — available: %s",
            chain_id_r,
            chain_id_l,
            pdb_path,
            sorted(set(structure.chain_id.tolist())),
        )
        return [], []

    res_idx_r = _per_atom_residue_index(chain_r)
    res_idx_l = _per_atom_residue_index(chain_l)

    # Efficient neighbour search: for each receptor atom, ligand atoms within cutoff.
    cell_list = struc.CellList(chain_l, cell_size=distance_cutoff)
    neighbors = cell_list.get_atoms(chain_r.coord, radius=distance_cutoff)

    interface_r: set[int] = set()
    interface_l: set[int] = set()

    for i in range(neighbors.shape[0]):
        js = neighbors[i]
        js = js[js >= 0]
        if js.size:
            interface_r.add(int(res_idx_r[i]))
            for j in js:
                interface_l.add(int(res_idx_l[j]))

    return sorted(interface_r), sorted(interface_l)
