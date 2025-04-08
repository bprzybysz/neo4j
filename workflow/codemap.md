# Neo4j Movie Analysis Codemap

## Core Components

### 1. ETL Process
- **Entry Point**: `scripts/etl_process.py`
- **Functions**:
  - `extract_data()`: Reads data from CSV files
  - `transform_data()`: Transforms movie data into Neo4j format
  - `load_data()`: Saves processed data as CSV files for Neo4j import
  - `main()`: Orchestrates the ETL flow

### 2. Database Connection
- **Class**: `Neo4jConnection` (from notebooks/movie_analysis.ipynb)
- **Methods**:
  - `__init__(uri, auth)`: Initializes connection
  - `close()`: Closes connection
  - `query(query, parameters)`: Executes Cypher query

### 3. Notebook Conversion
- **Script**: `convert_notebook.py`
- **Purpose**: Converts text file to Jupyter notebook format

## Data Flow

```
Raw CSV Files ──> ETL Process ──> Processed CSV Files ──> Neo4j Import
                     │
                     v
                  Analysis Notebooks ──> Visualizations/Reports
```

## Dependencies

- **neo4j**: Neo4j database driver
- **pandas**: Data processing and manipulation
- **matplotlib/seaborn**: Visualization
- **jupyter**: Notebook environment

## Key Files

1. **ETL Script** (`scripts/etl_process.py`):
   - Contains the complete ETL pipeline for processing movie data
   - Functions: extract_data, transform_data, load_data

2. **Movie Analysis Notebook** (`notebooks/movie_analysis.ipynb`):
   - Performs analysis on the Neo4j database
   - Contains Neo4jConnection class
   - Visualizes movie data relationships

3. **Notebook Converter** (`convert_notebook.py`):
   - Utility to convert text files to Jupyter notebooks
   - Used for creating analysis notebooks from templates

## Code Flow

1. **Data Ingestion**:
   - Raw CSV files are read from `data/raw`
   - `extract_data()` reads and merges movies and credits data

2. **Data Transformation**:
   - `transform_data()` converts to node/relationship structure
   - Entities: movies, persons, genres, keywords, companies
   - Relationships: acted_in, directed, produced, categorized_as, tagged_with

3. **Data Loading**:
   - Processed data saved to `data/processed`
   - Individual CSV files for each node/relationship type

4. **Data Analysis**:
   - Connect to Neo4j using `Neo4jConnection`
   - Execute Cypher queries to analyze the graph
   - Create visualizations of relationships and patterns

## Future Development

1. **Package Structure**:
   - Move ETL code to dedicated module
   - Create reusable Neo4j connection class
   - Add utility functions for common operations

2. **Testing**:
   - Add unit tests for ETL functions
   - Add integration tests for Neo4j connectivity

3. **Documentation**:
   - Create comprehensive API documentation
   - Add usage examples for common workflows 