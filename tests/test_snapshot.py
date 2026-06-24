"""Tests for the Snapshot class."""
import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch
from eavt_helper.classes.snapshot import Snapshot


class TestSnapshot:
    """Test cases for Snapshot class."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_data = pd.DataFrame({
            'user_id': [1, 1, 2, 2, 3],
            'timestamp': ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02', '2023-01-01'],
            'name': ['John', 'John', 'Jane', 'Jane', 'Bob'],
            'age': [25, 26, 30, 30, 40],
            'city': ['NYC', 'NYC', 'LA', 'SF', 'Chicago']
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
        
    def teardown_method(self):
        """Clean up test files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_snapshot_initialization_success(self):
        """Test successful snapshot initialization."""
        with patch('click.echo'):
            snapshot = Snapshot(self.temp_file.name, 'user_id', 'timestamp')
            
        assert snapshot.id_col == 'user_id'
        assert snapshot.tstamp_col == 'timestamp'
        assert len(snapshot.df) == 5
        assert pd.api.types.is_datetime64_any_dtype(snapshot.df['timestamp'])
    
    def test_snapshot_file_not_found(self):
        """Test error when snapshot file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Snapshot file not found"):
            Snapshot('nonexistent.csv', 'user_id', 'timestamp')
    
    def test_snapshot_missing_id_column(self):
        """Test error when ID column is missing."""
        with pytest.raises(ValueError, match="ID column 'missing_id' not found"):
            Snapshot(self.temp_file.name, 'missing_id', 'timestamp')
    
    def test_snapshot_missing_timestamp_column(self):
        """Test error when timestamp column is missing."""
        with pytest.raises(ValueError, match="Timestamp column 'missing_ts' not found"):
            Snapshot(self.temp_file.name, 'user_id', 'missing_ts')
    
    def test_snapshot_invalid_timestamp(self):
        """Test error when timestamp column can't be converted."""
        # Create data with invalid timestamps
        invalid_data = self.test_data.copy()
        invalid_data['timestamp'] = ['invalid', 'dates', 'here', 'always', 'bad']
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        invalid_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with pytest.raises(ValueError, match="Cannot convert timestamp column"):
                Snapshot(temp_file.name, 'user_id', 'timestamp')
        finally:
            os.unlink(temp_file.name)
    
    def test_snapshot_null_values(self):
        """Test error when key columns have null values."""
        # Create data with null ID values
        null_data = self.test_data.copy()
        null_data.loc[0, 'user_id'] = None
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        null_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with pytest.raises(ValueError, match="ID column 'user_id' contains null values"):
                Snapshot(temp_file.name, 'user_id', 'timestamp')
        finally:
            os.unlink(temp_file.name)
    
    def test_transform_to_eavt_basic(self):
        """Test basic EAVT transformation."""
        with patch('click.echo'):
            snapshot = Snapshot(self.temp_file.name, 'user_id', 'timestamp')
            result = snapshot.transform_to_eavt()
        
        # Check structure
        assert list(result.columns) == ['e', 'a', 'v', 't']
        
        # Should only contain changed values (age change for user 1)
        assert len(result) == 1
        assert result.iloc[0]['e'] == 1
        assert result.iloc[0]['a'] == 'age'
        assert result.iloc[0]['v'] == 26
    
    def test_transform_to_eavt_chunked(self):
        """Test EAVT transformation with chunking."""
        with patch('click.echo'), patch('click.progressbar') as mock_progress:
            snapshot = Snapshot(self.temp_file.name, 'user_id', 'timestamp')
            result = snapshot.transform_to_eavt(chunk_size=2)
        
        # Should use chunked processing
        mock_progress.assert_called()
        
        # Result should be the same as non-chunked
        assert list(result.columns) == ['e', 'a', 'v', 't']
        assert len(result) == 1
    
    def test_drop_snapshot_columns(self):
        """Test dropping of snapshot metadata columns."""
        # Add metadata columns to test data
        data_with_metadata = self.test_data.copy()
        data_with_metadata['row_version'] = [1, 2, 1, 2, 1]
        data_with_metadata['current_row_indicator'] = [False, True, False, True, True]
        data_with_metadata['row_expiration_tstamp'] = [None, None, None, None, None]
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data_with_metadata.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with patch('click.echo'):
                snapshot = Snapshot(temp_file.name, 'user_id', 'timestamp')
                result = snapshot.transform_to_eavt()
            
            # Metadata columns should not appear in attributes
            attributes = result['a'].unique()
            assert 'row_version' not in attributes
            assert 'current_row_indicator' not in attributes
            assert 'row_expiration_tstamp' not in attributes
            
        finally:
            os.unlink(temp_file.name) 