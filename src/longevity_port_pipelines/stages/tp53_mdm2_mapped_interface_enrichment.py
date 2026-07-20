"""Run audited MDM2 mapped-interface enrichment from existing local artifacts.

This dry-run-first stage consumes exact external sequences, ignored saved ESMC
embeddings, and the committed 1YCR:A-to-Q00987 interface mapping. It performs
no network, Biohub, structural-model, or Gate 8 disposition action.
"""

from __future__ import annotations

import csv
import hashlib
import math
import os
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import numpy as np
import typer
from dotenv import load_dotenv

from longevity_port_pipelines.stages import (
    tp53_mdm2_mdm2_external_exact_sequence_binding_results as bindings,
)
from longevity_port_pipelines.stages.analyze import (
    align_and_compute_deltas,
    compute_deltas_from_alignment,
    compute_enrichment,
    mann_whitney_test,
    shuffled_control_distribution,
)
from longevity_port_pipelines.stages.embed import PerResidueEmbedding, embedding_path
from longevity_port_pipelines.stages.reference_coordinate_mapping import (
    ReferenceTargetAlignment,
    align_reference_to_target,
)
from longevity_port_pipelines.stages.tp53_mdm2_embedding_based_negatome_control_repair_result import (
    DEFAULT_MAPPING_TABLE,
    EXPECTED_MAPPING_SHA256,
    canonical_text_sha256,
    validate_mapping_table,
)

MODEL_NAME = "esmc-300m-2024-12"
COMPLEX_ID = "tp53_mdm2_elephant_seed_mdm2_chain"
CHAIN = "mdm2"
REFERENCE_ACCESSION = "Q00987"
REFERENCE_TAXID = 9606
REFERENCE_SEQUENCE_ROOT_ENV = "MDM2_REFERENCE_SEQUENCE_ROOT"
SHUFFLE_SEED = 42
SHUFFLE_CONTROL_COUNT = 1000
RESULT_DATE = "2026-07-19"

DEFAULT_RESULT_TABLE = Path("data/input/tp53_mdm2_mdm2_mapped_interface_enrichment_results.csv")

METRIC_FAMILY = (
    "human_reference_to_ortholog_per_residue_esmc_l2_mapped_interface_vs_noninterface_enrichment"
)
ALIGNMENT_POLICY = (
    "biotite_global_blosum62_gap_open_-10_gap_extend_-1_terminal_penalty_false_first_optimal"
)
SHUFFLE_POLICY = (
    "uniform_without_replacement_same_mapped_interface_count_among_aligned_residue_pairs"
)
MAPPING_SOURCE = (
    "RCSB_PDB_1YCR_DBREF_Q00987_17_125|official_RCSB_coordinates|official_UniProt_Q00987_sequence"
)


@dataclass(frozen=True)
class SequenceContract:
    accession: str
    taxid: int
    filename: str
    length: int
    sequence_sha256: str
    raw_fasta_sha256: str
    root_env: str


@dataclass(frozen=True)
class TargetContract(SequenceContract):
    species: str
    species_name: str
    lifespan_category: str
    embedding_sha256: str


@dataclass(frozen=True)
class SequenceObservation:
    sequence: str
    raw_fasta_sha256: str
    relative_path: str
    root_env: str


@dataclass(frozen=True)
class EmbeddingObservation:
    embedding: PerResidueEmbedding
    relative_path: str
    shape: str
    dtype: str
    sha256: str


@dataclass(frozen=True)
class PreparedTarget:
    contract: TargetContract
    sequence: SequenceObservation
    embedding: EmbeddingObservation
    alignment: ReferenceTargetAlignment
    mapped_interface_target_indices: tuple[int, ...]
    dropped_reference_interface_indices: tuple[int, ...]
    mapped_interface_identity_count: int


@dataclass(frozen=True)
class PreparedPanel:
    reference_sequence: SequenceObservation
    reference_embedding: EmbeddingObservation
    interface_reference_indices: tuple[int, ...]
    interface_mapping_source: str
    targets: tuple[PreparedTarget, ...]


@dataclass(frozen=True)
class MappedInterfaceMetrics:
    aligned_residue_count: int
    mapped_interface_count: int
    noninterface_count: int
    interface_mean_delta: float
    noninterface_mean_delta: float
    enrichment_ratio: float
    p_interface_greater: float
    p_interface_less: float
    p_two_sided: float
    effect_size_cohens_d: float
    shuffle_ratios: np.ndarray
    shuffle_ge_observed_count: int
    shuffle_le_observed_count: int
    shuffle_empirical_p_greater: float
    shuffle_empirical_p_less: float
    shuffle_empirical_p_two_sided: float


REFERENCE_CONTRACT = SequenceContract(
    accession=REFERENCE_ACCESSION,
    taxid=REFERENCE_TAXID,
    filename="Q00987.fasta",
    length=491,
    sequence_sha256=("77ed25650e717b3f610e42ef8e5c1c88d50e7485725032f8535448a0ca8b61b1"),
    raw_fasta_sha256=("75573e90db2ef66e0acb952bd29883e8f04c98d5828405fc4fe8368420fd0496"),
    root_env=REFERENCE_SEQUENCE_ROOT_ENV,
)

REFERENCE_EMBEDDING_SHA256 = "ee0b8d9025dd6b5a18ecf5f1a344b8ab819f559f652d92f32ea23a006a0d8eeb"

TARGETS = (
    TargetContract(
        accession="G3SX30",
        taxid=9785,
        filename="G3SX30.fasta",
        length=492,
        sequence_sha256=("e288c6985ffcebe527716261c213e00a44f5f9acf0280eaa433154f6e19eab4f"),
        raw_fasta_sha256=("8fb14bb9d41ff6ca18065c026b576d2e962a4affe4a08a9442717a405c279c6c"),
        root_env=REFERENCE_SEQUENCE_ROOT_ENV,
        species="elephant",
        species_name="Loxodonta africana",
        lifespan_category="long_lived",
        embedding_sha256=("98ec10a07986e07c65a11f370f542e5b6c88453c544f9f0f49fb2fe0f8e6315c"),
    ),
    TargetContract(
        accession="P23804",
        taxid=10090,
        filename="P23804.fasta",
        length=489,
        sequence_sha256=("0841e7c8ebd6a4a9e9e051538600d8f201c6682b3246dfb95ba301ab6233a3e3"),
        raw_fasta_sha256=("ad1c51d55e9b5ae87ca2bed24cc5aeb529e475edfa9ea08cc08ff805bdbcc74d"),
        root_env=bindings.BINDING_ROOT_ENV,
        species="mouse",
        species_name="Mus musculus",
        lifespan_category="short_lived",
        embedding_sha256=("23c92fc3ceeb9b9141d502c0b3a0c47f9aa442f5fd9659030dc88502eee6c88e"),
    ),
    TargetContract(
        accession="A0ABM2YB85",
        taxid=10036,
        filename="A0ABM2YB85.fasta",
        length=510,
        sequence_sha256=("77125856d7835e2b31886052c94d818752c49b9eb7bb86dea1f8d5f313159fe5"),
        raw_fasta_sha256=("af21e7b2c9b9945bce482b3613a71ae9ebc9d58d9c58c6b0b13ea574b015faad"),
        root_env=bindings.BINDING_ROOT_ENV,
        species="hamster",
        species_name="Mesocricetus auratus",
        lifespan_category="short_lived",
        embedding_sha256=("36387d8ca76f764542225832f5146e524d615ec9c1fcc16c0523fe9c20b6de5a"),
    ),
)

RESULT_FIELDS = (
    "result_contract_version",
    "result_id",
    "candidate_set",
    "lane_name",
    "candidate_id",
    "gene_symbol",
    "target_species",
    "target_species_name",
    "target_taxid",
    "target_accession",
    "lifespan_category",
    "reference_accession",
    "reference_taxid",
    "reference_sequence_root_env",
    "reference_sequence_relative_path",
    "reference_sequence_length",
    "reference_sequence_sha256",
    "reference_raw_fasta_sha256",
    "target_sequence_root_env",
    "target_sequence_relative_path",
    "target_sequence_length",
    "target_sequence_sha256",
    "target_raw_fasta_sha256",
    "model_name",
    "reference_embedding_path",
    "reference_embedding_shape",
    "reference_embedding_dtype",
    "reference_embedding_sha256",
    "target_embedding_path",
    "target_embedding_shape",
    "target_embedding_dtype",
    "target_embedding_sha256",
    "mapping_table",
    "mapping_table_sha256",
    "mapping_source",
    "source_interface_coordinate_system",
    "target_interface_coordinate_system",
    "source_interface_residue_count",
    "source_interface_reference_identity_count",
    "alignment_policy",
    "biotite_version",
    "alignment_trace_length",
    "alignment_optimal_count",
    "aligned_residue_count",
    "mapped_interface_count",
    "mapped_interface_identity_count",
    "mapped_interface_target_zero_based_indices",
    "dropped_interface_count",
    "dropped_reference_zero_based_indices",
    "mapping_status",
    "metric_family",
    "residue_delta_metric",
    "primary_interface_count",
    "primary_noninterface_count",
    "interface_mean_delta",
    "noninterface_mean_delta",
    "enrichment_ratio",
    "p_interface_greater",
    "p_interface_less",
    "p_two_sided",
    "effect_size_cohens_d",
    "shuffle_metric_family",
    "shuffle_mask_policy",
    "shuffle_rng",
    "shuffle_seed",
    "shuffle_control_count",
    "shuffle_valid_control_count",
    "shuffle_ratio_mean",
    "shuffle_ratio_median",
    "shuffle_ratio_std",
    "shuffle_ratio_min",
    "shuffle_ratio_q025",
    "shuffle_ratio_q975",
    "shuffle_ratio_max",
    "shuffle_ge_observed_count",
    "shuffle_le_observed_count",
    "shuffle_empirical_p_greater",
    "shuffle_empirical_p_less",
    "shuffle_empirical_p_two_sided",
    "legacy_geometric_shuffled_result_reused",
    "negatome_metric_included",
    "negatome_metric_compatibility_status",
    "mapped_interface_enrichment_run",
    "gate8_contrast_run",
    "mapping_cutoff_alignment_sensitivity_run",
    "leave_one_control_out_run",
    "residue_block_jackknife_run",
    "single_long_lived_lineage_limitation",
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biohub_called",
    "esmc_called",
    "new_embedding_generated",
    "npy_artifact_written",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
    "gate8_input_status",
    "allowed_next_action",
    "claim_status",
    "result_date",
)

FALSE_BOUNDARY_FIELDS = (
    "legacy_geometric_shuffled_result_reused",
    "negatome_metric_included",
    "gate8_contrast_run",
    "mapping_cutoff_alignment_sensitivity_run",
    "leave_one_control_out_run",
    "residue_block_jackknife_run",
    "gate8_disposition_run",
    "gate8_promoted",
    "gate9_promoted",
    "biohub_called",
    "esmc_called",
    "new_embedding_generated",
    "npy_artifact_written",
    "npy_artifact_committed",
    "data_output_artifact_committed",
    "boltz_called",
    "af3_called",
    "chai_called",
    "biological_claim_made",
)

app = typer.Typer(add_completion=False)


def sha256_file(path: Path) -> str:
    """Return a streaming lowercase SHA-256 for one file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _float_text(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError(f"Expected a finite result value, got {value}")
    return format(value, ".17g")


def _indices_text(indices: tuple[int, ...]) -> str:
    return "|".join(str(index) for index in indices) if indices else "none"


def _shape_text(shape: tuple[int, ...]) -> str:
    return "x".join(str(value) for value in shape)


def load_sequence_observation(
    root: Path,
    contract: SequenceContract,
) -> SequenceObservation:
    """Load and bind one exact external FASTA to its accession contract."""
    path = root / contract.filename
    raw = path.read_bytes()
    header, sequence = bindings.parse_single_fasta(raw)

    expected_header_prefixes = (f"sp|{contract.accession}|", f"tr|{contract.accession}|")
    if not header.startswith(expected_header_prefixes):
        raise ValueError(f"{contract.accession}: FASTA accession mismatch")
    if f"OX={contract.taxid}" not in header:
        raise ValueError(f"{contract.accession}: FASTA taxid mismatch")
    if len(sequence) != contract.length:
        raise ValueError(f"{contract.accession}: sequence length mismatch")
    sequence_hash = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    if sequence_hash != contract.sequence_sha256:
        raise ValueError(f"{contract.accession}: normalized sequence SHA-256 mismatch")
    raw_hash = hashlib.sha256(raw).hexdigest()
    if raw_hash != contract.raw_fasta_sha256:
        raise ValueError(f"{contract.accession}: raw FASTA SHA-256 mismatch")

    return SequenceObservation(
        sequence=sequence,
        raw_fasta_sha256=raw_hash,
        relative_path=contract.filename,
        root_env=contract.root_env,
    )


def load_embedding_observation(
    *,
    repo_root: Path,
    accession: str,
    taxid: int,
    sequence: str,
    expected_sha256: str,
) -> EmbeddingObservation:
    """Load one exact ignored embedding and fail closed on any invariant drift."""
    relative_path = embedding_path(
        output_dir=Path("data/output"),
        model_name=MODEL_NAME,
        complex_id=COMPLEX_ID,
        chain=CHAIN,
        species_taxid=taxid,
    )
    path = repo_root / relative_path
    array = np.asarray(np.load(path, allow_pickle=False))
    if array.ndim != 2:
        raise ValueError(f"{accession}: embedding must be two-dimensional")
    if array.shape != (len(sequence), 960):
        raise ValueError(
            f"{accession}: expected embedding shape {(len(sequence), 960)}, got {array.shape}"
        )
    if array.dtype != np.dtype(np.float32):
        raise ValueError(f"{accession}: expected float32 embedding, got {array.dtype}")
    if not np.issubdtype(array.dtype, np.number) or not np.isfinite(array).all():
        raise ValueError(f"{accession}: embedding is non-numeric or non-finite")
    observed_hash = sha256_file(path)
    if observed_hash != expected_sha256:
        raise ValueError(f"{accession}: embedding SHA-256 mismatch")

    return EmbeddingObservation(
        embedding=PerResidueEmbedding(
            complex_id=COMPLEX_ID,
            chain=CHAIN,
            species_taxid=taxid,
            model_name=MODEL_NAME,
            sequence=sequence,
            embeddings=array,
            is_predicted_structure=False,
        ),
        relative_path=relative_path.as_posix(),
        shape=_shape_text(array.shape),
        dtype=str(array.dtype),
        sha256=observed_hash,
    )


def _validate_external_control_bindings(
    repo_root: Path,
    binding_root: Path,
) -> None:
    source_path = repo_root / bindings.DEFAULT_SOURCE_PROVENANCE_TABLE
    result_path = repo_root / bindings.DEFAULT_RESULT_TABLE
    manifest_path = binding_root / bindings.EXTERNAL_MANIFEST_RELATIVE_PATH
    source_rows = bindings.read_csv_rows(source_path)
    rebuilt_rows = bindings.build_rows_from_external(
        source_rows=source_rows,
        binding_root=binding_root,
        manifest_path=manifest_path,
    )
    committed_rows = bindings.load_and_validate_result(
        result_path=result_path,
        source_path=source_path,
    )
    if rebuilt_rows != committed_rows:
        raise ValueError("External mouse/hamster sequence bindings changed")


def prepare_panel(
    *,
    repo_root: Path,
    reference_sequence_root: Path,
    binding_root: Path,
) -> PreparedPanel:
    """Validate every A1 input and prepare audited target coordinate maps."""
    _validate_external_control_bindings(repo_root, binding_root)

    reference_sequence = load_sequence_observation(
        reference_sequence_root,
        REFERENCE_CONTRACT,
    )
    reference_embedding = load_embedding_observation(
        repo_root=repo_root,
        accession=REFERENCE_ACCESSION,
        taxid=REFERENCE_TAXID,
        sequence=reference_sequence.sequence,
        expected_sha256=REFERENCE_EMBEDDING_SHA256,
    )

    mapping_rows = validate_mapping_table(repo_root)
    interface_indices = tuple(int(row["full_length_zero_based_index"]) for row in mapping_rows)
    for row, reference_index in zip(mapping_rows, interface_indices, strict=True):
        if reference_sequence.sequence[reference_index] != row["residue_one_letter"]:
            raise ValueError(
                "Committed 1YCR/Q00987 residue identity differs from exact Q00987 FASTA"
            )
    mapping_sources = {row["mapping_source"] for row in mapping_rows}
    if len(mapping_sources) != 1:
        raise ValueError("Expected one 1YCR/Q00987 mapping source")

    prepared_targets: list[PreparedTarget] = []
    for contract in TARGETS:
        sequence_root = (
            reference_sequence_root
            if contract.root_env == REFERENCE_SEQUENCE_ROOT_ENV
            else binding_root
        )
        sequence = load_sequence_observation(sequence_root, contract)
        if contract.root_env == bindings.BINDING_ROOT_ENV:
            normalized_path = sequence_root / f"{contract.accession}.sequence.txt"
            if normalized_path.read_text(encoding="ascii") != sequence.sequence:
                raise ValueError(
                    f"{contract.accession}: normalized sequence differs from validated FASTA"
                )

        embedding = load_embedding_observation(
            repo_root=repo_root,
            accession=contract.accession,
            taxid=contract.taxid,
            sequence=sequence.sequence,
            expected_sha256=contract.embedding_sha256,
        )
        alignment = align_reference_to_target(
            reference_sequence.sequence,
            sequence.sequence,
        )
        by_reference = {pair.reference_index: pair for pair in alignment.aligned_pairs}
        mapped_pairs = [by_reference[index] for index in interface_indices if index in by_reference]
        dropped = tuple(index for index in interface_indices if index not in by_reference)
        mapped_target_indices = tuple(pair.target_index for pair in mapped_pairs)
        if len(set(mapped_target_indices)) != len(mapped_target_indices):
            raise ValueError(f"{contract.accession}: mapped target indices are not unique")
        if not all(0 <= index < contract.length for index in mapped_target_indices):
            raise ValueError(f"{contract.accession}: mapped target index is out of bounds")
        if len(mapped_target_indices) < 2:
            raise ValueError(f"{contract.accession}: too few mapped interface residues")
        if len(alignment.aligned_pairs) <= len(mapped_target_indices):
            raise ValueError(f"{contract.accession}: mapped interface leaves no background")

        prepared_targets.append(
            PreparedTarget(
                contract=contract,
                sequence=sequence,
                embedding=embedding,
                alignment=alignment,
                mapped_interface_target_indices=mapped_target_indices,
                dropped_reference_interface_indices=dropped,
                mapped_interface_identity_count=sum(
                    pair.residue_identity_consistent for pair in mapped_pairs
                ),
            )
        )

    return PreparedPanel(
        reference_sequence=reference_sequence,
        reference_embedding=reference_embedding,
        interface_reference_indices=interface_indices,
        interface_mapping_source=next(iter(mapping_sources)),
        targets=tuple(prepared_targets),
    )


def compute_mapped_interface_metrics(
    *,
    reference: PerResidueEmbedding,
    target: PerResidueEmbedding,
    interface_reference_indices: tuple[int, ...],
    alignment: ReferenceTargetAlignment | None = None,
    shuffle_seed: int = SHUFFLE_SEED,
    shuffle_control_count: int = SHUFFLE_CONTROL_COUNT,
) -> MappedInterfaceMetrics:
    """Compute primary and shuffled metrics in one residue-level family."""
    if alignment is None:
        deltas, aligned_positions = align_and_compute_deltas(reference, target)
    else:
        deltas, aligned_positions = compute_deltas_from_alignment(
            reference,
            target,
            alignment,
        )
    if deltas.size == 0 or not np.isfinite(deltas).all():
        raise ValueError("Aligned per-residue deltas are empty or non-finite")

    aligned_set = {int(position) for position in aligned_positions}
    mapped_interface = tuple(index for index in interface_reference_indices if index in aligned_set)
    interface_mean, noninterface_mean, enrichment = compute_enrichment(
        deltas,
        aligned_positions,
        list(mapped_interface),
    )
    p_greater, p_less, p_two_sided, cohens_d = mann_whitney_test(
        deltas,
        aligned_positions,
        list(mapped_interface),
    )
    shuffle_ratios = shuffled_control_distribution(
        deltas,
        n_interface=len(mapped_interface),
        n_permutations=shuffle_control_count,
        seed=shuffle_seed,
    )
    ge_count = int(np.count_nonzero(shuffle_ratios >= enrichment))
    le_count = int(np.count_nonzero(shuffle_ratios <= enrichment))
    p_shuffle_greater = (ge_count + 1) / (shuffle_control_count + 1)
    p_shuffle_less = (le_count + 1) / (shuffle_control_count + 1)
    p_shuffle_two = min(1.0, 2.0 * min(p_shuffle_greater, p_shuffle_less))

    return MappedInterfaceMetrics(
        aligned_residue_count=len(deltas),
        mapped_interface_count=len(mapped_interface),
        noninterface_count=len(deltas) - len(mapped_interface),
        interface_mean_delta=interface_mean,
        noninterface_mean_delta=noninterface_mean,
        enrichment_ratio=enrichment,
        p_interface_greater=p_greater,
        p_interface_less=p_less,
        p_two_sided=p_two_sided,
        effect_size_cohens_d=cohens_d,
        shuffle_ratios=shuffle_ratios,
        shuffle_ge_observed_count=ge_count,
        shuffle_le_observed_count=le_count,
        shuffle_empirical_p_greater=p_shuffle_greater,
        shuffle_empirical_p_less=p_shuffle_less,
        shuffle_empirical_p_two_sided=p_shuffle_two,
    )


def build_result_rows(panel: PreparedPanel) -> list[dict[str, str]]:
    """Compute and serialize the three canonical A1 result rows."""
    rows: list[dict[str, str]] = []
    for prepared in panel.targets:
        contract = prepared.contract
        metrics = compute_mapped_interface_metrics(
            reference=panel.reference_embedding.embedding,
            target=prepared.embedding.embedding,
            interface_reference_indices=panel.interface_reference_indices,
        )
        if metrics.aligned_residue_count != len(prepared.alignment.aligned_pairs):
            raise ValueError(f"{contract.accession}: audit alignment and metric alignment differ")
        if metrics.mapped_interface_count != len(prepared.mapped_interface_target_indices):
            raise ValueError(f"{contract.accession}: audit mapping and primary mask counts differ")
        dropped = prepared.dropped_reference_interface_indices
        mapping_status = (
            "complete_all_source_interface_residues_aligned"
            if not dropped
            else "partial_source_interface_mapping_with_recorded_drops"
        )
        ratios = metrics.shuffle_ratios
        row = {
            "result_contract_version": "1",
            "result_id": f"mdm2_mapped_interface_enrichment_{contract.accession.lower()}",
            "candidate_set": "tp53_mdm2_elephant",
            "lane_name": "tp53_mdm2_elephant_mdm2_scoped",
            "candidate_id": COMPLEX_ID,
            "gene_symbol": "MDM2",
            "target_species": contract.species,
            "target_species_name": contract.species_name,
            "target_taxid": str(contract.taxid),
            "target_accession": contract.accession,
            "lifespan_category": contract.lifespan_category,
            "reference_accession": REFERENCE_ACCESSION,
            "reference_taxid": str(REFERENCE_TAXID),
            "reference_sequence_root_env": REFERENCE_SEQUENCE_ROOT_ENV,
            "reference_sequence_relative_path": panel.reference_sequence.relative_path,
            "reference_sequence_length": str(len(panel.reference_sequence.sequence)),
            "reference_sequence_sha256": REFERENCE_CONTRACT.sequence_sha256,
            "reference_raw_fasta_sha256": panel.reference_sequence.raw_fasta_sha256,
            "target_sequence_root_env": prepared.sequence.root_env,
            "target_sequence_relative_path": prepared.sequence.relative_path,
            "target_sequence_length": str(len(prepared.sequence.sequence)),
            "target_sequence_sha256": contract.sequence_sha256,
            "target_raw_fasta_sha256": prepared.sequence.raw_fasta_sha256,
            "model_name": MODEL_NAME,
            "reference_embedding_path": panel.reference_embedding.relative_path,
            "reference_embedding_shape": panel.reference_embedding.shape,
            "reference_embedding_dtype": panel.reference_embedding.dtype,
            "reference_embedding_sha256": panel.reference_embedding.sha256,
            "target_embedding_path": prepared.embedding.relative_path,
            "target_embedding_shape": prepared.embedding.shape,
            "target_embedding_dtype": prepared.embedding.dtype,
            "target_embedding_sha256": prepared.embedding.sha256,
            "mapping_table": DEFAULT_MAPPING_TABLE.as_posix(),
            "mapping_table_sha256": EXPECTED_MAPPING_SHA256,
            "mapping_source": panel.interface_mapping_source,
            "source_interface_coordinate_system": "Q00987_full_length_zero_based",
            "target_interface_coordinate_system": "target_full_length_zero_based",
            "source_interface_residue_count": str(len(panel.interface_reference_indices)),
            "source_interface_reference_identity_count": str(
                len(panel.interface_reference_indices)
            ),
            "alignment_policy": ALIGNMENT_POLICY,
            "biotite_version": version("biotite"),
            "alignment_trace_length": str(prepared.alignment.trace_length),
            "alignment_optimal_count": str(prepared.alignment.optimal_alignment_count),
            "aligned_residue_count": str(metrics.aligned_residue_count),
            "mapped_interface_count": str(metrics.mapped_interface_count),
            "mapped_interface_identity_count": str(prepared.mapped_interface_identity_count),
            "mapped_interface_target_zero_based_indices": _indices_text(
                prepared.mapped_interface_target_indices
            ),
            "dropped_interface_count": str(len(dropped)),
            "dropped_reference_zero_based_indices": _indices_text(dropped),
            "mapping_status": mapping_status,
            "metric_family": METRIC_FAMILY,
            "residue_delta_metric": "euclidean_l2_between_aligned_esmc_residue_vectors",
            "primary_interface_count": str(metrics.mapped_interface_count),
            "primary_noninterface_count": str(metrics.noninterface_count),
            "interface_mean_delta": _float_text(metrics.interface_mean_delta),
            "noninterface_mean_delta": _float_text(metrics.noninterface_mean_delta),
            "enrichment_ratio": _float_text(metrics.enrichment_ratio),
            "p_interface_greater": _float_text(metrics.p_interface_greater),
            "p_interface_less": _float_text(metrics.p_interface_less),
            "p_two_sided": _float_text(metrics.p_two_sided),
            "effect_size_cohens_d": _float_text(metrics.effect_size_cohens_d),
            "shuffle_metric_family": METRIC_FAMILY,
            "shuffle_mask_policy": SHUFFLE_POLICY,
            "shuffle_rng": "numpy_default_rng_pcg64",
            "shuffle_seed": str(SHUFFLE_SEED),
            "shuffle_control_count": str(SHUFFLE_CONTROL_COUNT),
            "shuffle_valid_control_count": str(len(ratios)),
            "shuffle_ratio_mean": _float_text(float(np.mean(ratios))),
            "shuffle_ratio_median": _float_text(float(np.median(ratios))),
            "shuffle_ratio_std": _float_text(float(np.std(ratios))),
            "shuffle_ratio_min": _float_text(float(np.min(ratios))),
            "shuffle_ratio_q025": _float_text(float(np.quantile(ratios, 0.025))),
            "shuffle_ratio_q975": _float_text(float(np.quantile(ratios, 0.975))),
            "shuffle_ratio_max": _float_text(float(np.max(ratios))),
            "shuffle_ge_observed_count": str(metrics.shuffle_ge_observed_count),
            "shuffle_le_observed_count": str(metrics.shuffle_le_observed_count),
            "shuffle_empirical_p_greater": _float_text(metrics.shuffle_empirical_p_greater),
            "shuffle_empirical_p_less": _float_text(metrics.shuffle_empirical_p_less),
            "shuffle_empirical_p_two_sided": _float_text(metrics.shuffle_empirical_p_two_sided),
            "legacy_geometric_shuffled_result_reused": "false",
            "negatome_metric_included": "false",
            "negatome_metric_compatibility_status": (
                "not_applied_pending_separate_metric_compatibility_audit"
            ),
            "mapped_interface_enrichment_run": "true",
            "gate8_contrast_run": "false",
            "mapping_cutoff_alignment_sensitivity_run": "false",
            "leave_one_control_out_run": "false",
            "residue_block_jackknife_run": "false",
            "single_long_lived_lineage_limitation": "true",
            "gate8_disposition_run": "false",
            "gate8_promoted": "false",
            "gate9_promoted": "false",
            "biohub_called": "false",
            "esmc_called": "false",
            "new_embedding_generated": "false",
            "npy_artifact_written": "false",
            "npy_artifact_committed": "false",
            "data_output_artifact_committed": "false",
            "boltz_called": "false",
            "af3_called": "false",
            "chai_called": "false",
            "biological_claim_made": "false",
            "gate8_input_status": "created_pending_a2_a3_and_gate8_disposition",
            "allowed_next_action": "run_mapping_cutoff_and_alignment_sensitivity",
            "claim_status": ("technical_mapped_interface_enrichment_result_no_gate8_disposition"),
            "result_date": RESULT_DATE,
        }
        rows.append(row)

    validate_result_rows(rows)
    return rows


def _require(row: dict[str, str], field: str, expected: str) -> None:
    actual = row.get(field, "")
    if actual != expected:
        raise ValueError(f"Expected {field}={expected!r}, got {actual!r}")


def validate_result_rows(rows: list[dict[str, str]]) -> None:
    """Validate committed-compatible A1 rows without ignored runtime artifacts."""
    if [row.get("target_accession") for row in rows] != [target.accession for target in TARGETS]:
        raise ValueError("Expected elephant, mouse, hamster result order")

    finite_fields = (
        "interface_mean_delta",
        "noninterface_mean_delta",
        "enrichment_ratio",
        "p_interface_greater",
        "p_interface_less",
        "p_two_sided",
        "effect_size_cohens_d",
        "shuffle_ratio_mean",
        "shuffle_ratio_median",
        "shuffle_ratio_std",
        "shuffle_ratio_min",
        "shuffle_ratio_q025",
        "shuffle_ratio_q975",
        "shuffle_ratio_max",
        "shuffle_empirical_p_greater",
        "shuffle_empirical_p_less",
        "shuffle_empirical_p_two_sided",
    )
    probability_fields = (
        "p_interface_greater",
        "p_interface_less",
        "p_two_sided",
        "shuffle_empirical_p_greater",
        "shuffle_empirical_p_less",
        "shuffle_empirical_p_two_sided",
    )

    for row, contract in zip(rows, TARGETS, strict=True):
        if tuple(row) != RESULT_FIELDS:
            raise ValueError("Result fields or field order changed")
        static = {
            "result_contract_version": "1",
            "candidate_id": COMPLEX_ID,
            "gene_symbol": "MDM2",
            "target_species": contract.species,
            "target_taxid": str(contract.taxid),
            "target_accession": contract.accession,
            "lifespan_category": contract.lifespan_category,
            "reference_accession": REFERENCE_ACCESSION,
            "reference_taxid": str(REFERENCE_TAXID),
            "reference_sequence_root_env": REFERENCE_SEQUENCE_ROOT_ENV,
            "reference_sequence_relative_path": REFERENCE_CONTRACT.filename,
            "reference_sequence_length": str(REFERENCE_CONTRACT.length),
            "reference_sequence_sha256": REFERENCE_CONTRACT.sequence_sha256,
            "reference_raw_fasta_sha256": REFERENCE_CONTRACT.raw_fasta_sha256,
            "target_sequence_root_env": contract.root_env,
            "target_sequence_relative_path": contract.filename,
            "target_sequence_length": str(contract.length),
            "target_sequence_sha256": contract.sequence_sha256,
            "target_raw_fasta_sha256": contract.raw_fasta_sha256,
            "model_name": MODEL_NAME,
            "reference_embedding_shape": "491x960",
            "reference_embedding_dtype": "float32",
            "reference_embedding_sha256": REFERENCE_EMBEDDING_SHA256,
            "reference_embedding_path": embedding_path(
                output_dir=Path("data/output"),
                model_name=MODEL_NAME,
                complex_id=COMPLEX_ID,
                chain=CHAIN,
                species_taxid=REFERENCE_TAXID,
            ).as_posix(),
            "target_embedding_shape": f"{contract.length}x960",
            "target_embedding_dtype": "float32",
            "target_embedding_sha256": contract.embedding_sha256,
            "target_embedding_path": embedding_path(
                output_dir=Path("data/output"),
                model_name=MODEL_NAME,
                complex_id=COMPLEX_ID,
                chain=CHAIN,
                species_taxid=contract.taxid,
            ).as_posix(),
            "mapping_table": DEFAULT_MAPPING_TABLE.as_posix(),
            "mapping_table_sha256": EXPECTED_MAPPING_SHA256,
            "mapping_source": MAPPING_SOURCE,
            "source_interface_coordinate_system": "Q00987_full_length_zero_based",
            "target_interface_coordinate_system": "target_full_length_zero_based",
            "source_interface_residue_count": "47",
            "source_interface_reference_identity_count": "47",
            "alignment_policy": ALIGNMENT_POLICY,
            "metric_family": METRIC_FAMILY,
            "shuffle_metric_family": METRIC_FAMILY,
            "shuffle_mask_policy": SHUFFLE_POLICY,
            "shuffle_seed": str(SHUFFLE_SEED),
            "shuffle_control_count": str(SHUFFLE_CONTROL_COUNT),
            "shuffle_valid_control_count": str(SHUFFLE_CONTROL_COUNT),
            "mapped_interface_enrichment_run": "true",
            "single_long_lived_lineage_limitation": "true",
            "gate8_input_status": "created_pending_a2_a3_and_gate8_disposition",
            "allowed_next_action": "run_mapping_cutoff_and_alignment_sensitivity",
            "claim_status": ("technical_mapped_interface_enrichment_result_no_gate8_disposition"),
            "result_date": RESULT_DATE,
        }
        for field, expected in static.items():
            _require(row, field, expected)
        for field in FALSE_BOUNDARY_FIELDS:
            _require(row, field, "false")

        aligned = int(row["aligned_residue_count"])
        mapped = int(row["mapped_interface_count"])
        dropped = int(row["dropped_interface_count"])
        primary_interface = int(row["primary_interface_count"])
        primary_noninterface = int(row["primary_noninterface_count"])
        if mapped + dropped != 47:
            raise ValueError("Mapped and dropped interface counts do not sum to 47")
        if primary_interface != mapped or primary_noninterface != aligned - mapped:
            raise ValueError("Primary metric counts are inconsistent with mapping")
        if not 0 < mapped < aligned:
            raise ValueError("Mapped interface must leave aligned background residues")
        if dropped == 0:
            _require(row, "mapping_status", "complete_all_source_interface_residues_aligned")
            _require(row, "dropped_reference_zero_based_indices", "none")
        else:
            _require(
                row,
                "mapping_status",
                "partial_source_interface_mapping_with_recorded_drops",
            )

        for field in finite_fields:
            if not math.isfinite(float(row[field])):
                raise ValueError(f"Non-finite result field {field}")
        for field in probability_fields:
            if not 0.0 <= float(row[field]) <= 1.0:
                raise ValueError(f"Probability field {field} is out of bounds")
        ge_count = int(row["shuffle_ge_observed_count"])
        le_count = int(row["shuffle_le_observed_count"])
        if not 0 <= ge_count <= SHUFFLE_CONTROL_COUNT:
            raise ValueError("Invalid shuffled greater/equal count")
        if not 0 <= le_count <= SHUFFLE_CONTROL_COUNT:
            raise ValueError("Invalid shuffled less/equal count")


def write_result_rows(path: Path, rows: list[dict[str, str]]) -> None:
    """Write canonical result rows with stable field order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_and_validate_result(
    root: Path,
    result_table: Path = DEFAULT_RESULT_TABLE,
) -> list[dict[str, str]]:
    """Load and validate the committed A1 result table in CI."""
    if canonical_text_sha256(root / DEFAULT_MAPPING_TABLE) != EXPECTED_MAPPING_SHA256:
        raise ValueError("Committed mapping table SHA-256 changed")
    with (root / result_table).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    validate_result_rows(rows)
    return rows


def _required_root(
    explicit: Path | None,
    env_name: str,
) -> Path:
    if explicit is None:
        raw_value = os.environ.get(env_name, "").strip()
        if not raw_value:
            raise ValueError(f"{env_name} is not configured")
        value = Path(raw_value)
    else:
        value = explicit
    if not value.exists() or not value.is_dir():
        raise ValueError(f"{env_name} must point to an existing directory")
    return value


@app.command()
def main(
    repo_root: Annotated[Path, typer.Option(help="Repository root.")] = Path("."),
    reference_sequence_root: Annotated[
        Path | None,
        typer.Option(
            help=(f"External Q00987/G3SX30 FASTA root; defaults to {REFERENCE_SEQUENCE_ROOT_ENV}.")
        ),
    ] = None,
    binding_root: Annotated[
        Path | None,
        typer.Option(
            help=(
                f"External P23804/A0ABM2YB85 binding root; defaults to {bindings.BINDING_ROOT_ENV}."
            )
        ),
    ] = None,
    output: Annotated[Path, typer.Option(help="Committed compact result table.")] = (
        DEFAULT_RESULT_TABLE
    ),
    yes_run: Annotated[
        bool,
        typer.Option(
            "--yes-run",
            help="Compute the three local enrichment rows after a successful dry run.",
        ),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Replace an existing result table only when explicitly requested.",
        ),
    ] = False,
) -> None:
    """Validate A1 inputs or explicitly compute the three mapped-interface rows."""
    load_dotenv()
    resolved_repo_root = repo_root.resolve()
    try:
        resolved_reference_root = _required_root(
            reference_sequence_root,
            REFERENCE_SEQUENCE_ROOT_ENV,
        )
        resolved_binding_root = _required_root(
            binding_root,
            bindings.BINDING_ROOT_ENV,
        )
        panel = prepare_panel(
            repo_root=resolved_repo_root,
            reference_sequence_root=resolved_reference_root,
            binding_root=resolved_binding_root,
        )
    except (OSError, ValueError) as exc:
        typer.echo(f"BLOCKED: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo("A1 scoped MDM2 mapped-interface input audit: ready")
    typer.echo(
        f"mapping: {DEFAULT_MAPPING_TABLE.as_posix()} "
        f"sha256={EXPECTED_MAPPING_SHA256} interface_rows=47"
    )
    for prepared in panel.targets:
        mapped = len(prepared.mapped_interface_target_indices)
        dropped = len(prepared.dropped_reference_interface_indices)
        typer.echo(
            f"{prepared.contract.species}/{prepared.contract.accession}: "
            f"embedding={prepared.embedding.shape} mapped={mapped} dropped={dropped} "
            f"optimal_alignments={prepared.alignment.optimal_alignment_count}"
        )

    resolved_output = output if output.is_absolute() else resolved_repo_root / output
    if not yes_run:
        typer.echo("DRY RUN: no enrichment metrics were computed and no file was written.")
    else:
        if resolved_output.exists() and not overwrite:
            typer.echo(
                f"BLOCKED: output already exists: {resolved_output}; use --overwrite explicitly.",
                err=True,
            )
            raise typer.Exit(code=1)
        rows = build_result_rows(panel)
        write_result_rows(resolved_output, rows)
        typer.echo(f"Wrote {len(rows)} audited result rows -> {resolved_output}")

    typer.echo("No Biohub/ESMC calls were made.")
    typer.echo("No new embeddings or data/output artifacts were written.")
    typer.echo("No Gate 8 disposition or Gate 9 promotion was performed.")
    typer.echo("No biological claim was made.")


if __name__ == "__main__":
    app()
