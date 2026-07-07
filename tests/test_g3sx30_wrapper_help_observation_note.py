from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "docs/g3sx30_wrapper_help_observation_note.md"


def test_g3sx30_wrapper_help_observation_note_records_planned_not_observed_status() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "help_observation_status = planned_not_observed",
        "actual_cli_help_observed = false",
        "actual_command_verified = false",
        "command_selected = false",
        "output_path_selected = false",
        "execution_plan_materialized = false",
        "runtime_still_blocked = true",
        "final pre-help observation note",
        "does not run `--help`",
        "does not observe help output",
        "does not verify actual CLI flags",
        "does not implement a wrapper",
        "does not execute anything",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_observation_note_names_future_help_boundary() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "curated_embedding_preflight_dry_run_wrapper",
        "This note does not select the actual command name",
        "actual command remains unselected",
        "later PR can point to concrete source code and run only the help form",
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
        "not use `--yes-live`",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_observation_note_defines_safe_help_only_observation() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "the command is invoked only with --help or an equivalent help flag",
        "no manifest row is executed",
        "no sequence is fetched",
        "no Biohub / ESMC client is initialized for live work",
        "no embedding is generated",
        "no .npy artifact is created",
        "no data/output artifact is created or committed",
        "no ready_for_preflight status is written",
        "no Gate 8 / Gate 9 status is changed",
        "observed command form",
        "observed help output or safe excerpt",
        "exit status",
        "proof that no data/output artifact was created",
        "proof that no Biohub / ESMC call was made",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_observation_note_defines_later_checks_and_stop_conditions() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "G3SX30-specific or manifest-row-specific input control",
        "dry-run-only behavior",
        "no-live-call behavior",
        "max-live-batch-size 0 behavior",
        "non-committed output path requirement",
        "rejection of committed data/output artifacts",
        "does not claim `observed_help_flags`, `actual_supported_args`, or `verified_cli_contract`",
        "no wrapper source exists",
        "command is not clearly the G3SX30 manifest-aware wrapper",
        "help invocation creates data/output artifacts",
        "help invocation creates .npy artifacts",
        "help invocation requires Biohub / ESMC credentials",
        "help output lacks manifest-row control",
        "help output lacks dry-run-only or no-live-call controls",
        "help output permits ready_for_preflight promotion",
        "help output suggests Gate 8 / Gate 9 promotion",
    ]:
        assert required in text


def test_g3sx30_wrapper_help_observation_note_keeps_downstream_gates_blocked() -> None:
    text = NOTE.read_text(encoding="utf-8")

    for required in [
        "Help observation is metadata inspection",
        "does not process the G3SX30 manifest row",
        "does not generate embeddings",
        "does not fill missing data",
        "does not evaluate contrast",
        "does not run a biological or structural inference step",
        "remains runtime-blocked",
        "Help observation cannot mark G3SX30 `ready_for_preflight`",
        "not a live call",
        "not an embedding fill",
        "not a sequence fetch",
        "not a `.npy` artifact generation step",
        "not a `data/output` artifact commit",
        "actual G3SX30 wrapper help observation PR",
        "still no execution",
        "still no Biohub / ESMC",
        "still no embeddings",
    ]:
        assert required in text
