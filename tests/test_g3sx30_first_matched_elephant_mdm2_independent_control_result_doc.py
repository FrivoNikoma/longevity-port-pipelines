from pathlib import Path


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def test_matched_control_document_records_result_and_boundary() -> None:
    text = read_text("docs/g3sx30_first_matched_elephant_mdm2_independent_control_result.md")

    for required in [
        "First matched elephant MDM2 independent control result",
        "G3SX30",
        "P09874",
        "EPQ16369.1",
        "0.8409825967886765",
        "0.1563488334452703",
        "-0.0093635408405441",
        "0.0093635408405441",
        "not a validated biological negative control",
        "does not perform a new inventory",
        "does not reselect the comparator",
        "does not promote Gate 8 or Gate 9",
        "add_first_additional_source_backed_independent_comparator_result_with_selection_frozen_in_same_step",
        "No separate",
    ]:
        assert required in text


def test_matched_control_schema_records_frozen_comparator() -> None:
    text = read_text(
        "data/config/g3sx30_first_matched_elephant_mdm2_independent_control_result_schema.yaml"
    )

    for required in [
        "comparator_reselected: false",
        "comparator_remained_frozen: true",
        "accession: G3SX30",
        "target_accession: EPQ16369.1",
        "elephant_mdm2_to_frozen_comparator_cosine_similarity: 0.8409825967886765",
        "required_sha256: 4fe3e2ec90e83eb82a4e6ac792845259fec47c03f151e0f979cd2b4d71d73301",
        "biological_claim: false",
    ]:
        assert required in text
