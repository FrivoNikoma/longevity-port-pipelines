from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig")


def test_independent_control_doc_records_selection_before_similarity() -> None:
    text = read_doc("docs/g3sx30_first_independent_pairwise_embedding_control_result.md")
    for required in [
        "Selection was frozen before similarity",
        "inventory_similarity_computed = false",
        "inventory_embedding_file_count = 216",
        "inventory_technical_candidate_count = 1",
        "selected before its similarity to human MDM2 was known",
        "not an inventory-only",
    ]:
        assert required in text


def test_independent_control_doc_records_exact_result() -> None:
    text = read_doc("docs/g3sx30_first_independent_pairwise_embedding_control_result.md")
    for required in [
        "P09874",
        "EPQ16369.1",
        "brandts_bat",
        "0.9973314302339468",
        "0.8316190559481323",
        "0.1657123742858144",
        "first_independent_pairwise_embedding_control_result_created",
        "577b0b24c6a0657c78e0db2ab8b71499cf8dd2a5dd72b6ee33c241058bdbcf23",
    ]:
        assert required in text


def test_independent_control_doc_keeps_claim_and_runtime_boundary() -> None:
    text = read_doc("docs/g3sx30_first_independent_pairwise_embedding_control_result.md")
    for required in [
        "not a validated biological negative control",
        "not residue alignment",
        "not interface analysis",
        "not a binding result",
        "not orthology proof",
        "not functional-equivalence evidence",
        "not longevity evidence",
        "biohub_esmc_called = false",
        "new_embedding_generated = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "add_first_matched_elephant_mdm2_independent_control_result_before_interpretation",
    ]:
        assert required in text
