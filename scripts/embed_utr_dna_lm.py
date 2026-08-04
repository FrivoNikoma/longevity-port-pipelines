#!/usr/bin/env python3
"""Embed lane-gene UTRs with a DNA language model (Nucleotide Transformer).

This is the AI counterpart to the classical UTR-alignment divergence
(scripts/analyze_utr3_divergence.py). It mirrors, one biological level up, exactly the
ESM interface-embedding approach that the project used on coding interfaces: instead of
aligning sequences, embed each UTR with a pretrained genomic language model and later
measure lineage-specific L2 divergence in embedding space
(scripts/analyze_utr_embedding_divergence.py).

Model: InstaDeepAI/nucleotide-transformer-v2-50m-multi-species (CPU-friendly, 512-dim).
The sequence embedding is the attention-mask-weighted mean of the final hidden states.

torch + transformers are intentionally NOT project dependencies (they would bloat the
locked env and CI). Run with an ephemeral environment:

    uv run --with torch --with transformers --with numpy python scripts/embed_utr_dna_lm.py
    uv run --with torch --with transformers --with numpy python scripts/embed_utr_dna_lm.py \
        --model InstaDeepAI/nucleotide-transformer-v2-100m-multi-species

Inputs:  data/interim/utr/{GENE}_utr5.fasta, {GENE}_utr3.fasta
Outputs: data/interim/utr_emb/{GENE}_{region}.npz   (arrays keyed by species name)
         data/interim/utr_emb/embed_coverage.tsv
No Biohub credits are used.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
UTR_DIR = REPO / "data" / "interim" / "utr"
OUT_DIR = REPO / "data" / "interim" / "utr_emb"
DEFAULT_MODEL = "InstaDeepAI/nucleotide-transformer-v2-50m-multi-species"


def load_fasta(path: Path) -> dict[str, str]:
    seqs: dict[str, str] = {}
    name = None
    buf: list[str] = []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if name is not None:
                seqs[name] = "".join(buf)
            name = line[1:].split("|")[1]  # >{taxid}|{name}|{group}
            buf = []
        elif line.strip():
            buf.append(line.strip())
    if name is not None:
        seqs[name] = "".join(buf)
    return seqs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--max-tokens", type=int, default=1000)
    args = ap.parse_args()

    import torch  # noqa: PLC0415
    from transformers import AutoModelForMaskedLM, AutoTokenizer  # noqa: PLC0415

    if not UTR_DIR.exists() or not any(UTR_DIR.glob("*_utr*.fasta")):
        print(f"No UTR FASTAs in {UTR_DIR}. Run scripts/fetch_lane_utr3.py first.")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.model} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    model = AutoModelForMaskedLM.from_pretrained(args.model, trust_remote_code=True)
    model.eval()

    @torch.no_grad()
    def embed(seq: str) -> np.ndarray:
        enc = tok(
            seq, return_tensors="pt", truncation=True, max_length=args.max_tokens,
        )
        out = model(**enc, output_hidden_states=True)
        hidden = out.hidden_states[-1][0]  # (tokens, dim)
        mask = enc["attention_mask"][0].unsqueeze(-1).to(hidden.dtype)
        pooled = (hidden * mask).sum(0) / mask.sum(0).clamp(min=1.0)
        return pooled.float().cpu().numpy()

    report: list[tuple] = []
    for region in ("utr3", "utr5"):
        for fp in sorted(UTR_DIR.glob(f"*_{region}.fasta")):
            gene = fp.name.replace(f"_{region}.fasta", "")
            seqs = load_fasta(fp)
            vecs: dict[str, np.ndarray] = {}
            for sp, seq in seqs.items():
                seq = "".join(c for c in seq.upper() if c in "ACGTN")
                if len(seq) < 12:
                    continue
                vecs[sp] = embed(seq)
            if vecs:
                np.savez(OUT_DIR / f"{gene}_{region}.npz", **vecs)
                dim = len(next(iter(vecs.values())))
                report.append((gene, region, len(vecs), dim))
                print(f"[{gene:7s} {region}] {len(vecs)} species embedded (dim={dim})", flush=True)

    rep_path = OUT_DIR / "embed_coverage.tsv"
    with open(rep_path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["gene", "region", "n_species", "dim"])
        w.writerows(report)
    print(f"\nEmbeddings: {OUT_DIR}\nCoverage: {rep_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
