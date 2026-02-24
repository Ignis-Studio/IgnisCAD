from pathlib import Path

import igniscad as icad


def test_show_export_creates_stl(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with icad.Model("sample") as m:
        m << icad.Box(8, 8, 8)

    icad.show(m, mode="export")

    out = tmp_path / "sample.stl"
    assert out.exists()
    assert out.stat().st_size > 0
