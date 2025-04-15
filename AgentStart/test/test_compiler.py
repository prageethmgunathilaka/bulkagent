"""
Tests for the AgentStart compiler
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch
from AgentStart.compiler import compile_file, run_file

class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.as")
        
        # Create a test AgentStart file
        with open(self.test_file, "w") as f:
            f.write("agent testAgent = create\ntell testAgent 'Hello'\nfree testAgent")
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        py_file = os.path.join(self.test_dir, "test.py")
        if os.path.exists(py_file):
            os.remove(py_file)
            
        os.rmdir(self.test_dir)
    
    def test_compile_file(self):
        """Test compiling an AgentStart file"""
        # Compile the test file
        output_file = compile_file(self.test_file)
        
        # Check if output file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Check file content
        with open(output_file, "r") as f:
            content = f.read()
        
        self.assertIn("from agent_core import Agent", content)
        self.assertIn('testAgent = Agent("testAgent")', content)
    
    def test_compile_file_with_custom_output(self):
        """Test compiling with a custom output file"""
        custom_output = os.path.join(self.test_dir, "custom_output.py")
        output_file = compile_file(self.test_file, custom_output)
        
        # Check if the correct output file was created
        self.assertEqual(output_file, custom_output)
        self.assertTrue(os.path.exists(custom_output))
        
        # Clean up the custom output file
        os.remove(custom_output)
    
    @patch('AgentStart.compiler.exec')
    def test_run_file(self, mock_exec):
        """Test running an AgentStart file"""
        # Run the test file
        run_file(self.test_file)
        
        # Check if exec was called
        mock_exec.assert_called_once()
    
    @patch('sys.argv', ['compiler.py'])
    @patch('sys.exit')
    def test_main_no_args(self, mock_exit):
        """Test running the compiler with no arguments"""
        # Import __main__ to trigger the main logic
        from AgentStart.compiler import __name__
        if __name__ == "__main__":
            # This shouldn't execute in the test, but just in case
            pass
        
        # Check if sys.exit was called
        mock_exit.assert_called_once()
    
    @patch('sys.argv', ['compiler.py', 'test.as'])
    @patch('AgentStart.compiler.compile_file')
    def test_main_compile(self, mock_compile):
        """Test running the compiler with just an input file"""
        # Import __main__ to trigger the main logic
        from AgentStart.compiler import __name__
        if __name__ == "__main__":
            # This shouldn't execute in the test, but just in case
            pass
        
        # Check if compile_file was called
        mock_compile.assert_called_once()
    
    @patch('sys.argv', ['compiler.py', 'test.as', '--run'])
    @patch('AgentStart.compiler.run_file')
    def test_main_run(self, mock_run):
        """Test running the compiler with the run flag"""
        # Import __main__ to trigger the main logic
        from AgentStart.compiler import __name__
        if __name__ == "__main__":
            # This shouldn't execute in the test, but just in case
            pass
        
        # Check if run_file was called
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main() 