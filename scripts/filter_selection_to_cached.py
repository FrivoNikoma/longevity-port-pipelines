#!/usr/bin/env python3
"""Filter data/output/selection.csv to complexes that are (near-)fully embedded.

Keeps only selected complexes with >= THRESHOLD cached .npy files, so the
subsequent orthologs + analyze run reuses the embedding cache and never calls
Biohub. Drops uncached (0) and partially-cached complexes. Rewrites selection.csv
in place.

Usage: uv run python scripts/filter_selection_to_cached.py [threshold]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SELECTION = REPO / "data" / "output" / "selection.csv"
EMB = REPO / "data" / "output" / "embeddings" / "esmc-300m-2024-12"
THRESHOLD = int(sys.argv[1]) if len(sys.argv) > 1 else 42


def main():
    names = [p.name for p in EMB.iterdir()] if EMB.exists() else []
    with SELECTION.open(newline="") as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames
        rows = list(reader)
    kept = []
    for r in rows:
        cid = r["id"]
        c = sum(1 for n in names if n.startswith(cid + "_"))
        if c >= THRESHOLD:
            kept.append(r)
    with SELECTION.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(kept)
    print(f"kept {len(kept)}/{len(rows)} complexes with >= {THRESHOLD} cached embeddings "
          f"(Biohub-free); dropped {len(rows) - len(kept)}")
    for r in kept:
        print(f"  keep {r['id']}")


if __name__ == "__main__":
    main()
