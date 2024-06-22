import pandas as pd


class EAVT:
    def __init__(self, eavt_path: str):
        self.df = pd.read_csv(eavt_path)

    def transform_to_scd2(self) -> pd.DataFrame:
        return (self.df.pipe(self._with_pivot_eavt)
                       .pipe(self._with_ffil)
                       .pipe(self._with_reset_index)
                       .pipe(self._with_row_expiration_tstamp)
                       .pipe(self._with_current_row_indicator)
                       .pipe(self._with_rename_col, "e", "id")
                       .pipe(self._with_rename_col, "t", "row_effective_tstamp"))

    def _with_pivot_eavt(self, df):
        return df.pivot(index=['e', 't'], columns='a', values='v')

    def _with_stack_reset_index(self, df):
        return df.stack().reset_index()

    def _with_ffil(self, df):
        cols = list(df)
        for c in cols:
            df[c] = df.groupby(['e'])[c].ffill()
        return df

    def _with_row_expiration_tstamp(self, df):
        df['row_expiration_tstamp'] = df.sort_values(by=['t'], ascending=False)\
                                        .groupby(['e'])['t'].shift(1)
        return df

    def _with_current_row_indicator(self, df):
        df['row_version'] = (df.sort_values(['t']).groupby(['e']).cumcount() + 1)
        df['current_row_indicator'] = (df.sort_values(['t'], ascending=False)\
                                         .groupby(['e']).cumcount() + 1) == 1
        return df

    def _with_reset_index(self, df):
        return df.reset_index()

    def _with_rename_col(self, df, col_from, col_to):
        return df.rename(columns={col_from: col_to})
