"""
Test ETL process for transforming TMDB movie dataset into Neo4j importable format.
Uses a small subset of data for testing and includes additional validation.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Tuple


def ensure_dir(directory: str) -> None:
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def parse_json_fields(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Parse JSON string fields into Python objects."""

    def safe_json_loads(x):
        if pd.isna(x):
            return []
        try:
            # Clean up the string representation
            x_str = str(x).strip()
            # Handle single quotes and other common issues
            x_str = x_str.replace("'", '"')
            x_str = x_str.replace("None", "null")
            x_str = x_str.replace("True", "true")
            x_str = x_str.replace("False", "false")
            return json.loads(x_str)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON: {x}")
            print(f"Error: {e}")
            return []

    for col in columns:
        df[col] = df[col].apply(safe_json_loads)
    return df


def transform_data(df: pd.DataFrame) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Transform the data into Neo4j compatible format."""
    print("Transforming data...")

    # Extract nodes
    movies = []
    persons = {}  # Using dict to avoid duplicates
    genres = {}  # Using dict to avoid duplicates
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
        movie_id = row["id"]

        # Movie node
        movie = {
            "id": movie_id,
            "title": row["title"],
            "release_date": row["release_date"],
            "budget": row["budget"],
            "revenue": row["revenue"],
            "popularity": row["popularity"],
            "vote_average": row["vote_average"],
            "vote_count": row["vote_count"],
            "overview": row["overview"],
        }
        movies.append(movie)

        # Process genres
        for genre in row["genres"]:
            genre_id = genre["id"]
            genres[genre_id] = {"id": genre_id, "name": genre["name"]}
            categorized_as.append({"movie_id": movie_id, "genre_id": genre_id})

        # Process keywords
        for keyword in row["keywords"]:
            keyword_id = keyword["id"]
            keywords[keyword_id] = {"id": keyword_id, "name": keyword["name"]}
            tagged_with.append({"movie_id": movie_id, "keyword_id": keyword_id})

        # Process production companies
        for company in row["production_companies"]:
            company_id = company["id"]
            companies[company_id] = {
                "id": company_id,
                "name": company["name"],
                "origin_country": company.get("origin_country", ""),
            }
            produced.append({"movie_id": movie_id, "company_id": company_id})

        # Process cast (actors)
        for i, actor in enumerate(row["cast"][:10]):  # Limit to top 10 actors
            person_id = actor["id"]
            persons[person_id] = {
                "id": person_id,
                "name": actor["name"],
                "gender": actor.get("gender", 0),
                "profile_path": actor.get("profile_path", ""),
            }
            acted_in.append(
                {
                    "person_id": person_id,
                    "movie_id": movie_id,
                    "character": actor["character"],
                    "order": i,
                }
            )

        # Process crew (focus on directors)
        for crew_member in row["crew"]:
            if crew_member["job"] == "Director":
                person_id = crew_member["id"]
                persons[person_id] = {
                    "id": person_id,
                    "name": crew_member["name"],
                    "gender": crew_member.get("gender", 0),
                    "profile_path": crew_member.get("profile_path", ""),
                }
                directed.append(
                    {
                        "person_id": person_id,
                        "movie_id": movie_id,
                        "job": crew_member["job"],
                        "department": crew_member["department"],
                    }
                )

    # Convert dictionaries to lists
    genres_list = list(genres.values())
    keywords_list = list(keywords.values())
    companies_list = list(companies.values())
    persons_list = list(persons.values())

    transformed_data = {
        "nodes": {
            "movies": movies,
            "persons": persons_list,
            "genres": genres_list,
            "keywords": keywords_list,
            "companies": companies_list,
        },
        "relationships": {
            "acted_in": acted_in,
            "directed": directed,
            "produced": produced,
            "categorized_as": categorized_as,
            "tagged_with": tagged_with,
        },
    }

    return transformed_data


def load_data(
    data: Dict[str, Dict[str, List[Dict[str, Any]]]], output_dir: str
) -> None:
    """Save transformed data as CSV files for Neo4j import."""
    print("Loading data...")
    ensure_dir(output_dir)

    # Save nodes
    print("Saving nodes...")
    pd.DataFrame(data["nodes"]["movies"]).to_csv(
        os.path.join(output_dir, "movies.csv"), index=False
    )
    pd.DataFrame(data["nodes"]["persons"]).to_csv(
        os.path.join(output_dir, "persons.csv"), index=False
    )
    pd.DataFrame(data["nodes"]["genres"]).to_csv(
        os.path.join(output_dir, "genres.csv"), index=False
    )
    pd.DataFrame(data["nodes"]["keywords"]).to_csv(
        os.path.join(output_dir, "keywords.csv"), index=False
    )
    pd.DataFrame(data["nodes"]["companies"]).to_csv(
        os.path.join(output_dir, "companies.csv"), index=False
    )

    # Save relationships
    print("Saving relationships...")
    pd.DataFrame(data["relationships"]["acted_in"]).to_csv(
        os.path.join(output_dir, "acted_in.csv"), index=False
    )
    pd.DataFrame(data["relationships"]["directed"]).to_csv(
        os.path.join(output_dir, "directed.csv"), index=False
    )
    pd.DataFrame(data["relationships"]["produced"]).to_csv(
        os.path.join(output_dir, "produced.csv"), index=False
    )
    pd.DataFrame(data["relationships"]["categorized_as"]).to_csv(
        os.path.join(output_dir, "categorized_as.csv"), index=False
    )
    pd.DataFrame(data["relationships"]["tagged_with"]).to_csv(
        os.path.join(output_dir, "tagged_with.csv"), index=False
    )


def extract_test_data(
    input_dir: str, movies_file: str, credits_file: str, sample_size: int = 10
) -> Tuple[pd.DataFrame, List[str]]:
    """Extract a small sample of data from raw CSV files for testing."""
    print(f"Extracting test data (sample size: {sample_size})...")
    validation_msgs = []

    # Read sample of movies
    movies_df = pd.read_csv(os.path.join(input_dir, movies_file))
    movies_sample = movies_df.head(sample_size)
    validation_msgs.append(f"Sampled {len(movies_sample)} movies from {movies_file}")

    # Read corresponding credits
    credits_df = pd.read_csv(os.path.join(input_dir, credits_file))
    credits_sample = credits_df[credits_df["movie_id"].isin(movies_sample["id"])]
    validation_msgs.append(f"Found {len(credits_sample)} matching credit records")

    # Rename id column in credits to match movies
    if "movie_id" in credits_sample.columns:
        credits_sample.rename(columns={"movie_id": "id"}, inplace=True)

    # Merge dataframes
    df = pd.merge(movies_sample, credits_sample, on="id")
    validation_msgs.append(f"Final merged dataset has {len(df)} rows")

    # Validate JSON columns before parsing
    json_columns = ["genres", "keywords", "production_companies", "cast", "crew"]
    for col in json_columns:
        if col not in df.columns:
            validation_msgs.append(f"Warning: Column {col} not found in dataset")
            continue

        # Check for non-null values
        null_count = df[col].isnull().sum()
        if null_count > 0:
            validation_msgs.append(f"Warning: {null_count} null values found in {col}")

        # Sample and validate JSON structure
        sample_value = df[col].iloc[0]
        validation_msgs.append(f"Sample {col} value: {sample_value}")

    # Convert string representations of lists/dicts to actual Python objects
    df = parse_json_fields(df, json_columns)

    return df, validation_msgs


def run_test_etl(
    input_dir: str,
    output_dir: str,
    movies_file: str = "tmdb_5000_movies.csv",
    credits_file: str = "tmdb_5000_credits.csv",
    sample_size: int = 10,
) -> None:
    """Run the ETL process on a small sample for testing."""
    print("Starting test ETL process...")

    # Extract test data
    data_df, validation_msgs = extract_test_data(
        input_dir, movies_file, credits_file, sample_size
    )

    # Print validation messages
    print("\nValidation Messages:")
    for msg in validation_msgs:
        print(f"- {msg}")

    # Transform
    print("\nTransforming test data...")
    transformed_data = transform_data(data_df)

    # Validate transformed data
    print("\nValidating transformed data:")
    for node_type, nodes in transformed_data["nodes"].items():
        print(f"- {node_type}: {len(nodes)} nodes")
    for rel_type, rels in transformed_data["relationships"].items():
        print(f"- {rel_type}: {len(rels)} relationships")

    # Load
    test_output_dir = os.path.join(output_dir, "test")
    load_data(transformed_data, test_output_dir)

    print("\nTest ETL process completed successfully!")
    print(f"Test output files saved to: {test_output_dir}")


if __name__ == "__main__":
    # Run test ETL with 10 movies
    run_test_etl(input_dir="data/raw", output_dir="data/processed", sample_size=10)
