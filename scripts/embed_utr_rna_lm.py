#!/usr/bin/env python3
"""Embed extended-panel UTRs with an RNA (or DNA) language model.

This is the re-test of the project's AI regulatory arc. The earlier DNA-LM attempt
(`scripts/embed_utr_dna_lm.py` + `analyze_utr_embedding_divergence.py`) returned a null,
but it was run in a regime where the *classical* signal was also undetectable: n = 22
species on a hand-built tree, whole-UTR mean pooling, a genome-generic model. The power
calibration later showed n = 22 sits exactly at the detection floor, and the positional
map showed the real signal lives in the **proximal** 3' UTR. So that null confounds three
things: sample size, model domain, and window.

This script fixes all three inputs at once:

  * **Panel**  - the 57-species extended panel (`data/interim/utr_panel/`), not the n = 22 lane set.
  * **Model**  - RNA / 3'UTR-domain language models via `multimolecule`, with the old
    Nucleotide Transformer kept as an explicit control backend.
  * **Window** - every sequence is embedded twice, over the full UTR and over the
    proximal fraction (default first 38 %, where the classical signal is concentrated).

Models (``--model``)::

    multimolecule/utrbert-3mer   3UTRBERT, pretrained on human 3' UTRs   (default; domain match)
    multimolecule/rinalmo        RiNALMo 650M, general RNA               (large, slow on CPU)
    multimolecule/rinalmo-mega   RiNALMo 150M, general RNA
    multimolecule/utrlm-te_el    UTR-LM, pretrained on 5' UTRs           (domain-mismatch control)
    InstaDeepAI/nucleotide-transformer-v2-50m-multi-species   (--backend dna; the old null)

torch / transformers / multimolecule are intentionally NOT project dependencies (they would
bloat the locked env and CI). Run with an ephemeral environment.

**Use ``--no-project``.** The project lock pins ``transformers`` to a 4.57.6 git fork (an
``esm`` dependency), while ``multimolecule`` calls ``transformers.initialization``, which
only exists in transformers >= 5. A plain ``uv run --with multimolecule`` inherits the
locked 4.57.6 and fails at import; ``--no-project`` builds the ephemeral environment
without the project, so transformers resolves to 5.x. This script imports nothing from
``src/``, so dropping the project costs nothing::

    uv run --no-project --with torch --with transformers --with multimolecule --with numpy \
        python scripts/embed_utr_rna_lm.py --region utr3
The ``--backend dna`` control is deliberately run *without* ``--no-project``, i.e. against
the project's pinned transformers 4.57.6, because that is the environment the original NT
null was produced in. A control should reproduce the old setup, not a new one::

    uv run --with torch --with transformers --with numpy \
        python scripts/embed_utr_rna_lm.py --region utr3 --backend dna \
        --model InstaDeepAI/nucleotide-transformer-v2-50m-multi-species

Inputs:  data/interim/utr_panel/{GENE}_{region}.fasta  (+ human reference, see human_ref)
Outputs: data/interim/utr_panel_emb/{model_slug}/{GENE}_{region}.npz
             arrays keyed "{species}|full" and "{species}|prox"
         data/interim/utr_panel_emb/{model_slug}/coverage.tsv
Resumable: a gene/region whose .npz already covers every input species is skipped.
No Biohub credits are used.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent
UTR_DIR = REPO / "data" / "interim" / "utr_panel"
HUMAN_DIR = REPO / "data" / "interim" / "utr"  # original fetch holds the human reference
OUT_ROOT = REPO / "data" / "interim" / "utr_panel_emb"

DEFAULT_MODEL = "multimolecule/utrbert-3mer"
PROXIMAL_FRAC = 0.38  # first 38 % of the 3' UTR - where the positional map put the signal
MIN_PROX_NT = 60  # do not shrink very short UTRs (CDC20 has a ~68 nt 3' UTR) below this


def model_slug(model: str) -> str:
    return model.replace("/", "__")


def load_fasta(path: Path) -> dict[str, str]:
    """Read a panel UTR fasta. Headers are ``>{taxid}|{short_name}|{clade}``."""
    seqs: dict[str, str] = {}
    name: str | None = None
    buf: list[str] = []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if name is not None:
                seqs[name] = "".join(buf)
            parts = line[1:].split("|")
            name = parts[1] if len(parts) > 1 else parts[0]
            buf = []
        elif line.strip():
            buf.append(line.strip())
    if name is not None:
        seqs[name] = "".join(buf)
    return seqs


def human_ref(gene: str, region: str) -> str | None:
    """Human reference sequence, preferring the copy inside the panel fasta."""
    for base in (UTR_DIR, HUMAN_DIR):
        fp = base / f"{gene}_{region}.fasta"
        if fp.exists():
            h = load_fasta(fp).get("human")
            if h:
                return h
    return None


def windows(seq: str, max_nt: int, frac: float) -> dict[str, str]:
    """Full and proximal views of one UTR.

    Deliberately NOT truncated to the model context. 3UTRBERT caps at 510 tokens (~512 nt
    for its 3-mer tokenizer); truncating there would silently destroy the window contrast,
    because for any UTR longer than ~1350 nt the proximal 38 % already exceeds the cap and
    'prox' and 'full' would become the same first-512-nt string. On the cell-cycle module
    that collapse hits 28 % of sequences. Long inputs are instead chunked and length-weighted
    mean-pooled (see embed_sequences), so each window is a genuine representation of its
    region at any length.
    """
    cut = max(MIN_PROX_NT, int(round(len(seq) * frac)))
    full, prox = seq, seq[:cut]
    if max_nt > 0:  # optional hard cap, off by default
        full, prox = full[:max_nt], prox[:max_nt]
    return {"full": full, "prox": prox}


def chunk(seq: str, size: int) -> list[str]:
    return [seq[i : i + size] for i in range(0, len(seq), size)] or [seq]


def tokens_per_nt(tok, probe: int = 600) -> float:
    """Empirical token/nucleotide ratio (3-mer stride-1 ~ 1.0; NT 6-mer ~ 0.17)."""
    enc = tok(["A" * probe], return_tensors=None)
    ids = enc["input_ids"]
    n = len(ids[0]) if isinstance(ids[0], list) else len(ids)
    return max(n / probe, 1e-3)


def clean(seq: str, rna: bool) -> str:
    alphabet = set("ACGU") if rna else set("ACGT")
    src = seq.upper().replace("T", "U") if rna else seq.upper().replace("U", "T")
    return "".join(c if c in alphabet else "N" for c in src)


def build_model(model: str, backend: str):
    """Return (tokenizer, torch_model, torch). Imported lazily: heavy, non-project deps."""
    import torch
    from transformers import AutoModel, AutoModelForMaskedLM, AutoTokenizer

    if backend == "rna":
        try:
            import multimolecule  # noqa: F401  (registers the RNA architectures)
            from multimolecule import RnaTokenizer
        except ImportError:  # pragma: no cover - user-environment guidance
            print(
                "error: --backend rna needs 'multimolecule' AND transformers >= 5.\n"
                "       The project lock pins transformers 4.57.6 (an esm dependency), so run\n"
                "       the ephemeral environment WITHOUT the project:\n"
                "       uv run --no-project --with torch --with transformers "
                "--with multimolecule --with numpy python scripts/embed_utr_rna_lm.py ...",
                file=sys.stderr,
            )
            raise
        tok = RnaTokenizer.from_pretrained(model)
        net = AutoModel.from_pretrained(model, trust_remote_code=True)
        net.eval()
        return tok, net, torch, False

    tok = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    # Nucleotide Transformer v2 uses a gated MLP, and its custom architecture is exposed
    # through the checkpoint's auto_map for AutoModelForMaskedLM *only*. A plain AutoModel
    # silently falls back to the native ESM class and dies with a 4096-vs-2048 shape
    # mismatch on the intermediate weight. This mirrors the loader of the original NT arc
    # (scripts/embed_utr_dna_lm.py), which is the point: the control has to reproduce the
    # old null's setup, not a new one.
    net = AutoModelForMaskedLM.from_pretrained(model, trust_remote_code=True)
    net.eval()
    return tok, net, torch, True


def context_limit(net, requested: int) -> int:
    """Clamp the requested context to what the checkpoint's position embeddings allow."""
    limit = getattr(net.config, "max_position_embeddings", None)
    if not isinstance(limit, int) or limit <= 0:
        return requested
    # BERT-style checkpoints spend positions on [CLS]/[SEP]; leave a small margin.
    return min(requested, max(16, limit - 2))


def embed_batch(seqs: list[str], tok, net, torch, max_tokens: int, mlm: bool) -> np.ndarray:
    """Attention-mask-weighted mean of the final hidden states, one row per sequence."""
    enc = tok(
        seqs,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_tokens,
    )
    kwargs = {"output_hidden_states": True} if mlm else {}
    with torch.no_grad():
        try:
            out = net(**enc, **kwargs)
        except TypeError:  # model does not accept every field the tokenizer emits
            out = net(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                      **kwargs)
    # a MaskedLM head has no last_hidden_state; take the final hidden layer instead
    hidden = out.hidden_states[-1] if mlm else out.last_hidden_state  # (B, T, D)
    mask = enc["attention_mask"].unsqueeze(-1).to(hidden.dtype)
    pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
    return pooled.cpu().numpy().astype(np.float32)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--backend", choices=["rna", "dna"], default="rna")
    ap.add_argument("--region", choices=["utr3", "utr5", "both"], default="utr3")
    ap.add_argument("--genes", default="", help="comma-separated subset (default: all)")
    ap.add_argument("--max-nt", type=int, default=0,
                    help="optional hard cap in nucleotides (0 = no cap; long inputs are "
                         "chunked and length-weighted mean-pooled instead of truncated)")
    ap.add_argument("--max-tokens", type=int, default=1024, help="model context in tokens")
    ap.add_argument("--proximal-frac", type=float, default=PROXIMAL_FRAC)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--force", action="store_true", help="recompute genes that are already done")
    args = ap.parse_args()

    out_dir = OUT_ROOT / model_slug(args.model)
    out_dir.mkdir(parents=True, exist_ok=True)
    regions = ["utr3", "utr5"] if args.region == "both" else [args.region]
    want_genes = {g.strip() for g in args.genes.split(",") if g.strip()}

    jobs: list[tuple[str, str, Path]] = []
    for region in regions:
        for fp in sorted(UTR_DIR.glob(f"*_{region}.fasta")):
            gene = fp.name.replace(f"_{region}.fasta", "")
            if want_genes and gene not in want_genes:
                continue
            jobs.append((gene, region, fp))
    if not jobs:
        print(f"no input fastas in {UTR_DIR}", file=sys.stderr)
        return 1

    tok = net = torch = None  # built lazily, so --force-free reruns cost nothing
    mlm = False
    chunk_nt = 512  # replaced with the tokenizer-derived value once the model is loaded
    rows: list[tuple[str, str, int, int]] = []

    for gene, region, fp in jobs:
        dest = out_dir / f"{gene}_{region}.npz"
        seqs = load_fasta(fp)
        href = human_ref(gene, region)
        if href:
            seqs["human"] = href
        seqs = {s: q for s, q in seqs.items() if len(q) >= 20}
        if not seqs:
            print(f"  {gene:10s} {region}  skip (no usable sequences)")
            continue
        if dest.exists() and not args.force:
            have = set(np.load(dest).files)
            if all(f"{s}|full" in have for s in seqs):
                print(f"  {gene:10s} {region}  cached ({len(seqs)} species)")
                rows.append((gene, region, len(seqs), 1))
                continue

        if net is None:
            print(f"loading {args.model} (backend={args.backend}) ...", flush=True)
            tok, net, torch, mlm = build_model(args.model, args.backend)
            capped = context_limit(net, args.max_tokens)
            if capped != args.max_tokens:
                print(f"  context clamped to the checkpoint limit: {capped} tokens")
                args.max_tokens = capped
            ratio = tokens_per_nt(tok)
            chunk_nt = max(MIN_PROX_NT, int((args.max_tokens - 2) / ratio))
            print(f"  {ratio:.2f} tokens/nt -> chunking at {chunk_nt} nt, "
                  f"length-weighted mean pooling over chunks")

        keys: list[str] = []
        payload: list[str] = []
        owner: list[int] = []
        weight: list[int] = []
        for sp, raw in seqs.items():
            for win, sub in windows(raw, args.max_nt, args.proximal_frac).items():
                idx = len(keys)
                keys.append(f"{sp}|{win}")
                for piece in chunk(clean(sub, rna=args.backend == "rna"), chunk_nt):
                    payload.append(piece)
                    owner.append(idx)
                    weight.append(len(piece))

        vecs: list[np.ndarray] = []
        for i in range(0, len(payload), args.batch_size):
            vecs.append(
                embed_batch(payload[i : i + args.batch_size], tok, net, torch,
                            args.max_tokens, mlm)
            )
        mat = np.vstack(vecs)

        # length-weighted mean over the chunks of each window
        dim = mat.shape[1]
        acc = np.zeros((len(keys), dim), dtype=np.float64)
        wsum = np.zeros(len(keys), dtype=np.float64)
        for i, (o, w) in enumerate(zip(owner, weight, strict=True)):
            acc[o] += mat[i] * w
            wsum[o] += w
        pooled = (acc / np.maximum(wsum, 1.0)[:, None]).astype(np.float32)

        np.savez_compressed(dest, **{k: pooled[i] for i, k in enumerate(keys)})
        extra = f"  chunks={len(payload)}" if len(payload) > len(keys) else ""
        print(f"  {gene:10s} {region}  embedded {len(seqs)} species  dim={dim}{extra}",
              flush=True)
        rows.append((gene, region, len(seqs), 0))

    cov = out_dir / "coverage.tsv"
    with open(cov, "w", encoding="utf-8") as fh:
        fh.write("gene\tregion\tn_species\tcached\n")
        for gene, region, n, cached in rows:
            fh.write(f"{gene}\t{region}\t{n}\t{cached}\n")
    print(f"\nwrote {len(rows)} gene/region embeddings -> {out_dir}")
    print(f"coverage -> {cov}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
