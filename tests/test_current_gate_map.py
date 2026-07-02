from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_current_gate_map_lists_expected_gates() -> None:
    text = read_doc("docs/current_gate_map.md")

    for gate in [
        "Gate 0",
        "Gate 1",
        "Gate 2",
        "Gate 3",
        "Gate 4",
        "Gate 5",
        "Gate 6",
        "Gate 7",
        "Gate 8",
        "Gate 9",
        "Gate 10",
        "Gate 11",
        "Gate 12",
    ]:
        assert gate in text


def test_current_gate_map_distinguishes_current_calibration_lanes() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "SIRT6/core3" in text
    assert "first calibration lane" in text
    assert "TP53/MDM2 elephant" in text
    assert "second calibration lane" in text
    assert "beneficial_breakage" in text


def test_current_gate_map_records_generic_coverage_helper_adoption() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "both calibration lanes now expose generic coverage-helper traces" in text
    assert "TP53/MDM2 uses the generic coverage helper" in text
    assert "SIRT6 uses the generic coverage helper" in text
    assert "generic coverage preflight helper exists" in text


def test_current_gate_map_records_generic_control_helper_adoption() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "generic control readiness schema exists" in text
    assert "generic control readiness helper exists" in text
    assert "candidate contrast gate records generic control-helper traces" in text


def test_current_gate_map_records_generic_strict_panel_schema_helper_and_builder() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "generic strict contrast panel helper exists" in text
    assert "SIRT6 strict panel summary records generic strict panel helper trace" in text
    assert "generic strict panel runtime builder exists" in text
    assert "TP53/MDM2 uses the generic strict panel builder" in text
    assert "TP53/MDM2 preflight now emits a generic strict panel summary" in text


def test_current_gate_map_records_next_gate8_frontier() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "generic gated contrast runtime into additional calibration lanes beyond SIRT6" in text
    assert "generic gated contrast runtime into calibration lanes" not in text
    assert "contrast robustness flags" not in text


def test_current_gate_map_records_generic_gated_contrast_runtime() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert (
        "generic Gate 8 gated contrast schema, helper, runtime calculator, "
        "robustness annotations, SIRT6 generic input bridge, and SIRT6 generic "
        "dry-run wrapper now exist"
    ) in text
    assert "generic gated contrast schema exists" in text
    assert "generic gated contrast helper exists" in text
    assert "generic gated contrast runtime calculator exists" in text
    assert "generic gated contrast runtime records contrast robustness annotations" in text


def test_current_gate_map_contains_claim_policy_guardrails() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "technical checkpoint" in text
    assert "validated longevity signal" in text
    assert "proven pro-longevity variant" in text
    assert "Disallowed language" in text


def test_current_gate_map_records_sirt6_generic_gate8_dry_run_path() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "generic Gate 8 input bridge exists" in text
    assert "generic Gate 8 dry-run wrapper exists" in text
    assert "SIRT6 generic gated contrast input bridge exists" in text
    assert "SIRT6 generic gated contrast dry-run wrapper exists" in text


def test_current_gate_map_records_generic_cofolding_readiness_schema() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "generic Gate 9 cofolding readiness schema" in text
    assert "the generic cofolding readiness schema exists" in text


def test_current_gate_map_records_generic_cofolding_readiness_helper() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert (
        "generic Gate 9 cofolding readiness schema, helper, and runtime checklist now exist" in text
    )
    assert "the generic cofolding readiness helper exists" in text
    assert "generic dry-run manifest builder now exists" in text
    assert "SIRT6 Gate 9 context builder and dry-run path are now recorded" in text
    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert "additional lane context builders pending" in text


def test_current_gate_map_records_generic_cofolding_readiness_runtime() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert (
        "generic Gate 9 cofolding readiness schema, helper, and runtime checklist now exist" in text
    )
    assert "the generic cofolding readiness runtime checklist exists" in text
    assert "generic dry-run manifest builder now exists" in text
    assert "SIRT6 Gate 9 context builder and dry-run path are now recorded" in text
    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert "additional lane context builders pending" in text


def test_current_gate_map_records_generic_cofolding_dry_run_manifest() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "generic dry-run manifest builder now exists" in text
    assert "the generic cofolding dry-run manifest builder exists" in text
    assert "SIRT6 Gate 9 context builder and dry-run path are now recorded" in text
    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert "additional lane context builders pending" in text


def test_current_gate_map_records_sirt6_cofolding_readiness_context_builder() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "SIRT6 Gate 9 context builder and dry-run path are now recorded" in text
    assert "the SIRT6 Gate 9 cofolding context builder exists" in text
    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert "additional lane context builders pending" in text


def test_current_gate_map_records_sirt6_gate9_dry_run_path() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "SIRT6 Gate 9 context builder and dry-run path are now recorded" in text
    assert "the SIRT6 Gate 9 dry-run path is recorded" in text
    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert "additional lane context builders pending" in text
    assert "genericdry-run" not in text


def test_current_gate_map_records_tp53_mdm2_generic_gate8_blocked_summary() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "TP53/MDM2 now emits a generic Gate 8 blocked summary" in text
    assert (
        "TP53/MDM2 emits a generic Gate 8 blocked summary while coverage remains unresolved" in text
    )
    assert "not a validated biological claim" in text


def test_current_gate_map_records_tp53_mdm2_gate9_blocked_context() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert (
        "TP53/MDM2 emits a generic Gate 9 blocked context while coverage remains unresolved" in text
    )
    assert "additional lane context builders pending" in text
    assert "not a validated biological claim" in text


def test_current_gate_map_records_tp53_mdm2_gate9_blocked_dry_run_path() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert (
        "TP53/MDM2 Gate 9 blocked context builder and blocked dry-run path are now recorded" in text
    )
    assert "TP53/MDM2 Gate 9 blocked dry-run path is recorded" in text
    assert "empty eligible manifest expectation" in text
    assert "additional lane context builders pending" in text


def test_current_gate_map_records_gate8_gate9_calibration_roadmap_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Gate 8/Gate 9 calibration checkpoint" in text
    assert "SIRT6 has a recorded dry-run path" in text
    assert "TP53/MDM2 has a recorded blocked dry-run path" in text
    assert "the Gate 8/Gate 9 calibration-lane roadmap checkpoint is recorded" in text
    assert "genericdry-run" not in text
    assert "calculator,robustness" not in text
