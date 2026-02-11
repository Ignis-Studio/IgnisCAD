from pathlib import Path

import igniscad as ic


def test_show_export_creates_stl(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with ic.Model("sample") as m:
        m << ic.Box(8, 8, 8)

    ic.show(m, mode="export")

    out = tmp_path / "sample.stl"
    assert out.exists()
    assert out.stat().st_size > 0
