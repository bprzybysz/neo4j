# ETL Process for Neo4j Movie Analysis

This module handles the Extract, Transform, Load (ETL) process for preparing TMDB movie data for import into Neo4j.

## Overview

The ETL process consists of three main steps:

1. **Extract**: Reading raw data from CSV files
2. **Transform**: Converting the data into a Neo4j-friendly format
3. **Load**: Saving the transformed data as CSV files for Neo4j import

## Data Requirements

The process requires two primary data files:

- `tmdb_5000_movies.csv`: Contains movie details including title, budget, revenue, etc.
- `tmdb_5000_credits.csv`: Contains cast and crew information for each movie

These files should be placed in the `data/raw` directory before running the process.

## Running the ETL Process

To run the ETL process:

```bash
python scripts/etl_process.py --input data/raw --output data/processed
```

## Obtaining the Data

You can download the required dataset using the provided script:

```bash
python scripts/download_data.py
```

This script will automatically:
1. Create necessary directories if they don't exist
2. Download the dataset files from primary sources
3. Fall back to backup sources if primary downloads fail
4. As a last resort, create minimal test files with sample data if all downloads fail
5. Place the files in the `data/raw` directory

## Improvements and Fixes

### JSON Parsing

The ETL process includes robust JSON parsing that handles common issues:

- Single vs. double quotes in JSON strings
- Trailing commas in JSON arrays/objects
- Malformed JSON structures
- Empty/null values

The `parse_json_fields` function uses a multi-stage approach to process JSON data:
1. Standard JSON parsing
2. Common error fixes (like replacing single quotes)
3. Using `ast.literal_eval` for Python literal structures
4. Handling specific patterns like trailing commas

### Column Handling

When merging dataframes with duplicate column names (e.g., 'title' appears in both movies and credits files), the process:

1. Identifies columns that might get suffixes during merge
2. After merge, creates a new column with the desired name (e.g., new 'title' from 'title_x')
3. Drops the suffixed columns to clean up the resulting DataFrame

### Missing Column Handling

The process checks for required columns and provides default values when needed:

- For 'title': "Unknown Title"
- For text fields like 'release_date' and 'overview': Empty string
- For numeric fields: 0
- For other fields: None

### ID Column Flexibility

The ETL process now handles different ID column naming conventions:
- Automatically detects if credits file uses 'movie_id' or 'id'
- Renames the column to match the movies file for proper merging
- Reports detailed information on column matching and merging

## Debugging Tools

For troubleshooting complex ETL issues, a dedicated debugging script is available:

```bash
python scripts/debug_extract.py
```

This script provides detailed analysis of:
- File structure and content
- JSON parsing issues
- Column conflicts and naming
- Data type problems
- Missing or malformed values

## Output Files

The process creates the following output files in the specified output directory:

### Node Files
- `movies.csv`: Movie nodes with details
- `persons.csv`: Person nodes (actors, directors)
- `genres.csv`: Genre nodes
- `keywords.csv`: Keyword nodes
- `companies.csv`: Production company nodes

### Relationship Files
- `acted_in.csv`: Relationships between persons and movies (acting)
- `directed.csv`: Relationships between persons and movies (directing)
- `produced.csv`: Relationships between companies and movies
- `categorized_as.csv`: Relationships between movies and genres
- `tagged_with.csv`: Relationships between movies and keywords

## Troubleshooting

If you encounter issues with the ETL process:

1. **Data Files Missing**: Ensure the required CSV files are in the `data/raw` directory
2. **JSON Parsing Errors**: Check if your data has non-standard JSON that might need additional parsing rules
3. **Missing Columns**: Verify that your data contains all the expected columns
4. **Duplicate Columns**: The process handles duplicate column names, but you may need to adjust if your data has different naming patterns

For detailed debugging, you can use the `scripts/debug_extract.py` script to analyze your data structure. 