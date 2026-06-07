from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"YAML config must contain a mapping at top level: {path}")

    return data


def load_candidate_sets(path: str | Path = "data/config/candidate_sets.yaml") -> dict[str, Any]:
    data = load_yaml(path)
    sets = data.get("sets", {})

    if not isinstance(sets, dict):
        raise ValueError("candidate_sets.yaml must contain a top-level 'sets' mapping")

    return sets


def build_species_to_group_map(
    path: str | Path = "data/config/species_groups.yaml",
) -> dict[str, str]:
    data = load_yaml(path)
    species_to_group: dict[str, str] = {}

    for top_level_group, entries in data.items():
        if not isinstance(entries, dict):
            continue

        for canonical_name, spec in entries.items():
            if not isinstance(spec, dict):
                continue

            group = spec.get("group", top_level_group)
            aliases = spec.get("aliases", [])
            all_names = [canonical_name, *aliases]

            for name in all_names:
                if name is None:
                    continue

                raw = str(name)
                species_to_group[raw] = str(group)
                species_to_group[raw.lower()] = str(group)
                species_to_group[raw.replace(" ", "_")] = str(group)
                species_to_group[raw.replace(" ", "_").lower()] = str(group)

    return species_to_group


def infer_species_group(species: str, species_to_group: dict[str, str]) -> str:
    if species in species_to_group:
        return species_to_group[species]

    low = species.lower()
    if low in species_to_group:
        return species_to_group[low]

    underscored = species.replace(" ", "_")
    if underscored in species_to_group:
        return species_to_group[underscored]

    low_underscored = underscored.lower()
    if low_underscored in species_to_group:
        return species_to_group[low_underscored]

    return "unknown"
