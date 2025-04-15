"""
Core functionality for the AgentStart language.
Defines the base Agent class and common interface.
"""

import threading
import queue
import time

class Agent:
    def __init__(self, name=None):
        self.name = name or f"Agent_{id(self)}"
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.state = "ready"  # ready, busy, done, failed
        self._thread = None
        
    def start(self):
        """Start the agent in a new thread"""
        if self._thread and self._thread.is_alive():
            return False
            
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        return True
        
    def _run(self):
        """Main agent loop - processes tasks from queue"""
        while True:
            try:
                task = self.task_queue.get()
                if task == "TERMINATE":
                    self.state = "done"
                    break
                    
                self.state = "busy"
                result = self._process_task(task)
                self.result_queue.put(result)
                self.state = "ready"
                
            except Exception as e:
                self.state = "failed"
                self.result_queue.put({"error": str(e)})
    
    def _process_task(self, task):
        """Override this in subclasses to implement specific behaviors"""
        return {"status": "completed", "result": f"Processed: {task}"}
    
    def tell(self, instruction):
        """Send an instruction to this agent"""
        self.task_queue.put(instruction)
        if not self._thread or not self._thread.is_alive():
            self.start()
    
    def ask(self):
        """Get the latest result from the agent"""
        try:
            return self.result_queue.get(block=False)
        except queue.Empty:
            return {"status": "no_result_available"}
    
    def wait(self, timeout=None):
        """Wait for agent to finish current task"""
        try:
            return self.result_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return {"status": "timeout"}
    
    def free(self):
        """Terminate the agent"""
        if self._thread and self._thread.is_alive():
            self.task_queue.put("TERMINATE")
            self._thread.join(timeout=1.0)
            return True
        return False 