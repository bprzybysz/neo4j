#!/bin/bash

# Function to check if SSH key is added to ssh-agent
check_ssh_key() {
    local key_path="$HOME/.ssh/id_ed25519_git_private2"
    
    # Check if key exists
    if [ ! -f "$key_path" ]; then
        echo "Error: SSH key not found at $key_path"
        return 1
    fi
    
    # Check if ssh-agent is running
    if ! pgrep -u "$USER" ssh-agent > /dev/null; then
        eval "$(ssh-agent -s)"
    fi
    
    # Check if key is already added
    if ! ssh-add -l | grep -q "$key_path"; then
        echo "Adding SSH key to ssh-agent..."
        ssh-add "$key_path"
    fi
    
    return 0
}

# Function to check virtual environment
check_venv() {
    if [ ! -d ".venv" ]; then
        echo "Error: Virtual environment not found. Please run setup_venv.sh first."
        return 1
    fi
    
    # Check if venv is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    return 0
}

# Main check function
main() {
    local check_failed=0
    
    echo "Checking environment..."
    
    # Check SSH key
    if ! check_ssh_key; then
        check_failed=1
    fi
    
    # Check virtual environment
    if ! check_venv; then
        check_failed=1
    fi
    
    if [ $check_failed -eq 1 ]; then
        echo "Environment check failed. Please fix the issues above."
        exit 1
    fi
    
    echo "Environment check passed!"
    return 0
}

# Run main function
main 