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
