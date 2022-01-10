# EAVT helper CLI
Simple CLI to convert snapshots into eavt log, and eavt log into slowly changing dimensions

- [Usage](#usage)
  - [Installation](#installation)
  - [Snapshot to EAVT log](#snapshot-to-eavt-log)
  - [EAVT log to Slowly Changing Dimension](#eavt-log-to-slowly-changing-dimension)

## Usage

### Installation
Clone the repository. Then browse to the project folder install the package in the dev mode:
```bash
  $ pip3 install --editable .
```

### Snapshot to EAVT log

To convert a snapshot table into an EAVT log, make sure your csv have an unique column identifying the entities, and a date (or timestamp) column with the information of the time of the entity snapshot:

```bash
$ eavt_helper snapshot-to-eavt snapshot_table.csv id_col time_col out_eavt_file.csv
```

---

### EAVT log to Slowly Changing Dimension

To convert an EAVT log into a Slowly Changing Dimension:

```bash
$ eavt_helper eavt-to-scd eavt_log.csv out_scd_file.csv
```
