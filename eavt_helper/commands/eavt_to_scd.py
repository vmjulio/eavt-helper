"""
Sub command to transform an eavt log into a slowly changing dimension
"""
from eavt_helper.utils import (read_dataframe_from_csv,
                               write_dataframe_to_csv)
import click


@click.command()
@click.argument("snapshot_path")
@click.argument("out_path")
def eavt_to_scd(snapshot_path, out_path="out_scd.csv"):
    eavt_df = read_dataframe_from_csv(snapshot_path)
    df = eavt_df.pivot(index=['e', 't'], columns='a', values='v')
    df = df.ffill(axis=0)
    df = df.reset_index()
    df['row_expiration_tstamp'] = df.sort_values(by=['t'], ascending=False)\
                                    .groupby(['e'])['t'].shift(1)
    df['current_row_indicator'] = (df.sort_values(['t'], ascending=False)\
                                     .groupby(['e']).cumcount() + 1) == 1
    df["id"] = df["e"]
    df["row_effective_tstamp"] = df["t"]
    df = df.drop(columns=["e", "t"])
    write_dataframe_to_csv(df, out_path)
