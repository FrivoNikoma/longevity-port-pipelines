from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest
from scripts import run_core3_validation_closure as closure

from longevity_port_pipelines.stages.validation_closure import write_closure_summary


def test_parse_args_accepts_safe_local_mode_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_core3_validation_closure.py",
            "--skip-embed",
            "--skip-analyze",
        ],
    )

    args = closure.parse_args()

    assert args.skip_embed is True
    assert args.skip_analyze is True


def test_write_closure_summary_smoke(tmp_path: Path) -> None:
    enrichment = pl.DataFrame(
        {
            "complex_id": ["c1", "c2"],
            "chain": ["receptor", "ligand"],
            "target_species": ["naked_mole_rat", "mouse"],
            "enrichment_ratio": [1.5, 0.8],
            "shuffled_control_ratio": [1.1, 1.0],
            "negatome_control_ratio": [1.0, None],
        }
    )

    audit = pl.DataFrame(
        {
            "complex_id": ["c1", "c2"],
            "chain": ["receptor", "ligand"],
            "target_species": ["naked_mole_rat", "mouse"],
            "control_status": ["has_shuffled_and_negatome", "missing_negatome"],
            "control_evidence_tier": ["controlled_pass", "preliminary_shuffled_only"],
            "passes_controls": [True, False],
        }
    )

    scorecard = pl.DataFrame(
        {
            "candidate_id": ["c1|receptor|naked_mole_rat", "c2|ligand|mouse"],
            "proposal_outcome_class": ["maintained_interface", "unresolved"],
            "confidence": ["high", "low"],
            "score": [9.0, 3.0],
            "control_evidence_tier": ["controlled_pass", "preliminary_shuffled_only"],
            "passes_controls": [True, False],
        }
    )

    output_path = tmp_path / "validation_closure_summary.md"

    write_closure_summary(
        enrichment=enrichment,
        audit=audit,
        scorecard=scorecard,
        output_path=output_path,
    )

    text = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert "validation closure summary" in text
    assert "has_shuffled_and_negatome" in text
    assert "missing_negatome" in text
    assert "controlled_pass" in text
    assert "c1|receptor|naked_mole_rat" in text
