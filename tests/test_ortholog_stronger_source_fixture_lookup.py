from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import (
    ortholog_stronger_source_fixture_lookup as fixture_lookup,
)


def valid_fixture_plan_row() -> dict[str, str]:
    return {
        "candidate_set": "tp53_mdm2_elephant",
        "lane_name": "tp53_mdm2_elephant",
        "candidate_id": "tp53_mdm2_elephant_seed_mdm2_chain",
        "request_table": "data/input/ortholog_stronger_source_evidence_requests.csv",
        "request_source_row_index": "1",
        "gene_symbol": "MDM2",
        "source_species": "human",
        "target_species": "elephant",
        "target_species_taxid": "9785",
        "source_uniprot": "Q00987",
        "partner_uniprot": "P04637",
        "requested_evidence_source_database": "UniProtKB TrEMBL",
        "requested_evidence_source_accession": "G3SX30",
        "target_taxid": "9785",
        "target_species_name": "Loxodonta africana",
        "target_gene_symbol": "MDM2",
        "target_protein_accession": "G3SX30",
        "target_sequence_length": "492",
        "planned_lookup_source_type": "reviewed_uniprot",
        "planned_lookup_source_name": "UniProt reviewed entry lookup",
        "planned_lookup_query_identifier": "G3SX30",
        "planned_lookup_query_taxid": "9785",
        "planned_lookup_mode": "fixture_backed_only",
        "live_lookup_allowed": "false",
        "sequence_fetch_allowed": "false",
        "planned_output_target": ("data/input/ortholog_stronger_source_raw_metadata_responses.csv"),
        "lookup_plan_status": "lookup_planned_still_blocked",
        "downstream_block_status_after_lookup_plan": "blocked_gate4_gate5",
        "allowed_next_action_after_lookup_plan": "add_fixture_backed_lookup_client",
        "claim_policy_after_lookup_plan": "no_biological_claims_until_validation",
        "claim_status_after_lookup_plan": "repair_worklist",
        "forbidden_actions_after_lookup_plan": (
            "live external database lookup; source evidence collection; "
            "ortholog acceptance; curated ortholog candidate creation; "
            "standard ortholog coverage population; reviewed decision creation; "
            "Gate 4 or Gate 5 policy update; sequence fetch; Biohub call; "
            "embedding generation; Boltz call; AF3 call; Chai call; "
            "enrichment rerun; contrast rerun; Gate 8 promotion; "
            "Gate 9 promotion; biological claim"
        ),
        "reviewer_note": "Synthetic fixture-backed lookup test row; still blocked.",
    }


def valid_fixture_plan_rows() -> pl.DataFrame:
    return pl.DataFrame([valid_fixture_plan_row()])


def read_committed_fixture_rows() -> pl.DataFrame:
    return fixture_lookup.read_fixture_lookup_result_rows()


def test_default_fixture_path_points_under_tests_fixtures() -> None:
    path = fixture_lookup.DEFAULT_FIXTURE_LOOKUP_RESULTS_PATH

    assert path == Path("tests/fixtures/ortholog_stronger_source_fixture_lookup_results.csv")
    assert "data/" not in path.as_posix()


def test_committed_fixture_file_exists_and_has_expected_rows() -> None:
    rows = read_committed_fixture_rows()

    assert rows.height == 2
    assert rows.columns == list(fixture_lookup.REQUIRED_COLUMNS)
    assert set(rows.get_column("fixture_lookup_status").to_list()) == {
        "fixture_hit_still_blocked",
        "fixture_miss_still_blocked",
    }


def test_committed_fixture_rows_validate() -> None:
    rows = read_committed_fixture_rows()

    fixture_lookup.validate_fixture_lookup_result_rows(rows)


def test_committed_fixture_rows_are_not_evidence_or_downstream_permission() -> None:
    rows = read_committed_fixture_rows()

    assert set(rows.get_column("fixture_result_is_evidence").to_list()) == {"false"}
    assert set(rows.get_column("fixture_result_block_status").to_list()) == {"blocked_gate4_gate5"}
    assert set(rows.get_column("fixture_result_claim_status").to_list()) == {"repair_worklist"}


def test_committed_fixture_rows_do_not_encode_forbidden_claim_text() -> None:
    text = fixture_lookup.DEFAULT_FIXTURE_LOOKUP_RESULTS_PATH.read_text(encoding="utf-8")
    forbidden_text = (
        "accepted_ortholog",
        "validated_ortholog",
        "Gate 8 eligible",
        "Gate 9 eligible",
        "embedding ready",
        "Biohub ready",
        "Boltz ready",
        "AF3 ready",
        "Chai ready",
        "safe_to_port",
        "safe to port",
    )

    for value in forbidden_text:
        assert value not in text


def test_empty_fixture_lookup_result_rows_preserves_schema() -> None:
    rows = fixture_lookup.empty_fixture_lookup_result_rows()

    assert rows.height == 0
    assert rows.columns == list(fixture_lookup.REQUIRED_COLUMNS)


def test_missing_required_columns_reports_missing_fixture_column() -> None:
    rows = read_committed_fixture_rows().drop("fixture_result_is_evidence")

    assert fixture_lookup.missing_required_columns(rows) == ["fixture_result_is_evidence"]


def test_validate_required_columns_rejects_missing_fixture_column() -> None:
    rows = read_committed_fixture_rows().drop("fixture_lookup_result_id")

    with pytest.raises(ValueError, match="missing required columns"):
        fixture_lookup.validate_required_columns(rows)


def test_validate_allowed_values_rejects_evidence_true() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("true").alias("fixture_result_is_evidence")
    )

    with pytest.raises(ValueError, match="fixture_result_is_evidence"):
        fixture_lookup.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_gate8_block_status() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("Gate 8 eligible").alias("fixture_result_block_status")
    )

    with pytest.raises(ValueError, match="fixture_result_block_status"):
        fixture_lookup.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_unsafe_lookup_status() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("fixture_hit_unblocked").alias("fixture_lookup_status")
    )

    with pytest.raises(ValueError, match="fixture_lookup_status"):
        fixture_lookup.validate_allowed_values(rows)


def test_validate_allowed_values_rejects_unknown_review_status() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("validated").alias("fixture_payload_review_status")
    )

    with pytest.raises(ValueError, match="fixture_payload_review_status"):
        fixture_lookup.validate_allowed_values(rows)


def test_duplicate_fixture_result_ids_accepts_committed_fixture() -> None:
    rows = read_committed_fixture_rows()
    duplicates = fixture_lookup.duplicate_fixture_result_ids(rows)

    assert duplicates.height == 0


def test_validate_unique_fixture_result_ids_rejects_duplicate_ids() -> None:
    rows = read_committed_fixture_rows()
    duplicate_rows = pl.concat([rows, rows])

    with pytest.raises(ValueError, match="duplicate fixture lookup result ids"):
        fixture_lookup.validate_unique_fixture_result_ids(duplicate_rows)


def test_validate_no_blank_required_fields_rejects_blank_fixture_field() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("").alias("fixture_payload_source_name")
    )

    with pytest.raises(ValueError, match="blank required fixture fields"):
        fixture_lookup.validate_no_blank_required_fields(rows)


def test_validate_positive_integer_fields_accepts_unresolved_sequence_length() -> None:
    rows = read_committed_fixture_rows().filter(
        pl.col("fixture_lookup_status") == "fixture_miss_still_blocked"
    )

    fixture_lookup.validate_positive_integer_fields(rows)


def test_validate_positive_integer_fields_rejects_bad_taxid() -> None:
    rows = read_committed_fixture_rows().with_columns(pl.lit("0").alias("fixture_payload_taxid"))

    with pytest.raises(ValueError, match="invalid positive-integer fixture metadata"):
        fixture_lookup.validate_positive_integer_fields(rows)


def test_validate_positive_integer_fields_rejects_bad_sequence_length() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("not_a_length").alias("fixture_payload_sequence_length")
    )

    with pytest.raises(ValueError, match="fixture_payload_sequence_length"):
        fixture_lookup.validate_positive_integer_fields(rows)


def test_validate_no_disallowed_fixture_text_rejects_validated_ortholog() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("validated_ortholog").alias("fixture_result_note")
    )

    with pytest.raises(ValueError, match="disallowed fixture lookup text values"):
        fixture_lookup.validate_no_disallowed_fixture_text(rows)


def test_validate_no_disallowed_fixture_text_rejects_biohub_ready() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("Biohub ready").alias("fixture_result_note")
    )

    with pytest.raises(ValueError, match="disallowed fixture lookup text values"):
        fixture_lookup.validate_no_disallowed_fixture_text(rows)


def test_validate_no_disallowed_fixture_text_rejects_boltz_ready() -> None:
    rows = read_committed_fixture_rows().with_columns(
        pl.lit("Boltz ready").alias("fixture_result_note")
    )

    with pytest.raises(ValueError, match="disallowed fixture lookup text values"):
        fixture_lookup.validate_no_disallowed_fixture_text(rows)


def test_fixture_backed_lookup_plan_rows_keeps_only_fixture_mode() -> None:
    fixture_row = valid_fixture_plan_row()
    dry_run_row = valid_fixture_plan_row() | {
        "planned_lookup_source_type": "oma_orthology",
        "planned_lookup_source_name": "OMA dry-run lookup",
        "planned_lookup_mode": "dry_run_plan_only",
    }
    rows = pl.DataFrame([fixture_row, dry_run_row])

    selected = fixture_lookup.fixture_backed_lookup_plan_rows(rows)

    assert selected.height == 1
    assert selected.item(0, "planned_lookup_mode") == "fixture_backed_only"
    assert selected.item(0, "planned_lookup_source_type") == "reviewed_uniprot"


def test_lookup_fixture_results_for_plan_rows_returns_matching_fixture_hit() -> None:
    plan_rows = valid_fixture_plan_rows()
    fixture_rows = read_committed_fixture_rows()

    results = fixture_lookup.lookup_fixture_results_for_plan_rows(
        plan_rows,
        fixture_rows,
    )

    assert results.height == 1
    assert results.columns == list(fixture_lookup.REQUIRED_COLUMNS)
    assert results.item(0, "fixture_lookup_result_id") == ("synthetic_mdm2_reviewed_uniprot_hit")
    assert results.item(0, "fixture_result_block_status") == "blocked_gate4_gate5"
    assert results.item(0, "fixture_result_claim_status") == "repair_worklist"
    assert results.item(0, "fixture_result_is_evidence") == "false"


def test_lookup_fixture_results_for_plan_rows_returns_empty_for_dry_run_only() -> None:
    row = valid_fixture_plan_row() | {"planned_lookup_mode": "dry_run_plan_only"}
    plan_rows = pl.DataFrame([row])
    fixture_rows = read_committed_fixture_rows()

    results = fixture_lookup.lookup_fixture_results_for_plan_rows(
        plan_rows,
        fixture_rows,
    )

    assert results.height == 0
    assert results.columns == list(fixture_lookup.REQUIRED_COLUMNS)


def test_lookup_fixture_results_for_plan_rows_returns_empty_for_no_match() -> None:
    row = valid_fixture_plan_row() | {
        "planned_lookup_query_identifier": "NO_MATCH_SYNTHETIC_ACCESSION"
    }
    plan_rows = pl.DataFrame([row])
    fixture_rows = read_committed_fixture_rows()

    results = fixture_lookup.lookup_fixture_results_for_plan_rows(
        plan_rows,
        fixture_rows,
    )

    assert results.height == 0
    assert results.columns == list(fixture_lookup.REQUIRED_COLUMNS)


def test_lookup_fixture_results_from_default_fixture_reads_committed_fixture() -> None:
    results = fixture_lookup.lookup_fixture_results_from_default_fixture(valid_fixture_plan_rows())

    assert results.height == 1
    assert results.item(0, "fixture_lookup_result_id") == ("synthetic_mdm2_reviewed_uniprot_hit")


def test_fixture_lookup_module_does_not_import_network_libraries() -> None:
    source = Path(
        "src/longevity_port_pipelines/stages/ortholog_stronger_source_fixture_lookup.py"
    ).read_text(encoding="utf-8")

    forbidden_imports = (
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import urllib",
        "from urllib",
        "import socket",
        "from socket",
    )

    for forbidden in forbidden_imports:
        assert forbidden not in source


def test_fixture_lookup_module_does_not_reference_live_lookup_terms_as_actions() -> None:
    source = Path(
        "src/longevity_port_pipelines/stages/ortholog_stronger_source_fixture_lookup.py"
    ).read_text(encoding="utf-8")

    forbidden_action_terms = (
        "requests.get",
        "httpx.get",
        "urlopen",
        "socket.",
    )

    for forbidden in forbidden_action_terms:
        assert forbidden not in source
