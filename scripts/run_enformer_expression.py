#!/usr/bin/env python3
"""Predict per-species regulatory output at each gene's TSS with Enformer.

The AI expression-prediction step of the regulatory investigation. Enformer takes a
196,608 bp genomic window and predicts 896 bins x 5313 human tracks (CAGE expression,
DNase, ChIP). For each (gene, species) window (scripts/fetch_gene_genomic_windows.py) we
run the model and store the predicted track vector at the central (TSS) bins. Because
Enformer is trained on the human genome, feeding a species' orthologous window and reading
the human-head prediction is a comparative in-silico readout: "what the human regulatory
model predicts for this species' sequence" - the sequence varies, the reader is held fixed.

torch + enformer-pytorch are NOT project dependencies (they would bloat the locked env and
CI). Run ephemerally:

    uv run --with torch --with enformer-pytorch --with numpy \
        python scripts/run_enformer_expression.py

Inputs:  data/interim/genome_windows/{GENE}_{species}.fasta
Outputs: data/interim/enformer/{GENE}_{species}.npy    (central-bin-mean, 5313 human tracks)
         data/interim/enformer/enformer_coverage.tsv
No Biohub credits used.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
WIN_DIR = REPO / "data" / "interim" / "genome_windows"
OUT_DIR = REPO / "data" / "interim" / "enformer"
SEQ_LEN = 196_608
CENTER_BINS = 3  # average predictions over the +/-1 bins around the TSS bin


def load_window(path: Path) -> str:
    seq = "".join(ln.strip() for ln in path.read_text().splitlines()
                  if ln and not ln.startswith(">")).upper()
    # center-crop / N-pad to the exact model input length, keeping the TSS centred
    if len(seq) > SEQ_LEN:
        off = (len(seq) - SEQ_LEN) // 2
        seq = seq[off : off + SEQ_LEN]
    elif len(seq) < SEQ_LEN:
        pad = SEQ_LEN - len(seq)
        seq = "N" * (pad // 2) + seq + "N" * (pad - pad // 2)
    return seq


def main() -> int:
    import torch  # noqa: PLC0415
    from enformer_pytorch import Enformer, str_to_one_hot  # noqa: PLC0415

    if not WIN_DIR.exists() or not any(WIN_DIR.glob("*.fasta")):
        print(f"No windows in {WIN_DIR}. Run scripts/fetch_gene_genomic_windows.py first.")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading Enformer (EleutherAI/enformer-official-rough) ...", flush=True)
    model = Enformer.from_pretrained("EleutherAI/enformer-official-rough")
    model.eval()

    report: list[tuple] = []
    for fp in sorted(WIN_DIR.glob("*.fasta")):
        stem = fp.stem  # {GENE}_{species}
        out_path = OUT_DIR / f"{stem}.npy"
        if out_path.exists():
            continue
        seq = load_window(fp)
        one_hot = str_to_one_hot(seq)[None]  # (1, L, 4)
        with torch.no_grad():
            pred = model(one_hot)["human"][0]  # (896, 5313)
        mid = pred.shape[0] // 2
        lo, hi = mid - CENTER_BINS // 2, mid + CENTER_BINS // 2 + 1
        vec = pred[lo:hi].mean(dim=0).float().cpu().numpy()  # (5313,)
        np.save(out_path, vec)
        report.append((stem, int(vec.shape[0]), float(vec.mean())))
        print(f"[{stem:28s}] tracks={vec.shape[0]} mean_activity={vec.mean():.4f}", flush=True)

    with open(OUT_DIR / "enformer_coverage.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["window", "n_tracks", "mean_central_activity"])
        w.writerows(report)
    print(f"\nEmbeddings/predictions: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
