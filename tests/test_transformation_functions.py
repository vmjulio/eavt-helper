"""Tests for core transformation functions."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from eavt_helper.classes.snapshot import Snapshot
from eavt_helper.classes.eavt import EAVT


class TestSnapshotTransformationFunctions:
    """Test cases for Snapshot transformation helper functions."""
    
    def setup_method(self):
        """Set up test instance."""
        # Create a mock snapshot instance for testing internal methods
        with patch('eavt_helper.classes.snapshot.os.path.exists', return_value=True), \
             patch('eavt_helper.classes.snapshot.pd.read_csv') as mock_read_csv, \
             patch('click.echo'):
            
            mock_df = pd.DataFrame({
                'user_id': [1, 1, 2],
                'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-01']),
                'name': ['John', 'John', 'Jane'],
                'age': [25, 26, 30],
                'row_version': [1, 2, 1],
                'current_row_indicator': [False, True, True]
            })
            mock_read_csv.return_value = mock_df
            
            self.snapshot = Snapshot('dummy.csv', 'user_id', 'timestamp')
    
    def test_with_drop_snapshot_columns(self):
        """Test dropping of snapshot metadata columns."""
        test_df = pd.DataFrame({
            'user_id': [1, 2],
            'name': ['John', 'Jane'],
            'row_version': [1, 1],
            'current_row_indicator': [True, True],
            'row_expiration_tstamp': [None, None],
            'other_column': ['A', 'B']
        })
        
        result = self.snapshot._with_drop_snapshot_columns(test_df)
        
        # Should drop metadata columns but keep others
        assert 'row_version' not in result.columns
        assert 'current_row_indicator' not in result.columns
        assert 'row_expiration_tstamp' not in result.columns
        assert 'user_id' in result.columns
        assert 'name' in result.columns
        assert 'other_column' in result.columns
    
    def test_with_drop_snapshot_columns_missing_columns(self):
        """Test dropping snapshot columns when they don't exist."""
        test_df = pd.DataFrame({
            'user_id': [1, 2],
            'name': ['John', 'Jane']
        })
        
        # Should not raise error when columns don't exist
        result = self.snapshot._with_drop_snapshot_columns(test_df)
        assert len(result.columns) == 2
        assert list(result.columns) == ['user_id', 'name']
    
    def test_with_v_lag(self):
        """Test creation of lagged values for change detection."""
        test_df = pd.DataFrame({
            'e': [1, 1, 1, 2, 2],
            'a': ['age', 'age', 'age', 'age', 'age'],
            'v': [25, 25, 26, 30, 31],
            't': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-01', '2023-01-02'])
        })
        
        result = self.snapshot._with_v_lag(test_df)
        
        # Should have v_lag column
        assert 'v_lag' in result.columns
        
        # First value for each entity should be NaN
        entity_1_rows = result[result['e'] == 1].sort_values('t')
        assert pd.isna(entity_1_rows.iloc[0]['v_lag'])
        
        # Second value should be previous value
        assert entity_1_rows.iloc[1]['v_lag'] == 25
        assert entity_1_rows.iloc[2]['v_lag'] == 25
    
    def test_with_different_v_lag(self):
        """Test filtering for only changed values."""
        test_df = pd.DataFrame({
            'e': [1, 1, 1, 2, 2],
            'a': ['age', 'age', 'age', 'age', 'age'],
            'v': [25, 25, 26, 30, 31],
            't': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-01', '2023-01-02']),
            'v_lag': [np.nan, 25, 25, np.nan, 30]
        })
        
        result = self.snapshot._with_different_v_lag(test_df)
        
        # Should only keep rows where v != v_lag (including first occurrences with NaN)
        assert len(result) == 4  # First occurrence for each entity + one change each

        # Should include first occurrence and changes
        changes = result[result['e'] == 1]
        assert len(changes) == 2  # First occurrence + change from 25 to 26
        
    def test_with_stack_reset_index(self):
        """Test stacking of dataframe columns into EAVT format."""
        test_df = pd.DataFrame({
            'name': ['John', 'Jane'],
            'age': [25, 30]
        }, index=pd.MultiIndex.from_tuples([(1, '2023-01-01'), (2, '2023-01-01')], names=['user_id', 'timestamp']))
        
        result = self.snapshot._with_stack_reset_index(test_df)
        
        # Should have 2 entities × 2 attributes = 4 rows
        assert len(result) == 4
        assert len(result.columns) == 4  # user_id, timestamp, level_2, 0
        
        # Should have attributes as values in level_2
        assert 'name' in result['level_2'].values
        assert 'age' in result['level_2'].values


class TestEAVTTransformationFunctions:
    """Test cases for EAVT transformation helper functions."""
    
    def setup_method(self):
        """Set up test instance."""
        # Create a mock EAVT instance for testing internal methods
        with patch('eavt_helper.classes.eavt.os.path.exists', return_value=True), \
             patch('eavt_helper.classes.eavt.pd.read_csv') as mock_read_csv, \
             patch('click.echo'):
            
            mock_df = pd.DataFrame({
                'e': [1, 1, 2, 2],
                'a': ['name', 'age', 'name', 'age'],
                'v': ['John', 26, 'Jane', 30],
                't': pd.to_datetime(['2023-01-02', '2023-01-02', '2023-01-01', '2023-01-01'])
            })
            mock_read_csv.return_value = mock_df
            
            self.eavt = EAVT('dummy.csv')
    
    def test_with_pivot_eavt(self):
        """Test pivoting EAVT format to wide format."""
        test_df = pd.DataFrame({
            'e': [1, 1, 2, 2],
            'a': ['name', 'age', 'name', 'age'],
            'v': ['John', 26, 'Jane', 30],
            't': pd.to_datetime(['2023-01-02', '2023-01-02', '2023-01-01', '2023-01-01'])
        })
        
        result = self.eavt._with_pivot_eavt(test_df)
        
        # Should have attributes as columns
        assert 'name' in result.columns
        assert 'age' in result.columns
        
        # Should have entity-time as index
        assert result.index.names == ['e', 't']
        
        # Should have correct values
        assert result.loc[(1, pd.Timestamp('2023-01-02')), 'name'] == 'John'
        assert result.loc[(1, pd.Timestamp('2023-01-02')), 'age'] == 26
    
    def test_with_pivot_eavt_duplicate_error(self):
        """Test error handling for duplicate e,a,t combinations."""
        test_df = pd.DataFrame({
            'e': [1, 1],
            'a': ['name', 'name'],
            'v': ['John', 'Jane'],  # Different values for same e,a,t
            't': pd.to_datetime(['2023-01-01', '2023-01-01'])
        })
        
        with pytest.raises(ValueError, match="Error pivoting EAVT data"):
            self.eavt._with_pivot_eavt(test_df)
    
    def test_with_ffil(self):
        """Test forward filling of values within entity groups."""
        test_df = pd.DataFrame({
            'e': [1, 1, 2, 2],
            't': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02']),
            'name': ['John', None, 'Jane', None],
            'age': [25, 26, None, 30]
        }).set_index(['e', 't'])
        
        result = self.eavt._with_ffil(test_df)
        
        # Should forward fill within each entity
        assert result.loc[(1, pd.Timestamp('2023-01-02')), 'name'] == 'John'  # Forward filled
        assert result.loc[(1, pd.Timestamp('2023-01-02')), 'age'] == 26  # Not filled (has value)
        assert pd.isna(result.loc[(2, pd.Timestamp('2023-01-01')), 'age'])  # First value, no fill
        assert result.loc[(2, pd.Timestamp('2023-01-02')), 'age'] == 30
    
    def test_with_current_row_indicator(self):
        """Test creation of current row indicator and row versions."""
        test_df = pd.DataFrame({
            'e': [1, 1, 1, 2, 2],
            't': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-01', '2023-01-02']),
            'name': ['John', 'John', 'Johnny', 'Jane', 'Jane'],
            'age': [25, 26, 26, 30, 31]
        })
        
        result = self.eavt._with_current_row_indicator(test_df)
        
        # Should have row_version and current_row_indicator columns
        assert 'row_version' in result.columns
        assert 'current_row_indicator' in result.columns
        
        # Each entity should have exactly one current row
        for entity in result['e'].unique():
            entity_rows = result[result['e'] == entity]
            current_rows = entity_rows[entity_rows['current_row_indicator'] == True]
            assert len(current_rows) == 1, f"Entity {entity} should have exactly one current row"
            
            # Current row should be the latest one
            latest_time = entity_rows['t'].max()
            current_row = current_rows.iloc[0]
            assert current_row['t'] == latest_time
        
        # Row versions should be sequential starting from 1
        for entity in result['e'].unique():
            entity_rows = result[result['e'] == entity].sort_values('t')
            versions = entity_rows['row_version'].tolist()
            expected_versions = list(range(1, len(versions) + 1))
            assert versions == expected_versions
    
    def test_with_row_expiration_tstamp(self):
        """Test creation of row expiration timestamps."""
        test_df = pd.DataFrame({
            'e': [1, 1, 1, 2, 2],
            't': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-01', '2023-01-02']),
            'name': ['John', 'John', 'Johnny', 'Jane', 'Jane']
        })
        
        result = self.eavt._with_row_expiration_tstamp(test_df)
        
        # Should have row_expiration_tstamp column
        assert 'row_expiration_tstamp' in result.columns
        
        # For entity 1, first two rows should have expiration timestamps
        entity_1_rows = result[result['e'] == 1].sort_values('t')
        
        # First row expires when second row becomes effective
        assert entity_1_rows.iloc[0]['row_expiration_tstamp'] == pd.Timestamp('2023-01-02')
        # Second row expires when third row becomes effective  
        assert entity_1_rows.iloc[1]['row_expiration_tstamp'] == pd.Timestamp('2023-01-03')
        # Last row should have no expiration
        assert pd.isna(entity_1_rows.iloc[2]['row_expiration_tstamp'])


class TestDataValidationFunctions:
    """Test cases for data validation and edge cases."""
    
    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframes."""
        with patch('eavt_helper.classes.snapshot.os.path.exists', return_value=True), \
             patch('eavt_helper.classes.snapshot.pd.read_csv') as mock_read_csv, \
             patch('click.echo'):
            
            # Empty dataframe
            mock_df = pd.DataFrame(columns=['user_id', 'timestamp', 'name'])
            mock_df['timestamp'] = pd.to_datetime(mock_df['timestamp'])
            mock_read_csv.return_value = mock_df
            
            snapshot = Snapshot('dummy.csv', 'user_id', 'timestamp')
            result = snapshot.transform_to_eavt()
            
            # Should return empty EAVT dataframe with correct structure
            assert len(result) == 0
            assert list(result.columns) == ['e', 'a', 'v', 't']
    
    def test_single_row_handling(self):
        """Test handling of single row dataframes."""
        with patch('eavt_helper.classes.snapshot.os.path.exists', return_value=True), \
             patch('eavt_helper.classes.snapshot.pd.read_csv') as mock_read_csv, \
             patch('click.echo'):
            
            # Single row dataframe
            mock_df = pd.DataFrame({
                'user_id': [1],
                'timestamp': pd.to_datetime(['2023-01-01']),
                'name': ['John'],
                'age': [25]
            })
            mock_read_csv.return_value = mock_df
            
            snapshot = Snapshot('dummy.csv', 'user_id', 'timestamp')
            result = snapshot.transform_to_eavt()
            
            # Should return 2 EAVT records (name and age attributes)
            assert len(result) == 2
            assert set(result['a'].values) == {'name', 'age'}
            assert all(result['e'] == 1)
    
    def test_mixed_data_types_handling(self):
        """Test handling of mixed data types in values."""
        test_df = pd.DataFrame({
            'e': [1, 1, 1, 1],
            'a': ['name', 'age', 'active', 'score'],
            'v': ['John', 25, True, 95.5],  # Mixed types: string, int, bool, float
            't': pd.to_datetime(['2023-01-01'] * 4)
        })
        
        with patch('eavt_helper.classes.eavt.os.path.exists', return_value=True), \
             patch('eavt_helper.classes.eavt.pd.read_csv', return_value=test_df), \
             patch('click.echo'):
            
            eavt = EAVT('dummy.csv')
            result = eavt.transform_to_scd2()
            
            # Should handle mixed data types correctly
            assert 'name' in result.columns
            assert 'age' in result.columns
            assert 'active' in result.columns
            assert 'score' in result.columns
            
            # Values should be preserved with correct types
            row = result.iloc[0]
            assert row['name'] == 'John'
            assert row['age'] == 25
            assert row['active'] == True
            assert row['score'] == 95.5 