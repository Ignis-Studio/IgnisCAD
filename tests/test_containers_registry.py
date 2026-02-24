import pytest
import igniscad as icad


def test_model_registry_find_by_name():
    with icad.Model("demo") as m:
        m << icad.Box(5, 5, 5, name="base")
        m << icad.Cylinder(1, 6, name="peg")

    found = m.f("peg")
    assert found is not None
    assert found.name == "peg"


def test_model_registry_find_missing_raises():
    with icad.Model("demo") as m:
        m << icad.Box(1, 1, 1, name="only")

    with pytest.raises(ValueError):
        m.f("missing")
