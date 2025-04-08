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

1. Download the dataset using the provided script:
   ```
   python scripts/download_data.py
   ```
   This script will automatically download the TMDB dataset files to the `data/raw/` directory.

2. Alternatively, place your raw movie data manually in the `data/raw/` directory:
   - `tmdb_5000_movies.csv` - Movie information
   - `tmdb_5000_credits.csv` - Movie credits data

3. Run the ETL process:
   ```
   python scripts/etl_process.py --input data/raw --output data/processed
   ```

4. The processed data will be saved to `data/processed/` ready for Neo4j import

## Environment Checks

This project includes automatic environment checks that run before executing Python scripts. These checks ensure:

1. The SSH key (`~/.ssh/id_ed25519_git_private2`) is properly loaded in the ssh-agent
2. The virtual environment is set up and activated

### Running Scripts with Environment Checks

Use the `run_with_checks.py` wrapper to execute Python scripts:

```bash
python scripts/run_with_checks.py <script_path> [args...]
```

Example:
```bash
python scripts/run_with_checks.py scripts/etl_process.py --input data/raw --output data/processed
```

The wrapper will:
1. Verify the SSH key is loaded
2. Check and activate the virtual environment if needed
3. Execute the specified script with any provided arguments

If any checks fail, the script execution will be blocked until the issues are resolved.

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
│   ├── run_with_checks.py  # Environment check wrapper
│   ├── download_data.py    # Dataset download script
│   ├── debug_extract.py    # Debugging script for ETL issues
│   └── etl_process.py      # ETL processing script
├── tests/                  # Test suite
├── workflow/               # Project documentation
├── README.md               # Project documentation
├── requirements.txt        # Dependencies
├── setup_venv.sh           # Environment setup script
├── check_environment.sh    # Environment check script
└── run_tests.sh            # Test runner script
```