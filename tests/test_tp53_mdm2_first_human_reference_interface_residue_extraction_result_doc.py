"""Documentation tests for the first TP53/MDM2 interface extraction result."""

from pathlib import Path

RESULT_DOC = Path("docs/tp53_mdm2_first_human_reference_interface_residue_extraction_result.md")
SUMMARY_TABLE = Path(
    "data/input/tp53_mdm2_first_human_reference_interface_residue_extraction_results.csv"
)
RESIDUE_TABLE = Path("data/input/tp53_mdm2_first_human_reference_interface_residue_records.csv")
SCHEMA_PATH = Path(
    "data/config/tp53_mdm2_first_human_reference_interface_residue_extraction_result_schema.yaml"
)
VALIDATOR_PATH = Path(
    "src/longevity_port_pipelines/stages/"
    "tp53_mdm2_first_human_reference_interface_residue_extraction_result.py"
)


def test_interface_extraction_result_artifacts_exist() -> None:
    for path in (
        RESULT_DOC,
        SUMMARY_TABLE,
        RESIDUE_TABLE,
        SCHEMA_PATH,
        VALIDATOR_PATH,
    ):
        assert path.is_file(), path


def test_interface_extraction_result_doc_records_exact_result() -> None:
    text = RESULT_DOC.read_text(encoding="utf-8")

    for required in (
        "RCSB PDB",
        "`1YCR`",
        "`Q00987`, chain `A`",
        "`P04637`, chain `B`",
        "`95202` bytes",
        "`7b4e503dea1fe3a6966b9676a1b98caf511c735cde01029cd0998e2319e75493`",
        "`47` residues",
        "`38` residues outside the mask",
        "`13` parsed residues",
        "`13 / 13 = 1.0000000000000000`",
        "within-chain shuffle is degenerate for TP53 chain `B`",
        "restricted to MDM2 chain `A`",
        "not binding-hotspot annotations",
        "not a biological claim",
        "add_first_tp53_mdm2_mdm2_side_shuffled_interface_control_result",
        "No preflight-only, inventory-only, plan-only",
    ):
        assert required in text
