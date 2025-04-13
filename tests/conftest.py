"""
Pytest configuration for agent manager tests.
"""
import os
import sys
import pytest

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define global fixtures here if needed
@pytest.fixture(scope="session", autouse=True)
def setup_tests():
    """Set up any global test requirements."""
    # Create any necessary directories or resources
    from config import TEMP_AGENTS_DIR
    os.makedirs(TEMP_AGENTS_DIR, exist_ok=True)
    
    yield
    
    # Clean up after all tests
    # This runs after all tests have completed
    pass 