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
            "Export ChimeraX overview and closeup figure scripts from the "
            "core3-expanded viewer-ready structure selections."
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

    residues = [int(token) for token in match.group(1).split("+") if token.strip()]
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
    view_mode: str,
) -> str:
    residue_spec = chimerax_residue_spec(residues)
    patch_spec = f"/{structure_chain}:{residue_spec}"

    if view_mode == "overview":
        title_suffix = "Overview"
        view_commands = [f"view /{structure_chain}"]
    elif view_mode == "closeup":
        title_suffix = "Closeup"
        view_commands = [f"view {patch_spec}", "zoom 1.6"]
    else:
        raise ValueError(f"Unexpected view mode: {view_mode}")

    title = (
        f"{pdb_id} | {chain_role} | {target_species} | "
        f"{contrast_class} | {qc_status} | {title_suffix}"
    )

    lines = [
        f"# {title}",
        f'open "{structure_path.as_posix()}"',
        "set bgColor white",
        "hide atoms",
        "hide cartoons",
        "hide surfaces",
        f"cartoon /{structure_chain}",
        f"color /{structure_chain} gray",
        f"surface /{partner_chain}",
        f"color /{partner_chain} blue surfaces",
        f"transparency /{partner_chain} 75 surfaces",
        f"show {patch_spec} atoms",
        f"style {patch_spec} ball",
        f"color {patch_spec} orange",
        f"size {patch_spec} atomRadius 1.55",
        "lighting soft",
        "graphics silhouettes true",
        *view_commands,
        "windowsize 1600 1200",
        f'save "{png_path.as_posix()}" width 2400 height 1800 supersample 3',
        "exit",
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
        "This file indexes the ChimeraX overview and closeup figure scripts "
        "exported from the viewer-ready structure selections."
    )
    lines.append("")
    lines.append("The generated scripts use a robust ChimeraX command subset:")
    lines.append("")
    lines.append("- target chain: gray cartoon;")
    lines.append("- partner chain: blue semi-transparent surface;")
    lines.append("- candidate residue patch: orange spheres;")
    lines.append("- overview view: target-chain framing;")
    lines.append("- closeup view: patch-residue framing.")
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
        lines.append(
            f"### {row['pdb_id']} / {row['chain']} / {row['target_species']} / "
            f"{row['structure_chain']}/{row['partner_structure_chain']}"
        )
        lines.append("")
        lines.append(f"- Contrast class: `{row['contrast_class']}`")
        lines.append(f"- QC status: `{row['qc_status']}`")
        lines.append(f"- Residue count: `{row['n_residues']}`")
        lines.append(f"- Residues: `{row['residue_numbers_for_display']}`")
        lines.append(f"- Overview script: `{row['overview_script_path']}`")
        lines.append(f"- Overview PNG target: `{row['overview_png_path']}`")
        lines.append(f"- Closeup script: `{row['closeup_script_path']}`")
        lines.append(f"- Closeup PNG target: `{row['closeup_png_path']}`")
        lines.append("")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_csv = Path(args.input_csv)
    pdb_dir = Path(args.pdb_dir)
    output_dir = Path(args.output_dir)
    output_md = Path(args.output_md)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

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

        case_stem = safe_name(
            f"{pdb_id}_{chain_role}_{structure_chain}_{partner_chain}_"
            f"{target_species}_{contrast_class}"
        )

        script_paths: dict[str, Path] = {}
        png_paths: dict[str, Path] = {}

        for view_mode in ["overview", "closeup"]:
            script_path = output_dir / f"{case_stem}_{view_mode}.cxc"
            png_path = output_dir / f"{case_stem}_{view_mode}.png"

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
                view_mode=view_mode,
            )
            script_path.write_text(script_text, encoding="utf-8")

            script_paths[view_mode] = script_path
            png_paths[view_mode] = png_path

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
                "overview_script_path": str(script_paths["overview"]).replace("\\", "/"),
                "overview_png_path": str(png_paths["overview"]).replace("\\", "/"),
                "closeup_script_path": str(script_paths["closeup"]).replace("\\", "/"),
                "closeup_png_path": str(png_paths["closeup"]).replace("\\", "/"),
            }
        )

    write_markdown_summary(output_path=output_md, script_rows=script_rows)

    print(
        f"Wrote {len(script_rows) * 2} ChimeraX scripts ({len(script_rows)} cases) to {output_dir}"
    )
    print(f"Wrote {output_md}")

    for row in script_rows:
        print(
            f"{row['pdb_id']:>5}  "
            f"{row['chain']:<8}  "
            f"{row['target_species']:<18}  "
            f"{row['structure_chain']}/{row['partner_structure_chain']}  "
            f"n_residues={row['n_residues']}  "
            "overview+closeup"
        )


if __name__ == "__main__":
    main()
