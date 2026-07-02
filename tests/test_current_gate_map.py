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


def test_current_gate_map_records_gate_aware_embedding_fill_plan() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "gate-aware embedding fill plan is now recorded" in text
    assert "docs/gate_aware_embedding_fill_plan.md" in text
    assert "does not call Biohub" in text
    assert "genericdry-run" not in text
    assert "calculator,robustness" not in text


def test_current_gate_map_records_controlled_embedding_fill_protocol() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "controlled embedding fill protocol is now recorded" in text
    assert "docs/controlled_embedding_fill_protocol.md" in text
    assert "Brandt's bat `P09874` precedent" in text
    assert "sequence_length_status == matches" in text
    assert "explicit `--yes-live` approval" in text
    assert "no committed `data/output/` artifacts" in text
    assert "no enrichment/contrast rerun by default" in text
    assert "no Boltz calls" in text
    assert "no biological claims" in text


def test_current_gate_map_records_controlled_embedding_fill_worklist_schema() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "controlled embedding fill worklist schema is now recorded" in text
    assert "data/config/controlled_embedding_fill_worklist_schema.yaml" in text
    assert "machine-readable fill statuses" in text
    assert "`--yes-live` opt-in requirements" in text
    assert "sequence_length_status == matches" in text
    assert "no committed `data/output/` artifacts" in text
    assert "no Biohub calls from schema checks" in text
    assert "no Boltz calls" in text
    assert "no enrichment/contrast rerun" in text
    assert "no biological claims" in text


def test_current_gate_map_records_controlled_embedding_fill_worklist_builder() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "controlled embedding fill worklist builder is now recorded" in text
    assert "src/longevity_port_pipelines/stages/controlled_embedding_fill_worklist.py" in text
    assert "table-only dry-run worklist builder" in text
    assert "data/config/controlled_embedding_fill_worklist_schema.yaml" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not commit `data/output/` artifacts" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment/contrast" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_brandts_bat_p09874_controlled_fill_noop_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Brandt's bat P09874 controlled fill no-op checkpoint" in text
    assert "controlled_embedding_fill_worklist_brandts_bat_p09874_checkpoint.csv" in text
    assert "no-op table-only checkpoint" in text
    assert "fill_status: do_not_fill" in text
    assert "allowed_next_action: do_not_fill" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not commit `data/output/` artifacts" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment/contrast" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_controlled_missing_embedding_blocker_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Controlled missing embedding blocker checkpoint" in text
    assert "docs/controlled_missing_embedding_blocker_checkpoint.md" in text
    assert "8f86" in text
    assert "P84233" in text
    assert "blocked by missing ortholog coverage" in text
    assert "not selected for controlled dry-run or live fill" in text
    assert "coverage/provenance repair before any new embedding dry-run candidate selection" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not use `curated_embedding_single --yes-live`" in text
    assert "does not commit `data/output/` embedding artifacts" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment/contrast" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_coverage_provenance_repair_queue_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Coverage/provenance repair queue checkpoint" in text
    assert "docs/coverage_provenance_repair_queue_checkpoint.md" in text
    assert "Gate 4 / Gate 5 repair frontier" in text
    assert "SIRT6/core3 has 11 rows" in text
    assert "data/input/sirt6_candidate_coverage_repair_decisions.csv" in text
    assert "TP53/MDM2 elephant has two blocked seed rows" in text
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in text
    assert "coverage/provenance blockers" in text
    assert (
        "must not be bypassed by embedding fill, contrast, cofolding, live structural calls, or biological claims"
        in text
    )


def test_current_gate_map_records_tp53_mdm2_generic_repair_alignment_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "TP53/MDM2 generic repair alignment checkpoint" in text
    assert "docs/tp53_mdm2_generic_repair_alignment_checkpoint.md" in text
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in text
    assert "`lane_name`" in text
    assert "`source_species`" in text
    assert "`gene_symbol`" in text
    assert "`target_uniprot`" in text
    assert "`coverage_status`" in text
    assert "`provenance_status`" in text
    assert "`repair_status`" in text
    assert "`reviewer_note`" in text
    assert "`target_uniprot` is `unresolved`" in text
    assert "`coverage_status` is `unresolved_downstream_provenance`" in text
    assert "`provenance_status` is `unresolved`" in text
    assert "`repair_status` is `pending`" in text
    assert "does not fetch sequences" in text
    assert "does not resolve elephant orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote cofolding readiness" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_generic_repair_queue_summary_builder_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Generic repair queue summary builder checkpoint" in text
    assert "docs/generic_repair_queue_summary_builder_checkpoint.md" in text
    assert "data/input/sirt6_candidate_coverage_repair_decisions.csv" in text
    assert "data/input/tp53_mdm2_ortholog_repair_decisions.csv" in text
    assert "produce 13 repair queue rows" in text
    assert "11 SIRT6/core3 rows" in text
    assert "2 TP53/MDM2 elephant rows" in text
    assert "`repair_queue_status`" in text
    assert "`downstream_block_status`" in text
    assert "`allowed_next_action`" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_generic_repair_queue_usage_guide() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Generic repair queue usage guide" in text
    assert "docs/generic_repair_queue_usage_guide.md" in text
    assert "generic-repair-queue-summary" in text
    assert "repair_queue_status" in text
    assert "downstream_block_status" in text
    assert "allowed_next_action" in text
    assert "repair-planning signals rather than downstream permissions" in text
    assert "13 rows" in text
    assert "11 SIRT6/core3 rows" in text
    assert "2 TP53/MDM2 elephant rows" in text
    assert "keeps downstream gates blocked" in text
    assert "does not authorize sequence fetch" in text
    assert "manual ortholog curation" in text
    assert "Biohub calls" in text
    assert "embedding generation" in text
    assert "Boltz calls" in text
    assert "Gate 8 promotion" in text
    assert "Gate 9 promotion" in text
    assert "biological claims" in text


def test_current_gate_map_records_generic_repair_queue_review_checklist() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "Generic repair queue review checklist" in text
    assert "docs/generic_repair_queue_review_checklist.md" in text
    assert "reviewed-for-planning provenance evidence" in text
    assert "valid blocked repair-queue worklist item" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_generic_repair_queue_review_schema() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "Generic repair queue reviewed-decision schema" in text
    assert "data/config/generic_repair_queue_review_schema.yaml" in text
    assert "manual provenance review decisions" in text
    assert "machine-readably" in text
    assert "review decision vocabulary" in text
    assert "downstream blocking policy" in text
    assert "does not record a reviewed biological provenance row by itself" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_first_sirt6_manual_provenance_review_fixture() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "First SIRT6 manual provenance review fixture" in text
    assert "data/input/generic_repair_queue_review_decisions.csv" in text
    assert "docs/sirt6_manual_provenance_review_checkpoint.md" in text
    assert "Level 1 biological provenance data" in text
    assert "unreviewed Gate 4 / Gate 5 blocker" in text
    assert "reviewed-for-planning provenance evidence" in text
    assert "deferred provenance decision" in text
    assert "valid blocked repair-queue worklist item" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs globally" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_generic_repair_queue_review_overlay() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "Generic repair queue reviewed-decision overlay" in text
    assert "data/input/generic_repair_queue_review_decisions.csv" in text
    assert "already-reviewed Gate 4 / Gate 5 provenance decisions" in text
    assert "Deferred decisions remain blocked at Gate 4 / Gate 5" in text
    assert "do not become downstream eligibility" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment or contrast" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text
