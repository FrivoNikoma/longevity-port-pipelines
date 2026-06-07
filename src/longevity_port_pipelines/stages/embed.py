"""Stage 5: Embed protein sequences via the Biohub Platform REST API.

This is a remote compute stage — the Prefect `embed` task is a thin wrapper that
calls these functions. We hit the Biohub ESM C endpoint rather than running the
model locally (no torch/GPU dependency in this repo).

The auth token is read from the BIOHUB_API_TOKEN environment variable (see
.env.template). ESM-2 is outdated — do NOT use it; we use ESM C.

NOTE: the exact endpoint path and response schema below follow the documented
Biohub embeddings contract — if the API shape changes, adjust `embed_sequence`.
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
    subdir = output_dir / "embeddings" / emb.model_name
    subdir.mkdir(parents=True, exist_ok=True)
    fname = f"{emb.complex_id}_{emb.chain}_{emb.species_taxid}.npy"
    path = subdir / fname
    np.save(path, emb.embeddings)
    return path
