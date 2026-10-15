import importlib.util
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("init_site", ROOT / "scripts" / "init_site.py")
init_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(init_site)


@pytest.fixture
def copy(tmp_path):
    for name in ("render.yaml", ".env.example"):
        shutil.copy(ROOT / name, tmp_path / name)
    return tmp_path


def test_renames_service_disk_and_display_name(copy):
    init_site.apply(copy, "coffee-club", "Coffee Club")
    render = (copy / "render.yaml").read_text()
    assert "name: coffee-club\n" in render
    assert "name: coffee-club-disk\n" in render
    assert "value: Coffee Club\n" in render
    assert "SITE_NAME=Coffee Club" in (copy / ".env.example").read_text()


def test_can_be_rerun_with_another_name(copy):
    init_site.apply(copy, "first-name", "First")
    init_site.apply(copy, "second-name", "Second")
    render = (copy / "render.yaml").read_text()
    assert "first-name" not in render
    assert "name: second-name-disk\n" in render


def test_rejects_a_bad_slug(copy):
    with pytest.raises(ValueError):
        init_site.apply(copy, "Bad Name!", "x")
