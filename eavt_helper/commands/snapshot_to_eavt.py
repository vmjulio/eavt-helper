"""
Sub command to transform a snapshot into an eavt log
"""
from eavt_helper.utils import (read_dataframe_from_csv,
                               write_dataframe_to_csv)
import click


@click.command()
@click.argument("snapshot_path")
@click.argument("id_col")
@click.argument("tstamp_col")
@click.argument("out_path")
def snapshot_to_eavt(snapshot_path, id_col="id", tstamp_col="run", out_path="out.csv"):
    snapshot_df = read_dataframe_from_csv(snapshot_path)
    df = snapshot_df.set_index([id_col, tstamp_col])
    df = df.stack().reset_index()
    df.rename(columns={'id': 'e', 'level_2':
                       'a', 0: 'v', 'run': 't'}, inplace=True)
    df = df[['e', 'a', 'v', 't']]
    df['v_lag'] = df.sort_values(by=['t'], ascending=True)\
                    .groupby(['e', 'a'])['v'].shift(1)
    df = df[df["v"] != df["v_lag"]]
    df = df.drop(columns=["v_lag"])
    write_dataframe_to_csv(df, out_path)
