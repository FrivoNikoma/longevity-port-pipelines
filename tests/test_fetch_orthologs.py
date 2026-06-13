from __future__ import annotations

from typing import Any

from longevity_port_pipelines.stages.fetch_orthologs import query_oma_orthologs


class FakeResponse:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


def test_query_oma_orthologs_fetches_sequence_from_entry_detail(monkeypatch) -> None:
    calls: list[str] = []

    def fake_get(url: str, **kwargs: Any) -> FakeResponse:
        calls.append(url)
        if url.endswith("/orthologs/"):
            return FakeResponse(
                [
                    {
                        "canonicalid": "Q921K2",
                        "sequence": None,
                        "entry_url": "https://omabrowser.org/api/protein/24833816/?format=json",
                        "species": {"taxon_id": 10090},
                    }
                ]
            )

        return FakeResponse({"sequence": "MAEASEQUENCE"})

    monkeypatch.setattr(
        "longevity_port_pipelines.stages.fetch_orthologs.requests.get",
        fake_get,
    )

    results = query_oma_orthologs("P09874", 10090)

    assert len(results) == 1
    assert results[0].source_uniprot == "P09874"
    assert results[0].target_uniprot == "Q921K2"
    assert results[0].target_species_taxid == 10090
    assert results[0].target_sequence == "MAEASEQUENCE"
    assert results[0].source_db == "OMA"
    assert calls == [
        "https://omabrowser.org/api/protein/P09874/orthologs/",
        "https://omabrowser.org/api/protein/24833816/?format=json",
    ]
