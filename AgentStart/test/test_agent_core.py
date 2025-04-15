"""
Tests for the core Agent functionality
"""

import unittest
import time
import queue
from AgentStart.agent_core import Agent

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Agent("TestAgent")
    
    def test_agent_initialization(self):
        """Test agent initialization with name"""
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.state, "ready")
        self.assertIsNone(self.agent._thread)
        
        # Test auto-name generation
        unnamed_agent = Agent()
        self.assertTrue(unnamed_agent.name.startswith("Agent_"))
    
    def test_start_method(self):
        """Test agent starting"""
        result = self.agent.start()
        self.assertTrue(result)
        self.assertIsNotNone(self.agent._thread)
        self.assertTrue(self.agent._thread.is_alive())
        
        # Test starting an already running agent
        result = self.agent.start()
        self.assertFalse(result)
    
    def test_tell_method(self):
        """Test sending instructions to agent"""
        self.agent.tell("Test instruction")
        time.sleep(0.1)  # Allow time for processing
        self.assertEqual(self.agent.state, "ready")
        
        # Verify task was processed
        result = self.agent.ask()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["result"], "Processed: Test instruction")
    
    def test_ask_method(self):
        """Test retrieving results from agent"""
        self.agent.tell("Task 1")
        time.sleep(0.1)  # Allow time for processing
        
        # Get result
        result = self.agent.ask()
        self.assertEqual(result["status"], "completed")
        
        # Ask when no result is available
        result = self.agent.ask()
        self.assertEqual(result["status"], "no_result_available")
    
    def test_wait_method(self):
        """Test waiting for agent to complete task"""
        # Test timeout
        result = self.agent.wait(timeout=0.1)
        self.assertEqual(result["status"], "timeout")
        
        # Test successful wait
        self.agent.tell("Task to wait for")
        result = self.agent.wait()
        self.assertEqual(result["status"], "completed")
    
    def test_free_method(self):
        """Test terminating an agent"""
        self.agent.start()
        result = self.agent.free()
        self.assertTrue(result)
        time.sleep(0.1)  # Allow time for termination
        self.assertFalse(self.agent._thread.is_alive())
        
        # Test freeing an already terminated agent
        result = self.agent.free()
        self.assertFalse(result)
    
    def test_error_handling(self):
        """Test agent error handling"""
        # Create a subclass with a method that raises an exception
        class ErrorAgent(Agent):
            def _process_task(self, task):
                raise ValueError("Test error")
        
        error_agent = ErrorAgent()
        error_agent.tell("Trigger error")
        time.sleep(0.1)  # Allow time for processing
        
        result = error_agent.ask()
        self.assertEqual(error_agent.state, "failed")
        self.assertTrue("error" in result)

if __name__ == '__main__':
    unittest.main() 