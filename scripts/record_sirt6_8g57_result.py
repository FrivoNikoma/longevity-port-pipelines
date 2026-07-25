"""Build and validate the committed five-species SIRT6 8g57 result package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections.abc import Iterable
from io import StringIO
from pathlib import Path

COMPLEX_ID = "8g57__A1_Q8N6T7--8g57__H1_P04908"
PDB_ID = "8g57"
SOURCE_UNIPROT = "P04908"
MODEL_NAME = "esmc-300m-2024-12"
RESULT_DATE = "2026-07-25"
EXPECTED_BRANCH = "record-sirt6-8g57-sequence-divergence-limited-result"
EXPECTED_TAXIDS = (10036, 10090, 10116, 10181, 59463)
EXPECTED_CATEGORIES = {
    10036: "short_lived_control",
    10090: "short_lived_control",
    10116: "short_lived_control",
    10181: "long_lived",
    59463: "long_lived",
}

RESULT_TABLE = Path("data/input/sirt6_8g57_five_species_mapped_interface_results.csv")
BASELINE_TABLE = Path("data/input/sirt6_8g57_sequence_divergence_baseline_results.csv")
DISPOSITION_TABLE = Path("data/input/sirt6_8g57_result_disposition.csv")
CONTRACT_PATH = Path("data/config/sirt6_8g57_result_contract.json")
DOC_PATH = Path("docs/sirt6_8g57_result.md")

RESULT_FIELDS = (
    "result_contract_version",
    "result_id",
    "candidate_set",
    "lane_name",
    "complex_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "target_species",
    "target_species_taxid",
    "target_accession",
    "lifespan_category",
    "model_name",
    "resolved_receptor_chain",
    "resolved_ligand_chain",
    "interface_residue_count",
    "interface_mean_delta",
    "noninterface_mean_delta",
    "enrichment_ratio",
    "shuffled_control_ratio",
    "p_interface_greater",
    "p_interface_less",
    "p_two_sided",
    "effect_size_cohens_d",
    "negatome_metric_included",
    "binding_affinity_claim",
    "beneficial_or_harmful_claim",
    "causal_longevity_claim",
    "result_date",
)

BASELINE_FIELDS = (
    "baseline_contract_version",
    "result_id",
    "complex_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "target_species",
    "target_species_taxid",
    "target_accession",
    "lifespan_category",
    "reference_sequence_length",
    "target_sequence_length",
    "full_reference_identity",
    "full_reference_disruption",
    "interface_residue_count",
    "interface_identity_all_positions",
    "interface_disruption",
    "interface_substitution_count",
    "interface_unmapped_count",
    "enrichment_ratio",
    "full_divergence_adjusted_residual",
    "interface_divergence_adjusted_residual",
    "phylogenetic_correction_performed",
    "result_date",
)

DISPOSITION_FIELDS = (
    "disposition_contract_version",
    "result_id",
    "complex_id",
    "pdb_id",
    "chain",
    "source_uniprot",
    "resolved_receptor_chain",
    "resolved_ligand_chain",
    "interface_residue_count",
    "species_count",
    "independent_long_lived_lineages",
    "short_lived_controls",
    "historical_metric_reproduced",
    "all_long_lived_above_all_controls",
    "minimum_long_lived_ratio",
    "maximum_short_lived_ratio",
    "minimum_long_minus_max_short",
    "raw_long_minus_short_mean_enrichment",
    "raw_exact_label_permutation_p",
    "full_divergence_separates_groups",
    "full_divergence_spearman_rho",
    "full_divergence_model_r_squared",
    "full_adjusted_long_minus_short",
    "full_adjusted_exact_p",
    "interface_divergence_separates_groups",
    "interface_divergence_spearman_rho",
    "interface_divergence_model_r_squared",
    "interface_adjusted_long_minus_short",
    "interface_adjusted_exact_p",
    "scientific_classification",
    "lane_disposition",
    "lane_status",
    "phylogenetic_correction_performed",
    "binding_affinity_claim",
    "beneficial_or_harmful_claim",
    "causal_longevity_claim",
    "allowed_next_action",
    "result_date",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--build-from-runtime-root", type=Path)
    mode.add_argument("--validate-runtime-root", type=Path)
    return parser.parse_args()


def _git_output(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _canonical_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def canonical_text_sha256(path: Path) -> str:
    return hashlib.sha256(_canonical_text(path).encode("utf-8")).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _csv_text(fields: tuple[str, ...], rows: Iterable[dict[str, str]]) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _write_csv(path: Path, fields: tuple[str, ...], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_csv_text(fields, rows), encoding="utf-8", newline="")


def _read_csv(path: Path, fields: tuple[str, ...] | None = None) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if fields is not None and tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"Unexpected columns in {path}")
        return list(reader)


def _bool_text(value: object) -> str:
    return "true" if bool(value) else "false"


def _finite_float(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if not math.isfinite(value):
        raise ValueError(f"{field} must be finite")
    return value


def _runtime_paths(runtime_root: Path) -> dict[str, Path]:
    analysis_root = runtime_root / "enrichment_analysis"
    compat_root = analysis_root / "mapped_metric_compatible"
    return {
        "runtime_selection": analysis_root / "sirt6_8g57_runtime_selection.csv",
        "runtime_coverage": compat_root / "sirt6_8g57_ligand_runtime_coverage.csv",
        "mapped_enrichment": compat_root / "sirt6_8g57_ligand_mapped_enrichment.parquet",
        "five_species_comparison": compat_root / "sirt6_8g57_ligand_five_species_comparison.csv",
        "mapped_verdict": compat_root / "sirt6_8g57_ligand_verdict.json",
        "sequence_baseline": compat_root / "sirt6_8g57_sequence_divergence_baseline.csv",
        "sequence_baseline_verdict": compat_root
        / "sirt6_8g57_sequence_divergence_baseline_verdict.json",
    }


def _source_hashes(paths: dict[str, Path]) -> dict[str, str]:
    for path in paths.values():
        if not path.exists():
            raise FileNotFoundError(path)
    return {
        "runtime_selection_canonical_text_sha256": canonical_text_sha256(
            paths["runtime_selection"]
        ),
        "runtime_coverage_canonical_text_sha256": canonical_text_sha256(paths["runtime_coverage"]),
        "mapped_enrichment_raw_sha256": raw_sha256(paths["mapped_enrichment"]),
        "five_species_comparison_canonical_text_sha256": canonical_text_sha256(
            paths["five_species_comparison"]
        ),
        "mapped_verdict_canonical_text_sha256": canonical_text_sha256(paths["mapped_verdict"]),
        "sequence_baseline_canonical_text_sha256": canonical_text_sha256(
            paths["sequence_baseline"]
        ),
        "sequence_baseline_verdict_canonical_text_sha256": canonical_text_sha256(
            paths["sequence_baseline_verdict"]
        ),
    }


def build_from_runtime(repo_root: Path, runtime_root: Path) -> None:
    branch = _git_output(repo_root, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise ValueError(f"Expected branch {EXPECTED_BRANCH}, got {branch}")

    paths = _runtime_paths(runtime_root)
    source_hashes = _source_hashes(paths)
    selection = _read_csv(paths["runtime_selection"])
    coverage = _read_csv(paths["runtime_coverage"])
    comparison = _read_csv(paths["five_species_comparison"])
    baseline = _read_csv(paths["sequence_baseline"])
    mapped_verdict = json.loads(paths["mapped_verdict"].read_text(encoding="utf-8"))
    baseline_verdict = json.loads(paths["sequence_baseline_verdict"].read_text(encoding="utf-8"))

    if len(selection) != 1 or selection[0].get("id") != COMPLEX_ID:
        raise ValueError("Unexpected runtime selection")
    if len(coverage) != 5 or len(comparison) != 5 or len(baseline) != 5:
        raise ValueError("Expected five coverage, comparison, and baseline rows")

    coverage_by_taxid = {int(row["target_species_taxid"]): row for row in coverage}
    comparison_by_taxid = {int(row["target_species_taxid"]): row for row in comparison}
    baseline_by_taxid = {int(row["target_species_taxid"]): row for row in baseline}
    for observed in (coverage_by_taxid, comparison_by_taxid, baseline_by_taxid):
        if tuple(sorted(observed)) != EXPECTED_TAXIDS:
            raise ValueError("Unexpected five-species panel")

    resolved_r = str(mapped_verdict["resolved_receptor_chain"])
    resolved_l = str(mapped_verdict["resolved_ligand_chain"])
    interface_count = int(mapped_verdict["ligand_interface_residue_count"])
    if (resolved_r, resolved_l, interface_count) != ("K", "G", 38):
        raise ValueError("Expected K/G and 38 mapped ligand residues")
    if mapped_verdict["scientific_classification"] != "provisional_candidate_longevity_contrast":
        raise ValueError("Unexpected mapped-result classification")
    if (
        baseline_verdict["scientific_classification"]
        != "sequence_divergence_confounding_not_resolved"
    ):
        raise ValueError("Unexpected final classification")

    result_rows: list[dict[str, str]] = []
    baseline_rows: list[dict[str, str]] = []
    for taxid in EXPECTED_TAXIDS:
        coverage_row = coverage_by_taxid[taxid]
        result = comparison_by_taxid[taxid]
        base = baseline_by_taxid[taxid]
        category = result["category"]
        if category != EXPECTED_CATEGORIES[taxid] or base["category"] != category:
            raise ValueError(f"Unexpected category for taxid {taxid}")
        if int(result["interface_residue_count"]) != 38:
            raise ValueError("Comparison did not use 38 residues")
        if int(base["interface_residue_count"]) != 38:
            raise ValueError("Baseline did not use 38 residues")
        accession = coverage_row["target_uniprot"]
        species = result["target_species"]

        result_rows.append(
            {
                "result_contract_version": "1",
                "result_id": f"sirt6_8g57_mapped_interface_{taxid}",
                "candidate_set": "sirt6_dna_repair",
                "lane_name": "sirt6_8g57_histone_h2a",
                "complex_id": COMPLEX_ID,
                "pdb_id": PDB_ID,
                "chain": "ligand",
                "source_uniprot": SOURCE_UNIPROT,
                "target_species": species,
                "target_species_taxid": str(taxid),
                "target_accession": accession,
                "lifespan_category": category,
                "model_name": MODEL_NAME,
                "resolved_receptor_chain": resolved_r,
                "resolved_ligand_chain": resolved_l,
                "interface_residue_count": result["interface_residue_count"],
                "interface_mean_delta": result["interface_mean_delta"],
                "noninterface_mean_delta": result["noninterface_mean_delta"],
                "enrichment_ratio": result["enrichment_ratio"],
                "shuffled_control_ratio": result["shuffled_control_ratio"],
                "p_interface_greater": result["p_interface_greater"],
                "p_interface_less": result["p_interface_less"],
                "p_two_sided": result["p_two_sided"],
                "effect_size_cohens_d": result["effect_size_cohens_d"],
                "negatome_metric_included": "false",
                "binding_affinity_claim": "false",
                "beneficial_or_harmful_claim": "false",
                "causal_longevity_claim": "false",
                "result_date": RESULT_DATE,
            }
        )
        baseline_rows.append(
            {
                "baseline_contract_version": "1",
                "result_id": f"sirt6_8g57_sequence_baseline_{taxid}",
                "complex_id": COMPLEX_ID,
                "pdb_id": PDB_ID,
                "chain": "ligand",
                "source_uniprot": SOURCE_UNIPROT,
                "target_species": species,
                "target_species_taxid": str(taxid),
                "target_accession": accession,
                "lifespan_category": category,
                "reference_sequence_length": base["reference_sequence_length"],
                "target_sequence_length": base["target_sequence_length"],
                "full_reference_identity": base["full_reference_identity"],
                "full_reference_disruption": base["full_reference_disruption"],
                "interface_residue_count": base["interface_residue_count"],
                "interface_identity_all_positions": base["interface_identity_all_positions"],
                "interface_disruption": base["interface_disruption"],
                "interface_substitution_count": base["interface_substitution_count"],
                "interface_unmapped_count": base["interface_unmapped_count"],
                "enrichment_ratio": base["enrichment_ratio"],
                "full_divergence_adjusted_residual": base["full_divergence_adjusted_residual"],
                "interface_divergence_adjusted_residual": base[
                    "interface_divergence_adjusted_residual"
                ],
                "phylogenetic_correction_performed": "false",
                "result_date": RESULT_DATE,
            }
        )

    disposition = {
        "disposition_contract_version": "1",
        "result_id": "sirt6_8g57_sequence_divergence_limited_disposition",
        "complex_id": COMPLEX_ID,
        "pdb_id": PDB_ID,
        "chain": "ligand",
        "source_uniprot": SOURCE_UNIPROT,
        "resolved_receptor_chain": resolved_r,
        "resolved_ligand_chain": resolved_l,
        "interface_residue_count": str(interface_count),
        "species_count": str(baseline_verdict["species_count"]),
        "independent_long_lived_lineages": str(baseline_verdict["independent_long_lived_lineages"]),
        "short_lived_controls": str(baseline_verdict["short_lived_controls"]),
        "historical_metric_reproduced": _bool_text(mapped_verdict["historical_species_reproduced"]),
        "all_long_lived_above_all_controls": _bool_text(
            mapped_verdict["all_long_lived_above_all_controls"]
        ),
        "minimum_long_lived_ratio": str(mapped_verdict["minimum_long_lived_ratio"]),
        "maximum_short_lived_ratio": str(mapped_verdict["maximum_short_lived_ratio"]),
        "minimum_long_minus_max_short": str(mapped_verdict["minimum_long_minus_max_short"]),
        "raw_long_minus_short_mean_enrichment": str(
            baseline_verdict["raw_long_minus_short_mean_enrichment"]
        ),
        "raw_exact_label_permutation_p": str(baseline_verdict["raw_exact_label_permutation_p"]),
        "full_divergence_separates_groups": _bool_text(
            baseline_verdict["full_divergence_separates_groups"]
        ),
        "full_divergence_spearman_rho": str(baseline_verdict["full_divergence_spearman_rho"]),
        "full_divergence_model_r_squared": str(baseline_verdict["full_divergence_model_r_squared"]),
        "full_adjusted_long_minus_short": str(baseline_verdict["full_adjusted_long_minus_short"]),
        "full_adjusted_exact_p": str(baseline_verdict["full_adjusted_exact_p"]),
        "interface_divergence_separates_groups": _bool_text(
            baseline_verdict["interface_divergence_separates_groups"]
        ),
        "interface_divergence_spearman_rho": str(
            baseline_verdict["interface_divergence_spearman_rho"]
        ),
        "interface_divergence_model_r_squared": str(
            baseline_verdict["interface_divergence_model_r_squared"]
        ),
        "interface_adjusted_long_minus_short": str(
            baseline_verdict["interface_adjusted_long_minus_short"]
        ),
        "interface_adjusted_exact_p": str(baseline_verdict["interface_adjusted_exact_p"]),
        "scientific_classification": str(baseline_verdict["scientific_classification"]),
        "lane_disposition": str(baseline_verdict["lane_disposition"]),
        "lane_status": "closed_pending_divergence_decoupling_species",
        "phylogenetic_correction_performed": _bool_text(
            baseline_verdict["phylogenetic_correction_performed"]
        ),
        "binding_affinity_claim": "false",
        "beneficial_or_harmful_claim": "false",
        "causal_longevity_claim": "false",
        "allowed_next_action": (
            "move_to_next_lane_and_reopen_only_with_divergence_decoupling_species"
        ),
        "result_date": RESULT_DATE,
    }

    result_path = repo_root / RESULT_TABLE
    baseline_path = repo_root / BASELINE_TABLE
    disposition_path = repo_root / DISPOSITION_TABLE
    _write_csv(result_path, RESULT_FIELDS, result_rows)
    _write_csv(baseline_path, BASELINE_FIELDS, baseline_rows)
    _write_csv(disposition_path, DISPOSITION_FIELDS, [disposition])

    contract = {
        "schema_version": 1,
        "schema_id": "sirt6_8g57_sequence_divergence_limited_result",
        "complex_id": COMPLEX_ID,
        "resolved_chain_pair": "K/G",
        "mapped_ligand_interface_residue_count": 38,
        "species_count": 5,
        "independent_long_lived_lineages": 2,
        "short_lived_controls": 3,
        "expected_taxids": list(EXPECTED_TAXIDS),
        "expected_accessions": {
            str(taxid): coverage_by_taxid[taxid]["target_uniprot"] for taxid in EXPECTED_TAXIDS
        },
        "tables": {
            "mapped_interface": {
                "path": RESULT_TABLE.as_posix(),
                "row_count": 5,
                "canonical_text_sha256": canonical_text_sha256(result_path),
            },
            "sequence_divergence_baseline": {
                "path": BASELINE_TABLE.as_posix(),
                "row_count": 5,
                "canonical_text_sha256": canonical_text_sha256(baseline_path),
            },
            "disposition": {
                "path": DISPOSITION_TABLE.as_posix(),
                "row_count": 1,
                "canonical_text_sha256": canonical_text_sha256(disposition_path),
            },
        },
        "runtime_source_hashes": source_hashes,
        "metric": {
            "family": "historical_sequence_mapped_interface_embedding_enrichment",
            "model": MODEL_NAME,
            "distance_cutoff_angstrom": 8.0,
            "shuffled_control": "same_size_mask_seed_42_1000_permutations",
        },
        "final_result": {
            "raw_ordering": "all_long_lived_above_all_short_lived_controls",
            "scientific_classification": "sequence_divergence_confounding_not_resolved",
            "lane_status": "closed_pending_divergence_decoupling_species",
            "allowed_next_action": (
                "move_to_next_lane_and_reopen_only_with_divergence_decoupling_species"
            ),
        },
        "claim_boundaries": {
            "phylogenetic_correction_performed": False,
            "binding_affinity_claim": False,
            "beneficial_or_harmful_claim": False,
            "causal_longevity_claim": False,
            "biological_mechanism_claim": False,
        },
        "runtime_artifacts_not_committed": [
            "per_residue_npy_embeddings",
            "external_fasta_or_sequence_files",
            "pdb_or_mmcif_cache",
            "parquet_runtime_output",
            "console_logs",
        ],
    }
    contract_path = repo_root / CONTRACT_PATH
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    (repo_root / DOC_PATH).write_text(
        _documentation(result_rows, disposition), encoding="utf-8", newline=""
    )
    validate_committed(repo_root)
    validate_runtime_sources(repo_root, runtime_root)

    print("mapped_result_rows=5")
    print("sequence_baseline_rows=5")
    print("disposition_rows=1")
    print("scientific_classification=sequence_divergence_confounding_not_resolved")
    print("SIRT6_COMMITTED_RESULT_PACKAGE_BUILT=True")


def _documentation(result_rows: list[dict[str, str]], disposition: dict[str, str]) -> str:
    substitution_counts = {10036: 0, 10090: 0, 10116: 0, 10181: 3, 59463: 6}
    lines = [
        "# SIRT6 8g57 five-species result",
        "",
        "## Result",
        "",
        "The historical sequence-mapped `8g57` histone-H2A interface analysis was",
        "reproduced exactly and extended from mouse to rat and hamster controls.",
        "The resolved structure chains are `K/G`, with 38 ligand interface residues",
        "at the 8 Å heavy-atom cutoff.",
        "",
        "| Group | Species | Taxid | Accession | Enrichment | Interface substitutions |",
        "|---|---|---:|---|---:|---:|",
    ]
    for row in sorted(result_rows, key=lambda item: float(item["enrichment_ratio"]), reverse=True):
        taxid = int(row["target_species_taxid"])
        lines.append(
            f"| {row['lifespan_category']} | {row['target_species']} | {taxid} | "
            f"`{row['target_accession']}` | {float(row['enrichment_ratio']):.6f} | "
            f"{substitution_counts[taxid]} |"
        )
    lines.extend(
        [
            "",
            "Both independent long-lived lineages are above all three short-lived",
            "controls. The minimum long-lived enrichment is",
            f"`{float(disposition['minimum_long_lived_ratio']):.12f}` and the maximum",
            f"short-lived enrichment is `{float(disposition['maximum_short_lived_ratio']):.12f}`.",
            "",
            "## Sequence-divergence limitation",
            "",
            "The long-lived species are also the only species in this panel with",
            "substitutions at the 38-residue H2A interface. Simple full-sequence and",
            "interface-divergence adjustments reduce the contrast and do not separate",
            "a longevity-associated effect from ordinary sequence divergence.",
            "",
            "The committed classification is",
            "`sequence_divergence_confounding_not_resolved`.",
            "This is not a phylogenetic correction.",
            "",
            "The lane is closed as `closed_pending_divergence_decoupling_species`.",
            "It should be reopened only when species break the present correlation",
            "between lifespan group and interface divergence.",
            "",
            "## Claim boundaries",
            "",
            "This result does not establish altered SIRT6-nucleosome binding affinity,",
            "beneficial or harmful function, a causal longevity mechanism, or readiness",
            "for structural-model promotion.",
            "",
            "## Validation",
            "",
            "```bash",
            "uv run python -m scripts.record_sirt6_8g57_result",
            "uv run python -m scripts.record_sirt6_8g57_result \\",
            "  --validate-runtime-root <path-to-sirt6_8g57_sequence_package>",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _load_contract(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Result contract must be a JSON object")
    return value


def validate_committed(
    repo_root: Path,
    *,
    contract_path: Path | None = None,
    result_path: Path | None = None,
    baseline_path: Path | None = None,
    disposition_path: Path | None = None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    contract_file = contract_path or repo_root / CONTRACT_PATH
    result_file = result_path or repo_root / RESULT_TABLE
    baseline_file = baseline_path or repo_root / BASELINE_TABLE
    disposition_file = disposition_path or repo_root / DISPOSITION_TABLE
    contract = _load_contract(contract_file)
    tables = contract.get("tables")
    if not isinstance(tables, dict):
        raise ValueError("Contract tables section is missing")
    table_specs = {
        "mapped_interface": (result_file, RESULT_FIELDS, 5),
        "sequence_divergence_baseline": (baseline_file, BASELINE_FIELDS, 5),
        "disposition": (disposition_file, DISPOSITION_FIELDS, 1),
    }
    loaded: dict[str, list[dict[str, str]]] = {}
    for name, (path, fields, expected_count) in table_specs.items():
        spec = tables.get(name)
        if not isinstance(spec, dict):
            raise ValueError(f"Missing contract table spec: {name}")
        expected_hash = spec.get("canonical_text_sha256")
        if canonical_text_sha256(path) != expected_hash:
            raise ValueError(f"Committed {name} hash mismatch")
        rows = _read_csv(path, fields)
        if len(rows) != expected_count:
            raise ValueError(f"Unexpected row count for {name}")
        loaded[name] = rows

    result_rows = loaded["mapped_interface"]
    baseline_rows = loaded["sequence_divergence_baseline"]
    disposition = loaded["disposition"][0]
    result_by_taxid = {int(row["target_species_taxid"]): row for row in result_rows}
    baseline_by_taxid = {int(row["target_species_taxid"]): row for row in baseline_rows}
    if tuple(sorted(result_by_taxid)) != EXPECTED_TAXIDS:
        raise ValueError("Unexpected mapped-interface taxids")
    if tuple(sorted(baseline_by_taxid)) != EXPECTED_TAXIDS:
        raise ValueError("Unexpected baseline taxids")

    accessions = contract.get("expected_accessions")
    if not isinstance(accessions, dict):
        raise ValueError("Expected accession map is missing")
    for taxid in EXPECTED_TAXIDS:
        result = result_by_taxid[taxid]
        baseline = baseline_by_taxid[taxid]
        expected_accession = accessions.get(str(taxid))
        if result["target_accession"] != expected_accession:
            raise ValueError(f"Unexpected accession for taxid {taxid}")
        if baseline["target_accession"] != expected_accession:
            raise ValueError(f"Unexpected baseline accession for taxid {taxid}")
        if result["lifespan_category"] != EXPECTED_CATEGORIES[taxid]:
            raise ValueError(f"Unexpected category for taxid {taxid}")
        if int(result["interface_residue_count"]) != 38:
            raise ValueError("Mapped result must use 38 interface residues")
        if int(baseline["interface_residue_count"]) != 38:
            raise ValueError("Baseline must use 38 interface residues")
        if baseline["phylogenetic_correction_performed"] != "false":
            raise ValueError("Baseline must not claim phylogenetic correction")
        for field in (
            "negatome_metric_included",
            "binding_affinity_claim",
            "beneficial_or_harmful_claim",
            "causal_longevity_claim",
        ):
            if result[field] != "false":
                raise ValueError(f"Prohibited positive claim: {field}")

    long_values = [
        _finite_float(row, "enrichment_ratio")
        for row in result_rows
        if row["lifespan_category"] == "long_lived"
    ]
    short_values = [
        _finite_float(row, "enrichment_ratio")
        for row in result_rows
        if row["lifespan_category"] == "short_lived_control"
    ]
    if len(long_values) != 2 or len(short_values) != 3:
        raise ValueError("Expected two long-lived lineages and three controls")
    if min(long_values) <= max(short_values):
        raise ValueError("Raw long-lived/control ordering is not preserved")

    expected_disposition = {
        "historical_metric_reproduced": "true",
        "all_long_lived_above_all_controls": "true",
        "full_divergence_separates_groups": "true",
        "interface_divergence_separates_groups": "true",
        "scientific_classification": "sequence_divergence_confounding_not_resolved",
        "lane_disposition": "freeze_sirt6_as_sequence_divergence_confounded",
        "lane_status": "closed_pending_divergence_decoupling_species",
        "phylogenetic_correction_performed": "false",
        "binding_affinity_claim": "false",
        "beneficial_or_harmful_claim": "false",
        "causal_longevity_claim": "false",
        "allowed_next_action": (
            "move_to_next_lane_and_reopen_only_with_divergence_decoupling_species"
        ),
    }
    for field, expected in expected_disposition.items():
        if disposition[field] != expected:
            raise ValueError(f"Unexpected disposition field {field}")
    return result_rows, baseline_rows, disposition


def validate_runtime_sources(repo_root: Path, runtime_root: Path) -> None:
    result_rows, baseline_rows, disposition = validate_committed(repo_root)
    contract = _load_contract(repo_root / CONTRACT_PATH)
    expected_hashes = contract.get("runtime_source_hashes")
    if not isinstance(expected_hashes, dict):
        raise ValueError("Runtime source hashes are missing")
    paths = _runtime_paths(runtime_root)
    observed_hashes = _source_hashes(paths)
    if observed_hashes != expected_hashes:
        raise ValueError("Runtime source hash mismatch")

    runtime_result = {
        int(row["target_species_taxid"]): row for row in _read_csv(paths["five_species_comparison"])
    }
    committed_result = {int(row["target_species_taxid"]): row for row in result_rows}
    for taxid in EXPECTED_TAXIDS:
        for field in (
            "interface_residue_count",
            "interface_mean_delta",
            "noninterface_mean_delta",
            "enrichment_ratio",
            "shuffled_control_ratio",
            "p_interface_greater",
            "p_interface_less",
            "p_two_sided",
            "effect_size_cohens_d",
        ):
            if runtime_result[taxid][field] != committed_result[taxid][field]:
                raise ValueError(f"Runtime result mismatch: taxid={taxid}, field={field}")

    runtime_baseline = {
        int(row["target_species_taxid"]): row for row in _read_csv(paths["sequence_baseline"])
    }
    committed_baseline = {int(row["target_species_taxid"]): row for row in baseline_rows}
    for taxid in EXPECTED_TAXIDS:
        for field in (
            "reference_sequence_length",
            "target_sequence_length",
            "full_reference_identity",
            "full_reference_disruption",
            "interface_residue_count",
            "interface_identity_all_positions",
            "interface_disruption",
            "interface_substitution_count",
            "interface_unmapped_count",
            "enrichment_ratio",
            "full_divergence_adjusted_residual",
            "interface_divergence_adjusted_residual",
        ):
            if runtime_baseline[taxid][field] != committed_baseline[taxid][field]:
                raise ValueError(f"Runtime baseline mismatch: taxid={taxid}, field={field}")

    baseline_verdict = json.loads(paths["sequence_baseline_verdict"].read_text(encoding="utf-8"))
    if baseline_verdict["scientific_classification"] != disposition["scientific_classification"]:
        raise ValueError("Runtime and committed classifications differ")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    if args.build_from_runtime_root is not None:
        build_from_runtime(repo_root, args.build_from_runtime_root.resolve())
        return
    result_rows, baseline_rows, disposition = validate_committed(repo_root)
    if args.validate_runtime_root is not None:
        validate_runtime_sources(repo_root, args.validate_runtime_root.resolve())
        print("runtime_sources_validated=true")
    print(f"mapped_result_rows={len(result_rows)}")
    print(f"sequence_baseline_rows={len(baseline_rows)}")
    print(f"scientific_classification={disposition['scientific_classification']}")
    print("SIRT6_COMMITTED_RESULT_VALID=True")


if __name__ == "__main__":
    main()
