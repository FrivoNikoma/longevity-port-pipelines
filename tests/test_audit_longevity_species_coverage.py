from __future__ import annotations

import polars as pl
import pytest
from scripts.audit_longevity_species_coverage import build_species_coverage_audit


def test_build_species_coverage_audit_marks_present_and_missing_species() -> None:
    df = pl.DataFrame(
        {
            "target_species": [
                "mouse",
                "mouse",
                "naked_mole_rat",
                "myotis_lucifugus",
            ]
        },
        schema={"target_species": pl.Utf8},
    )

    coverage = build_species_coverage_audit(df)

    records = {
        (row["species_group"], row["species"]): row for row in coverage.iter_rows(named=True)
    }

    assert records[("short_lived", "mouse")]["present"] is True
    assert records[("short_lived", "mouse")]["row_count"] == 2

    assert records[("short_lived", "rat")]["present"] is False
    assert records[("short_lived", "rat")]["row_count"] == 0

    assert records[("long_lived", "naked_mole_rat")]["present"] is True
    assert records[("long_lived", "naked_mole_rat")]["row_count"] == 1

    assert records[("long_lived", "myotis_lucifugus")]["present"] is True
    assert records[("long_lived", "myotis_lucifugus")]["row_count"] == 1


def test_build_species_coverage_audit_requires_target_species_column() -> None:
    df = pl.DataFrame({"species": ["mouse"]})

    with pytest.raises(ValueError, match="Missing required columns"):
        build_species_coverage_audit(df)
