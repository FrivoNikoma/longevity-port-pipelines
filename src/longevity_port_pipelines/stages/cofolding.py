"""
Stage: cofolding
----------------
For top-ranked candidates from enrichment.parquet, submit cross-species
protein-protein complex predictions to the Boltz API and store the
structural confidence metrics (iptm, complex_iplddt, binding_confidence, etc.).

This is Stage 3 "Compatibility classification" from the LongevityPort plan:
    predict the cross-species complex (human partner chain + ortholog of the
    analyzed chain) and classify the interaction as maintained /
    functionally_broken / incompatible.

Cross-species logic
-------------------
A complex like "6b2e__A1_P54646--6b2e__B1_O43741" has two human chains:
    receptor = P54646  (first half, "A1_P54646")
    ligand   = O43741  (second half, "B1_O43741")

For each enrichment row we know which chain was analyzed (`chain`) and which
species we compare against (`target_species`). We co-fold:
    - the analyzed chain, replaced by its ortholog from target_species
    - the partner chain, kept as the human sequence
This asks Boltz whether the ortholog still docks against the human partner.

Ortholog sequences come from ortholog_coverage.csv (column target_sequence),
keyed on (source_uniprot, target_species_taxid). The human partner sequence is
fetched from UniProt.

Usage:
    uv run cofolding                          # top 10 by enrichment_ratio
    uv run cofolding --top-n 20               # top 20
    uv run cofolding --test                   # internal synthetic results, no API
    uv run cofolding --complex 6b2e__A1_P54646--6b2e__B1_O43741 --top-n 1

Output:
    data/output/cofolding_results.parquet     — one row per (complex, chain, species)
    data/output/cofolding_results.csv         — same, human-readable
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any

import polars as pl
import typer
from dotenv import load_dotenv

# Load .env so BOLTZ_API_KEY is available when this module runs standalone.
load_dotenv()

app = typer.Typer(help="Boltz API co-folding stage for cross-species PPI compatibility.")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_OUTPUT = Path("data/output")
ENRICHMENT_PATH = DATA_OUTPUT / "enrichment.parquet"
ORTHOLOG_COVERAGE_PATH = DATA_OUTPUT / "ortholog_coverage.csv"
COFOLDING_RESULTS = DATA_OUTPUT / "cofolding_results.parquet"

# ---------------------------------------------------------------------------
# Species name -> NCBI taxid (must match config.TARGET_SPECIES / REFERENCE_SPECIES)
# ---------------------------------------------------------------------------
SPECIES_TAXID = {
    "human": 9606,
    "naked_mole_rat": 10181,
    "bowhead_whale": 27622,
    "myotis_lucifugus": 59463,
    "mouse": 10090,
}

# ---------------------------------------------------------------------------
# Compatibility classification thresholds
# (tune after you have a few real predictions to calibrate)
# ---------------------------------------------------------------------------
MAINTAINED_IPTM_THRESHOLD = 0.75  # iptm >= this -> likely maintained
BROKEN_IPTM_THRESHOLD = 0.45  # iptm < this -> likely broken
BINDING_CONFIDENCE_HIGH = 0.70  # Boltz docs: 0.7+ is high-confidence


def classify_interaction(iptm: float, binding_confidence: float | None) -> str:
    """
    Binary structural filter: maintained / functionally_broken / incompatible / uncertain.

    Current models do not reliably predict absolute binding affinity, so this is
    a pass/fail filter only (as noted in the LongevityPort design doc).
    """
    if iptm >= MAINTAINED_IPTM_THRESHOLD:
        return "maintained"
    if iptm < BROKEN_IPTM_THRESHOLD:
        if binding_confidence is not None and binding_confidence < 0.5:
            return "incompatible"
        return "functionally_broken"
    return "uncertain"


# ---------------------------------------------------------------------------
# complex_id parsing
# ---------------------------------------------------------------------------


def parse_complex_id(complex_id: str) -> tuple[str | None, str | None]:
    """
    Parse a complex_id into (receptor_uniprot, ligand_uniprot).

    Format: "6b2e__A1_P54646--6b2e__B1_O43741"
            receptor side  ^^^^^^         ligand side ^^^^^^
    Returns (None, None) if it cannot be parsed.
    """
    halves = complex_id.split("--")
    if len(halves) != 2:
        return None, None

    def last_token(half: str) -> str | None:
        # half looks like "6b2e__A1_P54646"; the UniProt ID is the final _token.
        m = re.search(r"_([A-Z0-9]{6,10})$", half)
        return m.group(1) if m else None

    return last_token(halves[0]), last_token(halves[1])


# ---------------------------------------------------------------------------
# Ortholog lookup
# ---------------------------------------------------------------------------


def load_ortholog_table() -> pl.DataFrame | None:
    """Load ortholog_coverage.csv, or return None if it does not exist."""
    if not ORTHOLOG_COVERAGE_PATH.exists():
        return None
    return pl.read_csv(ORTHOLOG_COVERAGE_PATH)


def lookup_ortholog_sequence(
    ortholog_df: pl.DataFrame,
    source_uniprot: str,
    target_taxid: int,
) -> str | None:
    """
    Find the ortholog sequence for a human protein in a target species.

    Returns the target_sequence string, or None if no ortholog is on file.
    """
    hits = ortholog_df.filter(
        (pl.col("source_uniprot") == source_uniprot)
        & (pl.col("target_species_taxid") == target_taxid)
    )
    if hits.is_empty():
        return None
    seq = hits.row(0, named=True).get("target_sequence")
    return str(seq) if seq else None


# ---------------------------------------------------------------------------
# Boltz API helpers
# ---------------------------------------------------------------------------


def get_boltz_client() -> Any:
    """Return an authenticated Boltz client. Requires BOLTZ_API_KEY in env."""
    try:
        from boltz_api import Boltz
    except ImportError as err:
        typer.echo(
            "boltz_api not installed. Run:\n  uv add boltz-api\nor:\n  pip install boltz-api",
            err=True,
        )
        raise typer.Exit(1) from err

    api_key = os.environ.get("BOLTZ_API_KEY")
    if not api_key:
        typer.echo(
            "BOLTZ_API_KEY not set. Add it to your .env file:\n  BOLTZ_API_KEY=your_key_here",
            err=True,
        )
        raise typer.Exit(1)

    return Boltz(api_key=api_key)


def submit_ppi_prediction(
    client: Any,
    seq_a: str,
    seq_b: str,
    num_samples: int = 1,
) -> dict[str, Any]:
    """
    Submit a protein-protein co-folding prediction to Boltz API.

    Chain A and chain B are the two partners of the complex. Chain B is marked
    as the binder for binding-metric purposes.

    Returns the prediction result dict with metrics.
    """
    prediction_input = {
        "entities": [
            {"type": "protein", "value": seq_a, "chain_ids": ["A"]},
            {"type": "protein", "value": seq_b, "chain_ids": ["B"]},
        ],
        "binding": {
            "type": "protein_protein_binding",
            "binder_chain_ids": ["B"],
        },
        "num_samples": num_samples,
    }

    prediction = client.predictions.structure_and_binding.start(
        model="boltz-2.1",
        input=prediction_input,
    )

    # Poll until done.
    while prediction.status not in ("succeeded", "failed"):
        time.sleep(5)
        prediction = client.predictions.structure_and_binding.retrieve(prediction.id)

    if prediction.status == "failed":
        raise RuntimeError(f"Boltz prediction failed: {prediction.error}")

    best = prediction.output.best_sample
    metrics = best.metrics
    binding = prediction.output.binding_metrics

    return {
        "prediction_id": prediction.id,
        "structure_confidence": metrics.structure_confidence,
        "ptm": metrics.ptm,
        "iptm": metrics.iptm,
        "complex_plddt": metrics.complex_plddt,
        "complex_iplddt": metrics.complex_iplddt,
        "complex_pde": metrics.complex_pde,
        "complex_ipde": metrics.complex_ipde,
        "binding_confidence": binding.binding_confidence if binding else None,
        "structure_url": best.structure.url if best.structure else None,
    }


def make_test_result(name: str) -> dict[str, Any]:
    """Return a fake result for --test mode (no API call, no credits used)."""
    import random

    rng = random.Random(name)
    iptm = rng.uniform(0.3, 0.95)
    bc = rng.uniform(0.4, 0.95)
    return {
        "prediction_id": f"test_{name[:8]}",
        "structure_confidence": round(rng.uniform(0.6, 0.98), 3),
        "ptm": round(rng.uniform(0.6, 0.95), 3),
        "iptm": round(iptm, 3),
        "complex_plddt": round(rng.uniform(0.7, 0.97), 3),
        "complex_iplddt": round(rng.uniform(0.6, 0.92), 3),
        "complex_pde": round(rng.uniform(0.8, 3.5), 3),
        "complex_ipde": round(rng.uniform(1.0, 5.0), 3),
        "binding_confidence": round(bc, 3),
        "structure_url": None,
    }


# ---------------------------------------------------------------------------
# Sequence fetching
# ---------------------------------------------------------------------------


def fetch_sequence_uniprot(uniprot_id: str) -> str | None:
    """
    Fetch the canonical FASTA sequence for a UniProt ID.

    UniProt is a protein database; each protein has a unique ID
    (e.g. P04637 = human p53). Returns the amino-acid sequence as a plain
    string, or None on failure.
    """
    import urllib.request

    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            fasta = resp.read().decode()
        lines = [line for line in fasta.splitlines() if not line.startswith(">")]
        seq = "".join(lines)
        return seq or None
    except Exception as exc:
        typer.echo(f"    Warning: could not fetch {uniprot_id} from UniProt ({exc}).", err=True)
        return None


# ---------------------------------------------------------------------------
# Build the cross-species pair for one enrichment row
# ---------------------------------------------------------------------------


def build_cross_species_pair(
    complex_id: str,
    chain: str,
    target_species: str,
    ortholog_df: pl.DataFrame,
) -> tuple[str, str] | None:
    """
    Assemble the (chain A, chain B) sequences for a cross-species prediction.

    The analyzed chain is replaced by its ortholog in target_species; the
    partner chain stays human. Returns (seq_a, seq_b) or None if any piece is
    missing.
    """
    receptor_up, ligand_up = parse_complex_id(complex_id)
    if not receptor_up or not ligand_up:
        typer.echo(f"    Could not parse UniProt IDs from {complex_id}.", err=True)
        return None

    target_taxid = SPECIES_TAXID.get(target_species)
    if target_taxid is None:
        typer.echo(f"    Unknown species '{target_species}'.", err=True)
        return None

    # Decide which chain is analyzed (gets the ortholog) and which is the
    # human partner.
    if chain == "receptor":
        analyzed_up, partner_up = receptor_up, ligand_up
    elif chain == "ligand":
        analyzed_up, partner_up = ligand_up, receptor_up
    else:
        typer.echo(f"    Unknown chain '{chain}'.", err=True)
        return None

    ortholog_seq = lookup_ortholog_sequence(ortholog_df, analyzed_up, target_taxid)
    if not ortholog_seq:
        typer.echo(
            f"    No ortholog for {analyzed_up} in {target_species} (taxid {target_taxid}).",
            err=True,
        )
        return None

    partner_seq = fetch_sequence_uniprot(partner_up)
    if not partner_seq:
        return None

    # Chain A = human partner, Chain B = ortholog of analyzed chain (the binder).
    return partner_seq, ortholog_seq


# ---------------------------------------------------------------------------
# Main command
# ---------------------------------------------------------------------------


@app.command()
def main(
    top_n: int = typer.Option(
        10, "--top-n", help="How many top candidates to process (ranked by enrichment_ratio)."
    ),
    complex_id: str | None = typer.Option(
        None, "--complex", help="Run only this complex ID (matches complex_id column)."
    ),
    species: str | None = typer.Option(None, "--species", help="Run only this target species."),
    test: bool = typer.Option(
        False, "--test", help="Test mode: internal synthetic results, no API calls."
    ),
    num_samples: int = typer.Option(
        1,
        "--num-samples",
        help="Number of structure samples per prediction (more = more credits).",
    ),
) -> None:
    """
    Co-fold cross-species protein complexes via Boltz API and classify
    interactions as maintained / functionally_broken / incompatible / uncertain.
    """
    if not ENRICHMENT_PATH.exists():
        typer.echo(
            f"Enrichment file not found at {ENRICHMENT_PATH}.\n"
            "Run the embedding pipeline first:\n"
            "  uv run embed\n  uv run analyze",
            err=True,
        )
        raise typer.Exit(1)

    df = pl.read_parquet(ENRICHMENT_PATH)

    # Keep only rows where the interface significantly diverges -- these are
    # the candidates for a "remodeled interaction". signal_class is a future
    # column; for now we take all rows.
    if "signal_class" in df.columns:
        candidates = df.filter(
            pl.col("signal_class").is_in(
                [
                    "interface_divergent",
                    "interface_divergent_not_significant",
                ]
            )
        )
    else:
        candidates = df

    if complex_id:
        candidates = candidates.filter(pl.col("complex_id") == complex_id)
    if species:
        candidates = candidates.filter(pl.col("target_species") == species)

    if "enrichment_ratio" in candidates.columns:
        candidates = candidates.sort("enrichment_ratio", descending=True)
    candidates = candidates.head(top_n)

    if candidates.is_empty():
        typer.echo("No candidates found after filtering. Check your enrichment.parquet.", err=True)
        raise typer.Exit(1)

    typer.echo(f"\n{'[TEST MODE] ' if test else ''}Processing {len(candidates)} candidates...\n")

    # Load ortholog table and Boltz client only when running for real.
    ortholog_df = None if test else load_ortholog_table()
    if not test and ortholog_df is None:
        typer.echo(
            f"Ortholog coverage not found at {ORTHOLOG_COVERAGE_PATH}. Run `uv run orthologs`.",
            err=True,
        )
        raise typer.Exit(1)

    client = None if test else get_boltz_client()

    results = []

    for row in candidates.iter_rows(named=True):
        complex_id_val = row.get("complex_id", "unknown")
        chain_val = row.get("chain", "?")
        source_species = row.get("source_species", "human")
        target_species = row.get("target_species", "unknown")
        enrichment_ratio = row.get("enrichment_ratio", None)

        name = f"{complex_id_val}_{chain_val}_{target_species}"[:60]

        typer.echo(
            f"  -> {complex_id_val} / {chain_val} / {target_species}"
            + (f"  (enrichment_ratio={enrichment_ratio:.3f})" if enrichment_ratio else "")
        )

        try:
            if test:
                api_result = make_test_result(name)
            else:
                assert ortholog_df is not None  # for type-checkers; guarded above
                pair = build_cross_species_pair(
                    complex_id_val, chain_val, target_species, ortholog_df
                )
                if pair is None:
                    typer.echo(f"    Skipping {name}: could not build cross-species pair.")
                    continue
                seq_a, seq_b = pair

                typer.echo("    Submitting to Boltz API...")
                api_result = submit_ppi_prediction(client, seq_a, seq_b, num_samples=num_samples)

            iptm = api_result["iptm"]
            bc = api_result["binding_confidence"]
            classification = classify_interaction(iptm, bc)

            result_row = {
                "complex_id": complex_id_val,
                "chain": chain_val,
                "source_species": source_species,
                "target_species": target_species,
                "enrichment_ratio": enrichment_ratio,
                "boltz_classification": classification,
                **api_result,
            }
            results.append(result_row)

            typer.echo(
                f"    iptm={iptm:.3f}  binding_conf={bc:.3f}  -> {classification}"
                if bc is not None
                else f"    iptm={iptm:.3f}  -> {classification}"
            )

        except Exception as exc:
            typer.echo(f"    ERROR for {name}: {exc}", err=True)
            results.append(
                {
                    "complex_id": complex_id_val,
                    "chain": chain_val,
                    "source_species": source_species,
                    "target_species": target_species,
                    "enrichment_ratio": enrichment_ratio,
                    "boltz_classification": "error",
                    "error_message": str(exc),
                }
            )

    if not results:
        typer.echo("No results to save.", err=True)
        raise typer.Exit(1)

    DATA_OUTPUT.mkdir(parents=True, exist_ok=True)
    out_df = pl.DataFrame(results)
    out_df.write_parquet(COFOLDING_RESULTS)
    out_df.write_csv(COFOLDING_RESULTS.with_suffix(".csv"))

    typer.echo(f"\nSaved {len(results)} rows to {COFOLDING_RESULTS}")

    if "boltz_classification" in out_df.columns:
        summary = (
            out_df.group_by("boltz_classification")
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
        )
        typer.echo("\nClassification summary:")
        for r in summary.iter_rows(named=True):
            typer.echo(f"  {r['boltz_classification']:30s} {r['count']}")

    typer.echo("\nDone.")


if __name__ == "__main__":
    app()
