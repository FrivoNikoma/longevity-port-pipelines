"""Pydantic v2 data models for the cross-species interface pipeline."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class LifespanCategory(StrEnum):
    LONG_LIVED = "long-lived"
    SHORT_LIVED = "short-lived"
    REFERENCE = "reference"


class LongevityCategory(StrEnum):
    """Functional category for a candidate longevity protein (Task A)."""

    PRO_LONGEVITY = "pro-longevity"
    DNA_REPAIR = "dna-repair"
    PROTEOSTASIS = "proteostasis"
    INFLAMMATION = "inflammation/cGAS-STING"
    MITOCHONDRIAL = "mitochondrial-stress"
    SENESCENCE = "senescence"
    ECM = "ecm/hyaluronan"
    STRESS_RESPONSE = "stress-response/cold-shock"


class CandidateProtein(BaseModel):
    """A seed candidate protein for the longevity-interface screen (Task A)."""

    gene_name: str
    uniprot_id: str
    category: LongevityCategory
    description: str = ""


class Species(BaseModel):
    """A species with its NCBI taxonomy ID and lifespan category."""

    name: str
    taxid: int
    category: LifespanCategory


class PPIComplex(BaseModel):
    """A protein-protein interaction complex from PINDER."""

    pinder_id: str
    pdb_id: str | None = None
    receptor_uniprot: str | None = None
    ligand_uniprot: str | None = None
    receptor_sequence: str
    ligand_sequence: str
    receptor_chain: str | None = None
    ligand_chain: str | None = None
    interface_residues_receptor: list[int] = Field(default_factory=list)
    interface_residues_ligand: list[int] = Field(default_factory=list)
    is_predicted_receptor: bool = False
    is_predicted_ligand: bool = False
    n_interface_contacts: int = 0
    buried_sasa: float | None = None
    resolution: float | None = None
    string_partners_receptor: int | None = None
    string_partners_ligand: int | None = None
    foldseek_cluster: str | None = None
    is_hub: bool = False
    selected: bool = False
    selection_reason: str = ""


class OrthologMapping(BaseModel):
    """Maps a source protein to its ortholog in another species."""

    source_uniprot: str
    source_species_taxid: int
    target_uniprot: str
    target_species_taxid: int
    target_sequence: str
    is_reviewed: bool
    source_db: str


class OrthologCoverage(BaseModel):
    """Ortholog availability summary for a complex across target species."""

    complex_id: str
    chain: str
    source_uniprot: str
    target_species: str
    target_taxid: int
    has_ortholog: bool
    target_uniprot: str | None = None
    is_reviewed: bool | None = None
    source_db: str | None = None


class EmbeddingDelta(BaseModel):
    """Per-residue embedding delta between reference and ortholog."""

    complex_id: str
    chain: str
    model_name: str
    source_species_taxid: int
    target_species_taxid: int
    n_aligned_residues: int
    interface_mean_delta: float
    noninterface_mean_delta: float
    is_predicted_structure: bool = False


class EnrichmentResult(BaseModel):
    """Enrichment of embedding shift at interface vs non-interface residues."""

    complex_id: str
    model_name: str
    source_species: str
    target_species: str
    chain: str
    interface_mean_delta: float
    noninterface_mean_delta: float
    enrichment_ratio: float
    shuffled_control_ratio: float
    negatome_control_ratio: float | None = None
    mann_whitney_p: float
    effect_size_cohens_d: float
    is_predicted_structure: bool = False
