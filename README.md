# Neo4j Movie Analysis

A Python project for analyzing movie datasets using the Neo4j graph database. This project includes ETL processing, data visualization, and graph analysis using Jupyter notebooks.

## Project Overview

This project demonstrates how to:

1. Transform movie datasets into Neo4j graph structure
2. Import data into Neo4j database
3. Query and analyze the graph using Cypher
4. Visualize relationships between movies, actors, directors, and genres

## Setup Instructions

### Prerequisites

- Python 3.11+
- Neo4j Database (local or cloud)
- Movie dataset (compatible with TMDB format)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd neo4j-movie-analysis
   ```

2. Create and activate virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up Neo4j:
   - Install Neo4j or use Neo4j Aura (cloud)
   - Create a new database
   - Note your connection URL and credentials

### Data Preparation

1. Place your raw movie data in the `data/raw/` directory:
   - `tmdb_5000_movies.csv` - Movie information
   - `tmdb_5000_credits.csv` - Movie credits data

2. Run the ETL process:
   ```
   python scripts/etl_process.py
   ```

3. The processed data will be saved to `data/processed/` ready for Neo4j import

## Project Structure

```
neo4j-movie-analysis/
├── data/                   # Data directory
│   ├── raw/                # Raw data files
│   └── processed/          # Processed data for Neo4j import
├── notebooks/              # Jupyter notebooks
│   ├── movie_analysis.ipynb    # Main analysis notebook
│   └── cypher/             # Cypher query examples
├── movie_graph/            # Main package
│   ├── etl/                # ETL code
│   ├── db/                 # Database connectivity
│   └── utils/              # Utility functions
├── scripts/                # Utility scripts
├── tests/                  # Test suite
├── .venv/                  # Virtual environment
└── requirements.txt        # Dependencies
```

## Using the Analysis Notebooks

1. Start Jupyter Notebook:
   ```
   jupyter notebook
   ```

2. Open the `notebooks/movie_analysis.ipynb` notebook

3. Update the Neo4j connection details:
   ```python
   URI = "bolt://localhost:7687"  # Update with your Neo4j URI
   AUTH = ("neo4j", "password")   # Update with your credentials
   ```

4. Run the notebook cells to connect to Neo4j and analyze the movie graph

## Data Model

The graph model consists of the following node types:
- Movie
- Person (actors, directors)
- Genre
- Keyword
- Company

And these relationship types:
- ACTED_IN (Person → Movie)
- DIRECTED (Person → Movie)
- PRODUCED (Company → Movie)
- CATEGORIZED_AS (Movie → Genre)
- TAGGED_WITH (Movie → Keyword)

For more details, see [data_model.md](data_model.md).

## Example Queries

### Find all movies by a director
```cypher
MATCH (p:Person {name: 'Christopher Nolan'})-[:DIRECTED]->(m:Movie)
RETURN m.title, m.release_date, m.vote_average
ORDER BY m.release_date DESC
```

### Find actors who worked together the most
```cypher
MATCH (a1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(a2:Person)
WHERE a1.id < a2.id
RETURN a1.name, a2.name, COUNT(m) AS movies
ORDER BY movies DESC
LIMIT 10
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 