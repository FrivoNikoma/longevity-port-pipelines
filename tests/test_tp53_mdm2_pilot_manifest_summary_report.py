from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/tp53_mdm2_pilot_manifest_summary.md"
MANIFEST_PATH = ROOT / "data/input/tp53_mdm2_pilot_manifest.csv"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def load_manifest() -> pl.DataFrame:
    return pl.read_csv(MANIFEST_PATH)


def test_tp53_mdm2_pilot_manifest_summary_report_exists() -> None:
    assert DOC_PATH.exists()


def test_tp53_mdm2_pilot_manifest_summary_report_records_source_manifest() -> None:
    doc = read_doc()

    assert "data/input/tp53_mdm2_pilot_manifest.csv" in doc


def test_tp53_mdm2_pilot_manifest_summary_report_matches_manifest_identity() -> None:
    doc = read_doc()
    manifest = load_manifest()

    assert manifest.height == 2
    assert "Row count: `2`" in doc

    candidate_sets = set(manifest.get_column("candidate_set").to_list())
    biological_modes = set(manifest.get_column("biological_mode").to_list())
    target_species = set(manifest.get_column("target_species").to_list())
    pdb_ids = set(manifest.get_column("pdb_id").to_list())

    assert candidate_sets == {"tp53_mdm2_elephant"}
    assert biological_modes == {"beneficial_breakage"}
    assert target_species == {"elephant"}
    assert pdb_ids == {"1ycr"}

    assert "Candidate set: `tp53_mdm2_elephant`" in doc
    assert "Biological mode: `beneficial_breakage`" in doc
    assert "Target species: `elephant`" in doc
    assert "PDB structure: `1ycr`" in doc


def test_tp53_mdm2_pilot_manifest_summary_report_matches_manifest_statuses() -> None:
    doc = read_doc()
    manifest = load_manifest()

    strict_gate_statuses = set(manifest.get_column("strict_contrast_gate_status").to_list())
    cofolding_statuses = set(manifest.get_column("cofolding_plan_status").to_list())

    assert strict_gate_statuses == {"blocked_contrast_coverage"}
    assert cofolding_statuses == {"blocked_by_contrast_gate"}

    assert "Current strict contrast gate status: `blocked_contrast_coverage`" in doc
    assert "Current cofolding plan status: `blocked_by_contrast_gate`" in doc


def test_tp53_mdm2_pilot_manifest_summary_report_records_manifest_rows() -> None:
    doc = read_doc()

    assert "tp53_mdm2_elephant_seed_tp53_chain" in doc
    assert "tp53_mdm2_elephant_seed_mdm2_chain" in doc
    assert "`P04637`" in doc
    assert "`Q00987`" in doc
    assert "`A`" in doc
    assert "`B`" in doc


def test_tp53_mdm2_pilot_manifest_summary_report_records_policy_guardrails() -> None:
    doc = read_doc()

    assert "`technical_checkpoint_no_claim`" in doc
    assert "`do_not_auto_classify_breakage_as_incompatibility`" in doc
    assert "planning-only status" in doc


def test_tp53_mdm2_pilot_manifest_summary_report_records_no_live_actions() -> None:
    doc = read_doc()

    assert "fetch orthologs" in doc
    assert "run Biohub" in doc
    assert "run Boltz" in doc
    assert "generate embeddings" in doc
    assert "create cofolding inputs" in doc
    assert "change downstream gate decisions" in doc
    assert "make biological validation claims" in doc


def test_tp53_mdm2_pilot_manifest_summary_report_records_next_action() -> None:
    doc = read_doc()

    assert "Resolve the TP53/MDM2 contrast coverage blocker" in doc
    assert "coverage preflight" in doc
    assert "contrast gate checks" in doc
