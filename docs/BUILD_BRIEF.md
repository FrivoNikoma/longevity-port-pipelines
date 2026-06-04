# Build brief — cross-species interface embedding signal check

This is a brief, not a rigid spec. Use judgment; ask me when a real fork comes up
(model choice, threshold, which complexes). Don't ask about obvious plumbing — just build it.

## The core idea (read this first)

Long-lived species (naked mole-rat, bowhead whale, certain bats) resist aging. Part of
the hypothesis is that their protein–protein INTERFACES diverged in ways that change how
key proteins interact — interactions get maintained, broken, or rewired relative to
short-lived species like mouse/human.

We want a FAST computational signal check before any structure prediction or wet-lab work:

  Take a known protein complex (with a real structure — known interface residues).
  Embed each chain with a protein language model.
  Swap one chain for its ortholog from a long-lived species, re-embed.
  Ask: does the embedding SHIFT concentrate at the interface residues, more than at
  non-interface residues, and more than for known non-interacting pairs?

If yes, that's a signal that the interface is under cross-species divergence pressure —
worth escalating. That enrichment number (+ controls) is the whole deliverable.

Why this is cheap: it's minutes of GPU per protein, no docking, no folding. The expensive
parts (interactions, structures, interfaces) are already precomputed and downloadable —
see RESOURCES.md. We are assembling downloads, not building databases.

## What to build

A **Prefect 3 flow** (orchestration + reliable, retryable downloads) where each
stage is one task passing dataframes to the next:

1. load_pinder        — HF dataset Synthyra/PINDER: PPI pairs w/ sequences, bound PDBs,
                        interface annotations. This replaces all interactome ETL.
2. load_foldseek_clusters — AFDB Foldseek cluster table — keep candidates in structurally
                        conserved (tree-of-life-spanning) families. First-pass filter.
3. load_string_hubs   — STRING v12.5 per-organism file — partner counts. Deprioritize
                        hubs (>15 partners): they risk network-wide incompatibility.
4. fetch_orthologs    — OMA API (pkg: omadb), fallback UniProt REST by taxid, for the
                        long-lived species. PINDER has no orthologs; this supplies them.
5. embed              — ESM C 600M and SaProt 650M, both on the 16GB GPU. See note below.
6. analyze            — per-residue embedding delta (human vs ortholog), enrichment at
                        interface vs non-interface, with controls.
7. plot               — per-complex delta track + summary enrichment (real vs controls).

Pick ~5–10 complexes for v1 — write them to a CSV at stage 1 so I can eyeball/curate
before the GPU stages run. Don't run the whole dataset.

## Data layout

- data/input  — all downloaded / cached source data
- data/output — pipeline outputs (CSVs, embeddings, plots)

No DVC — Prefect handles orchestration, retries, and caching.

## Models (ESM-2 is outdated — do not use it for our embeddings)
- ESM C 600M (open weights, sequence-only) and SaProt 650M (structure-aware, uses Foldseek
  3Di tokens from the PDB). Run BOTH; if they disagree that's informative. Both fit 16GB.
- SaProt needs a structure to tokenize. For non-model species you'll often have only an
  AlphaFold *predicted* structure — flag those as lower confidence; the 3Di inherits any
  prediction error.

## Controls (non-optional — this is what makes the signal believable)
- Shuffled random residue mask of equal size.
- Synthyra/NEGATOME non-interacting pairs through the same pipeline.
Real interface enrichment must beat both. Report effect size + a rank test p-value.

## Orchestration guidance (Prefect 3)
- Use Prefect 3 (open source, runs locally with zero config). Each stage = a `@task`,
  the whole pipeline = a `@flow` in flow.py. Tasks give downloads retry/backoff, and the
  flow gives a run graph with logs in the Prefect UI.
- We picked Prefect over MageAI: the latest mage-ai (0.9.79) force-pins legacy deps
  (numpy 1.x, pydantic 2.9, typer 0.9) that conflict with our modern stack. Prefect 3
  co-resolves cleanly with numpy 2.x / polars / pydantic 2.13.
- IMPORTANT: the `embed` task is NOT real ETL — it's a GPU compute job. Keep it a thin
  `@task` that calls a normal, well-typed Python module
  (src/longevity_port_pipelines/embed.py). Put the real logic in plain modules; tasks just
  orchestrate. This keeps our pydantic/typed style intact.
- The modules are the product. They run standalone via the per-stage CLI commands
  (`select`, `orthologs`, `embed`, `analyze`, `plot`) with no Prefect involved at all;
  the flow just sequences the same module functions. Build modules first, wire the flow second.

## Stack conventions
- uv for env/deps, uv_build backend. Python 3.11+, full type hints, pydantic v2 models
  for data records, ruff + mypy clean, structured logging.
- All network fetches cached to data/input.

## Docs that must stay in sync (see AGENTS.md)
Maintain ONE canonical doc (AGENTS.md) with project context + conventions. CLAUDE.md is a
symlink to it so Claude Code and other agents read the same context. If you change project
conventions, edit AGENTS.md; never let the two drift.

## Definition of done
One command produces an enrichment table + summary plot showing interface enrichment vs
both controls across the picked complexes, reproducibly, with the selection and
ortholog-coverage CSVs I can audit.
