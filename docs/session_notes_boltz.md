# Session notes: Boltz cofolding integration

Working notes capturing the state of the Boltz API cofolding work, so a future
session (or contributor) can pick up without re-deriving context. This is
documentation, not a result artifact.

## Git workflow

- Development happens on a fork (`FrivoNikoma/longevity-port-pipelines`) with
  pull requests into the upstream repo (`longevity-genie/longevity-port-pipelines`).
- Remotes: `origin` = fork, `upstream` = canonical repo.
- Sync ritual before starting a new task (avoids merge commits from squash-merges):
  ```
  git fetch upstream
  git reset --hard upstream/main
  git push origin main
  git checkout -b feature/<task>
  ```
  Then work in the branch, open a PR, squash-merge. Avoid committing directly to
  main (it caused divergence/conflicts earlier).
- CI runs on `src/ tests/`: `ruff check`, `ruff format --check`, `mypy src/`,
  `pytest`. Run all four locally before pushing (`ruff check` and `ruff format`
  are separate gates).
- Environment: `uv`, Python 3.13, Windows/PowerShell.

## Boltz API

- SDK: `boltz-api==0.36.2`. Auth key in `.env` as `BOLTZ_API_KEY`.
- `client.predictions.structure_and_binding.start(model="boltz-2.1", input=...)`
  takes NO `name` argument.
- Result shape: `prediction.output.best_sample.metrics` exposes `iptm`, `ptm`,
  `complex_plddt`, `complex_iplddt`, `complex_pde`, `complex_ipde`,
  `structure_confidence`. `prediction.output.binding_metrics` is `None` in the
  test environment, carries `binding_confidence` on live keys.
- Cost: roughly $0.10 per protein-protein prediction at ~500-700 aa total.
- Test keys (prefix `sk_bc_ws_test_`) return synthetic results and spend no
  credits; live keys spend credits.

## cofolding stage

`src/longevity_port_pipelines/stages/cofolding.py` (CLI: `uv run cofolding`).

For each enrichment candidate it co-folds the analyzed chain's ortholog against
the human partner chain, then classifies the interaction as
maintained / functionally_broken / incompatible / uncertain from iptm and
binding_confidence.

- `parse_complex_id` extracts receptor/ligand UniProt IDs from `complex_id`
  (format `pdb__chainR_uniprotR--pdb__chainL_uniprotL`).
- Ortholog sequence comes from `ortholog_coverage.csv` (column `target_sequence`),
  keyed on `(source_uniprot, target_species_taxid)`.
- Human partner sequence is fetched from UniProt.
- `build_cross_species_pair` decides, based on which chain (`receptor`/`ligand`)
  was analyzed, which chain becomes the ortholog and which stays human.
- `--test` mode uses internal synthetic results (no API, no credits).
- Classification thresholds: iptm >= 0.75 maintained; iptm < 0.45 broken
  (incompatible if binding_confidence < 0.5); else uncertain. Tune after more
  real predictions.

## Free re-analysis

`scripts/analyze_saved_embeddings.py` recomputes `enrichment.parquet` from the
saved `.npy` embeddings on disk WITHOUT calling Biohub. Use this to regenerate
enrichment cheaply after fixing data issues.

## Reporting

`scripts/summarize_cofolding_contrast.py` joins ESM-C interface divergence
(`enrichment_ratio`) with Boltz structural co-folding (`iptm`,
`binding_confidence`) per target species, computes a long-lived-vs-mouse
contrast, and emits a plain-language interpretation. Output is gitignored.

## Species

TARGET_SPECIES taxids: naked_mole_rat 10181, bowhead_whale 27622,
myotis_lucifugus 59463, mouse 10090. Reference: human 9606. There is NO elephant
species in the set (the `tp53_mdm2_elephant` candidate set is named for the
biological motivation, not an elephant target species).

## Candidate sets

Defined in `data/config/candidate_sets.yaml`: ampk_pilot, sirt6_dna_repair,
tp53_mdm2_elephant, has2_cd44_nmr, igf_rheb_mtor. Switching set requires
regenerating the pipeline (select -> orthologs -> embed -> analyze), and embed
needs Biohub.

## Current scientific state (preliminary)

- Active data: `ampk_pilot` (10 PINDER complexes). Embeddings cached on disk;
  `enrichment.parquet` regenerated clean (53 rows) after an ortholog-dedup fix.
- Best contrast target: `5iso` (AMPK alpha2 P54646 / beta1 Q9Y478).
  On the ligand chain: naked_mole_rat ESM enrichment 2.65 vs mouse 1.39, while
  Boltz iptm naked_mole_rat 0.758 >= mouse 0.675 -> consistent with
  signaling rewiring (interface diverges but stays well-formed), not breakage.
- Caveats: binding_confidence is low across the board (~0.27-0.32); human Q9Y478
  (183 aa) and its orthologs (270 aa) differ in length, so treat absolute values
  cautiously and lean on the relative (long-lived vs mouse) contrast.

## Next steps

- Regenerate the pipeline on another candidate set (e.g. `sirt6_dna_repair`,
  `has2_cd44_nmr`) to get fresh targets; requires Biohub embeddings.
- Resolve the human/ortholog length mismatch (likely isoform/gene mapping) before
  trusting absolute binding metrics.
- Consider an agentic coding tool for the multi-file regeneration work.
