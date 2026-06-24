# EAVT Helper CLI

A robust CLI tool to convert snapshots into EAVT logs, and EAVT logs into Slowly Changing Dimensions (SCD Type 2).

## Features

- ✅ **Snapshot to EAVT conversion**: Transform snapshot tables into efficient EAVT logs
- ✅ **EAVT to SCD2 conversion**: Convert EAVT logs into Slowly Changing Dimension Type 2 format
- ✅ **Memory-efficient processing**: Handle large datasets with chunked processing
- ✅ **Comprehensive validation**: Input validation and error handling
- ✅ **Progress tracking**: Visual progress bars for large datasets
- ✅ **Robust error handling**: Clear error messages and graceful failure handling

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Snapshot to EAVT Log](#snapshot-to-eavt-log)
  - [EAVT Log to Slowly Changing Dimension](#eavt-log-to-slowly-changing-dimension)
- [Performance Optimization](#performance-optimization)
- [Development](#development)
- [Testing](#testing)

## Installation

### From Source
Clone the repository and install in development mode:

```bash
git clone https://github.com/vmjulio/eavt-helper.git
cd eavt-helper
pip install --editable .
```

### Development Installation
Install with development dependencies:

```bash
pip install --editable .[dev]
```

## Usage

### Snapshot to EAVT Log

Convert a snapshot table into an EAVT log. Your CSV must have:
- A unique column identifying entities (`--id-col`)
- A timestamp column (`--tstamp-col`) indicating when the snapshot was taken

**Basic Usage:**
```bash
eavt-helper snapshot-to-eavt \
  --id-col user_id \
  --tstamp-col row_effective_tstamp \
  --snapshot-path snapshot.csv \
  --out-path output.csv
```

**Short Form:**
```bash
eavt-helper snapshot-to-eavt \
  -i user_id \
  -t row_effective_tstamp \
  -p snapshot.csv \
  -o output.csv
```

**Large Dataset Processing:**
```bash
eavt-helper snapshot-to-eavt \
  -i user_id \
  -t row_effective_tstamp \
  -p large_snapshot.csv \
  -o output.csv \
  --chunk-size 10000
```

### EAVT Log to Slowly Changing Dimension

Convert an EAVT log into SCD Type 2 format. Your EAVT log must have columns: `e`, `a`, `v`, `t`.

**Basic Usage:**
```bash
eavt-helper eavt-to-scd \
  --eavt-path eavt_log.csv \
  --out-path output_scd2.csv
```

**Short Form:**
```bash
eavt-helper eavt-to-scd -p eavt_log.csv -o output_scd2.csv
```

**Large Dataset Processing:**
```bash
eavt-helper eavt-to-scd \
  -p large_eavt_log.csv \
  -o output_scd2.csv \
  --chunk-size 5000
```

## Performance Optimization

### Chunked Processing

For large datasets, use the `--chunk-size` parameter to process data in chunks:

- **Snapshot to EAVT**: Processes rows in chunks of specified size
- **EAVT to SCD2**: Processes entities in chunks to maintain data integrity

**Recommended chunk sizes:**
- Small datasets (< 100K rows): No chunking needed
- Medium datasets (100K - 1M rows): `--chunk-size 10000`
- Large datasets (> 1M rows): `--chunk-size 50000`

### Memory Management

The tool automatically:
- Validates input data before processing
- Provides progress indicators for long-running operations
- Uses efficient pandas operations with method chaining
- Manages memory usage through chunked processing

## Development

### Project Structure
```
eavt-helper/
├── eavt_helper/
│   ├── classes/           # Core transformation classes
│   ├── commands/          # CLI command implementations
│   ├── help/              # Help text and documentation
│   └── main.py           # CLI entry point
├── tests/                 # Unit tests
├── setup.py              # Package configuration
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=eavt_helper

# Run specific test file
pytest tests/test_snapshot.py

# Run tests with verbose output
pytest -v
```

### Code Quality

The project includes:
- Comprehensive unit tests with pytest
- Type hints for better code clarity
- Docstrings for all public methods
- Error handling and input validation
- Progress tracking for user feedback

## Requirements

- Python 3.8+
- pandas >= 1.3.0
- click >= 8.0.0
- numpy >= 1.20.0

## License

This project is licensed under the MIT License - see the LICENSE file for details.

