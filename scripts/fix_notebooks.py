#!/usr/bin/env python
"""
Jupyter Notebook Fixer Script

This script fixes common issues in Jupyter notebooks (.ipynb files) to ensure 
they meet the requirements for both Cursor and Spark environments.
"""

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import nbformat
from nbformat.validator import validate


def load_notebook(notebook_path: str) -> Tuple[Dict[str, Any], bool]:
    """
    Loads a notebook from the given path.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Tuple of (notebook_content, success)
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
        return notebook_content, True
    except Exception as e:
        print(f"Error loading notebook {notebook_path}: {str(e)}")
        return {}, False


def save_notebook(notebook_path: str, notebook_content: Dict[str, Any]) -> bool:
    """
    Saves a notebook to the given path.
    
    Args:
        notebook_path: Path to save the notebook
        notebook_content: Notebook content to save
        
    Returns:
        Success status
    """
    try:
        # Ensure the notebook is valid before saving
        nb = nbformat.reads(json.dumps(notebook_content), as_version=4)
        validate(nb)
        
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook_content, f, indent=1)
        return True
    except Exception as e:
        print(f"Error saving notebook {notebook_path}: {str(e)}")
        return False


def fix_notebook_structure(notebook_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fixes structural issues in the notebook.
    
    Args:
        notebook_content: The notebook content
        
    Returns:
        Fixed notebook content
    """
    # Fix nbformat version
    notebook_content['nbformat'] = 4
    notebook_content['nbformat_minor'] = 5
    
    # Fix or add kernelspec
    if 'metadata' not in notebook_content:
        notebook_content['metadata'] = {}
        
    if 'kernelspec' not in notebook_content['metadata']:
        notebook_content['metadata']['kernelspec'] = {
            'display_name': 'Python 3',
            'language': 'python',
            'name': 'python3'
        }
    else:
        # Ensure kernel is Python-based
        kernelspec = notebook_content['metadata']['kernelspec']
        if not kernelspec.get('name') or 'python' not in kernelspec.get('name', '').lower():
            kernelspec['name'] = 'python3'
            kernelspec['display_name'] = 'Python 3'
            kernelspec['language'] = 'python'
    
    # Ensure cells array exists
    if 'cells' not in notebook_content:
        notebook_content['cells'] = []
        
    # Fix cell structures
    for i, cell in enumerate(notebook_content['cells']):
        # Fix missing cell type
        if 'cell_type' not in cell:
            # Default to code cell if source contains Python-like code indicators
            source = ''.join(cell.get('source', []))
            if any(kw in source for kw in ['import ', 'def ', 'class ', '= ', 'print(']):
                cell['cell_type'] = 'code'
            else:
                cell['cell_type'] = 'markdown'
        
        # Add metadata if missing
        if 'metadata' not in cell:
            cell['metadata'] = {}
            
        # Add cell ID if missing
        if 'id' not in cell['metadata']:
            cell['metadata']['id'] = str(uuid.uuid4())
            
        # Ensure source is present
        if 'source' not in cell:
            cell['source'] = []
            
        # Fix pyspark magic commands
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'spark.sql' in source and not source.strip().startswith('%%pyspark'):
                if isinstance(cell['source'], list):
                    cell['source'] = ['%%pyspark\n'] + cell['source']
                else:
                    cell['source'] = f"%%pyspark\n{cell['source']}"
    
    return notebook_content


def fix_spark_compatibility(notebook_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fixes Spark compatibility issues in the notebook.
    
    Args:
        notebook_content: The notebook content
        
    Returns:
        Fixed notebook content
    """
    cells = notebook_content.get('cells', [])
    
    # Check if notebook uses Spark
    uses_spark = any('spark.' in ''.join(cell.get('source', []))
                    if cell.get('cell_type') == 'code' else False 
                    for cell in cells)
                    
    if not uses_spark:
        return notebook_content
        
    # Check if SparkSession is initialized
    spark_initialized = any('SparkSession' in ''.join(cell.get('source', []))
                         and '.builder' in ''.join(cell.get('source', []))
                         if cell.get('cell_type') == 'code' else False
                         for cell in cells)
                         
    if not spark_initialized:
        # Add SparkSession initialization cell at the beginning
        spark_init_cell = {
            'cell_type': 'code',
            'metadata': {'id': str(uuid.uuid4())},
            'source': [
                '# Initialize Spark Session\n',
                'from pyspark.sql import SparkSession\n',
                '\n',
                'spark = SparkSession.builder \\\n',
                '    .appName("Notebook") \\\n',
                '    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \\\n',
                '    .getOrCreate()\n'
            ],
            'execution_count': None,
            'outputs': []
        }
        
        # Find the best position to insert - after imports but before other code
        inserted = False
        for i, cell in enumerate(cells):
            if cell.get('cell_type') != 'code':
                continue
                
            source = ''.join(cell.get('source', []))
            if 'import ' in source and not any(x in source for x in [
                'spark.', 'SparkContext', 'SparkSession'
            ]):
                notebook_content['cells'].insert(i + 1, spark_init_cell)
                inserted = True
                break
                
        if not inserted:
            # Insert after the first markdown cell or at the beginning
            for i, cell in enumerate(cells):
                if cell.get('cell_type') == 'markdown':
                    notebook_content['cells'].insert(i + 1, spark_init_cell)
                    inserted = True
                    break
                    
            if not inserted:
                notebook_content['cells'].insert(0, spark_init_cell)
    
    # Fix DataFrame caching
    for i, cell in enumerate(notebook_content['cells']):
        if cell.get('cell_type') != 'code':
            continue
            
        source = ''.join(cell.get('source', []))
        if 'spark.read' in source and '.cache()' not in source and '.persist(' not in source:
            # Add caching to dataframe assignment lines
            lines = source.split('\n')
            modified_lines = []
            
            for line in lines:
                if '=' in line and 'spark.read' in line:
                    var_name = line.split('=')[0].strip()
                    modified_lines.append(line)
                    modified_lines.append(f"{var_name} = {var_name}.cache()  # Improved performance with caching")
                else:
                    modified_lines.append(line)
                    
            if isinstance(cell['source'], list):
                cell['source'] = [line + '\n' for line in modified_lines[:-1]] + [modified_lines[-1]]
            else:
                cell['source'] = '\n'.join(modified_lines)
                
    return notebook_content


def fix_cursor_integration(notebook_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fixes Cursor integration issues in the notebook.
    
    Args:
        notebook_content: The notebook content
        
    Returns:
        Fixed notebook content
    """
    cells = notebook_content.get('cells', [])
    
    # Check if notebook has a title
    has_header = any(
        cell.get('cell_type') == 'markdown' and 
        ''.join(cell.get('source', [])).startswith('# ')
        for cell in cells
    )
    
    if not has_header:
        # Extract a potential title from the filename or use a default
        notebook_path = notebook_content.get('_file_path', 'Notebook')
        if notebook_path:
            title = os.path.splitext(os.path.basename(notebook_path))[0]
            title = title.replace('_', ' ').title()
        else:
            title = "Untitled Notebook"
            
        # Create title cell
        title_cell = {
            'cell_type': 'markdown',
            'metadata': {'id': str(uuid.uuid4())},
            'source': [f"# {title}\n", "\n", "This notebook was automatically formatted for Cursor and Spark compatibility.\n"]
        }
        
        # Insert at the beginning
        notebook_content['cells'].insert(0, title_cell)
    
    # Check for section headers
    has_sections = any(
        cell.get('cell_type') == 'markdown' and 
        ''.join(cell.get('source', [])).startswith('## ')
        for cell in cells
    )
    
    if not has_sections:
        # Add a default section before the first code cell
        for i, cell in enumerate(cells):
            if cell.get('cell_type') == 'code':
                section_cell = {
                    'cell_type': 'markdown',
                    'metadata': {'id': str(uuid.uuid4())},
                    'source': ["## Data Processing\n", "\n", "This section contains code for data processing.\n"]
                }
                notebook_content['cells'].insert(i, section_cell)
                break
    
    # Ensure all cells have IDs
    for cell in cells:
        if 'metadata' not in cell:
            cell['metadata'] = {}
        if 'id' not in cell['metadata']:
            cell['metadata']['id'] = str(uuid.uuid4())
    
    return notebook_content


def fix_notebook(notebook_path: str) -> bool:
    """
    Fixes issues in a notebook to make it Cursor and Spark compatible.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Success status
    """
    # Load the notebook
    notebook_content, success = load_notebook(notebook_path)
    if not success:
        return False
        
    # Store the original path for reference
    notebook_content['_file_path'] = notebook_path
    
    # Apply fixes
    notebook_content = fix_notebook_structure(notebook_content)
    notebook_content = fix_spark_compatibility(notebook_content)
    notebook_content = fix_cursor_integration(notebook_content)
    
    # Remove temporary field
    if '_file_path' in notebook_content:
        del notebook_content['_file_path']
    
    # Save the fixed notebook
    return save_notebook(notebook_path, notebook_content)


def main():
    """Main function to fix all notebooks."""
    notebooks_dir = Path('notebooks')
    
    if not notebooks_dir.exists():
        print(f"Error: Notebooks directory {notebooks_dir} not found")
        sys.exit(1)
        
    notebook_files = list(notebooks_dir.glob('**/*.ipynb'))
    if not notebook_files:
        print("No notebook files found to fix")
        sys.exit(0)
        
    print(f"Found {len(notebook_files)} notebook(s) to fix")
    
    all_fixed = True
    
    for notebook_path in notebook_files:
        # Skip checkpoints
        if '.ipynb_checkpoints' in str(notebook_path):
            print(f"Skipping checkpoint file: {notebook_path}")
            continue
            
        print(f"\nFixing {notebook_path}...")
        success = fix_notebook(str(notebook_path))
        
        if success:
            print(f"✅ Successfully fixed {notebook_path}")
        else:
            all_fixed = False
            print(f"❌ Failed to fix {notebook_path}")
    
    if all_fixed:
        print("\nAll notebooks have been fixed successfully!")
        sys.exit(0)
    else:
        print("\nSome notebooks could not be fixed. Please check the errors.")
        sys.exit(1)


if __name__ == "__main__":
    main() 