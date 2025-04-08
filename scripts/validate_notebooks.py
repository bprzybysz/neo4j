#!/usr/bin/env python
"""
Jupyter Notebook Validator Script

This script validates Jupyter notebooks (.ipynb files) to ensure they meet
the requirements for both Cursor and Spark environments.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import nbformat
from nbformat.validator import validate


def validate_notebook_structure(notebook_path: str) -> Tuple[bool, List[str]]:
    """
    Validates the basic structure of a Jupyter notebook.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
            
        # Validate with nbformat
        try:
            nb = nbformat.reads(json.dumps(notebook_content), as_version=4)
            validate(nb)
        except Exception as e:
            issues.append(f"nbformat validation failed: {str(e)}")
            return False, issues
            
        # Check nbformat version
        if notebook_content.get('nbformat') != 4:
            issues.append(f"nbformat should be 4, got {notebook_content.get('nbformat')}")
        
        if notebook_content.get('nbformat_minor', 0) < 5:
            issues.append(f"nbformat_minor should be at least 5, got {notebook_content.get('nbformat_minor')}")
            
        # Check if kernelspec is present and valid
        metadata = notebook_content.get('metadata', {})
        kernelspec = metadata.get('kernelspec', {})
        
        if not kernelspec:
            issues.append("Missing kernelspec in metadata")
        else:
            kernel_name = kernelspec.get('name')
            if not kernel_name:
                issues.append("Missing kernel name in kernelspec")
            elif "python" not in kernel_name.lower():
                issues.append(f"Kernel should be Python-based, got {kernel_name}")
                
        # Check cells structure
        cells = notebook_content.get('cells', [])
        if not cells:
            issues.append("Notebook has no cells")
            
        for i, cell in enumerate(cells):
            # Check cell type
            if 'cell_type' not in cell:
                issues.append(f"Cell {i} is missing cell_type")
                
            # Check cell metadata
            cell_metadata = cell.get('metadata', {})
            if not cell_metadata:
                issues.append(f"Cell {i} has no metadata")
            
            # Check if cell has source
            if 'source' not in cell:
                issues.append(f"Cell {i} is missing source content")
                
            # Check for code cells using pyspark
            if cell.get('cell_type') == 'code' and isinstance(cell.get('source'), list):
                source = ''.join(cell.get('source', []))
                if 'spark.sql' in source and not source.strip().startswith('%%pyspark'):
                    issues.append(f"Cell {i} contains Spark SQL but is missing %%pyspark magic")
                    
        return len(issues) == 0, issues
        
    except Exception as e:
        issues.append(f"Failed to validate notebook: {str(e)}")
        return False, issues


def validate_spark_compatibility(notebook_path: str) -> Tuple[bool, List[str]]:
    """
    Validates if the notebook is compatible with Spark environment.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
            
        cells = notebook_content.get('cells', [])
        
        spark_session_initialized = False
        for i, cell in enumerate(cells):
            if cell.get('cell_type') != 'code':
                continue
                
            source = ''.join(cell.get('source', []))
            
            # Check for SparkSession initialization
            if 'SparkSession' in source and '.builder' in source:
                spark_session_initialized = True
                
            # Check for direct SparkContext usage without session
            if 'SparkContext' in source and not spark_session_initialized:
                issues.append(f"Cell {i} uses SparkContext directly without SparkSession")
                
            # Check for appropriate DataFrame caching
            if 'spark.read' in source and '.cache()' not in source and '.persist(' not in source:
                issues.append(f"Cell {i} loads data without caching strategy")
                
        if not spark_session_initialized and any('spark.' in ''.join(cell.get('source', [])) 
                                               for cell in cells 
                                               if cell.get('cell_type') == 'code'):
            issues.append("Notebook uses Spark but does not initialize SparkSession")
            
        return len(issues) == 0, issues
        
    except Exception as e:
        issues.append(f"Failed to validate Spark compatibility: {str(e)}")
        return False, issues


def validate_cursor_integration(notebook_path: str) -> Tuple[bool, List[str]]:
    """
    Validates if the notebook follows Cursor integration best practices.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
            
        cells = notebook_content.get('cells', [])
        
        has_header = False
        section_headers = 0
        
        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type')
            
            # Check for markdown cells with headers
            if cell_type == 'markdown':
                source = ''.join(cell.get('source', []))
                if source.startswith('# '):
                    has_header = True
                if source.startswith('## '):
                    section_headers += 1
                    
            # Check for cell IDs in metadata
            cell_metadata = cell.get('metadata', {})
            if 'id' not in cell_metadata:
                issues.append(f"Cell {i} is missing an ID in metadata")
                
        # Ensure notebook has a title and sections
        if not has_header:
            issues.append("Notebook is missing a title (# Header)")
            
        if section_headers == 0:
            issues.append("Notebook has no section headers (## Section)")
            
        return len(issues) == 0, issues
        
    except Exception as e:
        issues.append(f"Failed to validate Cursor integration: {str(e)}")
        return False, issues


def main():
    """Main function to validate all notebooks."""
    notebooks_dir = Path('notebooks')
    
    if not notebooks_dir.exists():
        print(f"Error: Notebooks directory {notebooks_dir} not found")
        sys.exit(1)
        
    notebook_files = list(notebooks_dir.glob('**/*.ipynb'))
    if not notebook_files:
        print("No notebook files found to validate")
        sys.exit(0)
        
    print(f"Found {len(notebook_files)} notebook(s) to validate")
    
    all_valid = True
    
    for notebook_path in notebook_files:
        print(f"\nValidating {notebook_path}...")
        
        # Skip checkpoints
        if '.ipynb_checkpoints' in str(notebook_path):
            print(f"Skipping checkpoint file: {notebook_path}")
            continue
            
        # Validate structure
        structure_valid, structure_issues = validate_notebook_structure(str(notebook_path))
        if not structure_valid:
            all_valid = False
            print("❌ Structure validation failed:")
            for issue in structure_issues:
                print(f"  - {issue}")
        else:
            print("✅ Structure validation passed")
            
        # Validate Spark compatibility
        spark_valid, spark_issues = validate_spark_compatibility(str(notebook_path))
        if not spark_valid:
            all_valid = False
            print("❌ Spark compatibility validation failed:")
            for issue in spark_issues:
                print(f"  - {issue}")
        else:
            print("✅ Spark compatibility validation passed")
            
        # Validate Cursor integration
        cursor_valid, cursor_issues = validate_cursor_integration(str(notebook_path))
        if not cursor_valid:
            all_valid = False
            print("❌ Cursor integration validation failed:")
            for issue in cursor_issues:
                print(f"  - {issue}")
        else:
            print("✅ Cursor integration validation passed")
    
    if all_valid:
        print("\nAll notebooks are valid!")
        sys.exit(0)
    else:
        print("\nSome notebooks have validation issues. Please fix them or run the fix_notebooks.py script.")
        sys.exit(1)


if __name__ == "__main__":
    main() 