"""
Sub command to transform an eavt log into a slowly changing dimension
"""
from eavt_helper.utils import (read_dataframe_from_csv,
                               write_dataframe_to_csv)
import click


@click.command()
@click.argument("eavt_path")
@click.argument("out_path")
def eavt_to_scd(eavt_path, out_path="out_scd.csv"):
    eavt_df = read_dataframe_from_csv(eavt_path)
    df = (eavt_df.pipe(with_pivot_eavt)
                 .pipe(with_ffil)
                 .pipe(with_reset_index)
                 .pipe(with_row_expiration_tstamp)
                 .pipe(with_current_row_indicator)
                 .pipe(with_rename_col, "e", "id")
                 .pipe(with_rename_col, "t", "row_effective_tstamp"))
    write_dataframe_to_csv(df, out_path)

def with_pivot_eavt(df):
    return df.pivot(index=['e', 't'], columns='a', values='v')

def with_stack_reset_index(df):
    return df.stack().reset_index()

def with_ffil(df):
    return df.ffill(axis=0)

def with_row_expiration_tstamp(df):
    df['row_expiration_tstamp'] = df.sort_values(by=['t'], ascending=False)\
                                    .groupby(['e'])['t'].shift(1)
    return df

def with_current_row_indicator(df):
    df['row_version'] = (df.sort_values(['t']).groupby(['e']).cumcount() + 1)
    df['current_row_indicator'] = (df.sort_values(['t'], ascending=False)\
                                     .groupby(['e']).cumcount() + 1) == 1
    return df

def with_reset_index(df):
    return df.reset_index()

def with_rename_col(df, col_from, col_to):
    return df.rename(columns={col_from: col_to})
