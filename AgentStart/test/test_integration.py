"""
Integration tests for the AgentStart language
"""

import unittest
import os
import tempfile
import time
from AgentStart.agent_core import Agent
from AgentStart.agent_types import FileAgent, DatabaseAgent
from AgentStart.compiler import compile_file, run_file

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_as_file = os.path.join(self.test_dir, "integration_test.as")
        self.test_output_file = os.path.join(self.test_dir, "test_output.txt")
    
    def tearDown(self):
        # Clean up test files
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)
    
    def test_file_operations(self):
        """Test a complete file operation workflow"""
        # Create an AgentStart program
        with open(self.test_as_file, "w") as f:
            f.write(f"""
            // Import agent types
            import "agent_types"
            
            // Create a FileAgent
            agent fileHandler = create from "agent_types.FileAgent"
            
            // Write to a file
            tell fileHandler {{
                "action": "write",
                "path": "{self.test_output_file}",
                "content": "Integration test content"
            }}
            
            // Wait for completion
            wait fileHandler
            
            // Read the file back
            tell fileHandler {{
                "action": "read",
                "path": "{self.test_output_file}"
            }}
            
            // Get results
            var result = ask fileHandler
            
            // Clean up
            free fileHandler
            
            // Check result
            if (result.status == "success") {{
                print("Test passed: " + result.content)
            }} else {{
                print("Test failed")
            }}
            """)
        
        # Create a direct test with FileAgent
        file_agent = FileAgent("DirectFileAgent")
        
        # Write to file
        file_agent.tell({
            "action": "write",
            "path": self.test_output_file,
            "content": "Direct test content"
        })
        
        result = file_agent.wait()
        self.assertEqual(result["status"], "success")
        
        # Read from file
        file_agent.tell({
            "action": "read",
            "path": self.test_output_file
        })
        
        result = file_agent.wait()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "Direct test content")
    
    def test_database_operations(self):
        """Test a complete database operation workflow"""
        # Create a database agent
        db_agent = DatabaseAgent("TestDBAgent", ":memory:")
        
        # Create table
        db_agent.tell("CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)")
        result = db_agent.wait()
        self.assertEqual(result["status"], "success")
        
        # Insert data
        db_agent.tell("INSERT INTO test_table (value) VALUES ('test1'), ('test2'), ('test3')")
        result = db_agent.wait()
        self.assertEqual(result["status"], "success")
        
        # Query data
        db_agent.tell("SELECT * FROM test_table ORDER BY id")
        result = db_agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["rows"]), 3)
        self.assertEqual(result["rows"][0][1], "test1")
        self.assertEqual(result["rows"][1][1], "test2")
        self.assertEqual(result["rows"][2][1], "test3")
        
        # Test structured query
        db_agent.tell({
            "action": "query",
            "sql": "SELECT * FROM test_table WHERE id = ?",
            "params": [2]
        })
        
        result = db_agent.wait()
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0][1], "test2")
    
    def test_multi_agent_interaction(self):
        """Test interaction between multiple agents"""
        # Create a temporary database file
        db_file = os.path.join(self.test_dir, "test.db")
        
        # Create agents
        file_agent = FileAgent("FileHandler")
        db_agent = DatabaseAgent("DBHandler", db_file)
        
        # Initialize database
        db_agent.tell("CREATE TABLE log (id INTEGER PRIMARY KEY, message TEXT, timestamp TEXT)")
        db_agent.wait()
        
        # Write to a file using file agent
        file_agent.tell({
            "action": "write",
            "path": self.test_output_file,
            "content": "Test message from file agent"
        })
        
        file_agent.wait()
        
        # Read file content
        file_agent.tell({
            "action": "read",
            "path": self.test_output_file
        })
        
        result = file_agent.wait()
        self.assertEqual(result["status"], "success")
        
        # Log the content to database using database agent
        message = result["content"]
        db_agent.tell(f"INSERT INTO log (message, timestamp) VALUES ('{message}', datetime('now'))")
        db_agent.wait()
        
        # Query the logged data
        db_agent.tell("SELECT message FROM log")
        result = db_agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0][0], "Test message from file agent")
        
        # Clean up
        file_agent.free()
        db_agent.free()

if __name__ == '__main__':
    unittest.main() 