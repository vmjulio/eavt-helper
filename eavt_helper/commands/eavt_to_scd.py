"""
Sub command to transform an eavt log into a slowly changing dimension
"""
import eavt_helper.help as h
from eavt_helper.classes.eavt import EAVT
import click


@click.command()
@click.option("-p", "--eavt-path", "eavt_path", type=str, required=True, help=h.EAVT__IN_PATH)
@click.option("-o", "--out-path", "out_path", type=str, required=True, help=h.EAVT__OUT_PATH)
def eavt_to_scd(eavt_path, out_path="out_scd.csv"):
    eavt = EAVT(eavt_path)
    scd2_df = eavt.transform_to_scd2()
    scd2_df.to_csv(out_path, index=False)
