#!/usr/bin/env python3
import unittest
import sys
import os

# Add the parent directory to the path so we can import AgentStart
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Find and run all tests
loader = unittest.TestLoader()
tests = loader.discover('AgentStart/test')
runner = unittest.TextTestRunner()
result = runner.run(tests)

# Return non-zero exit code if tests failed
sys.exit(not result.wasSuccessful()) 