from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import cofolding_readiness_runtime
from longevity_port_pipelines.stages import sirt6_cofolding_readiness_context as stage
from longevity_port_pipelines.stages.cofolding_readiness_runtime import (
    build_generic_cofolding_readiness,
)

GATE8_SCHEMA = {
    "candidate_set": pl.Utf8,
    "lane_name": pl.Utf8,
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "priority": pl.Utf8,
    "long_lived_species": pl.Utf8,
    "short_lived_species": pl.Utf8,
    "short_lived_control_count": pl.Int64,
    "contrast_class": pl.Utf8,
    "contrast_requires_review": pl.Boolean,
    "robustness_status": pl.Utf8,
    "robustness_note": pl.Utf8,
    "contrast_status": pl.Utf8,
    "recommended_next_action": pl.Utf8,
    "contrast_dry_run_allowed": pl.Boolean,
    "controlled_claim_allowed": pl.Boolean,
    "claim_policy": pl.Utf8,
    "claim_status": pl.Utf8,
    "contrast_note": pl.Utf8,
}

PARTNER_CONTEXT_SCHEMA = {
    "candidate_id": pl.Utf8,
    "pdb_id": pl.Utf8,
    "chain": pl.Utf8,
    "source_uniprot": pl.Utf8,
    "partner_uniprot": pl.Utf8,
}


def gate8_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=GATE8_SCHEMA)


def partner_context_rows(rows: list[dict[str, object]]) -> pl.DataFrame:
    return pl.DataFrame(rows, schema=PARTNER_CONTEXT_SCHEMA)


def gate8_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "sirt6_dna_repair",
        "lane_name": "sirt6_dna_repair",
        "candidate_id": "4xhu__A1_P09874--4xhu__B1_Q9UNS1",
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "priority": "1",
        "long_lived_species": "naked_mole_rat",
        "short_lived_species": "mouse,rat",
        "short_lived_control_count": 2,
        "contrast_class": "long_lived_specific_interface_divergence",
        "contrast_requires_review": False,
        "robustness_status": "technical_multispecies_contrast",
        "robustness_note": "Multiple controls and long-lived species represented.",
        "contrast_status": "technical_contrast_ready",
        "recommended_next_action": "review_technical_contrast_checkpoint_without_biological_claims",
        "contrast_dry_run_allowed": True,
        "controlled_claim_allowed": False,
        "claim_policy": "no_biological_claims_until_validation",
        "claim_status": "technical_contrast_checkpoint",
        "contrast_note": "Technical contrast only.",
    }
    row.update(overrides)
    return row


def partner_context_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_id": "candidate_without_encoded_partner",
        "pdb_id": "4xhu",
        "chain": "receptor",
        "source_uniprot": "P09874",
        "partner_uniprot": "Q9UNS1",
    }
    row.update(overrides)
    return row


def test_sirt6_cofolding_context_schema_matches_generic_runtime_context_columns() -> None:
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_rows([gate8_row()]),
    )

    assert context.columns == cofolding_readiness_runtime.CONTEXT_COLUMNS
    assert list(stage.SIRT6_COFOLDING_CONTEXT_SCHEMA) == cofolding_readiness_runtime.CONTEXT_COLUMNS


def test_sirt6_cofolding_context_infers_partner_from_receptor_candidate_id() -> None:
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_rows([gate8_row()]),
    )

    row = context.row(0, named=True)

    assert row["candidate_set"] == "sirt6_dna_repair"
    assert row["lane_name"] == "sirt6_dna_repair"
    assert row["target_species"] == "naked_mole_rat"
    assert row["partner_uniprot"] == "Q9UNS1"
    assert row["partner_context_status"] == "partner_context_ready"
    assert row["source_provenance_status"] == "source_provenance_ready"
    assert row["cofolding_input_review_status"] == "dry_run_inputs_unreviewed"
    assert row["live_opt_in_status"] == "live_not_requested"


def test_sirt6_cofolding_context_infers_partner_from_ligand_candidate_id() -> None:
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_rows(
            [
                gate8_row(
                    candidate_id="4xhu__A1_P09874--4xhu__B1_Q9UNS1",
                    chain="ligand",
                    source_uniprot="Q9UNS1",
                )
            ]
        ),
    )

    row = context.row(0, named=True)

    assert row["partner_uniprot"] == "P09874"
    assert row["partner_context_status"] == "partner_context_ready"


def test_sirt6_cofolding_context_uses_explicit_partner_table_for_simple_ids() -> None:
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_rows(
            [
                gate8_row(
                    candidate_id="candidate_without_encoded_partner",
                    pdb_id="4xhu",
                    chain="receptor",
                    source_uniprot="P09874",
                )
            ]
        ),
        partner_context=partner_context_rows([partner_context_row()]),
    )

    row = context.row(0, named=True)

    assert row["partner_uniprot"] == "Q9UNS1"
    assert row["partner_context_status"] == "partner_context_ready"


def test_sirt6_cofolding_context_marks_missing_partner_context() -> None:
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_rows(
            [
                gate8_row(
                    candidate_id="candidate_without_encoded_partner",
                )
            ]
        ),
    )

    row = context.row(0, named=True)

    assert row["partner_uniprot"] == ""
    assert row["partner_context_status"] == "partner_context_missing"


def test_sirt6_context_with_unreviewed_inputs_blocks_generic_gate9_runtime() -> None:
    gate8 = gate8_rows([gate8_row()])
    context = stage.build_sirt6_cofolding_readiness_context(gate8_summary=gate8)

    readiness = build_generic_cofolding_readiness(gate8, context)

    row = readiness.row(0, named=True)

    assert row["cofolding_readiness_status"] == "blocked_unreviewed_dry_run_inputs"
    assert row["cofolding_dry_run_allowed"] is False
    assert row["live_cofolding_allowed"] is False


def test_sirt6_context_with_reviewed_inputs_can_feed_generic_gate9_runtime() -> None:
    gate8 = gate8_rows([gate8_row()])
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8,
        cofolding_input_review_status="dry_run_inputs_reviewed",
    )

    readiness = build_generic_cofolding_readiness(gate8, context)

    row = readiness.row(0, named=True)

    assert row["cofolding_readiness_status"] == "cofolding_dry_run_ready"
    assert row["cofolding_dry_run_allowed"] is True
    assert row["live_cofolding_allowed"] is False
    assert row["controlled_claim_allowed"] is False
    assert row["claim_policy"] == "no_biological_claims_until_validation"


def test_sirt6_context_with_missing_partner_blocks_generic_gate9_runtime() -> None:
    gate8 = gate8_rows(
        [
            gate8_row(
                candidate_id="candidate_without_encoded_partner",
            )
        ]
    )
    context = stage.build_sirt6_cofolding_readiness_context(
        gate8_summary=gate8,
        cofolding_input_review_status="dry_run_inputs_reviewed",
    )

    readiness = build_generic_cofolding_readiness(gate8, context)

    row = readiness.row(0, named=True)

    assert row["cofolding_readiness_status"] == "blocked_missing_partner_context"
    assert row["cofolding_dry_run_allowed"] is False


def test_sirt6_cofolding_context_validates_gate8_columns() -> None:
    with pytest.raises(ValueError, match="gate8_summary is missing required columns"):
        stage.build_sirt6_cofolding_readiness_context(
            gate8_summary=gate8_rows([gate8_row()]).drop("long_lived_species"),
        )


def test_sirt6_cofolding_context_validates_partner_context_columns() -> None:
    with pytest.raises(ValueError, match="partner_context is missing required columns"):
        stage.build_sirt6_cofolding_readiness_context(
            gate8_summary=gate8_rows([gate8_row()]),
            partner_context=partner_context_rows([partner_context_row()]).drop("partner_uniprot"),
        )


def test_sirt6_cofolding_context_rejects_duplicate_partner_context_keys() -> None:
    duplicate_partner_context = partner_context_rows(
        [
            partner_context_row(),
            partner_context_row(),
        ]
    )

    with pytest.raises(ValueError, match="duplicate SIRT6 cofolding key"):
        stage.build_sirt6_cofolding_readiness_context(
            gate8_summary=gate8_rows(
                [
                    gate8_row(
                        candidate_id="candidate_without_encoded_partner",
                        pdb_id="4xhu",
                        chain="receptor",
                        source_uniprot="P09874",
                    )
                ]
            ),
            partner_context=duplicate_partner_context,
        )


def test_write_sirt6_cofolding_readiness_context_writes_csv(tmp_path: Path) -> None:
    output = tmp_path / "sirt6_generic_cofolding_readiness_context.csv"

    context = stage.write_sirt6_cofolding_readiness_context(
        gate8_summary=gate8_rows([gate8_row()]),
        output=output,
    )

    assert output.exists()
    written = pl.read_csv(output)

    assert written.height == context.height
    assert written.columns == cofolding_readiness_runtime.CONTEXT_COLUMNS
