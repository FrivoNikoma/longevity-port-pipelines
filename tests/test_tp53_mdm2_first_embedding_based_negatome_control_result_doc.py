from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / ("docs/tp53_mdm2_first_embedding_based_negatome_control_result.md")


def test_result_doc_records_checked_blocker_contract() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    for required in (
        "result-bearing checked blocker result",
        "checked_blocker_count=2",
        "chain_local_to_full_length_interface_mapping_not_verified",
        "data/interim/pdb/1ycr.pdb",
        "exact_negatome_pair_lookup_key_missing",
        "data/interim/negatome_control_pairs.csv",
        "human `Q00987`",
        "elephant `G3SX30`",
        "491x960",
        "492x960",
        "zero_based_chain_local_residue_indices",
        "local_1ycr_pdb_candidate_count=0",
        "tp53_mdm2_elephant_seed_mdm2_chain|mdm2|elephant",
        "negatome_pair_exact_lookup_row_count=0",
        "embedding_based_negatome_control_computed=false",
        "negatome_control_ratio=not_computed",
        "No surrogate ratio is invented",
        "blocked_pending_control_repair",
        "gate7_entry_allowed_after=false",
        "does not open Gate 7",
        "not biological approval",
        "writes or commits no `.npy` artifact",
        "no automatic Biohub / ESMC call",
        "no biological claim",
        "e92c045e44db2800fe2cb643bab281d875a1de6e0ce2413a2fed9b23bc3a49c2",
        "repair_local_mapping_and_exact_pair_then_add_first_",
        "must not become a separate inventory-only",
    ):
        assert required in text
