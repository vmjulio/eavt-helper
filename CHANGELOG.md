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
