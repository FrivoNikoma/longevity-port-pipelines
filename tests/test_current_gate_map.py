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
    assert "`planning_policy_updated_runtime_blocked`" in text
    assert "`--yes-live` opt-in requirements" in text
    assert "sequence_length_status == matches" in text
    assert "no sequence fetch" in text
    assert "no committed `data/output/` artifacts" in text
    assert "no Biohub calls from schema checks" in text
    assert "no Gate 8 or Gate 9 promotion" in text
    assert "no Boltz/AF3/Chai calls" in text
    assert "no enrichment/contrast rerun" in text
    assert "no biological claims" in text


def test_current_gate_map_records_controlled_embedding_fill_worklist_builder() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "controlled embedding fill worklist builder is now recorded" in text
    assert "src/longevity_port_pipelines/stages/controlled_embedding_fill_worklist.py" in text
    assert "table-only dry-run worklist builder" in text
    assert "data/config/controlled_embedding_fill_worklist_schema.yaml" in text
    assert (
        "does not infer that status from ordinary preflight rows without explicit policy context"
        in text
    )
    assert "does not fetch sequences" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not commit `data/output/` artifacts" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
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


def test_current_gate_map_records_generic_repair_queue_summary_fixtures() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "Generic repair queue summary checkpoint fixtures" in text
    assert "tests/fixtures/generic_repair_queue_summary_base.csv" in text
    assert "tests/fixtures/generic_repair_queue_summary_reviewed_overlay.csv" in text
    assert "13 blocked Gate 4 / Gate 5 repair rows" in text
    assert "reviewed SIRT6 row remaining deferred and blocked" in text
    assert "do not fetch sequences" in text
    assert "do not curate orthologs" in text
    assert "do not call Biohub" in text
    assert "do not generate embeddings" in text
    assert "do not call Boltz" in text
    assert "do not rerun enrichment or contrast" in text
    assert "do not promote Gate 8 or Gate 9" in text
    assert "do not make biological claims" in text


def test_current_gate_map_records_gate_repair_policy_helper() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "Gate 4 / Gate 5 repair policy helper" in text
    assert "docs/gate_repair_policy_helper.md" in text
    assert "src/longevity_port_pipelines/stages/gate_repair_policy.py" in text
    assert (
        "Current blocked, deferred, rejected, second-review, and unknown states remain blocked at Gate 4 / Gate 5"
        in text
    )
    assert "later explicit Gate 4 / Gate 5 policy update" in text
    assert "does not make a row Gate 8 eligible" in text
    assert "does not make a row Gate 9 eligible" in text
    assert "does not make embeddings ready" in text
    assert "does not make Boltz ready" in text
    assert "does not allow biological claims" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment or contrast" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_tp53_mdm2_provenance_review_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "TP53/MDM2 provenance review checkpoint" in text
    assert "docs/tp53_mdm2_provenance_review_checkpoint.md" in text
    assert "elephant TP53 and MDM2 seed repair rows" in text
    assert "deferred_pending_source" in text
    assert "no accession-level elephant target ortholog evidence is accepted" in text
    assert "remain blocked at Gate 4 / Gate 5" in text
    assert "repair_worklist rows" in text
    assert "three reviewed rows total" in text
    assert "one SIRT6 row and two TP53/MDM2 rows" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment or contrast" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_ortholog_evidence_intake_checklist() -> None:
    text = read_doc("docs/current_gate_map.md")
    assert "Ortholog evidence intake checklist" in text
    assert "docs/ortholog_evidence_intake_checklist.md" in text
    assert "accession-level ortholog evidence" in text
    assert "required row identity fields" in text
    assert "minimum accession-level evidence fields" in text
    assert "acceptable evidence sources" in text
    assert "unacceptable evidence sources" in text
    assert "SIRT6/core3 and TP53/MDM2 elephant lanes" in text
    assert "does not add new accessions" in text
    assert "does not accept target orthologs" in text
    assert "does not change any repair queue row status" in text
    assert "Gate 4 / Gate 5 repair-queue worklist item" in text
    assert "does not fetch sequences" in text
    assert "does not curate orthologs automatically" in text
    assert "does not call Biohub" in text
    assert "does not generate embeddings" in text
    assert "does not call Boltz" in text
    assert "does not rerun enrichment or contrast" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_gate_aware_embedding_fill_plan_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 gate-aware embedding fill plan checkpoint status" in text
    assert "`planning_policy_updated_runtime_blocked`" in text
    assert "data/input/ortholog_evidence_gate45_policy_updates.csv#1" in text
    assert "docs-only planning checkpoint" in text
    assert "no sequence fetch" in text
    assert "no Biohub call" in text
    assert "no embedding generation" in text
    assert "no committed embedding artifact" in text
    assert "no Gate 8 / Gate 9 promotion" in text
    assert "no biological claim" in text


def test_current_gate_map_records_planning_policy_updated_runtime_blocked_fill_status() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "controlled embedding fill worklist vocabulary status" in text
    assert "`planning_policy_updated_runtime_blocked` is now machine-readable and blocked" in text
    assert "recommended next action is `keep_blocked`" in text
    assert "no preflight" in text
    assert "no single dry-run" in text
    assert "no live call" in text
    assert "no Gate 8 / Gate 9 promotion" in text
    assert "no biological claim" in text


def test_current_gate_map_records_g3sx30_blocked_embedding_fill_worklist_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 blocked controlled embedding-fill worklist checkpoint" in text
    assert "data/interim/controlled_embedding_fill_worklist_g3sx30_blocked_checkpoint.csv" in text
    assert "data/input/ortholog_evidence_gate45_policy_updates.csv#1" in text
    assert "target_accession=G3SX30" in text
    assert "target_sequence_length=492" in text
    assert "sequence_length_status=not_fetched" in text
    assert "embedding_path=not_applicable_runtime_blocked" in text
    assert "fill_status: planning_policy_updated_runtime_blocked" in text
    assert "allowed_next_action: keep_blocked" in text
    assert "dry_run_required: false" in text
    assert "max_live_batch_size: 0" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not rerun enrichment or contrast" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_blocked_embedding_fill_exit_criteria() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 blocked embedding-fill exit criteria checkpoint" in text
    assert "docs/g3sx30_blocked_embedding_fill_exit_criteria.md" in text
    assert "docs-only review protocol for a later possible dry-run preflight decision" in text
    assert "does not change the G3SX30 worklist row" in text
    assert "does not make G3SX30 preflight-ready" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text
    assert "G3SX30 blocked embedding-fill exit criteria status" in text
    assert "later exit requires reviewed target sequence provenance" in text
    assert "`sequence_length_status=matches`" in text
    assert "explicit separate dry-run preflight decision" in text


def test_current_gate_map_records_reviewed_target_sequence_provenance_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Reviewed target sequence provenance scaffold checkpoint" in text
    assert "data/config/reviewed_target_sequence_provenance_schema.yaml" in text
    assert "data/input/reviewed_target_sequence_provenance.csv" in text
    assert "src/longevity_port_pipelines/stages/reviewed_target_sequence_provenance.py" in text
    assert "header-only reviewed target sequence provenance table" in text
    assert "does not add a G3SX30 sequence row" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_deferred_target_sequence_provenance_row() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 deferred target sequence provenance row checkpoint" in text
    assert "data/input/reviewed_target_sequence_provenance.csv" in text
    assert "sequence_source_type=deferred_pending_review" in text
    assert "sequence_length_status=not_fetched" in text
    assert "sequence_review_status=deferred_pending_review" in text
    assert "provenance_review_status=deferred" in text
    assert "allowed_next_action_after_sequence_review=defer_pending_sequence_review" in text
    assert "does not record reviewed sequence provenance" in text
    assert "does not record `sequence_length_status=matches`" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not change the G3SX30 controlled embedding-fill worklist row" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text
    assert (
        "reviewed target sequence provenance rows: one G3SX30 deferred pending-review row" in text
    )
    assert "no ready_for_preflight" in text


def test_current_gate_map_records_g3sx30_target_sequence_review_checklist() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 target sequence review checklist checkpoint" in text
    assert "docs/g3sx30_target_sequence_review_checklist.md" in text
    assert "human-review requirements" in text
    assert "deferred_pending_review" in text
    assert "reviewed_sequence_provenance" in text
    assert "data/input/ortholog_evidence_gate45_policy_updates.csv#1" in text
    assert "accession `G3SX30`" in text
    assert "database `UniProtKB TrEMBL`" in text
    assert "species `Loxodonta africana`" in text
    assert "taxid `9785`" in text
    assert "gene symbol `MDM2`" in text
    assert "explicit reviewed sequence artifact/hash checks" in text
    assert "expected metadata length `492`" in text
    assert "mismatch handling" in text
    assert "separate later dry-run preflight decision" in text
    assert "does not fetch sequences" in text
    assert "does not add reviewed sequence provenance" in text
    assert "does not record `sequence_length_status=matches`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_target_sequence_review_decision_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "Target sequence review decision scaffold checkpoint" in text
    assert "data/config/target_sequence_review_decision_schema.yaml" in text
    assert "data/input/target_sequence_review_decisions.csv" in text
    assert "src/longevity_port_pipelines/stages/target_sequence_review_decisions.py" in text
    assert "header-only decision scaffold" in text
    assert "adds no G3SX30 decision row" in text
    assert "does not mutate the existing G3SX30 target sequence provenance row" in text
    assert "approve_reviewed_sequence_provenance_for_planning" in text
    assert "defer_pending_sequence_review" in text
    assert "reject_sequence_provenance" in text
    assert "keep_blocked_after_mismatch" in text
    assert "sequence_reviewed_still_preflight_decision_blocked" in text
    assert "separate later dry-run preflight decision PR" in text
    assert "does not fetch sequences" in text
    assert "does not add reviewed sequence provenance" in text
    assert "does not record `sequence_length_status=matches`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not mark ready_for_preflight" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text
    assert "target sequence review decision scaffold status" in text
    assert "no G3SX30 decision row" in text
    assert "no mutation of reviewed target sequence provenance rows" in text


def test_current_gate_map_records_g3sx30_deferred_target_sequence_review_decision_row() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 deferred target sequence review decision row checkpoint" in text
    assert "data/input/target_sequence_review_decisions.csv" in text
    assert "sequence_review_decision=defer_pending_sequence_review" in text
    assert "sequence_length_status_after_decision=not_fetched" in text
    assert "provenance_review_status_after_decision=deferred" in text
    assert "decision_status=deferred_pending_review" in text
    assert "downstream_block_status_after_decision=sequence_review_deferred_still_blocked" in text
    assert "allowed_next_action_after_decision=defer_pending_sequence_review" in text
    assert "does not approve reviewed sequence provenance" in text
    assert "does not record `sequence_length_status_after_decision=matches`" in text
    assert "does not mutate the source sequence provenance row" in text
    assert "does not fetch sequences" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text
    assert "target sequence review decision rows: one G3SX30 deferred decision row" in text


def test_current_gate_map_records_g3sx30_official_sequence_source_review_preparation() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 official sequence source review preparation checkpoint" in text
    assert "docs/g3sx30_official_sequence_source_review_preparation.md" in text
    assert "later possible G3SX30 reviewed target sequence provenance PR" in text
    assert "accession `G3SX30`" in text
    assert "database `UniProtKB TrEMBL`" in text
    assert "species `Loxodonta africana`" in text
    assert "taxid `9785`" in text
    assert "gene symbol `MDM2`" in text
    assert "expected metadata length `492`" in text
    assert "explicit sequence source traceability" in text
    assert "stable `reviewed_sequence_sha256`" in text
    assert "direct reviewed amino-acid sequence length calculation" in text
    assert "direct length comparison" in text
    assert "explicit mismatch handling" in text
    assert "does not perform the review" in text
    assert "does not fetch sequences inside the repository" in text
    assert "does not commit a raw sequence artifact" in text
    assert "does not mutate `data/input/reviewed_target_sequence_provenance.csv`" in text
    assert "does not mutate `data/input/target_sequence_review_decisions.csv`" in text
    assert "does not approve reviewed sequence provenance" in text
    assert "does not record `sequence_length_status=matches`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text
    assert "G3SX30 official sequence source review preparation status" in text


def test_current_gate_map_records_g3sx30_reviewed_target_sequence_provenance_row() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 reviewed target sequence provenance row checkpoint" in text
    assert "data/input/reviewed_target_sequence_provenance.csv" in text
    assert (
        "one deferred G3SX30 provenance row plus one reviewed official UniProt sequence provenance row"
        in text
    )
    assert "sequence_source_type=reviewed_external_database_record" in text
    assert "sequence_source_reference=https://rest.uniprot.org/uniprotkb/G3SX30.fasta" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "sequence_length_status=matches" in text
    assert "sequence_review_status=reviewed_sequence_provenance" in text
    assert "provenance_review_status=reviewed" in text
    assert (
        "allowed_next_action_after_sequence_review=consider_later_dry_run_preflight_decision_pr"
        in text
    )
    assert "manual official-source review package stored outside the repo" in text
    assert "does not commit the raw FASTA amino-acid sequence artifact" in text
    assert "reviewed sequence provenance for planning only" in text
    assert "does not mutate `data/input/target_sequence_review_decisions.csv`" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not fetch sequences inside the repository" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_reviewed_target_sequence_approval_decision_row() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 reviewed target sequence approval decision row checkpoint" in text
    assert "data/input/target_sequence_review_decisions.csv" in text
    assert (
        "one deferred G3SX30 decision row and adds one reviewed G3SX30 target sequence approval decision row"
        in text
    )
    assert "data/input/reviewed_target_sequence_provenance.csv#2" in text
    assert "sequence_review_decision=approve_reviewed_sequence_provenance_for_planning" in text
    assert "sequence_length_status_after_decision=matches" in text
    assert "provenance_review_status_after_decision=reviewed" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "decision_status=reviewed_for_planning_still_preflight_blocked" in text
    assert (
        "downstream_block_status_after_decision=sequence_reviewed_still_preflight_decision_blocked"
        in text
    )
    assert "allowed_next_action_after_decision=consider_later_dry_run_preflight_decision_pr" in text
    assert "planning-only approval decision" in text
    assert "does not mutate `data/input/reviewed_target_sequence_provenance.csv`" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not fetch sequences inside the repository" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_dry_run_preflight_decision_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 dry-run preflight decision scaffold checkpoint" in text
    assert "header-only dry-run preflight decision scaffold for G3SX30" in text
    assert "data/input/target_sequence_review_decisions.csv#2" in text
    assert "sequence_review_decision=approve_reviewed_sequence_provenance_for_planning" in text
    assert "sequence_length_status_after_decision=matches" in text
    assert "provenance_review_status_after_decision=reviewed" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "decision_status=reviewed_for_planning_still_preflight_blocked" in text
    assert "allowed_next_action_after_decision=consider_later_dry_run_preflight_decision_pr" in text
    assert "data/config/g3sx30_dry_run_preflight_decision_schema.yaml" in text
    assert "data/input/g3sx30_dry_run_preflight_decisions.csv" in text
    assert "src/longevity_port_pipelines/stages/g3sx30_dry_run_preflight_decisions.py" in text
    assert "adds no committed G3SX30 dry-run preflight decision row" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_first_g3sx30_dry_run_preflight_decision_row() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "First G3SX30 dry-run preflight decision row checkpoint" in text
    assert "data/input/g3sx30_dry_run_preflight_decisions.csv" in text
    assert "one G3SX30 dry-run preflight decision row" in text
    assert "data/input/target_sequence_review_decisions.csv#2" in text
    assert "dry_run_preflight_decision=approve_dry_run_preflight_for_planning" in text
    assert (
        "dry_run_preflight_status_after_decision=dry_run_preflight_planning_approved_runtime_blocked"
        in text
    )
    assert "allowed_next_action_after_decision=prepare_later_dry_run_preflight_manifest_pr" in text
    assert "max_live_batch_size_after_decision=0" in text
    assert "ready_for_preflight_after_decision=false" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "planning-only dry-run preflight decision row" in text
    assert "authorizes only preparation of a later dry-run preflight manifest PR" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_dry_run_preflight_manifest_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 dry-run preflight manifest scaffold checkpoint" in text
    assert "header-only dry-run preflight manifest scaffold for G3SX30" in text
    assert "data/input/g3sx30_dry_run_preflight_decisions.csv#1" in text
    assert "dry_run_preflight_decision=approve_dry_run_preflight_for_planning" in text
    assert (
        "dry_run_preflight_status_after_decision=dry_run_preflight_planning_approved_runtime_blocked"
        in text
    )
    assert "allowed_next_action_after_decision=prepare_later_dry_run_preflight_manifest_pr" in text
    assert "max_live_batch_size_after_decision=0" in text
    assert "ready_for_preflight_after_decision=false" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "data/config/g3sx30_dry_run_preflight_manifest_schema.yaml" in text
    assert "data/input/g3sx30_dry_run_preflight_manifest.csv" in text
    assert "src/longevity_port_pipelines/stages/g3sx30_dry_run_preflight_manifest.py" in text
    assert "adds no committed G3SX30 dry-run preflight manifest entry" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_first_g3sx30_dry_run_preflight_manifest_row() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "First G3SX30 dry-run preflight manifest row checkpoint" in text
    assert "data/input/g3sx30_dry_run_preflight_manifest.csv" in text
    assert "one G3SX30 dry-run preflight manifest row" in text
    assert "data/input/g3sx30_dry_run_preflight_decisions.csv#1" in text
    assert "manifest_entry_status=manifest_scaffold_ready_runtime_blocked" in text
    assert "dry_run_only=true" in text
    assert "max_live_batch_size=0" in text
    assert "ready_for_preflight_after_manifest=false" in text
    assert "sequence_fetch_allowed=false" in text
    assert "biohub_call_allowed=false" in text
    assert "esmc_call_allowed=false" in text
    assert "embedding_generation_allowed=false" in text
    assert "curated_embedding_preflight_allowed=false" in text
    assert "curated_embedding_single_allowed=false" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "planning-only dry-run preflight manifest row" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create or commit `.npy` artifacts" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_dry_run_preflight_execution_checklist() -> None:
    text = read_doc("docs/current_gate_map.md")

    assert "G3SX30 dry-run preflight execution checklist checkpoint" in text
    assert "docs/g3sx30_dry_run_preflight_execution_checklist.md" in text
    assert "docs-only checklist for a later G3SX30 dry-run preflight execution PR" in text
    assert "data/input/g3sx30_dry_run_preflight_manifest.csv#1" in text
    assert "manifest_entry_status=manifest_scaffold_ready_runtime_blocked" in text
    assert "dry_run_only=true" in text
    assert "max_live_batch_size=0" in text
    assert "ready_for_preflight_after_manifest=false" in text
    assert "sequence_fetch_allowed=false" in text
    assert "biohub_call_allowed=false" in text
    assert "esmc_call_allowed=false" in text
    assert "embedding_generation_allowed=false" in text
    assert "curated_embedding_preflight_allowed=false" in text
    assert "curated_embedding_single_allowed=false" in text
    assert "reviewed_sequence_length=492" in text
    assert (
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"
        in text
    )
    assert "future dry-run command templating" in text
    assert "pre-run checks" in text
    assert "post-run checks" in text
    assert "forbidden artifacts" in text
    assert "does not run `curated_embedding_preflight`" in text
    assert "does not run `curated_embedding_single`" in text
    assert "does not call Biohub / ESMC" in text
    assert "does not generate embeddings" in text
    assert "does not create `.npy` artifacts" in text
    assert "does not commit `data/output` artifacts" in text
    assert "does not mark anything `ready_for_preflight`" in text
    assert "does not promote Gate 8 or Gate 9" in text
    assert "does not call Boltz, AF3, or Chai" in text
    assert "does not make biological claims" in text


def test_current_gate_map_records_g3sx30_dry_run_preflight_command_discovery_note() -> None:
    text = read_doc("docs/current_gate_map.md")
    for required in [
        "G3SX30 dry-run preflight command discovery note checkpoint",
        "docs/g3sx30_dry_run_preflight_command_discovery_note.md",
        "docs-only command discovery note",
        "docs/g3sx30_dry_run_preflight_execution_checklist.md",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "`curated-embedding-preflight`",
        "`curated-embedding-single`",
        "does not execute either script",
        "non-executed help commands",
        "required help-output checks",
        "required repository-search checks",
        "no-run proof for this PR",
        "stop conditions for any later execution PR",
        "does not run `curated-embedding-preflight`",
        "does not run `curated_embedding_preflight`",
        "does not run `curated-embedding-single`",
        "does not run `curated_embedding_single`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_dry_run_preflight_cli_compatibility_note() -> None:
    text = read_doc("docs/current_gate_map.md")
    for required in [
        "G3SX30 dry-run preflight CLI compatibility checkpoint",
        "docs/g3sx30_dry_run_preflight_cli_compatibility_note.md",
        "docs-only compatibility note",
        "docs/g3sx30_dry_run_preflight_execution_checklist.md",
        "docs/g3sx30_dry_run_preflight_command_discovery_note.md",
        "src/longevity_port_pipelines/stages/curated_embedding_preflight.py",
        "src/longevity_port_pipelines/stages/curated_embedding_single.py",
        "current CLI behavior does not match the G3SX30 dry-run preflight checklist expectations closely enough for direct execution",
        "`curated-embedding-preflight` is dry-run-only by implementation but is not manifest-aware",
        "no explicit `--dry-run`",
        "no `--no-live-call`",
        "no `--max-live-batch-size 0`",
        "no `--no-output-artifacts`",
        "writes `data/output/curated_ortholog_embedding_preflight.csv` by default",
        "`curated-embedding-single` is dry-run by default but can call Biohub / ESMC if `--yes-live` is passed",
        "not directly use the current `curated-embedding-preflight` default behavior against G3SX30",
        "manifest mismatch and output-path issue are resolved",
        "manifest-aware dry-run adapter/wrapper scaffold",
        "source-level guardrail before execution",
        "G3SX30 remains runtime-blocked",
        "does not run `curated-embedding-preflight`",
        "does not run `curated_embedding_preflight`",
        "does not run `curated-embedding-single`",
        "does not run `curated_embedding_single`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold() -> (
    None
):
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 manifest-aware dry-run preflight adapter scaffold checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_manifest_aware_dry_run_preflight_adapter.py",
        "helper-only manifest-aware dry-run preflight adapter scaffold",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "dry_run_only=true",
        "max_live_batch_size=0",
        "ready_for_preflight_after_manifest=false",
        "reviewed sequence length `492`",
        "reviewed sequence SHA256 `e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f`",
        "claim_status=technical_checkpoint",
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1",
        "data/config/g3sx30_manifest_aware_dry_run_preflight_adapter_schema.yaml",
        "manifest_understood_runtime_blocked",
        "do_not_execute_current_cli_directly",
        "not_directly_executable_manifest_mismatch_output_path_issue",
        "add_manifest_aware_wrapper_or_guardrail_before_execution",
        "do_not_write_committed_data_output",
        "does not add a `pyproject.toml` script entry point",
        "does not run `curated-embedding-preflight`",
        "does not run `curated_embedding_preflight`",
        "does not run `curated-embedding-single`",
        "does not run `curated_embedding_single`",
        "does not run `--help`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_manifest_aware_adapter_policy_contract() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 manifest-aware adapter policy contract checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_manifest_aware_adapter_policy_contract.py",
        "machine-readable transition policy contract",
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1",
        "keeps the old adapter scaffold row unchanged",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "policy_status=adapter_policy_runtime_blocked",
        "policy_decision=require_manifest_aware_wrapper_before_execution",
        "current_cli_direct_execution_decision=reject_current_cli_direct_execution",
        "wrapper_scaffold_decision=allow_wrapper_scaffold_only",
        "wrapper_execution_decision=not_authorized",
        "dry_run_execution_decision=not_authorized",
        "live_execution_decision=not_authorized",
        "ready_for_preflight_decision=not_authorized",
        "biohub_esmc_decision=not_authorized",
        "embedding_generation_decision=not_authorized",
        "artifact_decision=not_authorized",
        "allowed_next_action_after_policy=prepare_manifest_aware_wrapper_scaffold_pr",
        "required_next_action=add_manifest_aware_wrapper_or_guardrail_before_execution",
        "prepare_manifest_aware_wrapper_scaffold_pr",
        "add_source_level_manifest_guardrail_before_execution",
        "keep_runtime_blocked",
        "does not mean the wrapper exists",
        "does not mean wrapper execution is allowed",
        "does not mean dry-run execution is allowed",
        "does not add a `pyproject.toml` script entry point",
        "does not implement a manifest-aware wrapper",
        "does not authorize wrapper execution",
        "does not authorize dry-run execution",
        "does not run `curated-embedding-preflight`",
        "does not run `curated_embedding_preflight`",
        "does not run `curated-embedding-single`",
        "does not run `curated_embedding_single`",
        "does not run `--help`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_manifest_aware_dry_run_wrapper_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 manifest-aware dry-run wrapper scaffold checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_manifest_aware_dry_run_wrapper_scaffold.py",
        "non-executable helper/table scaffold",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "data/interim/g3sx30_manifest_aware_dry_run_preflight_adapter_scaffold.csv#1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1",
        "wrapper_status=wrapper_scaffold_runtime_blocked",
        "wrapper_decision=prepare_wrapper_plan_only",
        "policy_contract_status=adapter_policy_runtime_blocked",
        "policy_contract_decision=require_manifest_aware_wrapper_before_execution",
        "current_cli_direct_execution_decision=reject_current_cli_direct_execution",
        "wrapper_scaffold_decision=allow_wrapper_scaffold_only",
        "wrapper_execution_decision=not_authorized",
        "dry_run_execution_decision=not_authorized",
        "live_execution_decision=not_authorized",
        "ready_for_preflight_decision=not_authorized",
        "biohub_esmc_decision=not_authorized",
        "embedding_generation_decision=not_authorized",
        "artifact_decision=not_authorized",
        "command_selected=false",
        "output_path_selected=false",
        "execution_plan_materialized=false",
        "runtime_still_blocked=true",
        "allowed_next_action_after_wrapper_scaffold=add_wrapper_command_contract_pr",
        "does not add a `pyproject.toml` script entry point",
        "does not add a Typer executable wrapper",
        "does not implement a manifest-aware wrapper",
        "does not authorize wrapper execution",
        "does not authorize dry-run execution",
        "does not authorize live execution",
        "does not run `curated-embedding-preflight`",
        "does not run `curated_embedding_preflight`",
        "does not run `curated-embedding-single`",
        "does not run `curated_embedding_single`",
        "does not run `--help`",
        "does not select a command",
        "does not select an output path",
        "does not materialize an execution plan",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_command_contract_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper command contract scaffold checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_wrapper_command_contract_scaffold.py",
        "non-executable helper/table scaffold",
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "data/interim/g3sx30_wrapper_command_contract_scaffold.csv#1",
        "command_contract_status=command_contract_scaffold_runtime_blocked",
        "command_contract_decision=define_future_command_contract_only",
        "source_wrapper_status=wrapper_scaffold_runtime_blocked",
        "source_wrapper_decision=prepare_wrapper_plan_only",
        "expected_command_family=curated_embedding_preflight_dry_run_wrapper",
        "actual_cli_help_observed=false",
        "actual_command_verified=false",
        "command_selected=false",
        "output_path_selected=false",
        "execution_plan_materialized=false",
        "execution_authorized=false",
        "wrapper_execution_authorized=false",
        "dry_run_execution_authorized=false",
        "live_execution_authorized=false",
        "ready_for_preflight_authorized=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "npy_artifact_authorized=false",
        "data_output_artifact_commit_authorized=false",
        "output_path_policy=do_not_write_committed_data_output",
        "allowed_output_location_policy=future_temp_or_manual_reviews_path_only",
        "unverified_until_help_or_source_guardrail=true",
        "future_command_contract_scaffold_only=true",
        "runtime_still_blocked=true",
        "allowed_next_action_after_command_contract=add_wrapper_source_guardrail_pr",
        "claim_status=technical_checkpoint",
        "expected future command contract vocabulary",
        "required future args vocabulary",
        "forbidden future args vocabulary",
        "required future guardrails",
        "forbidden actions",
        "output-path policy",
        "must not claim `actual_supported_args`, `observed_help_flags`, or `verified_cli_contract`",
        "does not add a `pyproject.toml` script entry point",
        "does not add a Typer executable wrapper",
        "does not authorize wrapper execution",
        "does not authorize dry-run execution",
        "does not authorize live execution",
        "does not run any actual command",
        "does not run `--help`",
        "does not make observed-help claims",
        "does not make actual CLI flag verification claims",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_source_guardrail_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")
    for required in [
        "G3SX30 wrapper source guardrail scaffold checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_wrapper_source_guardrail_scaffold.py",
        "non-executable helper/table scaffold",
        "data/interim/g3sx30_wrapper_command_contract_scaffold.csv#1",
        "data/interim/g3sx30_manifest_aware_dry_run_wrapper_scaffold.csv#1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "data/input/g3sx30_manifest_aware_adapter_policy_contract.csv#1",
        "data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv#1",
        "source_guardrail_status=source_guardrail_scaffold_runtime_blocked",
        "source_guardrail_decision=define_source_level_guardrails_only",
        "guardrail_scope=future_wrapper_source_checks_only",
        "guardrail_runtime_effect=no_runtime_effect",
        "source_actual_cli_help_observed=false",
        "source_actual_command_verified=false",
        "source_command_selected=false",
        "source_output_path_selected=false",
        "source_execution_plan_materialized=false",
        "reviewed_sequence_length=492",
        "max_live_batch_size_zero_required=true",
        "all_runtime_permissions_false_required=true",
        "wrapper_implementation_authorized=false",
        "wrapper_execution_authorized=false",
        "dry_run_execution_authorized=false",
        "live_execution_authorized=false",
        "ready_for_preflight_authorized=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "gate8_promotion_authorized=false",
        "gate9_promotion_authorized=false",
        "biological_claim_authorized=false",
        "allowed_next_action_after_source_guardrail=add_wrapper_help_observation_note_pr",
        "claim_status=technical_checkpoint",
        "runtime_still_blocked=true",
        "future wrapper source checks only",
        "has no runtime effect",
        "does not implement a source guardrail",
        "does not run any actual command",
        "does not run `--help`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not promote Gate 8 or Gate 9",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_help_observation_note() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper help observation note checkpoint",
        "docs/g3sx30_wrapper_help_observation_note.md",
        "final pre-help observation note",
        "docs-only checkpoint",
        "not a schema/table/helper layer",
        "data/interim/g3sx30_wrapper_source_guardrail_scaffold.csv#1",
        "help_observation_status=planned_not_observed",
        "actual_cli_help_observed=false",
        "actual_command_verified=false",
        "command_selected=false",
        "output_path_selected=false",
        "execution_plan_materialized=false",
        "runtime_still_blocked=true",
        "curated_embedding_preflight_dry_run_wrapper",
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
        "safe help-only observation",
        "output/evidence must be captured later",
        "strings/flags must be checked later",
        "stop conditions abort before any later execution",
        "still not execution",
        "still not `ready_for_preflight`",
        "still not Biohub / ESMC / embedding generation",
        "does not run `--help`",
        "does not run any actual command",
        "does not make observed-help claims",
        "does not make actual CLI flag verification claims",
        "does not add a `pyproject.toml` script entry point",
        "does not add a Typer executable wrapper",
        "does not implement a wrapper",
        "does not authorize wrapper execution",
        "does not authorize dry-run execution",
        "does not authorize live execution",
        "does not select a command",
        "does not select an output path",
        "does not materialize an execution plan",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "actual G3SX30 wrapper help observation PR",
        "still no execution",
        "still no Biohub / ESMC",
        "still no embeddings",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_help_target_inspection_blocker() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper help target inspection blocker checkpoint",
        "docs/g3sx30_wrapper_help_target_inspection_blocker.md",
        "source-inspection blocker",
        "docs/tests-only checkpoint",
        "not a schema/table/helper layer",
        "not a help-observation evidence layer",
        "help_target_inspection_status=inspected_target_missing",
        "real_g3sx30_wrapper_help_target_found=false",
        "pyproject_g3sx30_script_entry_present=false",
        "pyproject_wrapper_script_entry_present=false",
        "ordinary_curated_embedding_scripts_present=true",
        "ordinary_scripts_valid_as_substitutes=false",
        "actual_cli_help_observed=false",
        "actual_command_verified=false",
        "command_selected=false",
        "output_path_selected=false",
        "execution_plan_materialized=false",
        "runtime_still_blocked=true",
        "curated_embedding_preflight_dry_run_wrapper",
        "expected future command family",
        "not as a real executable script entry point or implemented wrapper command",
        "pyproject.toml",
        "curated-embedding-preflight",
        "curated-embedding-single",
        "no G3SX30 script entry",
        "no wrapper script entry",
        "must not be observed as substitutes",
        "curated_embedding_preflight",
        "curated_embedding_single",
        "misleading observed-help claim",
        "does not run `--help`",
        "does not run any actual command",
        "does not make observed-help claims",
        "does not make actual CLI flag verification claims",
        "does not add a `pyproject.toml` script entry point",
        "does not add a Typer executable wrapper",
        "does not implement a wrapper",
        "does not authorize wrapper execution",
        "does not authorize dry-run execution",
        "does not authorize live execution",
        "does not select a command",
        "does not select an output path",
        "does not materialize an execution plan",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "natural next step is not help observation yet",
        "G3SX30 manifest-aware wrapper source/entry-point implementation plan",
        "implementation boundary",
        "Only after a real wrapper help target exists",
        "actual help-only observation",
        "no wrapper execution",
        "no dry-run execution",
        "no Biohub / ESMC",
        "no embeddings",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_source_entrypoint_boundary() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper source entry-point boundary checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py",
        "pyproject.toml",
        "g3sx30-wrapper-dry-run",
        "entrypoint_boundary_status=source_entrypoint_boundary_runtime_blocked",
        "script_entry_point=g3sx30-wrapper-dry-run",
        "expected_command_family=curated_embedding_preflight_dry_run_wrapper",
        "actual_cli_help_observed=false",
        "actual_command_verified=false",
        "command_selected_for_execution=false",
        "output_path_selected_for_execution=false",
        "execution_plan_materialized=false",
        "wrapper_execution_authorized=false",
        "dry_run_execution_authorized=false",
        "live_execution_authorized=false",
        "ready_for_preflight_authorized=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "runtime_still_blocked=true",
        "docs/g3sx30_wrapper_help_target_inspection_blocker.md",
        "real wrapper help target now exists",
        "uv run g3sx30-wrapper-dry-run --help",
        "does not run `--help`",
        "does not make observed-help claims",
        "does not make actual CLI flag verification claims",
        "does not execute the wrapper",
        "does not execute a dry-run",
        "does not execute a live run",
        "does not select a command for execution",
        "does not select an output path for execution",
        "does not materialize an execution plan",
        "does not read or execute the G3SX30 manifest",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "curated-embedding-preflight",
        "curated_embedding_preflight",
        "curated-embedding-single",
        "curated_embedding_single",
        "remain invalid substitutes",
        "actual G3SX30 wrapper help observation PR",
        "still help-only",
        "still no wrapper execution",
        "still no dry-run execution",
        "still no Biohub / ESMC",
        "still no embeddings",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_actual_help_observation() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper actual help observation checkpoint",
        "docs/g3sx30_wrapper_actual_help_observation.md",
        "help-only observation",
        "uv run g3sx30-wrapper-dry-run --help",
        "HELP_EXIT_CODE=0",
        "D:\\biohub_projects\\_chatgpt_observations\\g3sx30_wrapper_help_output.txt",
        "not a committed runtime artifact",
        "help_observation_status=observed_help_only",
        "observed_help_target=g3sx30-wrapper-dry-run",
        "observed_manifest_option=true",
        "observed_manifest_row_index_option=true",
        "observed_output_path_option=true",
        "observed_help_option=true",
        "actual_cli_help_observed=true",
        "actual_command_verified_for_help=true",
        "command_selected_for_execution=false",
        "output_path_selected_for_execution=false",
        "execution_plan_materialized=false",
        "wrapper_execution_authorized=false",
        "dry_run_execution_authorized=false",
        "live_execution_authorized=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "runtime_still_blocked=true",
        "Usage: g3sx30-wrapper-dry-run [OPTIONS]",
        "--manifest",
        "--manifest-row-index",
        "--output-path",
        "--help",
        "PowerShell `NativeCommandError` wrapper",
        "not treated as command failure",
        "No-runtime-artifact proof",
        "git status -sb",
        "observe-g3sx30-wrapper-help",
        "git ls-files --others --exclude-standard",
        "no untracked files",
        "does not run the wrapper without `--help`",
        "does not execute a dry-run",
        "does not execute a live run",
        "does not read or execute the G3SX30 manifest",
        "does not select a command for execution",
        "does not select an output path for execution",
        "does not materialize an execution plan",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not unlock the manifest runtime path",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "natural next layer is not execution yet",
        "stricter source-level runtime blocker",
        "execution-plan review gate",
        "Runtime execution should remain blocked",
        "non-committed output location",
        "no Biohub / ESMC",
        "no embedding generation",
        "no `ready_for_preflight` promotion",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_execution_plan_review_gate() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper execution-plan review gate checkpoint",
        "data/interim/g3sx30_wrapper_execution_plan_review_gate.csv#1",
        "runtime-blocked execution-plan review gate",
        "execution_plan_review_status=execution_plan_review_gate_runtime_blocked",
        "execution_plan_review_decision=require_separate_review_before_any_execution",
        "help_observation_status=observed_help_only",
        "help_exit_code=0",
        "observed_help_target=g3sx30-wrapper-dry-run",
        "observed_manifest_option=true",
        "observed_manifest_row_index_option=true",
        "observed_output_path_option=true",
        "observed_help_option=true",
        "dry_run_plan_review_required_before_execution=true",
        "non_committed_output_path_review_required=true",
        "output_path_selected_for_execution=false",
        "command_selected_for_execution=false",
        "execution_plan_materialized=false",
        "wrapper_execution_authorized=false",
        "dry_run_execution_authorized=false",
        "live_execution_authorized=false",
        "ready_for_preflight_authorized=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "npy_artifact_authorized=false",
        "data_output_artifact_commit_authorized=false",
        "gate8_promotion_authorized=false",
        "gate9_promotion_authorized=false",
        "biological_claim_authorized=false",
        "runtime_still_blocked=true",
        "allowed_next_action_after_review_gate=add_g3sx30_wrapper_execution_plan_runtime_blocker",
        "claim_status=technical_checkpoint",
        "help observation is not execution authorization",
        "explicit non-committed output path",
        "reject committed `data/output` artifacts",
        "reject Biohub / ESMC",
        "reject embedding generation",
        "reject `.npy` artifacts",
        "keep `ready_for_preflight` false",
        "keep Gate 8 and Gate 9 blocked",
        "make no biological claim",
        "does not run `g3sx30-wrapper-dry-run`",
        "does not run the wrapper without `--help`",
        "does not execute a dry-run",
        "does not execute a live run",
        "does not read or execute the G3SX30 manifest",
        "does not select a command for execution",
        "does not select an output path for execution",
        "does not materialize an execution plan",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz, AF3, or Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "natural next layer is still not dry-run execution",
        "source-level runtime blocker",
        "non-executable execution-plan object scaffold",
        "Runtime execution should remain blocked",
        "non-committed output location",
        "all live/embedding permissions false",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_source_runtime_fail_closed_tests() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper source runtime fail-closed tests checkpoint",
        "tests/test_g3sx30_wrapper_source_entrypoint_boundary.py",
        "actual `g3sx30-wrapper-dry-run` Typer entrypoint",
        "non-help invocation",
        "exits blocked with exit code 2",
        "runtime-blocked boundary message",
        "does not authorize wrapper execution",
        "dry-run execution",
        "live execution",
        "Biohub / ESMC calls",
        "embedding generation",
        "--manifest",
        "--manifest-row-index",
        "--output-path",
        "interface-documentation-only",
        "manifest is not read or created",
        "output path is not written",
        "no output directory is created",
        "no command is selected for execution",
        "no output path is selected for execution",
        "no execution plan is materialized",
        "all runtime authorization flags remain false",
        "`runtime_still_blocked` remains true",
        "does not run a dry-run",
        "does not run a live path",
        "does not execute the G3SX30 manifest",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not make biological claims",
        "next practical layer should be `Add G3SX30 wrapper dry-run execution plan scaffold`",
        "not another blocker layer",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_dry_run_execution_plan_scaffold() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper dry-run execution plan scaffold checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_wrapper_dry_run_execution_plan_scaffold.py",
        "data/interim/g3sx30_wrapper_dry_run_execution_plan_scaffold.csv#1",
        "execution_plan_scaffold_status=dry_run_execution_plan_scaffold_non_executable",
        "execution_plan_scaffold_decision=select_future_command_form_and_external_output_path_only",
        "script_entry_point=g3sx30-wrapper-dry-run",
        "future_command_form_selected=true",
        "future_non_committed_output_path_selected=true",
        "future_output_path=D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "output_path_policy=external_non_committed_observation_path_only",
        "committed_data_output_rejected=true",
        "output_file_created=false",
        "output_directory_created=false",
        "command_selected_for_execution=false",
        "output_path_selected_for_execution=false",
        "execution_plan_materialized=false",
        "wrapper_execution_authorized=false",
        "dry_run_execution_authorized=false",
        "live_execution_authorized=false",
        "manifest_execution_authorized=false",
        "ready_for_preflight_authorized=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "npy_artifact_authorized=false",
        "data_output_artifact_commit_authorized=false",
        "gate8_promotion_authorized=false",
        "gate9_promotion_authorized=false",
        "biological_claim_authorized=false",
        "runtime_still_blocked=true",
        "dry_run_execution_plan_scaffold_only=true",
        "claim_status=technical_checkpoint",
        "uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "future command form for review only",
        "not a command selected for execution",
        "does not run `g3sx30-wrapper-dry-run`",
        "does not run a dry-run",
        "does not run a live path",
        "does not execute the G3SX30 manifest",
        "does not create the future output file",
        "does not create the future output directory",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not make biological claims",
        "natural next step is review of this scaffold before any execution is considered",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_dry_run_execution_plan_review() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper dry-run execution plan scaffold review checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_wrapper_dry_run_execution_plan_review.py",
        "data/interim/g3sx30_wrapper_dry_run_execution_plan_review.csv#1",
        "review_status=dry_run_execution_plan_scaffold_reviewed",
        "review_scope=final_non_execution_review_before_actual_dry_run_pr",
        "review_decision=approve_selected_external_output_dry_run_for_next_pr",
        "selected_command_form_reviewed=true",
        "selected_external_output_path_reviewed=true",
        "selected_manifest_row_reviewed=true",
        "dry_run_execution_authorized_for_next_pr=true",
        "dry_run_execution_authorized_in_this_pr=false",
        "dry_run_executed=false",
        "live_execution_authorized=false",
        "manifest_execution_authorized_in_this_pr=false",
        "biohub_esmc_authorized=false",
        "embedding_generation_authorized=false",
        "npy_artifact_authorized=false",
        "output_file_created=false",
        "output_directory_created=false",
        "data_output_artifact_commit_authorized=false",
        "ready_for_preflight_authorized=false",
        "gate8_promotion_authorized=false",
        "gate9_promotion_authorized=false",
        "biological_claim_authorized=false",
        "runtime_still_blocked_in_this_pr=true",
        "next_pr_must_use_reviewed_command_form=true",
        "next_pr_must_use_reviewed_external_output_path=true",
        "allowed_next_action_after_review=execute_g3sx30_wrapper_dry_run_with_external_output_path",
        "claim_status=technical_checkpoint",
        "uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "approves the selected command form and external output path for the next PR only",
        "does not run `g3sx30-wrapper-dry-run`",
        "does not run a dry-run",
        "does not run a live path",
        "does not execute the G3SX30 manifest in this PR",
        "does not create the external output file",
        "does not create the external output directory",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not write `data/output` artifacts",
        "does not mark anything `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not make biological claims",
        "do not add another blocker, review, or scaffold layer",
        "next practical PR should be `Execute G3SX30 wrapper dry-run with external output path`",
        "still with no Biohub / ESMC, no embeddings",
        "no Gate 8 / Gate 9",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_dry_run_external_output_execution() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper dry-run external output execution checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_wrapper_source_entrypoint_boundary.py",
        "permits only the reviewed G3SX30 external-output dry-run path",
        "uv run g3sx30-wrapper-dry-run --manifest data/input/g3sx30_dry_run_preflight_manifest.csv --manifest-row-index 1 --output-path D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "validates `data/input/g3sx30_dry_run_preflight_manifest.csv#1`",
        "validates the G3SX30 constants",
        "validates the reviewed external output path",
        "writes a small JSON observation",
        "JSON output is external and must not be committed",
        "dry_run_executed=true",
        "manifest_row_index=1",
        "target_accession=G3SX30",
        "target_taxid=9785",
        "reviewed_sequence_length=492",
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "biohub_esmc_called=false",
        "embedding_generation_performed=false",
        "npy_artifact_created=false",
        "data_output_artifact_created=false",
        "ready_for_preflight_promoted=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "allows only the reviewed external-output dry-run",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output` artifacts",
        "does not run a live path",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_wrapper_dry_run_observation_checkpoint() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 wrapper dry-run observation checkpoint",
        "docs/g3sx30_wrapper_dry_run_observation_checkpoint.md",
        "already-executed G3SX30 wrapper dry-run external observation",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "external JSON observation is outside the repository and is not committed",
        "dry_run_executed=true",
        "manifest_row_index=1",
        "target_accession=G3SX30",
        "target_taxid=9785",
        "reviewed_sequence_length=492",
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "manifest_row_read=true",
        "manifest_row_validated=true",
        "biohub_esmc_called=false",
        "embedding_generation_performed=false",
        "npy_artifact_created=false",
        "data_output_artifact_created=false",
        "ready_for_preflight_promoted=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "sequence_fetch_performed=false",
        "live_execution_performed=false",
        "manifest_execution_performed=false",
        "curated_embedding_preflight_run=false",
        "curated_embedding_single_run=false",
        "boltz_called=false",
        "af3_called=false",
        "chai_called=false",
        "enrichment_rerun=false",
        "contrast_rerun=false",
        "claim_status=technical_checkpoint",
        "does not rerun `g3sx30-wrapper-dry-run`",
        "does not commit the external JSON observation",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not create or commit `data/output` artifacts",
        "does not run a live path",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "do not add another generic checkpoint, review, scaffold, or blocker layer",
        "Review G3SX30 dry-run observation and decide the next data-producing step",
        "prepare a one-row live embedding decision",
        "repair a concrete blocker found in the dry-run observation",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_dry_run_observation_next_data_step_review() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 dry-run observation next data-step review checkpoint",
        "docs/g3sx30_dry_run_observation_next_data_step_review.md",
        "already-observed G3SX30 wrapper dry-run external observation",
        "directly decides the next data-producing step",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_wrapper_dry_run_execution_plan.json",
        "external JSON observation remains outside the repository and is not committed",
        "dry_run_observation_reviewed=true",
        "dry_run_observation_blocker_found=false",
        "dry_run_executed=true",
        "manifest_row_index=1",
        "target_accession=G3SX30",
        "target_taxid=9785",
        "reviewed_sequence_length=492",
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "manifest_row_read=true",
        "manifest_row_validated=true",
        "biohub_esmc_called=false",
        "embedding_generation_performed=false",
        "npy_artifact_created=false",
        "data_output_artifact_created=false",
        "ready_for_preflight_promoted=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "next_data_step_decision=approve_one_row_live_embedding_for_next_pr",
        "live_embedding_authorized_for_next_pr=true",
        "live_embedding_authorized_in_this_pr=false",
        "max_live_batch_size_for_next_pr=1",
        "ready_for_preflight_authorized=false",
        "gate8_promotion_authorized=false",
        "gate9_promotion_authorized=false",
        "biological_claim_authorized=false",
        "allowed_next_action_after_review=execute_one_row_g3sx30_live_embedding_with_strict_guardrails",
        "claim_status=technical_checkpoint",
        "does not rerun `g3sx30-wrapper-dry-run`",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not create or commit `data/output` artifacts",
        "does not run a live path in this PR",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "do not add another generic checkpoint, review, scaffold, or decision layer",
        "Execute one-row G3SX30 live embedding with strict guardrails",
        "one row only",
        "manifest row #1 only",
        "explicit live opt-in required",
        "max_live_batch_size=1",
        "local runtime artifact only",
        "no committed `.npy`",
        "no committed `data/output`",
        "no `ready_for_preflight`",
        "no Gate 8 / Gate 9",
        "no Boltz / AF3 / Chai",
        "no enrichment or contrast rerun",
        "no biological claim",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_one_row_live_embedding_guardrail_wrapper() -> None:
    text = read_doc("docs/current_gate_map.md")
    for required in [
        "G3SX30 one-row live embedding strict guardrail wrapper checkpoint",
        "src/longevity_port_pipelines/stages/g3sx30_live_embedding_one_row.py",
        "Execute one-row G3SX30 live embedding with strict guardrails",
        "g3sx30-live-embedding-one-row = longevity_port_pipelines.stages.g3sx30_live_embedding_one_row:app",
        "uv run g3sx30-live-embedding-one-row",
        "uv run g3sx30-live-embedding-one-row --yes-live --max-live-batch-size 1",
        "data/input/g3sx30_dry_run_preflight_manifest.csv#1",
        "execute_one_row_g3sx30_live_embedding_with_strict_guardrails",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta",
        "manifest_row_index=1",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "chain=mdm2",
        "target_accession=G3SX30",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "reviewed_sequence_length=492",
        "reviewed_sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "max_live_batch_size=1",
        "explicit `--yes-live` before any Biohub / ESMC call",
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not create `.npy` artifacts",
        "does not commit `data/output`",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "same PR may run the guarded command",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_one_row_live_embedding_runtime_observation() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row live embedding runtime observation checkpoint",
        "docs/g3sx30_one_row_live_embedding_runtime_observation.md",
        "uv run g3sx30-live-embedding-one-row --yes-live --max-live-batch-size 1",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json",
        "external observation artifacts are not committed",
        "manifest_path=data/input/g3sx30_dry_run_preflight_manifest.csv",
        "manifest_row_index=1",
        "reviewed_sequence_fasta=D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "chain=mdm2",
        "target_accession=G3SX30",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "model_name=esmc-300m-2024-12",
        "sequence_length=492",
        "sequence_sha256=e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f",
        "mode=live",
        "status=live_completed",
        "embedding_shape=492x960",
        "live_exit_code=0",
        "embedding_exists=true",
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "shape=492x960",
        "dtype=float32",
        "finite=true",
        "sequence_length_matches=true",
        "biohub_esmc_called=true",
        "embedding_generation_performed=true",
        "npy_artifact_created=true",
        "data_output_artifact_committed=false",
        "ready_for_preflight_promoted=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "artifact_location=local_runtime_data_output_ignored_by_git",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not commit the external FASTA artifact",
        "does not commit the external live log",
        "does not commit the external validation JSON",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make biological claims",
        "technical runtime checkpoint only",
        "does not unlock downstream gates by itself",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_post_live_local_artifact_status() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 post-live local artifact status checkpoint",
        "docs/g3sx30_post_live_local_artifact_status.md",
        "already-merged guarded one-row G3SX30 live embedding",
        "first guarded Biohub / ESMC live embedding call has already happened",
        "status=live_completed",
        "embedding_shape=492x960",
        "live_exit_code=0",
        "embedding_exists=true",
        "does not run live embedding again",
        "data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "local_runtime_embedding_exists=true",
        "tracked_embedding_files=none",
        "ignore_rule=.gitignore:9:data/output/*",
        "local_runtime_embedding_tracked=false",
        "local_runtime_embedding_committed=false",
        "artifact_location=local_runtime_data_output_ignored_by_git",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_output.txt",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_live_embedding_one_row_validation.json",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence.fasta",
        "D:/biohub_projects/_chatgpt_observations/g3sx30_reviewed_sequence_validation.json",
        "exist outside the repository and are not committed",
        "shape=492x960",
        "dtype=float32",
        "finite=true",
        "sequence_length_matches=true",
        "biohub_esmc_called=true",
        "embedding_generation_performed=true",
        "npy_artifact_created=true",
        "data_output_artifact_committed=false",
        "ready_for_preflight_promoted=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "does not make a new Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not commit the external FASTA artifact",
        "does not commit the external live log",
        "does not commit the external validation JSON",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
        "do not add another generic checkpoint, review, scaffold, or decision layer",
        "Review G3SX30 local embedding artifact and decide readiness/preflight path",
        "Approve G3SX30 local embedding artifact for one-row readiness/preflight input",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_local_embedding_readiness_input_decision() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row local embedding readiness/preflight input decision",
        "data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv",
        "docs/g3sx30_one_row_live_embedding_runtime_observation.md",
        "docs/g3sx30_post_live_local_artifact_status.md",
        "local_embedding_path=data/output/embeddings/esmc-300m-2024-12/"
        "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "external_validation_json=D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_live_embedding_one_row_validation.json",
        "local_runtime_embedding_exists=true",
        "local_runtime_embedding_tracked=false",
        "local_runtime_embedding_committed=false",
        "artifact_location=local_runtime_data_output_ignored_by_git",
        "embedding_shape=492x960",
        "embedding_dtype=float32",
        "embedding_finite=true",
        "sequence_length_matches=true",
        "validation_ready_for_preflight_promoted=false",
        "validation_gate8_promoted=false",
        "validation_gate9_promoted=false",
        "validation_biological_claim_made=false",
        "approved_for_one_row_readiness_preflight_input=true",
        "ready_for_preflight=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "approving the local artifact path as a one-row readiness/preflight input reference",
        "does not make a new Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
        "prepare_one_row_non_committed_preflight_input_consumer_or_manifest_binding_pr",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_non_committed_preflight_input_binding() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row non-committed preflight input binding",
        "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv",
        "machine-readable one-row binding",
        "G3SX30 / elephant MDM2 ESMC embedding artifact",
        "data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv#1",
        "approved_for_one_row_readiness_preflight_input=true",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession=G3SX30",
        "target_accession_db=UniProtKB TrEMBL",
        "target_species=Loxodonta africana",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "sequence_length=492",
        "local_embedding_path=data/output/embeddings/esmc-300m-2024-12/"
        "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "artifact_location=local_runtime_data_output_ignored_by_git",
        "local_runtime_embedding_tracked=false",
        "local_runtime_embedding_committed=false",
        "embedding_shape=492x960",
        "embedding_dtype=float32",
        "embedding_finite=true",
        "sequence_length_matches=true",
        "non_committed_preflight_input_reference_created=true",
        "ready_for_preflight=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "run_record_g3sx30_one_row_local_embedding_preflight_check",
        "next_check_scope=local_artifact_shape_dtype_finiteness_sequence_length_path_policy_only",
        "next_check_input=data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1",
        "next_check_output_policy=external_non_committed_observation_only",
        "D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_one_row_local_embedding_preflight_check.json",
        "do not add another review, scaffold, or binding layer",
        "does not make a new Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not copy external validation JSON into the repo",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_local_embedding_preflight_check_result() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row local embedding preflight check result",
        "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv",
        "externally executed local preflight check result",
        "G3SX30 / elephant MDM2 ESMC embedding artifact",
        "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1",
        "non_committed_preflight_input_reference_created=true",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession=G3SX30",
        "target_accession_db=UniProtKB TrEMBL",
        "target_species=Loxodonta africana",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "sequence_length=492",
        "D:/biohub_projects/_chatgpt_observations/"
        "g3sx30_one_row_local_embedding_preflight_check.json",
        "The external JSON is not committed.",
        "check_name=g3sx30_one_row_local_embedding_preflight_check",
        "check_status=local_preflight_pass",
        "local_embedding_path=data/output/embeddings/esmc-300m-2024-12/"
        "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "artifact_location=local_runtime_data_output_ignored_by_git",
        "local_runtime_embedding_exists=true",
        "local_runtime_embedding_tracked=false",
        "local_runtime_embedding_committed=false",
        "git_ignore_rule_status=data_output_ignored",
        "embedding_shape=492x960",
        "embedding_dtype=float32",
        "embedding_finite=true",
        "sequence_length_matches=true",
        "biohub_esmc_called_by_check=false",
        "live_embedding_rerun_by_check=false",
        "embedding_generation_performed_by_check=false",
        "npy_artifact_created_by_check=false",
        "data_output_artifact_committed=false",
        "external_validation_json_committed=false",
        "ready_for_preflight_promoted=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "boltz_called=false",
        "af3_called=false",
        "chai_called=false",
        "enrichment_rerun=false",
        "contrast_rerun=false",
        "biological_claim_made=false",
        "downstream_gate_unlocked=false",
        "concrete local artifact preflight pass",
        "does not mean `ready_for_preflight=true`",
        "does not promote Gate 8 or Gate 9",
        "does not make a biological claim",
        "approve_one_row_readiness_preflight_transition_path_or_repair_concrete_blocker",
        "pass decision path is `approve_one_row_readiness_preflight_transition_path`",
        "fail decision path is `repair_concrete_local_preflight_blocker`",
        "do not add another generic checkpoint, review, scaffold, or binding layer",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not commit the external local preflight JSON",
        "does not copy external validation JSON into the repo",
        "does not make a new Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not promote `ready_for_preflight`",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_readiness_preflight_transition_decision() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row readiness/preflight transition path decision",
        "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv",
        "final decision before the actual one-row G3SX30 readiness/preflight transition/check",
        "data/input/g3sx30_one_row_local_embedding_preflight_check_results.csv#1",
        "source_check_name=g3sx30_one_row_local_embedding_preflight_check",
        "source_check_status=local_preflight_pass",
        "source_embedding_shape=492x960",
        "source_embedding_dtype=float32",
        "source_embedding_finite=true",
        "source_sequence_length_matches=true",
        "source_local_runtime_embedding_tracked=false",
        "source_local_runtime_embedding_committed=false",
        "decision=approve_one_row_readiness_preflight_transition_path",
        "approved_for_next_transition_step=true",
        "ready_for_preflight=false",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "allowed_next_action=run_one_row_g3sx30_readiness_preflight_transition",
        "final decision PR before the actual transition/check",
        "next_pr_must_be_actual_transition_check=true",
        "no_additional_decision_before_transition=true",
        "next_required_pr_title=Run one-row G3SX30 readiness/preflight transition",
        "After this PR, the next PR must run the one-row G3SX30 readiness/preflight transition.",
        "Do not add another decision, review, scaffold, or binding layer before that.",
        "does not make a Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not promote `ready_for_preflight`",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_readiness_preflight_transition_result() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row readiness/preflight transition result",
        "data/input/g3sx30_one_row_readiness_preflight_transition_results.csv",
        "actual one-row G3SX30 readiness/preflight transition/check result",
        "This is not another approval, review, scaffold, or binding layer.",
        "data/input/g3sx30_one_row_readiness_preflight_transition_decisions.csv#1",
        "source_decision=approve_one_row_readiness_preflight_transition_path",
        "source_approved_for_next_transition_step=true",
        "source_allowed_next_action=run_one_row_g3sx30_readiness_preflight_transition",
        "source_next_pr_must_be_actual_transition_check=true",
        "source_no_additional_decision_before_transition=true",
        "transition_action=run_one_row_g3sx30_readiness_preflight_transition",
        "transition_status=one_row_readiness_preflight_transition_passed",
        "one_row_only=true",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession=G3SX30",
        "target_species=Loxodonta africana",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "ready_for_preflight=true",
        "ready_scope=one_row_g3sx30_elephant_mdm2_only",
        "The `ready_for_preflight=true` status applies only to this one row.",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "does not make a Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
        "add_first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "not another transition approval",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_one_row_controlled_downstream_use_path() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row controlled downstream use path",
        "data/input/g3sx30_one_row_controlled_downstream_use_paths.csv",
        "first controlled downstream use path",
        "This is not another decision layer.",
        "data/input/g3sx30_one_row_readiness_preflight_transition_results.csv#1",
        "source_transition_status=one_row_readiness_preflight_transition_passed",
        "source_ready_for_preflight=true",
        "source_allowed_downstream_use_path=first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "controlled_downstream_use_path=first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "controlled_handle_id=g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle",
        "controlled_input_status=one_row_ready_artifact_available_for_controlled_downstream_use",
        "one_row_only=true",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession=G3SX30",
        "target_species=Loxodonta africana",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "ready_scope=one_row_g3sx30_elephant_mdm2_only",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "does not make a Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
        "run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_downstream_use_path_anti_loop() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "next_pr_must_be_actual_controlled_downstream_read_check=true",
        "no_additional_downstream_approval_before_read_check=true",
        "Do not add another approval, review, scaffold, or binding layer before that read/check.",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_one_row_controlled_downstream_read_check_result() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row controlled downstream read/check result",
        "data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv",
        "actual controlled downstream read/check result",
        "This is not another approval layer, scaffold, handle, or decision layer.",
        "data/input/g3sx30_one_row_controlled_downstream_use_paths.csv#1",
        "source_controlled_downstream_use_path=first_controlled_downstream_use_path_for_one_row_ready_artifact",
        "source_controlled_handle_id=g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle",
        "source_controlled_input_status=one_row_ready_artifact_available_for_controlled_downstream_use",
        "source_ready_artifact_reference=data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "source_next_pr_must_be_actual_controlled_downstream_read_check=true",
        "source_no_additional_downstream_approval_before_read_check=true",
        "read_check_action=run_controlled_downstream_read_check_for_one_row_ready_g3sx30_artifact",
        "read_check_status=controlled_downstream_read_check_passed",
        "controlled_handle_id=g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle",
        "controlled_input_status=one_row_ready_artifact_available_for_controlled_downstream_use",
        "one_row_only=true",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession=G3SX30",
        "target_species=Loxodonta africana",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "ready_scope=one_row_g3sx30_elephant_mdm2_only",
        "local_runtime_embedding_exists=true",
        "local_runtime_embedding_tracked=false",
        "local_runtime_embedding_committed=false",
        "git_ignore_rule_status=data_output_ignored",
        "embedding_shape=492x960",
        "embedding_dtype=float32",
        "embedding_finite=true",
        "sequence_length=492",
        "sequence_length_matches=true",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "does not make a Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
        "move_toward_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact",
        "next_pr_should_move_toward_first_minimal_controlled_downstream_output=true",
        "no_additional_read_check_approval_before_output=true",
        "Do not add another read/check approval, review, scaffold, handle, or decision layer before that output-oriented step.",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_first_minimal_controlled_downstream_output() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row first minimal controlled downstream output",
        "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv",
        "creates the first minimal controlled downstream output",
        "actual output record, not another non-result layer",
        "data/input/g3sx30_one_row_controlled_downstream_read_check_results.csv#1",
        "source_read_check_status=controlled_downstream_read_check_passed",
        "source_controlled_handle_id=g3sx30_elephant_mdm2_one_row_ready_artifact_controlled_downstream_handle",
        "source_controlled_input_status=one_row_ready_artifact_available_for_controlled_downstream_use",
        "source_ready_artifact_reference=data/output/embeddings/esmc-300m-2024-12/tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy",
        "output_action=add_first_minimal_controlled_downstream_output_for_one_row_ready_g3sx30_artifact",
        "output_status=first_minimal_controlled_downstream_output_created",
        "output_type=one_row_artifact_identity_and_embedding_health_summary",
        "output_scope=identity_and_embedding_health_only_no_biological_claim",
        "candidate_id=tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession=G3SX30",
        "target_species=Loxodonta africana",
        "target_taxid=9785",
        "gene_symbol=MDM2",
        "one_row_only=true",
        "ready_scope=one_row_g3sx30_elephant_mdm2_only",
        "candidate_identity_confirmed=true",
        "artifact_reference_confirmed=true",
        "embedding_health_confirmed=true",
        "source_embedding_shape=492x960",
        "source_embedding_dtype=float32",
        "source_embedding_finite=true",
        "source_sequence_length=492",
        "source_sequence_length_matches=true",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "does not make a Biohub / ESMC call",
        "does not rerun live embedding",
        "does not generate a new embedding",
        "does not commit the generated `.npy` artifact",
        "does not commit any `data/output` artifact",
        "does not promote Gate 8 or Gate 9",
        "does not call Boltz / AF3 / Chai",
        "does not rerun enrichment or contrast",
        "does not make a biological claim",
        "move_toward_first_analysis_adjacent_controlled_output_or_next_concrete_biological_data_bearing_step_for_one_row_ready_g3sx30_artifact",
        "next_pr_should_be_concrete_analysis_adjacent_or_biological_data_bearing_step=true",
        "no_additional_non_result_layer_before_next_concrete_step=true",
        "Do not insert another non-result layer before that concrete step.",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_first_analysis_adjacent_embedding_summary() -> None:
    text = read_doc("docs/current_gate_map.md")

    for required in [
        "G3SX30 one-row first analysis-adjacent controlled embedding summary",
        "data/input/g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv#1",
        "first numerical analysis-adjacent result",
        "data/input/g3sx30_one_row_first_minimal_controlled_downstream_outputs.csv#1",
        "source_output_status=first_minimal_controlled_downstream_output_created",
        "source_output_type=one_row_artifact_identity_and_embedding_health_summary",
        "summary_status=first_analysis_adjacent_controlled_embedding_summary_created",
        "summary_type=one_row_embedding_scalar_summary_statistics",
        "summary_scope=scalar_embedding_statistics_only_no_biological_claim",
        "token_count=492",
        "embedding_dim=960",
        "total_values=472320",
        "finite_value_count=472320",
        "finite_fraction=1.0000000000",
        "pipeline integration / analysis-adjacent result",
        "not a biological comparison",
        "not a biological comparison, interface result, binding result, or longevity evidence",
        "gate8_promoted=false",
        "gate9_promoted=false",
        "biological_claim_made=false",
        "data_output_artifact_committed=false",
        "biohub_esmc_called_by_summary=false",
        "live_embedding_rerun_by_summary=false",
        "embedding_generation_performed_by_summary=false",
        "npy_artifact_created_by_summary=false",
        "raw_embedding_values_committed=false",
        "boltz_called=false",
        "af3_called=false",
        "chai_called=false",
        "enrichment_rerun=false",
        "contrast_rerun=false",
        "next_step=add_first_controlled_comparator_or_pairwise_embedding_summary",
        "next_pr_should_add_controlled_comparator_or_pairwise_embedding_summary=true",
        "no_additional_scalar_summary_approval_before_comparator=true",
        "no_additional_non_result_layer_before_next_concrete_step=true",
        "Do not insert another scalar-summary approval",
    ]:
        assert required in text


def test_current_gate_map_records_g3sx30_source_backed_human_mdm2_comparator_path() -> None:
    text = read_doc("docs/current_gate_map.md")
    for required in [
        "G3SX30 source-backed human MDM2 comparator path checkpoint",
        "g3sx30_source_backed_human_mdm2_comparator_paths.csv#1",
        "tp53_mdm2_pilot_manifest.csv#2",
        "tp53_mdm2_ortholog_repair_decisions.csv#2",
        "ortholog_evidence_review_decisions.csv#1",
        "g3sx30_one_row_first_analysis_adjacent_controlled_embedding_summaries.csv#1",
        "Q00987",
        "1ycr",
        "human_reference_source_backed=true",
        "human_embedding_available=false",
        "elephant_embedding_available=true",
        "pairwise_summary_created=false",
        "source_backed_human_mdm2_embedding_not_available",
        "does not call Biohub / ESMC",
        "does not generate embeddings",
        "does not promote Gate 8 or Gate 9",
        "does not make biological claims",
        "generate_source_backed_human_mdm2_embedding_and_create_first_pairwise_summary",
        "no additional comparator approval",
    ]:
        assert required in text
