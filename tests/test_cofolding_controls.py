import polars as pl

from longevity_port_pipelines.stages import cofolding_controls as cc


def test_parse_pinder_uniprots() -> None:
    assert cc.parse_pinder_uniprots("3lqz__B1_P04440--3lqz__A1_P20036") == (
        "P04440",
        "P20036",
    )


def test_parse_pinder_uniprots_rejects_invalid_id() -> None:
    try:
        cc.parse_pinder_uniprots("not-a-pinder-id")
    except ValueError as exc:
        assert "Invalid PINDER id" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_add_parsed_uniprot_columns_flags_same_and_undefined() -> None:
    df = pl.DataFrame(
        [
            {
                "id": "1abc__A1_P12345--1abc__B1_P12345",
                "probability": 1.0,
                "buried_sasa": 2000.0,
                "intermolecular_contacts": 100,
                "n_residue_pairs": 250,
                "receptor_len": 100,
                "ligand_len": 100,
                "link_density": 0.1,
                "planarity": 4.0,
            },
            {
                "id": "2abc__A1_UNDEFINED--2abc__B1_Q99999",
                "probability": 0.9,
                "buried_sasa": 1500.0,
                "intermolecular_contacts": 80,
                "n_residue_pairs": 200,
                "receptor_len": 120,
                "ligand_len": 130,
                "link_density": 0.1,
                "planarity": 4.0,
            },
        ]
    )

    parsed = cc.add_parsed_uniprot_columns(df)

    first = parsed.row(0, named=True)
    second = parsed.row(1, named=True)

    assert first["receptor_uniprot"] == "P12345"
    assert first["ligand_uniprot"] == "P12345"
    assert first["same_uniprot"] is True
    assert first["has_undefined"] is False

    assert second["receptor_uniprot"] == "UNDEFINED"
    assert second["ligand_uniprot"] == "Q99999"
    assert second["same_uniprot"] is False
    assert second["has_undefined"] is True


def test_looks_viral_or_capsid() -> None:
    assert cc.looks_viral_or_capsid(
        "Escherichia phage MS2",
        "Escherichia phage MS2",
        "Capsid protein",
        "Capsid protein",
    )
    assert not cc.looks_viral_or_capsid(
        "Homo sapiens",
        "Homo sapiens",
        "Protein A",
        "Protein B",
    )


def test_annotate_candidates_flags_human_heterodimer_control() -> None:
    parsed = pl.DataFrame(
        [
            {
                "id": "3lqz__B1_P04440--3lqz__A1_P20036",
                "probability": 1.0,
                "buried_sasa": 6368.0,
                "intermolecular_contacts": 220,
                "n_residue_pairs": 775,
                "receptor_len": 198,
                "ligand_len": 181,
                "link_density": 0.05,
                "planarity": 5.0,
                "receptor_uniprot": "P04440",
                "ligand_uniprot": "P20036",
                "same_uniprot": False,
                "has_undefined": False,
            }
        ]
    )

    metadata = {
        "P04440": cc.UniProtMetadata(
            accession="P04440",
            taxid=9606,
            organism="Homo sapiens",
            protein_name="HLA class II histocompatibility antigen, DR beta chain",
        ),
        "P20036": cc.UniProtMetadata(
            accession="P20036",
            taxid=9606,
            organism="Homo sapiens",
            protein_name="HLA class II histocompatibility antigen, DR alpha chain",
        ),
    }

    annotated = cc.annotate_candidates(parsed, metadata)
    row = annotated.row(0, named=True)

    assert row["human_human"] is True
    assert row["same_taxid"] is True
    assert row["likely_viral_or_capsid"] is False
    assert row["human_heterodimer_control"] is True
    assert row["technical_homomer_control"] is False


def test_annotate_candidates_rejects_viral_homomer_as_human_control() -> None:
    parsed = pl.DataFrame(
        [
            {
                "id": "1msc__A1_P03612--1msc__A2_P03612",
                "probability": 1.0,
                "buried_sasa": 7020.0,
                "intermolecular_contacts": 265,
                "n_residue_pairs": 1052,
                "receptor_len": 129,
                "ligand_len": 129,
                "link_density": 0.05,
                "planarity": 5.7,
                "receptor_uniprot": "P03612",
                "ligand_uniprot": "P03612",
                "same_uniprot": True,
                "has_undefined": False,
            }
        ]
    )

    metadata = {
        "P03612": cc.UniProtMetadata(
            accession="P03612",
            taxid=12022,
            organism="Escherichia phage MS2",
            protein_name="Capsid protein",
        ),
    }

    annotated = cc.annotate_candidates(parsed, metadata)
    row = annotated.row(0, named=True)

    assert row["human_human"] is False
    assert row["same_uniprot"] is True
    assert row["likely_viral_or_capsid"] is True
    assert row["human_heterodimer_control"] is False
    assert row["technical_homomer_control"] is False


def test_human_heterodimer_controls_filters_rows() -> None:
    annotated = pl.DataFrame(
        [
            {
                "id": "human_pair",
                "probability": 1.0,
                "buried_sasa": 2000.0,
                "human_heterodimer_control": True,
            },
            {
                "id": "viral_pair",
                "probability": 1.0,
                "buried_sasa": 3000.0,
                "human_heterodimer_control": False,
            },
        ]
    )

    controls = cc.human_heterodimer_controls(annotated)

    assert controls.height == 1
    assert controls.row(0, named=True)["id"] == "human_pair"
