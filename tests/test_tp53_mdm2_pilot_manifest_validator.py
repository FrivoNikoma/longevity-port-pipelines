import polars as pl
import pytest

from longevity_port_pipelines.stages.tp53_mdm2_pilot_manifest_validator import (
    EXPECTED_BIOLOGICAL_MODE,
    EXPECTED_BREAKAGE_INTERPRETATION_POLICY,
    EXPECTED_CANDIDATE_SET,
    EXPECTED_CLAIM_POLICY,
    validate_tp53_mdm2_pilot_manifest,
)


def valid_manifest_rows() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "candidate_set": [EXPECTED_CANDIDATE_SET, EXPECTED_CANDIDATE_SET],
            "biological_mode": [
                EXPECTED_BIOLOGICAL_MODE,
                EXPECTED_BIOLOGICAL_MODE,
            ],
            "candidate_id": ["tp53_mdm2_elephant_001", "tp53_mdm2_elephant_002"],
            "pdb_id": ["1ycr", "1ycr"],
            "chain": ["A", "B"],
            "source_uniprot": ["P04637", "Q00987"],
            "partner_uniprot": ["Q00987", "P04637"],
            "target_species": ["elephant", "elephant"],
            "strict_contrast_gate_status": [
                "eligible_for_contrast_dry_run",
                "blocked_negatome_controls",
            ],
            "contrast_checkpoint_policy": [
                EXPECTED_CLAIM_POLICY,
                EXPECTED_CLAIM_POLICY,
            ],
            "cofolding_plan_status": [
                "eligible_for_cofolding_dry_run",
                "blocked_pending_negatome_repair",
            ],
            "breakage_interpretation_policy": [
                EXPECTED_BREAKAGE_INTERPRETATION_POLICY,
                EXPECTED_BREAKAGE_INTERPRETATION_POLICY,
            ],
            "claim_policy": [EXPECTED_CLAIM_POLICY, EXPECTED_CLAIM_POLICY],
        }
    )


def test_validate_tp53_mdm2_pilot_manifest_accepts_valid_rows() -> None:
    validate_tp53_mdm2_pilot_manifest(valid_manifest_rows())


def test_validate_tp53_mdm2_pilot_manifest_accepts_empty_schema() -> None:
    empty = valid_manifest_rows().head(0)

    validate_tp53_mdm2_pilot_manifest(empty)


def test_validate_tp53_mdm2_pilot_manifest_rejects_missing_columns() -> None:
    frame = valid_manifest_rows().drop("breakage_interpretation_policy")

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_blank_required_fields() -> None:
    frame = valid_manifest_rows().with_columns(pl.lit("").alias("source_uniprot"))

    with pytest.raises(ValueError, match="Blank required fields"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_duplicate_keys() -> None:
    row = valid_manifest_rows().head(1)
    frame = pl.concat([row, row])

    with pytest.raises(ValueError, match="Duplicate TP53/MDM2 manifest keys"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_wrong_candidate_set() -> None:
    frame = valid_manifest_rows().with_columns(pl.lit("sirt6_dna_repair").alias("candidate_set"))

    with pytest.raises(ValueError, match="Invalid candidate_set"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_wrong_biological_mode() -> None:
    frame = valid_manifest_rows().with_columns(
        pl.lit("maintained_interaction").alias("biological_mode")
    )

    with pytest.raises(ValueError, match="Invalid biological_mode"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_wrong_breakage_policy() -> None:
    frame = valid_manifest_rows().with_columns(
        pl.lit("auto_classify_breakage_as_incompatibility").alias("breakage_interpretation_policy")
    )

    with pytest.raises(ValueError, match="Invalid breakage_interpretation_policy"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_claim_policy() -> None:
    frame = valid_manifest_rows().with_columns(pl.lit("biological_claim").alias("claim_policy"))

    with pytest.raises(ValueError, match="Invalid claim_policy"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_wrong_contrast_policy() -> None:
    frame = valid_manifest_rows().with_columns(
        pl.lit("validated_biological_signal").alias("contrast_checkpoint_policy")
    )

    with pytest.raises(ValueError, match="Invalid contrast_checkpoint_policy"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_unknown_gate_status() -> None:
    frame = valid_manifest_rows().with_columns(
        pl.lit("validated_for_live_boltz").alias("strict_contrast_gate_status")
    )

    with pytest.raises(ValueError, match="Invalid strict_contrast_gate_status"):
        validate_tp53_mdm2_pilot_manifest(frame)


def test_validate_tp53_mdm2_pilot_manifest_rejects_unknown_cofolding_status() -> None:
    frame = valid_manifest_rows().with_columns(
        pl.lit("submit_live_boltz_now").alias("cofolding_plan_status")
    )

    with pytest.raises(ValueError, match="Invalid cofolding_plan_status"):
        validate_tp53_mdm2_pilot_manifest(frame)
