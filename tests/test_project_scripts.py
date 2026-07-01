import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = ROOT / "pyproject.toml"


def load_pyproject() -> dict[str, Any]:
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


def test_lane_manifest_summary_cli_is_registered_as_project_script() -> None:
    scripts = load_pyproject()["project"]["scripts"]

    assert scripts["lane-manifest-summary"] == "longevity_port_pipelines.stages.lane_manifest:main"


def test_generic_strict_panel_cli_is_registered_as_project_script() -> None:
    scripts = load_pyproject()["project"]["scripts"]

    assert scripts["strict-contrast-panel"] == (
        "longevity_port_pipelines.stages.strict_contrast_panel:app"
    )


def test_generic_gated_contrast_cli_is_registered_as_project_script() -> None:
    scripts = load_pyproject()["project"]["scripts"]

    assert scripts["gated-contrast"] == "longevity_port_pipelines.stages.gated_contrast:app"
