import pandas as pd


def read_dataframe_from_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def write_dataframe_to_csv(df: pd.DataFrame, path: str) -> None:
    df.to_csv(path, index=False)
