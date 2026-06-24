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
  --id-column user_id \
  --tstamp-column row_effective_tstamp \
  --snapshot-path examples/snapshot.csv \
  --out-path /tmp/eavt.csv

# EAVT → SCD2
eavt-helper eavt-to-scd \
  --eavt-path /tmp/eavt.csv \
  --out-path /tmp/scd2.csv
```

The `/tmp/` outputs should match `examples/eavt.csv` and `examples/scd2.csv` (up to row ordering).
