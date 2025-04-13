#!/usr/bin/env python3
"""
Simple runner script for agent manager tests.
"""
import os
import sys
import pytest

def main():
    """Run the test suite."""
    # Add the parent directory to the path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Set up test arguments
    args = [
        "-v",                # Verbose output
        "--color=yes",       # Colored output
        "tests/",            # Test directory
    ]
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run the tests
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 