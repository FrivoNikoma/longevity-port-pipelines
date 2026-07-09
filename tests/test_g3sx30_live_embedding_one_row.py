from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from longevity_port_pipelines.stages import g3sx30_live_embedding_one_row as stage


def _write_approval_doc(path: Path) -> None:
    path.write_text("\n".join(stage.APPROVAL_REQUIRED_STRINGS), encoding="utf-8")


def _write_manifest(path: Path, *, sequence_sha256: str, length: int = 492) -> None:
    path.write_text(
        "\n".join(
            [
                (
                    "candidate_id,target_accession,target_taxid,gene_symbol,"
                    "reviewed_sequence_length,reviewed_sequence_sha256,dry_run_only,"
                    "max_live_batch_size,ready_for_preflight_after_manifest,"
                    "sequence_fetch_allowed,biohub_call_allowed,esmc_call_allowed,"
                    "embedding_generation_allowed,curated_embedding_preflight_allowed,"
                    "curated_embedding_single_allowed"
                ),
                (
                    "tp53_mdm2_elephant_seed_mdm2_chain,G3SX30,9785,MDM2,"
                    f"{length},{sequence_sha256},true,0,false,false,false,false,false,false,false"
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_fasta(path: Path, sequence: str) -> None:
    path.write_text(
        (
            ">tr|G3SX30|G3SX30_LOXAF E3 ubiquitin-protein ligase Mdm2 "
            "OS=Loxodonta africana OX=9785 GN=MDM2 PE=3 SV=1\n"
            f"{sequence}\n"
        ),
        encoding="utf-8",
    )


def _build_test_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> stage.G3SX30LiveEmbeddingPlan:
    sequence = "M" * 492
    sequence_sha256 = hashlib.sha256(sequence.encode("utf-8")).hexdigest()
    monkeypatch.setattr(stage, "EXPECTED_SEQUENCE_SHA256", sequence_sha256)
    approval_doc = tmp_path / "current_gate_map.md"
    fasta = tmp_path / "g3sx30_reviewed_sequence.fasta"
    manifest = tmp_path / "g3sx30_dry_run_preflight_manifest.csv"
    _write_approval_doc(approval_doc)
    _write_fasta(fasta, sequence)
    _write_manifest(manifest, sequence_sha256=sequence_sha256)
    return stage.build_g3sx30_live_embedding_plan(
        manifest_path=manifest,
        manifest_row_index=1,
        approval_doc=approval_doc,
        reviewed_sequence_fasta=fasta,
        output_dir=tmp_path / "output",
        model_name="esmc-test",
    )


def test_build_g3sx30_live_embedding_plan_validates_manifest_and_fasta(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _build_test_plan(tmp_path, monkeypatch)
    assert plan.manifest_row_index == 1
    assert plan.candidate_id == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert plan.target_accession == "G3SX30"
    assert plan.target_taxid == 9785
    assert plan.gene_symbol == "MDM2"
    assert plan.reviewed_sequence.length == 492
    assert plan.embedding_path == (
        tmp_path
        / "output"
        / "embeddings"
        / "esmc-test"
        / "tp53_mdm2_elephant_seed_mdm2_chain_mdm2_9785.npy"
    )


def test_build_g3sx30_live_embedding_plan_refuses_non_one_row_index(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _build_test_plan(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="one-row only"):
        stage.build_g3sx30_live_embedding_plan(
            manifest_path=plan.manifest_path,
            manifest_row_index=2,
            approval_doc=plan.approval_doc,
            reviewed_sequence_fasta=plan.reviewed_sequence_fasta,
            output_dir=plan.output_dir,
            model_name=plan.model_name,
        )


def test_build_g3sx30_live_embedding_plan_refuses_bad_sequence_sha(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sequence = "M" * 492
    sequence_sha256 = hashlib.sha256(sequence.encode("utf-8")).hexdigest()
    monkeypatch.setattr(stage, "EXPECTED_SEQUENCE_SHA256", sequence_sha256)
    approval_doc = tmp_path / "current_gate_map.md"
    fasta = tmp_path / "g3sx30_reviewed_sequence.fasta"
    manifest = tmp_path / "g3sx30_dry_run_preflight_manifest.csv"
    _write_approval_doc(approval_doc)
    _write_fasta(fasta, "A" * 492)
    _write_manifest(manifest, sequence_sha256=sequence_sha256)
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        stage.build_g3sx30_live_embedding_plan(
            manifest_path=manifest,
            manifest_row_index=1,
            approval_doc=approval_doc,
            reviewed_sequence_fasta=fasta,
            output_dir=tmp_path / "output",
            model_name="esmc-test",
        )


def test_run_g3sx30_live_embedding_dry_run_does_not_call_biohub(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _build_test_plan(tmp_path, monkeypatch)

    def fail_get_token() -> str:
        raise AssertionError("dry-run must not request Biohub token")

    monkeypatch.setattr(stage, "get_biohub_token", fail_get_token)
    result = stage.run_g3sx30_live_embedding(
        plan,
        api_url="https://example.test",
        yes_live=False,
        max_live_batch_size=1,
    )
    assert result.status == "dry_run_missing"
    assert result.embedding_shape is None


def test_run_g3sx30_live_embedding_requires_batch_size_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _build_test_plan(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="max_live_batch_size=1"):
        stage.run_g3sx30_live_embedding(
            plan,
            api_url="https://example.test",
            yes_live=True,
            max_live_batch_size=2,
        )


def test_run_g3sx30_live_embedding_live_calls_biohub_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _build_test_plan(tmp_path, monkeypatch)
    calls: list[dict[str, Any]] = []

    class FakeEmbedding:
        embeddings = np.zeros((492, 3), dtype=np.float32)

    def fake_get_token() -> str:
        return "token"

    def fake_embed_or_load_sequence(**kwargs: Any) -> FakeEmbedding:
        calls.append(kwargs)
        return FakeEmbedding()

    monkeypatch.setattr(stage, "get_biohub_token", fake_get_token)
    monkeypatch.setattr(stage, "embed_or_load_sequence", fake_embed_or_load_sequence)
    result = stage.run_g3sx30_live_embedding(
        plan,
        api_url="https://example.test",
        yes_live=True,
        max_live_batch_size=1,
    )
    assert result.status == "live_completed"
    assert result.embedding_shape == "492x3"
    assert len(calls) == 1
    assert calls[0]["complex_id"] == "tp53_mdm2_elephant_seed_mdm2_chain"
    assert calls[0]["chain"] == "mdm2"
    assert calls[0]["sequence"] == "M" * 492
    assert calls[0]["species_taxid"] == 9785
    assert calls[0]["model"] == "esmc-test"
    assert calls[0]["output_dir"] == tmp_path / "output"
