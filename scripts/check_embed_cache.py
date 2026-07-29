#!/usr/bin/env python3
"""Gate check: are the currently-selected complexes already embedded (cache hit)?

Reads data/output/selection.csv and the ESM embedding cache dir, and reports, per
selected complex, how many cached .npy files exist. A complex with 0 cached files
would trigger fresh Biohub embedding; one with ~40+ was fully embedded before and
can be re-analyzed for free. Run right after `uv run select`, before the slow
orthologs stage, to decide whether regenerating a lane's enrichment is Biohub-free.
"""
from __future__ import annotations

import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SELECTION = REPO / "data" / "output" / "selection.csv"
EMB = REPO / "data" / "output" / "embeddings" / "esmc-300m-2024-12"


def main():
    ids = [r["id"] for r in csv.DictReader(SELECTION.open())]
    cached = list(EMB.iterdir()) if EMB.exists() else []
    names = [p.name for p in cached]
    n_zero = 0
    print(f"{'complex':42s} cached_npy")
    for cid in ids:
        c = sum(1 for n in names if n.startswith(cid + "_"))
        flag = "  <-- NOT CACHED (would hit Biohub)" if c == 0 else ""
        if c == 0:
            n_zero += 1
        print(f"{cid:42s} {c:4d}{flag}")
    safe = n_zero == 0
    print(f"\n{len(ids)} complexes; {n_zero} not cached. "
          f"{'BIOHUB-FREE — safe to run orthologs+analyze.' if safe else 'Some need Biohub.'}")


if __name__ == "__main__":
    main()
