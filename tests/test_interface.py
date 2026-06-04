"""Tests for interface residue extraction."""

from pathlib import Path

from longevity_port_pipelines.stages.interface import extract_interface_residues


def test_extract_interface_missing_chains(tmp_path: Path) -> None:
    pdb_content = """ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  CA  ALA A   2       3.800   0.000   0.000  1.00  0.00           C
END
"""
    pdb_path = tmp_path / "test.pdb"
    pdb_path.write_text(pdb_content)

    rec, lig = extract_interface_residues(pdb_path, "A", "B", distance_cutoff=8.0)
    assert rec == []
    assert lig == []


def test_extract_interface_close_residues(tmp_path: Path) -> None:
    pdb_content = """ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  CA  ALA A   2      10.000   0.000   0.000  1.00  0.00           C
ATOM      3  CA  GLY B   1       5.000   0.000   0.000  1.00  0.00           C
ATOM      4  CA  GLY B   2      20.000   0.000   0.000  1.00  0.00           C
END
"""
    pdb_path = tmp_path / "test.pdb"
    pdb_path.write_text(pdb_content)

    rec, lig = extract_interface_residues(pdb_path, "A", "B", distance_cutoff=8.0)
    assert 0 in rec or 1 in rec
    assert 0 in lig
