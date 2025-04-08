#!/usr/bin/env python3
"""
ETL script to transform TMDB movie dataset into Neo4j importable format.
"""
import pandas as pd
import json
import os
import ast

# Configuration
INPUT_DIR = "../data/raw"
OUTPUT_DIR = "../data/processed"
MOVIES_FILE = "tmdb_5000_movies.csv"
CREDITS_FILE = "tmdb_5000_credits.csv"

def ensure_dir(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def parse_json_fields(df, columns):
    """Parse JSON string fields into Python objects."""
    for col in columns:
        df[col] = df[col].apply(lambda x: json.loads(str(x).replace("'", "\"")) if pd.notnull(x) else [])
    return df

def extract_data():
    """Extract data from raw CSV files."""
    print("Extracting data...")
    
    movies_df = pd.read_csv(os.path.join(INPUT_DIR, MOVIES_FILE))
    credits_df = pd.read_csv(os.path.join(INPUT_DIR, CREDITS_FILE))
    
    # Rename id column in credits to match movies
    if 'movie_id' in credits_df.columns:
        credits_df.rename(columns={'movie_id': 'id'}, inplace=True)
    
    # Merge dataframes
    df = pd.merge(movies_df, credits_df, on='id')
    
    # Convert string representations of lists/dicts to actual Python objects
    json_columns = ['genres', 'keywords', 'production_companies', 'cast', 'crew']
    df = parse_json_fields(df, json_columns)
    
    return df

def transform_data(df):
    """Transform the data into Neo4j compatible format."""
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
    genres = list(genres.values())
    keywords = list(keywords.values())
    companies = list(companies.values())
    persons = list(persons.values())
    
    transformed_data = {
        'nodes': {
            'movies': movies,
            'persons': persons,
            'genres': genres,
            'keywords': keywords,
            'companies': companies
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

def load_data(data):
    """Save transformed data as CSV files for Neo4j import."""
    print("Loading data...")
    ensure_dir(OUTPUT_DIR)
    
    # Save nodes
    print("Saving nodes...")
    pd.DataFrame(data['nodes']['movies']).to_csv(os.path.join(OUTPUT_DIR, 'movies.csv'), index=False)
    pd.DataFrame(data['nodes']['persons']).to_csv(os.path.join(OUTPUT_DIR, 'persons.csv'), index=False)
    pd.DataFrame(data['nodes']['genres']).to_csv(os.path.join(OUTPUT_DIR, 'genres.csv'), index=False)
    pd.DataFrame(data['nodes']['keywords']).to_csv(os.path.join(OUTPUT_DIR, 'keywords.csv'), index=False)
    pd.DataFrame(data['nodes']['companies']).to_csv(os.path.join(OUTPUT_DIR, 'companies.csv'), index=False)
    
    # Save relationships
    print("Saving relationships...")
    pd.DataFrame(data['relationships']['acted_in']).to_csv(os.path.join(OUTPUT_DIR, 'acted_in.csv'), index=False)
    pd.DataFrame(data['relationships']['directed']).to_csv(os.path.join(OUTPUT_DIR, 'directed.csv'), index=False)
    pd.DataFrame(data['relationships']['produced']).to_csv(os.path.join(OUTPUT_DIR, 'produced.csv'), index=False)
    pd.DataFrame(data['relationships']['categorized_as']).to_csv(os.path.join(OUTPUT_DIR, 'categorized_as.csv'), index=False)
    pd.DataFrame(data['relationships']['tagged_with']).to_csv(os.path.join(OUTPUT_DIR, 'tagged_with.csv'), index=False)

def main():
    """Main ETL process."""
    print("Starting ETL process...")
    
    # Extract
    data_df = extract_data()
    
    # Transform
    transformed_data = transform_data(data_df)
    
    # Load
    load_data(transformed_data)
    
    print("ETL process completed successfully!")

if __name__ == "__main__":
    main() 