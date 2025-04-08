"""
Tests for the database connection module.
"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from movie_graph.db.connection import Neo4jConnection, get_connection


class TestNeo4jConnection:
    """Tests for the Neo4jConnection class."""
    
    @patch('movie_graph.db.connection.GraphDatabase')
    def test_init(self, mock_graph_db):
        """Test initialization of Neo4jConnection."""
        # Arrange
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Act
        conn = Neo4jConnection("bolt://localhost:7687", ("neo4j", "password"))
        
        # Assert
        mock_graph_db.driver.assert_called_once_with("bolt://localhost:7687", auth=("neo4j", "password"))
        assert conn.driver == mock_driver
        assert conn.database is None
    
    @patch('movie_graph.db.connection.GraphDatabase')
    def test_init_with_database(self, mock_graph_db):
        """Test initialization of Neo4jConnection with database."""
        # Arrange
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Act
        conn = Neo4jConnection("bolt://localhost:7687", ("neo4j", "password"), "movies")
        
        # Assert
        mock_graph_db.driver.assert_called_once_with("bolt://localhost:7687", auth=("neo4j", "password"))
        assert conn.driver == mock_driver
        assert conn.database == "movies"
    
    @patch('movie_graph.db.connection.GraphDatabase')
    def test_close(self, mock_graph_db):
        """Test close method."""
        # Arrange
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        conn = Neo4jConnection("bolt://localhost:7687", ("neo4j", "password"))
        
        # Act
        conn.close()
        
        # Assert
        mock_driver.close.assert_called_once()
    
    @patch('movie_graph.db.connection.GraphDatabase')
    def test_query(self, mock_graph_db):
        """Test query method."""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        
        mock_result.keys.return_value = ["name", "count"]
        mock_result.__iter__.return_value = [
            MagicMock(values=lambda: ["John", 10]),
            MagicMock(values=lambda: ["Jane", 20])
        ]
        
        mock_session.run.return_value = mock_result
        mock_session.__enter__.return_value = mock_session
        mock_driver.session.return_value = mock_session
        
        mock_graph_db.driver.return_value = mock_driver
        
        conn = Neo4jConnection("bolt://localhost:7687", ("neo4j", "password"))
        
        # Act
        df = conn.query("MATCH (n) RETURN n.name as name, count(*) as count")
        
        # Assert
        mock_session.run.assert_called_once_with("MATCH (n) RETURN n.name as name, count(*) as count", {})
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name", "count"]
        assert df.shape == (2, 2)
        assert df.iloc[0, 0] == "John"
        assert df.iloc[0, 1] == 10
        assert df.iloc[1, 0] == "Jane"
        assert df.iloc[1, 1] == 20
    
    @patch('movie_graph.db.connection.GraphDatabase')
    def test_query_with_parameters(self, mock_graph_db):
        """Test query method with parameters."""
        # Arrange
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        
        mock_result.keys.return_value = ["name"]
        mock_result.__iter__.return_value = [
            MagicMock(values=lambda: ["John"])
        ]
        
        mock_session.run.return_value = mock_result
        mock_session.__enter__.return_value = mock_session
        mock_driver.session.return_value = mock_session
        
        mock_graph_db.driver.return_value = mock_driver
        
        conn = Neo4jConnection("bolt://localhost:7687", ("neo4j", "password"))
        
        # Act
        df = conn.query("MATCH (n) WHERE n.name = $name RETURN n.name as name", {"name": "John"})
        
        # Assert
        mock_session.run.assert_called_once_with(
            "MATCH (n) WHERE n.name = $name RETURN n.name as name", 
            {"name": "John"}
        )
        
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name"]
        assert df.shape == (1, 1)
        assert df.iloc[0, 0] == "John"
    
    @patch('movie_graph.db.connection.GraphDatabase')
    def test_context_manager(self, mock_graph_db):
        """Test Neo4jConnection as context manager."""
        # Arrange
        mock_driver = MagicMock()
        mock_graph_db.driver.return_value = mock_driver
        
        # Act
        with Neo4jConnection("bolt://localhost:7687", ("neo4j", "password")) as conn:
            pass
        
        # Assert
        mock_driver.close.assert_called_once()
    
    @patch('movie_graph.db.connection.Neo4jConnection')
    def test_get_connection(self, mock_connection_class):
        """Test get_connection function."""
        # Arrange
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection
        
        # Act
        conn = get_connection("bolt://localhost:7687", ("neo4j", "password"))
        
        # Assert
        mock_connection_class.assert_called_once_with("bolt://localhost:7687", ("neo4j", "password"), None)
        assert conn == mock_connection 