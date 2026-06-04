"""Tests for species registry consistency and config logic."""

from longevity_port_pipelines.config import (
    LONG_LIVED_SPECIES,
    REFERENCE_SPECIES,
    SHORT_LIVED_SPECIES,
    SPECIES_REGISTRY,
    TARGET_SPECIES,
)
from longevity_port_pipelines.models import LifespanCategory


def test_species_registry_categories_are_consistent() -> None:
    """Every species in LONG/SHORT lists must actually have the matching category."""
    for sp in LONG_LIVED_SPECIES:
        assert sp.category == LifespanCategory.LONG_LIVED, f"{sp.name} should be long-lived"
    for sp in SHORT_LIVED_SPECIES:
        assert sp.category == LifespanCategory.SHORT_LIVED, f"{sp.name} should be short-lived"


def test_target_species_excludes_reference() -> None:
    """The reference species (human) must not appear in the target list."""
    target_taxids = {sp.taxid for sp in TARGET_SPECIES}
    assert REFERENCE_SPECIES.taxid not in target_taxids


def test_all_registry_species_accounted_for() -> None:
    """Every species in the registry lands in exactly one group (ref or target)."""
    accounted_taxids = {sp.taxid for sp in TARGET_SPECIES}
    accounted_taxids.add(REFERENCE_SPECIES.taxid)
    registry_taxids = {sp.taxid for sp in SPECIES_REGISTRY.values()}
    assert accounted_taxids == registry_taxids, (
        f"Unaccounted taxids: {registry_taxids - accounted_taxids}"
    )


def test_taxids_are_unique() -> None:
    taxids = [sp.taxid for sp in SPECIES_REGISTRY.values()]
    assert len(taxids) == len(set(taxids)), "Duplicate taxids in registry"
