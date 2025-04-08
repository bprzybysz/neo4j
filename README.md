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
   ./setup_venv.sh
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies (if not using the setup script):
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
   python scripts/etl_process.py --input data/raw --output data/processed
   ```

3. The processed data will be saved to `data/processed/` ready for Neo4j import

## Project Structure

```
neo4j-movie-analysis/
├── data/                   # Data directory
│   ├── raw/                # Raw data files
│   └── processed/          # Processed data for Neo4j import
├── movie_graph/            # Main package
│   ├── __init__.py         # Package initialization
│   ├── etl/                # ETL code
│   │   ├── __init__.py
│   │   └── process.py      # ETL processing code
│   ├── db/                 # Database connectivity
│   │   ├── __init__.py
│   │   └── connection.py   # Neo4j connection class
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── helpers.py      # Helper functions
├── notebooks/              # Jupyter notebooks
│   ├── movie_analysis.ipynb        # Original notebook
│   ├── movie_analysis_updated.ipynb  # Updated notebook using the package API
│   └── cypher/             # Cypher query examples
├── scripts/                # Utility scripts
├── tests/                  # Test suite
├── workflow/               # Project documentation
├── README.md               # Project documentation
├── requirements.txt        # Dependencies
├── setup_venv.sh           # Environment setup script
└── run_tests.sh            # Test runner script
```

## Using the Analysis Notebooks

1. Start Jupyter Notebook:
   ```
   jupyter notebook
   ```

2. Open the `notebooks/movie_analysis_updated.ipynb` notebook

3. Update the Neo4j connection details:
   ```python
   URI = "bolt://localhost:7687"  # Update with your Neo4j URI
   AUTH = ("neo4j", "password")   # Update with your credentials
   ```

4. Run the notebook cells to connect to Neo4j and analyze the movie graph

## Using the Package API

### Basic Usage

```python
from movie_graph import connect_to_neo4j, run_etl

# Connect to Neo4j
conn = connect_to_neo4j("bolt://localhost:7687", ("neo4j", "password"))

# Query the database
results = conn.query("MATCH (m:Movie) RETURN m.title LIMIT 5")
print(results)

# Don't forget to close the connection
conn.close()
```

### Running ETL Process

```python
from movie_graph import run_etl

# Run the ETL process
run_etl(
    input_dir="data/raw",
    output_dir="data/processed",
    movies_file="tmdb_5000_movies.csv",
    credits_file="tmdb_5000_credits.csv"
)
```

### Context Manager Pattern

```python
from movie_graph import connect_to_neo4j

# Using the connection as a context manager
with connect_to_neo4j("bolt://localhost:7687", ("neo4j", "password")) as conn:
    # Query the database
    results = conn.query("MATCH (m:Movie) RETURN m.title LIMIT 5")
    print(results)
    
# Connection is automatically closed outside the with block
```

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

### Movie recommendations based on shared genres
```cypher
MATCH (m1:Movie {title: 'Inception'})-[:CATEGORIZED_AS]->(g:Genre)<-[:CATEGORIZED_AS]-(m2:Movie)
WHERE m1 <> m2
RETURN m2.title, m2.vote_average, COUNT(g) AS shared_genres
ORDER BY shared_genres DESC, m2.vote_average DESC
LIMIT 10
```

## Running Tests

To run the tests with coverage reporting:

```bash
./run_tests.sh
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 