from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs/tp53_mdm2_first_gate6_blocker_disposition_result.md"


def test_gate6_blocker_disposition_doc_records_exact_result() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for required in (
        "First TP53/MDM2 Gate 6 blocker-disposition result",
        "does not aggregate or recompute the underlying evidence",
        "gate6_blocker_disposition_recorded_require_embedding_based_control",
        "disposition_class=repair",
        "disposition_action=require_embedding_based_control",
        "closed_with_curated_negatome_interface_control_blocked",
        "57587b740da5df9685b5c5eace1428f675e961e1323a31a50cb04bd5a6d60ed7",
        "information_missing_not_runtime_failure",
        "`W23G`",
        "`47 / 85` geometric mask",
        "generic_control_repair_status=pending",
        "generic_control_readiness_status=blocked_pending_control_repair",
        "generic_contrast_dry_run_allowed=false",
        "generic_controlled_claim_allowed=false",
        "Gate 6 remains blocked",
        "Gate 6 blocker disposition is not biological approval",
        "It does not open",
        "Gate 7",
        "evidence_recomputed=false",
        "runtime_execution_authorized=false",
        "embedding_based_control_computed=false",
        "existing_embedding_based_negatome_runtime_reused=false",
        "no evidence recomputation",
        "no interface scoring",
        "no elephant interface scoring",
        "no new embeddings",
        "no `.npy` read or write",
        "no `data/output` artifact",
        "no Biohub / ESMC call",
        "no Boltz / AF3 / Chai",
        "no Gate 8 or Gate 9 promotion",
        "no biological claim",
        "valid_for_embedding_based_negatome_control_ratio",
        "1ef15df255929ca89e248fabec6eba6456d89a972b230389dd7135f24b13b4e4",
        "add_first_tp53_mdm2_embedding_based_negatome_control_result",
        "No inventory-only, plan-only, scaffold-only, vocabulary-only",
    ):
        assert required in text
