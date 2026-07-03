# Ortholog stronger-source lookup API policy

This document defines the API-boundary policy for future stronger-source ortholog evidence lookup.

It applies to Gate 4 / Gate 5 stronger-source evidence collection, especially the current `tp53_mdm2_elephant` / `G3SX30` worklist item.

This is a policy scaffold only. It does not implement a client, does not call external services, does not fetch sequences, does not add evidence rows, and does not change any candidate status.

## Purpose

The purpose of this policy is to prepare a safe path from blocked accession-level evidence candidates to manually reviewable stronger-source evidence.

The intended future flow is:

- blocked accession-level evidence candidate
- stronger-source evidence request
- stronger-source evidence collection table
- source lookup policy boundary
- dry-run lookup plan
- fixture-backed source client
- explicit opt-in live lookup
- recorded source evidence row
- separate collection review
- later reviewed-decision PR
- later explicit Gate 4 / Gate 5 policy update, if justified

This policy does not skip any step in that chain.

## Relationship to curated ortholog inputs

This policy is upstream of the curated ortholog input contract.

`docs/ortholog_curation_inputs.md` defines how curated ortholog candidate rows may later be represented, validated, and explicitly merged into standard ortholog coverage.

This stronger-source lookup policy is narrower and earlier:

- it records source evidence for review;
- it does not create curated ortholog candidates;
- it does not populate standard ortholog coverage;
- it does not write sequence-bearing coverage rows;
- it does not modify the standard OMA / UniProt lookup path;
- it does not call or modify `fetch_ortholog()` behavior.

A future source lookup result may support a later curated-input or reviewed-decision PR, but it is not itself either of those things.

## Current scope

The immediate scope is the current stronger-source collection frontier:

- candidate set: `tp53_mdm2_elephant`
- candidate id: `tp53_mdm2_elephant_seed_mdm2_chain`
- gene: `MDM2`
- target species: `Loxodonta africana`
- target taxid: `9785`
- accession-level evidence candidate: `G3SX30`
- current status: `blocked_gate4_gate5`
- claim status: `repair_worklist`

`G3SX30` remains an accession-level evidence candidate only.

## Allowed source namespaces

Future lookup planning may target authoritative source namespaces such as:

- reviewed UniProt
- NCBI protein or gene records
- Ensembl orthology
- OMA orthology
- OrthoDB orthology
- primary literature

Recording a source namespace or identifier is not the same as accepting an ortholog.

## No-live-lookup default

Live external lookups must be disabled by default.

Any future implementation must make the non-live mode the default behavior. CI must not call external APIs.

Allowed default modes:

- policy documentation
- dry-run lookup planning
- fixture-backed tests
- static source examples
- committed table validation

Forbidden default modes:

- live UniProt query
- live NCBI query
- live Ensembl query
- live OMA query
- live OrthoDB query
- sequence fetch
- Biohub call
- Boltz call
- AF3 call
- Chai call

## Future opt-in requirements

A future live lookup mode, if added, must require explicit opt-in.

The opt-in mechanism should be visible at the command boundary, for example a flag such as `--yes-live`.

A future implementation should also record:

- candidate id
- requested source namespace
- target species
- target taxid
- accession or identifier being checked
- whether sequence retrieval is disabled
- output path
- claim policy
- downstream block status

## Output boundary

The only allowed output target for future stronger-source lookup results is the stronger-source evidence collection layer:

- `data/input/ortholog_stronger_source_evidence_collection.csv`

Allowed status after recording source evidence:

- `blocked_gate4_gate5`
- `repair_worklist`
- `no_biological_claims_until_validation`

A lookup result may record source evidence, but it must not:

- accept an ortholog;
- validate an ortholog;
- create a reviewed ortholog decision;
- create curated ortholog coverage;
- populate standard ortholog coverage;
- mark a row as Gate 8 eligible;
- mark a row as Gate 9 eligible;
- mark a row as embedding ready;
- mark a row as Boltz ready;
- create biological claims.

## Sequence policy

Stronger-source evidence lookup must not fetch sequences by default.

A source record may mention sequence length or accession metadata, but sequence retrieval is a separate action and must require a separate policy layer.

For the current `G3SX30` case, the target sequence length remains evidence metadata, not permission to fetch or use sequence data downstream.

## Fixture policy

Tests for any future source lookup client must use fixtures.

Fixtures may represent:

- source metadata payloads
- source identifier matches
- missing-source outcomes
- conflicting-source outcomes
- insufficient-evidence outcomes

Fixtures must not be treated as live source evidence unless a later PR explicitly records them as manually reviewed source evidence.

## Forbidden actions

This policy does not authorize:

- live external database lookup by default
- sequence fetch
- Biohub calls
- embedding generation
- Boltz calls
- AF3 calls
- Chai calls
- enrichment reruns
- contrast reruns
- Gate 8 promotion
- Gate 9 promotion
- reviewed ortholog decision creation
- Gate 4 / Gate 5 policy update
- biological claims

## Safe next implementation steps

Safe follow-up PRs may include:

1. a dry-run source lookup plan schema;
2. a dry-run source lookup plan table scaffold;
3. a validator for source lookup plans;
4. fixture-backed client interfaces with live lookup disabled by default;
5. explicit opt-in live lookup plumbing;
6. a manually reviewed stronger-source evidence row.

The manually reviewed evidence row must still remain blocked until a separate collection review and reviewed-decision PR exist.