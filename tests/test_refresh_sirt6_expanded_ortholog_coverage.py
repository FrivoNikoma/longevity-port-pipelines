from __future__ import annotations

import polars as pl
import pytest
from scripts import refresh_sirt6_expanded_ortholog_coverage as refresh

from longevity_port_pipelines.models import LifespanCategory, Species


class FakeMapping:
    def __init__(self, source_uniprot: str, target_species_taxid: int) -> None:
        self.source_uniprot = source_uniprot
        self.target_species_taxid = target_species_taxid


def test_selected_uniprots_deduplicates_receptor_and_ligand_ids() -> None:
    selection = pl.DataFrame(
        {
            "uniprot_R": ["P1", "P2", "P1", None],
            "uniprot_L": ["P3", "P2", "", " P4 "],
        }
    )

    assert refresh.selected_uniprots(selection) == ["P1", "P2", "P3", "P4"]


def test_fetch_ortholog_coverage_records_mappings_and_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    targets = [
        Species(name="mouse", taxid=10090, category=LifespanCategory.SHORT_LIVED),
        Species(name="rat", taxid=10116, category=LifespanCategory.SHORT_LIVED),
    ]

    calls: list[tuple[str, int]] = []

    def fake_fetch_ortholog(uniprot_id: str, target: Species) -> FakeMapping | None:
        calls.append((uniprot_id, target.taxid))
        if uniprot_id == "P1" and target.name == "mouse":
            return FakeMapping(uniprot_id, target.taxid)
        return None

    monkeypatch.setattr(refresh, "fetch_ortholog", fake_fetch_ortholog)

    mappings, missing = refresh.fetch_ortholog_coverage(["P1"], targets)

    assert calls == [("P1", 10090), ("P1", 10116)]
    assert len(mappings) == 1
    assert mappings[0].source_uniprot == "P1"
    assert mappings[0].target_species_taxid == 10090

    assert missing == [
        {
            "source_uniprot": "P1",
            "target_species_taxid": 10116,
            "target_species": "rat",
            "reason": "no_ortholog_mapping",
        }
    ]


def test_require_columns_reports_missing_columns() -> None:
    frame = pl.DataFrame({"uniprot_R": ["P1"]})

    with pytest.raises(ValueError, match="missing required columns"):
        refresh.require_columns(frame, {"uniprot_R", "uniprot_L"}, refresh.Path("selection.csv"))
