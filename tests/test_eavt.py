"""Tests for the EAVT class."""
import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch
from eavt_helper.classes.eavt import EAVT


class TestEAVT:
    """Test cases for EAVT class."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_eavt_data = pd.DataFrame({
            'e': [1, 1, 2, 2, 3],
            'a': ['name', 'age', 'name', 'city', 'age'],
            'v': ['John', 26, 'Jane', 'SF', 40],
            't': ['2023-01-02', '2023-01-02', '2023-01-02', '2023-01-02', '2023-01-01']
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_eavt_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
        
    def teardown_method(self):
        """Clean up test files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_eavt_initialization_success(self):
        """Test successful EAVT initialization."""
        with patch('click.echo'):
            eavt = EAVT(self.temp_file.name)
            
        assert len(eavt.df) == 5
        assert list(eavt.df.columns) == ['e', 'a', 'v', 't']
        assert pd.api.types.is_datetime64_any_dtype(eavt.df['t'])
    
    def test_eavt_file_not_found(self):
        """Test error when EAVT file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="EAVT file not found"):
            EAVT('nonexistent.csv')
    
    def test_eavt_missing_required_columns(self):
        """Test error when required EAVT columns are missing."""
        # Create data missing required columns
        incomplete_data = pd.DataFrame({
            'e': [1, 2],
            'a': ['name', 'age'],
            'v': ['John', 25]
            # Missing 't' column
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        incomplete_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with pytest.raises(ValueError, match="EAVT file missing required columns"):
                EAVT(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_eavt_invalid_timestamp(self):
        """Test error when timestamp column can't be converted."""
        # Create data with invalid timestamps
        invalid_data = self.test_eavt_data.copy()
        invalid_data['t'] = ['invalid', 'dates', 'here', 'always', 'bad']
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        invalid_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with pytest.raises(ValueError, match="Cannot convert time column 't' to datetime"):
                EAVT(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_eavt_null_values(self):
        """Test error when required columns have null values."""
        # Create data with null values
        null_data = self.test_eavt_data.copy()
        null_data.loc[0, 'e'] = None
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        null_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with pytest.raises(ValueError, match="EAVT column 'e' contains null values"):
                EAVT(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_transform_to_scd2_basic(self):
        """Test basic SCD2 transformation."""
        with patch('click.echo'):
            eavt = EAVT(self.temp_file.name)
            result = eavt.transform_to_scd2()
        
        # Check that required SCD2 columns are present
        required_scd2_cols = ['id', 'row_effective_tstamp', 'row_expiration_tstamp', 
                             'row_version', 'current_row_indicator']
        for col in required_scd2_cols:
            assert col in result.columns
        
        # Check that attributes became columns
        assert 'name' in result.columns
        assert 'age' in result.columns
        assert 'city' in result.columns
        
        # Should have records for each entity
        assert len(result) >= 2  # At least one record per entity
    
    def test_transform_to_scd2_chunked(self):
        """Test SCD2 transformation with chunking."""
        with patch('click.echo'), patch('click.progressbar') as mock_progress:
            eavt = EAVT(self.temp_file.name)
            result = eavt.transform_to_scd2(chunk_size=2)
        
        # Should use chunked processing
        mock_progress.assert_called()
        
        # Result structure should be the same as non-chunked
        required_scd2_cols = ['id', 'row_effective_tstamp', 'row_expiration_tstamp', 
                             'row_version', 'current_row_indicator']
        for col in required_scd2_cols:
            assert col in result.columns
    
    def test_pivot_eavt_duplicate_values(self):
        """Test error handling for duplicate e,a,t combinations."""
        # Create data with duplicate combinations
        duplicate_data = pd.DataFrame({
            'e': [1, 1],
            'a': ['name', 'name'],
            'v': ['John', 'Jane'],  # Different values for same e,a,t
            't': ['2023-01-01', '2023-01-01']
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        duplicate_data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            with patch('click.echo'):
                eavt = EAVT(temp_file.name)
                with pytest.raises(ValueError, match="Error pivoting EAVT data"):
                    eavt.transform_to_scd2()
        finally:
            os.unlink(temp_file.name)
    
    def test_current_row_indicator(self):
        """Test that current row indicator is correctly set."""
        with patch('click.echo'):
            eavt = EAVT(self.temp_file.name)
            result = eavt.transform_to_scd2()
        
        # Each entity should have exactly one current row
        for entity_id in result['id'].unique():
            entity_rows = result[result['id'] == entity_id]
            current_rows = entity_rows[entity_rows['current_row_indicator'] == True]
            assert len(current_rows) == 1, f"Entity {entity_id} should have exactly one current row"
    
    def test_row_versioning(self):
        """Test that row versioning is correctly implemented."""
        with patch('click.echo'):
            eavt = EAVT(self.temp_file.name)
            result = eavt.transform_to_scd2()
        
        # Each entity should have row versions starting from 1
        for entity_id in result['id'].unique():
            entity_rows = result[result['id'] == entity_id].sort_values('row_effective_tstamp')
            versions = entity_rows['row_version'].tolist()
            expected_versions = list(range(1, len(versions) + 1))
            assert versions == expected_versions, f"Entity {entity_id} should have sequential row versions" 