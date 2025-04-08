import json
import re
import os

def convert_notebook(input_file: str, output_file: str) -> None:
    """
    Convert a text file with cell markers to Jupyter notebook format.
    
    Args:
        input_file (str): Path to input text file
        output_file (str): Path to output ipynb file
    """
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
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(notebook, f, indent=2)

if __name__ == '__main__':
    convert_notebook('notebooks/movie_analysis.txt', 'notebooks/movie_analysis.ipynb')
    print('Conversion completed successfully.') 