# Longevity PPI — cross-species protein interaction analysis

## The big picture

Some species live extraordinarily long: naked mole-rats (~30 yr), bowhead whales (~200 yr),
and certain bats (~40 yr). One hypothesis is that their **protein-protein interactions**
have diverged — key interactions are maintained, broken, or rewired compared to short-lived
species (mouse ~3 yr, human ~80 yr).

This repo tackles two complementary questions:

### 1. Which proteins should we investigate? (Candidate & interactome analysis)

Before any structural modelling, we need a defensible candidate list. Tasks A-D build this:
- Curate ~30 longevity-relevant proteins across 8 functional categories
- Map their **full interactome** from OmniPath (STRING + BioGRID + IntAct + 100 more databases)
- Flag **hub proteins** (>15 partners) that risk network-wide incompatibility if ported
- Score candidates on 10 wet-lab feasibility criteria (size, membrane, glycosylation, etc.)
- Generate a **breakage taxonomy** — which interactions should be maintained, broken, or
  rewired in long-lived species — for human curation

This is pure data science. Runs on a laptop, no GPU, no API keys.

### 2. Do protein interfaces actually diverge? (Embedding signal check)

For the top candidates, we test the interface divergence hypothesis computationally:
- Take a known protein complex with a solved 3D structure (known interface residues)
- Embed each chain with ESM C (protein language model, via Biohub REST API)
- Swap one chain for the ortholog from a long-lived species, re-embed
- Check whether the embedding **shift concentrates at interface residues** — more than at
  non-interface residues, and more than for known non-interacting pairs

If yes, that's a signal that the interface is under cross-species divergence pressure.
The deliverable is an enrichment table + plots with two negative controls.

## Prerequisites

You need **two things**:

1. **Python 3.13+** — check with `python3 --version`
2. **uv** — a fast Python package manager (replaces pip/conda/virtualenv):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

That's it. No conda environments, no Docker, no system-level packages.

## Setup (2 minutes)

```bash
# Clone the repo
git clone https://github.com/longevity-genie/longevity-port-pipelines.git
cd longevity-port-pipelines

# Install all dependencies into a local .venv (automatic, no activation needed)
uv sync
```

> **What is `uv run`?** It runs a command inside the project's virtual environment without
> you having to activate it. Think of it as `conda run` but instant. Every command in this
> README uses `uv run <name>`.

---

## Candidate preparation (Tasks A-D)

Run these in order. Each command writes CSV/parquet files to `data/output/`.

### Step 1 — Generate candidate protein list

```bash
uv run candidates
```

**What it does:** Writes a curated list of 32 longevity-relevant human proteins across 8
functional categories to `data/output/candidates.csv`.

**What you get:**

```
gene_name  uniprot_id  category                     description
SIRT1      Q96EB6      pro-longevity                NAD-dependent deacetylase, master metabolic sensor
TP53       P04637      dna-repair                   Tumor suppressor, genome guardian
HAS2       Q92819      ecm/hyaluronan               Hyaluronan synthase 2, NMR high-MW-HA producer
CIRBP      Q14011      stress-response/cold-shock   Cold-inducible RNA-binding protein
CGAS       Q8N884      inflammation/cGAS-STING      Cyclic GMP-AMP synthase, cytosolic DNA sensor
...        ...         ...                          ...
```

**Categories:** pro-longevity (7), DNA repair (5), inflammation/cGAS-STING (4),
proteostasis (4), mitochondrial stress (3), senescence (3), ECM/hyaluronan (3),
stress response/cold shock (3).

> **Want to add your own proteins?** Edit `src/longevity_port_pipelines/stages/candidates.py`
> and add a `CandidateProtein(...)` entry. You need the gene name and UniProt ID
> (look it up at [uniprot.org](https://www.uniprot.org/)).

### Step 2 — Fetch interactome data

```bash
uv run interactome
```

**What it does:** Queries [OmniPath](https://omnipathdb.org/) — a meta-database that
aggregates STRING, BioGRID, IntAct, Reactome, SIGNOR, and 100+ other sources — for every
candidate protein in one bulk API call. Then fetches UniProt annotations (molecular weight,
subcellular location, glycosylation) for each protein.

**What you get (2 files):**

`data/output/interactome.csv` — one row per candidate:

```
gene_name  n_partners  is_hub  databases                           top_partners
SIRT1      248         true    BioGRID, IntAct, SIGNOR, ...        FOXO3, TP53, NFE2L2, ...
CIRBP      18          true    OmniPath, SIGNOR, ...               RBM3, EIF4G1, ...
```

`data/output/interactome_partners.parquet` — full interaction list (one row per pair).

**Key concept — hub proteins:** Proteins with >15 interaction partners are flagged as
"hubs". Porting a hub protein across species risks destabilising its entire interaction
network (the "mTOR-like rewiring" problem). Hubs aren't excluded — they're just scored
lower in the validation step.

### Step 3 — Generate breakage taxonomy table

```bash
uv run breakage-table
```

**What it does:** Creates a table crossing each candidate protein with each target species,
listing known functional and regulatory/degradation partners.

**What you get:** `data/output/breakage_taxonomy.csv`

```
protein  species          functional_partners  regulatory_partners  desired_interaction_state
SIRT1    naked_mole_rat   FOXO3, TP53, ...     MDM2, UBE2I, ...     (fill in)
SIRT1    bowhead_whale    FOXO3, TP53, ...     MDM2, UBE2I, ...     (fill in)
HAS2     naked_mole_rat   CD44, RHAMM, ...                          (fill in)
```

**Your job:** Fill in the `desired_interaction_state` column with one of:
- `maintained` — this interaction should be preserved in the long-lived species
- `broken` — this interaction should be disrupted (e.g., pro-aging pathway)
- `rewired` — the interaction changes partners or strength

This is the biological hypothesis — the computational pipeline then tests it.

### Step 4 — Score candidates + generate protocol

```bash
uv run validation-protocol
```

**What it does:** Scores each candidate on 10 binary criteria and generates a prioritised
ranking plus SVG plots.

**Scoring criteria (10 points max):**

| # | Criterion | Why it matters |
|---|-----------|---------------|
| 1 | Has AlphaFold structure | Can we model it? |
| 2 | Has human ortholog | Always true (we start from human) |
| 3 | Has known interactors | Is there a network to analyse? |
| 4 | Not a hub (<=15 partners) | Hubs risk network-wide side effects |
| 5 | Assay-feasible (soluble, <80 kDa) | Can we test it in the lab? |
| 6 | Has breakage hypothesis | Did you fill in the breakage table? |
| 7 | Cell-free expressible | Works in Adaptyv's cell-free system? |
| 8 | Under 80 kDa | Size constraint for cell-free expression |
| 9 | Not membrane protein | Membrane proteins are hard to express |
| 10 | No glycosylation needed | Cell-free systems can't glycosylate |

**Priority tiers:** HIGH (8-10), MEDIUM (5-7), LOW (0-4)

**What you get (4 files):**

- `data/output/validation_scores.csv` — full scored table
- `data/output/validation_protocol.md` — formatted protocol document
- `data/output/plots/priority_scores.svg` — bar chart by priority tier
- `data/output/plots/hub_vs_score.svg` — scatter: partner count vs score
- `data/output/plots/category_breakdown.svg` — mean score per category

---

## Interface embedding pipeline (Stages 1-7)

After you have your prioritised candidates, this pipeline tests whether cross-species
sequence divergence concentrates at protein-protein interfaces.

**Embeddings use the Biohub REST API** (ESM C 600M/6B) — no local GPU required.
Set your API token in `.env` (copy from `.env.template`).

```bash
uv run select              # Load PINDER PPI dataset, filter, annotate hubs
uv run orthologs           # Fetch orthologs for long-lived species
# >>> Review data/output/selection.csv and ortholog_coverage.csv <<<
uv run embed               # Per-residue embeddings via Biohub API
uv run analyze             # Enrichment analysis (interface vs non-interface)
uv run plot                # Summary plots
```

Or run all stages at once:

```bash
uv run run-pipeline                  # everything
uv run run-pipeline --pre-gpu-only   # stop after stage 4 (audit checkpoint)
```

## Data layout

The project uses three data directories with different git policies:

```
data/
├── input/          IN GIT — user-curated configuration files
│   └── custom_candidates.csv     Your custom proteins (edit this!)
│
├── interim/        GITIGNORED — cached downloads & API responses (regenerable)
│   ├── uniprot/                  Cached UniProt JSON entries (~6 MB)
│   ├── alphafold/                Cached AlphaFold DB structure checks (~300 KB)
│   ├── pinder/                   HuggingFace PINDER dataset cache (~120 MB)
│   ├── string/                   STRING interaction files
│   └── foldseek/                 Foldseek cluster data
│
└── output/         GITIGNORED — all pipeline outputs (regenerable)
    ├── candidates.csv              Task A: seed protein list (32+ proteins)
    ├── interactome.csv             Task B: interaction summary per protein
    ├── interactome_partners.parquet  Task B: all interaction pairs (~12k rows)
    ├── breakage_taxonomy.csv       Task C: protein x species table (fill in!)
    ├── validation_scores.csv       Task D: scored candidates
    ├── validation_protocol.md      Task D: protocol document
    ├── plots/
    │   ├── priority_scores.svg     Candidate priority bar chart
    │   ├── hub_vs_score.svg        Hub status vs priority scatter
    │   └── category_breakdown.svg  Score by functional category
    ├── selection.csv               Embedding pipeline: selected PPI complexes
    ├── ortholog_coverage.csv       Embedding pipeline: ortholog lookup results
    └── enrichment.parquet          Embedding pipeline: enrichment statistics
```

**What's committed vs generated:**

| File | In git? | How to regenerate |
|------|---------|-------------------|
| `data/input/custom_candidates.csv` | **YES** | Edit manually to add proteins |
| `data/interim/*` | no | Rebuilt automatically on first run (API caches) |
| `data/output/*` | no | `uv run candidates` then `uv run interactome` etc. |

## Key libraries

| Library | What it does | Why we use it |
|---------|-------------|--------------|
| [omnipath](https://omnipathdb.org/) | Aggregated PPI data | One API call covers STRING + BioGRID + IntAct + 100 more |
| [biotite](https://www.biotite-python.org/) | Structure parsing | Modern replacement for BioPython, numpy-backed |
| [polars](https://pola.rs/) | DataFrames | Faster than pandas, lazy evaluation, native parquet |
| [plotly](https://plotly.com/) + kaleido | Plots | Interactive HTML + static SVG export |
| [pydantic v2](https://docs.pydantic.dev/) | Data models | Type-safe protein/interaction records |
| [typer](https://typer.tiangolo.com/) | CLI | Each command = one function, auto-generated `--help` |
| [prefect 3](https://www.prefect.io/) | Orchestration | Optional — retry/cache for the embedding pipeline |

## Glossary (for data scientists new to bioinformatics)

| Term | Meaning |
|------|---------|
| **UniProt ID** | Unique identifier for a protein (e.g., Q96EB6 = human SIRT1). Look up at [uniprot.org](https://www.uniprot.org/) |
| **Gene symbol** | Short name for a gene (e.g., SIRT1, TP53). One gene = one protein (mostly) |
| **PPI** | Protein-protein interaction — two proteins that physically bind or functionally interact |
| **Hub protein** | A protein with many interaction partners (>15 here). Modifying it has wide network effects |
| **Ortholog** | The "same" protein in a different species (e.g., human SIRT1 vs naked mole-rat SIRT1) |
| **Interface residues** | The amino acids at the contact surface where two proteins bind |
| **OmniPath** | A meta-database that combines 100+ interaction databases into one query |
| **kDa** | Kilodaltons — unit of protein mass. 80 kDa is roughly a "large" single-chain protein |
| **Glycosylation** | Sugar molecules attached to a protein. Cell-free expression systems can't add these |
| **Parquet** | A compressed columnar file format. Like CSV but typed and much smaller. Open with polars/pandas |

## Development

```bash
uv sync --group dev         # install dev dependencies
uv run ruff check src       # lint
uv run mypy src             # type check
uv run pytest               # tests
```

## Further reading

- [BUILD_BRIEF.md](BUILD_BRIEF.md) — the original design brief
- [RESOURCES.md](RESOURCES.md) — data source inventory with freshness checks
- [AGENTS.md](AGENTS.md) — conventions for AI-assisted development
