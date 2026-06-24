"""Tests for main CLI functionality."""

from click.testing import CliRunner
from eavt_helper.main import cli


class TestMainCLI:
    """Test cases for main CLI functionality."""

    def test_cli_help(self):
        """Test that CLI help command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_cli_no_command(self):
        """Test CLI behavior when no command is provided."""
        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code in (0, 2)
        assert "Usage:" in result.output

    def test_cli_invalid_command(self):
        """Test CLI behavior with invalid command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["invalid-command"])

        assert result.exit_code != 0
        assert "No such command" in result.output

    def test_cli_snapshot_to_eavt_command_exists(self):
        """Test that snapshot-to-eavt command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["snapshot-to-eavt", "--help"])

        assert result.exit_code == 0
        assert "snapshot-to-eavt" in result.output
        assert "--snapshot-path" in result.output
        assert "--id-column" in result.output
        assert "--tstamp-column" in result.output
        assert "--out-path" in result.output
        assert "--chunk-size" in result.output

    def test_cli_eavt_to_scd_command_exists(self):
        """Test that eavt-to-scd command is available."""
        runner = CliRunner()
        result = runner.invoke(cli, ["eavt-to-scd", "--help"])

        assert result.exit_code == 0
        assert "eavt-to-scd" in result.output
        assert "--eavt-path" in result.output
        assert "--out-path" in result.output
        assert "--chunk-size" in result.output

    def test_cli_commands_have_proper_help_text(self):
        """Test that commands have proper help text."""
        runner = CliRunner()

        # Test snapshot-to-eavt help
        result = runner.invoke(cli, ["snapshot-to-eavt", "--help"])
        assert "Convert snapshot table to EAVT log format" in result.output

        # Test eavt-to-scd help
        result = runner.invoke(cli, ["eavt-to-scd", "--help"])
        assert "Convert EAVT log to Slowly Changing Dimension Type 2 format" in result.output

    def test_cli_short_and_long_options(self):
        """Test that both short and long options are available."""
        runner = CliRunner()

        # Test snapshot-to-eavt options
        result = runner.invoke(cli, ["snapshot-to-eavt", "--help"])
        assert "-p" in result.output and "--snapshot-path" in result.output
        assert "-i" in result.output and "--id-column" in result.output
        assert "-t" in result.output and "--tstamp-column" in result.output
        assert "-o" in result.output and "--out-path" in result.output

        # Test eavt-to-scd options
        result = runner.invoke(cli, ["eavt-to-scd", "--help"])
        assert "-p" in result.output and "--eavt-path" in result.output
        assert "-o" in result.output and "--out-path" in result.output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_cli_error_handling(self):
        """Test that CLI handles errors gracefully."""
        runner = CliRunner()

        # Test snapshot-to-eavt with missing required arguments
        result = runner.invoke(cli, ["snapshot-to-eavt"])
        assert result.exit_code != 0

        # Test eavt-to-scd with missing required arguments
        result = runner.invoke(cli, ["eavt-to-scd"])
        assert result.exit_code != 0


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
