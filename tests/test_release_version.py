"""Tests for release-version consistency and the CI version helper."""

import re
from pathlib import Path

import pytest

import pyreact
from scripts.set_ci_version import create_post_version, update_ci_version

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


def test_repository_release_metadata_is_consistent():
    with (ROOT / "pyproject.toml").open("rb") as handle:
        package_version = tomllib.load(handle)["project"]["version"]

    docs_config = (ROOT / "docs" / "conf.py").read_text(encoding="utf-8")
    match = re.search(r"^release\s*=\s*['\"]([^'\"]+)['\"]", docs_config, re.MULTILINE)

    assert match is not None
    assert pyreact.__version__ == package_version
    assert match.group(1) == package_version


def test_create_post_version_is_unique_per_attempt():
    assert create_post_version("1.0.5", 12345, 1) == "1.0.5.post1234501"
    assert create_post_version("1.0.5", 12345, 2) == "1.0.5.post1234502"


@pytest.mark.parametrize("base_version", ["1.0.5.post1", "v1.0.5", "1.0-beta"])
def test_create_post_version_rejects_non_release_versions(base_version):
    with pytest.raises(ValueError):
        create_post_version(base_version, 1, 1)


def test_update_ci_version_updates_build_and_runtime_files(tmp_path: Path):
    (tmp_path / "pyreact").mkdir()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "2.4.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "pyreact" / "__init__.py").write_text(
        "__version__ = '2.4.0'\n",
        encoding="utf-8",
    )

    version = update_ci_version(tmp_path, run_id=42, run_attempt=3)

    assert version == "2.4.0.post4203"
    assert 'version = "2.4.0.post4203"' in (
        tmp_path / "pyproject.toml"
    ).read_text(encoding="utf-8")
    assert "__version__ = '2.4.0.post4203'" in (
        tmp_path / "pyreact" / "__init__.py"
    ).read_text(encoding="utf-8")
