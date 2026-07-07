from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "docs/g3sx30_wrapper_help_target_inspection_blocker.md"


def test_g3sx30_wrapper_help_target_inspection_blocker_records_missing_target() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "help_target_inspection_status = inspected_target_missing",
        "real_g3sx30_wrapper_help_target_found = false",
        "pyproject_g3sx30_script_entry_present = false",
        "pyproject_wrapper_script_entry_present = false",
        "ordinary_curated_embedding_scripts_present = true",
        "ordinary_scripts_valid_as_substitutes = false",
        "actual_cli_help_observed = false",
        "actual_command_verified = false",
        "command_selected = false",
        "output_path_selected = false",
        "execution_plan_materialized = false",
        "runtime_still_blocked = true",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_target_inspection_blocker_rejects_substitute_commands() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "curated_embedding_preflight_dry_run_wrapper",
        "expected future command family",
        "not as a real executable script entry point or implemented wrapper command",
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
        "ordinary commands must not be observed as substitutes",
        "not the planned G3SX30 manifest-aware wrapper target",
        "would not verify the wrapper interface",
        "misleading observed-help claim",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_target_inspection_blocker_keeps_help_observation_blocked() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "no real G3SX30 manifest-aware wrapper help target exists yet",
        "actual help-observation step is blocked",
        "This PR does not run `--help`",
        "source inspection only",
        "does not observe help output",
        "does not verify actual CLI flags",
        "does not select a command",
        "does not select an output path",
        "does not materialize an execution plan",
        "no real G3SX30 manifest-aware wrapper help target exists",
        "runtime-blocked",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_target_inspection_blocker_forbids_runtime_side_effects() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "--help run",
        "ordinary command help substitution",
        "actual command run",
        "observed-help claims",
        "actual CLI flag verification claims",
        "pyproject script entry point",
        "Typer executable wrapper",
        "wrapper implementation",
        "wrapper execution",
        "dry-run execution",
        "live execution",
        "command selection",
        "output path selection",
        "execution plan materialization",
        "Biohub / ESMC",
        "embeddings",
        ".npy artifacts",
        "data/output artifact commit",
        "ready_for_preflight",
        "manifest runtime unlock",
        "Gate 8 / Gate 9",
        "Boltz / AF3 / Chai",
        "enrichment / contrast rerun",
        "biological claim",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_target_inspection_blocker_sets_next_safe_layer() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "The natural next step is not help observation yet",
        "G3SX30 manifest-aware wrapper source/entry-point implementation plan",
        "implementation boundary",
        "Only after a real wrapper help target exists",
        "actual help-only observation",
        "still be help-only",
        "still no wrapper execution",
        "still no dry-run execution",
        "still no Biohub / ESMC",
        "still no embeddings",
    ]:
        assert required in text
