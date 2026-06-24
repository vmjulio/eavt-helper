"""
Sub command to transform an eavt log into a slowly changing dimension
"""
import eavt_helper.help as h
from eavt_helper.classes.eavt import EAVT
import click
import sys


@click.command()
@click.option("-p", "--eavt-path", "eavt_path", type=str, required=True, help=h.EAVT__IN_PATH)
@click.option("-o", "--out-path", "out_path", type=str, required=True, help=h.EAVT__OUT_PATH)
@click.option("--chunk-size", "chunk_size",
              type=int, help=h.EAVT__CHUNK_SIZE)
def eavt_to_scd(eavt_path, out_path, chunk_size=None):
    """Convert EAVT log to Slowly Changing Dimension Type 2 format."""
    try:
        click.echo("🔄 Starting EAVT to SCD2 transformation...")
        
        # Initialize and validate EAVT
        eavt = EAVT(eavt_path)
        
        # Transform to SCD2
        scd2_df = eavt.transform_to_scd2(chunk_size=chunk_size)
        
        # Save output
        click.echo(f"💾 Saving SCD2 table to {out_path}...")
        scd2_df.to_csv(out_path, index=False)
        
        click.echo(f"✅ Successfully converted {len(scd2_df)} SCD2 records to {out_path}")
        
    except Exception as e:
        click.echo(f"❌ Transformation failed: {str(e)}", err=True)
        sys.exit(1)
