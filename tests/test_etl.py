"""
Tests for the ETL module.
"""
import os
import tempfile
import pandas as pd
import pytest

from movie_graph.etl.process import (
    ensure_dir,
    parse_json_fields,
    extract_data,
    transform_data,
    load_data
)


def test_ensure_dir():
    """Test that ensure_dir creates directories correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, 'test_dir')
        
        # Directory shouldn't exist yet
        assert not os.path.exists(test_dir)
        
        # Create directory
        ensure_dir(test_dir)
        
        # Directory should exist now
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)


def test_parse_json_fields():
    """Test that parse_json_fields correctly parses JSON strings."""
    # Create test dataframe
    df = pd.DataFrame({
        'id': [1, 2],
        'json_field': ['[{"id": 1, "name": "test1"}]', '[{"id": 2, "name": "test2"}]']
    })
    
    # Parse JSON fields
    result_df = parse_json_fields(df, ['json_field'])
    
    # Check results
    assert isinstance(result_df['json_field'][0], list)
    assert result_df['json_field'][0][0]['id'] == 1
    assert result_df['json_field'][0][0]['name'] == 'test1'
    assert result_df['json_field'][1][0]['id'] == 2
    assert result_df['json_field'][1][0]['name'] == 'test2'


@pytest.mark.skip(reason="Requires actual data files")
def test_extract_data():
    """Test that extract_data correctly reads and merges data."""
    # This would require actual data files
    pass


def test_transform_data():
    """Test that transform_data correctly transforms the data."""
    # Create a minimal test dataframe
    df = pd.DataFrame({
        'id': [1],
        'title': ['Test Movie'],
        'release_date': ['2023-01-01'],
        'budget': [1000000],
        'revenue': [2000000],
        'popularity': [7.5],
        'vote_average': [8.0],
        'vote_count': [100],
        'overview': ['Test overview'],
        'genres': [[{'id': 1, 'name': 'Action'}]],
        'keywords': [[{'id': 1, 'name': 'hero'}]],
        'production_companies': [[{'id': 1, 'name': 'Test Studio', 'origin_country': 'US'}]],
        'cast': [[{'id': 1, 'name': 'Test Actor', 'gender': 1, 'character': 'Main Character'}]],
        'crew': [[{'id': 2, 'name': 'Test Director', 'gender': 2, 'job': 'Director', 'department': 'Directing'}]]
    })
    
    # Transform data
    result = transform_data(df)
    
    # Check structure
    assert 'nodes' in result
    assert 'relationships' in result
    
    # Check nodes
    assert 'movies' in result['nodes']
    assert 'persons' in result['nodes']
    assert 'genres' in result['nodes']
    assert 'keywords' in result['nodes']
    assert 'companies' in result['nodes']
    
    # Check relationships
    assert 'acted_in' in result['relationships']
    assert 'directed' in result['relationships']
    assert 'produced' in result['relationships']
    assert 'categorized_as' in result['relationships']
    assert 'tagged_with' in result['relationships']
    
    # Check content
    assert len(result['nodes']['movies']) == 1
    assert result['nodes']['movies'][0]['title'] == 'Test Movie'
    
    assert len(result['nodes']['persons']) == 2
    assert result['nodes']['persons'][0]['name'] in ['Test Actor', 'Test Director']
    assert result['nodes']['persons'][1]['name'] in ['Test Actor', 'Test Director']
    
    assert len(result['nodes']['genres']) == 1
    assert result['nodes']['genres'][0]['name'] == 'Action'
    
    assert len(result['relationships']['acted_in']) == 1
    assert len(result['relationships']['directed']) == 1


@pytest.mark.skip(reason="Creates output files")
def test_load_data():
    """Test that load_data correctly saves the data."""
    # This would create output files, so we'll skip it for now
    pass 