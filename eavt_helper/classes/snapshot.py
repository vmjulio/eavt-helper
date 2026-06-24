import pandas as pd
import os
import click
from typing import Optional


class Snapshot:
    def __init__(self, snapshot_path: str, id_col: str, tstamp_col: str):
        """
        Initialize Snapshot with validation and error handling.
        
        Args:
            snapshot_path: Path to the snapshot CSV file
            id_col: Column name containing unique entity IDs
            tstamp_col: Column name containing timestamps
        """
        try:
            # Validate file exists
            if not os.path.exists(snapshot_path):
                raise FileNotFoundError(f"Snapshot file not found: {snapshot_path}")
            
            # Load data
            self.df = pd.read_csv(snapshot_path)
            
            # Validate required columns exist
            if id_col not in self.df.columns:
                raise ValueError(f"ID column '{id_col}' not found in snapshot. Available columns: {list(self.df.columns)}")
            if tstamp_col not in self.df.columns:
                raise ValueError(f"Timestamp column '{tstamp_col}' not found in snapshot. Available columns: {list(self.df.columns)}")
            
            # Validate data types and convert timestamp
            try:
                self.df[tstamp_col] = pd.to_datetime(self.df[tstamp_col])
            except Exception as e:
                raise ValueError(f"Cannot convert timestamp column '{tstamp_col}' to datetime: {str(e)}")
            
            # Check for null values in key columns
            if self.df[id_col].isnull().any():
                raise ValueError(f"ID column '{id_col}' contains null values")
            if self.df[tstamp_col].isnull().any():
                raise ValueError(f"Timestamp column '{tstamp_col}' contains null values")
            
            self.id_col = id_col
            self.tstamp_col = tstamp_col
            
            click.echo(f"✓ Loaded snapshot with {len(self.df)} rows and {len(self.df.columns)} columns")
            
        except Exception as e:
            click.echo(f"Error loading snapshot: {str(e)}", err=True)
            raise
    
    def transform_to_eavt(self, chunk_size: Optional[int] = None) -> pd.DataFrame:
        """
        Transform snapshot to EAVT format with optional chunked processing.
        
        Args:
            chunk_size: Size of chunks for processing large datasets. If None, processes entire dataset.
            
        Returns:
            DataFrame in EAVT format (Entity, Attribute, Value, Time)
        """
        try:
            if chunk_size and len(self.df) > chunk_size:
                click.echo(f"Processing large dataset in chunks of {chunk_size} rows...")
                return self._process_in_chunks(chunk_size)
            else:
                return self._transform_single_chunk(self.df)
        except Exception as e:
            click.echo(f"Error during EAVT transformation: {str(e)}", err=True)
            raise

    def _process_in_chunks(self, chunk_size: int) -> pd.DataFrame:
        """Process large datasets in chunks of entities to manage memory usage.

        Chunking is done by entity ID rather than by row index. This ensures
        an entity's full history is always contained within a single chunk,
        which is required for the lag-based change detection in
        `_with_v_lag` / `_with_different_v_lag` to be correct.
        """
        entities = self.df[self.id_col].unique()
        # Approximate entities-per-chunk from the requested row chunk_size,
        # using the average rows-per-entity. Always at least 1 entity per chunk.
        avg_rows_per_entity = max(1, len(self.df) / max(1, len(entities)))
        entities_per_chunk = max(1, int(chunk_size / avg_rows_per_entity))

        results = []
        total_entity_chunks = (len(entities) + entities_per_chunk - 1) // entities_per_chunk

        with click.progressbar(range(0, len(entities), entities_per_chunk),
                               label='Processing entity chunks',
                               length=total_entity_chunks) as bar:
            for start in bar:
                end = min(start + entities_per_chunk, len(entities))
                chunk_entities = entities[start:end]
                chunk_df = self.df[self.df[self.id_col].isin(chunk_entities)].copy()

                processed_chunk = self._transform_single_chunk(chunk_df)
                results.append(processed_chunk)

        click.echo("✓ Combining processed chunks...")
        return pd.concat(results, ignore_index=True)

    def _transform_single_chunk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform a single chunk or the entire dataset."""
        return (df.pipe(self._with_set_index, [self.id_col, self.tstamp_col])
                  .pipe(self._with_drop_snapshot_columns)
                  .pipe(self._with_stack_reset_index)
                  .pipe(self._with_rename_cols_eavt, self.id_col, self.tstamp_col)
                  .pipe(self._with_order_eavt)
                  .pipe(self._with_v_lag)
                  .pipe(self._with_different_v_lag)
                  .pipe(self._with_drop_v_lag))

    def _with_drop_snapshot_columns(self, df):
        """Drop common snapshot metadata columns."""
        columns_to_drop = ['row_version', 'current_row_indicator', 'row_expiration_tstamp']
        existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        
        if existing_columns_to_drop:
            df = df.drop(columns=existing_columns_to_drop)
            
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
