"""Pipeline configuration: species, thresholds, paths."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from longevity_port_pipelines.models import LifespanCategory, Species

SPECIES_REGISTRY: dict[str, Species] = {
    "human": Species(name="human", taxid=9606, category=LifespanCategory.REFERENCE),
    "mouse": Species(name="mouse", taxid=10090, category=LifespanCategory.SHORT_LIVED),
    "naked_mole_rat": Species(
        name="naked_mole_rat", taxid=10181, category=LifespanCategory.LONG_LIVED
    ),
    "bowhead_whale": Species(
        name="bowhead_whale", taxid=27622, category=LifespanCategory.LONG_LIVED
    ),
    "bat": Species(name="myotis_lucifugus", taxid=59463, category=LifespanCategory.LONG_LIVED),
}

LONG_LIVED_SPECIES = [
    sp for sp in SPECIES_REGISTRY.values() if sp.category == LifespanCategory.LONG_LIVED
]
SHORT_LIVED_SPECIES = [
    sp for sp in SPECIES_REGISTRY.values() if sp.category == LifespanCategory.SHORT_LIVED
]
REFERENCE_SPECIES = SPECIES_REGISTRY["human"]

TARGET_SPECIES = LONG_LIVED_SPECIES + SHORT_LIVED_SPECIES


class PipelineConfig(BaseModel):
    """Full pipeline configuration."""

    input_dir: Path = Path("data/input")
    interim_dir: Path = Path("data/interim")
    output_dir: Path = Path("data/output")

    # Stage 1: PINDER selection
    pinder_dataset: str = "Synthyra/PINDER"
    negatome_dataset: str = "Synthyra/NEGATOME"
    candidate_sets_path: Path = Path("data/config/candidate_sets.yaml")
    candidate_set: str = "ampk_pilot"
    allow_unfiltered_fallback: bool = True
    selection_count: int = 10
    min_interface_contacts: int = 5
    max_resolution: float = 3.0
    max_chain_length: int = 1000
    allow_predicted_structures: bool = True

    # Stage 2: Foldseek conservation
    min_cluster_species: int = 3

    # Stage 3: STRING hubs
    string_score_threshold: int = 700
    hub_partner_threshold: int = 15

    # Stage 5: embedding (Biohub Platform REST API; token via BIOHUB_API_TOKEN env)
    biohub_api_url: str = "https://biohub.ai"
    esmc_model: str = "esmc-300m-2024-12"

    # Stage 6: analysis
    n_permutations: int = 1000
    interface_distance_cutoff: float = 8.0

    def ensure_dirs(self) -> None:
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.interim_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "plots").mkdir(parents=True, exist_ok=True)
