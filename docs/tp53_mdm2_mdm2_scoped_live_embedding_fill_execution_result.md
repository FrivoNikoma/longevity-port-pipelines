# Scoped TP53/MDM2 MDM2 live embedding fill execution result

## Summary

The authorized MDM2-only live embedding fill completed successfully for exactly
two accessions, executed sequentially one accession at a time:

1. mouse `P23804`;
2. hamster `A0ABM2YB85`.

Each accession received its own pre-live dry-run and explicit human opt-in.
`A0ABM2YB85` was not started until the immediate `P23804` post-fill audit had
passed.

## P23804

Recorded technical result:

- taxid: `10090`;
- model: `esmc-300m-2024-12`;
- pre-live status: `dry_run_missing`;
- live status: `live_completed`;
- embedding shape: `489x960`;
- dtype: `float32`;
- numeric: `true`;
- finite: `true`;
- sequence dimension matches 489 aa: `true`;
- embedding SHA-256:
  `23c92fc3ceeb9b9141d502c0b3a0c47f9aa442f5fd9659030dc88502eee6c88e`;
- follow-up runner status: `dry_run_present`;
- follow-up prerequisite status: `present_valid`.

## A0ABM2YB85

Recorded technical result:

- taxid: `10036`;
- model: `esmc-300m-2024-12`;
- pre-live status: `dry_run_missing`;
- live status: `live_completed`;
- embedding shape: `510x960`;
- dtype: `float32`;
- numeric: `true`;
- finite: `true`;
- sequence dimension matches 510 aa: `true`;
- embedding SHA-256:
  `36387d8ca76f764542225832f5146e524d615ec9c1fcc16c0523fe9c20b6de5a`;
- follow-up runner status: `dry_run_present`;
- follow-up prerequisite status: `present_valid`.

## Artifact policy

Both `.npy` files remain local runtime artifacts under `data/output/`.

They are:

- ignored by Git;
- untracked;
- not committed;
- not copied into the committed execution-result table.

External runtime sequence input, opt-in records, command logs, post-fill
preflight output, and the detailed evidence JSON also remain outside the
repository.

## Gate and claim boundaries

This execution checkpoint:

- did not run a contrast;
- did not open aggregate Gate 7 or Gate 8;
- did not promote Gate 8 or Gate 9;
- did not call Boltz, AF3, or Chai;
- made no biological claim.

The aggregate TP53/MDM2 lane remains closed because TP53 is still
`deferred_pending_source`.

## Next permitted action

Both scoped MDM2 local prerequisites are now `present_valid`.

The next permitted technical action is:

`prepare_and_execute_scoped_mdm2_contrast_dry_run`
