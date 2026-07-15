from pathlib import Path

DOC_PATH = Path("docs/tp53_mdm2_first_curated_negatome_interface_control_result.md")


def test_curated_negatome_result_doc_records_exact_concrete_outcome() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for required in (
        "First TP53/MDM2 curated NEGATOME interface-control result",
        "curated_negatome_record_reviewed_no_computable_interface_control",
        "not an inventory, plan, scaffold, or generic refactor",
        "DOI `10.7554/eLife.11994`",
        "Figure `10E`",
        "`ENSLAFG00000028299`",
        "HEK-293",
        "Endogenous human MDM2",
        "internal positive co-immunoprecipitation control",
        "Myc-tagged TP53RTG12 was not detected",
        "`F19`, `W23`, and `L26`",
        "`W23G`",
        "5c9b77284294997ad5067be4a6991a54892bf883f9d91c0e334004d9068089c0",
        "MDM2 chain-`A` mask containing `47` of",
        "an MDM2-side negative residue mask",
        "residue_level_context_available=false",
        "deterministic_sequence_context_available=false",
        "interface_control_metric_computed=false",
        "curated_record_does_not_define_residue_level_or_deterministic_sequence_context",
        "conditional interface strength",
        "random overlap",
        "protein length",
        "arbitrary sequence similarity",
        "existing NEGATOME path remains valid",
        "embedding-based NEGATOME",
        "existing_runtime_negatome_path_reused=false",
        "requires_embed_sequence_npy_and_per_residue_embeddings",
        "valid_for_embedding_based_negatome_control_ratio",
        "no Biohub / ESMC call",
        "no new embeddings",
        "no `.npy` artifact",
        "no `data/output` artifact",
        "no Boltz / AF3 / Chai",
        "neither Gate 8 nor Gate 9",
        "does not establish binding, non-binding, binding strength",
        "not a biological claim",
        "curated_negatome_control_computed=false",
        "curated_negatome_control_closed=false",
        "add_first_tp53_mdm2_control_closure_result",
        "No inventory-only, plan-only, scaffold-only",
    ):
        assert required in text
