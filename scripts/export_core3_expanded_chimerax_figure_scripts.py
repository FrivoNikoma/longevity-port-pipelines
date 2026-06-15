from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

DEFAULT_INPUT_CSV = "data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.csv"
DEFAULT_PDB_DIR = "data/interim/pdb"
DEFAULT_OUTPUT_DIR = "data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_scripts"
DEFAULT_OUTPUT_MD = "data/output/sirt6_mini_pilot_v2_core3_expanded_chimerax_figure_scripts.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export ChimeraX figure scripts from the core3-expanded "
            "viewer-ready structure selections."
        )
    )
    parser.add_argument(
        "--input-csv",
        default=DEFAULT_INPUT_CSV,
        help="Viewer-ready structure selections CSV.",
    )
    parser.add_argument(
        "--pdb-dir",
        default=DEFAULT_PDB_DIR,
        help="Directory containing local PDB/mmCIF structure files.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where ChimeraX .cxc scripts will be written.",
    )
    parser.add_argument(
        "--output-md",
        default=DEFAULT_OUTPUT_MD,
        help="Markdown summary path.",
    )
    return parser.parse_args()


def safe_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def find_structure_file(pdb_dir: Path, pdb_id: str) -> Path:
    candidates = [
        pdb_dir / f"{pdb_id}.cif",
        pdb_dir / f"{pdb_id}.pdb",
        pdb_dir / f"{pdb_id.upper()}.cif",
        pdb_dir / f"{pdb_id.upper()}.pdb",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find structure file for {pdb_id} in {pdb_dir}")


def parse_pymol_patch_selection(selection: str) -> list[int]:
    match = re.search(r"resi\s+([0-9+]+)", selection)
    if not match:
        raise ValueError(f"Could not parse residue list from: {selection}")

    residue_block = match.group(1)
    residues = [int(token) for token in residue_block.split("+") if token.strip()]
    if not residues:
        raise ValueError(f"Parsed empty residue list from: {selection}")
    return residues


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def chimerax_residue_spec(residues: list[int]) -> str:
    return ",".join(str(value) for value in residues)


def build_script_text(
    *,
    structure_path: Path,
    png_path: Path,
    pdb_id: str,
    chain_role: str,
    target_species: str,
    structure_chain: str,
    partner_chain: str,
    contrast_class: str,
    qc_status: str,
    residues: list[int],
) -> str:
    residue_spec = chimerax_residue_spec(residues)

    title = f"{pdb_id} | {chain_role} | {target_species} | {contrast_class} | {qc_status}"

    lines = [
        f"# {title}",
        f'open "{structure_path.as_posix()}"',
        "hide atoms",
        "cartoon",
        f"color /{structure_chain} light gray",
        f"color /{partner_chain} cornflower blue",
        f"surface /{partner_chain}",
        f"transparency 65 /{partner_chain}",
        f"show /{structure_chain}:{residue_spec} atoms",
        f"style /{structure_chain}:{residue_spec} ball",
        f"color /{structure_chain}:{residue_spec} orange red",
        f"size /{structure_chain}:{residue_spec} atomRadius 1.0",
        "lighting soft",
        "graphics silhouettes true",
        f"view /{structure_chain}:{residue_spec}",
        "windowsize 1600 1200",
        f'save "{png_path.as_posix()}" width 2000 height 1600 supersample 3',
    ]
    return "\n".join(lines) + "\n"


def write_markdown_summary(
    *,
    output_path: Path,
    script_rows: list[dict[str, str]],
) -> None:
    lines: list[str] = []
    lines.append("# SIRT6 v2 core3-expanded ChimeraX figure scripts")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file indexes the ChimeraX figure scripts exported from the "
        "viewer-ready structure selections."
    )
    lines.append("")
    lines.append(
        "These scripts are intended to generate biologically interpretable 3D "
        "structure views in which:"
    )
    lines.append("")
    lines.append("- the target chain is shown as a light-gray cartoon;")
    lines.append("- the partner chain is shown as a blue semi-transparent surface;")
    lines.append("- the candidate residue patch is highlighted as orange-red spheres.")
    lines.append("")
    lines.append("## How to use")
    lines.append("")
    lines.append("Open a `.cxc` file in ChimeraX, or run it with:")
    lines.append("")
    lines.append("```text")
    lines.append("ChimeraX --script path/to/script.cxc")
    lines.append("```")
    lines.append("")
    lines.append("Each script also contains a `save` command to export a PNG rendering.")
    lines.append("")
    lines.append("## Exported scripts")
    lines.append("")

    for row in script_rows:
        heading = (
            f"### {row['pdb_id']} / {row['chain']} / {row['target_species']} / "
            f"{row['structure_chain']}/{row['partner_structure_chain']}"
        )
        lines.append(heading)
        lines.append("")
        lines.append(f"- Structure chain: `{row['structure_chain']}`")
        lines.append(f"- Partner chain: `{row['partner_structure_chain']}`")
        lines.append(f"- Contrast class: `{row['contrast_class']}`")
        lines.append(f"- QC status: `{row['qc_status']}`")
        lines.append(f"- Residue count: `{row['n_residues']}`")
        lines.append(f"- Script: `{row['script_path']}`")
        lines.append(f"- PNG target: `{row['png_path']}`")
        lines.append(f"- Residues: `{row['residue_numbers_for_display']}`")
        lines.append("")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_csv = Path(args.input_csv)
    pdb_dir = Path(args.pdb_dir)
    output_dir = Path(args.output_dir)
    output_md = Path(args.output_md)

    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_rows(input_csv)
    script_rows: list[dict[str, str]] = []

    for row in rows:
        pdb_id = row["pdb_id"]
        chain_role = row["chain"]
        target_species = row["target_species"]
        structure_chain = row["structure_chain"]
        partner_chain = row["partner_structure_chain"]
        contrast_class = row.get("contrast_class", "not_applicable")
        qc_status = row.get("qc_status", "unknown")
        pymol_patch_selection = row["pymol_patch_selection"]

        residues = parse_pymol_patch_selection(pymol_patch_selection)
        structure_path = find_structure_file(pdb_dir, pdb_id)

        script_stem = safe_name(
            f"{pdb_id}_{chain_role}_{structure_chain}_{partner_chain}_"
            f"{target_species}_{contrast_class}"
        )
        script_path = output_dir / f"{script_stem}.cxc"
        png_path = output_dir / f"{script_stem}.png"

        script_text = build_script_text(
            structure_path=structure_path,
            png_path=png_path,
            pdb_id=pdb_id,
            chain_role=chain_role,
            target_species=target_species,
            structure_chain=structure_chain,
            partner_chain=partner_chain,
            contrast_class=contrast_class,
            qc_status=qc_status,
            residues=residues,
        )
        script_path.write_text(script_text, encoding="utf-8")

        script_rows.append(
            {
                "pdb_id": pdb_id,
                "chain": chain_role,
                "target_species": target_species,
                "structure_chain": structure_chain,
                "partner_structure_chain": partner_chain,
                "contrast_class": contrast_class,
                "qc_status": qc_status,
                "n_residues": str(len(residues)),
                "residue_numbers_for_display": ",".join(str(value) for value in residues),
                "script_path": str(script_path).replace("\\", "/"),
                "png_path": str(png_path).replace("\\", "/"),
            }
        )

    write_markdown_summary(output_path=output_md, script_rows=script_rows)

    print(f"Wrote {len(script_rows)} ChimeraX scripts to {output_dir}")
    print(f"Wrote {output_md}")

    for row in script_rows:
        print(
            f"{row['pdb_id']:>5}  "
            f"{row['chain']:<8}  "
            f"{row['target_species']:<18}  "
            f"{row['structure_chain']}/{row['partner_structure_chain']}  "
            f"n_residues={row['n_residues']}"
        )


if __name__ == "__main__":
    main()
