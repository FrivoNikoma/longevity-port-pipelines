# Documentation tests for the MDM2-side shuffled control.

from pathlib import Path

DOC_PATH = Path("docs/tp53_mdm2_first_mdm2_side_shuffled_interface_control_result.md")


def test_mdm2_side_shuffled_control_doc_records_exact_result() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for required in (
        "First TP53/MDM2 MDM2-side shuffled-interface control result",
        "`1YCR`",
        "MDM2 chain-`A`",
        "`85`-residue MDM2 chain",
        "`47` chain-local positions",
        "TP53 chain `B` is not shuffled",
        "`numpy.random.default_rng`",
        "seed: `42`",
        "control masks: `1000`",
        "6ebc3aea77388a9929d945acdb1962fe8eed148feecac7326fcbeceefbe2015c",
        "Adjacent residue pairs",
        "`38`",
        "`25.4239999999999995`",
        "Contiguous runs",
        "`9`",
        "`21.5760000000000005`",
        "Longest contiguous run",
        "`16`",
        "`6.6260000000000003`",
        "more sequence-contiguous",
        "does not establish binding",
        "no curated NEGATOME control",
        "no Biohub / ESMC call",
        "no `.npy` read or commit",
        "no Gate 8 or Gate 9 promotion",
        "not a biological claim",
        "adds no generic shuffle framework",
        "add_first_tp53_mdm2_curated_negatome_interface_control_result",
        "No inventory-only, preflight-only, plan-only",
    ):
        assert required in text
