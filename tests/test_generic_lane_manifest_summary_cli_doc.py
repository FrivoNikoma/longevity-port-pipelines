from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/generic_lane_manifest_summary_cli.md"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_generic_lane_manifest_summary_cli_doc_exists() -> None:
    assert DOC_PATH.exists()


def test_generic_lane_manifest_summary_cli_doc_records_command() -> None:
    doc = read_doc()

    assert "uv run python -m longevity_port_pipelines.stages.lane_manifest" in doc
    assert "data/interim/generic_lane_manifest_seed.csv" in doc
    assert "--output-path reports/lane_manifest_status_summary.md" in doc


def test_generic_lane_manifest_summary_cli_doc_records_validation_flow() -> None:
    doc = read_doc()

    assert "Reads the lane manifest CSV" in doc
    assert "Loads the generic lane manifest schema" in doc
    assert "Loads the candidate lane registry" in doc
    assert "Validates the manifest against the schema and registry" in doc
    assert "Writes a Markdown status summary" in doc


def test_generic_lane_manifest_summary_cli_doc_records_guardrails() -> None:
    doc = read_doc()

    assert "local reporting command only" in doc
    assert "fetch orthologs" in doc
    assert "run Biohub" in doc
    assert "run Boltz" in doc
    assert "generate embeddings" in doc
    assert "create cofolding inputs" in doc
    assert "make biological validation claims" in doc


def test_generic_lane_manifest_summary_cli_doc_records_pipeline_position() -> None:
    doc = read_doc()

    assert "manifest CSV" in doc
    assert "generic lane manifest validator" in doc
    assert "status summary" in doc
    assert "Markdown report" in doc
