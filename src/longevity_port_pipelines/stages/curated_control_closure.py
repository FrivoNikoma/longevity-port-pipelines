from __future__ import annotations

from pathlib import Path

import polars as pl
import typer

from longevity_port_pipelines.stages.negative_controls import (
    DEFAULT_CONTROL_P_ALPHA,
    DEFAULT_CONTROL_RATIO_MARGIN,
    control_signal_direction,
)

DEFAULT_ENRICHMENT_INPUT = Path("data/output/curated_ortholog_enrichment.csv")
DEFAULT_CLOSURE_OUTPUT = Path("data/output/curated_ortholog_control_closure.csv")
DEFAULT_CLOSURE_MARKDOWN = Path("data/output/curated_ortholog_control_closure.md")

REQUIRED_ENRICHMENT_COLUMNS = {
    "complex_id",
    "chain",
    "target_species",
    "target_species_taxid",
    "source_uniprot",
    "status",
    "control_status",
    "interpretation_status",
    "enrichment_ratio",
    "shuffled_control_ratio",
    "negatome_control_ratio",
    "p_interface_greater",
    "p_interface_less",
    "effect_size_cohens_d",
}

CLOSURE_SCHEMA = {
    "complex_id": pl.Utf8,
    "chain": pl.Utf8,
    "target_species": pl.Utf8,
    "target_species_taxid": pl.Int64,
    "source_uniprot": pl.Utf8,
    "status": pl.Utf8,
    "control_status": pl.Utf8,
    "interpretation_status": pl.Utf8,
    "signal_direction": pl.Utf8,
    "passes_shuffled_gate": pl.Boolean,
    "passes_negatome_gate": pl.Boolean,
    "passes_directional_p_gate": pl.Boolean,
    "closure_status": pl.Utf8,
    "closure_note": pl.Utf8,
    "enrichment_ratio": pl.Float64,
    "shuffled_control_ratio": pl.Float64,
    "negatome_control_ratio": pl.Float64,
    "p_interface_greater": pl.Float64,
    "p_interface_less": pl.Float64,
    "effect_size_cohens_d": pl.Float64,
}

app = typer.Typer(add_completion=False)


def empty_curated_control_closure_report() -> pl.DataFrame:
    return pl.DataFrame(schema=CLOSURE_SCHEMA)


def validate_enrichment_schema(enrichment: pl.DataFrame) -> None:
    missing = sorted(REQUIRED_ENRICHMENT_COLUMNS.difference(enrichment.columns))
    if missing:
        raise ValueError(f"Curated enrichment report is missing required columns: {missing}")


def _as_str(row: dict[str, object], column: str) -> str:
    value = row[column]
    if value is None:
        return ""
    return str(value).strip()


def _as_int(row: dict[str, object], column: str) -> int:
    value = row[column]
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return int(value.strip())
    raise ValueError(f"Cannot interpret integer value for {column}: {value!r}")


def _optional_float(row: dict[str, object], column: str) -> float | None:
    value = row[column]
    if value is None:
        return None
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return float(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        return float(stripped)
    raise ValueError(f"Cannot interpret float value for {column}: {value!r}")


def _passes_ratio_gate(
    *,
    enrichment_ratio: float | None,
    control_ratio: float | None,
    signal_direction: str,
    ratio_margin: float,
) -> bool:
    if enrichment_ratio is None or control_ratio is None:
        return False
    if control_ratio <= 0.0:
        return False

    if signal_direction == "divergence":
        return enrichment_ratio > control_ratio * ratio_margin
    if signal_direction == "constraint":
        return enrichment_ratio < control_ratio / ratio_margin

    return False


def _passes_directional_p_gate(
    *,
    signal_direction: str,
    p_interface_greater: float | None,
    p_interface_less: float | None,
    p_alpha: float,
) -> bool:
    if signal_direction == "divergence":
        return p_interface_greater is not None and p_interface_greater < p_alpha
    if signal_direction == "constraint":
        return p_interface_less is not None and p_interface_less < p_alpha
    return False


def _closure_status(
    *,
    status: str,
    control_status: str,
    interpretation_status: str,
    passes_shuffled_gate: bool,
    passes_negatome_gate: bool,
    passes_directional_p_gate: bool,
) -> str:
    if status != "enrichment_completed":
        return "not_completed"

    if control_status == "has_shuffled_and_negatome":
        if (
            interpretation_status == "controlled_pass"
            and passes_shuffled_gate
            and passes_negatome_gate
            and passes_directional_p_gate
        ):
            return "controlled_pass"

        if passes_shuffled_gate and not passes_negatome_gate and passes_directional_p_gate:
            return "controlled_fail_negatome_not_specific"

        if not passes_shuffled_gate and passes_negatome_gate and passes_directional_p_gate:
            return "controlled_fail_shuffled_not_specific"

        if not passes_directional_p_gate:
            return "controlled_fail_directional_p"

        return "controlled_fail_ratio_gate"

    if control_status == "missing_negatome":
        if passes_shuffled_gate and passes_directional_p_gate:
            return "preliminary_shuffled_only"
        return "preliminary_missing_negatome"

    if control_status == "missing_shuffled":
        return "incomplete_missing_shuffled"

    if control_status == "missing_all_controls":
        return "missing_all_controls"

    return "not_audited"


def _closure_note(*, closure_status: str, signal_direction: str) -> str:
    if closure_status == "controlled_pass":
        return (
            f"Controlled {signal_direction} signal passes shuffled, NEGATOME, "
            "and directional p-value gates."
        )

    if closure_status == "controlled_fail_negatome_not_specific":
        return (
            f"The {signal_direction} signal passes shuffled and directional p-value gates, "
            "but does not beat the curated NEGATOME control by the configured margin. "
            "Treat as not specific enough for strict controlled evidence."
        )

    if closure_status == "controlled_fail_shuffled_not_specific":
        return (
            f"The {signal_direction} signal passes NEGATOME and directional p-value gates, "
            "but does not beat the shuffled-mask control by the configured margin."
        )

    if closure_status == "controlled_fail_directional_p":
        return (
            f"The {signal_direction} signal has both controls populated, but the directional "
            "p-value gate does not pass."
        )

    if closure_status == "controlled_fail_ratio_gate":
        return (
            f"The {signal_direction} signal has both controls populated, but at least one "
            "strict ratio gate does not pass."
        )

    if closure_status == "preliminary_shuffled_only":
        return (
            f"The {signal_direction} signal has shuffled-control support, but NEGATOME "
            "control is missing. Treat as preliminary evidence only."
        )

    if closure_status == "preliminary_missing_negatome":
        return "NEGATOME control is missing; strict controlled evidence cannot be claimed."

    if closure_status == "not_completed":
        return "Curated enrichment did not complete for this row."

    return "Control evidence is incomplete or not audited."


def build_curated_control_closure(
    enrichment: pl.DataFrame,
    *,
    ratio_margin: float = DEFAULT_CONTROL_RATIO_MARGIN,
    p_alpha: float = DEFAULT_CONTROL_P_ALPHA,
) -> pl.DataFrame:
    validate_enrichment_schema(enrichment)

    if enrichment.is_empty():
        return empty_curated_control_closure_report()

    rows: list[dict[str, object]] = []
    for row in enrichment.iter_rows(named=True):
        status = _as_str(row, "status")
        control_status = _as_str(row, "control_status")
        interpretation_status = _as_str(row, "interpretation_status")

        enrichment_ratio = _optional_float(row, "enrichment_ratio")
        shuffled_control_ratio = _optional_float(row, "shuffled_control_ratio")
        negatome_control_ratio = _optional_float(row, "negatome_control_ratio")
        p_interface_greater = _optional_float(row, "p_interface_greater")
        p_interface_less = _optional_float(row, "p_interface_less")
        effect_size = _optional_float(row, "effect_size_cohens_d")

        signal_direction = (
            control_signal_direction(enrichment_ratio)
            if status == "enrichment_completed" and enrichment_ratio is not None
            else "not_computed"
        )

        passes_shuffled_gate = _passes_ratio_gate(
            enrichment_ratio=enrichment_ratio,
            control_ratio=shuffled_control_ratio,
            signal_direction=signal_direction,
            ratio_margin=ratio_margin,
        )
        passes_negatome_gate = _passes_ratio_gate(
            enrichment_ratio=enrichment_ratio,
            control_ratio=negatome_control_ratio,
            signal_direction=signal_direction,
            ratio_margin=ratio_margin,
        )
        passes_directional_p_gate = _passes_directional_p_gate(
            signal_direction=signal_direction,
            p_interface_greater=p_interface_greater,
            p_interface_less=p_interface_less,
            p_alpha=p_alpha,
        )

        closure_status = _closure_status(
            status=status,
            control_status=control_status,
            interpretation_status=interpretation_status,
            passes_shuffled_gate=passes_shuffled_gate,
            passes_negatome_gate=passes_negatome_gate,
            passes_directional_p_gate=passes_directional_p_gate,
        )

        rows.append(
            {
                "complex_id": _as_str(row, "complex_id"),
                "chain": _as_str(row, "chain"),
                "target_species": _as_str(row, "target_species"),
                "target_species_taxid": _as_int(row, "target_species_taxid"),
                "source_uniprot": _as_str(row, "source_uniprot"),
                "status": status,
                "control_status": control_status,
                "interpretation_status": interpretation_status,
                "signal_direction": signal_direction,
                "passes_shuffled_gate": passes_shuffled_gate,
                "passes_negatome_gate": passes_negatome_gate,
                "passes_directional_p_gate": passes_directional_p_gate,
                "closure_status": closure_status,
                "closure_note": _closure_note(
                    closure_status=closure_status,
                    signal_direction=signal_direction,
                ),
                "enrichment_ratio": enrichment_ratio,
                "shuffled_control_ratio": shuffled_control_ratio,
                "negatome_control_ratio": negatome_control_ratio,
                "p_interface_greater": p_interface_greater,
                "p_interface_less": p_interface_less,
                "effect_size_cohens_d": effect_size,
            }
        )

    return (
        pl.DataFrame(rows)
        .select(
            [pl.col(column).cast(dtype).alias(column) for column, dtype in CLOSURE_SCHEMA.items()]
        )
        .sort(["closure_status", "complex_id", "chain", "target_species_taxid"])
    )


def render_curated_control_closure_markdown(closure: pl.DataFrame) -> str:
    lines = [
        "# Curated ortholog control closure",
        "",
        "This generated report summarizes whether curated ortholog enrichment rows pass the",
        "strict shuffled-mask and NEGATOME-style control gates.",
        "",
    ]

    if closure.is_empty():
        lines.append("No curated enrichment rows were available for closure.")
        lines.append("")
        return "\n".join(lines)

    for row in closure.iter_rows(named=True):
        lines.extend(
            [
                f"## {row['complex_id']} / {row['chain']} / {row['target_species']}",
                "",
                f"- source_uniprot: `{row['source_uniprot']}`",
                f"- signal_direction: `{row['signal_direction']}`",
                f"- control_status: `{row['control_status']}`",
                f"- interpretation_status: `{row['interpretation_status']}`",
                f"- closure_status: `{row['closure_status']}`",
                f"- passes_shuffled_gate: `{row['passes_shuffled_gate']}`",
                f"- passes_negatome_gate: `{row['passes_negatome_gate']}`",
                f"- passes_directional_p_gate: `{row['passes_directional_p_gate']}`",
                f"- enrichment_ratio: `{row['enrichment_ratio']}`",
                f"- shuffled_control_ratio: `{row['shuffled_control_ratio']}`",
                f"- negatome_control_ratio: `{row['negatome_control_ratio']}`",
                "",
                str(row["closure_note"]),
                "",
            ]
        )

    return "\n".join(lines)


def _closure_status_counts(closure: pl.DataFrame) -> dict[str, int]:
    if closure.is_empty():
        return {}

    counts: dict[str, int] = {}
    for row in closure.group_by("closure_status").len().iter_rows(named=True):
        counts[_as_str(row, "closure_status")] = int(row["len"])

    return counts


@app.command()
def main(
    enrichment: Path = DEFAULT_ENRICHMENT_INPUT,
    output_csv: Path = DEFAULT_CLOSURE_OUTPUT,
    output_md: Path = DEFAULT_CLOSURE_MARKDOWN,
    ratio_margin: float = DEFAULT_CONTROL_RATIO_MARGIN,
    p_alpha: float = DEFAULT_CONTROL_P_ALPHA,
) -> None:
    """Summarize strict controlled-evidence closure for curated ortholog enrichment."""
    if not enrichment.exists():
        raise FileNotFoundError(f"Missing curated enrichment report: {enrichment}")

    enrichment_df = pl.read_csv(enrichment)
    closure = build_curated_control_closure(
        enrichment_df,
        ratio_margin=ratio_margin,
        p_alpha=p_alpha,
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    closure.write_csv(output_csv)

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_curated_control_closure_markdown(closure), encoding="utf-8")

    typer.echo(f"curated enrichment rows closed: {closure.height}")
    for status, count in sorted(_closure_status_counts(closure).items()):
        typer.echo(f"{status}: {count}")

    for row in closure.iter_rows(named=True):
        typer.echo(
            "  "
            f"{row['complex_id']} "
            f"{row['chain']} "
            f"{row['target_species']} "
            f"signal={row['signal_direction']} "
            f"closure={row['closure_status']}"
        )

    typer.echo(f"Wrote curated control closure -> {output_csv}")
    typer.echo(f"Wrote curated control closure markdown -> {output_md}")


if __name__ == "__main__":
    app()
