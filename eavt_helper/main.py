""" Entrypoint of the CLI """
import click
from eavt_helper.commands import snapshot_to_eavt, eavt_to_scd


@click.group()
def cli():
    pass


cli.add_command(snapshot_to_eavt)
cli.add_command(eavt_to_scd)
