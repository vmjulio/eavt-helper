"""
Sub command to transform a snapshot into an eavt log
"""

import sys

import click

import eavt_helper.help as h
from eavt_helper.classes.snapshot import Snapshot


@click.command()
@click.option(
    "-p", "--snapshot-path", "snapshot_path", type=str, required=True, help=h.SNAPSHOT__IN_PATH
)
@click.option("-i", "--id-column", "id_col", type=str, required=True, help=h.SNAPSHOT__ID_COLUMN)
@click.option(
    "-t", "--tstamp-column", "tstamp_col", type=str, required=True, help=h.SNAPSHOT__TSTAMP_COLUMN
)
@click.option("-o", "--out-path", "out_path", type=str, required=True, help=h.SNAPSHOT__OUT_PATH)
@click.option("--chunk-size", "chunk_size", type=int, help=h.SNAPSHOT__CHUNK_SIZE)
def snapshot_to_eavt(snapshot_path: str, id_col: str, tstamp_col: str, out_path: str, chunk_size: int | None = None) -> None:
    """Convert snapshot table to EAVT log format."""
    try:
        click.echo("🔄 Starting snapshot to EAVT transformation...")

        # Initialize and validate snapshot
        snapshot = Snapshot(snapshot_path, id_col=id_col, tstamp_col=tstamp_col)

        # Transform to EAVT
        eavt_df = snapshot.transform_to_eavt(chunk_size=chunk_size)

        # Save output
        click.echo(f"💾 Saving EAVT log to {out_path}...")
        eavt_df.to_csv(out_path, index=False)

        click.echo(f"✅ Successfully converted {len(eavt_df)} EAVT records to {out_path}")

    except Exception as e:
        click.echo(f"❌ Transformation failed: {str(e)}", err=True)
        sys.exit(1)
