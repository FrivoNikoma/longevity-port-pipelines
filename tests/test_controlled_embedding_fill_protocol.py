from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_contains_all(text: str, phrases: list[str]) -> None:
    for phrase in phrases:
        assert phrase in text


def test_controlled_embedding_fill_protocol_references_existing_tools() -> None:
    text = read_doc("docs/controlled_embedding_fill_protocol.md")

    assert_contains_all(
        text,
        [
            "curated_embedding_preflight",
            "curated_embedding_single",
            "docs/gate_aware_embedding_fill_plan.md",
            "docs/brandts_bat_p09874_live_embedding_generation.md",
            "Brandt's bat P09874",
            "P09874",
        ],
    )


def test_controlled_embedding_fill_protocol_requires_dry_run_before_live() -> None:
    text = read_doc("docs/controlled_embedding_fill_protocol.md")

    assert_contains_all(
        text,
        [
            "Run `curated_embedding_preflight` first",
            "run `curated_embedding_single` in dry-run mode first",
            "Require `sequence_length_status == matches`",
            "Require `embedding_exists == False`",
            "explicit human approval before using `--yes-live`",
            "Run at most one live row at a time",
        ],
    )


def test_controlled_embedding_fill_protocol_locks_artifact_guardrails() -> None:
    text = read_doc("docs/controlled_embedding_fill_protocol.md")

    assert_contains_all(
        text,
        [
            "Never commit `data/output/` artifacts",
            "Generated embeddings are runtime artifacts",
            ".npy",
            "local runtime artifact validation",
            "status: dry_run_present",
            "embedding_exists: True",
        ],
    )


def test_controlled_embedding_fill_protocol_blocks_downstream_shortcuts() -> None:
    text = read_doc("docs/controlled_embedding_fill_protocol.md")

    assert_contains_all(
        text,
        [
            "Do not rerun enrichment or contrast automatically",
            "Do not call Boltz automatically",
            "Embedding fill does not automatically permit downstream analysis",
            "do not generate a cofolding manifest automatically",
            "do not produce a candidate decision package automatically",
        ],
    )


def test_controlled_embedding_fill_protocol_records_claim_guardrails() -> None:
    text = read_doc("docs/controlled_embedding_fill_protocol.md")

    assert_contains_all(
        text,
        [
            "validated longevity signal",
            "validated biological hit",
            "confirmed binding change",
            "confirmed functional effect",
            "safe to port",
            "proven pro-longevity variant",
        ],
    )


def test_controlled_embedding_fill_protocol_keeps_aggregate_lane_closed_with_scoped_mdm2_exception() -> (
    None
):
    text = read_doc("docs/controlled_embedding_fill_protocol.md")

    assert_contains_all(
        text,
        [
            "SIRT6/core3 is the advanced calibration lane",
            "The aggregate TP53/MDM2 lane remains closed while TP53 is",
            "beneficial_breakage",
            "TP53 rows must not receive live embedding fills while their source and coverage",
            "Narrow MDM2-only technical authorization exception",
            "at most one live row at a time",
        ],
    )
