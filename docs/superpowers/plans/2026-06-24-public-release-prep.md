# EAVT Helper — Public Release Prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the `eavt-helper` repo to a publishable-on-GitHub bar — fix the credibility-killers, fix one correctness bug in the chunking logic, and add the standard OSS scaffolding (modern packaging, CI, linting, type-checking, contributor docs).

**Architecture:** Twelve small, mostly-independent changes. The structural fixes (license, dead code, chunking bug) come first because they affect correctness and trust. Then packaging modernization (`pyproject.toml`, `--version`, `ruff`, `mypy`). Then CI and contributor scaffolding. Finally documentation polish. Each task ends with a green test suite and a commit.

**Tech Stack:** Python 3.10+, pandas, click, pytest, ruff, mypy, GitHub Actions.

## Global Constraints

- License: **MIT** — `LICENSE` file, `pyproject.toml`, and `README.md` must all say MIT consistently.
- Python floor: **3.10+** (drop 3.8 and 3.9 entirely).
- NumPy pin: **`numpy>=1.20.0`** with no upper bound (drop the `<2.0` cap).
- Packaging: **`pyproject.toml` (PEP 621)** as the single source of truth. `setup.py` is deleted at the end of Task 5.
- Linting/formatting: **`ruff`** replaces both `flake8` and `black`.
- Type checking: **`mypy`** with `strict = true` on the `eavt_helper` package.
- All changes preserve the existing public CLI surface: `eavt-helper snapshot-to-eavt …` and `eavt-helper eavt-to-scd …` must work identically after this plan (except `--version` is newly available).
- Commit style: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`).
- Every task ends with `pytest -q` green before commit.

---

## File Structure

Files this plan creates, modifies, or deletes:

**Created:**
- `pyproject.toml` — replaces `setup.py`
- `.github/workflows/ci.yml` — lint + type-check + test matrix
- `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`
- `examples/snapshot.csv`, `examples/eavt.csv`, `examples/scd2.csv`, `examples/README.md`
- `tests/test_chunking.py` — new tests for the entity-aware chunking
- `eavt_helper/_version.py` — single-source-of-truth version exposure

**Modified:**
- `LICENSE` — replace GPL-3.0 with MIT
- `README.md` — fix license claim, correct memory-efficiency claim, add the "why EAVT" section, add CI badge, add example walkthrough
- `eavt_helper/classes/snapshot.py` — fix `_process_in_chunks` to chunk by entity
- `eavt_helper/main.py` — add `--version` flag and group docstring
- `Makefile` — drop flake8/black targets, replace with ruff
- `pytest.ini` — minor cleanup (keep as-is or move into `pyproject.toml`)

**Deleted:**
- `setup.py` (after migrating to `pyproject.toml`)
- `run_tests.py` (redundant with `make test`)
- `eavt_helper/utils/__init__.py` and the empty `utils/` directory

---

## Task 1: Fix the license

**Files:**
- Modify: `LICENSE` (entire file replaced)
- Modify: `setup.py:37` (classifier is already MIT — verify only)
- Modify: `README.md:159` (verify license line)

**Interfaces:**
- Consumes: nothing
- Produces: `LICENSE` file containing MIT license text with year `2026` and copyright holder `Vitor Julio`.

- [ ] **Step 1: Replace `LICENSE` file contents**

Overwrite `LICENSE` with exactly this text (standard SPDX MIT template):

```
MIT License

Copyright (c) 2026 Vitor Julio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Verify README's license section matches**

Open `README.md` and confirm the section reads exactly:

```markdown
## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

If it doesn't, edit it to match.

- [ ] **Step 3: Verify `setup.py` classifier is MIT**

Open `setup.py:37` and confirm the line reads:

```python
        "License :: OSI Approved :: MIT License",
```

It already does — no change needed. This step is a verification only.

- [ ] **Step 4: Run tests to confirm nothing broke**

Run: `pytest -q`
Expected: all tests pass (license changes don't touch code).

- [ ] **Step 5: Commit**

```bash
git add LICENSE README.md
git commit -m "chore: switch license from GPL-3.0 to MIT to match classifier and README"
```

---

## Task 2: Remove dead code

**Files:**
- Delete: `run_tests.py`
- Delete: `eavt_helper/utils/__init__.py` and the `eavt_helper/utils/` directory
- Modify: `Makefile` — remove the `test-interactive` target

**Interfaces:**
- Consumes: nothing
- Produces: a smaller repo surface. No public API removed (utils was empty; `run_tests.py` was a wrapper around pytest).

- [ ] **Step 1: Confirm `utils/` is empty and unreferenced**

Run: `cat eavt_helper/utils/__init__.py`
Expected: empty file (zero bytes).

Run: `grep -r "from eavt_helper.utils\|import eavt_helper.utils\|eavt_helper\.utils" eavt_helper tests`
Expected: no matches.

- [ ] **Step 2: Delete `utils/`**

Run: `rm -rf eavt_helper/utils`

- [ ] **Step 3: Delete `run_tests.py`**

Run: `rm run_tests.py`

- [ ] **Step 4: Update `Makefile` — remove `test-interactive` target**

In `Makefile`, delete these two blocks:

```makefile
test-interactive:
	@echo "🎯 Running interactive test selection..."
	python run_tests.py --interactive
```

And from the `help:` target, delete the line:

```makefile
	@echo "make test-interactive - Run tests interactively"
```

And from the `.PHONY:` line, remove `test-interactive`. The final `.PHONY` line should read:

```makefile
.PHONY: help install test test-coverage clean lint format
```

- [ ] **Step 5: Run tests**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 6: Run `make test` to confirm Makefile still works**

Run: `make test`
Expected: pytest runs successfully.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: remove empty utils package and redundant run_tests.py"
```

---

## Task 3: Write failing test for the chunk-boundary duplicate-row bug

**Files:**
- Create: `tests/test_chunking.py`

**Interfaces:**
- Consumes: existing `Snapshot` class from `eavt_helper.classes.snapshot`
- Produces: a failing pytest test `test_snapshot_chunking_no_duplicate_changes` that will pass after Task 4. It asserts that an entity's history is not split across chunks (which today emits spurious "change" rows at chunk boundaries).

- [ ] **Step 1: Create the test file**

Create `tests/test_chunking.py` with this exact content:

```python
"""Tests for chunked processing correctness.

Specifically tests that chunk-by-entity grouping prevents an entity's history
from being split across chunks (which would produce duplicate EAVT rows at
chunk boundaries — see Task 3/4 of the public-release-prep plan).
"""
import os
import tempfile
from unittest.mock import patch

import pandas as pd
import pytest

from eavt_helper.classes.snapshot import Snapshot


class TestSnapshotChunkingByEntity:
    """Verify chunked snapshot->EAVT transformation produces the same output as unchunked."""

    def setup_method(self):
        # 6 entities, each with 3 snapshot rows (same value across rows for
        # attribute `name`; changing value for attribute `age`).
        # If chunking splits an entity's history, we will see duplicate
        # 'name' rows in the EAVT output instead of just one.
        rows = []
        for entity_id in range(1, 7):
            rows.extend([
                {"user_id": entity_id, "timestamp": "2024-01-01",
                 "name": f"user_{entity_id}", "age": 20},
                {"user_id": entity_id, "timestamp": "2024-02-01",
                 "name": f"user_{entity_id}", "age": 21},
                {"user_id": entity_id, "timestamp": "2024-03-01",
                 "name": f"user_{entity_id}", "age": 22},
            ])
        self.df = pd.DataFrame(rows)

        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        )
        self.df.to_csv(self.tmp.name, index=False)
        self.tmp.close()

    def teardown_method(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def _eavt_sorted(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.sort_values(["e", "a", "t"])
              .reset_index(drop=True)
        )

    def test_snapshot_chunking_matches_unchunked(self):
        """Chunked transform must produce the same EAVT rows as unchunked."""
        with patch("click.echo"):
            snap_unchunked = Snapshot(self.tmp.name, "user_id", "timestamp")
            eavt_unchunked = snap_unchunked.transform_to_eavt(chunk_size=None)

            snap_chunked = Snapshot(self.tmp.name, "user_id", "timestamp")
            # chunk_size=5 forces multiple chunks across 18 rows (6 entities * 3 rows)
            eavt_chunked = snap_chunked.transform_to_eavt(chunk_size=5)

        pd.testing.assert_frame_equal(
            self._eavt_sorted(eavt_unchunked),
            self._eavt_sorted(eavt_chunked),
        )

    def test_snapshot_chunking_no_duplicate_name_rows(self):
        """Each entity's 'name' attribute should emit exactly one EAVT row.

        Because 'name' never changes within an entity, only the first
        observation should be emitted. If chunking splits an entity's history,
        the first row of the second chunk re-emits 'name' as a spurious change.
        """
        with patch("click.echo"):
            snap = Snapshot(self.tmp.name, "user_id", "timestamp")
            eavt = snap.transform_to_eavt(chunk_size=5)

        name_rows = eavt[eavt["a"] == "name"]
        per_entity_counts = name_rows.groupby("e").size()
        # Each of the 6 entities should appear exactly once for attribute 'name'.
        assert (per_entity_counts == 1).all(), (
            f"Expected 1 'name' row per entity, got:\n{per_entity_counts}"
        )
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `pytest tests/test_chunking.py -v`
Expected: both tests **FAIL**. The failure mode for `test_snapshot_chunking_no_duplicate_name_rows` should show some entities with `2` instead of `1` (those whose history spans a chunk boundary). The failure mode for `test_snapshot_chunking_matches_unchunked` should show extra rows in the chunked output.

If the tests pass instead of fail, something is wrong — stop and investigate before proceeding to Task 4.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/test_chunking.py
git commit -m "test: add failing test exposing snapshot chunk-boundary duplicate-row bug"
```

---

## Task 4: Fix `Snapshot._process_in_chunks` to chunk by entity

**Files:**
- Modify: `eavt_helper/classes/snapshot.py:72-87` (the `_process_in_chunks` method)

**Interfaces:**
- Consumes: existing `_transform_single_chunk(df)` method (unchanged signature)
- Produces: corrected `_process_in_chunks(chunk_size)` that groups rows by entity ID before chunking, so an entity's full history is always within a single chunk. Public signature unchanged.

- [ ] **Step 1: Replace `_process_in_chunks` with entity-aware version**

In `eavt_helper/classes/snapshot.py`, replace the existing `_process_in_chunks` method (lines 72-87) with:

```python
    def _process_in_chunks(self, chunk_size: int) -> pd.DataFrame:
        """Process large datasets in chunks of entities to manage memory usage.

        Chunking is done by entity ID rather than by row index. This ensures
        an entity's full history is always contained within a single chunk,
        which is required for the lag-based change detection in
        `_with_v_lag` / `_with_different_v_lag` to be correct.
        """
        entities = self.df[self.id_col].unique()
        # Approximate entities-per-chunk from the requested row chunk_size,
        # using the average rows-per-entity. Always at least 1 entity per chunk.
        avg_rows_per_entity = max(1, len(self.df) / max(1, len(entities)))
        entities_per_chunk = max(1, int(chunk_size / avg_rows_per_entity))

        results = []
        total_entity_chunks = (len(entities) + entities_per_chunk - 1) // entities_per_chunk

        with click.progressbar(range(0, len(entities), entities_per_chunk),
                               label='Processing entity chunks',
                               length=total_entity_chunks) as bar:
            for start in bar:
                end = min(start + entities_per_chunk, len(entities))
                chunk_entities = entities[start:end]
                chunk_df = self.df[self.df[self.id_col].isin(chunk_entities)].copy()

                processed_chunk = self._transform_single_chunk(chunk_df)
                results.append(processed_chunk)

        click.echo("✓ Combining processed chunks...")
        return pd.concat(results, ignore_index=True)
```

- [ ] **Step 2: Run the chunking tests and confirm they now pass**

Run: `pytest tests/test_chunking.py -v`
Expected: both tests **PASS**.

- [ ] **Step 3: Run the full test suite to confirm no regressions**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add eavt_helper/classes/snapshot.py
git commit -m "fix: chunk snapshot transformation by entity to preserve history boundaries"
```

---

## Task 5: Migrate `setup.py` → `pyproject.toml`, bump Python floor to 3.10, loosen numpy

**Files:**
- Create: `pyproject.toml`
- Delete: `setup.py`
- Modify: `Makefile` — `install` target wording unchanged, but verify it still works

**Interfaces:**
- Consumes: nothing (this is a metadata-only change)
- Produces: `pyproject.toml` as the single source of truth for package metadata; `pip install -e .[dev]` continues to work; classifiers updated to 3.10/3.11/3.12; numpy upper-pin removed.

- [ ] **Step 1: Create `pyproject.toml`**

Create `pyproject.toml` at the repo root with this content:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "eavt-helper"
version = "0.3.0"
description = "CLI tool to convert snapshots to EAVT logs and EAVT logs to Slowly Changing Dimensions"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Vitor Julio" }]
keywords = ["eavt", "scd", "slowly-changing-dimension", "data-engineering", "etl"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Database",
    "Topic :: Scientific/Engineering",
]
dependencies = [
    "click>=8.0.0,<9.0.0",
    "pandas>=1.3.0,<3.0.0",
    "numpy>=1.20.0",
    "python-dateutil>=2.8.0",
    "pytz>=2021.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.4.0",
    "mypy>=1.8.0",
]

[project.urls]
Homepage = "https://github.com/vmjulio/eavt-helper"
Repository = "https://github.com/vmjulio/eavt-helper"
Issues = "https://github.com/vmjulio/eavt-helper/issues"

[project.scripts]
eavt-helper = "eavt_helper.main:cli"

[tool.setuptools.packages.find]
include = ["eavt_helper*"]
exclude = ["tests*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers --disable-warnings"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

- [ ] **Step 2: Delete `setup.py`**

Run: `rm setup.py`

- [ ] **Step 3: Delete `pytest.ini`** (now lives inside `pyproject.toml`)

Run: `rm pytest.ini`

- [ ] **Step 4: Reinstall the package to verify the new metadata works**

Run: `pip install --editable .[dev]`
Expected: install completes successfully; no errors about missing metadata.

- [ ] **Step 5: Run tests to confirm pytest config moved cleanly**

Run: `pytest -q`
Expected: all tests pass; pytest picks up config from `pyproject.toml`.

- [ ] **Step 6: Verify the CLI entry point still works**

Run: `eavt-helper --help`
Expected: shows the two subcommands `snapshot-to-eavt` and `eavt-to-scd`.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml
git rm setup.py pytest.ini
git commit -m "build: migrate to pyproject.toml, bump python floor to 3.10, unpin numpy upper bound"
```

---

## Task 6: Add `__version__` and `--version` CLI flag

**Files:**
- Modify: `eavt_helper/__init__.py` — expose `__version__` from package metadata
- Modify: `eavt_helper/main.py` — add `@click.version_option`

**Interfaces:**
- Consumes: package name `eavt-helper` from `pyproject.toml`
- Produces:
  - `eavt_helper.__version__` (string) readable from Python
  - `eavt-helper --version` CLI flag prints the version

- [ ] **Step 1: Update `eavt_helper/__init__.py`**

Open `eavt_helper/__init__.py` and replace its contents with:

```python
"""eavt-helper — convert snapshots ↔ EAVT logs ↔ SCD Type 2 tables."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("eavt-helper")
except PackageNotFoundError:
    # Package is not installed (e.g. running from a source checkout without
    # `pip install -e .`). Fall back to a sentinel.
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
```

- [ ] **Step 2: Update `eavt_helper/main.py`**

Replace the contents of `eavt_helper/main.py` with:

```python
"""Entrypoint of the CLI."""
import click

from eavt_helper import __version__
from eavt_helper.commands import eavt_to_scd, snapshot_to_eavt


@click.group(help="Convert snapshots to EAVT logs and EAVT logs to Slowly Changing Dimensions (SCD Type 2).")
@click.version_option(version=__version__, prog_name="eavt-helper")
def cli():
    pass


cli.add_command(snapshot_to_eavt)
cli.add_command(eavt_to_scd)
```

- [ ] **Step 3: Add a test for `--version`**

Append this test class to `tests/test_main.py`:

```python


class TestVersionFlag:
    """Test the --version flag on the top-level CLI."""

    def test_version_flag_prints_version(self):
        from click.testing import CliRunner

        from eavt_helper import __version__
        from eavt_helper.main import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output
        assert "eavt-helper" in result.output
```

- [ ] **Step 4: Run the new test and full suite**

Run: `pytest tests/test_main.py::TestVersionFlag -v`
Expected: test passes.

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 5: Smoke-test from the CLI**

Run: `eavt-helper --version`
Expected output (version string may differ):

```
eavt-helper, version 0.3.0
```

- [ ] **Step 6: Commit**

```bash
git add eavt_helper/__init__.py eavt_helper/main.py tests/test_main.py
git commit -m "feat: add --version CLI flag and expose eavt_helper.__version__"
```

---

## Task 7: Replace flake8 + black with ruff

**Files:**
- Modify: `pyproject.toml` — add `[tool.ruff]` config
- Modify: `Makefile` — replace `lint` and `format` targets
- Delete: any existing `.flake8` config (run `ls -la` to check; none expected)

**Interfaces:**
- Consumes: `ruff>=0.4.0` (already declared in dev dependencies in Task 5)
- Produces:
  - `make lint` runs `ruff check`
  - `make format` runs `ruff format` (and `ruff check --fix`)
  - All existing source files pass `ruff check` (any auto-fixable issues are fixed in this task)

- [ ] **Step 1: Add ruff config to `pyproject.toml`**

Append this to `pyproject.toml`:

```toml

[tool.ruff]
line-length = 100
target-version = "py310"
src = ["eavt_helper", "tests"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "SIM", # flake8-simplify
]
ignore = [
    "E203",  # whitespace before ':' — conflicts with black/ruff format
    "E501",  # line too long — handled by formatter
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["B011"]  # asserts in tests are fine
```

- [ ] **Step 2: Run `ruff check --fix` to auto-fix what it can**

Run: `ruff check --fix eavt_helper tests`
Expected: ruff reports the issues it auto-fixed (likely import sorting, a few pyupgrade items like `Optional[X]` → `X | None`). Review the diff briefly to confirm changes are reasonable.

- [ ] **Step 3: Run `ruff format` to apply formatting**

Run: `ruff format eavt_helper tests`
Expected: ruff reformats files in place.

- [ ] **Step 4: Run `ruff check` to confirm clean**

Run: `ruff check eavt_helper tests`
Expected: `All checks passed!`

- [ ] **Step 5: Run the test suite to confirm nothing broke**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 6: Update `Makefile`**

In `Makefile`, replace the `lint:` and `format:` targets with:

```makefile
lint:
	@echo "🔍 Running ruff lint..."
	ruff check eavt_helper tests

format:
	@echo "🎨 Formatting with ruff..."
	ruff format eavt_helper tests
	ruff check --fix eavt_helper tests
```

- [ ] **Step 7: Confirm Makefile targets work**

Run: `make lint`
Expected: `All checks passed!`

Run: `make format`
Expected: ruff reports it's already formatted (no diffs).

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "build: replace flake8 + black with ruff for lint + format"
```

---

## Task 8: Add mypy with strict config

**Files:**
- Modify: `pyproject.toml` — add `[tool.mypy]` config
- Modify: `Makefile` — add `typecheck` target
- Possibly modify: `eavt_helper/classes/snapshot.py`, `eavt_helper/classes/eavt.py` — add type annotations to internal `_with_*` helpers if mypy complains

**Interfaces:**
- Consumes: `mypy>=1.8.0` (already in dev deps from Task 5)
- Produces: `make typecheck` passes cleanly on the `eavt_helper` package

- [ ] **Step 1: Add mypy config to `pyproject.toml`**

Append to `pyproject.toml`:

```toml

[tool.mypy]
python_version = "3.10"
strict = true
files = ["eavt_helper"]
# pandas has incomplete stubs; allow untyped calls when interacting with it.
disallow_untyped_calls = false
warn_return_any = false

[[tool.mypy.overrides]]
module = ["pandas.*", "click.*"]
ignore_missing_imports = true
```

- [ ] **Step 2: Run mypy and read the output**

Run: `mypy eavt_helper`
Expected: mypy will likely report some untyped private helpers (the `_with_*` methods). Read the errors.

- [ ] **Step 3: Annotate the `_with_*` helpers as needed**

In `eavt_helper/classes/snapshot.py`, the private helpers currently look like:

```python
    def _with_drop_snapshot_columns(self, df):
        ...
    def _with_set_index(self, df, list_index):
        ...
```

Add type annotations to each `_with_*` method using `pd.DataFrame` as both parameter and return type where appropriate. Example transformation for the first one:

```python
    def _with_drop_snapshot_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop common snapshot metadata columns."""
        columns_to_drop = ['row_version', 'current_row_indicator', 'row_expiration_tstamp']
        existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]

        if existing_columns_to_drop:
            df = df.drop(columns=existing_columns_to_drop)

        return df
```

Apply the same `(self, df: pd.DataFrame, ...) -> pd.DataFrame` pattern to every other `_with_*` method in **both** `snapshot.py` and `eavt.py`. For `_with_set_index`, use `list_index: list[str]`. For `_with_rename_col`, use `col_from: str, col_to: str`.

- [ ] **Step 4: Re-run mypy until clean**

Run: `mypy eavt_helper`
Expected: `Success: no issues found in N source files`.

If errors remain, fix them. Do **not** disable strict mode globally — use targeted `# type: ignore[error-code]` comments on individual lines if a pandas-stub limitation can't be worked around, and document why in a one-line comment.

- [ ] **Step 5: Add `typecheck` target to `Makefile`**

In `Makefile`, add after the `lint:` target:

```makefile
typecheck:
	@echo "🔎 Running mypy type checks..."
	mypy eavt_helper
```

And update the `help:` target to list it:

```makefile
	@echo "make typecheck      - Run mypy type checks"
```

And add `typecheck` to the `.PHONY:` line.

- [ ] **Step 6: Run the full suite**

Run: `make lint && make typecheck && pytest -q`
Expected: all three pass.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "build: add mypy strict type checking and annotate internal helpers"
```

---

## Task 9: GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the `pyproject.toml` dev extras, `make lint`, `make typecheck`, `pytest`
- Produces: a CI workflow that runs on every push and PR, across Python 3.10/3.11/3.12, that lints, type-checks, and runs tests.

- [ ] **Step 1: Create the workflow file**

Create `.github/workflows/ci.yml` with this content:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install package and dev dependencies
        run: |
          python -m pip install --upgrade pip
          pip install --editable ".[dev]"

      - name: Lint with ruff
        run: ruff check eavt_helper tests

      - name: Check formatting with ruff
        run: ruff format --check eavt_helper tests

      - name: Type-check with mypy
        run: mypy eavt_helper

      - name: Run tests
        run: pytest -q --cov=eavt_helper --cov-report=term-missing
```

- [ ] **Step 2: Verify the workflow file is valid YAML**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
Expected: no output (success).

- [ ] **Step 3: Run the same checks locally to make sure CI will pass**

Run: `ruff check eavt_helper tests && ruff format --check eavt_helper tests && mypy eavt_helper && pytest -q`
Expected: all four checks pass.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for lint, typecheck, and tests on 3.10/3.11/3.12"
```

---

## Task 10: Add CONTRIBUTING.md, CHANGELOG.md, CODE_OF_CONDUCT.md

**Files:**
- Create: `CONTRIBUTING.md`
- Create: `CHANGELOG.md`
- Create: `CODE_OF_CONDUCT.md`

**Interfaces:**
- Consumes: nothing
- Produces: three standard OSS docs at the repo root.

- [ ] **Step 1: Create `CONTRIBUTING.md`**

```markdown
# Contributing to eavt-helper

Thanks for your interest in contributing! This is a small, focused project — please keep PRs small and focused as well.

## Development setup

```bash
git clone https://github.com/vmjulio/eavt-helper.git
cd eavt-helper
pip install --editable ".[dev]"
```

## Running the checks locally

Before opening a PR, make sure all of these pass:

```bash
make lint       # ruff check
make typecheck  # mypy strict
make test       # pytest
```

`make format` will auto-fix lint and formatting issues.

## Pull requests

- Branch from `main`.
- Keep each PR focused on one logical change.
- Add tests for new behavior or bug fixes — see existing tests in `tests/` for style.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `build:`, `ci:`.
- CI must be green before review.

## Reporting bugs

Open an issue with:
- What you ran (the exact CLI command)
- What you expected
- What actually happened (including any traceback)
- Your Python version and OS

A minimal reproducing CSV is enormously helpful.
```

- [ ] **Step 2: Create `CHANGELOG.md`**

```markdown
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--version` flag on the top-level CLI.
- GitHub Actions CI workflow (lint, type-check, test on Python 3.10/3.11/3.12).
- `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`.
- `examples/` directory with sample snapshot, EAVT, and SCD2 CSVs.
- `pyproject.toml` (PEP 621) as single source of truth for package metadata.
- Strict `mypy` type-checking.

### Changed
- License switched from GPL-3.0 to MIT (the classifier and README always said MIT; the `LICENSE` file is now consistent).
- Python floor bumped from 3.8 to 3.10. Dropped 3.8 and 3.9 (both EOL).
- `numpy` upper-pin removed (`<2.0` cap dropped); NumPy 2.x is now supported.
- Linting and formatting unified under `ruff` (replaces `flake8` + `black`).
- README clarified: chunking is per-entity for transformation; the full CSV is still read into memory.

### Fixed
- **Correctness bug:** `Snapshot._process_in_chunks` previously chunked by row index, which could split an entity's history across chunks and emit spurious "change" rows at chunk boundaries. Chunking is now done by entity, mirroring the existing `EAVT` class behavior.

### Removed
- `setup.py` (replaced by `pyproject.toml`).
- `pytest.ini` (config moved into `pyproject.toml`).
- `run_tests.py` (redundant with `make test`).
- Empty `eavt_helper/utils/` package.

## [0.2.0] - prior

Initial public-prep state (see git history for details).
```

- [ ] **Step 3: Create `CODE_OF_CONDUCT.md`**

Use the Contributor Covenant v2.1. Create `CODE_OF_CONDUCT.md` with the exact text from <https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md>, with `[INSERT CONTACT METHOD]` replaced by a real contact (e.g., a GitHub issue link: `Open an issue at https://github.com/vmjulio/eavt-helper/issues`).

If the executor cannot fetch the URL, use this verbatim copy:

```markdown
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders by opening an issue at
https://github.com/vmjulio/eavt-helper/issues.

All complaints will be reviewed and investigated promptly and fairly.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
[https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html
```

- [ ] **Step 4: Run lint on the new files (in case any have formatting issues that ruff cares about — unlikely for `.md`, but harmless)**

Run: `pytest -q`
Expected: all tests pass (these files don't affect tests).

- [ ] **Step 5: Commit**

```bash
git add CONTRIBUTING.md CHANGELOG.md CODE_OF_CONDUCT.md
git commit -m "docs: add CONTRIBUTING, CHANGELOG, and CODE_OF_CONDUCT"
```

---

## Task 11: Add `examples/` folder with sample data

**Files:**
- Create: `examples/snapshot.csv`
- Create: `examples/eavt.csv`
- Create: `examples/scd2.csv`
- Create: `examples/README.md`

**Interfaces:**
- Consumes: the CLI commands `snapshot-to-eavt` and `eavt-to-scd` (must work as installed)
- Produces: a 5-minute walkthrough that a new user can run end-to-end.

- [ ] **Step 1: Create `examples/snapshot.csv`**

Create `examples/snapshot.csv` with this exact content (a tiny user-profile snapshot table with 3 users observed over 3 dates):

```csv
user_id,row_effective_tstamp,name,city,plan
1,2024-01-01,Ana,NYC,free
1,2024-02-01,Ana,NYC,pro
1,2024-03-01,Ana,LA,pro
2,2024-01-01,Bruno,SF,free
2,2024-02-01,Bruno,SF,free
2,2024-03-01,Bruno,SF,pro
3,2024-01-01,Carla,Chicago,pro
3,2024-02-01,Carla,Chicago,pro
3,2024-03-01,Carla,NYC,pro
```

- [ ] **Step 2: Generate the EAVT output by running the CLI**

Run:

```bash
eavt-helper snapshot-to-eavt \
  --id-col user_id \
  --tstamp-col row_effective_tstamp \
  --snapshot-path examples/snapshot.csv \
  --out-path examples/eavt.csv
```

Expected output: `✅ Successfully converted N EAVT records to examples/eavt.csv`

- [ ] **Step 3: Generate the SCD2 output by running the CLI**

Run:

```bash
eavt-helper eavt-to-scd \
  --eavt-path examples/eavt.csv \
  --out-path examples/scd2.csv
```

Expected output: `✅ Successfully converted N SCD2 records to examples/scd2.csv`

- [ ] **Step 4: Inspect the generated files**

Run: `head examples/eavt.csv examples/scd2.csv`
Confirm both files are sensible — EAVT should have `e,a,v,t` columns; SCD2 should have `id,row_effective_tstamp,…,row_version,current_row_indicator`.

- [ ] **Step 5: Create `examples/README.md`**

```markdown
# Examples

A 5-minute walkthrough.

## The three shapes

This project deals with three ways to represent the history of an entity over time:

| Shape | When you have it | What it looks like |
|---|---|---|
| **Snapshot** | A table dumped at each observation date — one row per entity per date. | `snapshot.csv` |
| **EAVT log** | An append-only event log of attribute changes. One row per `(entity, attribute, new_value, time)`. | `eavt.csv` |
| **SCD Type 2** | A wide table with `row_effective_tstamp` / `row_expiration_tstamp` columns marking each version's validity window. | `scd2.csv` |

The CLI converts `Snapshot → EAVT → SCD2`.

## Reproduce the outputs

From the repo root:

```bash
# Snapshot → EAVT
eavt-helper snapshot-to-eavt \
  --id-col user_id \
  --tstamp-col row_effective_tstamp \
  --snapshot-path examples/snapshot.csv \
  --out-path /tmp/eavt.csv

# EAVT → SCD2
eavt-helper eavt-to-scd \
  --eavt-path /tmp/eavt.csv \
  --out-path /tmp/scd2.csv
```

The `/tmp/` outputs should match `examples/eavt.csv` and `examples/scd2.csv` (up to row ordering).
```

- [ ] **Step 6: Commit**

```bash
git add examples/
git commit -m "docs: add examples/ folder with sample snapshot, EAVT, and SCD2 CSVs"
```

---

## Task 12: README rewrite — fix claims, add the "why", add badges

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing
- Produces: a README that opens with the "why EAVT", correctly describes chunking (per-entity, not per-row; full file is still loaded into memory), references `examples/`, and shows a CI badge.

- [ ] **Step 1: Replace `README.md` with the rewritten version**

Overwrite `README.md` with this exact content:

````markdown
# eavt-helper

[![CI](https://github.com/vmjulio/eavt-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/vmjulio/eavt-helper/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

A small CLI for converting between three common ways of representing entity history over time:

```
   Snapshot  ───►  EAVT log  ───►  SCD Type 2
```

## Why these three shapes?

If you've worked with slowly-changing data, you've probably hit all three:

- **Snapshots** are easy to produce (just dump the table every day) but wasteful — most rows are unchanged copies of the previous day's row.
- **EAVT logs** (`entity, attribute, value, time`) are the change-data-capture form: append-only, one row per actual change. Compact, but awkward to query without pivoting.
- **SCD Type 2** is the warehouse-friendly form: wide rows with `row_effective_tstamp` and `row_expiration_tstamp` marking each version's validity window. Easy to query "what did this row look like on date X."

This tool converts one shape into the next. See `examples/` for a 5-minute walkthrough.

## Install

```bash
pip install --editable .
```

(PyPI release coming.)

## Usage

### Snapshot → EAVT

Your CSV needs a unique entity-id column and a timestamp column marking when the snapshot was taken.

```bash
eavt-helper snapshot-to-eavt \
  --id-col user_id \
  --tstamp-col row_effective_tstamp \
  --snapshot-path snapshot.csv \
  --out-path eavt.csv
```

### EAVT → SCD Type 2

Your EAVT log must have columns `e`, `a`, `v`, `t`.

```bash
eavt-helper eavt-to-scd \
  --eavt-path eavt.csv \
  --out-path scd2.csv
```

### Chunked processing

For larger datasets, pass `--chunk-size`:

```bash
eavt-helper snapshot-to-eavt -i user_id -t row_effective_tstamp \
  -p snapshot.csv -o eavt.csv --chunk-size 10000
```

**What chunking does and doesn't do:** the CSV is still read into memory in full (pandas `read_csv`). Chunking applies to the *transformation* step — the dataset is processed in batches **grouped by entity ID** so an entity's full history is never split across chunks. This bounds peak memory during the pivot/stack/groupby steps, which is usually the spike. For truly large datasets (tens of GB), reach for DuckDB or Polars instead.

## Development

```bash
pip install --editable ".[dev]"
make lint        # ruff
make typecheck   # mypy strict
make test        # pytest
make format      # auto-fix lint + formatting
```

See `CONTRIBUTING.md` for the PR workflow.

## Requirements

- Python 3.10+
- pandas >= 1.3
- click >= 8.0
- numpy >= 1.20

## License

MIT — see `LICENSE`.
````

- [ ] **Step 2: Verify everything still passes**

Run: `make lint && make typecheck && pytest -q`
Expected: all green.

- [ ] **Step 3: Verify the README renders sensibly**

Open `README.md` in a markdown previewer (or just `cat` it and skim). Confirm:
- Three badges show at the top
- The "Why these three shapes?" section is present
- Chunking section honestly states the in-memory caveat
- License section says MIT

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README — add 'why EAVT' section, correct chunking claim, add badges"
```

---

## Self-Review Checklist

Before marking this plan complete, the executor (or reviewer) should confirm:

- [ ] License says MIT consistently in `LICENSE`, `pyproject.toml`, and `README.md`
- [ ] `pyproject.toml` exists; `setup.py` and `pytest.ini` are gone
- [ ] `eavt-helper --version` works
- [ ] `tests/test_chunking.py` exists and its tests pass
- [ ] `ruff check`, `mypy eavt_helper`, and `pytest -q` all pass locally
- [ ] `.github/workflows/ci.yml` exists and the YAML is valid
- [ ] `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md` exist
- [ ] `examples/` folder has `snapshot.csv`, `eavt.csv`, `scd2.csv`, and `README.md`
- [ ] README has the three badges, the "why" section, the honest chunking description, and the MIT license line
- [ ] `eavt_helper/utils/` is gone
- [ ] `run_tests.py` is gone
- [ ] Twelve commits land on the branch, each one a single logical change with a Conventional Commits prefix

## Out of Scope (Deferred)

The following were discussed but explicitly deferred to a future round:

- **Parquet support** — sniff by extension and use `pd.read_parquet` / `to_parquet`. High ROI, but a behavior change.
- **DuckDB / Polars backend** — the real answer for "large datasets," but a substantial architectural change.
- **Property-based round-trip tests** — `snapshot → eavt → scd2 → snapshot'` identity test using `hypothesis`. Would have caught the chunking bug automatically.
- **PyPI publication** — after this round, a release-please workflow + first PyPI upload.
- **Append/idempotent mode** — extending an existing EAVT log with a new snapshot.
