#!/usr/bin/env python3
"""
Debugging script to understand column access issues in the ETL process.
"""
import os
import sys
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movie_graph.etl.process import parse_json_fields

def debug_extract():
    """Debug the extraction process."""
    input_dir = "data/raw"
    movies_file = "tmdb_5000_movies.csv"
    credits_file = "tmdb_5000_credits.csv"
    
    print("Reading movies data...")
    movies_path = os.path.join(input_dir, movies_file)
    movies_df = pd.read_csv(movies_path)
    print(f"Movies data shape: {movies_df.shape}")
    print(f"Movies columns: {movies_df.columns.tolist()}")
    
    # Print first 5 movie titles
    print("\nSample movie titles from movies_df:")
    if 'title' in movies_df.columns:
        print(movies_df['title'].head(5).tolist())
    else:
        print("'title' column not found in movies_df!")
    
    print("\nReading credits data...")
    credits_path = os.path.join(input_dir, credits_file)
    credits_df = pd.read_csv(credits_path)
    print(f"Credits data shape: {credits_df.shape}")
    print(f"Credits columns: {credits_df.columns.tolist()}")
    
    # Print first 5 movie titles from credits
    print("\nSample movie titles from credits_df:")
    if 'title' in credits_df.columns:
        print(credits_df['title'].head(5).tolist())
    else:
        print("'title' column not found in credits_df!")
    
    # Rename ID column in credits to match movies
    id_column_in_movies = 'id'
    id_column_in_credits = None
    
    if 'movie_id' in credits_df.columns:
        id_column_in_credits = 'movie_id'
    elif 'id' in credits_df.columns:
        id_column_in_credits = 'id'
    else:
        raise ValueError("Could not find 'id' or 'movie_id' column in credits file")
    
    if id_column_in_credits != id_column_in_movies:
        print(f"\nRenaming column '{id_column_in_credits}' to '{id_column_in_movies}' in credits data")
        credits_df.rename(columns={id_column_in_credits: id_column_in_movies}, inplace=True)
    
    # Merge dataframes
    print(f"\nMerging data on column '{id_column_in_movies}'")
    df = pd.merge(movies_df, credits_df, on=id_column_in_movies)
    print(f"Merged data shape: {df.shape}")
    print(f"Merged data columns: {df.columns.tolist()}")
    
    # Print column names with '_x' or '_y' suffix (indicates duplicates)
    duplicate_cols = [col for col in df.columns if '_x' in col or '_y' in col]
    if duplicate_cols:
        print(f"\nDuplicate columns after merge: {duplicate_cols}")
    
    # Check for title columns with suffix
    if 'title_x' in df.columns and 'title_y' in df.columns:
        print("\nFound title_x and title_y columns after merge. This indicates duplicate 'title' columns.")
        print("Sample values from title_x:")
        print(df['title_x'].head(5).tolist())
        print("Sample values from title_y:")
        print(df['title_y'].head(5).tolist())
    
    # Convert string representations of lists/dicts to actual Python objects
    json_columns = ['genres', 'keywords', 'production_companies', 'cast', 'crew']
    print(f"\nParsing JSON in columns: {json_columns}")
    df = parse_json_fields(df, json_columns)
    
    # Check if 'title' column exists after processing
    if 'title' in df.columns:
        print("\nTitle column exists after parsing JSON")
        print("Sample movie titles from merged df:")
        print(df['title'].head(5).tolist())
    else:
        print("\n'title' column NOT FOUND after parsing JSON!")
        # Try to find title with suffix
        if 'title_x' in df.columns:
            print("Found 'title_x' column instead:")
            print(df['title_x'].head(5).tolist())
        if 'title_y' in df.columns:
            print("Found 'title_y' column instead:")
            print(df['title_y'].head(5).tolist())
    
    return df

if __name__ == "__main__":
    df = debug_extract()
    
    # Save a small sample to CSV for inspection
    sample_df = df.head(10)
    sample_df.to_csv("data/sample_merged.csv", index=False)
    print("\nSaved 10 rows sample to data/sample_merged.csv for inspection") 