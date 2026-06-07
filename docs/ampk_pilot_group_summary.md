# AMPK pilot: species-group summary

## Technical status

The AMPK pilot validates the current interface-aware evolutionary embedding pipeline.

The current workflow does the following:

1. Selects protein-protein complexes from PINDER.
2. Maps PINDER chain identifiers such as A1/B1 to PDB-like chain identifiers A/B.
3. Computes per-residue ESMC embedding shifts between human proteins and orthologs.
4. Compares embedding shifts on protein-protein interface residues versus non-interface residues.
5. Estimates enrichment ratios and compares them against shuffled controls.
6. Adds species-group annotation to separate long-lived species from short-lived controls.

The current AMPK run produced:

- 30 enrichment rows.
- 0 skipped rows due to missing interface.
- 0 skipped rows due to missing mapping.
- 0 skipped rows due to missing embedding.
- A grouped output file: `data/output/enrichment_group_summary.csv`.
- An annotated row-level output file: `data/output/enrichment_top_with_fdr_and_groups.csv`.

## Biological interpretation

The AMPK pilot shows that evolutionary embedding shifts between human proteins and orthologs are enriched at protein-protein interfaces.

This is biologically meaningful because protein-protein interfaces are functional surfaces. If embedding shifts concentrate at interfaces, the differences are more likely to affect interaction geometry, regulatory coupling, partner recognition, or allosteric signaling than if the shifts were uniformly distributed across the protein.

However, the current grouped analysis does not yet support a strong longevity-specific interpretation.

Current group-level result:


| species group         | mean enrichment ratio | median enrichment ratio | count |
| --------------------- | --------------------- | ----------------------- | ----- |
| long_lived_small_body | 1.4216                | 1.4552                  | 20    |
| short_lived_control   | 1.3978                | 1.4380                  | 10    |
| long_vs_short_delta   | 0.0238                | NA                      | 30    |


The long-lived group is only slightly above the short-lived control group.

Therefore, the AMPK result should be interpreted as:

> A reproducible interface-localized evolutionary embedding shift, but not yet as evidence for a longevity-specific AMPK adaptation.

## Why this is useful

This result is still valuable because it demonstrates that the pipeline can detect non-random localization of evolutionary embedding shifts at protein-protein interfaces.

It also shows why short-lived controls are essential. Without the mouse control, the strong interface enrichment in naked mole-rat and Myotis lucifugus could be overinterpreted as a longevity signal. The grouped analysis shows that similar enrichment can also appear in a short-lived mammalian control.

Biologically, this means that AMPK interfaces are evolutionarily sensitive, but the current pilot does not yet show that this sensitivity is specific to long-lived species.

## Next biological direction

The next candidate set should be selected to test a clearer longevity mechanism.

Recommended next module:

```text
sirt6_dna_repair

```

Rationale:

- SIRT6 is directly connected to DNA double-strand break repair.
- DNA repair capacity is a major comparative-longevity mechanism.
- Species differences in SIRT6 activity have known functional relevance.
- The expected biological scenario is not simple interaction loss, but maintained or enhanced repair-related function.

The next analytical goal is to ask whether SIRT6-centered interfaces show stronger long-lived versus short-lived separation than the AMPK pilot.

## Biological meaning of the next step

AMPK is a broad energy-sensing and signaling module. It is important for aging biology, but it is also highly conserved and broadly involved in normal metabolic regulation. Therefore, interface shifts in AMPK may reflect general mammalian divergence rather than a longevity-specific adaptation.

SIRT6 is a better next benchmark because it is closer to a concrete longevity mechanism: genome maintenance. If long-lived species have evolved improved DNA double-strand break repair, then SIRT6 and its repair-related partners are a more direct place to search for longevity-associated interface changes.

The biological question becomes:

> Are SIRT6-related interaction surfaces in long-lived species shifted in a way that is stronger or more structured than in short-lived controls?

If yes, this would support the broader LongevityPort hypothesis: long-lived species may encode transferable or engineerable changes in signaling and repair proteins, especially at functional interfaces.