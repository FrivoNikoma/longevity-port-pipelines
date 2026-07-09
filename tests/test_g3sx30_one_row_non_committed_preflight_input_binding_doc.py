from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/g3sx30_one_row_non_committed_preflight_input_binding.md"
SCHEMA = ROOT / "data/config/g3sx30_one_row_non_committed_preflight_input_binding_schema.yaml"


def test_g3sx30_binding_doc_identifies_target_and_artifact() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "G3SX30 / elephant MDM2",
        "candidate_id = tp53_mdm2_elephant_seed_mdm2_chain",
        "target_accession = G3SX30",
        "target_species = Loxodonta africana",
        "target_taxid = 9785",
        "gene_symbol = MDM2",
        "sequence_length = 492",
        "embedding_shape = 492x960",
        "embedding_dtype = float32",
        "embedding_finite = true",
        "sequence_length_matches = true",
    ]:
        assert required in text


def test_g3sx30_binding_doc_records_decision_and_next_check() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "source_decision_table = data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv",
        "source_decision_row_index = 1",
        "approved_for_one_row_readiness_preflight_input = true",
        "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv",
        "non_committed_preflight_input_reference_created = true",
        "ready_for_preflight = false",
        "gate8_promoted = false",
        "gate9_promoted = false",
        "biological_claim_made = false",
        "next_concrete_check = run_record_g3sx30_one_row_local_embedding_preflight_check",
        "next_check_scope = local_artifact_shape_dtype_finiteness_sequence_length_path_policy_only",
        "next_check_input = data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv#1",
        "next_check_output_policy = external_non_committed_observation_only",
        "Run/record G3SX30 one-row local embedding preflight check",
    ]:
        assert required in text


def test_g3sx30_binding_doc_records_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    for required in [
        "make a new Biohub / ESMC call",
        "rerun live embedding",
        "generate a new embedding",
        "commit the generated `.npy` artifact",
        "commit any `data/output` artifact",
        "copy external validation JSON into the repo",
        "promote `ready_for_preflight`",
        "promote Gate 8 or Gate 9",
        "call Boltz / AF3 / Chai",
        "rerun enrichment or contrast",
        "make a biological claim",
    ]:
        assert required in text


def test_g3sx30_binding_schema_records_required_semantics() -> None:
    text = SCHEMA.read_text(encoding="utf-8")

    for required in [
        "g3sx30_one_row_non_committed_preflight_input_binding",
        "data/input/g3sx30_one_row_local_embedding_readiness_input_decisions.csv",
        "data/input/g3sx30_one_row_non_committed_preflight_input_bindings.csv",
        "target_accession: G3SX30",
        "target_species: Loxodonta africana",
        'target_taxid: "9785"',
        "gene_symbol: MDM2",
        "non_committed_preflight_input_reference_created",
        "run_record_g3sx30_one_row_local_embedding_preflight_check",
        "external_non_committed_observation_only",
        "ready_for_preflight promotion",
        "Gate 8 promotion",
        "biological claim",
    ]:
        assert required in text
