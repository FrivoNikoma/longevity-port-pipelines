import polars as pl
from scripts.cluster_divergence_profile_features import (
    markdown_table,
    parse_feature_list,
)


def test_parse_feature_list_defaults() -> None:
    features = parse_feature_list(None)

    assert "log2_enrichment_ratio" in features
    assert "effect_size_cohens_d_computed" in features


def test_parse_feature_list_comma_separated() -> None:
    features = parse_feature_list("a, b,,c")

    assert features == ["a", "b", "c"]


def test_markdown_table_escapes_pipe_characters() -> None:
    table = markdown_table(pl.DataFrame({"name": ["a|b"], "value": [1.23456789]}))

    assert "a\\|b" in table
    assert "1.23457" in table
