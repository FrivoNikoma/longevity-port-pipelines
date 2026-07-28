# SIRT6 DNA-repair panel — higher-powered 5×4 longevity-divergence contrast

Date: 2026-07-28
Candidate set: `sirt6_dna_repair`
Status: **technical checkpoint / preliminary result — not a validated biological claim.**
All three controls applied (shuffled-mask + NEGATOME + cross-lineage convergence).
Supersedes the 3×3 checkpoint in `../2026-07-28-sirt6-panel-longevity-contrast/` (same panel, more species).

## Summary

We re-ran the interface-embedding pipeline on the SIRT6 DNA-repair panel at **higher statistical
power**: **5 long-lived** species (elephant, naked mole-rat, *Myotis lucifugus*, **Damaraland
mole-rat**, **blind mole-rat**) vs **4 short-lived** (mouse, rat, hamster, **guinea pig**), human
as reference. The two added long-lived species are independent subterranean-rodent lineages
(*Fukomys*, *Nannospalax*) distinct from the naked mole-rat (*Heterocephalus*), which lets us test
cross-lineage **convergence**, not just a group-mean difference.

**Headline: the panel-wide negative result holds and strengthens.** Across **26 interfaces**,
**0 survive Benjamini-Hochberg FDR** (min q = 0.71). The extra power did exactly what it should —
the Mann-Whitney floor dropped from p = 0.100 (3×3) to ~0.016 (5×4), and one interface (Ku80/8ag5)
did reach nominal p = 0.032 — but that single lead then fails **all three** controls. Interface
divergence in this panel is species-general, not longevity-linked, and the conclusion is now robust
to the "underpowered by design" caveat that qualified the 3×3 checkpoint.

## Method (brief)

Per-residue ESM C embeddings (`esmc-300m-2024-12`, Biohub) for the human reference chain and each
ortholog. Residues aligned by BLOSUM62 global alignment; per-position L2 embedding delta.
`enrichment_ratio = mean interface delta / mean non-interface delta` (interface = 8 Å inter-chain
heavy-atom contacts on the reference structure). `> 1` = interface-divergent; `< 1` =
interface-constrained. Long-vs-short contrast per interface by Mann-Whitney U (5 vs 4, two-sided),
BH-corrected across interfaces. Three controls: (1) 1000-permutation shuffled-mask, (2) NEGATOME
coupling baseline (universal β-tubulin non-partner; `enr/neg > 1` = interface-specific),
(3) cross-lineage convergence (min-long > max-short).

## Panel & coverage

15 complexes / **26 complex × chain interfaces** yielded valid signal (236 rows written, 229 in the
9-species panel). Per-species coverage: elephant 26, naked mole-rat 25, *Myotis* 26, Damaraland 23,
blind mole-rat 25 (long); guinea pig 27, rat 27, mouse 27, hamster 23 (short). Modules: NHEJ repair
(Ku80/Ku70 8bot, Ku80 8ag5), apoptosis (caspase-3 7xn5/1i3o, Bcl-xL 2mej), p53 regulation
(ASPP2 1ycs, CBP 2l14, EP300 2mzd, p53 complexes 2h1l/2ruk/4xr8/…), inflammation (RELA/IκBα 1nfi),
kinase signaling (CDK5 7vdr, ERK2 4iz5).

Bowhead whale and Brandt's bat remain unavailable in OMA/UniProt for these proteins (real coverage
gap for the most extreme long-lived species). A few complexes are dropped by structural chain-naming
mismatches (7mo7, 1h2k, 8bhy, 4xr8, 7s68). Hamster orthologs are predicted structures.

## Results

### Long-lived vs short-lived contrast — nothing survives FDR

Interfaces ranked by contrast p (5 long vs 4 short, `enrichment_ratio`):

| Gene | PDB | Chain | mean Long | mean Short | Δ (L−S) | p | BH q |
|---|---|---|---|---|---|---|---|
| Ku80 | 8ag5 | receptor | 1.203 | 1.109 | +0.094 | 0.032 | 0.71 |
| IκBα | 1nfi | ligand | 1.029 | 1.129 | −0.100 | 0.111 | 0.71 |
| TP53 | 2h1l | ligand | 0.981 | 0.759 | +0.222 | 0.111 | 0.71 |
| Q8IW19 | 6yn1 | ligand | 1.047 | 0.950 | +0.097 | 0.114 | 0.71 |
| ERK2 | 4iz5 | receptor | 0.844 | 1.009 | −0.165 | 0.174 | 0.71 |
| TP53 | 1ycs | ligand | 0.874 | 0.769 | +0.105 | 0.190 | 0.71 |
| RELA | 1nfi | receptor | 1.320 | 1.256 | +0.064 | 0.200 | 0.71 |
| Ku80 | 8bot | receptor | 0.775 | 0.770 | +0.005 | 0.413 | 0.98 |

**0 of 26** interface contrasts significant after FDR. Directions inconsistent, magnitudes small
(|Δ| < 0.23, most < 0.1). **0 of 26** show clean cross-lineage convergence (min-long > max-short).

### The one nominal lead (Ku80 / 8ag5 receptor) fails all three controls

8ag5 (Ku80) is the only interface reaching nominal significance (p = 0.032, long-ward, Δ = +0.094).
It dies three independent ways:

| Species | Group | enrichment | enr/neg |
|---|---|---|---|
| Damaraland mole-rat | long | 1.255 | 0.90 |
| naked mole-rat | long | 1.221 | 0.85 |
| elephant | long | 1.200 | 0.79 |
| blind mole-rat | long | 1.195 | 0.70 |
| **guinea pig** | **short** | **1.154** | 0.76 |
| *Myotis lucifugus* | long | 1.142 | 0.79 |
| hamster | short | 1.126 | 0.67 |
| rat | short | 1.087 | 0.72 |
| mouse | short | 1.069 | 0.65 |

1. **FDR — FAIL:** q = 0.71.
2. **Convergence — FAIL:** guinea pig (short-lived, 1.154) sits **above** *Myotis* (long-lived,
   1.142); the groups overlap, so this is not a clean long-vs-short separation.
3. **NEGATOME — FAIL:** `enr/neg < 1` in **all 9 species** (0.65–0.90) — the Ku80 interface diverges
   *less* than the generic non-partner (tubulin) baseline, i.e. it is not interface-specific.

Note the three *independent* long-lived mole-rat lineages (naked/Damaraland/blind) do rank 1/2/4,
which is the one biologically suggestive crumb. But guinea pig — a **short-lived** hystricomorph
rodent — ranks 5th, ahead of a long-lived bat. That pattern tracks **rodent phylogeny**, not
lifespan, and is exactly why the convergence and NEGATOME controls exist. Same failure mode as the
RELA lead in the 3×3 checkpoint.

### Method validation

- **98 / 229** (interface, species) rows show significant interface localization at BH q < 0.05 —
  the embedding signal is real and broad at this power.
- Shuffled-mask control ≈ 1.00 across all rows (0.997–1.015, mean 1.002) — no sampling artifact.
- NEGATOME control populated for **229 / 229** in-panel rows (full-panel β-tubulin baseline).
- Flagship **Ku70/Ku80 (8bot, NHEJ core)** is strongly, uniformly **constrained** across all 9
  species (Ku80 enrichment 0.72–0.80, Cohen's d −0.48 to −0.73) with no longevity contrast
  (Δ = +0.005) — a robust, lifespan-independent purifying-selection signal.

## Interpretation

1. The core hypothesis — that protein-protein interfaces diverge specifically in long-lived species —
   is **not supported across 26 interfaces**, now at power sufficient to detect near-clean separation
   (floor p ≈ 0.016). Divergence, where present, is species-general.
2. The NHEJ Ku70/Ku80 interface is under strong, lifespan-independent purifying selection.
3. The single nominal lead (Ku80/8ag5) fails FDR, convergence, and NEGATOME — the same three-test
   death as the RELA lead. No interface is a longevity-portability candidate on this panel.

## Limitations

- **NEGATOME** uses a single generic partner (β-tubulin) applied uniformly; a stronger version uses
  per-source-protein NEGATOME-verified non-interactors, 2–3 partners per source.
- **Phylogenetic confounding:** three of five long-lived species are rodents; guinea pig's behavior
  shows the enrichment signal partly tracks clade. A phylogenetically-controlled contrast (e.g.
  independent-contrasts / matched sister pairs) would be the rigorous next step.
- **Embedding proxy:** L2 embedding shift is a heuristic for interface change, not binding energy.
- Single structure per interface; hamster orthologs predicted; whale/Brandt's-bat orthologs
  unavailable; AnxA2 (7nmi) enrichment ≈ 6.6 is driven by a short interface and is unstable.

## Reproduce

```bash
uv run select --candidate-set sirt6_dna_repair --count 20
uv run orthologs                                            # 5 long × 4 short coverage
uv run embed
uv run analyze                                              # enrichment.parquet (shuffled control)
cp data/input/sirt6_negatome_control_pairs.csv data/interim/negatome_control_pairs.csv
uv run analyze                                              # populates negatome_control_ratio (9 species)
```

Contrast + FDR + convergence computed from `data/output/enrichment.parquet` over
long = {elephant, naked_mole_rat, myotis_lucifugus, damaraland_mole_rat, blind_mole_rat},
short = {guinea_pig, rat, mouse, hamster}.
