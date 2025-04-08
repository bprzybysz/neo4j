#!/usr/bin/env python
"""
Jupyter Notebook Template Generator

This script creates a properly formatted Jupyter notebook template
that adheres to the Cursor and Spark compatibility requirements.
"""

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

import nbformat
from nbformat.validator import validate


def create_notebook_template(
    output_path: str,
    title: str = "Notebook Template",
    with_spark: bool = True
) -> bool:
    """
    Creates a properly formatted Jupyter notebook template.
    
    Args:
        output_path: Path to save the notebook
        title: Title of the notebook
        with_spark: Whether to include Spark integration
        
    Returns:
        Success status
    """
    # Create notebook structure
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.8"
            }
        },
        "cells": []
    }
    
    # Add title cell
    title_cell = {
        "cell_type": "markdown",
        "metadata": {"id": str(uuid.uuid4())},
        "source": [
            f"# {title}\n",
            "\n",
            "This notebook was created following the standard format for compatibility with Cursor and Spark environments.\n"
        ]
    }
    notebook["cells"].append(title_cell)
    
    # Add imports cell
    imports_cell = {
        "cell_type": "code",
        "metadata": {"id": str(uuid.uuid4())},
        "source": [
            "# Standard imports\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "\n",
            "# Configure visualization\n",
            "plt.style.use('ggplot')\n",
            "sns.set(style=\"whitegrid\")\n"
        ],
        "execution_count": None,
        "outputs": []
    }
    notebook["cells"].append(imports_cell)
    
    # Add Spark session initialization if requested
    if with_spark:
        spark_section_cell = {
            "cell_type": "markdown",
            "metadata": {"id": str(uuid.uuid4())},
            "source": [
                "## Spark Integration\n",
                "\n",
                "Initialize Spark session for data processing.\n"
            ]
        }
        notebook["cells"].append(spark_section_cell)
        
        spark_init_cell = {
            "cell_type": "code",
            "metadata": {"id": str(uuid.uuid4())},
            "source": [
                "# Initialize Spark Session\n",
                "from pyspark.sql import SparkSession\n",
                "\n",
                "spark = SparkSession.builder \\\n",
                "    .appName(\"Notebook\") \\\n",
                "    .config(\"spark.sql.execution.arrow.pyspark.enabled\", \"true\") \\\n",
                "    .getOrCreate()\n"
            ],
            "execution_count": None,
            "outputs": []
        }
        notebook["cells"].append(spark_init_cell)
        
        spark_data_cell = {
            "cell_type": "code",
            "metadata": {"id": str(uuid.uuid4())},
            "source": [
                "# Load data with Spark\n",
                "# Replace with your actual data source\n",
                "df = spark.read.csv(\"data/sample.csv\", header=True, inferSchema=True)\n",
                "df = df.cache()  # Improved performance with caching\n",
                "\n",
                "# Display sample data\n",
                "df.limit(5).toPandas()\n"
            ],
            "execution_count": None,
            "outputs": []
        }
        notebook["cells"].append(spark_data_cell)
        
        spark_sql_cell = {
            "cell_type": "code",
            "metadata": {"id": str(uuid.uuid4())},
            "source": [
                "%%pyspark\n",
                "# Spark SQL example\n",
                "df.createOrReplaceTempView(\"data\")\n",
                "\n",
                "result = spark.sql(\"\"\"\n",
                "SELECT *\n",
                "FROM data\n",
                "LIMIT 10\n",
                "\"\"\")\n",
                "\n",
                "result.toPandas()\n"
            ],
            "execution_count": None,
            "outputs": []
        }
        notebook["cells"].append(spark_sql_cell)
    
    # Add data analysis section
    analysis_section_cell = {
        "cell_type": "markdown",
        "metadata": {"id": str(uuid.uuid4())},
        "source": [
            "## Data Analysis\n",
            "\n",
            "This section contains data analysis code.\n"
        ]
    }
    notebook["cells"].append(analysis_section_cell)
    
    analysis_code_cell = {
        "cell_type": "code",
        "metadata": {"id": str(uuid.uuid4())},
        "source": [
            "# Data analysis example\n",
            "# Replace with your actual analysis code\n",
            "\n",
            "# Sample DataFrame for demonstration\n",
            "sample_df = pd.DataFrame({\n",
            "    'A': np.random.randn(100),\n",
            "    'B': np.random.randn(100),\n",
            "    'C': np.random.randn(100)\n",
            "})\n",
            "\n",
            "# Display sample data\n",
            "sample_df.head()\n"
        ],
        "execution_count": None,
        "outputs": []
    }
    notebook["cells"].append(analysis_code_cell)
    
    visualization_code_cell = {
        "cell_type": "code",
        "metadata": {"id": str(uuid.uuid4())},
        "source": [
            "# Visualization example\n",
            "plt.figure(figsize=(10, 6))\n",
            "sns.histplot(data=sample_df, x='A', kde=True)\n",
            "plt.title('Distribution of A')\n",
            "plt.xlabel('Value')\n",
            "plt.ylabel('Frequency')\n",
            "plt.grid(True)\n",
            "plt.show()\n"
        ],
        "execution_count": None,
        "outputs": []
    }
    notebook["cells"].append(visualization_code_cell)
    
    # Add conclusion section
    conclusion_cell = {
        "cell_type": "markdown",
        "metadata": {"id": str(uuid.uuid4())},
        "source": [
            "## Conclusion\n",
            "\n",
            "Summary of findings and next steps.\n"
        ]
    }
    notebook["cells"].append(conclusion_cell)
    
    # Save notebook
    try:
        # Validate with nbformat
        nb = nbformat.reads(json.dumps(notebook), as_version=4)
        validate(nb)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
            
        print(f"✅ Successfully created notebook template at {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating notebook template: {str(e)}")
        return False


def main():
    """Main function to create a notebook template."""
    if len(sys.argv) < 2:
        print("Usage: python create_notebook_template.py <output_path> [title] [with_spark]")
        print("  output_path: Path to save the notebook")
        print("  title: Title of the notebook (optional, defaults to 'Notebook Template')")
        print("  with_spark: Include Spark integration (optional, 'true' or 'false', defaults to 'true')")
        sys.exit(1)
        
    output_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Notebook Template"
    with_spark = True
    if len(sys.argv) > 3:
        with_spark = sys.argv[3].lower() in ('true', 'yes', '1')
        
    success = create_notebook_template(output_path, title, with_spark)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 