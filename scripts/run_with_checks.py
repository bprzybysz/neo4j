#!/usr/bin/env python3
"""
Wrapper script to run Python scripts with environment checks.
This ensures SSH key and virtual environment are properly set up before execution.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

def run_environment_checks() -> bool:
    """Run the environment check script."""
    check_script = Path(__file__).parent.parent / "check_environment.sh"
    try:
        subprocess.run(["bash", str(check_script)], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Environment checks failed. Please fix the issues above.")
        return False

def run_script(script_path: str, args: List[str]) -> Optional[int]:
    """
    Run the specified Python script with given arguments.
    
    Args:
        script_path: Path to the Python script to run
        args: List of command line arguments for the script
        
    Returns:
        Return code from the script execution or None if checks failed
    """
    if not run_environment_checks():
        return None
        
    # Execute the target script
    try:
        result = subprocess.run([sys.executable, script_path] + args)
        return result.returncode
    except Exception as e:
        print(f"Error executing script: {e}")
        return 1

def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python run_with_checks.py <script_path> [args...]")
        return 1
        
    script_path = sys.argv[1]
    script_args = sys.argv[2:]
    
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        return 1
        
    result = run_script(script_path, script_args)
    return 0 if result is None else result

if __name__ == "__main__":
    sys.exit(main()) 