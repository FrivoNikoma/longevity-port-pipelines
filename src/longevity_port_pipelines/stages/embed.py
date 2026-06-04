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
import requests

logger = logging.getLogger(__name__)


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


def embed_sequence(
    sequence: str,
    model: str,
    api_url: str,
    token: str,
    timeout: int = 180,
) -> np.ndarray:
    """Request per-residue ESM C embeddings for one sequence from Biohub.

    Returns an array of shape (L, D) where L == len(sequence).
    """
    resp = requests.post(
        f"{api_url.rstrip('/')}/v1/embeddings",
        headers={"Authorization": f"Bearer {token}"},
        json={"model": model, "sequence": sequence},
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()

    embeddings = np.asarray(data["embeddings"], dtype=np.float32)
    if embeddings.ndim != 2:
        raise ValueError(
            f"Expected per-residue embeddings of shape (L, D), got {embeddings.shape}"
        )
    return embeddings


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
