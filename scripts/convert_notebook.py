#!/usr/bin/env python3
"""
Script to convert text files to Jupyter notebook format.
"""
import os
import sys
import argparse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movie_graph.utils.helpers import convert_text_to_notebook


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Convert text file to Jupyter notebook')
    parser.add_argument('input', type=str, help='Input text file path')
    parser.add_argument('output', type=str, help='Output notebook file path')
    return parser.parse_args()


def main():
    """Main conversion process."""
    args = parse_args()
    
    # Convert text to notebook
    convert_text_to_notebook(args.input, args.output)


if __name__ == "__main__":
    main() 