#!/usr/bin/env python3
"""Fetch 5'/3' UTRs for the extended species panel (species resolved by scientific name).

Extends the 22-species UTR fetch to the ~60-species panel in
data/config/species_panel_extended.tsv. To avoid hand-entering taxids, each species'
NCBI taxid is resolved from its scientific name via the NCBI taxonomy database; UTRs are
then fetched with the same mRNA -> CDS-substring slicing as scripts/fetch_lane_utr3.py
(whose helpers are reused).

Outputs (data/interim/utr_panel/):
  {GENE}_utr5.fasta   {GENE}_utr3.fasta   headers: >{taxid}|{short_name}|{clade}
  panel_utr_coverage.tsv

Pure standard library; network runs on YOUR machine. No Biohub credits.

Usage:
    uv run python scripts/fetch_panel_utr.py
    uv run python scripts/fetch_panel_utr.py --genes SIRT6,TP53 --limit 3
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import re
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
PANEL = REPO / "data" / "config" / "species_panel_extended.tsv"
OUT_DIR = REPO / "data" / "interim" / "utr_panel"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


F = _load("fetch_lane_utr3")  # reuse http_get, ncbi_url, resolve_gene, fasta_block, DEFAULT_GENES


def resolve_taxid(sciname: str) -> str | None:
    xml = F.http_get(F.ncbi_url("esearch.fcgi", db="taxonomy",
                                term=f"{sciname}[Scientific Name]", retmax="1"))
    time.sleep(0.34)
    ids = re.findall(r"<Id>(\d+)</Id>", xml)
    return ids[0] if ids else None


def load_panel() -> list[tuple[str, str, str]]:
    rows = []
    with open(PANEL, newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            rows.append((r["short_name"], r["scientific_name"], r["clade"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", default=",".join(F.DEFAULT_GENES))
    ap.add_argument("--limit", type=int, default=0, help="only first N species (testing)")
    args = ap.parse_args()
    genes = [g.strip() for g in args.genes.split(",") if g.strip()]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    panel = load_panel()
    if args.limit:
        panel = panel[: args.limit]

    # resolve taxids once; always include the human reference (needed for divergence)
    species: list[tuple[str, str, str, str]] = [("human", "Homo sapiens", "primates", "9606")]
    for short, sci, clade in panel:
        try:
            taxid = resolve_taxid(sci)
        except Exception:  # noqa: BLE001
            taxid = None
        if taxid:
            species.append((short, sci, clade, taxid))
            print(f"taxid {sci:32s} -> {taxid} ({short})", flush=True)
        else:
            print(f"taxid {sci:32s} -> NOT FOUND ({short})", flush=True)

    def read_blocks(path: Path) -> dict[str, str]:
        blocks: dict[str, str] = {}
        if not path.exists():
            return blocks
        cur, buf = None, []
        for line in path.read_text().splitlines():
            if line.startswith(">"):
                if cur is not None:
                    blocks[cur] = "\n".join(buf)
                cur, buf = line[1:].split("|")[1], [line]
            elif line.strip():
                buf.append(line)
        if cur is not None:
            blocks[cur] = "\n".join(buf)
        return blocks

    report: list[tuple] = []
    for gene in genes:
        b5 = read_blocks(OUT_DIR / f"{gene}_utr5.fasta")
        b3 = read_blocks(OUT_DIR / f"{gene}_utr3.fasta")
        done = set(b5) | set(b3)  # resume: species with any UTR already fetched
        for short, _sci, clade, taxid in species:
            if short in done:
                continue
            try:
                res = F.resolve_gene(gene, int(taxid))
            except Exception as exc:  # noqa: BLE001
                res, note = None, f"ERR:{exc}"
            else:
                note = ""
            if res is None:
                report.append((gene, short, taxid, "", 0, 0, "FAIL", note))
                print(f"[{gene:7s} {short:20s}] FAIL", flush=True)
                continue
            acc, _cds, a5, a3 = res
            if a5:
                b5[short] = F.fasta_block(f"{taxid}|{short}|{clade}", a5)
            if a3:
                b3[short] = F.fasta_block(f"{taxid}|{short}|{clade}", a3)
            status = "OK" if (a5 and a3) else ("UTR5" if a5 else "UTR3" if a3 else "NONE")
            report.append((gene, short, taxid, acc, len(a5), len(a3), status, note))
            print(f"[{gene:7s} {short:20s}] {status:5s} {acc} 5'={len(a5)} 3'={len(a3)}", flush=True)
        order = [s for s, _, _, _ in species]
        if b5:
            (OUT_DIR / f"{gene}_utr5.fasta").write_text(
                "\n".join(b5[n] for n in order if n in b5) + "\n")
        if b3:
            (OUT_DIR / f"{gene}_utr3.fasta").write_text(
                "\n".join(b3[n] for n in order if n in b3) + "\n")

    with open(OUT_DIR / "panel_utr_coverage.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["gene", "short_name", "taxid", "accession", "utr5_len", "utr3_len", "status", "note"])
        w.writerows(report)
    ok = sum(1 for r in report if r[6] == "OK")
    print(f"\n=== {ok}/{len(report)} (gene,species) with both UTRs; {len(species)} species resolved ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
