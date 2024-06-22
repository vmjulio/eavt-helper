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
To convert a snapshot table into an EAVT log, make sure your csv has an unique column identifying the entities (--id-col), and a date or timestamp column with the information of the time of the entity snapshot (--tstamp-col):
```bash
eavt-helper snapshot-to-eavt --id-col user_id --tstamp-col row_effective_tstamp --snapshot-path snapshot.csv --out-path output.csv ```

Or, alternatively:
```bash
eavt-helper snapshot-to-eavt -i user_id -t row_effective_tstamp -p snapshot.csv -o output.csv ```

---

### EAVT log to Slowly Changing Dimension

Make sure your EAVT log has the column headers as "e", "a", "v", "t". To convert an EAVT log into a Slowly Changing Dimension type 2:

```bash
eavt-helper eavt-to-scd -p eavt_log.csv -o output_scd2.csv
```

Or, alternatively:
```bash
eavt-helper eavt-to-scd --eavt-path eavt_log.csv --out-path output_scd2.csv
```

