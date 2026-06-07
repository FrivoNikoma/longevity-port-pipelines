import polars as pl

sel = pl.read_csv("data/output/selection.csv")
cov = pl.read_csv("data/output/ortholog_coverage.csv")

total_pairs = 0
api_calls = 0
rows = []

for r in sel.iter_rows(named=True):
    cid = r["id"]

    for chain, up in [
        ("receptor", r["uniprot_R"]),
        ("ligand", r["uniprot_L"]),
    ]:
        n = (
            cov.filter(pl.col("source_uniprot") == up)
            .select(["source_uniprot", "target_uniprot", "target_species_taxid"])
            .unique()
            .height
        )

        if n:
            rows.append((cid, chain, up, n))
            total_pairs += n
            api_calls += 2 * n

print("complexes:", sel.height)
print("embedding pairs:", total_pairs)
print("estimated Biohub API calls:", api_calls)
print()
print("first rows:")
for row in rows[:30]:
    print(row)