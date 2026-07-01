# LongevityPort roadmap v2

## Compass

LongevityPort is a reusable gated decision pipeline for cross-species protein-protein interaction portability.

The project is not SIRT6-only and not Boltz-first. SIRT6 is the first calibration lane. TP53/MDM2 is the second calibration lane. HAS2/CD44, IGF/RHEB/mTOR, AMPK, and future modules should become additional biological lanes that follow the same architecture.

The central question after every PR is:

- Which gate are we closing?

The second question is:

- Are we making a reusable layer, or just patching one biological lane?

## Core pipeline shape

The intended reusable architecture is:

1. candidate lane
2. manifest
3. coverage/provenance preflight
4. repair decisions
5. control/NEGATOME readiness
6. strict panel / contrast gate
7. long-lived-vs-short-lived technical contrast
8. contrast-gated cofolding readiness
9. candidate decision package

Boltz is a downstream compatibility classifier. AF3, Chai, MD, and chimera design are downstream compatibility and validation layers. They are not the discovery layer and should not bypass coverage, provenance, controls, and contrast gates.

## Biological lanes

The current and planned lanes are:

- sirt6_dna_repair: maintained_or_enhanced_repair
- tp53_mdm2_elephant: beneficial_breakage
- has2_cd44_nmr: transferable_function
- igf_rheb_mtor: signaling_rewiring
- ampk_pilot: signaling_rewiring

The same interface signal can mean different things in different biological modes.

For example:

- SIRT6/DNA repair: interface constraint or maintained compatibility may be promising.
- TP53/MDM2 elephant: interface divergence or weakening can be a desired regulatory escape rather than a failure.
- HAS2/CD44: transferable function and extracellular matrix context are central.
- IGF/RHEB/mTOR and AMPK: signaling rewiring and hub-risk matter more than a simple maintained/broken binary.

## Architecture-first PR roadmap

### Phase 0 - project compass

- PR 1 - Document LongevityPort roadmap v2 and current gate map
- PR 2 - Document generic candidate lane contract
- PR 3 - Add generic candidate lane registry

### Phase 1 - shared schemas before new claims

- PR 4 - Add generic claim policy schema
- PR 5 - Add generic ortholog repair decision schema
- PR 6 - Add generic coverage preflight helper

### Phase 2 - migrate calibration lanes onto shared architecture

- PR 7 - Register SIRT6 lane in generic lane registry
- PR 8 - Register TP53 MDM2 lane in generic lane registry
- PR 9 - Use generic ortholog repair schema for TP53 MDM2
- PR 10 - Use generic coverage preflight helper for TP53 MDM2
- PR 11 - Use generic coverage preflight helper for SIRT6

### Phase 3 - generic contrast and controls

- PR 12 - Add generic strict contrast panel builder
- PR 13 - Add generic candidate contrast gate
- PR 14 - Add generic NEGATOME/control readiness schema
- PR 15 - Use generic control readiness in candidate contrast gate

### Phase 4 - long-lived vs short-lived contrast

- PR 16 - Add generic long-lived vs short-lived contrast summary schema
- PR 17 - Add generic longevity contrast calculator
- PR 18 - Add contrast robustness flags

### Phase 5 - cofolding as downstream compatibility planning

- PR 19 - Generalize contrast-gated cofolding manifest
- PR 20 - Add generic cofolding readiness checklist
- PR 21 - Add opt-in live cofolding guardrail tests

### Phase 6 - decision package

- PR 22 - Add generic candidate decision package writer

The decision package should collect:

- candidate lane
- manifest status
- coverage/provenance status
- repair decisions
- control readiness
- strict panel status
- longevity contrast status
- cofolding readiness
- biological interpretation mode
- allowed claims
- forbidden claims
- recommended next action

### Phase 7 - additional biological lanes with real data

- PR 23 - Add HAS2 CD44 pilot manifest
- PR 24 - Add HAS2 CD44 coverage and provenance preflight
- PR 25 - Add IGF RHEB mTOR pilot manifest
- PR 26 - Add IGF RHEB mTOR hub-risk preflight
- PR 27 - Align AMPK pilot with generic candidate lane registry
- PR 28 - Add AMPK coverage and contrast preflight

### Phase 8 - live structural compatibility only after gates

- PR 29 - Add first generic Boltz campaign plan
- PR 30 - Add first Boltz technical compatibility checkpoint

Live structural calls must remain opt-in and explicitly documented. They should be treated as technical compatibility checkpoints, not binding validation, not biological proof, and not longevity-specific claims.

## Development rules

Use small PRs.

Do not mix:

- new biological data
- new algorithm
- new docs
- live API calls
- runtime outputs

Dry-run by default.

Do not commit:

- data/output/
- runtime Boltz results
- signed structure URLs
- large CIF/PDB outputs
- API-generated artifacts without review

Before opening a PR, run:

```bash
uv sync --frozen
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
uv run pytest tests/ -v
git diff --check
``` 

## One-sentence compass

Build a reusable multi-lane gated decision pipeline first; use SIRT6 and TP53/MDM2 as calibration lanes, not as one-off exceptions.


```

