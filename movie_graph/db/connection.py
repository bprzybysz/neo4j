"""
Neo4j database connection and query utilities.
"""
from typing import Dict, List, Optional, Tuple, Any, Union

import pandas as pd
from neo4j import GraphDatabase


class Neo4jConnection:
    """
    Handles Neo4j database connections and queries.
    
    This class provides a simple interface for connecting to Neo4j,
    executing Cypher queries, and returning results as DataFrames.
    """
    
    def __init__(self, uri: str, auth: Tuple[str, str], database: Optional[str] = None):
        """
        Initialize a new Neo4j connection.
        
        Args:
            uri: The Neo4j connection URI (e.g., "bolt://localhost:7687")
            auth: A tuple containing (username, password)
            database: Optional database name to connect to
        """
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.database = database
        
    def close(self) -> None:
        """
        Close the Neo4j connection.
        """
        self.driver.close()
        
    def query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a Cypher query and return results as a pandas DataFrame.
        
        Args:
            query: The Cypher query string
            parameters: Optional parameters to pass to the query
        
        Returns:
            A pandas DataFrame containing the query results
        """
        if parameters is None:
            parameters = {}
            
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters)
            return pd.DataFrame([r.values() for r in result], columns=result.keys())

    def __enter__(self) -> 'Neo4jConnection':
        """
        Support for using this class as a context manager.
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close connection when exiting context.
        """
        self.close()


def get_connection(uri: str, auth: Tuple[str, str], database: Optional[str] = None) -> Neo4jConnection:
    """
    Create and return a Neo4j connection.
    
    A utility function to simplify creating a connection.
    
    Args:
        uri: The Neo4j connection URI
        auth: A tuple containing (username, password)
        database: Optional database name to connect to
        
    Returns:
        A Neo4jConnection instance
    """
    return Neo4jConnection(uri, auth, database) 