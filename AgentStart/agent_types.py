"""
Predefined agent types with specific capabilities.
All agents maintain the common interface.
"""

from agent_core import Agent
import os
import sqlite3
import json

class FileAgent(Agent):
    """Agent specialized in file operations"""
    
    def _process_task(self, task):
        if isinstance(task, str):
            # Try to parse as JSON
            try:
                task = json.loads(task)
            except:
                return {"status": "error", "message": "Invalid task format"}
        
        action = task.get("action")
        
        if action == "read":
            try:
                with open(task.get("path"), 'r') as f:
                    content = f.read()
                return {"status": "success", "content": content}
            except Exception as e:
                return {"status": "error", "message": str(e)}
                
        elif action == "write":
            try:
                with open(task.get("path"), 'w') as f:
                    f.write(task.get("content", ""))
                return {"status": "success"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
                
        elif action == "list":
            try:
                files = os.listdir(task.get("path", "."))
                return {"status": "success", "files": files}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        return {"status": "error", "message": "Unknown action"}

class DatabaseAgent(Agent):
    """Agent specialized in SQLite database operations"""
    
    def __init__(self, name=None, db_path=":memory:"):
        super().__init__(name)
        self.db_path = db_path
        self.conn = None
        
    def _connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn
    
    def _process_task(self, task):
        if isinstance(task, str):
            # Assume direct SQL if string
            try:
                conn = self._connect()
                cursor = conn.cursor()
                cursor.execute(task)
                
                if task.strip().upper().startswith(("SELECT", "PRAGMA")):
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    conn.commit()
                    return {
                        "status": "success", 
                        "columns": columns,
                        "rows": results
                    }
                else:
                    conn.commit()
                    return {"status": "success", "rows_affected": cursor.rowcount}
                    
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        # Structured command
        action = task.get("action", "")
        
        if action == "query":
            try:
                conn = self._connect()
                cursor = conn.cursor()
                cursor.execute(task.get("sql", ""), task.get("params", []))
                
                if task.get("fetch", True):
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    conn.commit()
                    return {
                        "status": "success", 
                        "columns": columns,
                        "rows": results
                    }
                else:
                    conn.commit()
                    return {"status": "success", "rows_affected": cursor.rowcount}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        return {"status": "error", "message": "Unknown action"} 