from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import lane_manifest

ROOT = Path(__file__).resolve().parents[1]

LANE_MANIFEST_SCHEMA_PATH = ROOT / "data/config/lane_manifest_schema.yaml"
CANDIDATE_LANES_PATH = ROOT / "data/config/candidate_lanes.yaml"


def load_schema() -> dict:
    return lane_manifest.load_lane_manifest_schema(LANE_MANIFEST_SCHEMA_PATH)


def load_candidate_lanes() -> dict:
    return lane_manifest.load_candidate_lanes(CANDIDATE_LANES_PATH)


def manifest_row() -> dict[str, str]:
    schema = load_schema()
    candidate_lanes = load_candidate_lanes()
    lane_name = "sirt6_dna_repair"
    lane = candidate_lanes["lanes"][lane_name]

    return {
        "candidate_set": lane["candidate_set"],
        "candidate_id": "sirt6_example_candidate",
        "lane_name": lane_name,
        "lane_lifecycle_status": "calibration",
        "biological_mode": lane["biological_mode"],
        "source_species": "human",
        "source_species_taxid": "9606",
        "target_species": "naked_mole_rat",
        "target_species_taxid": "10181",
        "gene_symbol": "SIRT6",
        "source_uniprot": "Q8N6T7",
        "target_uniprot": "example_target_uniprot",
        "partner_gene_symbol": "XRCC6",
        "partner_source_uniprot": "P12956",
        "partner_target_uniprot": "example_partner_target_uniprot",
        "interaction_role": "receptor",
        "evidence_scope": "planning_manifest_only",
        "gate_sequence": ",".join(schema["required_gate_status_fields"]),
        "manifest_status": "planning_only",
        "claim_policy": schema["claim_policy"],
        "claim_status": "planning_only",
        "reviewer_note": "Synthetic validator smoke row; no biological claim.",
    }


def manifest_frame(*rows: dict[str, str]) -> pl.DataFrame:
    return pl.DataFrame(list(rows))


def test_load_lane_manifest_schema_reads_committed_schema() -> None:
    schema = load_schema()

    assert schema["schema_id"] == "generic_lane_manifest_schema"
    assert schema["claim_policy"] == "no_biological_claims_until_validation"


def test_empty_lane_manifest_uses_required_schema_fields() -> None:
    schema = load_schema()
    empty = lane_manifest.empty_lane_manifest(schema)

    assert empty.is_empty()
    assert set(empty.columns) == set(schema["required_manifest_fields"])


def test_validate_lane_manifest_accepts_valid_manifest_row() -> None:
    lane_manifest.validate_lane_manifest(
        manifest_frame(manifest_row()),
        schema=load_schema(),
        candidate_lanes=load_candidate_lanes(),
    )


def test_validate_lane_manifest_rejects_missing_required_columns() -> None:
    row = manifest_row()
    row.pop("reviewer_note")

    with pytest.raises(ValueError, match="missing required columns"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_blank_required_fields() -> None:
    row = manifest_row()
    row["target_uniprot"] = ""

    with pytest.raises(ValueError, match="blank required fields"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_duplicate_manifest_keys() -> None:
    row = manifest_row()

    with pytest.raises(ValueError, match="duplicate manifest identity rows"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row, row.copy()),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_unknown_lane_name() -> None:
    row = manifest_row()
    row["lane_name"] = "unknown_lane"

    with pytest.raises(ValueError, match="unknown lane_name"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_candidate_set_mismatch() -> None:
    row = manifest_row()
    row["candidate_set"] = "wrong_candidate_set"

    with pytest.raises(ValueError, match="candidate_set does not match"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_biological_mode_mismatch() -> None:
    row = manifest_row()
    row["biological_mode"] = "beneficial_breakage"

    with pytest.raises(ValueError, match="biological_mode does not match"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_invalid_manifest_status() -> None:
    row = manifest_row()
    row["manifest_status"] = "validated_biological_hit"

    with pytest.raises(ValueError, match="invalid manifest_status"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_nonconservative_claim_policy() -> None:
    row = manifest_row()
    row["claim_policy"] = "validated_biological_claims_allowed"

    with pytest.raises(ValueError, match="invalid claim_policy"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_validate_lane_manifest_rejects_incomplete_gate_sequence() -> None:
    row = manifest_row()
    row["gate_sequence"] = "manifest"

    with pytest.raises(ValueError, match="gate_sequence is missing gates"):
        lane_manifest.validate_lane_manifest(
            manifest_frame(row),
            schema=load_schema(),
            candidate_lanes=load_candidate_lanes(),
        )


def test_summarize_lane_manifest_status_counts_empty_manifest() -> None:
    schema = load_schema()
    empty = lane_manifest.empty_lane_manifest(schema)

    summary = lane_manifest.summarize_lane_manifest_status(empty)

    assert summary == {
        "row_count": 0,
        "lane_names": [],
        "candidate_sets": [],
        "manifest_status_counts": {},
        "claim_status_counts": {},
        "lane_name_counts": {},
        "candidate_set_counts": {},
        "planning_only_rows": 0,
        "validation_required_rows": 0,
    }


def test_summarize_lane_manifest_status_counts_manifest_rows() -> None:
    row_a = manifest_row()
    row_b = manifest_row()
    row_b["candidate_id"] = "sirt6_second_seed_row"
    row_b["manifest_status"] = "coverage_pending"
    row_b["claim_status"] = "coverage_readiness"

    manifest = manifest_frame(row_a, row_b)

    lane_manifest.validate_lane_manifest(
        manifest,
        schema=load_schema(),
        candidate_lanes=load_candidate_lanes(),
    )

    summary = lane_manifest.summarize_lane_manifest_status(manifest)

    assert summary["row_count"] == 2
    assert summary["lane_names"] == ["sirt6_dna_repair"]
    assert summary["candidate_sets"] == ["sirt6_dna_repair"]
    assert summary["manifest_status_counts"] == {
        "coverage_pending": 1,
        "planning_only": 1,
    }
    assert summary["claim_status_counts"] == {
        "coverage_readiness": 1,
        "planning_only": 1,
    }
    assert summary["lane_name_counts"] == {"sirt6_dna_repair": 2}
    assert summary["candidate_set_counts"] == {"sirt6_dna_repair": 2}
    assert summary["planning_only_rows"] == 1
    assert summary["validation_required_rows"] == 0


def test_render_lane_manifest_status_summary_markdown_records_guardrails() -> None:
    summary = lane_manifest.summarize_lane_manifest_status(manifest_frame(manifest_row()))

    markdown = lane_manifest.render_lane_manifest_status_summary_markdown(summary)

    assert "# Lane manifest status summary" in markdown
    assert "planning-only technical summary" in markdown
    assert "does not make biological validation claims" in markdown
    assert "sirt6_dna_repair" in markdown
    assert "No live Biohub calls" in markdown
    assert "No live Boltz calls" in markdown
    assert "No embedding generation" in markdown
    assert "No cofolding input generation" in markdown


def test_write_lane_manifest_status_summary_writes_markdown(tmp_path: Path) -> None:
    manifest = manifest_frame(manifest_row())
    output_path = tmp_path / "lane_manifest_status_summary.md"

    summary = lane_manifest.write_lane_manifest_status_summary(
        manifest,
        output_path,
    )

    assert summary["row_count"] == 1
    assert output_path.exists()

    markdown = output_path.read_text(encoding="utf-8")
    assert "# Lane manifest status summary" in markdown
    assert "| planning_only | 1 |" in markdown
    assert "No biological validation claims" in markdown


def test_load_lane_manifest_csv_reads_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.csv"
    manifest_frame(manifest_row()).write_csv(manifest_path)

    manifest = lane_manifest.load_lane_manifest_csv(manifest_path)

    assert manifest.height == 1
    assert manifest.row(0, named=True)["lane_name"] == "sirt6_dna_repair"


def test_run_lane_manifest_status_summary_cli_validates_and_writes_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manifest_path = tmp_path / "manifest.csv"
    output_path = tmp_path / "reports/lane_manifest_status_summary.md"
    manifest_frame(manifest_row()).write_csv(manifest_path)

    summary = lane_manifest.run_lane_manifest_status_summary_cli(
        [
            str(manifest_path),
            "--output-path",
            str(output_path),
            "--schema-path",
            str(LANE_MANIFEST_SCHEMA_PATH),
            "--candidate-lanes-path",
            str(CANDIDATE_LANES_PATH),
        ],
    )

    captured = capsys.readouterr()

    assert summary["row_count"] == 1
    assert output_path.exists()
    assert "Wrote lane manifest status summary" in captured.out

    markdown = output_path.read_text(encoding="utf-8")
    assert "# Lane manifest status summary" in markdown
    assert "sirt6_dna_repair" in markdown
    assert "No live Biohub calls" in markdown


def test_run_lane_manifest_status_summary_cli_rejects_invalid_manifest(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "manifest.csv"
    output_path = tmp_path / "lane_manifest_status_summary.md"

    row = manifest_row()
    row["claim_policy"] = "validated_biological_claims_allowed"
    manifest_frame(row).write_csv(manifest_path)

    with pytest.raises(ValueError, match="invalid claim_policy"):
        lane_manifest.run_lane_manifest_status_summary_cli(
            [
                str(manifest_path),
                "--output-path",
                str(output_path),
                "--schema-path",
                str(LANE_MANIFEST_SCHEMA_PATH),
                "--candidate-lanes-path",
                str(CANDIDATE_LANES_PATH),
            ],
        )

    assert not output_path.exists()
