# AGENTS.md

Canonical context for any AI agent (Claude Code, Cursor, Codex) working on this repo.
CLAUDE.md is a symlink to this file — edit THIS file only.

## What this project is

A fast computational signal check for a longevity hypothesis: do protein–protein
INTERFACES diverge in long-lived species (naked mole-rat, bowhead whale, bats) in ways
that change key interactions (maintained / broken / rewired) vs short-lived mouse/human?

Method: take a known complex with a real structure (so we know the true interface),
embed its chains with a protein language model, swap one chain for the long-lived-species
ortholog, re-embed, and measure whether the embedding shift concentrates at interface
residues — more than at non-interface residues, and more than for known non-interacting
pairs. Enrichment at the interface = the signal.

This is a PROTOTYPE for preliminary data, ~1 week. Bias toward downloading precomputed
assets over building pipelines. We assemble; we don't curate databases from scratch.

## Architecture

Prefect 3 flow, one task per stage: load_pinder → load_foldseek_clusters →
load_string_hubs → fetch_orthologs → embed → analyze → plot. Tasks orchestrate; the real
logic lives in plain typed modules under src/longevity_port_pipelines/stages/. The flow
lives in flow.py; tasks are thin wrappers. The embed stage calls the remote Biohub ESMC service through the Biohub ESM SDK — keep its task thin. The model is not run locally; torch may be imported only because the SDK can return torch tensors that we convert to NumPy arrays.

Beyond the seven core-flow stages, src/longevity_port_pipelines/stages/ also holds
supporting modules that are invoked by the candidate-prep CLI commands and pipeline.py
rather than the Prefect flow:
- candidates / interactome / breakage_table / validation_protocol — Tasks A–D (CLI commands below).
- interface / mapped_interface / interaction_outcomes — interface residue mapping and maintained/broken/rewired calls.
- negative_controls + the NEGATOME suite (negatome_seed / negatome_inputs / negatome_curation / negatome_controls / negatome_analyze) — the two negative controls.
- scorecard / validation_plan / validation_closure — candidate scoring and validation-closure reporting.
These are plain typed modules, not separate entry points; the registered CLI is the list below.

We chose Prefect over MageAI: the latest mage-ai (0.9.79) force-pins legacy deps
(numpy 1.x, pydantic 2.9, typer 0.9) that conflict with our modern stack. Prefect 3
co-resolves cleanly with numpy 2.x / polars / pydantic 2.13.

Data layout:
- data/input — user-curated files, committed to git (custom_candidates.csv)
- data/interim — cached downloads & API responses, gitignored (PINDER, UniProt, AlphaFold, STRING, Foldseek)
- data/output — pipeline outputs, gitignored (CSVs, embeddings, enrichment tables, plots)

Key data sources (details + freshness in docs/RESOURCES.md):
- Synthyra/PINDER (HF) — PPI pairs + structures + interface annotations. Replaces interactome ETL.
- AFDB Foldseek clusters — structural conservation filter.
- STRING v12.5 — hub/partner counts.
- OMA / UniProt — orthologs for long-lived species (PINDER has none).
- Biohub ESM C (600M/6B via the remote Biohub ESM SDK service) — the embedding model. NOT ESM-2 (outdated).
- ESMFold2 (via Biohub API) — structure prediction for ortholog chains.
- Synthyra/NEGATOME — non-interacting pairs for the negative control.

## CLI

Typer app with one command per meaningful pipeline step:

```
# --- Candidate preparation (Tasks A-D, no GPU needed) ---
uv run candidates          # Task A: generate seed list of ~30 longevity proteins
uv run interactome         # Task B: fetch interactors via OmniPath + UniProt annotations
uv run breakage-table      # Task C: breakage taxonomy table (protein x species x partners)
uv run validation-protocol # Task D: score candidates, generate protocol + SVG plots

# --- Interface embedding pipeline (GPU stages) ---
uv run select              # Stages 1-3: load PINDER, filter, annotate hubs
uv run orthologs           # Stage 4: fetch orthologs for long-lived species
uv run embed               # Stage 5: ESM C embeddings (Biohub API)
uv run analyze             # Stage 6: enrichment analysis
uv run plot                # Stage 7: generate Plotly figures
uv run run-pipeline        # All stages (or --pre-gpu-only for stages 1-4)

# --- Reporting ---
uv run render-poster       # Render docs/poster/poster.html to PNG via headless Chrome
```

Every new pipeline step gets its own direct entry point — no umbrella CLI.

## Conventions

- Env/deps: uv (with uv_build backend). Python 3.13+.
- Secrets/config: all env variables live in `.env` (gitignored). `.env.template` is the
  committed schema — copy to `.env` and fill in values. Load with
  `python-dotenv` (`load_dotenv()`) at CLI entry points. Never hard-code tokens.
- CLI: typer. Each meaningful operation is a separate command, not a flag.
- Full type hints. pydantic v2 for data records.
- Pre-push checks: run ALL of `ruff format`, `ruff check`, `mypy`, and `pytest` clean
  before pushing — not just `ruff check`. `ruff check` and `ruff format` are separate;
  CI runs both, so a `ruff check`-only pass can still fail CI on formatting.
- Logging: structured `logging`, not print.
- Polars LazyFrame is the default dataframe type. Never call `.collect()` unless you
  genuinely need eager evaluation (row-by-row iteration, final output write). Pass
  LazyFrames between stages; let polars optimize the query plan.
- Default output format is parquet (typed, compressed). Use CSV only for files that
  a human needs to eyeball directly (selection audit, ortholog coverage).
- Plotting: plotly. No matplotlib.
- Cache all network fetches to data/interim/. Prefect handles pipeline-level retries/caching.
- Real logic in src/longevity_port_pipelines/stages/ modules; Prefect tasks stay thin
  wrappers. Modules are the product — they run standalone via the per-stage CLI commands;
  the Prefect flow (flow.py) just sequences them with retries + a run graph.

## Testing

- Prefer integration tests with real (or realistic synthetic) inputs over unit tests
  that just restate constructor arguments. A test that only asserts pydantic stored
  what you passed in tests pydantic, not this project — delete it.
- Every test must exercise real logic: numerical computation, I/O behaviour, parsing,
  or a non-trivial code path. If removing the test wouldn't risk missing a bug, it
  has no value.
- Don't assert hardcoded counts of config constants (e.g. `len(SPECIES) == 3`) —
  these break on any addition and verify nothing.
- For scientific stages (enrichment, statistics, alignment), test with synthetic data
  that has a known ground truth, then assert the statistical properties hold.
- For I/O stages (PDB parsing, API calls, file caching), use small fixture files
  or `tmp_path` and verify the actual behaviour, not just that the function returns.

## Non-negotiables

- Two negative controls (shuffled mask + NEGATOME). Enrichment must beat both. This is
  what makes the result believable — never drop it.
- Write selection + ortholog-coverage CSVs BEFORE the GPU stage so a human can audit and
  curate the ~5–10 v1 complexes. Don't run the whole dataset.
- Flag predicted (vs experimental) structures as lower confidence — SaProt's 3Di tokens
  inherit prediction error for non-model species.

## When to ask the human

Ask on real forks: model/threshold choices, which complexes, ambiguous ortholog hits.
Don't ask about routine plumbing — just build it.

## Doc sync

AGENTS.md is canonical. CLAUDE.md symlinks to it. A pre-commit hook re-creates the symlink
if it's missing (e.g. after a Windows checkout). Change conventions HERE; never let the
two files diverge.
