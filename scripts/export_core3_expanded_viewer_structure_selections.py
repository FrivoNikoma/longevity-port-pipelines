from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

QC_PATH = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_manual_review_structure_qc.csv")
OUT_CSV = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.csv")
OUT_MD = Path("data/output/sirt6_mini_pilot_v2_core3_expanded_viewer_structure_selections.md")


def safe_name(value: object) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "selection"


def parse_residue_list(value: object) -> list[int]:
    if value is None or pd.isna(value):
        return []

    text = str(value)
    return [int(match) for match in re.findall(r"\d+", text)]


def parse_mapping(value: object) -> dict[int, int]:
    if value is None or pd.isna(value):
        return {}

    text = str(value)
    pairs: dict[int, int] = {}

    for left, right in re.findall(r"(\d+)\s*(?:->|:|=)\s*(\d+)", text):
        pairs[int(left)] = int(right)

    if pairs:
        return pairs

    # Fallback for compact pair formats such as "45,44;46,45".
    for part in re.split(r"[;|]", text):
        numbers = [int(match) for match in re.findall(r"\d+", part)]
        if len(numbers) == 2:
            pairs[numbers[0]] = numbers[1]

    return pairs


def residue_join_pymol(residues: list[int]) -> str:
    return "+".join(str(value) for value in residues)


def residue_join_chimerax(residues: list[int]) -> str:
    return ",".join(str(value) for value in residues)


def residue_join_text(residues: list[int]) -> str:
    return ";".join(str(value) for value in residues)


def mapping_join(mapping: dict[int, int]) -> str:
    return ";".join(f"{ref}->{structure}" for ref, structure in sorted(mapping.items()))


def main() -> None:
    qc = pd.read_csv(QC_PATH)

    required = {
        "candidate_type",
        "complex_id",
        "pdb_id",
        "chain",
        "structure_chain",
        "partner_structure_chain",
        "target_species",
        "contrast_class",
        "selected_reference_residues",
        "remapped_reference_to_structure_residue",
        "remapped_fraction_found",
        "remapped_fraction_within_interface_cutoff",
        "qc_status",
    }

    missing = required - set(qc.columns)
    if missing:
        raise ValueError(f"{QC_PATH} is missing required columns: {sorted(missing)}")

    rows: list[dict[str, object]] = []

    for _, row in qc.iterrows():
        mapping = parse_mapping(row["remapped_reference_to_structure_residue"])
        reference_residues = parse_residue_list(row["selected_reference_residues"])
        structure_residues = sorted(set(mapping.values()))

        if not structure_residues:
            raise RuntimeError(
                "No remapped structure residues parsed for "
                f"{row['complex_id']} / {row['chain']} / {row['target_species']}"
            )

        pdb_id = str(row["pdb_id"])
        chain_role = str(row["chain"])
        species = str(row["target_species"])
        structure_chain = str(row["structure_chain"])
        partner_chain = str(row["partner_structure_chain"])

        selection_name = safe_name(
            f"{pdb_id}_{chain_role}_{structure_chain}_{partner_chain}_{species}_{row['contrast_class']}_patch"
        )
        partner_selection_name = safe_name(
            f"{pdb_id}_{chain_role}_{structure_chain}_{partner_chain}_{species}_partner"
        )

        pymol_patch = (
            f"select {selection_name}, chain {structure_chain} "
            f"and resi {residue_join_pymol(structure_residues)}"
        )
        pymol_partner = f"select {partner_selection_name}, chain {partner_chain}"
        pymol_show = (
            f"show sticks, {selection_name}; "
            f"show surface, chain {partner_chain}; "
            f"color yellow, {selection_name}; "
            f"color cyan, {partner_selection_name}"
        )

        chimerax_patch = f"select /{structure_chain}:{residue_join_chimerax(structure_residues)}"
        chimerax_partner = f"select /{partner_chain}"
        chimerax_show = (
            f"style /{structure_chain}:{residue_join_chimerax(structure_residues)} stick; "
            f"surface /{partner_chain}"
        )

        rows.append(
            {
                "candidate_type": row["candidate_type"],
                "complex_id": row["complex_id"],
                "pdb_id": pdb_id,
                "chain": chain_role,
                "target_species": species,
                "contrast_class": row["contrast_class"],
                "qc_status": row["qc_status"],
                "structure_chain": structure_chain,
                "partner_structure_chain": partner_chain,
                "n_reference_residues": len(reference_residues),
                "n_remapped_structure_residues": len(structure_residues),
                "remapped_fraction_found": row["remapped_fraction_found"],
                "remapped_fraction_within_interface_cutoff": row[
                    "remapped_fraction_within_interface_cutoff"
                ],
                "reference_residues": residue_join_text(reference_residues),
                "structure_residues": residue_join_text(structure_residues),
                "reference_to_structure_mapping": mapping_join(mapping),
                "pymol_selection_name": selection_name,
                "pymol_patch_selection": pymol_patch,
                "pymol_partner_selection": pymol_partner,
                "pymol_display_hint": pymol_show,
                "chimerax_patch_selection": chimerax_patch,
                "chimerax_partner_selection": chimerax_partner,
                "chimerax_display_hint": chimerax_show,
                "molstar_note": (
                    f"Select chain {structure_chain} residues "
                    f"{residue_join_text(structure_residues)}; "
                    f"partner chain {partner_chain}."
                ),
            }
        )

    out = pd.DataFrame(rows).sort_values(
        ["candidate_type", "complex_id", "chain", "target_species"]
    )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    lines: list[str] = []
    lines.append("# SIRT6 v2 core3-expanded viewer-ready structure selections")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file exports viewer-ready selections for manual 3D review of the "
        "SIRT6 v2 core3-expanded manual-review residue patches."
    )
    lines.append("")
    lines.append(
        "Selections are based on `remapped_reference_to_structure_residue` from "
        "the structure-QC output, not on raw `residue_number_1based` values."
    )
    lines.append("")
    lines.append("## Important caveat")
    lines.append("")
    lines.append(
        "These selections are review aids. They should be visually inspected before "
        "being used for final figures or biological claims."
    )
    lines.append("")
    lines.append("## Selection summary")
    lines.append("")

    for _, row in out.iterrows():
        lines.append(f"### {row['pdb_id']} / {row['chain']} / {row['target_species']}")
        lines.append("")
        lines.append(f"- Candidate type: {row['candidate_type']}")
        lines.append(f"- Complex: `{row['complex_id']}`")
        lines.append(f"- Contrast class: `{row['contrast_class']}`")
        lines.append(f"- QC status: `{row['qc_status']}`")
        lines.append(f"- Structure chain: `{row['structure_chain']}`")
        lines.append(f"- Partner chain: `{row['partner_structure_chain']}`")
        lines.append(f"- Reference residues: `{row['reference_residues']}`")
        lines.append(f"- Remapped structure residues: `{row['structure_residues']}`")
        lines.append("")
        lines.append("PyMOL:")
        lines.append("")
        lines.append("```text")
        lines.append(str(row["pymol_patch_selection"]))
        lines.append(str(row["pymol_partner_selection"]))
        lines.append(str(row["pymol_display_hint"]))
        lines.append("```")
        lines.append("")
        lines.append("ChimeraX:")
        lines.append("")
        lines.append("```text")
        lines.append(str(row["chimerax_patch_selection"]))
        lines.append(str(row["chimerax_partner_selection"]))
        lines.append(str(row["chimerax_display_hint"]))
        lines.append("```")
        lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CSV} with {len(out)} rows")
    print(f"Wrote {OUT_MD}")
    print("")
    print(
        out[
            [
                "pdb_id",
                "chain",
                "target_species",
                "structure_chain",
                "partner_structure_chain",
                "n_remapped_structure_residues",
                "qc_status",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
