"""
Tests for specialized agent types
"""

import unittest
import os
import sqlite3
import json
import tempfile
from AgentStart.agent_types import FileAgent, DatabaseAgent

class TestFileAgent(unittest.TestCase):
    def setUp(self):
        self.agent = FileAgent("TestFileAgent")
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
    
    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.test_dir)
    
    def test_write_operation(self):
        """Test writing to a file"""
        task = {
            "action": "write",
            "path": self.test_file,
            "content": "Test content"
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content")
    
    def test_read_operation(self):
        """Test reading from a file"""
        # First create a file
        with open(self.test_file, "w") as f:
            f.write("Test content to read")
        
        task = {
            "action": "read",
            "path": self.test_file
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["content"], "Test content to read")
    
    def test_list_operation(self):
        """Test listing files in a directory"""
        # Create a test file
        with open(self.test_file, "w") as f:
            f.write("Test content")
        
        task = {
            "action": "list",
            "path": self.test_dir
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertIn("test_file.txt", result["files"])
    
    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test reading non-existent file
        task = {
            "action": "read",
            "path": os.path.join(self.test_dir, "nonexistent.txt")
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "error")
        self.assertTrue("message" in result)
        
        # Test unknown action
        task = {
            "action": "unknown",
            "path": self.test_file
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Unknown action")
    
    def test_json_string_input(self):
        """Test sending JSON as a string"""
        json_task = json.dumps({
            "action": "write",
            "path": self.test_file,
            "content": "JSON string content"
        })
        
        self.agent.tell(json_task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "JSON string content")
    
    def test_invalid_json_string(self):
        """Test invalid JSON string input"""
        self.agent.tell("Not a valid JSON")
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Invalid task format")


class TestDatabaseAgent(unittest.TestCase):
    def setUp(self):
        # Use in-memory database for testing
        self.agent = DatabaseAgent("TestDatabaseAgent", ":memory:")
    
    def test_create_table(self):
        """Test creating a table in the database"""
        self.agent.tell("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        
        # Verify table was created
        self.agent.tell("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0][0], "test")
    
    def test_insert_and_select(self):
        """Test inserting and selecting data"""
        # Create table
        self.agent.tell("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        self.agent.wait()
        
        # Insert data
        self.agent.tell("INSERT INTO users (name) VALUES ('Alice'), ('Bob')")
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_affected"], 2)
        
        # Select data
        self.agent.tell("SELECT * FROM users ORDER BY name")
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][0][1], "Alice")
        self.assertEqual(result["rows"][1][1], "Bob")
    
    def test_structured_query(self):
        """Test using structured query format"""
        # Create table
        self.agent.tell("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
        self.agent.wait()
        
        # Insert with structured command
        task = {
            "action": "query",
            "sql": "INSERT INTO products (name, price) VALUES (?, ?)",
            "params": ["Product A", 99.99],
            "fetch": False
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        
        # Select with structured command
        task = {
            "action": "query",
            "sql": "SELECT * FROM products WHERE price > ?",
            "params": [50.0]
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["rows"]), 1)
        self.assertEqual(result["rows"][0][1], "Product A")
    
    def test_error_handling(self):
        """Test SQL error handling"""
        # Invalid SQL syntax
        self.agent.tell("SELECT * FROM nonexistent_table")
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "error")
        self.assertTrue("message" in result)
        
        # Invalid structured command
        task = {
            "action": "unknown",
            "sql": "SELECT 1"
        }
        
        self.agent.tell(task)
        result = self.agent.wait()
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Unknown action")

if __name__ == '__main__':
    unittest.main() 