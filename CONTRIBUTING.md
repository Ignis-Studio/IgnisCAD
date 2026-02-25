Thanks for your interest in contributing to IgnisCAD.   
We welcome contributions from everyone. 

# Contributing Guide
This repo's main code is under `src/igniscad/`.  
The helpers and constants is under `src/igniscad/helpers`.  
Before contributing, do these things:
 - Fork this repository and commit in your own fork.
 - List the things that should be done in this Pull Request. (e.g. Bug fixes)
 - Open a draft Pull Request.
 - If this Pull Request is meant to fix a bug, open an issue before contributing, and link it to your Pull Request.
 - When ready, convert the Pull Request to `ready to review` state.

Important:
 - Every commit must be signed by the contributor's [verified signature](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification).
 - Since we use squash merges, your PR title will become the final commit message.
 - Please strictly follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0) format.
   - Types: Use standard types like `feat`, `fix`, `docs`, `refactor`. (Avoid non-standard types like `impl`).
   - Scope: Use kebab-case (e.g., `primitives-op`, not `PrimitivesOp` or `primitives_op`).
   - Format: Ensure there is a **space** after the colon.

# Testing Guide

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
- `tests/test_selectors.py`
  - `top(), bottom(), face_touching()` and other selectors works correctly.
  - The tagging system.

## 4) Add new tests (quick rule)

When fixing a bug, add one test that reproduces it first, then fix it.
