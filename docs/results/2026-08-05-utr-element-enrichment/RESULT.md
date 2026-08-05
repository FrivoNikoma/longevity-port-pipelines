# Which element? The proximal 3' UTR conservation is not miRNA sites or AREs

The cell-cycle 3' UTR conservation is proximal
([utr-positional](../2026-08-05-utr-positional/RESULT.md)). This tests *what* the conserved
positions are, comparing the two obvious post-transcriptional dosage levers side by side.

## Method

Every human 3' UTR position of each cell-cycle gene is classified as **miRNA** (inside a
canonical 7mer-m8 target site of one of 108 broadly conserved human miRNA families, TargetScan),
**ARE** (inside an ATTTA AU-rich core, not a miRNA site), or **background** (neither). Each
species is aligned to the human UTR; per species, per class, divergence is the mean
mismatch/gap over that class' positions. Pooled across the cell-cycle module, each class'
per-species mean divergence is regressed on lifespan + mass (PGLS)
(`scripts/analyze_utr_element_enrichment.py`). Comparing the three classes side by side isolates
which element type - if any - carries the conservation.

## Results

| Position class | n species | PGLS lifespan p | slope | direction |
|---|---|---|---|---|
| background (neither) | 57 | **0.035** | −0.038 | conserve |
| miRNA site | 57 | 0.14 | −0.034 | conserve |
| ARE (ATTTA) | 57 | 0.093 | −0.044 | conserve |

**No element type carries the signal.** All three classes conserve with **similar effect
sizes** (slopes −0.034 to −0.044), and the miRNA-site and ARE positions are **not** more
lifespan-conserved than background — if anything background, which has the most positions, is
the most significant. The proximal 3' UTR conservation in long-lived species is **diffuse
across the sequence**, not concentrated on canonical miRNA target sites or ARE stability motifs.

## Interpretation and bounds

The proximal-3' UTR conservation is a broad, sequence-wide property, not the footprint of a
discrete canonical element. This confirms and extends the earlier 22-species finding (the
whole-UTR conservation was not in miRNA sites) to the 57-species cell-cycle module, and rules
out AREs as well. The conserved feature is the **proximal 3' UTR region itself** - plausibly
RNA secondary structure, non-canonical or other RNA-binding-protein sites, overall composition,
or general regulatory constraint on the stop-proximal region - rather than the two textbook
motif classes.

Bounds: only canonical **7mer-m8** miRNA sites of **broadly conserved** families and the
**ATTTA** ARE core were scored; non-canonical miRNA pairing, poorly conserved families, and
longer / clustered ARE definitions are not captured, and a real but weaker element-specific
component could hide under those definitions. This is a position-level comparative analysis on
the module; it localises the conservation to the proximal region and shows it is not the two
obvious motifs, but does not yet identify the responsible feature.

## Reproducing

```
uv run python scripts/analyze_utr_element_enrichment.py   # -> utr_element_enrichment.{json,png}
```

Requires the panel UTRs, TimeTree tree, and TargetScan miR_Family_Info.txt (all under
data/interim, gitignored). No Biohub credits used.
