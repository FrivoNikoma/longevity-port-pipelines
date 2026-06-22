from __future__ import annotations

import polars as pl
from scripts.make_sirt6_mini_pilot_v2_core3_expanded import (
    build_core3_outputs,
    build_readiness_audit,
    core3_ready_ids,
)


def selection_frame() -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "id": "complex_ready",
                "pdb_id": "1abc",
                "uniprot_R": "UR",
                "uniprot_L": "UL",
                "intermolecular_contacts": 42,
                "predicted_R": False,
                "predicted_L": False,
            }
        ]
    )


def coverage_frame(rows: list[tuple[str, int, str]]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "source_uniprot": source_uniprot,
                "target_species_taxid": taxid,
                "target_uniprot": target_uniprot,
            }
            for source_uniprot, taxid, target_uniprot in rows
        ],
        schema={
            "source_uniprot": pl.Utf8,
            "target_species_taxid": pl.Int64,
            "target_uniprot": pl.Utf8,
        },
    )


def test_core3_audit_covers_expanded_species_but_requires_only_core_species() -> None:
    selection = selection_frame()
    coverage = coverage_frame(
        [
            # Core3 required species for both chains.
            ("UR", 10181, "UR_NMR"),
            ("UL", 10181, "UL_NMR"),
            ("UR", 59463, "UR_MYO"),
            ("UL", 59463, "UL_MYO"),
            ("UR", 10090, "UR_MOUSE"),
            ("UL", 10090, "UL_MOUSE"),
            # Extra registry species should be audited and retained when available,
            # but not required for core3 readiness.
            ("UR", 10116, "UR_RAT"),
        ]
    )

    readiness_audit = build_readiness_audit(selection, coverage)

    assert readiness_audit["target_species"].n_unique() == 8
    assert "required_for_core3" in readiness_audit.columns

    records = {
        (row["chain_role"], row["target_species"]): row
        for row in readiness_audit.iter_rows(named=True)
    }

    assert records[("receptor", "rat")]["has_ortholog_mapping"] is True
    assert records[("receptor", "rat")]["required_for_core3"] is False
    assert records[("ligand", "rat")]["has_ortholog_mapping"] is False
    assert records[("ligand", "rat")]["required_for_core3"] is False

    assert records[("receptor", "mouse")]["required_for_core3"] is True
    assert records[("ligand", "mouse")]["required_for_core3"] is True

    assert core3_ready_ids(readiness_audit) == ["complex_ready"]

    core_selection, core_coverage = build_core3_outputs(selection, coverage, readiness_audit)

    assert core_selection.height == 1
    assert 10116 in core_coverage["target_species_taxid"].to_list()


def test_core3_ready_ids_excludes_complex_missing_required_species() -> None:
    selection = selection_frame()
    coverage = coverage_frame(
        [
            ("UR", 10181, "UR_NMR"),
            ("UL", 10181, "UL_NMR"),
            ("UR", 59463, "UR_MYO"),
            # Missing ligand Myotis mapping makes the complex not core3-ready.
            ("UR", 10090, "UR_MOUSE"),
            ("UL", 10090, "UL_MOUSE"),
            # Extra non-required species cannot rescue missing required coverage.
            ("UR", 10116, "UR_RAT"),
            ("UL", 10116, "UL_RAT"),
        ]
    )

    readiness_audit = build_readiness_audit(selection, coverage)

    assert core3_ready_ids(readiness_audit) == []
