import pandas as pd


def read_dataframe_from_csv(path):
    return pd.read_csv(path)


def write_dataframe_to_csv(df, path):
    df.to_csv(path, index=False)


def eavt_to_scd(eavt_df):
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
    return df
