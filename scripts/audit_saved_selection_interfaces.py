from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal

import polars as pl
import requests
from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1

from longevity_port_pipelines.config import PipelineConfig
from longevity_port_pipelines.stages.interface import extract_interface_residues

StructureFormat = Literal["pdb", "cif"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit interface extraction and chain mapping for a saved PINDER selection CSV."
    )
    parser.add_argument(
        "--selection",
        default="data/output/sirt6_mini_pilot_selection.csv",
        help="Selection CSV path.",
    )
    return parser.parse_args()


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


def main() -> None:
    args = parse_args()
    cfg = PipelineConfig()
    cfg.ensure_dirs()

    selection_path = Path(args.selection)
    if not selection_path.exists():
        raise FileNotFoundError(f"Missing selection CSV: {selection_path}")

    selection = pl.read_csv(selection_path)

    for row in selection.iter_rows(named=True):
        complex_id = str(row["id"])
        pdb_id = str(row["pdb_id"])
        chain_r = str(row["chain_R"])
        chain_l = str(row["chain_L"])
        receptor_sequence = str(row["receptor_sequence"])
        ligand_sequence = str(row["ligand_sequence"])

        print()
        print("=" * 100)
        print("complex_id:", complex_id)
        print("pdb_id:", pdb_id)
        print("PINDER chains:", chain_r, chain_l)
        print("UniProt:", row["uniprot_R"], row["uniprot_L"])

        try:
            structure_path, fmt = download_structure(pdb_id, cfg.interim_dir / "pdb")
            chains = chain_sequences(structure_path, fmt)

            print("structure file:", structure_path)
            print("structure format:", fmt)
            print("available chains:", sorted(chains))
            print("chain lengths:", {chain_id: len(seq) for chain_id, seq in chains.items()})

            best_r, score_r = best_chain_match(receptor_sequence, chains)
            best_l, score_l = best_chain_match(ligand_sequence, chains)

            print("best receptor chain:", best_r, "score:", round(score_r, 4))
            print("best ligand chain:", best_l, "score:", round(score_l, 4))

            if fmt != "pdb":
                print("interface extraction skipped: current extractor expects PDB format")
                continue

            if best_r is None or best_l is None:
                print("interface extraction skipped: no sequence-based chain match")
                continue

            interface_r, interface_l = extract_interface_residues(
                structure_path,
                best_r,
                best_l,
                cfg.interface_distance_cutoff,
            )
            print("interface_R residues:", len(interface_r))
            print("interface_L residues:", len(interface_l))

        except Exception as exc:
            print("ERROR:", exc)


if __name__ == "__main__":
    main()
