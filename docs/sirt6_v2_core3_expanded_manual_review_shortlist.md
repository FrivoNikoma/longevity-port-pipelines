# SIRT6 v2 core3-expanded manual review shortlist

## Purpose

This note defines the manual biological review shortlist for the SIRT6 v2 core3-expanded divergence-profile analysis.

The previous clustering interpretation showed that the core3-expanded run separates residue-level interface behavior into interpretable regimes:

1. divergent / high-tail-enriched interface profiles;
2. constrained or mixed interface profiles;
3. shared extreme interface-constraint anchors;
4. singleton divergent outliers.

This document turns those exploratory clusters into a practical manual review queue.

The goal is not to claim validated longevity mechanisms. The goal is to identify concrete complex-chain-species cases that should be inspected structurally before they are treated as candidate biological hits or used for downstream prioritization.

## Interpretation rule

Each case should be reviewed as a `complex x chain x species` object.

For each object, manual review should ask:

1. Is the signal localized to a real mapped interface?
2. Are the top residue-level deltas near the physical binding surface after sequence-to-structure remapping?
3. Does the case distinguish long-lived species from the mouse baseline?
4. Is the biological direction plausible: maintained interaction, remodeled interaction, or incompatibility risk?
5. Is there an artifact risk from chain mapping, residue numbering, missing residues, predicted structures, or very small interface size?

## Review priority 1: 8g57 ligand / naked_mole_rat and Myotis lucifugus

### Case

- Complex: `8g57`
- Chain: ligand
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Review class: long-lived-specific or long-lived-enriched interface divergence candidate
- Cluster regime: divergent / high-tail-enriched mode

### Why it is interesting

This is one of the strongest candidate cases from the core3-expanded clustering interpretation.

Biologically, 8g57 is a SIRT6-nucleosome complex context. SIRT6 is directly relevant to the LongevityPort hypothesis because it links chromatin regulation, DNA repair, and lifespan-associated repair efficiency. A long-lived-specific divergence pattern at a SIRT6-associated nucleosome interface could indicate altered chromatin engagement, substrate positioning, or nucleosome-surface recognition.

This is therefore a high-priority manual review target.

### What to inspect

Check whether the top divergent residues are:

- on the ligand-side binding surface;
- near the SIRT6-contacting nucleosome/histone/DNA surface;
- shared or recurrent between naked mole-rat and Myotis;
- absent or weaker in mouse.

### Artifact checks

- Confirm chain identity and biological role of the ligand.
- Confirm sequence-to-structure residue remapping.
- Check whether the apparent signal is driven by a small number of residues.
- Check whether nucleosome/histone residue numbering differs from canonical sequence numbering.
- Separate protein-protein contacts from protein-DNA contacts if the interface definition includes nucleosomal DNA proximity.

### Manual review decision

Keep as a top candidate if the divergent residues map to a coherent physical surface and if the mouse baseline is weaker or qualitatively different.

Defer if the signal is mostly caused by ambiguous histone/nucleosome numbering or non-protein structural context.

## Review priority 2: 1nfi receptor / naked_mole_rat and Myotis lucifugus

### Case

- Complex: `1nfi`
- Chain: receptor
- Species: `naked_mole_rat`, `myotis_lucifugus`
- Review class: long-lived-enhanced interface divergence candidate
- Cluster regime: divergent / high-tail-enriched mode

### Why it is interesting

1nfi corresponds to the NF-kappaB / IkappaBalpha regulatory complex context.

The receptor-side signal is biologically interesting because NF-kappaB is not simply a DNA repair enzyme; it is a stress, inflammatory, immune, survival, and senescence-associated transcriptional regulator. A long-lived-enhanced interface divergence pattern here may suggest altered regulatory sequestration, altered release threshold, or modified inflammatory responsiveness.

This makes 1nfi a strong regulatory rewiring candidate rather than a simple repair-protein candidate.

### What to inspect

Check whether the top divergent residues are:

- on the RELA/p65-facing regulatory interface;
- near the IkappaBalpha ankyrin-repeat binding surface;
- recurrent in both naked mole-rat and Myotis;
- stronger than the mouse baseline.

### Artifact checks

- Confirm whether the receptor role corresponds to RELA/p65 or the inhibitory partner in this selection.
- Check whether truncation in the experimental structure affects the mapped interface.
- Check if the divergent residues cluster on one structural face or are scattered.
- Check whether the same residues are recurrent across long-lived species.

### Manual review decision

Keep as a top regulatory-interface candidate if residues form a coherent surface and long-lived species exceed mouse.

Use careful wording: this is a candidate for altered inflammatory/stress regulation, not direct proof of lifespan extension.

## Review priority 3: 7s68 receptor / naked_mole_rat

### Case

- Complex: `7s68`
- Chain: receptor
- Species: `naked_mole_rat`
- Review class: long-lived-specific interface divergence candidate, but lower confidence
- Cluster regime: cluster 0 / mixed or constrained background mode

### Why it is interesting

7s68 is a PARP1 DNA-damage recognition context. PARP1 rapidly detects DNA strand breaks and triggers poly(ADP-ribose)-based DNA damage signaling. A naked mole-rat-specific signal in this context would be biologically relevant because it touches the DNA damage response layer upstream of repair coordination.

However, because this case falls into cluster 0, it should be treated cautiously. The signal may be subtle, mixed, or less robust than the main divergent cluster.

### What to inspect

Check whether the naked mole-rat residues:

- lie near PARP1 domain-domain or DNA-damage-recognition interfaces;
- are actually interface-proximal after remapping;
- differ qualitatively from mouse and Myotis;
- overlap with known regulatory/allosteric regions.

### Artifact checks

- Check whether the interface in this structure is protein-protein, protein-DNA, or intra-PARP1 domain contact.
- Confirm that the signal is not dominated by DNA-contact residues if the intended analysis is protein-protein interface divergence.
- Check whether PARP1 domain boundaries make residue mapping ambiguous.

### Manual review decision

Keep as a cautious secondary candidate if the signal maps to a meaningful PARP1 regulatory surface.

Do not present it as a top hit unless manual structure review supports the interface interpretation.

## Review priority 4: 8f86 receptor / Myotis lucifugus

### Case

- Complex: `8f86`
- Chain: receptor
- Species: `myotis_lucifugus`
- Review class: long-lived-specific interface constraint candidate
- Cluster regime: constrained / mixed mode

### Why it is interesting

8f86 is another SIRT6-nucleosome context. Unlike divergent candidates, this case appears interesting because of interface constraint: the interface may be more preserved than the surrounding protein background.

For LongevityPort, this matters because not all useful long-lived-species variants should disrupt interfaces. Some may be portable precisely because the critical interaction surface is preserved while other parts of the protein diverge.

### What to inspect

Check whether constrained residues are:

- located on the SIRT6-nucleosome contact surface;
- conserved in Myotis relative to human;
- surrounded by more divergent non-interface regions;
- consistent with a maintained chromatin-engagement mode.

### Artifact checks

- Confirm receptor chain identity.
- Confirm residue remapping between sequence and structure.
- Check whether the constraint call depends on a small interface or missing residues.
- Check whether the interface includes histone/DNA contacts that need separate interpretation.

### Manual review decision

Keep as a maintained-interface / safer-portability candidate if the constrained residues form a coherent SIRT6-nucleosome surface.

This should be framed as a counterexample to the idea that only divergent interfaces matter.

## Review priority 5: 4xhu receptor / all species

### Case

- Complex: `4xhu`
- Chain: receptor
- Species: mouse, naked_mole_rat, Myotis lucifugus
- Review class: shared extreme interface constraint anchor
- Cluster regime: extreme shared interface constraint

### Why it is interesting

4xhu is not a clean longevity-specific candidate. Its value is as an internal anchor: a case where the interface appears strongly constrained across all species.

This is useful because it shows that the pipeline does not call every interface divergent. It can also detect preserved interaction surfaces.

Biologically, 4xhu is a PARP1-linked context. A shared constrained PARP1-associated interface may represent a deeply conserved DNA-repair or replication-associated interaction that should not be disrupted.

### What to inspect

Check whether the constrained residues:

- form the expected PARP1-associated binding surface;
- are shared across all three species;
- show low interface delta but higher non-interface/background delta;
- support a maintained-interaction interpretation.

### Artifact checks

- Confirm that all three species show the same structural mapping pattern.
- Check whether the constraint is caused by sequence identity rather than a meaningful interface-specific pattern.
- Check whether the partner and receptor definitions are biologically appropriate.

### Manual review decision

Use this as an internal negative/anchor case.

Do not present it as a longevity-specific hit. Present it as evidence that the method can separate shared constraint from candidate long-lived-specific divergence.

## Review priority 6: 8bhv ligand / mouse

### Case

- Complex: `8bhv`
- Chain: ligand
- Species: mouse
- Review class: singleton divergent outlier / artifact-risk benchmark
- Cluster regime: singleton extreme divergent outlier

### Why it is interesting

8bhv is an NHEJ DNA double-strand-break repair complex involving Ku/DNA-PK-associated repair machinery and XLF/PAXX-mediated bridging.

The ligand mouse case is important because it is extreme, but it is not a longevity-specific hit. A strong mouse signal means the method may be detecting non-human-vs-human divergence, chain-specific behavior, or mapping effects rather than a long-lived adaptation.

This case should be retained as an artifact-risk benchmark.

### What to inspect

Check whether the extreme signal is caused by:

- a very small interface;
- residue-numbering mismatch;
- chain-role mismatch;
- a few high-delta residues;
- alignment or remapping artifacts;
- mouse-specific divergence unrelated to longevity.

### Artifact checks

- Confirm exact chain identity and residue remapping.
- Check whether the top residues physically contact the partner.
- Check whether the same surface is also divergent in naked mole-rat or Myotis.
- Compare against the 8bhv receptor cases, which may be more relevant after long-lived-vs-mouse contrast.

### Manual review decision

Use as a cautionary outlier.

Do not present this as a longevity result. Present it as a useful stress test showing why mouse baseline and negative controls are required.

## Shortlist summary

| Priority | Case                                      | Proposed interpretation                                    | Confidence before manual review     |

| -------- | ----------------------------------------- | ---------------------------------------------------------- | ----------------------------------- |

| 1        | 8g57 ligand / naked_mole_rat and Myotis   | SIRT6-nucleosome long-lived interface divergence candidate | high-priority exploratory           |

| 2        | 1nfi receptor / naked_mole_rat and Myotis | NF-kappaB regulatory-interface rewiring candidate          | high-priority exploratory           |

| 3        | 7s68 receptor / naked_mole_rat            | PARP1-linked subtle long-lived-specific candidate          | cautious                            |

| 4        | 8f86 receptor / Myotis                    | SIRT6-nucleosome maintained-interface candidate            | cautious but biologically important |

| 5        | 4xhu receptor / all species               | shared constrained-interface anchor                        | anchor/control                      |

| 6        | 8bhv ligand / mouse                       | singleton divergent outlier / artifact-risk benchmark      | not a longevity hit                 |

## Working conclusion

The core3-expanded run has produced enough structure to justify manual biological review.

The strongest interpretation is not that any single case is already validated. The strongest interpretation is that the pipeline now separates:

1. long-lived-enriched interface divergence candidates;
2. maintained-interface candidates;
3. shared constraint anchors;
4. short-lived or singleton outliers that warn against overinterpretation.

This distinction is necessary before moving from computational signal to biological claims, structural interpretation, or experimental validation.






