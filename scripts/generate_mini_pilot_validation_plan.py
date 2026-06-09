from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

DEFAULT_SCORECARD = "data/output/sirt6_mini_pilot_candidate_scorecard.csv"
DEFAULT_OUTPUT_CSV = "data/output/sirt6_mini_pilot_validation_plan.csv"
DEFAULT_OUTPUT_MD = "data/output/sirt6_mini_pilot_validation_plan.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a preliminary validation plan from the mini-pilot candidate scorecard."
    )
    parser.add_argument(
        "--scorecard",
        default=DEFAULT_SCORECARD,
        help="Input mini-pilot candidate scorecard CSV.",
    )
    parser.add_argument(
        "--output-csv",
        default=DEFAULT_OUTPUT_CSV,
        help="Output validation plan CSV.",
    )
    parser.add_argument(
        "--output-md",
        default=DEFAULT_OUTPUT_MD,
        help="Output validation plan Markdown.",
    )
    return parser.parse_args()


def evidence_level(control_status: str, confidence: str) -> str:
    if control_status == "has_shuffled_and_negatome":
        if confidence == "high":
            return "controlled_high_confidence"
        if confidence == "medium":
            return "controlled_medium_confidence"
        return "controlled_low_confidence"

    if control_status == "missing_negatome":
        if confidence in {"high", "medium"}:
            return "preliminary_shuffled_only"
        return "low_confidence_shuffled_only"

    if control_status == "not_audited":
        return "not_audited"

    return "incomplete_control_evidence"


def validation_priority(
    outcome_class: str,
    confidence: str,
    control_status: str,
    score: float,
) -> str:
    if control_status != "has_shuffled_and_negatome":
        if outcome_class == "possible_interface_remodeling_or_incompatibility" and confidence in {
            "high",
            "medium",
        }:
            return "medium_preliminary"
        if outcome_class == "maintained_candidate" and confidence == "high" and score >= 10:
            return "medium_preliminary"
        if confidence in {"high", "medium"}:
            return "low_preliminary"
        return "defer"

    if outcome_class == "possible_interface_remodeling_or_incompatibility" and confidence in {
        "high",
        "medium",
    }:
        return "high"

    if outcome_class == "maintained_candidate" and confidence == "high":
        return "medium"

    if confidence == "medium":
        return "low"

    return "defer"


def primary_validation_assay(outcome_class: str, protein: str) -> str:
    if outcome_class == "maintained_candidate":
        return (
            f"Interaction-retention assay for {protein}: compare reference and target-species "
            "ortholog binding to the same partner/interface context."
        )

    if outcome_class == "possible_interface_remodeling_or_incompatibility":
        return (
            f"Differential binding assay for {protein}: compare reference and target-species "
            "ortholog binding strength and specificity against the matched partner."
        )

    if outcome_class == "possible_interface_remodeling_low_confidence":
        return (
            f"Low-confidence differential binding screen for {protein}; run only after structural "
            "inspection or added species support."
        )

    if outcome_class == "possible_maintained_low_confidence":
        return (
            f"Low-priority interaction-retention check for {protein}; use mainly as background "
            "or control evidence."
        )

    return (
        f"No immediate assay for {protein}. Expand species, partners, or controls before wet-lab "
        "validation."
    )


def secondary_validation_assay(outcome_class: str, biological_process: str) -> str:
    if "DNA double-strand break" in biological_process:
        return (
            "DNA damage response follow-up: test recruitment or retention after double-strand "
            "break induction, if a cell-based validation system is available."
        )

    if "PARP1" in biological_process or "PARP1-mediated" in biological_process:
        return (
            "PARP1 pathway follow-up: test DNA-damage-induced PARP1 recruitment, PARylation-linked "
            "readouts, or partner retention."
        )

    if "SIRT6" in biological_process or "chromatin" in biological_process:
        return (
            "Chromatin/DNA-repair follow-up: test chromatin association, histone-context binding, "
            "or DNA-repair-linked recruitment."
        )

    if outcome_class == "possible_interface_remodeling_or_incompatibility":
        return "Partner-panel specificity screen to distinguish true remodeling from general destabilization."

    return "No secondary assay assigned in the current mini-pilot."


def structural_followup(
    outcome_class: str,
    top_divergent: str,
    top_constrained: str,
) -> str:
    if outcome_class == "possible_interface_remodeling_or_incompatibility":
        return (
            "Inspect divergent interface residues in PyMOL/ChimeraX selections; check whether "
            "candidate sites cluster near the partner-binding surface."
        )

    if outcome_class == "maintained_candidate":
        return (
            "Inspect constrained interface residues as possible conserved interaction-core sites; "
            "use divergent residues as secondary context."
        )

    if top_divergent:
        return "Inspect top divergent residues before deciding whether this unresolved case deserves follow-up."

    if top_constrained:
        return "Inspect top constrained residues as background conserved-interface evidence."

    return "No structure-level follow-up assigned."


def control_requirement(control_status: str) -> str:
    if control_status == "has_shuffled_and_negatome":
        return (
            "No immediate control blocker; both shuffled and NEGATOME-style controls are populated."
        )

    if control_status == "missing_negatome":
        return (
            "Populate NEGATOME-style negative-control inputs and recompute control ratios before "
            "treating this as fully controlled evidence."
        )

    if control_status == "missing_shuffled":
        return "Recompute shuffled-mask controls before prioritization."

    if control_status == "missing_all_controls":
        return "Do not prioritize until shuffled and NEGATOME-style controls are populated."

    return "Run negative-control audit before prioritization."


def interpretation_warning(control_status: str, evidence: str) -> str:
    if control_status == "missing_negatome":
        return (
            "Preliminary plan only: current evidence is based on interface-vs-background statistics "
            "and shuffled-mask control, but lacks NEGATOME-style negative-control support."
        )

    if evidence.startswith("controlled"):
        return "Controlled evidence available; still requires biological and structural validation."

    if control_status == "not_audited":
        return "Negative-control audit has not been joined into the scorecard."

    return "Interpret cautiously because negative-control coverage is incomplete."


def priority_reason(
    outcome_class: str,
    confidence: str,
    score: float,
    control_status: str,
    effect_size: float,
    p_directional: float,
) -> str:
    return (
        f"Outcome={outcome_class}; confidence={confidence}; score={score:.3f}; "
        f"effect_size={effect_size:.3f}; p_directional={p_directional:.3g}; "
        f"control_status={control_status}."
    )


def required_columns() -> set[str]:
    return {
        "candidate_id",
        "protein",
        "target_species",
        "biological_process",
        "proposal_outcome_class",
        "confidence",
        "score",
        "effect_size_cohens_d",
        "p_directional",
        "control_status",
        "assay_priority",
        "engineering_priority",
        "top_divergent_interface_residues",
        "top_constrained_interface_residues",
        "recommended_next_action",
    }


def build_validation_plan(scorecard: pl.DataFrame) -> pl.DataFrame:
    missing = required_columns() - set(scorecard.columns)
    if missing:
        raise ValueError(f"Scorecard is missing required columns: {sorted(missing)}")

    rows: list[dict[str, object]] = []
    for row in scorecard.iter_rows(named=True):
        outcome_class = str(row["proposal_outcome_class"])
        confidence = str(row["confidence"])
        control_status = str(row["control_status"])
        protein = str(row["protein"])
        biological_process = str(row["biological_process"])
        score = float(row["score"])
        effect_size = float(row["effect_size_cohens_d"])
        p_directional = float(row["p_directional"])
        top_divergent = str(row["top_divergent_interface_residues"] or "")
        top_constrained = str(row["top_constrained_interface_residues"] or "")

        evidence = evidence_level(control_status, confidence)

        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "protein": protein,
                "target_species": row["target_species"],
                "biological_process": biological_process,
                "proposal_outcome_class": outcome_class,
                "confidence": confidence,
                "control_status": control_status,
                "evidence_level": evidence,
                "validation_priority": validation_priority(
                    outcome_class=outcome_class,
                    confidence=confidence,
                    control_status=control_status,
                    score=score,
                ),
                "score": score,
                "effect_size_cohens_d": effect_size,
                "p_directional": p_directional,
                "assay_priority": row["assay_priority"],
                "engineering_priority": row["engineering_priority"],
                "primary_validation_assay": primary_validation_assay(outcome_class, protein),
                "secondary_validation_assay": secondary_validation_assay(
                    outcome_class,
                    biological_process,
                ),
                "structural_followup": structural_followup(
                    outcome_class,
                    top_divergent,
                    top_constrained,
                ),
                "control_requirement": control_requirement(control_status),
                "interpretation_warning": interpretation_warning(control_status, evidence),
                "priority_reason": priority_reason(
                    outcome_class=outcome_class,
                    confidence=confidence,
                    score=score,
                    control_status=control_status,
                    effect_size=effect_size,
                    p_directional=p_directional,
                ),
                "top_divergent_interface_residues": top_divergent,
                "top_constrained_interface_residues": top_constrained,
                "scorecard_recommended_next_action": row["recommended_next_action"],
            }
        )

    priority_order = {
        "high": 0,
        "medium": 1,
        "medium_preliminary": 2,
        "low": 3,
        "low_preliminary": 4,
        "defer": 5,
    }

    return (
        pl.DataFrame(rows)
        .with_columns(
            pl.col("validation_priority")
            .replace_strict(priority_order, default=9)
            .alias("priority_sort")
        )
        .sort(["priority_sort", "score"], descending=[False, True])
        .drop("priority_sort")
    )


def write_markdown(plan: pl.DataFrame, output_path: Path) -> None:
    columns = [
        "candidate_id",
        "protein",
        "target_species",
        "proposal_outcome_class",
        "confidence",
        "control_status",
        "evidence_level",
        "validation_priority",
        "primary_validation_assay",
        "control_requirement",
    ]

    lines = [
        "# SIRT6 mini-pilot validation plan",
        "",
        "This is a preliminary validation plan generated from the mini-pilot candidate scorecard.",
        "",
        "Important: candidates with `missing_negatome` are not fully controlled hits. They should be treated as shuffled-control-only evidence until NEGATOME-style control ratios are populated.",
        "",
        "| candidate_id | protein | target_species | outcome | confidence | control_status | evidence_level | validation_priority | primary_validation_assay | control_requirement |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for row in plan.select(columns).iter_rows(named=True):
        lines.append(
            "| "
            f"{row['candidate_id']} | "
            f"{row['protein']} | "
            f"{row['target_species']} | "
            f"{row['proposal_outcome_class']} | "
            f"{row['confidence']} | "
            f"{row['control_status']} | "
            f"{row['evidence_level']} | "
            f"{row['validation_priority']} | "
            f"{row['primary_validation_assay']} | "
            f"{row['control_requirement']} |"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    scorecard_path = Path(args.scorecard)
    output_csv_path = Path(args.output_csv)
    output_md_path = Path(args.output_md)

    if not scorecard_path.exists():
        raise FileNotFoundError(f"Missing candidate scorecard: {scorecard_path}")

    scorecard = pl.read_csv(scorecard_path)
    plan = build_validation_plan(scorecard)

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    plan.write_csv(output_csv_path)
    write_markdown(plan, output_md_path)

    print(f"Wrote validation plan CSV -> {output_csv_path}")
    print(f"Wrote validation plan Markdown -> {output_md_path}")
    print()
    print("Validation priority counts:")
    print(
        plan.group_by(["validation_priority", "evidence_level"]).len().sort("len", descending=True)
    )

    print()
    print("Validation plan preview:")
    print(
        plan.select(
            [
                "candidate_id",
                "protein",
                "target_species",
                "proposal_outcome_class",
                "confidence",
                "control_status",
                "evidence_level",
                "validation_priority",
                "primary_validation_assay",
            ]
        ).head(15)
    )


if __name__ == "__main__":
    main()
