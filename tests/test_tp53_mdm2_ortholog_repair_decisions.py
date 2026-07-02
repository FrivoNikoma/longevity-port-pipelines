from pathlib import Path

import polars as pl
import pytest

from longevity_port_pipelines.stages import tp53_mdm2_ortholog_repair_decisions as repair


def repair_rows() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "candidate_set": "tp53_mdm2_elephant",
                "candidate_id": "tp53_mdm2_elephant_seed_tp53_chain",
                "lane_name": "tp53_mdm2_elephant",
                "pdb_id": "1ycr",
                "chain": "B",
                "source_species": "human",
                "target_species": "elephant",
                "gene_symbol": "TP53",
                "source_uniprot": "P04637",
                "partner_uniprot": "Q00987",
                "target_uniprot": "unresolved",
                "coverage_preflight_status": "blocked_pending_coverage_repair",
                "source_ortholog_status": "not_checked",
                "local_candidate_row_status": "not_checked",
                "coverage_status": "unresolved_downstream_provenance",
                "provenance_status": "unresolved",
                "recommended_next_action": ("curate_or_fetch_tp53_mdm2_source_ortholog_coverage"),
                "repair_decision": "fetch_or_curate_source_ortholog",
                "repair_status": "pending",
                "repair_priority": "high",
                "claim_policy": "ortholog_repair_only",
                "repair_note": (
                    "TP53 elephant pilot row remains blocked until source ortholog "
                    "provenance is fetched or manually curated."
                ),
                "reviewer_note": (
                    "Generic repair vocabulary alignment only; elephant target UniProt "
                    "remains unresolved and must be fetched or manually curated before "
                    "downstream eligibility."
                ),
            }
        ]
    )


def test_committed_tp53_mdm2_ortholog_repair_decision_table_is_valid() -> None:
    rows = repair.read_repair_decisions()

    repair.validate_repair_decisions(rows)

    assert rows.height == 2
    assert set(rows.get_column("candidate_set").to_list()) == {repair.EXPECTED_CANDIDATE_SET}
    assert set(rows.get_column("lane_name").to_list()) == {repair.EXPECTED_CANDIDATE_SET}
    assert set(rows.get_column("source_species").to_list()) == {"human"}
    assert set(rows.get_column("target_species").to_list()) == {"elephant"}
    assert set(rows.get_column("gene_symbol").to_list()) == {"TP53", "MDM2"}
    assert set(rows.get_column("target_uniprot").to_list()) == {"unresolved"}
    assert set(rows.get_column("repair_decision").to_list()) == {"fetch_or_curate_source_ortholog"}
    assert set(rows.get_column("repair_status").to_list()) == {"pending"}
    assert set(rows.get_column("repair_priority").to_list()) == {"high"}
    assert set(rows.get_column("claim_policy").to_list()) == {"ortholog_repair_only"}


def test_committed_tp53_mdm2_ortholog_repair_decision_table_covers_seed_rows() -> None:
    rows = repair.read_repair_decisions()

    assert set(rows.get_column("candidate_id").to_list()) == {
        "tp53_mdm2_elephant_seed_tp53_chain",
        "tp53_mdm2_elephant_seed_mdm2_chain",
    }
    assert set(rows.get_column("source_uniprot").to_list()) == {"P04637", "Q00987"}
    assert set(rows.get_column("partner_uniprot").to_list()) == {"P04637", "Q00987"}
    assert set(rows.get_column("target_species").to_list()) == {"elephant"}


def test_committed_tp53_mdm2_ortholog_repair_decision_table_keeps_coverage_blocked() -> None:
    rows = repair.read_repair_decisions()

    assert set(rows.get_column("coverage_preflight_status").to_list()) == {
        "blocked_pending_coverage_repair"
    }
    assert set(rows.get_column("source_ortholog_status").to_list()) == {"not_checked"}
    assert set(rows.get_column("local_candidate_row_status").to_list()) == {"not_checked"}
    assert set(rows.get_column("coverage_status").to_list()) == {"unresolved_downstream_provenance"}
    assert set(rows.get_column("provenance_status").to_list()) == {"unresolved"}
    assert set(rows.get_column("repair_status").to_list()) == {"pending"}


def test_generic_repair_columns_returns_schema_aligned_view() -> None:
    rows = repair.read_repair_decisions()

    generic_rows = repair.generic_repair_columns(rows)

    assert generic_rows.columns == list(repair.GENERIC_REPAIR_COLUMNS)
    assert generic_rows.height == 2
    assert set(generic_rows.get_column("coverage_status").to_list()) == {
        "unresolved_downstream_provenance"
    }
    assert set(generic_rows.get_column("provenance_status").to_list()) == {"unresolved"}
    assert set(generic_rows.get_column("repair_status").to_list()) == {"pending"}


def test_blocked_generic_repair_rows_keeps_tp53_mdm2_out_of_downstream_gates() -> None:
    rows = repair.read_repair_decisions()

    blocked_rows = repair.blocked_generic_repair_rows(rows)

    assert blocked_rows.height == 2
    assert set(blocked_rows.get_column("repair_status").to_list()) == {"pending"}
    assert set(blocked_rows.get_column("candidate_id").to_list()) == {
        "tp53_mdm2_elephant_seed_tp53_chain",
        "tp53_mdm2_elephant_seed_mdm2_chain",
    }


def test_validate_repair_decisions_accepts_valid_rows() -> None:
    repair.validate_repair_decisions(repair_rows())


def test_validate_repair_decisions_rejects_missing_columns() -> None:
    rows = repair_rows().drop("claim_policy")

    with pytest.raises(ValueError, match="missing required columns"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_duplicate_keys() -> None:
    rows = pl.concat([repair_rows(), repair_rows()])

    with pytest.raises(ValueError, match="duplicate"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_wrong_candidate_set() -> None:
    rows = repair_rows().with_columns(pl.lit("sirt6_dna_repair").alias("candidate_set"))

    with pytest.raises(ValueError, match="invalid values in candidate_set"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_wrong_lane_name() -> None:
    rows = repair_rows().with_columns(pl.lit("sirt6_dna_repair").alias("lane_name"))

    with pytest.raises(ValueError, match="invalid values in lane_name"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_gene_symbol() -> None:
    rows = repair_rows().with_columns(pl.lit("SIRT6").alias("gene_symbol"))

    with pytest.raises(ValueError, match="invalid values in gene_symbol"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_coverage_status() -> None:
    rows = repair_rows().with_columns(pl.lit("claim_ready").alias("coverage_status"))

    with pytest.raises(ValueError, match="invalid values in coverage_status"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_provenance_status() -> None:
    rows = repair_rows().with_columns(pl.lit("validated").alias("provenance_status"))

    with pytest.raises(ValueError, match="invalid values in provenance_status"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_repair_status() -> None:
    rows = repair_rows().with_columns(pl.lit("ready_for_claim").alias("repair_status"))

    with pytest.raises(ValueError, match="invalid values in repair_status"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_repair_decision() -> None:
    rows = repair_rows().with_columns(
        pl.lit("claim_ready_without_ortholog").alias("repair_decision")
    )

    with pytest.raises(ValueError, match="invalid values in repair_decision"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_invalid_claim_policy() -> None:
    rows = repair_rows().with_columns(pl.lit("biological_claim").alias("claim_policy"))

    with pytest.raises(ValueError, match="invalid values in claim_policy"):
        repair.validate_repair_decisions(rows)


def test_validate_repair_decisions_rejects_blank_decision_fields() -> None:
    rows = repair_rows().with_columns(pl.lit("").alias("reviewer_note"))

    with pytest.raises(ValueError, match="blank required decision fields"):
        repair.validate_repair_decisions(rows)


def test_default_repair_decision_path_points_to_committed_input() -> None:
    assert (
        Path("data/input/tp53_mdm2_ortholog_repair_decisions.csv")
        == repair.DEFAULT_REPAIR_DECISIONS_PATH
    )


def test_committed_tp53_mdm2_ortholog_repair_decision_table_does_not_make_claims() -> None:
    rows = repair.read_repair_decisions()

    forbidden_values = {
        "biological_claim",
        "validated_biological_signal",
        "eligible_for_cofolding_live_run",
        "submit_live_boltz_now",
        "coverage_ready_for_claim",
        "validated_ortholog",
        "confirmed_conserved_function",
    }

    observed_values = set()
    for column in rows.columns:
        observed_values.update(str(value) for value in rows.get_column(column).to_list())

    assert observed_values.isdisjoint(forbidden_values)
