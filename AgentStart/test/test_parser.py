"""
Tests for the AgentStart parser
"""

import unittest
import os
import tempfile
from AgentStart.parser import AgentStartParser

class TestAgentStartParser(unittest.TestCase):
    def setUp(self):
        self.parser = AgentStartParser()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        os.rmdir(self.test_dir)
    
    def test_agent_creation_parsing(self):
        """Test parsing agent creation commands"""
        code = "agent myAgent = create"
        result = self.parser.parse(code)
        
        self.assertIn("from agent_core import Agent", result)
        self.assertIn('myAgent = Agent("myAgent")', result)
        self.assertIn('myAgent.start()', result)
    
    def test_tell_command_parsing(self):
        """Test parsing tell commands"""
        code = 'tell myAgent "Do this task"'
        result = self.parser.parse(code)
        
        self.assertIn('myAgent.tell("Do this task")', result)
        
        # Test with JSON object
        code = 'tell myAgent {"action": "read", "path": "file.txt"}'
        result = self.parser.parse(code)
        
        self.assertIn('myAgent.tell({"action": "read", "path": "file.txt"})', result)
    
    def test_ask_command_parsing(self):
        """Test parsing ask commands"""
        code = 'result = ask myAgent'
        result = self.parser.parse(code)
        
        self.assertIn('result = myAgent.ask()', result)
    
    def test_wait_command_parsing(self):
        """Test parsing wait commands"""
        code = 'wait myAgent'
        result = self.parser.parse(code)
        
        self.assertIn('myAgent.wait()', result)
    
    def test_free_command_parsing(self):
        """Test parsing free commands"""
        code = 'free myAgent'
        result = self.parser.parse(code)
        
        self.assertIn('myAgent.free()', result)
    
    def test_complex_code_parsing(self):
        """Test parsing a more complex code snippet"""
        code = """
        // Create agents
        agent worker1 = create
        agent worker2 = create
        
        // Send tasks
        tell worker1 "Task 1"
        tell worker2 "Task 2"
        
        // Wait for completion
        wait worker1
        wait worker2
        
        // Get results
        result1 = ask worker1
        result2 = ask worker2
        
        // Clean up
        free worker1
        free worker2
        """
        
        result = self.parser.parse(code)
        
        self.assertIn("from agent_core import Agent", result)
        self.assertIn('worker1 = Agent("worker1")', result)
        self.assertIn('worker2 = Agent("worker2")', result)
        self.assertIn('worker1.tell("Task 1")', result)
        self.assertIn('worker2.tell("Task 2")', result)
        self.assertIn('worker1.wait()', result)
        self.assertIn('worker2.wait()', result)
        self.assertIn('result1 = worker1.ask()', result)
        self.assertIn('result2 = worker2.ask()', result)
        self.assertIn('worker1.free()', result)
        self.assertIn('worker2.free()', result)
    
    def test_compile_method(self):
        """Test compiling an AgentStart file to Python"""
        # Create a temporary file
        input_file = os.path.join(self.test_dir, "test.as")
        output_file = os.path.join(self.test_dir, "test.py")
        
        with open(input_file, "w") as f:
            f.write("agent testAgent = create\ntell testAgent 'Hello'\nfree testAgent")
        
        self.parser.compile(input_file, output_file)
        
        # Check if the output file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Read and check the content
        with open(output_file, "r") as f:
            content = f.read()
            
        self.assertIn("from agent_core import Agent", content)
        self.assertIn('testAgent = Agent("testAgent")', content)
        
        # Clean up test files
        os.remove(input_file)
        os.remove(output_file)

if __name__ == '__main__':
    unittest.main() 