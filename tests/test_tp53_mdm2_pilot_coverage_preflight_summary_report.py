from pathlib import Path

import polars as pl

from longevity_port_pipelines.stages import tp53_mdm2_ortholog_repair_decisions as repair
from longevity_port_pipelines.stages.tp53_mdm2_pilot_coverage_preflight import (
    build_tp53_mdm2_pilot_coverage_preflight,
    status_counts,
)

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/tp53_mdm2_pilot_coverage_preflight_summary.md"
MANIFEST_PATH = ROOT / "data/input/tp53_mdm2_pilot_manifest.csv"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def load_manifest() -> pl.DataFrame:
    return pl.read_csv(MANIFEST_PATH)


def build_preflight() -> pl.DataFrame:
    return build_tp53_mdm2_pilot_coverage_preflight(
        load_manifest(),
        repair_decisions=repair.read_repair_decisions(),
    )


def test_tp53_mdm2_pilot_coverage_preflight_summary_report_exists() -> None:
    assert DOC_PATH.exists()


def test_tp53_mdm2_pilot_coverage_preflight_summary_records_inputs_and_output() -> None:
    doc = read_doc()

    assert "data/input/tp53_mdm2_pilot_manifest.csv" in doc
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in doc
    assert "data/interim/tp53_mdm2_pilot_coverage_preflight.csv" in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_records_command() -> None:
    doc = read_doc()

    assert "uv run tp53-mdm2-pilot-coverage-preflight" in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_matches_preflight_status() -> None:
    doc = read_doc()
    preflight = build_preflight()

    assert preflight.height == 2
    assert status_counts(preflight) == {"blocked_pending_coverage_repair": 2}

    assert "Row count: `2`" in doc
    assert "Coverage preflight status: `blocked_pending_coverage_repair`" in doc
    assert ("Recommended next action: `curate_or_fetch_tp53_mdm2_source_ortholog_coverage`") in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_matches_repair_decisions() -> None:
    doc = read_doc()
    preflight = build_preflight()

    assert set(preflight.get_column("repair_decision").to_list()) == {
        "fetch_or_curate_source_ortholog"
    }
    assert set(preflight.get_column("repair_priority").to_list()) == {"high"}
    assert set(preflight.get_column("repair_claim_policy").to_list()) == {"ortholog_repair_only"}

    assert "Repair decision: `fetch_or_curate_source_ortholog`" in doc
    assert "Repair priority: `high`" in doc
    assert "Repair claim policy: `ortholog_repair_only`" in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_records_rows() -> None:
    doc = read_doc()

    assert "tp53_mdm2_elephant_seed_tp53_chain" in doc
    assert "tp53_mdm2_elephant_seed_mdm2_chain" in doc
    assert "`P04637`" in doc
    assert "`Q00987`" in doc
    assert "`A`" in doc
    assert "`B`" in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_records_blocker_interpretation() -> None:
    doc = read_doc()

    assert "blocked before contrast analysis" in doc
    assert "source ortholog coverage" in doc
    assert "cofolding should remain blocked" in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_records_no_live_actions() -> None:
    doc = read_doc()

    assert "fetch orthologs" in doc
    assert "run Biohub" in doc
    assert "run Boltz" in doc
    assert "generate embeddings" in doc
    assert "create cofolding inputs" in doc
    assert "submit cofolding jobs" in doc
    assert "spend Boltz credits" in doc
    assert "change downstream gate decisions" in doc
    assert "make biological validation claims" in doc


def test_tp53_mdm2_pilot_coverage_preflight_summary_records_next_action() -> None:
    doc = read_doc()

    assert "Curate or fetch the TP53/MDM2 source ortholog coverage" in doc
    assert "re-run the TP53/MDM2 coverage preflight" in doc
    assert "re-check the contrast gate" in doc
