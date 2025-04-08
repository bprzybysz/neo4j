"""
ETL process for transforming TMDB movie dataset into Neo4j importable format.
"""
import os
import json
from typing import Dict, List, Any, Union, Optional

import pandas as pd


def ensure_dir(directory: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Path to directory to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def parse_json_fields(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Parse JSON strings in DataFrame columns.
    
    Args:
        df: DataFrame to process
        columns: List of column names containing JSON strings
        
    Returns:
        DataFrame with parsed JSON columns
    """
    def safe_json_loads(x):
        if pd.isna(x):
            return []
        
        if isinstance(x, list):
            return x  # Already parsed
            
        try:
            # First attempt: standard JSON parsing
            return json.loads(x)
        except json.JSONDecodeError:
            try:
                # Second attempt: try fixing common JSON issues
                # Replace single quotes with double quotes if that's the issue
                fixed_json = x.replace("'", '"')
                return json.loads(fixed_json)
            except json.JSONDecodeError:
                try:
                    # Third attempt: try to use ast.literal_eval for Python literal structures
                    import ast
                    return ast.literal_eval(x)
                except (SyntaxError, ValueError):
                    try:
                        # Fourth attempt: handle potential trailing commas
                        # This is a common error in JSON strings
                        if x.endswith(',]}'):
                            fixed_json = x.replace(',]}', ']}')
                            return json.loads(fixed_json)
                        elif x.endswith(',}'):
                            fixed_json = x.replace(',}', '}')
                            return json.loads(fixed_json)
                        else:
                            # Create more detailed error reporting
                            print(f"Warning: Could not parse JSON: {x[:100]}...")
                            print(f"Using a fallback empty list")
                            return []
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse JSON: {x[:100]}...")
                        print(f"Error: {e}")
                        return []
            
    # Apply the safe parsing to each specified column
    for col in columns:
        # Check if column exists
        if col in df.columns:
            df[col] = df[col].apply(safe_json_loads)
        else:
            print(f"Warning: Column '{col}' not found in DataFrame")
    
    return df


def extract_data(input_dir: str, movies_file: str, credits_file: str) -> pd.DataFrame:
    """
    Extract data from raw CSV files and prepare it for transformation.
    
    This function handles the following tasks:
    1. Reads movie and credits data from CSV files
    2. Resolves column naming conflicts during the merge (e.g., 'title' appearing in both files)
    3. Parses JSON-formatted columns into Python objects
    4. Adds default values for any missing required columns
    
    Implementation details:
    - Both the movies and credits files contain a 'title' column, which causes pandas to append
      '_x' and '_y' suffixes during merging. We handle this by creating a new 'title' column from
      'title_x' and dropping both suffixed columns.
    - JSON parsing is improved to handle various edge cases and problematic JSON formatting.
    - Validation is performed to ensure all required columns are present before transformation.
    
    Args:
        input_dir: Directory containing input files
        movies_file: Filename for movies data
        credits_file: Filename for credits data
        
    Returns:
        DataFrame containing merged movie data ready for transformation
    """
    print("Extracting data...")
    
    # Check if files exist
    movies_path = os.path.join(input_dir, movies_file)
    credits_path = os.path.join(input_dir, credits_file)
    
    if not os.path.exists(movies_path):
        raise FileNotFoundError(f"Movies file not found: {movies_path}")
    if not os.path.exists(credits_path):
        raise FileNotFoundError(f"Credits file not found: {credits_path}")
    
    print(f"Reading movies data from {movies_path}")
    movies_df = pd.read_csv(movies_path)
    print(f"Movies data shape: {movies_df.shape}")
    print(f"Movies columns: {movies_df.columns.tolist()}")
    
    print(f"Reading credits data from {credits_path}")
    credits_df = pd.read_csv(credits_path)
    print(f"Credits data shape: {credits_df.shape}")
    print(f"Credits columns: {credits_df.columns.tolist()}")
    
    # Handle different column naming conventions
    # Some datasets use 'movie_id', some use 'id' in the credits file
    id_column_in_movies = 'id'
    id_column_in_credits = None
    
    # Determine the ID column in credits
    if 'movie_id' in credits_df.columns:
        id_column_in_credits = 'movie_id'
    elif 'id' in credits_df.columns:
        id_column_in_credits = 'id'
    else:
        raise ValueError("Could not find 'id' or 'movie_id' column in credits file")
    
    # Rename ID column in credits to match movies
    if id_column_in_credits != id_column_in_movies:
        print(f"Renaming column '{id_column_in_credits}' to '{id_column_in_movies}' in credits data")
        credits_df.rename(columns={id_column_in_credits: id_column_in_movies}, inplace=True)
    
    # Both dataframes have a 'title' column which will cause duplicates when merging
    # We'll handle this by tracking which columns might get suffixes
    common_columns = set(movies_df.columns) & set(credits_df.columns)
    print(f"Common columns that may get suffixes: {common_columns}")
    
    # Merge dataframes
    print(f"Merging data on column '{id_column_in_movies}'")
    df = pd.merge(movies_df, credits_df, on=id_column_in_movies)
    print(f"Merged data shape: {df.shape}")
    
    # Check and handle duplicate columns with suffixes
    duplicate_cols = [col for col in df.columns if '_x' in col or '_y' in col]
    if duplicate_cols:
        print(f"Found duplicate columns after merge: {duplicate_cols}")
        
        # If title has been split into title_x and title_y, fix it
        if 'title_x' in df.columns and 'title_y' in df.columns:
            print("Fixing title column (using title_x from movies file)")
            # Rename title_x to title (preserve the title from the movies file)
            df['title'] = df['title_x']
            # Drop the duplicate columns
            df = df.drop(columns=['title_x', 'title_y'])
    
    # Identify JSON columns
    json_columns = []
    for col in ['genres', 'keywords', 'production_companies', 'cast', 'crew']:
        if col in df.columns:
            json_columns.append(col)
        else:
            print(f"Warning: Expected column '{col}' not found in merged dataframe")
    
    print(f"Parsing JSON in columns: {json_columns}")
    # Convert string representations of lists/dicts to actual Python objects
    df = parse_json_fields(df, json_columns)
    
    # Verify that required columns are present for transformation
    required_columns = ['id', 'title', 'release_date', 'budget', 'revenue', 
                        'popularity', 'vote_average', 'vote_count', 'overview']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing required columns: {missing_columns}")
        # Add missing columns with default values to prevent KeyError later
        for col in missing_columns:
            print(f"Adding missing column '{col}' with default values")
            if col == 'title':
                df[col] = 'Unknown Title'
            elif col in ['release_date', 'overview']:
                df[col] = ''
            elif col in ['budget', 'revenue', 'popularity', 'vote_average', 'vote_count']:
                df[col] = 0
            else:
                df[col] = None
    
    return df


def transform_data(df: pd.DataFrame) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Transform the data into Neo4j compatible format.
    
    Args:
        df: DataFrame containing movie data
        
    Returns:
        Dictionary containing nodes and relationships data
    """
    print("Transforming data...")
    
    # Extract nodes
    movies = []
    persons = {}  # Using dict to avoid duplicates
    genres = {}   # Using dict to avoid duplicates
    keywords = {}  # Using dict to avoid duplicates
    companies = {}  # Using dict to avoid duplicates
    
    # Extract relationships
    acted_in = []
    directed = []
    produced = []
    categorized_as = []
    tagged_with = []
    
    # Process each movie
    for _, row in df.iterrows():
        movie_id = row['id']
        
        # Movie node
        movie = {
            'id': movie_id,
            'title': row['title'],
            'release_date': row['release_date'],
            'budget': row['budget'],
            'revenue': row['revenue'],
            'popularity': row['popularity'],
            'vote_average': row['vote_average'],
            'vote_count': row['vote_count'],
            'overview': row['overview']
        }
        movies.append(movie)
        
        # Process genres
        for genre in row['genres']:
            genre_id = genre['id']
            genres[genre_id] = {'id': genre_id, 'name': genre['name']}
            categorized_as.append({'movie_id': movie_id, 'genre_id': genre_id})
        
        # Process keywords
        for keyword in row['keywords']:
            keyword_id = keyword['id']
            keywords[keyword_id] = {'id': keyword_id, 'name': keyword['name']}
            tagged_with.append({'movie_id': movie_id, 'keyword_id': keyword_id})
        
        # Process production companies
        for company in row['production_companies']:
            company_id = company['id']
            companies[company_id] = {
                'id': company_id, 
                'name': company['name'],
                'origin_country': company.get('origin_country', '')
            }
            produced.append({'movie_id': movie_id, 'company_id': company_id})
        
        # Process cast (actors)
        for i, actor in enumerate(row['cast'][:10]):  # Limit to top 10 actors
            person_id = actor['id']
            persons[person_id] = {
                'id': person_id,
                'name': actor['name'],
                'gender': actor.get('gender', 0),
                'profile_path': actor.get('profile_path', '')
            }
            acted_in.append({
                'person_id': person_id,
                'movie_id': movie_id,
                'character': actor['character'],
                'order': i
            })
        
        # Process crew (focus on directors)
        for crew_member in row['crew']:
            if crew_member['job'] == 'Director':
                person_id = crew_member['id']
                persons[person_id] = {
                    'id': person_id,
                    'name': crew_member['name'],
                    'gender': crew_member.get('gender', 0),
                    'profile_path': crew_member.get('profile_path', '')
                }
                directed.append({
                    'person_id': person_id,
                    'movie_id': movie_id,
                    'job': crew_member['job'],
                    'department': crew_member['department']
                })
    
    # Convert dictionaries to lists
    genres_list = list(genres.values())
    keywords_list = list(keywords.values())
    companies_list = list(companies.values())
    persons_list = list(persons.values())
    
    transformed_data = {
        'nodes': {
            'movies': movies,
            'persons': persons_list,
            'genres': genres_list,
            'keywords': keywords_list,
            'companies': companies_list
        },
        'relationships': {
            'acted_in': acted_in,
            'directed': directed,
            'produced': produced,
            'categorized_as': categorized_as,
            'tagged_with': tagged_with
        }
    }
    
    return transformed_data


def load_data(data: Dict[str, Dict[str, List[Dict[str, Any]]]], output_dir: str) -> None:
    """
    Save transformed data as CSV files for Neo4j import.
    
    Args:
        data: Dictionary containing transformed data
        output_dir: Directory to save output files
    """
    print("Loading data...")
    ensure_dir(output_dir)
    
    # Save nodes
    print("Saving nodes...")
    pd.DataFrame(data['nodes']['movies']).to_csv(os.path.join(output_dir, 'movies.csv'), index=False)
    pd.DataFrame(data['nodes']['persons']).to_csv(os.path.join(output_dir, 'persons.csv'), index=False)
    pd.DataFrame(data['nodes']['genres']).to_csv(os.path.join(output_dir, 'genres.csv'), index=False)
    pd.DataFrame(data['nodes']['keywords']).to_csv(os.path.join(output_dir, 'keywords.csv'), index=False)
    pd.DataFrame(data['nodes']['companies']).to_csv(os.path.join(output_dir, 'companies.csv'), index=False)
    
    # Save relationships
    print("Saving relationships...")
    pd.DataFrame(data['relationships']['acted_in']).to_csv(os.path.join(output_dir, 'acted_in.csv'), index=False)
    pd.DataFrame(data['relationships']['directed']).to_csv(os.path.join(output_dir, 'directed.csv'), index=False)
    pd.DataFrame(data['relationships']['produced']).to_csv(os.path.join(output_dir, 'produced.csv'), index=False)
    pd.DataFrame(data['relationships']['categorized_as']).to_csv(os.path.join(output_dir, 'categorized_as.csv'), index=False)
    pd.DataFrame(data['relationships']['tagged_with']).to_csv(os.path.join(output_dir, 'tagged_with.csv'), index=False)


def run_etl(input_dir: str, output_dir: str, movies_file: str = "tmdb_5000_movies.csv",
            credits_file: str = "tmdb_5000_credits.csv") -> None:
    """
    Run the complete ETL process.
    
    Args:
        input_dir: Directory containing input files
        output_dir: Directory to save output files
        movies_file: Filename for movies data
        credits_file: Filename for credits data
    """
    print("Starting ETL process...")
    
    # Extract
    data_df = extract_data(input_dir, movies_file, credits_file)
    
    # Transform
    transformed_data = transform_data(data_df)
    
    # Load
    load_data(transformed_data, output_dir)
    
    print("ETL process completed successfully!") 