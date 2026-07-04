from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import polars as pl

DEFAULT_POLICY_UPDATES_PATH = Path("data/input/ortholog_evidence_gate45_policy_updates.csv")

NO_BIOLOGICAL_CLAIMS_POLICY = "no_biological_claims_until_validation"
REPAIR_WORKLIST_CLAIM_STATUS = "repair_worklist"
BLOCKED_GATE4_GATE5 = "blocked_gate4_gate5"
UPDATED_STILL_RUNTIME_BLOCKED = "gate45_policy_updated_still_runtime_blocked"

REQUIRED_COLUMNS = (
    "candidate_set",
    "lane_name",
    "candidate_id",
    "policy_source_table",
    "policy_source_row_index",
    "reviewed_target_uniprot",
    "reviewed_source_database",
    "reviewed_source_accession",
    "reviewed_taxid",
    "reviewed_sequence_length",
    "review_decision_before_policy",
    "downstream_block_status_before_policy",
    "allowed_next_action_before_policy",
    "claim_status_before_policy",
    "policy_update_decision",
    "gate4_status_after_policy",
    "gate5_status_after_policy",
    "downstream_block_status_after_policy",
    "allowed_next_action_after_policy",
    "claim_policy_after_policy",
    "claim_status_after_policy",
    "policy_update_note",
    "forbidden_actions_after_policy",
)

POLICY_UPDATE_KEY_COLUMNS = (
    "candidate_set",
    "candidate_id",
    "policy_source_table",
    "policy_source_row_index",
    "reviewed_source_database",
    "reviewed_source_accession",
)

ALLOWED_REVIEW_DECISIONS_BEFORE_POLICY = {"accepted_for_planning_after_review"}
ALLOWED_DOWNSTREAM_BLOCK_STATUSES_BEFORE_POLICY = {
    "reviewed_for_planning_still_policy_blocked",
}
ALLOWED_NEXT_ACTIONS_BEFORE_POLICY = {
    "consider_later_explicit_gate4_gate5_policy_update",
}

ALLOWED_POLICY_UPDATE_DECISIONS = {
    "approve_gate45_policy_update_for_planning",
    "reject_gate45_policy_update",
    "keep_policy_blocked_pending_review",
    "needs_additional_reviewed_evidence",
}

ALLOWED_DOWNSTREAM_BLOCK_STATUSES_AFTER_POLICY = {
    UPDATED_STILL_RUNTIME_BLOCKED,
    BLOCKED_GATE4_GATE5,
}

ALLOWED_NEXT_ACTIONS_AFTER_POLICY = {
    "prepare_later_gate_aware_embedding_fill_plan_pr",
    "keep_policy_blocked",
    "defer_until_additional_reviewed_evidence",
    "prepare_later_manual_policy_recheck",
}

POLICY_UPDATE_DECISION_EXPECTED_VALUES = {
    "approve_gate45_policy_update_for_planning": {
        "gate4_status_after_policy": "gate4_policy_updated_for_planning",
        "gate5_status_after_policy": "gate5_policy_updated_for_planning",
        "downstream_block_status_after_policy": UPDATED_STILL_RUNTIME_BLOCKED,
        "allowed_next_action_after_policy": "prepare_later_gate_aware_embedding_fill_plan_pr",
        "claim_status_after_policy": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "reject_gate45_policy_update": {
        "gate4_status_after_policy": BLOCKED_GATE4_GATE5,
        "gate5_status_after_policy": BLOCKED_GATE4_GATE5,
        "downstream_block_status_after_policy": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_policy": "keep_policy_blocked",
        "claim_status_after_policy": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "keep_policy_blocked_pending_review": {
        "gate4_status_after_policy": BLOCKED_GATE4_GATE5,
        "gate5_status_after_policy": BLOCKED_GATE4_GATE5,
        "downstream_block_status_after_policy": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_policy": "prepare_later_manual_policy_recheck",
        "claim_status_after_policy": REPAIR_WORKLIST_CLAIM_STATUS,
    },
    "needs_additional_reviewed_evidence": {
        "gate4_status_after_policy": BLOCKED_GATE4_GATE5,
        "gate5_status_after_policy": BLOCKED_GATE4_GATE5,
        "downstream_block_status_after_policy": BLOCKED_GATE4_GATE5,
        "allowed_next_action_after_policy": "defer_until_additional_reviewed_evidence",
        "claim_status_after_policy": REPAIR_WORKLIST_CLAIM_STATUS,
    },
}

RUNTIME_SIDE_EFFECTS = frozenset(
    {
        "sequence fetch",
        "Biohub call",
        "embedding generation",
        "Boltz call",
        "AF3 call",
        "Chai call",
        "enrichment rerun",
        "contrast rerun",
        "Gate 8 promotion",
        "Gate 9 promotion",
        "biological claim",
    }
)

DISALLOWED_CLAIM_VALUES = {
    "accepted_ortholog",
    "validated_ortholog",
    "validated_biological_signal",
    "validated_longevity_signal",
    "validated_biological_hit",
    "confirmed_binding_change",
    "confirmed_functional_effect",
    "Gate 8 eligible",
    "Gate 9 eligible",
    "embedding ready",
    "Biohub ready",
    "Boltz ready",
    "AF3 ready",
    "Chai ready",
    "safe_to_port",
    "safe to port",
    "proven_pro_longevity_variant",
}


def read_policy_update_rows(
    path: Path = DEFAULT_POLICY_UPDATES_PATH,
) -> pl.DataFrame:
    """Read explicit Gate 4 / Gate 5 policy update rows.

    This reader is table-only. It does not fetch sequences, call Biohub,
    generate embeddings, call Boltz/AF3/Chai, rerun enrichment or contrast,
    promote Gate 8 / Gate 9, or make biological claims.
    """

    return pl.read_csv(path, infer_schema_length=0)


def _text(row: Mapping[str, object], key: str) -> str:
    value = row.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def _missing_columns(rows: pl.DataFrame) -> list[str]:
    return [column for column in REQUIRED_COLUMNS if column not in rows.columns]


def _invalid_values(
    rows: pl.DataFrame,
    *,
    column: str,
    allowed_values: set[str],
) -> list[str]:
    if column not in rows.columns:
        return []

    return sorted(
        str(value).strip()
        for value in rows.get_column(column).unique().to_list()
        if str(value).strip() not in allowed_values
    )


def find_duplicate_policy_update_keys(rows: pl.DataFrame) -> pl.DataFrame:
    """Return duplicate explicit Gate 4 / Gate 5 policy update keys."""

    return (
        rows.group_by(list(POLICY_UPDATE_KEY_COLUMNS))
        .len(name="n_rows")
        .filter(pl.col("n_rows") > 1)
        .sort(list(POLICY_UPDATE_KEY_COLUMNS))
    )


def approved_policy_update_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return policy rows approved for planning but still runtime-blocked."""

    return rows.filter(
        pl.col("downstream_block_status_after_policy") == UPDATED_STILL_RUNTIME_BLOCKED
    )


def blocked_policy_update_rows(rows: pl.DataFrame) -> pl.DataFrame:
    """Return policy rows that keep Gate 4 / Gate 5 blocked."""

    return rows.filter(pl.col("downstream_block_status_after_policy") == BLOCKED_GATE4_GATE5)


def forbidden_actions_present(row: Mapping[str, object]) -> bool:
    """Return true when the row explicitly forbids all runtime side effects."""

    forbidden_actions = _text(row, "forbidden_actions_after_policy")
    return all(action in forbidden_actions for action in RUNTIME_SIDE_EFFECTS)


def _validate_reviewed_sequence_lengths(rows: pl.DataFrame) -> None:
    bad_values: list[str] = []
    for value in rows.get_column("reviewed_sequence_length").to_list():
        text = str(value).strip()
        if text == "unresolved":
            continue
        if not text.isdigit() or int(text) <= 0:
            bad_values.append(text)

    if bad_values:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table has invalid "
            "reviewed sequence lengths: " + ", ".join(sorted(set(bad_values)))
        )


def _validate_policy_update_rules(rows: pl.DataFrame) -> None:
    mismatches: list[str] = []
    for row in rows.iter_rows(named=True):
        decision = _text(row, "policy_update_decision")
        expected_values = POLICY_UPDATE_DECISION_EXPECTED_VALUES[decision]
        for column, expected_value in expected_values.items():
            if _text(row, column) != expected_value:
                mismatches.append(f"{_text(row, 'candidate_id')}:{column}")

    if mismatches:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table has "
            "decision-rule mismatches: " + ", ".join(sorted(mismatches))
        )


def _validate_required_forbidden_actions(rows: pl.DataFrame) -> None:
    missing: list[str] = []
    for row in rows.iter_rows(named=True):
        if not forbidden_actions_present(row):
            missing.append(_text(row, "candidate_id"))

    if missing:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table has rows "
            "missing required forbidden actions: " + ", ".join(sorted(missing))
        )


def _validate_no_disallowed_claim_values(rows: pl.DataFrame) -> None:
    observed_values: set[str] = set()
    for column in rows.columns:
        observed_values.update(str(value).strip() for value in rows.get_column(column).to_list())

    disallowed_observed = sorted(observed_values & DISALLOWED_CLAIM_VALUES)
    if disallowed_observed:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table contains "
            "disallowed claim values: " + ", ".join(disallowed_observed)
        )


def validate_policy_update_rows(rows: pl.DataFrame) -> None:
    """Validate policy update rows without creating runtime permission."""

    missing = _missing_columns(rows)
    if missing:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table is missing "
            "required columns: " + ", ".join(missing)
        )

    duplicate_keys = find_duplicate_policy_update_keys(rows)
    if duplicate_keys.height:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table has duplicate keys."
        )

    checks = {
        "review_decision_before_policy": ALLOWED_REVIEW_DECISIONS_BEFORE_POLICY,
        "downstream_block_status_before_policy": (ALLOWED_DOWNSTREAM_BLOCK_STATUSES_BEFORE_POLICY),
        "allowed_next_action_before_policy": ALLOWED_NEXT_ACTIONS_BEFORE_POLICY,
        "policy_update_decision": ALLOWED_POLICY_UPDATE_DECISIONS,
        "downstream_block_status_after_policy": (ALLOWED_DOWNSTREAM_BLOCK_STATUSES_AFTER_POLICY),
        "allowed_next_action_after_policy": ALLOWED_NEXT_ACTIONS_AFTER_POLICY,
        "claim_policy_after_policy": {NO_BIOLOGICAL_CLAIMS_POLICY},
        "claim_status_after_policy": {REPAIR_WORKLIST_CLAIM_STATUS},
    }
    for column, allowed_values in checks.items():
        invalid = _invalid_values(rows, column=column, allowed_values=allowed_values)
        if invalid:
            raise ValueError(
                "Ortholog evidence Gate 4 / Gate 5 policy update table has "
                f"invalid values in {column}: " + ", ".join(invalid)
            )

    blank_required: list[str] = []
    for column in REQUIRED_COLUMNS:
        if rows.filter(pl.col(column).str.strip_chars() == "").height:
            blank_required.append(column)

    if blank_required:
        raise ValueError(
            "Ortholog evidence Gate 4 / Gate 5 policy update table has blank "
            "required fields: " + ", ".join(blank_required)
        )

    _validate_reviewed_sequence_lengths(rows)
    _validate_policy_update_rules(rows)
    _validate_required_forbidden_actions(rows)
    _validate_no_disallowed_claim_values(rows)
