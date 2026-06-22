"""Stage 5: Embed protein sequences via the remote Biohub ESMC SDK.

This is a remote-compute stage: the Prefect `embed` task is a thin wrapper
around these functions, and the model is not run locally. The implementation
uses Biohub's ESM SDK client to call the remote ESMC service.

The SDK may return torch tensors, so this module imports torch to convert
returned embeddings to NumPy arrays. This does not mean the pipeline requires
a local GPU or local model weights.

The auth token is read from the BIOHUB_API_TOKEN environment variable
(see .env.template). ESM-2 is outdated — do NOT use it; we use ESM C.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from esm.sdk import ESMCForgeInferenceClient  # type: ignore[import-untyped]
from esm.sdk.api import ESMProtein, ESMProteinError, LogitsConfig  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)
_CLIENT_CACHE: dict[tuple[str, str, str], ESMCForgeInferenceClient] = {}


@dataclass
class PerResidueEmbedding:
    """Per-residue embedding for a single protein chain."""

    complex_id: str
    chain: str
    species_taxid: int
    model_name: str
    sequence: str
    embeddings: np.ndarray  # shape: (L, D)
    is_predicted_structure: bool = False


def get_biohub_token() -> str:
    """Read the Biohub API token from the environment."""
    token = os.getenv("BIOHUB_API_TOKEN")
    if not token:
        raise RuntimeError(
            "BIOHUB_API_TOKEN is not set. Copy .env.template to .env and fill it in "
            "(the CLI loads .env automatically)."
        )
    return token


def get_esmc_client(
    model: str,
    api_url: str,
    token: str,
    timeout: int | None = 180,
) -> ESMCForgeInferenceClient:
    """Create or reuse a Biohub ESMC SDK client."""
    key = (model, api_url, token)
    if key not in _CLIENT_CACHE:
        _CLIENT_CACHE[key] = ESMCForgeInferenceClient(
            model=model,
            url=api_url,
            token=token,
            request_timeout=timeout,
        )
    return _CLIENT_CACHE[key]


def embedding_path(
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    species_taxid: int,
) -> Path:
    """Return the canonical saved embedding path for one complex/chain/species."""
    return output_dir / "embeddings" / model_name / f"{complex_id}_{chain}_{species_taxid}.npy"


def load_saved_embedding(
    output_dir: Path,
    model_name: str,
    complex_id: str,
    chain: str,
    species_taxid: int,
    sequence: str,
    is_predicted_structure: bool = False,
) -> PerResidueEmbedding:
    """Load a saved per-residue embedding from disk."""
    path = embedding_path(
        output_dir=output_dir,
        model_name=model_name,
        complex_id=complex_id,
        chain=chain,
        species_taxid=species_taxid,
    )
    arr = np.load(path).astype(np.float32, copy=False)

    if arr.ndim != 2:
        raise ValueError(f"Expected saved embedding matrix with shape (L, D), got {arr.shape}")
    if arr.shape[0] != len(sequence):
        raise ValueError(
            f"Saved embedding length mismatch for {path}: "
            f"expected {len(sequence)}, got {arr.shape[0]}"
        )

    return PerResidueEmbedding(
        complex_id=complex_id,
        chain=chain,
        species_taxid=species_taxid,
        model_name=model_name,
        sequence=sequence,
        embeddings=arr,
        is_predicted_structure=is_predicted_structure,
    )


def embed_sequence(
    sequence: str,
    model: str,
    api_url: str,
    token: str,
    timeout: int = 180,
) -> np.ndarray:
    """Request per-residue ESMC embeddings for one sequence from Biohub SDK.

    Returns an array of shape (L, D), where L is expected to match len(sequence).
    """
    client = get_esmc_client(model=model, api_url=api_url, token=token, timeout=timeout)

    protein = ESMProtein(sequence=sequence)
    protein_tensor = client.encode(protein)
    if isinstance(protein_tensor, ESMProteinError):
        raise RuntimeError(f"Biohub ESMC encode failed: {protein_tensor}")

    output = client.logits(
        protein_tensor,
        LogitsConfig(sequence=True, return_embeddings=True),
    )
    if isinstance(output, ESMProteinError):
        raise RuntimeError(f"Biohub ESMC logits failed: {output}")

    embeddings = output.embeddings
    if embeddings is None:
        raise RuntimeError("Biohub ESMC response did not contain embeddings")

    if isinstance(embeddings, torch.Tensor):
        arr = embeddings.detach().cpu().to(torch.float32).numpy().astype(np.float32)
    else:
        arr = np.asarray(embeddings, dtype=np.float32)

    # SDK responses may include a batch dimension.
    if arr.ndim == 3 and arr.shape[0] == 1:
        arr = arr[0]

    # Some token-level models may include special tokens. Trim conservatively
    # to the biological sequence length if needed.
    if arr.ndim == 2 and arr.shape[0] != len(sequence):
        if arr.shape[0] >= len(sequence):
            arr = arr[: len(sequence)]
        else:
            raise ValueError(
                f"Expected at least {len(sequence)} residue embeddings, got {arr.shape}"
            )

    if arr.ndim != 2:
        raise ValueError(f"Expected per-residue embeddings of shape (L, D), got {arr.shape}")

    return arr


def embed_pair(
    complex_id: str,
    chain: str,
    ref_sequence: str,
    orth_sequence: str,
    ref_taxid: int,
    orth_taxid: int,
    model: str,
    api_url: str,
    token: str,
    is_predicted: bool = False,
) -> tuple[PerResidueEmbedding, PerResidueEmbedding]:
    """Embed both reference and ortholog sequences with the same Biohub model.

    Returns (ref_embedding, orth_embedding).
    """
    ref_emb = embed_sequence(ref_sequence, model, api_url, token)
    orth_emb = embed_sequence(orth_sequence, model, api_url, token)

    return (
        PerResidueEmbedding(
            complex_id=complex_id,
            chain=chain,
            species_taxid=ref_taxid,
            model_name=model,
            sequence=ref_sequence,
            embeddings=ref_emb,
        ),
        PerResidueEmbedding(
            complex_id=complex_id,
            chain=chain,
            species_taxid=orth_taxid,
            model_name=model,
            sequence=orth_sequence,
            embeddings=orth_emb,
            is_predicted_structure=is_predicted,
        ),
    )


def save_embeddings(emb: PerResidueEmbedding, output_dir: Path) -> Path:
    """Save embedding array to disk as a .npy file."""
    path = embedding_path(
        output_dir=output_dir,
        model_name=emb.model_name,
        complex_id=emb.complex_id,
        chain=emb.chain,
        species_taxid=emb.species_taxid,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, emb.embeddings)
    return path


def embed_or_load_sequence(
    complex_id: str,
    chain: str,
    sequence: str,
    species_taxid: int,
    model: str,
    api_url: str,
    token: str,
    output_dir: Path,
    is_predicted_structure: bool = False,
) -> PerResidueEmbedding:
    """Reuse a saved embedding when present, otherwise request it from Biohub."""
    path = embedding_path(
        output_dir=output_dir,
        model_name=model,
        complex_id=complex_id,
        chain=chain,
        species_taxid=species_taxid,
    )

    if path.exists():
        logger.info("Reusing saved embedding: %s", path)
        return load_saved_embedding(
            output_dir=output_dir,
            model_name=model,
            complex_id=complex_id,
            chain=chain,
            species_taxid=species_taxid,
            sequence=sequence,
            is_predicted_structure=is_predicted_structure,
        )

    logger.info("Embedding missing sequence via Biohub: %s", path)
    emb = PerResidueEmbedding(
        complex_id=complex_id,
        chain=chain,
        species_taxid=species_taxid,
        model_name=model,
        sequence=sequence,
        embeddings=embed_sequence(sequence, model, api_url, token),
        is_predicted_structure=is_predicted_structure,
    )
    save_embeddings(emb, output_dir)
    return emb


def embed_pair_cached(
    complex_id: str,
    chain: str,
    ref_sequence: str,
    orth_sequence: str,
    ref_taxid: int,
    orth_taxid: int,
    model: str,
    api_url: str,
    token: str,
    output_dir: Path,
    is_predicted: bool = False,
) -> tuple[PerResidueEmbedding, PerResidueEmbedding]:
    """Embed a reference/ortholog pair, reusing saved files when available."""
    return (
        embed_or_load_sequence(
            complex_id=complex_id,
            chain=chain,
            sequence=ref_sequence,
            species_taxid=ref_taxid,
            model=model,
            api_url=api_url,
            token=token,
            output_dir=output_dir,
        ),
        embed_or_load_sequence(
            complex_id=complex_id,
            chain=chain,
            sequence=orth_sequence,
            species_taxid=orth_taxid,
            model=model,
            api_url=api_url,
            token=token,
            output_dir=output_dir,
            is_predicted_structure=is_predicted,
        ),
    )
