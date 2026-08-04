#!/usr/bin/env python3
"""Fetch 5' and 3' UTR nucleotide sequences for lane genes across the 22-species panel.

Motivation
----------
The interface-divergence screen (ESM-L2 on coding interfaces) is formally closed as
negative (docs/results/2026-07-29-synthesis-negative-and-method-boundary). The project's
only positive leads sit at a *regulatory / dosage* level (elephant TP53 copy number;
naked mole-rat HAS2 output), which coding-interface metrics cannot see. This script moves
the *unit of analysis* off the coding interface and onto the non-coding regulatory
sequence that controls how much protein is made: the 5' UTR (translation efficiency) and
the 3' UTR (mRNA stability, miRNA regulation -- the most "dosage" lever).

Strategy (uniform, resilient to rotted accessions)
--------------------------------------------------
For each (gene symbol, taxid):
  1. NCBI Gene esearch: `SYMBOL[Gene Name] AND txidNNNN[Organism]` -> gene id(s).
  2. elink gene -> nuccore (refseq mRNA preferred) -> candidate transcript ids.
  3. For each transcript: efetch the full mRNA (rettype=fasta) AND its CDS
     (rettype=fasta_cds_na). The CDS is an exact substring of the mRNA, so:
        5' UTR = mRNA[:cds_start]      3' UTR = mRNA[cds_end:]
     No GenBank coordinate parsing needed.
  4. Validate the CDS (len % 3 == 0, ATG start, single terminal stop) and pick the
     transcript with the longest valid CDS, preferring curated NM_ over predicted XM_.

Outputs (data/interim/utr/):
  {GENE}_utr5.fasta   {GENE}_utr3.fasta   headers: >{taxid}|{name}|{group}
  utr_coverage.tsv    per (gene, species) resolution report

Pure standard library (urllib) -- no third-party deps. Network runs on YOUR machine.
ESM / Biohub are NOT used; no Biohub credits are spent.

Usage:
    uv run python scripts/fetch_lane_utr3.py
    uv run python scripts/fetch_lane_utr3.py --genes SIRT6,TP53 --only 10181,9785
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
OUT_DIR = REPO / "data" / "interim" / "utr"
EMAIL = "nikomafrivo@gmail.com"
TOOL = "longevity-port-pipelines-lane-utr"

# Broad first pass: cell_cycle focus genes + the five registry lane leads.
DEFAULT_GENES = [
    "SIRT6", "TP53", "HAS2", "IGF1R", "MTOR", "PRKAA1", "PRKAA2",
    "RB1", "CDK4", "CDK6", "CDK2", "CDK1", "ATM", "ATR", "CDC20",
]

# taxid -> (species_name, group).  Names match TRAITS in analyze_phylo_continuous.py.
TAXA = {
    9606: ("human", "REFERENCE"),
    # long-lived, small-bodied
    10181: ("naked_mole_rat", "ELLSM"),
    885580: ("damaraland_mole_rat", "ELLSM"),
    1026970: ("blind_mole_rat", "ELLSM"),
    59463: ("myotis_lucifugus", "ELLSM"),
    59479: ("greater_horseshoe_bat", "ELLSM"),
    # long-lived, large-bodied
    9785: ("elephant", "BMAL"),
    9771: ("blue_whale", "BMAL"),
    9749: ("beluga", "BMAL"),
    9755: ("sperm_whale", "BMAL"),
    73337: ("white_rhino", "BMAL"),
    # typical-lifespan references
    10090: ("mouse", "REFERENCE"),
    10116: ("rat", "REFERENCE"),
    10036: ("hamster", "REFERENCE"),
    10141: ("guinea_pig", "REFERENCE"),
    9544: ("rhesus", "REFERENCE"),
    9940: ("sheep", "REFERENCE"),
    13616: ("opossum", "REFERENCE"),
    9615: ("dog", "REFERENCE"),
    30608: ("mouse_lemur", "REFERENCE"),
    43179: ("ground_squirrel", "REFERENCE"),
    9365: ("hedgehog", "REFERENCE"),
    9685: ("cat", "REFERENCE"),
}

STOP = {"TAA", "TAG", "TGA"}


def http_get(url: str, tries: int = 4, pause: float = 0.34) -> str:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": f"{TOOL} ({EMAIL})", "Accept": "*/*"}
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
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


def parse_fasta_single(text: str) -> tuple[str, str]:
    """Return (header_line, sequence) for the first record in a FASTA payload."""
    header, seq = "", []
    for line in text.splitlines():
        if line.startswith(">"):
            if header:
                break
            header = line[1:]
        elif line.strip():
            seq.append(line.strip())
    return header, "".join(seq).upper().replace("U", "T")


def parse_cds_fasta(text: str) -> list[tuple[dict[str, str], str]]:
    """Parse an efetch fasta_cds_na payload into [(header_tags, ntseq), ...]."""
    out: list[tuple[dict[str, str], str]] = []
    header: dict[str, str] | None = None
    seq: list[str] = []
    for line in text.splitlines():
        if line.startswith(">"):
            if header is not None:
                out.append((header, "".join(seq).upper().replace("U", "T")))
            tags = dict(re.findall(r"\[(\w+)=([^\]]*)\]", line))
            tags["_raw"] = line
            header, seq = tags, []
        elif line.strip():
            seq.append(line.strip())
    if header is not None:
        out.append((header, "".join(seq).upper().replace("U", "T")))
    return out


def cds_is_valid(cds: str) -> bool:
    if len(cds) < 90 or len(cds) % 3 != 0:
        return False
    if cds[:3] != "ATG" or cds[-3:] not in STOP:
        return False
    # no internal stop codon
    for i in range(0, len(cds) - 3, 3):
        if cds[i : i + 3] in STOP:
            return False
    return set(cds) <= set("ACGTN")


def refseqrna_ids(gene_id: str) -> list[str]:
    for lname in ("gene_nuccore_refseqrna", "gene_nuccore_mrna", "gene_nuccore"):
        el = http_get(
            ncbi_url("elink.fcgi", dbfrom="gene", db="nuccore", id=gene_id, linkname=lname)
        )
        time.sleep(0.34)
        ids = re.findall(r"<Link>\s*<Id>(\d+)</Id>", el)
        if ids:
            return ids
    return []


def utrs_from_transcript(nuccore_id: str) -> tuple[str, str, str, str] | None:
    """Return (accession, cds, utr5, utr3) for a transcript, or None if unusable."""
    full_txt = http_get(
        ncbi_url("efetch.fcgi", db="nuccore", id=nuccore_id, rettype="fasta", retmode="text")
    )
    time.sleep(0.34)
    header, mrna = parse_fasta_single(full_txt)
    accession = header.split()[0] if header else nuccore_id
    if not mrna or set(mrna) - set("ACGTN"):
        return None
    cds_txt = http_get(
        ncbi_url(
            "efetch.fcgi", db="nuccore", id=nuccore_id,
            rettype="fasta_cds_na", retmode="text",
        )
    )
    time.sleep(0.34)
    best: tuple[str, str, str, str] | None = None
    for _tags, cds in parse_cds_fasta(cds_txt):
        if not cds_is_valid(cds):
            continue
        idx = mrna.find(cds)
        if idx < 0:
            continue
        utr5, utr3 = mrna[:idx], mrna[idx + len(cds) :]
        if best is None or len(cds) > len(best[1]):
            best = (accession, cds, utr5, utr3)
    return best


def resolve_gene(gene: str, taxid: int) -> tuple[str, str, str, str] | None:
    term = f"{gene}[Gene Name] AND txid{taxid}[Organism]"
    xml = http_get(ncbi_url("esearch.fcgi", db="gene", term=term, retmax="5"))
    time.sleep(0.34)
    gene_ids = re.findall(r"<Id>(\d+)</Id>", xml)
    best: tuple[str, str, str, str] | None = None
    best_key = (-1, -1)  # (prefer NM_, cds_len)
    for gid in gene_ids[:3]:
        for nid in refseqrna_ids(gid)[:4]:
            try:
                res = utrs_from_transcript(nid)
            except Exception:  # noqa: BLE001
                continue
            if res is None:
                continue
            acc, cds, _u5, _u3 = res
            key = (1 if acc.startswith("NM_") else 0, len(cds))
            if key > best_key:
                best, best_key = res, key
        if best is not None and best[0].startswith("NM_"):
            break
    return best


def fasta_block(header: str, seq: str, width: int = 60) -> str:
    lines = [f">{header}"]
    for i in range(0, len(seq), width):
        lines.append(seq[i : i + width])
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genes", default=",".join(DEFAULT_GENES), help="comma-separated symbols")
    ap.add_argument("--only", default="", help="comma-separated taxids to restrict to")
    args = ap.parse_args()

    genes = [g.strip() for g in args.genes.split(",") if g.strip()]
    only = {int(x) for x in args.only.split(",") if x.strip()}
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report: list[tuple] = []
    for gene in genes:
        u5_blocks: list[str] = []
        u3_blocks: list[str] = []
        for taxid, (name, group) in TAXA.items():
            if only and taxid not in only:
                continue
            try:
                res = resolve_gene(gene, taxid)
            except Exception as exc:  # noqa: BLE001
                res = None
                note = f"ERROR:{exc}"
            else:
                note = ""
            if res is None:
                report.append((gene, taxid, name, group, "", 0, 0, "FAIL", note))
                print(f"[{gene:7s} {name:20s}] FAIL {note}", flush=True)
                continue
            acc, _cds, u5, u3 = res
            if u5:
                u5_blocks.append(fasta_block(f"{taxid}|{name}|{group}", u5))
            if u3:
                u3_blocks.append(fasta_block(f"{taxid}|{name}|{group}", u3))
            status = "OK" if (u5 and u3) else ("UTR5_ONLY" if u5 else "UTR3_ONLY" if u3 else "NO_UTR")
            report.append((gene, taxid, name, group, acc, len(u5), len(u3), status, note))
            print(f"[{gene:7s} {name:20s}] {status:9s} {acc} 5'={len(u5)} 3'={len(u3)}", flush=True)
        if u5_blocks:
            (OUT_DIR / f"{gene}_utr5.fasta").write_text("\n".join(u5_blocks) + "\n")
        if u3_blocks:
            (OUT_DIR / f"{gene}_utr3.fasta").write_text("\n".join(u3_blocks) + "\n")

    rep_path = OUT_DIR / "utr_coverage.tsv"
    with open(rep_path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["gene", "taxid", "name", "group", "accession",
                    "utr5_len", "utr3_len", "status", "note"])
        w.writerows(report)

    ok = sum(1 for r in report if r[7] == "OK")
    print(f"\n=== {ok}/{len(report)} (gene,species) pairs with BOTH UTRs ===", file=sys.stderr)
    print(f"Coverage: {rep_path}", file=sys.stderr)
    print("Paste the coverage table back to continue.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
