#!/usr/bin/env python3
"""Fetch an intronic window per (gene, species) — the neutral control for the indel result.

The proximal 3' UTR indel deficit (docs/results/2026-08-07-utr-constraint-nature) survives a
*internal* background control built from the distal half of the same UTRs. That background is
neither neutral nor well annotated. The decisive test is an **external** neutral reference:
intronic sequence from the same genes in the same species, run through the identical alignment
and indel machinery. If long-lived mammals simply accumulate indels more slowly everywhere
(longer generation times, lower per-year mutation rate), it will show up here too and the 3' UTR
result deflates. If introns are flat, the deficit is specific to the proximal 3' UTR.

Window choice: a fixed-length window centred on the **midpoint of the gene body**. For genes of
this size the exonic fraction is a few percent, so a mid-gene window is intronic with high
probability without needing exon-level annotation (which esummary does not provide). Genes whose
genomic span is below --min-span are skipped rather than risking an exon-dense window.

Route (NCBI, stdlib only, same plumbing as scripts/fetch_gene_genomic_windows.py):
  1. esearch gene: SYMBOL[Gene Name] AND txidNNNN[Organism] -> gene id
  2. esummary gene (xml): GenomicInfo -> ChrAccVer, ChrStart, ChrStop (0-based, strand implied)
  3. efetch nuccore over the mid-gene window; reverse-complement for minus-strand genes

Output goes into the panel UTR directory with the panel's own header format, so the existing
analysis reads it unchanged::

    data/interim/utr_panel/{GENE}_intron.fasta    headers: >{taxid}|{short_name}|{clade}

    uv run python scripts/fetch_gene_introns.py
    uv run python scripts/analyze_utr_constraint_geometry.py --region intron \
        --out-dir docs/results/<next-layer>

Resumable: a gene whose fasta already covers every resolvable species is skipped. Network runs
on YOUR machine. No Biohub credits used.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PANEL = REPO / "data" / "config" / "species_panel_extended.tsv"
OUT_DIR = REPO / "data" / "interim" / "utr_panel"
EMAIL = "nikomafrivo@gmail.com"
TOOL = "longevity-port-pipelines-introns"
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

WINDOW = 3000  # matches MAX_ALN in the analysis, so no further truncation happens
MIN_SPAN = 20_000  # below this a mid-gene window risks being exon-dense
PAUSE = 0.34  # NCBI courtesy rate limit without an API key

CELLCYCLE = [
    "RB1", "TP53", "CDK1", "CDK2", "CDK4", "CDK6", "ATM", "ATR", "CDC20",
    "E2F1", "TFDP1", "CCND1", "CCNE1", "CCNA2", "CCNB1", "CDKN1A", "CDKN1B",
    "CDKN2A", "MDM2", "MDM4", "CHEK1", "CHEK2", "WEE1", "CDC25A", "BUB1B",
]

_COMP = str.maketrans("ACGTN", "TGCAN")


def revcomp(seq: str) -> str:
    return seq.translate(_COMP)[::-1]


def http_get(url: str, tries: int = 4, pause: float = PAUSE) -> str:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": f"{TOOL} ({EMAIL})", "Accept": "*/*"}
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(pause * (attempt + 1) * 2)
    raise RuntimeError(f"GET failed after {tries} tries: {url}\n  {last}")


def ncbi_url(endpoint: str, **params: str) -> str:
    params.setdefault("tool", TOOL)
    params.setdefault("email", EMAIL)
    return f"{NCBI}/{endpoint}?" + urllib.parse.urlencode(params)


def resolve_taxid(sciname: str) -> str | None:
    xml = http_get(ncbi_url("esearch.fcgi", db="taxonomy",
                            term=f"{sciname}[Scientific Name]", retmax="1"))
    time.sleep(PAUSE)
    m = re.search(r"<Id>(\d+)</Id>", xml)
    return m.group(1) if m else None


def load_panel() -> list[tuple[str, str, str]]:
    with open(PANEL, newline="") as fh:
        return [(r["short_name"], r["scientific_name"], r["clade"])
                for r in csv.DictReader(fh, delimiter="\t")]


def gene_locus(gene: str, taxid: str) -> tuple[str, int, int] | None:
    """(chr_accession, chr_start_0based, chr_stop_0based); start > stop means minus strand."""
    term = f"{gene}[Gene Name] AND txid{taxid}[Organism]"
    xml = http_get(ncbi_url("esearch.fcgi", db="gene", term=term, retmax="5"))
    time.sleep(PAUSE)
    for gid in re.findall(r"<Id>(\d+)</Id>", xml)[:3]:
        summ = http_get(ncbi_url("esummary.fcgi", db="gene", id=gid,
                                 retmode="xml", version="2.0"))
        time.sleep(PAUSE)
        m = re.search(
            r"<ChrAccVer>([^<]+)</ChrAccVer>\s*<ChrStart>(\d+)</ChrStart>"
            r"\s*<ChrStop>(\d+)</ChrStop>",
            summ,
        )
        if m:
            return m.group(1), int(m.group(2)), int(m.group(3))
    return None


def fetch_region(acc: str, start_1: int, stop_1: int) -> str:
    txt = http_get(ncbi_url("efetch.fcgi", db="nuccore", id=acc, rettype="fasta",
                            retmode="text", seq_start=str(start_1),
                            seq_stop=str(stop_1), strand="1"))
    time.sleep(PAUSE)
    return "".join(ln.strip() for ln in txt.splitlines()
                   if ln and not ln.startswith(">")).upper()


def intron_window(gene: str, taxid: str, window: int,
                  min_span: int) -> tuple[str, str, int, str] | None:
    """(accession, strand, gene_span, sequence in transcription orientation) or None."""
    locus = gene_locus(gene, taxid)
    if locus is None:
        return None
    acc, chr_start, chr_stop = locus
    minus = chr_start > chr_stop
    lo0, hi0 = (chr_stop, chr_start) if minus else (chr_start, chr_stop)
    span = hi0 - lo0
    if span < min_span:
        return None
    mid0 = lo0 + span // 2
    start_1 = max(1, mid0 + 1 - window // 2)
    seq = fetch_region(acc, start_1, start_1 + window - 1)
    if not seq or set(seq) - set("ACGTN"):
        return None
    if seq.count("N") / len(seq) > 0.2:
        return None
    return acc, ("-" if minus else "+"), span, (revcomp(seq) if minus else seq)


def read_existing(fp: Path) -> set[str]:
    if not fp.exists():
        return set()
    return {ln[1:].split("|")[1] for ln in fp.read_text().splitlines()
            if ln.startswith(">") and len(ln[1:].split("|")) > 1}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--genes", default=",".join(CELLCYCLE))
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--min-span", type=int, default=MIN_SPAN)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    genes = [g.strip() for g in args.genes.split(",") if g.strip()]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("resolving taxids ...", flush=True)
    species: list[tuple[str, str, str]] = [("human", "REFERENCE", "9606")]
    for short, sci, cl in load_panel():
        if short == "human":
            continue
        try:
            taxid = resolve_taxid(sci)
        except Exception:  # noqa: BLE001
            taxid = None
        if taxid:
            species.append((short, cl, taxid))
        else:
            print(f"  taxid NOT FOUND: {sci} ({short})", flush=True)
    print(f"  {len(species)} species resolved\n", flush=True)

    report: list[tuple] = []
    for gene in genes:
        fp = OUT_DIR / f"{gene}_intron.fasta"
        have = set() if args.force else read_existing(fp)
        if have and all(s in have for s, _c, _t in species):
            print(f"[{gene:8s}] cached ({len(have)} species)", flush=True)
            continue
        lines: list[str] = [] if args.force else (
            fp.read_text().rstrip("\n").splitlines() if fp.exists() else [])
        added = 0
        for short, cl, taxid in species:
            if short in have:
                continue
            try:
                res = intron_window(gene, taxid, args.window, args.min_span)
            except Exception as exc:  # noqa: BLE001
                res = None
                note = f"ERROR:{exc}"
            else:
                note = "" if res else "no locus / span too small / too many Ns"
            if res is None:
                report.append((gene, short, taxid, "", "", 0, "FAIL", note))
                continue
            acc, strand, span, seq = res
            lines.append(f">{taxid}|{short}|{cl}")
            lines += [seq[i:i + 80] for i in range(0, len(seq), 80)]
            added += 1
            report.append((gene, short, taxid, acc, strand, span, "OK", ""))
        if lines:
            fp.write_text("\n".join(lines) + "\n")
        print(f"[{gene:8s}] +{added} species -> {fp.name}", flush=True)

    rep = OUT_DIR / "intron_coverage.tsv"
    with open(rep, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["gene", "species", "taxid", "accession", "strand", "gene_span",
                    "status", "note"])
        w.writerows(report)
    ok = sum(1 for r in report if r[6] == "OK")
    print(f"\n=== {ok}/{len(report)} intron windows OK ===", file=sys.stderr)
    print(f"Coverage: {rep}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
