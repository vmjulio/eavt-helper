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
  --id-column user_id \
  --tstamp-column row_effective_tstamp \
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

