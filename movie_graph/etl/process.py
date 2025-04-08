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
    Parse JSON string fields into Python objects.
    
    Args:
        df: DataFrame containing JSON string columns
        columns: List of column names to parse
        
    Returns:
        DataFrame with JSON strings converted to Python objects
    """
    for col in columns:
        df[col] = df[col].apply(lambda x: json.loads(str(x).replace("'", "\"")) if pd.notnull(x) else [])
    return df


def extract_data(input_dir: str, movies_file: str, credits_file: str) -> pd.DataFrame:
    """
    Extract data from raw CSV files.
    
    Args:
        input_dir: Directory containing input files
        movies_file: Filename for movies data
        credits_file: Filename for credits data
        
    Returns:
        DataFrame containing merged movie data
    """
    print("Extracting data...")
    
    movies_df = pd.read_csv(os.path.join(input_dir, movies_file))
    credits_df = pd.read_csv(os.path.join(input_dir, credits_file))
    
    # Rename id column in credits to match movies
    if 'movie_id' in credits_df.columns:
        credits_df.rename(columns={'movie_id': 'id'}, inplace=True)
    
    # Merge dataframes
    df = pd.merge(movies_df, credits_df, on='id')
    
    # Convert string representations of lists/dicts to actual Python objects
    json_columns = ['genres', 'keywords', 'production_companies', 'cast', 'crew']
    df = parse_json_fields(df, json_columns)
    
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