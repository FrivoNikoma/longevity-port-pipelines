#!/usr/bin/env python3
"""Fetch coding (CDS) nucleotide sequences for Ku80 (XRCC5, human P13010) orthologs.

Reads data/output/ortholog_coverage.csv, keeps rows whose source_uniprot is P13010,
and resolves a CDS for each target accession from its native database:

  * Ensembl protein IDs (ENS...P...) -> Ensembl REST (lookup transcript, fetch CDS)
  * RefSeq protein IDs (XP_/NP_...)  -> NCBI E-utilities (elink to mRNA, fetch CDS)
  * UniProt accessions / entry names -> UniProt REST (.txt cross-refs) -> NCBI/EMBL CDS

Every candidate CDS is translated and compared to the stored protein; the best match
is kept. Outputs:

  data/interim/ku80/ku80_cds.fasta          (headers: >{taxid}|{name}|{group}|{acc})
  data/interim/ku80/ku80_cds_coverage.tsv   (per-species resolution report)

Pure standard library (urllib) -- no third-party deps. Network runs on YOUR machine.

Usage:
    uv run python scripts/fetch_ku80_cds.py
    uv run python scripts/fetch_ku80_cds.py --only 10181,9771   # test a couple taxids
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COVERAGE_CSV = REPO / "data" / "output" / "ortholog_coverage.csv"
OUT_DIR = REPO / "data" / "interim" / "ku80"
SOURCE_UNIPROT = "P13010"  # human Ku80 / XRCC5
EMAIL = "nikomafrivo@gmail.com"
TOOL = "longevity-port-pipelines-ku80-cds"

# taxid -> (species_name, group).  Groups: ELLSM / BMAL / REFERENCE.  Human is the anchor.
TAXA = {
    9606: ("human", "REFERENCE"),
    # ELLSM (small-bodied long-lived)
    10181: ("naked_mole_rat", "ELLSM"),
    885580: ("damaraland_mole_rat", "ELLSM"),
    1026970: ("blind_mole_rat", "ELLSM"),
    59463: ("myotis_lucifugus", "ELLSM"),
    59479: ("greater_horseshoe_bat", "ELLSM"),
    # BMAL (large-bodied long-lived)
    9785: ("elephant", "BMAL"),
    9771: ("blue_whale", "BMAL"),
    9749: ("beluga", "BMAL"),
    9755: ("sperm_whale", "BMAL"),
    73337: ("white_rhino", "BMAL"),
    # REFERENCE (typical lifespan)
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

CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L", "CTT": "L", "CTC": "L",
    "CTA": "L", "CTG": "L", "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V", "TCT": "S", "TCC": "S",
    "TCA": "S", "TCG": "S", "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T", "GCT": "A", "GCC": "A",
    "GCA": "A", "GCG": "A", "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q", "AAT": "N", "AAC": "N",
    "AAA": "K", "AAG": "K", "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W", "CGT": "R", "CGC": "R",
    "CGA": "R", "CGG": "R", "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def translate(nt: str) -> str:
    nt = nt.upper().replace("U", "T")
    aa = []
    for i in range(0, len(nt) - 2, 3):
        aa.append(CODON_TABLE.get(nt[i : i + 3], "X"))
    return "".join(aa)


def kmers(s: str, k: int = 7) -> set[str]:
    s = s.rstrip("*")
    return {s[i : i + k] for i in range(len(s) - k + 1)} if len(s) >= k else {s}


def verify(stored: str, nt: str) -> float:
    """Containment of the stored protein's k-mers within translate(nt).

    Robust to truncation / N-terminal offset (stored may be a partial OMA fragment),
    unlike a positional identity. Returns 0..1.
    """
    trans = translate(nt).rstrip("*")
    if not stored:  # no reference protein (e.g. human anchor if UniProt fetch failed)
        return 1.0 if (len(trans) > 600 and trans.startswith("M")) else 0.0
    ks = kmers(stored)
    if not ks:
        return 0.0
    tk = kmers(trans)
    return len(ks & tk) / len(ks)


ACCEPT = 0.5  # min k-mer containment to accept a CDS


def http_get(url: str, tries: int = 4, pause: float = 0.34) -> str:
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": f"{TOOL} ({EMAIL})", "Accept": "*/*"},
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(pause * (attempt + 1) * 2)
    raise RuntimeError(f"GET failed after {tries} tries: {url}\n  {last}")


# --------------------------------------------------------------------------- NCBI
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def ncbi_url(endpoint: str, **params: str) -> str:
    params.setdefault("tool", TOOL)
    params.setdefault("email", EMAIL)
    return f"{NCBI}/{endpoint}?" + urllib.parse.urlencode(params)


def parse_cds_fasta(text: str) -> list[tuple[dict, str]]:
    """Parse an efetch fasta_cds_na payload into [(header_tags, ntseq), ...]."""
    out = []
    header, seq = None, []
    for line in text.splitlines():
        if line.startswith(">"):
            if header is not None:
                out.append((header, "".join(seq)))
            tags = dict(re.findall(r"\[(\w+)=([^\]]*)\]", line))
            tags["_raw"] = line
            header, seq = tags, []
        elif line.strip():
            seq.append(line.strip())
    if header is not None:
        out.append((header, "".join(seq)))
    return out


def ncbi_cds_from_nuccore(nuccore_id: str, want_protein: str, stored: str):
    text = http_get(
        ncbi_url("efetch.fcgi", db="nuccore", id=nuccore_id,
                 rettype="fasta_cds_na", retmode="text")
    )
    time.sleep(0.34)
    best, best_id = None, -1.0
    for tags, seq in parse_cds_fasta(text):
        idv = verify(stored, seq)
        # nudge toward the CDS whose protein_id matches the requested accession
        stem = want_protein.split(".")[0] if want_protein else ""
        pref = idv + (0.001 if stem and tags.get("protein_id", "").startswith(stem) else 0.0)
        if pref > best_id:
            best, best_id = seq, idv
    return best, best_id


def resolve_by_gene_taxid(taxid: int, stored: str, symbol: str = "XRCC5"):
    """Primary route: NCBI Gene ortholog for `symbol` in `taxid` -> RefSeq mRNA -> CDS.

    Robust to rotted/deleted UniProt accessions, and uniform across species.
    """
    term = f"{symbol}[Gene Name] AND txid{taxid}[Organism]"
    xml = http_get(ncbi_url("esearch.fcgi", db="gene", term=term, retmax="5"))
    time.sleep(0.34)
    gids = re.findall(r"<Id>(\d+)</Id>", xml)
    best = (None, 0.0, f"gene:{taxid}:none")
    for gid in gids[:3]:
        mids = []
        for lname in ("gene_nuccore_refseqrna", "gene_nuccore_mrna", "gene_nuccore"):
            el = http_get(ncbi_url("elink.fcgi", dbfrom="gene", db="nuccore",
                                   id=gid, linkname=lname))
            time.sleep(0.34)
            mids = re.findall(r"<Link>\s*<Id>(\d+)</Id>", el)
            if mids:
                break
        for mid in mids[:4]:
            seq, idv = ncbi_cds_from_nuccore(mid, "", stored)
            if seq and idv >= ACCEPT and len(seq) % 3 == 0:
                return seq, idv, f"gene:{gid}:nuccore:{mid}"
            if seq and idv > best[1]:
                best = (seq, idv, f"gene:{gid}:nuccore:{mid}(low)")
    return best


def resolve_refseq_protein(xp_acc: str, stored: str):
    # protein -> mRNA
    xml = http_get(ncbi_url("elink.fcgi", dbfrom="protein", db="nuccore",
                            id=xp_acc, linkname="protein_nuccore_mrna"))
    time.sleep(0.34)
    ids = re.findall(r"<Link>\s*<Id>(\d+)</Id>", xml)
    if not ids:
        # fall back to any protein_nuccore link (genomic/refseq)
        xml = http_get(ncbi_url("elink.fcgi", dbfrom="protein", db="nuccore",
                                id=xp_acc, linkname="protein_nuccore"))
        time.sleep(0.34)
        ids = re.findall(r"<Link>\s*<Id>(\d+)</Id>", xml)
    best = (None, 0.0, "refseq:none")
    for nid in ids[:3]:
        seq, idv = ncbi_cds_from_nuccore(nid, xp_acc, stored)
        if seq and idv >= ACCEPT:
            return seq, idv, f"refseq:{nid}"
        if seq and idv > best[1]:
            best = (seq, idv, f"refseq:{nid}(low)")
    return best


# ------------------------------------------------------------------------- Ensembl
ENSEMBL = "https://rest.ensembl.org"


def resolve_ensembl(ensp: str, stored: str):
    base = ensp.split(".")[0]
    j = json.loads(http_get(f"{ENSEMBL}/lookup/id/{base}?content-type=application/json"))
    time.sleep(0.2)
    transcript = j.get("Parent")
    if not transcript:
        return None, 0.0, "ensembl:no-parent"
    fa = http_get(f"{ENSEMBL}/sequence/id/{transcript}?type=cds;content-type=text/x-fasta")
    time.sleep(0.2)
    seq = "".join(ln.strip() for ln in fa.splitlines() if not ln.startswith(">"))
    if seq and set(seq.upper()) <= set("ACGTN"):
        return seq, verify(stored, seq), f"ensembl:{transcript}"
    return None, 0.0, "ensembl:not-nt"


# ------------------------------------------------------------------------- UniProt
UNIPROT = "https://rest.uniprot.org"


def uniprot_accession(token: str) -> str:
    if "_" in token:  # entry name like XRCC5_MOUSE
        tsv = http_get(f"{UNIPROT}/uniprotkb/search?query=id:{token}&fields=accession&format=tsv")
        lines = [ln for ln in tsv.splitlines() if ln.strip()]
        return lines[1].strip() if len(lines) > 1 else token
    return token


def ncbi_protein_query_to_cds(query: str, stored: str):
    """Fallback: find the NCBI protein mirroring a UniProt accession, then its CDS."""
    xml = http_get(ncbi_url("esearch.fcgi", db="protein", term=query, retmax="5"))
    time.sleep(0.34)
    ids = re.findall(r"<Id>(\d+)</Id>", xml)
    best = (None, 0.0, "npsearch:none")
    for pid in ids[:5]:
        try:
            seq, idv, note = resolve_refseq_protein(pid, stored)
        except Exception:  # noqa: BLE001
            continue
        if seq and idv >= ACCEPT:
            return seq, idv, f"npsearch->{note}"
        if seq and idv > best[1]:
            best = (seq, idv, f"npsearch->{note}(low)")
    return best


def _uniprot_xrefs(acc: str):
    raw = http_get(f"{UNIPROT}/uniprotkb/{acc}.json")
    time.sleep(0.2)
    try:
        data = json.loads(raw)
    except Exception:  # noqa: BLE001
        data = {}
    return data, raw


def resolve_uniprot(token: str, stored: str, debug: bool = False):
    acc = uniprot_accession(token)
    data, raw = _uniprot_xrefs(acc)
    # follow one merge/demerge hop for inactive entries
    inact = data.get("inactiveReason")
    if inact:
        cand = inact.get("mergedInto")
        if isinstance(cand, list):
            cand = cand[0] if cand else None
        if not cand:
            dl = inact.get("mergeDemergeTo") or []
            cand = dl[0] if dl else None
        if cand:
            if debug:
                print(f"      inactive {acc} -> follow {cand}", flush=True)
            acc = cand
            data, raw = _uniprot_xrefs(acc)
    refseq_mrna, refseq_prot, embl = [], [], []
    for x in data.get("uniProtKBCrossReferences", []):
        db, xid = x.get("database"), x.get("id", "")
        props = {p.get("key"): p.get("value") for p in x.get("properties", [])}
        if db == "RefSeq":
            if xid:
                refseq_prot.append(xid)
            nt = props.get("NucleotideSequenceId", "")
            if nt:
                refseq_mrna.append(nt)
        elif db == "EMBL":
            if xid:
                embl.append((xid, props.get("ProteinId", "")))  # (nt_acc, protein_id)
    if debug:
        head = raw[:180].replace("\n", " ") if len(raw) < 400 else ""
        print(f"      raw_len={len(raw)} RefSeq_mRNA={refseq_mrna} "
              f"RefSeq_prot={refseq_prot} EMBL={embl[:6]} {head}", flush=True)
    best = (None, 0.0, f"uniprot:{acc}:none")
    # 1) RefSeq mRNA -> CDS (most reliable)
    for xm in refseq_mrna[:4]:
        seq, idv = ncbi_cds_from_nuccore(xm, "", stored)
        if seq and idv >= ACCEPT:
            return seq, idv, f"uniprot->refseq_mrna:{xm}"
        if seq and idv > best[1]:
            best = (seq, idv, f"uniprot->refseq_mrna:{xm}(low)")
    # 2) RefSeq protein -> linked mRNA -> CDS
    for xp in refseq_prot[:3]:
        try:
            seq, idv, note = resolve_refseq_protein(xp, stored)
        except Exception:  # noqa: BLE001
            continue
        if seq and idv >= ACCEPT:
            return seq, idv, f"uniprot->{note}"
        if seq and idv > best[1]:
            best = (seq, idv, f"uniprot->{note}(low)")
    # 3) EMBL nucleotide entries -> CDS (match by protein_id)
    for nt_acc, prot_id in embl[:6]:
        try:
            seq, idv = ncbi_cds_from_nuccore(nt_acc, prot_id, stored)
        except Exception:  # noqa: BLE001
            continue
        if seq and idv >= ACCEPT:
            return seq, idv, f"uniprot->embl:{nt_acc}"
        if seq and idv > best[1]:
            best = (seq, idv, f"uniprot->embl:{nt_acc}(low)")
    # 4) last resort: search NCBI protein for a mirror of this accession
    for q in {token, acc}:
        try:
            seq, idv, note = ncbi_protein_query_to_cds(q, stored)
        except Exception:  # noqa: BLE001
            continue
        if seq and idv >= ACCEPT:
            return seq, idv, note
        if seq and idv > best[1]:
            best = (seq, idv, note)
    return best


# --------------------------------------------------------------------------- main
def classify(acc: str) -> str:
    if re.match(r"^ENS[A-Z]*P\d", acc):
        return "ensembl"
    if re.match(r"^[NX]P_\d", acc):
        return "refseq"
    return "uniprot"


def load_targets():
    rows = []
    with open(COVERAGE_CSV, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["source_uniprot"] != SOURCE_UNIPROT:
                continue
            rows.append((int(r["target_species_taxid"]), r["target_uniprot"], r["target_sequence"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated taxids to restrict to")
    ap.add_argument("--debug", action="store_true", help="print resolved xref candidates")
    args = ap.parse_args()
    only = {int(x) for x in args.only.split(",") if x.strip()}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = load_targets()

    # human anchor: pull canonical protein from UniProt so we can verify its own CDS
    human_prot = ""
    try:
        fa = http_get(f"{UNIPROT}/uniprotkb/{SOURCE_UNIPROT}.fasta")
        human_prot = "".join(ln.strip() for ln in fa.splitlines() if not ln.startswith(">"))
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: could not fetch human protein: {exc}", file=sys.stderr)
    targets = [(9606, SOURCE_UNIPROT, human_prot)] + targets

    fasta_lines, report = [], []
    for taxid, acc, stored in targets:
        if only and taxid not in only:
            continue
        name, group = TAXA.get(taxid, (f"tax{taxid}", "UNKNOWN"))
        kind = classify(acc)
        print(f"[{name:22s} tax={taxid:<8d} {kind:8s}] {acc} ...", flush=True)
        seq, idv, note = None, 0.0, ""
        # primary: NCBI Gene by taxid (uniform, resilient to rotted accessions)
        try:
            seq, idv, note = resolve_by_gene_taxid(taxid, stored)
        except Exception as exc:  # noqa: BLE001
            note = f"gene-ERROR:{exc}"
        # fallback: native accession route, if gene route under threshold
        if not (seq and idv >= ACCEPT):
            try:
                if kind == "ensembl":
                    s2, i2, n2 = resolve_ensembl(acc, stored)
                elif kind == "refseq":
                    s2, i2, n2 = resolve_refseq_protein(acc, stored)
                else:
                    s2, i2, n2 = resolve_uniprot(acc, stored, debug=args.debug)
                if i2 > idv:
                    seq, idv, note = s2, i2, n2
            except Exception as exc:  # noqa: BLE001
                note = f"{note}|acc-ERROR:{exc}"
        status = "OK" if (seq and idv >= ACCEPT and len(seq) % 3 == 0) else (
            "LOW_ID" if seq else "FAIL")
        report.append((taxid, name, group, acc, kind, note,
                       len(seq) if seq else 0, len(stored), round(idv, 4), status))
        print(f"    -> {status} id={idv:.3f} cds_len={len(seq) if seq else 0} ({note})", flush=True)
        if seq and status == "OK":
            fasta_lines.append(f">{taxid}|{name}|{group}|{acc}")
            for i in range(0, len(seq), 60):
                fasta_lines.append(seq[i : i + 60])

    fasta_path = OUT_DIR / "ku80_cds.fasta"
    fasta_path.write_text("\n".join(fasta_lines) + "\n")
    rep_path = OUT_DIR / "ku80_cds_coverage.tsv"
    with open(rep_path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["taxid", "name", "group", "accession", "kind", "note",
                    "cds_len", "prot_len", "identity", "status"])
        w.writerows(report)

    ok = sum(1 for r in report if r[-1] == "OK")
    print(f"\n=== {ok}/{len(report)} sequences OK ===")
    by_group = {}
    for r in report:
        by_group.setdefault(r[2], [0, 0])
        by_group[r[2]][1] += 1
        if r[-1] == "OK":
            by_group[r[2]][0] += 1
    for g, (o, t) in sorted(by_group.items()):
        print(f"  {g:10s} {o}/{t} OK")
    print(f"\nFASTA:  {fasta_path}")
    print(f"Report: {rep_path}")
    print("\nPaste the report contents back to continue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
