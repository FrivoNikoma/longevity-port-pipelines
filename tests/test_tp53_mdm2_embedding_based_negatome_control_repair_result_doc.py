from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tp53_mdm2_repair_retry_doc_records_coherent_result() -> None:
    text = (ROOT / "docs/tp53_mdm2_embedding_based_negatome_control_repair_result.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "result-bearing repair/retry",
        "chain_local_to_full_length_interface_mapping_not_verified -> resolved",
        "exact_negatome_pair_lookup_key_missing -> resolved",
        "negative_partner_embedding_missing_or_invalid",
        "mapping_unique=true",
        "mapped_interface_count=47",
        "mapped_indices_unique=true",
        "mapped_indices_in_bounds=true",
        "residue_identity_consistent=true",
        "ENSLAFG00000028299",
        "ENSLAFT00000037003",
        "ENSLAFP00000024998",
        "G3UAZ0",
        "sequence_length=364",
        "reported_w23g_alignment_consistent=true",
        "exact_pair_schema_valid=true",
        "repaired_pair_runtime_loadable=true",
        "model_name=esmc-300m-2024-12",
        "human_shape=491x960",
        "elephant_shape=492x960",
        "No G3UAZ0 embedding existed",
        "negatome_control_ratio=not_computed",
        "blocked_pending_control_repair",
        "gate7_entry_allowed_after=false",
        "no Biohub / ESMC call",
        "commits no `.npy` or `data/output`",
        "no binding, functional, beneficial-breakage",
    ):
        assert required in text
