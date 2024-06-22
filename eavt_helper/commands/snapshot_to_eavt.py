"""
Sub command to transform a snapshot into an eavt log
"""
from eavt_helper.utils import (read_dataframe_from_csv, write_dataframe_to_csv)
import eavt_helper.help as h
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
    snapshot_df = read_dataframe_from_csv(snapshot_path)
    df = (snapshot_df.pipe(with_set_index, [id_col, tstamp_col])
                     .pipe(with_drop_snapshot_columns)
                     .pipe(with_stack_reset_index)
                     .pipe(with_rename_cols_eavt, id_col, tstamp_col)
                     .pipe(with_order_eavt)
                     .pipe(with_v_lag)
                     .pipe(with_different_v_lag)
                     .pipe(with_drop_v_lag))
    write_dataframe_to_csv(df, out_path)

def with_drop_snapshot_columns(df):
    if 'row_version' in df.columns:
        df = df.drop(columns=["row_version"])
    if 'current_row_indicator' in df.columns:
        df = df.drop(columns=["current_row_indicator"])
    if 'row_expiration_tstamp' in df.columns:
        df = df.drop(columns=["row_expiration_tstamp"])
    return df
    
def with_set_index(df, list_index):
    return df.set_index(list_index)

def with_stack_reset_index(df):
    return df.stack().reset_index()

def with_rename_cols_eavt(df, id_col, tstamp_col):
    return df.rename(columns={id_col: 'e', 'level_2': 'a', 0: 'v', tstamp_col: 't'})

def with_order_eavt(df):
    return df[['e', 'a', 'v', 't']]

def with_v_lag(df):
    df["v_lag"] = df.sort_values(by=['t'], ascending=True).groupby(['e', 'a'])['v'].shift(1)
    return df

def with_different_v_lag(df):
    return df[df["v"] != df["v_lag"]]

def with_drop_v_lag(df):
    return df.drop(columns=["v_lag"])
