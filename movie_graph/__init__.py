"""
Neo4j Movie Analysis package.

This package provides tools for analyzing movie data with Neo4j.
"""
from typing import Tuple, Optional

from movie_graph.db.connection import Neo4jConnection, get_connection
from movie_graph.etl.process import run_etl

__version__ = "0.1.0"


def connect_to_neo4j(uri: str, auth: Tuple[str, str], database: Optional[str] = None) -> Neo4jConnection:
    """
    Connect to Neo4j database.
    
    A convenience function to easily connect to Neo4j from anywhere.
    
    Args:
        uri: Neo4j connection URI
        auth: Tuple containing (username, password)
        database: Optional database name
        
    Returns:
        A connected Neo4jConnection instance
    """
    return get_connection(uri, auth, database)
