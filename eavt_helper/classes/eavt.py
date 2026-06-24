import os

import click
import pandas as pd


class EAVT:
    def __init__(self, eavt_path: str):
        """
        Initialize EAVT with validation and error handling.

        Args:
            eavt_path: Path to the EAVT CSV file
        """
        try:
            # Validate file exists
            if not os.path.exists(eavt_path):
                raise FileNotFoundError(f"EAVT file not found: {eavt_path}")

            # Load data
            self.df = pd.read_csv(eavt_path)

            # Validate EAVT format (must have e, a, v, t columns)
            required_columns = ["e", "a", "v", "t"]
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            if missing_columns:
                raise ValueError(
                    f"EAVT file missing required columns: {missing_columns}. "
                    f"Available columns: {list(self.df.columns)}"
                )

            # Validate data types
            try:
                self.df["t"] = pd.to_datetime(self.df["t"])
            except Exception as e:
                raise ValueError(f"Cannot convert time column 't' to datetime: {str(e)}") from e

            # Check for null values in required columns
            for col in required_columns:
                if self.df[col].isnull().any():
                    raise ValueError(f"EAVT column '{col}' contains null values")

            click.echo(f"✓ Loaded EAVT log with {len(self.df)} rows")

        except Exception as e:
            click.echo(f"Error loading EAVT file: {str(e)}", err=True)
            raise

    def transform_to_scd2(self, chunk_size: int | None = None) -> pd.DataFrame:
        """
        Transform EAVT to SCD Type 2 format with optional chunked processing.

        Args:
            chunk_size: Size of chunks for processing large datasets. If None, processes entire dataset.

        Returns:
            DataFrame in SCD Type 2 format
        """
        try:
            if chunk_size and len(self.df) > chunk_size:
                click.echo(f"Processing large EAVT dataset in chunks of {chunk_size} rows...")
                return self._process_in_chunks(chunk_size)
            else:
                return self._transform_single_chunk(self.df)
        except Exception as e:
            click.echo(f"Error during SCD2 transformation: {str(e)}", err=True)
            raise

    def _process_in_chunks(self, chunk_size: int) -> pd.DataFrame:
        """Process large datasets in chunks to manage memory usage."""
        # Group by entity to ensure we don't split entity histories across chunks
        entities = self.df["e"].unique()
        results = []

        total_entities = len(entities)
        entities_per_chunk = max(1, chunk_size // 100)  # Rough estimate

        with click.progressbar(
            range(0, total_entities, entities_per_chunk), label="Processing entity chunks"
        ) as bar:
            for i in bar:
                end_idx = min(i + entities_per_chunk, total_entities)
                chunk_entities = entities[i:end_idx]
                chunk_df = self.df[self.df["e"].isin(chunk_entities)].copy()

                processed_chunk = self._transform_single_chunk(chunk_df)
                results.append(processed_chunk)

        click.echo("✓ Combining processed chunks...")
        return pd.concat(results, ignore_index=True)

    def _transform_single_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform a single chunk or the entire dataset."""
        return (
            df.pipe(self._with_pivot_eavt)
            .pipe(self._with_ffil)
            .pipe(self._with_reset_index)
            .pipe(self._with_row_expiration_tstamp)
            .pipe(self._with_current_row_indicator)
            .pipe(self._with_rename_col, "e", "id")
            .pipe(self._with_rename_col, "t", "row_effective_tstamp")
        )

    def _with_pivot_eavt(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pivot EAVT format to wide format."""
        try:
            return df.pivot(index=["e", "t"], columns="a", values="v")
        except Exception as e:
            raise ValueError(
                f"Error pivoting EAVT data: {str(e)}. "
                "This may indicate duplicate e,a,t combinations."
            ) from e

    def _with_stack_reset_index(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.stack().reset_index()

    def _with_ffil(self, df: pd.DataFrame) -> pd.DataFrame:
        """Forward fill values within each entity group."""
        cols = list(df.columns)
        # Skip the index columns 'e' and 't'
        data_cols = [c for c in cols if c not in ["e", "t"]]

        for c in data_cols:
            df[c] = df.groupby(["e"])[c].ffill()
        return df

    def _with_row_expiration_tstamp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add row expiration timestamp (next row's effective timestamp)."""
        df["row_expiration_tstamp"] = (
            df.sort_values(by=["t"], ascending=False).groupby(["e"])["t"].shift(1)
        )
        return df

    def _with_current_row_indicator(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add row version and current row indicator."""
        df["row_version"] = df.sort_values(["t"]).groupby(["e"]).cumcount() + 1
        df["current_row_indicator"] = (
            df.sort_values(["t"], ascending=False).groupby(["e"]).cumcount() + 1
        ) == 1
        return df

    def _with_reset_index(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.reset_index()

    def _with_rename_col(self, df: pd.DataFrame, col_from: str, col_to: str) -> pd.DataFrame:
        return df.rename(columns={col_from: col_to})
