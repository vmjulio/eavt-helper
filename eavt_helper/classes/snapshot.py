import pandas as pd


class Snapshot:
    def __init__(self, snapshot_path: str, id_col: str, tstamp_col: str):
        self.id_col = id_col
        self.tstamp_col = tstamp_col
        self.df = pd.read_csv(snapshot_path)
    
    def transform_to_eavt(self) -> pd.DataFrame:
        return (self.df.pipe(self._with_set_index, [self.id_col, self.tstamp_col])
                       .pipe(self._with_drop_snapshot_columns)
                       .pipe(self._with_stack_reset_index)
                       .pipe(self._with_rename_cols_eavt, self.id_col, self.tstamp_col)
                       .pipe(self._with_order_eavt)
                       .pipe(self._with_v_lag)
                       .pipe(self._with_different_v_lag)
                       .pipe(self._with_drop_v_lag))

    def _with_drop_snapshot_columns(self, df):
        if 'row_version' in df.columns:
            df = df.drop(columns=["row_version"])
        if 'current_row_indicator' in df.columns:
            df = df.drop(columns=["current_row_indicator"])
        if 'row_expiration_tstamp' in df.columns:
            df = df.drop(columns=["row_expiration_tstamp"])
        return df
        
    def _with_set_index(self, df, list_index):
        return df.set_index(list_index)

    def _with_stack_reset_index(self, df):
        return df.stack().reset_index()

    def _with_rename_cols_eavt(self, df, id_col, tstamp_col):
        return df.rename(columns={id_col: 'e', 'level_2': 'a', 0: 'v', tstamp_col: 't'})

    def _with_order_eavt(self, df):
        return df[['e', 'a', 'v', 't']]

    def _with_v_lag(self, df):
        df["v_lag"] = df.sort_values(by=['t'], ascending=True).groupby(['e', 'a'])['v'].shift(1)
        return df

    def _with_different_v_lag(self, df):
        return df[df["v"] != df["v_lag"]]

    def _with_drop_v_lag(self, df):
        return df.drop(columns=["v_lag"])
