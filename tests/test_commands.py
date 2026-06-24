"""Tests for CLI commands."""

import os
import tempfile

import pandas as pd
from click.testing import CliRunner
from eavt_helper.commands.eavt_to_scd import eavt_to_scd
from eavt_helper.commands.snapshot_to_eavt import snapshot_to_eavt


class TestSnapshotToEavtCommand:
    """Test cases for snapshot_to_eavt CLI command."""

    def setup_method(self):
        """Set up test data and files."""
        self.test_data = pd.DataFrame(
            {
                "user_id": [1, 1, 2, 2],
                "timestamp": ["2023-01-01", "2023-01-02", "2023-01-01", "2023-01-02"],
                "name": ["John", "John", "Jane", "Jane"],
                "age": [25, 26, 30, 30],
                "city": ["NYC", "NYC", "LA", "SF"],
            }
        )

        # Create temporary input file
        self.input_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        self.test_data.to_csv(self.input_file.name, index=False)
        self.input_file.close()

        # Create temporary output file path
        self.output_file = tempfile.NamedTemporaryFile(delete=False)
        self.output_file.close()

    def teardown_method(self):
        """Clean up test files."""
        for file_path in [self.input_file.name, self.output_file.name]:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_snapshot_to_eavt_success(self):
        """Test successful snapshot to EAVT conversion via CLI."""
        runner = CliRunner()
        result = runner.invoke(
            snapshot_to_eavt,
            [
                "--snapshot-path",
                self.input_file.name,
                "--id-column",
                "user_id",
                "--tstamp-column",
                "timestamp",
                "--out-path",
                self.output_file.name,
            ],
        )

        assert result.exit_code == 0
        assert "✅ Successfully converted" in result.output

        # Verify output file was created and has correct structure
        assert os.path.exists(self.output_file.name)
        output_df = pd.read_csv(self.output_file.name)
        assert list(output_df.columns) == ["e", "a", "v", "t"]

    def test_snapshot_to_eavt_short_options(self):
        """Test snapshot to EAVT conversion with short option flags."""
        runner = CliRunner()
        result = runner.invoke(
            snapshot_to_eavt,
            [
                "-p",
                self.input_file.name,
                "-i",
                "user_id",
                "-t",
                "timestamp",
                "-o",
                self.output_file.name,
            ],
        )

        assert result.exit_code == 0
        assert "✅ Successfully converted" in result.output

    def test_snapshot_to_eavt_with_chunk_size(self):
        """Test snapshot to EAVT conversion with chunk size parameter."""
        runner = CliRunner()
        result = runner.invoke(
            snapshot_to_eavt,
            [
                "--snapshot-path",
                self.input_file.name,
                "--id-column",
                "user_id",
                "--tstamp-column",
                "timestamp",
                "--out-path",
                self.output_file.name,
                "--chunk-size",
                "2",
            ],
        )

        assert result.exit_code == 0
        assert "✅ Successfully converted" in result.output

    def test_snapshot_to_eavt_missing_file(self):
        """Test error handling when input file is missing."""
        runner = CliRunner()
        result = runner.invoke(
            snapshot_to_eavt,
            [
                "--snapshot-path",
                "nonexistent.csv",
                "--id-column",
                "user_id",
                "--tstamp-column",
                "timestamp",
                "--out-path",
                self.output_file.name,
            ],
        )

        assert result.exit_code == 1
        assert "❌ Transformation failed" in result.output

    def test_snapshot_to_eavt_missing_column(self):
        """Test error handling when required column is missing."""
        runner = CliRunner()
        result = runner.invoke(
            snapshot_to_eavt,
            [
                "--snapshot-path",
                self.input_file.name,
                "--id-column",
                "missing_column",
                "--tstamp-column",
                "timestamp",
                "--out-path",
                self.output_file.name,
            ],
        )

        assert result.exit_code == 1
        assert "❌ Transformation failed" in result.output

    def test_snapshot_to_eavt_missing_required_args(self):
        """Test error when required arguments are missing."""
        runner = CliRunner()
        result = runner.invoke(
            snapshot_to_eavt,
            [
                "--snapshot-path",
                self.input_file.name,
                # Missing required --id-column, --tstamp-column, --out-path
            ],
        )

        assert result.exit_code != 0


class TestEavtToScdCommand:
    """Test cases for eavt_to_scd CLI command."""

    def setup_method(self):
        """Set up test data and files."""
        self.test_eavt_data = pd.DataFrame(
            {
                "e": [1, 1, 2, 2],
                "a": ["name", "age", "name", "age"],
                "v": ["John", 26, "Jane", 30],
                "t": ["2023-01-02", "2023-01-02", "2023-01-01", "2023-01-01"],
            }
        )

        # Create temporary input file
        self.input_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        self.test_eavt_data.to_csv(self.input_file.name, index=False)
        self.input_file.close()

        # Create temporary output file path
        self.output_file = tempfile.NamedTemporaryFile(delete=False)
        self.output_file.close()

    def teardown_method(self):
        """Clean up test files."""
        for file_path in [self.input_file.name, self.output_file.name]:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_eavt_to_scd_success(self):
        """Test successful EAVT to SCD2 conversion via CLI."""
        runner = CliRunner()
        result = runner.invoke(
            eavt_to_scd, ["--eavt-path", self.input_file.name, "--out-path", self.output_file.name]
        )

        assert result.exit_code == 0
        assert "✅ Successfully converted" in result.output

        # Verify output file was created and has SCD2 structure
        assert os.path.exists(self.output_file.name)
        output_df = pd.read_csv(self.output_file.name)

        # Check for SCD2 columns
        expected_cols = [
            "id",
            "row_effective_tstamp",
            "row_expiration_tstamp",
            "row_version",
            "current_row_indicator",
        ]
        for col in expected_cols:
            assert col in output_df.columns

    def test_eavt_to_scd_short_options(self):
        """Test EAVT to SCD2 conversion with short option flags."""
        runner = CliRunner()
        result = runner.invoke(
            eavt_to_scd, ["-p", self.input_file.name, "-o", self.output_file.name]
        )

        assert result.exit_code == 0
        assert "✅ Successfully converted" in result.output

    def test_eavt_to_scd_with_chunk_size(self):
        """Test EAVT to SCD2 conversion with chunk size parameter."""
        runner = CliRunner()
        result = runner.invoke(
            eavt_to_scd,
            [
                "--eavt-path",
                self.input_file.name,
                "--out-path",
                self.output_file.name,
                "--chunk-size",
                "2",
            ],
        )

        assert result.exit_code == 0
        assert "✅ Successfully converted" in result.output

    def test_eavt_to_scd_missing_file(self):
        """Test error handling when input file is missing."""
        runner = CliRunner()
        result = runner.invoke(
            eavt_to_scd, ["--eavt-path", "nonexistent.csv", "--out-path", self.output_file.name]
        )

        assert result.exit_code == 1
        assert "❌ Transformation failed" in result.output

    def test_eavt_to_scd_invalid_eavt_format(self):
        """Test error handling when EAVT file has invalid format."""
        # Create invalid EAVT data (missing required columns)
        invalid_data = pd.DataFrame(
            {
                "entity": [1, 2],
                "attribute": ["name", "age"],
                "value": ["John", 25],
                # Missing 't' column
            }
        )

        invalid_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        invalid_data.to_csv(invalid_file.name, index=False)
        invalid_file.close()

        try:
            runner = CliRunner()
            result = runner.invoke(
                eavt_to_scd, ["--eavt-path", invalid_file.name, "--out-path", self.output_file.name]
            )

            assert result.exit_code == 1
            assert "❌ Transformation failed" in result.output
        finally:
            os.unlink(invalid_file.name)

    def test_eavt_to_scd_missing_required_args(self):
        """Test error when required arguments are missing."""
        runner = CliRunner()
        result = runner.invoke(
            eavt_to_scd,
            [
                "--eavt-path",
                self.input_file.name,
                # Missing required --out-path
            ],
        )

        assert result.exit_code != 0
