# First TP53/MDM2 interface-ready manifest result

## Result

The first result-bearing TP53/MDM2 interface-ready manifest is committed in:

```text
data/input/tp53_mdm2_first_interface_ready_manifest_results.csv#1
```

Its machine-readable contract is:

```text
data/config/tp53_mdm2_first_interface_ready_manifest_result_schema.yaml
```

The table-only loader and validator are:

```text
src/longevity_port_pipelines/stages/tp53_mdm2_first_interface_ready_manifest_result.py
```

This is the required concrete result after the three-comparator whole-protein
embedding-control checkpoint. It is not a preflight-only, inventory-only,
plan-only, approval-only, review-only, scaffold-only, or generic-refactor PR.

## Exact human reference and partner context

The committed human reference is fixed as:

```text
structure database = RCSB PDB
structure id = 1YCR
model policy = model 1 only
MDM2 chain = A
MDM2 UniProt = Q00987
TP53 chain = B
TP53 UniProt = P04637
partner context = human MDM2 chain A bound to human TP53 chain B in 1YCR
```

The chain and accession assignments are inherited from committed rows
`data/input/tp53_mdm2_pilot_manifest.csv#1-2`.

## Interface-residue source

The interface-residue source is fixed before extraction as:

```text
extractor = src/longevity_port_pipelines/stages/interface.py::extract_interface_residues
method = inter-chain heavy-atom distance
distance cutoff = 8.0 angstrom
structure model = model 1
residue indexing = zero-based chain-local residue indices
```

No residue list is extracted in this PR and no interface score is computed.

## Elephant ortholog mapping

Elephant MDM2 is source-backed and reviewed:

```text
candidate id = tp53_mdm2_elephant_seed_mdm2_chain
target accession = G3SX30
database = UniProtKB TrEMBL
species = Loxodonta africana
taxid = 9785
reviewed sequence length = 492
mapping status = reviewed_sequence_provenance
source = data/input/reviewed_target_sequence_provenance.csv#2
```

Elephant TP53 remains explicitly unresolved:

```text
candidate id = tp53_mdm2_elephant_seed_tp53_chain
target accession = unresolved
mapping status = blocked_pending_source_ortholog_provenance
source = data/input/tp53_mdm2_ortholog_repair_decisions.csv#1
```

The manifest does not invent an elephant TP53 accession. Human-reference
interface extraction is ready for the next result, but comparative elephant
interface scoring remains blocked until elephant TP53 ortholog provenance is
resolved.

## Structure-confidence policy

The human reference uses the committed experimental `1YCR` coordinate
reference only. The manifest does not use pLDDT, PAE, AF3 confidence, Chai
confidence, or another predicted-structure confidence metric.

Ortholog-mapping confidence remains a separate provenance question. Reviewed
elephant MDM2 provenance does not imply that the unresolved elephant TP53 side
is ready, and it does not authorize comparative interface scoring.

## Interpretation boundary

The `beneficial_breakage` policy remains:

```text
do_not_auto_classify_breakage_as_incompatibility
```

This manifest does not establish interface divergence, interface constraint,
binding weakening, regulatory escape, functional benefit, longevity evidence,
or another biological claim.

## Runtime and artifact boundary

This result:

- performs no structure call;
- extracts no interface residues;
- computes no interface score;
- reads or commits no `.npy` artifact;
- commits no `data/output/` artifact;
- calls neither Biohub nor ESMC;
- calls neither Boltz, AlphaFold 3, nor Chai;
- does not promote Gate 8 or Gate 9;
- makes no biological claim.

## Next result-bearing action

```text
add_first_tp53_mdm2_human_reference_interface_residue_extraction_result
```

No preflight-only, inventory-only, plan-only, approval-only, review-only,
runtime-preparation-only, scaffold-only, or generic-validator-refactor PR
should precede that extraction result.
