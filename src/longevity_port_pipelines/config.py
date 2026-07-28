"""Pipeline configuration: species, thresholds, paths."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from longevity_port_pipelines.models import LifespanCategory, Species

SPECIES_REGISTRY: dict[str, Species] = {
    "human": Species(name="human", taxid=9606, category=LifespanCategory.REFERENCE),
    "mouse": Species(name="mouse", taxid=10090, category=LifespanCategory.SHORT_LIVED),
    # Additional short-lived controls (taxids verified via UniProt taxonomy API).
    "rat": Species(name="rat", taxid=10116, category=LifespanCategory.SHORT_LIVED),
    "hamster": Species(name="hamster", taxid=10036, category=LifespanCategory.SHORT_LIVED),
    "naked_mole_rat": Species(
        name="naked_mole_rat", taxid=10181, category=LifespanCategory.LONG_LIVED
    ),
    "bowhead_whale": Species(
        name="bowhead_whale", taxid=27622, category=LifespanCategory.LONG_LIVED
    ),
    "bat": Species(name="myotis_lucifugus", taxid=59463, category=LifespanCategory.LONG_LIVED),
    # Additional long-lived species (taxids verified via UniProt taxonomy API).
    "elephant": Species(name="elephant", taxid=9785, category=LifespanCategory.LONG_LIVED),
    "brandts_bat": Species(name="brandts_bat", taxid=109478, category=LifespanCategory.LONG_LIVED),
    # Additional independent long-lived rodent lineages with good OMA/Ensembl coverage
    # (confirmed empirically by the orthologs stage). Damaraland (Fukomys) and blind
    # (Nannospalax) mole-rats are long-lived, cancer-resistant subterranean rodents from
    # lineages independent of the naked mole-rat (Heterocephalus), which strengthens the
    # cross-lineage convergence test. Bowhead whale, Brandt's/big-brown bat, and Mongolian
    # gerbil were also tested but lack ortholog coverage for this panel.
    "damaraland_mole_rat": Species(
        name="damaraland_mole_rat", taxid=885580, category=LifespanCategory.LONG_LIVED
    ),
    "blind_mole_rat": Species(
        name="blind_mole_rat", taxid=1026970, category=LifespanCategory.LONG_LIVED
    ),
    # Well-annotated short-lived control — boosts Mann-Whitney power (n depends on both groups).
    "guinea_pig": Species(name="guinea_pig", taxid=10141, category=LifespanCategory.SHORT_LIVED),
    # --- Expanded panel for the convergent-divergent (BMAL vs ELLSM) design ---
    # Longevity is convergent via divergent strategies, so pooling all long-lived species can
    # cancel signal. Below we add candidate species for two long-lived strata plus a typical-
    # lifespan reference group. Category here is only used to make them pipeline targets
    # (BMAL/ELLSM -> LONG_LIVED; reference-typical -> SHORT_LIVED); the analysis grouping is by
    # the *_NAMES lists below. Taxids are best-effort; species without ortholog coverage simply
    # drop out at the scoping step. (bowhead_whale/brandts_bat above already carry 0 coverage.)
    # BMAL: body-mass-associated long-lived (large-bodied).
    "asiatic_elephant": Species(
        name="asiatic_elephant", taxid=9783, category=LifespanCategory.LONG_LIVED
    ),
    "white_rhino": Species(name="white_rhino", taxid=73337, category=LifespanCategory.LONG_LIVED),
    "sperm_whale": Species(name="sperm_whale", taxid=9755, category=LifespanCategory.LONG_LIVED),
    "killer_whale": Species(name="killer_whale", taxid=9733, category=LifespanCategory.LONG_LIVED),
    "minke_whale": Species(name="minke_whale", taxid=310752, category=LifespanCategory.LONG_LIVED),
    "blue_whale": Species(name="blue_whale", taxid=9771, category=LifespanCategory.LONG_LIVED),
    "beluga": Species(name="beluga", taxid=9749, category=LifespanCategory.LONG_LIVED),
    # ELLSM: extremely long-lived small mammals (mole-rats + bats).
    "egyptian_rousette": Species(
        name="egyptian_rousette", taxid=9407, category=LifespanCategory.LONG_LIVED
    ),
    "indian_flying_fox": Species(
        name="indian_flying_fox", taxid=143292, category=LifespanCategory.LONG_LIVED
    ),
    "greater_horseshoe_bat": Species(
        name="greater_horseshoe_bat", taxid=59479, category=LifespanCategory.LONG_LIVED
    ),
    "davids_myotis": Species(
        name="davids_myotis", taxid=225400, category=LifespanCategory.LONG_LIVED
    ),
    "mouse_eared_bat": Species(
        name="mouse_eared_bat", taxid=51298, category=LifespanCategory.LONG_LIVED
    ),
    "big_brown_bat": Species(
        name="big_brown_bat", taxid=29078, category=LifespanCategory.LONG_LIVED
    ),
    # Reference: typical lifespan-for-size comparison group.
    "rhesus": Species(name="rhesus", taxid=9544, category=LifespanCategory.SHORT_LIVED),
    "sheep": Species(name="sheep", taxid=9940, category=LifespanCategory.SHORT_LIVED),
    "opossum": Species(name="opossum", taxid=13616, category=LifespanCategory.SHORT_LIVED),
    "dog": Species(name="dog", taxid=9615, category=LifespanCategory.SHORT_LIVED),
    "mouse_lemur": Species(name="mouse_lemur", taxid=30608, category=LifespanCategory.SHORT_LIVED),
    "ground_squirrel": Species(
        name="ground_squirrel", taxid=43179, category=LifespanCategory.SHORT_LIVED
    ),
    "tree_shrew": Species(name="tree_shrew", taxid=246437, category=LifespanCategory.SHORT_LIVED),
    "hedgehog": Species(name="hedgehog", taxid=9365, category=LifespanCategory.SHORT_LIVED),
    "cat": Species(name="cat", taxid=9685, category=LifespanCategory.SHORT_LIVED),
}

LONG_LIVED_SPECIES = [
    sp for sp in SPECIES_REGISTRY.values() if sp.category == LifespanCategory.LONG_LIVED
]
SHORT_LIVED_SPECIES = [
    sp for sp in SPECIES_REGISTRY.values() if sp.category == LifespanCategory.SHORT_LIVED
]
REFERENCE_SPECIES = SPECIES_REGISTRY["human"]

TARGET_SPECIES = LONG_LIVED_SPECIES + SHORT_LIVED_SPECIES

# --- Longevity-strategy groups for stratified (convergent-divergent) contrasts ---
# Test ELLSM-vs-Reference and BMAL-vs-Reference separately instead of pooling all long-lived
# species (which can cancel signal when the two strata use divergent molecular strategies).
# Only species that survive ortholog-coverage scoping are used at analysis time.
_BMAL_NAMES = [
    "elephant",  # Loxodonta africana (African bush elephant)
    "asiatic_elephant",
    "white_rhino",
    "sperm_whale",
    "killer_whale",
    "minke_whale",
    "blue_whale",
    "beluga",
    "bowhead_whale",
]
_ELLSM_NAMES = [
    "naked_mole_rat",
    "damaraland_mole_rat",
    "blind_mole_rat",
    "myotis_lucifugus",  # little brown bat
    "brandts_bat",
    "davids_myotis",
    "mouse_eared_bat",
    "big_brown_bat",
    "egyptian_rousette",
    "indian_flying_fox",
    "greater_horseshoe_bat",
]
_REFERENCE_NAMES = [
    "mouse",
    "rat",
    "hamster",
    "guinea_pig",
    "rhesus",
    "sheep",
    "opossum",
    "dog",
    "mouse_lemur",
    "ground_squirrel",
    "tree_shrew",
    "hedgehog",
    "cat",
]
BMAL_SPECIES = [sp for sp in SPECIES_REGISTRY.values() if sp.name in _BMAL_NAMES]
ELLSM_SPECIES = [sp for sp in SPECIES_REGISTRY.values() if sp.name in _ELLSM_NAMES]
REFERENCE_GROUP_SPECIES = [sp for sp in SPECIES_REGISTRY.values() if sp.name in _REFERENCE_NAMES]


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
    candidate_selection_mode: str = "partner_aware"
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
    negatome_control_pairs_path: Path = Path("data/interim/negatome_control_pairs.csv")

    def ensure_dirs(self) -> None:
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.interim_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "plots").mkdir(parents=True, exist_ok=True)
