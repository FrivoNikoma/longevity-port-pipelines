from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_lookup_policy as live_policy,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_live_metadata_dry_run as dry_run,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_lookup_plan as lookup_plan,
)
from longevity_port_pipelines.stages import (
    ortholog_stronger_source_raw_metadata_response as raw_metadata,
)


def lookup_plan_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2",
        "candidate_id": "mdm2_elephant_G3SX30",
        "request_table": "data/input/ortholog_stronger_source_evidence_requests.csv",
        "request_source_row_index": "0",
        "gene_symbol": "MDM2",
        "source_species": "human",
        "target_species": "elephant",
        "target_species_taxid": "9785",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "requested_evidence_source_database": "UniProt",
        "requested_evidence_source_accession": "G3SX30",
        "target_taxid": "9785",
        "target_species_name": "Loxodonta africana",
        "target_gene_symbol": "MDM2",
        "target_protein_accession": "G3SX30",
        "target_sequence_length": "491",
        "planned_lookup_source_type": "reviewed_uniprot",
        "planned_lookup_source_name": "UniProt reviewed record",
        "planned_lookup_query_identifier": "G3SX30",
        "planned_lookup_query_taxid": "9785",
        "planned_lookup_mode": live_policy.EXPLICIT_LIVE_LOOKUP_MODE,
        "live_lookup_allowed": "false",
        "sequence_fetch_allowed": "false",
        "planned_output_target": lookup_plan.DEFAULT_LOOKUP_PLAN_OUTPUT_TARGET,
        "lookup_plan_status": "lookup_planned_still_blocked",
        "downstream_block_status_after_lookup_plan": lookup_plan.BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_lookup_plan": "add_manual_source_evidence_row_later",
        "claim_policy_after_lookup_plan": lookup_plan.NO_BIOLOGICAL_CLAIMS_POLICY,
        "claim_status_after_lookup_plan": lookup_plan.REPAIR_WORKLIST_CLAIM_STATUS,
        "forbidden_actions_after_lookup_plan": "; ".join(sorted(lookup_plan.RUNTIME_SIDE_EFFECTS)),
        "reviewer_note": "Raw metadata response exporter test row; remains blocked.",
    }
    row.update(overrides)
    return row


def lookup_plan_rows(*rows: dict[str, object]) -> pl.DataFrame:
    if not rows:
        return pl.DataFrame(schema={column: pl.String for column in lookup_plan.REQUIRED_COLUMNS})

    return pl.DataFrame(list(rows)).select(list(lookup_plan.REQUIRED_COLUMNS))


def authorized_dry_run_summary(plan_rows: pl.DataFrame) -> pl.DataFrame:
    context = live_policy.LiveLookupOptInContext(
        explicit_live_opt_in=True,
        running_in_ci=False,
        sequence_fetch_requested=False,
        operator_acknowledged_blockers=True,
    )

    return dry_run.build_live_metadata_dry_run_summary(
        plan_rows,
        context=context,
    )


def dry_run_derived_raw_metadata_response_rows() -> pl.DataFrame:
    plan_rows = lookup_plan_rows(lookup_plan_row())
    summary = authorized_dry_run_summary(plan_rows)

    return raw_metadata.build_raw_metadata_response_rows_from_dry_run_summary(
        lookup_plan_rows=plan_rows,
        dry_run_summary_rows=summary,
    )


def test_write_raw_metadata_response_rows_writes_empty_header_only_table(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "raw_metadata_responses.csv"
    rows = raw_metadata.empty_raw_metadata_response_rows()

    written_path = raw_metadata.write_raw_metadata_response_rows(rows, output_path)
    read_back = raw_metadata.read_raw_metadata_response_rows(written_path)

    assert written_path == output_path
    assert read_back.is_empty()
    assert read_back.columns == list(raw_metadata.REQUIRED_COLUMNS)
    raw_metadata.validate_stronger_source_raw_metadata_response_rows(read_back)


def test_write_raw_metadata_response_rows_writes_valid_dry_run_derived_rows(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "raw_metadata_responses.csv"
    rows = dry_run_derived_raw_metadata_response_rows()

    written_path = raw_metadata.write_raw_metadata_response_rows(rows, output_path)
    read_back = raw_metadata.read_raw_metadata_response_rows(written_path)

    assert written_path == output_path
    assert read_back.height == 1
    assert read_back.columns == list(raw_metadata.REQUIRED_COLUMNS)
    assert read_back.row(0, named=True)["raw_metadata_source_type"] == (
        raw_metadata.DRY_RUN_DERIVED_RAW_METADATA_SOURCE_TYPE
    )
    raw_metadata.validate_stronger_source_raw_metadata_response_rows(read_back)
    raw_metadata.validate_dry_run_derived_rows_remain_explicit(read_back)


def test_write_raw_metadata_response_rows_rejects_invalid_rows_before_writing(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "raw_metadata_responses.csv"
    rows = dry_run_derived_raw_metadata_response_rows().with_columns(
        pl.lit("true").alias("gate8_promoted")
    )

    with pytest.raises(ValueError, match="must remain false"):
        raw_metadata.write_raw_metadata_response_rows(rows, output_path)

    assert not output_path.exists()


def test_dry_run_derived_guardrail_rejects_rows_that_look_like_real_metadata() -> None:
    rows = dry_run_derived_raw_metadata_response_rows().with_columns(
        pl.lit("real_external_payload_persisted").alias("raw_metadata_payload_ref"),
        pl.lit("Real external database metadata response.").alias("raw_metadata_summary"),
        pl.lit("Looks like real external metadata.").alias("reviewer_note"),
    )

    with pytest.raises(ValueError, match="must remain explicit"):
        raw_metadata.validate_dry_run_derived_rows_remain_explicit(rows)


def test_committed_raw_metadata_response_table_remains_header_only() -> None:
    rows = raw_metadata.read_raw_metadata_response_rows()

    assert rows.is_empty()
    assert rows.columns == list(raw_metadata.REQUIRED_COLUMNS)
