"""
Utility helper functions for the Neo4j Movie Analysis project.
"""
import json
import re
import os
from typing import Dict, List, Any, Union, Optional


def ensure_dir(directory: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Path to directory to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def convert_text_to_notebook(input_file: str, output_file: str) -> None:
    """
    Convert text file to Jupyter notebook format.
    
    Args:
        input_file: Path to input text file
        output_file: Path to output notebook file
    """
    # Ensure output directory exists
    ensure_dir(os.path.dirname(output_file))
    
    # Read the text file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Initialize notebook structure
    notebook = {
        'cells': [],
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'
            },
            'language_info': {
                'codemirror_mode': {
                    'name': 'ipython',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.8.0'
            }
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }
    
    # Split content into cells
    cell_pattern = re.compile(r'# %% \[(markdown|code)\](?: id=\"([^\"]+)\")?\n((?:.+\n)*?)(?=# %% |$)', re.DOTALL)
    matches = cell_pattern.finditer(content)
    
    for match in matches:
        cell_type, cell_id, cell_content = match.groups()
        
        # Process cell content based on type
        if cell_type == 'markdown':
            # Remove the leading # from each line in markdown cells
            source = [line[2:] + '\n' if line.startswith('# ') else line + '\n' 
                     for line in cell_content.split('\n') if line]
            cell = {
                'cell_type': 'markdown',
                'metadata': {'id': cell_id} if cell_id else {},
                'source': source
            }
        else:  # code cell
            source = [line + '\n' for line in cell_content.split('\n') if line]
            cell = {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {'id': cell_id} if cell_id else {},
                'outputs': [],
                'source': source
            }
        
        notebook['cells'].append(cell)
    
    # Write to ipynb file
    with open(output_file, 'w') as f:
        json.dump(notebook, f, indent=2)
    
    print(f'Conversion completed: {output_file} created successfully.')


def clean_text(text: str) -> str:
    """
    Clean and normalize text for consistency.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    return text 