# Testing Guide (minimal)

This repo now includes a small pytest suite under `tests/`.

## 1) Install dependencies

Using `uv` (recommended):

```bash
uv sync --group test
```

## 2) Run tests

```bash
uv run pytest
```

## 3) What these tests cover

- `tests/test_primitives_and_ops.py`
  - Primitive creation and basic boolean safety (`-`, `&`)
  - Move/rotate chain behavior
- `tests/test_containers_registry.py`
  - `Model` registry lookup (`f()` / `find()`)
  - Missing key raises `ValueError`
- `tests/test_export.py`
  - `show(..., mode="export")` writes STL file successfully

## 4) Add new tests (quick rule)

When fixing a bug, add one test that reproduces it first, then fix it.
