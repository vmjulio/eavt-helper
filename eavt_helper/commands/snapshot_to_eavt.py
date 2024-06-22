"""
Sub command to transform a snapshot into an eavt log
"""
import eavt_helper.help as h
from eavt_helper.classes.snapshot import Snapshot
import click


@click.command()
@click.option("-p", "--snapshot-path", "snapshot_path",
              type=str, required=True, help=h.SNAPSHOT__IN_PATH)
@click.option("-i", "--id-column", "id_col",
              type=str, required=True, help=h.SNAPSHOT__ID_COLUMN)
@click.option("-t", "--tstamp-column", "tstamp_col",
              type=str, required=True, help=h.SNAPSHOT__TSTAMP_COLUMN)
@click.option("-o", "--out-path", "out_path",
              type=str, required=True, help=h.SNAPSHOT__OUT_PATH)
def snapshot_to_eavt(snapshot_path, id_col="id", tstamp_col="run", out_path="out.csv"):
    snapshot = Snapshot(snapshot_path, id_col=id_col, tstamp_col=tstamp_col)
    eavt_df= snapshot.transform_to_eavt()
    eavt_df.to_csv(out_path, index=False)
