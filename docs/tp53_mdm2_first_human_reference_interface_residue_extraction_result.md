# First TP53/MDM2 human-reference interface-residue extraction result

## Result

The first result-bearing human-reference interface-residue extraction is
committed in:

```text
data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv#1
```

The one-row-per-residue table is:

```text
data/input/tp53_mdm2_first_human_reference_interface_residue_records.csv
```

The machine-readable contract is:

```text
data/config/tp53_mdm2_first_human_reference_interface_residue_extraction_result_schema.yaml
```

The committed table-only validator is:

```text
src/longevity_port_pipelines/stages/tp53_mdm2_first_human_reference_interface_residue_extraction_result.py
```

This is the concrete result required by the preceding interface-ready manifest.
It is not a preflight-only, inventory-only, plan-only, approval-only,
review-only, runtime-preparation-only, scaffold-only, or generic-refactor PR.

## Structure and extraction provenance

The extraction used the experimental human complex:

- database: RCSB PDB;
- structure: `1YCR`;
- model: `1`;
- MDM2: UniProt `Q00987`, chain `A`;
- TP53: UniProt `P04637`, chain `B`;
- downloaded PDB size: `95202` bytes;
- downloaded PDB SHA256: `7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493`;
- extractor:
  `src/longevity_port_pipelines/stages/interface.py::extract_interface_residues`;
- extractor repository commit: `3d657509beba4f68e0e7121ff82414e77b98c0dd`;
- distance cutoff: `8.0` angstrom;
- indexing: zero-based chain-local residue indices.

The downloaded PDB and external runtime observation are not committed. The
runtime observation is represented by canonical JSON SHA256
`43fcec2cfe5e04f3353578c192ab4975bfb75f5918b6419eb8b05d1aa749e3aa`. Validation of the committed tables requires no network
call.

## MDM2 chain-A result

Chain `A` contains `85` amino-acid residues in the parsed model. The geometric
contact mask contains `47` residues, leaving `38` residues outside the mask.

- interface fraction: `47 / 85 = 0.5529411764705883`;
- zero-based chain-local indices:

```text
0, 1, 2, 3, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 57, 61, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 82, 84
```

- PDB residue labels:

```text
GLU25, THR26, LEU27, VAL28, TYR48, THR49, MET50, LYS51, GLU52, VAL53, LEU54, PHE55, TYR56, LEU57, GLY58, GLN59, TYR60, ILE61, MET62, THR63, LEU66, TYR67, ASP68, GLU69, LYS70, GLN71, GLN72, HIS73, ILE74, VAL75, LEU82, PHE86, PHE91, SER92, VAL93, LYS94, GLU95, HIS96, ARG97, LYS98, ILE99, TYR100, THR101, ILE103, TYR104, LEU107, VAL109
```

## TP53 chain-B result

Chain `B` is the crystallized 13-residue TP53 peptide. All `13` parsed residues
fall inside the `8.0` angstrom geometric contact mask.

- interface fraction: `13 / 13 = 1.0000000000000000`;
- zero-based chain-local indices:

```text
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
```

- PDB residue labels:

```text
GLU17, THR18, PHE19, SER20, ASP21, LEU22, TRP23, LYS24, LEU25, LEU26, PRO27, GLU28, ASN29
```

## Consequence for the shuffled interface control

A naive within-chain shuffle is non-degenerate for MDM2 chain `A`, because the
mask contains `47` of `85` residues.

A naive within-chain shuffle is degenerate for TP53 chain `B`, because the mask
contains all `13` observed residues and there are zero observed non-interface
residues. Any size-preserving selection of 13 residues from this 13-residue
chain returns the original set.

Therefore the next committed shuffled-interface control must be restricted to MDM2 chain `A` until a separate, non-degenerate TP53 background is explicitly
defined. This result does not silently substitute full-length TP53 sequence
positions for the crystallized chain-B coordinate set.

## Interpretation boundary

The extracted lists are geometric contact masks at the committed `8.0`
angstrom cutoff. They are not binding-hotspot annotations and not a biological claim.
They are also not:

- binding-hotspot annotations;
- per-residue interface scores;
- evidence that every listed residue contributes equally to binding;
- a shuffled interface control;
- a curated NEGATOME control;
- an elephant TP53/MDM2 comparison;
- proof of orthology, functional equivalence, or a longevity mechanism;
- a Gate 8 or Gate 9 promotion;
- a biological claim.

The relatively broad MDM2 mask and complete TP53-peptide coverage must
therefore be carried into control construction rather than interpreted as
functional importance.

## Boundaries

This result records one completed RCSB PDB download and one completed geometric
interface extraction. The PR and its committed validation do not:

- commit the PDB file or external observation JSON;
- call a predicted-structure service;
- compute an interface score;
- compute a shuffled or NEGATOME control;
- perform comparative elephant interface scoring;
- read or commit `.npy` files;
- commit files under `data/output`;
- call Biohub/ESMC, Boltz, AlphaFold 3, or Chai;
- promote Gate 8 or Gate 9;
- make a biological claim.

## Next result-bearing action

```text
add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result
```

No preflight-only, inventory-only, plan-only, approval-only, review-only,
runtime-preparation-only, scaffold-only, generic-validator-refactor, or other
non-result PR should precede that MDM2-side shuffled-interface control result.
