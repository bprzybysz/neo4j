#!/usr/bin/env python3
"""
ETL script to transform TMDB movie dataset into Neo4j importable format.
"""
import os
import sys
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movie_graph.etl.process import run_etl


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Transform movie data for Neo4j import')
    parser.add_argument('--input', type=str, default='data/raw',
                        help='Directory containing input files')
    parser.add_argument('--output', type=str, default='data/processed',
                        help='Directory to save output files')
    parser.add_argument('--movies', type=str, default='tmdb_5000_movies.csv',
                        help='Filename for movies data')
    parser.add_argument('--credits', type=str, default='tmdb_5000_credits.csv',
                        help='Filename for credits data')
    return parser.parse_args()


def main():
    """Main ETL process."""
    args = parse_args()
    
    # Run ETL process
    run_etl(
        input_dir=args.input,
        output_dir=args.output,
        movies_file=args.movies,
        credits_file=args.credits
    )


if __name__ == "__main__":
    main() 