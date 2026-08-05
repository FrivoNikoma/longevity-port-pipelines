#!/usr/bin/env python3
"""Fetch Enformer-sized genomic windows centered on each gene's TSS, per species.

Enformer (and Borzoi) predict regulatory output (expression, chromatin) from a large
genomic window, not from mRNA. To score predicted gene dosage per species we need, for each
(gene, species), a fixed-length window centered on the transcription start site.

Route (NCBI, uniform, stdlib only):
  1. esearch gene: SYMBOL[Gene Name] AND txidNNNN[Organism] -> gene id.
  2. esummary gene (xml): GenomicInfo -> ChrAccVer, ChrStart, ChrStop (0-based). Strand is
     inferred from ChrStart vs ChrStop; the TSS is the gene-oriented 5' end (ChrStart).
  3. efetch nuccore over [TSS-HALF, TSS+HALF) on the plus strand; reverse-complement for
     minus-strand genes; N-pad at scaffold edges to the exact Enformer length. The TSS sits
     at the window centre.

Outputs (data/interim/genome_windows/, gitignored):
  {GENE}_{species}.fasta   header: >{taxid}|{species}|{group}|{ChrAccVer}|{strand}|tss_center
  window_coverage.tsv

Pilot default genes: HAS2, TP53, CDK2. Pure stdlib; network runs on YOUR machine.
No Biohub credits used.
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
OUT_DIR = REPO / "data" / "interim" / "genome_windows"
EMAIL = "nikomafrivo@gmail.com"
TOOL = "longevity-port-pipelines-genome-windows"
SEQ_LEN = 196_608       # Enformer input length (896 bins x 128 bp)
HALF = SEQ_LEN // 2

DEFAULT_GENES = ["HAS2", "TP53", "CDK2"]

TAXA = {
    9606: ("human", "REFERENCE"),
    10181: ("naked_mole_rat", "ELLSM"), 885580: ("damaraland_mole_rat", "ELLSM"),
    1026970: ("blind_mole_rat", "ELLSM"), 59463: ("myotis_lucifugus", "ELLSM"),
    59479: ("greater_horseshoe_bat", "ELLSM"),
    9785: ("elephant", "BMAL"), 9771: ("blue_whale", "BMAL"), 9749: ("beluga", "BMAL"),
    9755: ("sperm_whale", "BMAL"), 73337: ("white_rhino", "BMAL"),
    10090: ("mouse", "REFERENCE"), 10116: ("rat", "REFERENCE"), 10036: ("hamster", "REFERENCE"),
    10141: ("guinea_pig", "REFERENCE"), 9544: ("rhesus", "REFERENCE"), 9940: ("sheep", "REFERENCE"),
    13616: ("opossum", "REFERENCE"), 9615: ("dog", "REFERENCE"), 30608: ("mouse_lemur", "REFERENCE"),
    43179: ("ground_squirrel", "REFERENCE"), 9365: ("hedgehog", "REFERENCE"), 9685: ("cat", "REFERENCE"),
}

_COMP = str.maketrans("ACGTN", "TGCAN")


def revcomp(seq: str) -> str:
    return seq.translate(_COMP)[::-1]


def http_get(url: str, tries: int = 4, pause: float = 0.34) -> str:
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


NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def ncbi_url(endpoint: str, **params: str) -> str:
    params.setdefault("tool", TOOL)
    params.setdefault("email", EMAIL)
    return f"{NCBI}/{endpoint}?" + urllib.parse.urlencode(params)


def gene_locus(gene: str, taxid: int) -> tuple[str, int, int] | None:
    """Return (chr_accession, chr_start_0based, chr_stop_0based) for the gene, or None."""
    term = f"{gene}[Gene Name] AND txid{taxid}[Organism]"
    xml = http_get(ncbi_url("esearch.fcgi", db="gene", term=term, retmax="5"))
    time.sleep(0.34)
    gene_ids = re.findall(r"<Id>(\d+)</Id>", xml)
    for gid in gene_ids[:3]:
        summ = http_get(ncbi_url("esummary.fcgi", db="gene", id=gid, retmode="xml", version="2.0"))
        time.sleep(0.34)
        m = re.search(
            r"<ChrAccVer>([^<]+)</ChrAccVer>\s*<ChrStart>(\d+)</ChrStart>\s*<ChrStop>(\d+)</ChrStop>",
            summ,
        )
        if m:
            return m.group(1), int(m.group(2)), int(m.group(3))
    return None


def fetch_region(acc: str, start_1: int, stop_1: int) -> str:
    """Fetch plus-strand nuccore region [start_1, stop_1] (1-based, inclusive)."""
    txt = http_get(
        ncbi_url("efetch.fcgi", db="nuccore", id=acc, rettype="fasta", retmode="text",
                 seq_start=str(start_1), seq_stop=str(stop_1), strand="1")
    )
    time.sleep(0.34)
    return "".join(ln.strip() for ln in txt.splitlines()
                   if ln and not ln.startswith(">")).upper()


def window_for(gene: str, taxid: int) -> tuple[str, str, str] | None:
    """Return (accession, strand, SEQ_LEN sequence in transcription orientation), or None."""
    locus = gene_locus(gene, taxid)
    if locus is None:
        return None
    acc, chr_start, chr_stop = locus
    minus = chr_start > chr_stop
    tss0 = chr_start                       # 0-based gene-oriented 5' end
    center1 = tss0 + 1                     # 1-based
    want_start = center1 - HALF
    want_stop = center1 + HALF - 1
    fetch_start = max(1, want_start)
    left_pad = fetch_start - want_start
    seq = fetch_region(acc, fetch_start, want_stop)
    if not seq or set(seq) - set("ACGTN"):
        return None
    full = "N" * left_pad + seq
    if len(full) < SEQ_LEN:
        full = full + "N" * (SEQ_LEN - len(full))
    full = full[:SEQ_LEN]
    oriented = revcomp(full) if minus else full
    return acc, ("-" if minus else "+"), oriented


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", default=",".join(DEFAULT_GENES))
    ap.add_argument("--only", default="", help="comma-separated taxids")
    args = ap.parse_args()
    genes = [g.strip() for g in args.genes.split(",") if g.strip()]
    only = {int(x) for x in args.only.split(",") if x.strip()}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report: list[tuple] = []
    for gene in genes:
        for taxid, (name, group) in TAXA.items():
            if only and taxid not in only:
                continue
            try:
                res = window_for(gene, taxid)
            except Exception as exc:  # noqa: BLE001
                res = None
                note = f"ERROR:{exc}"
            else:
                note = ""
            if res is None:
                report.append((gene, taxid, name, group, "", "", 0, "FAIL", note))
                print(f"[{gene:6s} {name:20s}] FAIL {note}", flush=True)
                continue
            acc, strand, seq = res
            n_frac = seq.count("N") / len(seq)
            fp = OUT_DIR / f"{gene}_{name}.fasta"
            lines = [f">{taxid}|{name}|{group}|{acc}|{strand}|tss_center"]
            lines += [seq[i : i + 80] for i in range(0, len(seq), 80)]
            fp.write_text("\n".join(lines) + "\n")
            status = "OK" if n_frac < 0.5 else "MOSTLY_N"
            report.append((gene, taxid, name, group, acc, strand, round(n_frac, 3), status, note))
            print(f"[{gene:6s} {name:20s}] {status:8s} {acc} {strand} N={n_frac:.2f}", flush=True)

    rep = OUT_DIR / "window_coverage.tsv"
    with open(rep, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["gene", "taxid", "name", "group", "accession", "strand", "n_frac", "status", "note"])
        w.writerows(report)
    ok = sum(1 for r in report if r[7] == "OK")
    print(f"\n=== {ok}/{len(report)} windows OK ===", file=sys.stderr)
    print(f"Coverage: {rep}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
