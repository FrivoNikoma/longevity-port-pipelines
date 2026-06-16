# Resources to validate — freshness-checked June 2026

Versions verified current as of June 2026. Where I was wrong before, it's marked [CORRECTED].

## 0. SKIP-THE-ETL OPTION (check these FIRST)

**Synthyra/PINDER** (HuggingFace) — https://huggingface.co/datasets/Synthyra/PINDER
- THE shortcut. 1.49M PPI pairs as parquet, one `load_dataset` call. Per pair:
  receptor_sequence, ligand_sequence, holo (bound) + apo (unbound) PDBs, predicted flag,
  AND precomputed interface annotations: buried_sasa, intermolecular_contacts,
  n_residue_pairs, n_residues, contact-type breakdown.
- Why it matters: replaces the entire Interactome3D download + legacy-PDB parsing +
  interface-residue computation chain with a dataframe load. Deduplicated, split by
  structural similarity. Canonical PPI benchmark (behind modern docking models).
- Validate: (a) confirm the interface annotations are granular enough for your
  per-residue enrichment, or whether you still need per-residue contact maps from the
  holo PDB; (b) it's human/standard PPIs — NO cross-species orthologs, you still fetch
  those separately.

**Synthyra/StringDBSeqsv12** — https://huggingface.co/datasets/Synthyra/StringDBSeqsv12
- STRING v12 interactions WITH sequences attached. Saves the protein-sequence join.

**Synthyra/NEGATOME** — https://huggingface.co/datasets/Synthyra/NEGATOME
- Curated NON-interacting protein pairs. Use as a biologically-grounded negative control
  (better than the shuffled-residue-mask idea — real non-interaction, not within-protein shuffle).

**Synthyra/SHS148k** — https://huggingface.co/datasets/Synthyra/SHS148k
- Standard multiclass PPI benchmark (Chen et al.). Reference point if needed.

**PINNACLE embeddings** — hf: mims-harvard/ToolSpace (pinnacle_cge/ dir)
- Precomputed context-specific PPI embeddings. Comparison baseline vs your own ESM embeddings.
- Download: `uvx --from huggingface_hub hf download mims-harvard/ToolSpace --repo-type dataset --include "pinnacle_cge/*"`

Full collection: https://huggingface.co/collections/Synthyra/ppi-datasets-67b1193c9f4f5c9957477d1d

## 1. Structure-resolved interactions (FALLBACK if PINDER annotations insufficient)

**Interactome3D** — https://interactome3d.irbbarcelona.org/
- Version 2024_12, on UniProt 2024_05. Recent. [CORRECTED: I gave no version before.]
- WARNING: still uses OLD PDB format, cannot parse structures with 2-char chain IDs —
  silently drops some superseded entries. Your parser must expect legacy PDB.
- Use only if PINDER's interface annotations aren't granular enough.

**3did** — https://3did.irbbarcelona.org/  (last modified June 2025) — domain-level, skip for v1.

## 2. Network / hub layer (Task B)

**STRING v12.5** — https://string-db.org/cgi/download  [CORRECTED: it's 12.5 (2025), not 12.0]
- New in 12.5: regulatory network + directionality, three network types (functional/
  physical/regulatory), and DOWNLOADABLE NETWORK EMBEDDINGS for ML + cross-species transfer
  — directly relevant, worth a look.
- Validate: bulk per-organism flat files may still sit under the v12.0 path — check the
  exact filename. Set a combined_score threshold (e.g. >=700) before counting hubs.
- Or just use the Synthyra/StringDBSeqsv12 HF mirror above.

**BioGRID 5.0.252** — https://downloads.thebiogrid.org/BioGRID/Latest-Release/  [CORRECTED: now 5.0.x series, Dec 2025, ~2.25M interactions]
- Filename pattern changed from 4.4.x — verify exact BIOGRID-ALL-*.tab3.txt name.
- Has physical vs genetic flags. Only parse if STRING doesn't give what you need.

**IntAct** — https://www.ebi.ac.uk/intact/ — skip for v1.

## 3. Orthologs (cross-species sequence swap — PINDER won't give you this)

**OMA Browser** — https://omabrowser.org/api | pip: `omadb` — live, best scriptable option.
- Validate NMR coverage per-protein, not guaranteed.

**UniProt REST** — https://rest.uniprot.org/ — live, often faster fallback.
- Taxids: human 9606, mouse 10090, NMR 10181, bowhead 27622, bat (VALIDATE, e.g. Myotis 59463).
- Prefer reviewed (Swiss-Prot); flag TrEMBL-only as lower confidence.

**OrthoDB v12** — https://www.orthodb.org/ — REST + Python pkg, backup resolver.

## 4. Embeddings

**ESM C (Biohub)** — hf: https://huggingface.co/biohub | repo: github.com/Biohub/esm
- [CORRECTED: EvolutionaryScale rebranded to Biohub (Chan Zuckerberg). New repo + HF org.]
- Open weights: ESMC-600M (fits 16GB VRAM), ESMC-6B (needs multi-GPU or API).
- Install SDK: `pip install esm@git+https://github.com/Biohub/esm.git@main`
  NOTE: the pipeline currently uses the Biohub ESM SDK client for remote ESMC calls. Keep dependency constraints aligned with `pyproject.toml` and `uv.lock`.
- Local inference via HuggingFace AutoModel (if deps resolve):
  ```python
  from transformers import AutoModelForMaskedLM, AutoTokenizer
  model = AutoModelForMaskedLM.from_pretrained("biohub/ESMC-600M")
  ```

**Biohub Platform / ESM SDK remote service** — see Biohub API and SDK documentation
- API key: get one at https://biohub.ai/developer-console/api-keys, store in `.env`
  as `BIOHUB_API_TOKEN` (see `.env.template`).
- Auth: `Authorization: Bearer <token>` header on all requests.
- Base URL: `https://biohub.ai/api/v1/`
- Models: `esmc-300m-2024-12`, `esmc-600m-2024-12`, `esmc-6b-2024-12`, `esm3-open-2024-03`

  Endpoints (all POST, JSON body):

  | Endpoint | Cost | What it returns |
  |----------|------|-----------------|
  | `/encode` | **0 credits** | Token IDs from sequence |
  | `/logits` | seq_len tokens | Per-residue embeddings + logits |
  | `/fold` | seq_len × min(25, seq_len) | 3D coords, pLDDT, pTM, PAE |
  | `/forward_and_sample` | seq_len | Sampled output tokens (ESM3) |
  | `/generate` | seq_len × steps | Generated protein (ESM3) |
  | `/decode` | **0 credits** | Tokens → raw representation |

  Ref: https://biohub.ai/api-reference/encode (replace `encode` with endpoint name)

  Embedding workflow (tested, works):
  ```python
  import requests, os
  from dotenv import load_dotenv
  load_dotenv()
  TOKEN = os.environ["BIOHUB_API_TOKEN"]
  HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
  BASE = "https://biohub.ai/api/v1"

  # Step 1: encode sequence → tokens (free)
  enc = requests.post(f"{BASE}/encode", headers=HEADERS, json={
      "model": "esmc-600m-2024-12",
      "inputs": {"sequence": "MKTVRQERLKSIVRILERSKEPVSGAQ"}
  }).json()
  tokens = enc["outputs"]["sequence"]

  # Step 2: logits → per-residue embeddings (seq_len tokens)
  emb = requests.post(f"{BASE}/logits", headers=HEADERS, json={
      "model": "esmc-600m-2024-12",
      "inputs": {"sequence": tokens},
      "logits_config": {"sequence": True, "return_embeddings": True}
  }).json()
  embeddings = emb["embeddings"]  # shape: [1 layer][seq_len positions][1152 dims]
  ```

  Embedding dimensions: 600M → 1152d, 6B → 2560d. Both return per-residue vectors.

  Fold workflow (for ortholog structure prediction):
  ```python
  fold = requests.post(f"{BASE}/fold", headers=HEADERS, json={
      "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQ",
      "model": "esmfold2-fast-2026-05",  # or esmfold2-2026-05 for higher quality
      "include_pae": True,
  }).json()
  # fold["coordinates"]  — [n_residues][n_atoms][3] xyz
  # fold["plddt"]        — per-residue confidence
  # fold["ptm"]          — predicted TM-score
  # fold["pae"]          — predicted aligned error matrix
  ```

**ESM Atlas** — https://biohub.ai/esm/protein/atlas
- 6.8B protein sequences + 1.1B predicted structures + SAE interpretability features.
- Browsable per-protein at biohub.ai; bulk download via AWS S3 (~377 TB total, no auth).
- Indexed by sequence, NOT by PDB/UniProt accession — search by sequence, not ID.
- For our pipeline: use the remote Biohub ESMC service for per-protein embeddings/folds rather than
  downloading Atlas bulk data.

## 5. Candidate annotation (Task A, optional) — GenAge/HAGR, OpenGenes, Open Targets
