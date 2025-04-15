import os
import uuid
import subprocess
import importlib.util
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable
# Import the config
from config import TEMP_AGENTS_DIR

class AgentManager:
    """
    A manager that creates, executes, and cleans up temporary agent code.
    """
    
    def __init__(self, agents_dir: str = TEMP_AGENTS_DIR, config=None):
        """
        Initialize the agent manager.
        
        Args:
            agents_dir: Directory where temporary agent files will be stored
            config: Configuration for the agent manager
        """
        self.agents_dir = agents_dir
        self.active_agents = {}
        
        # Create the agents directory if it doesn't exist
        os.makedirs(self.agents_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AgentManager")
        self.logger.info(f"Agent Manager initialized with agents directory: {self.agents_dir}")
        
        # Ensure config is properly initialized
        self.config = config if config is not None else {}
        # Set a default timeout if not provided
        if 'inactive_timeout' not in self.config:
            self.config['inactive_timeout'] = 300  # Default 5 minutes
        
        self.logger.info(f"Agent Manager configured with inactive_timeout: {self.config['inactive_timeout']} seconds")
        
        # Set up the cleanup timer
        self.cleanup_timer = None
        self._start_cleanup_timer()
    
    def _start_cleanup_timer(self):
        """Start a timer to periodically check for inactive agents."""
        # Check every 2 seconds instead of 10 for inactive agents
        if self.cleanup_timer and self.cleanup_timer.is_alive():
            self.logger.warning("Cleanup timer already running, not starting a new one")
            return
        
        self.logger.debug("Starting cleanup timer to check for inactive agents every 2 seconds")
        self.cleanup_timer = threading.Timer(2, self._cleanup_timer_callback)  # Changed from 10 to 2
        self.cleanup_timer.daemon = True
        self.cleanup_timer.start()
    
    def _cleanup_timer_callback(self):
        """Callback for the cleanup timer."""
        self.logger.debug("Cleanup timer triggered, checking for inactive agents")
        self._cleanup_inactive_agents()
        # Restart the timer
        self._start_cleanup_timer()
    
    def create_agent(self, agent_code: str, agent_name: Optional[str] = None) -> str:
        """
        Create a new agent with the provided code.
        
        Args:
            agent_code: The Python code for the agent
            agent_name: Optional name for the agent (will be generated if not provided)
            
        Returns:
            agent_id: A unique identifier for the created agent
        """
        # Generate a unique ID for this agent
        agent_id = agent_name or f"agent_{uuid.uuid4().hex[:8]}"
        
        # Create the file path
        file_path = os.path.join(self.agents_dir, f"{agent_id}.py")
        self.logger.info(f"Creating agent {agent_id} at {file_path}")
        
        # Write the agent code to the file
        with open(file_path, "w") as f:
            f.write(agent_code)
        
        self.active_agents[agent_id] = {
            "file_path": file_path,
            "status": "created",
            "last_active": time.time()  # Add timestamp
        }
        
        self.logger.info(f"Created agent: {agent_id}")
        return agent_id
    
    def run_agent(self, agent_id: str, *args, **kwargs) -> Any:
        """
        Run the specified agent.
        
        Args:
            agent_id: The ID of the agent to run
            *args, **kwargs: Arguments to pass to the agent
            
        Returns:
            The result from the agent execution
        """
        if agent_id not in self.active_agents:
            self.logger.error(f"Agent {agent_id} not found")
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_info = self.active_agents[agent_id]
        file_path = agent_info["file_path"]
        
        self.logger.info(f"Running agent: {agent_id}")
        
        # Method 1: Import and run the module directly
        try:
            # Import the module dynamically
            self.logger.info(f"Importing agent module: {agent_id}")
            spec = importlib.util.spec_from_file_location(agent_id, file_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Failed to load agent module: {agent_id}")
                raise ImportError(f"Could not load agent module: {agent_id}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Execute the main function if it exists
            if hasattr(module, "main"):
                self.logger.info(f"Executing main function for agent: {agent_id}")
                result = module.main(*args, **kwargs)
                agent_info["status"] = "completed"
                self.logger.info(f"Agent {agent_id} completed successfully")
                # Update last active timestamp
                self.active_agents[agent_id]["last_active"] = time.time()
                
                # Force cleanup check immediately if timeout is 0
                if self.config['inactive_timeout'] == 0:
                    self._cleanup_inactive_agents()
                
                return result
            else:
                agent_info["status"] = "error"
                self.logger.error(f"Agent {agent_id} does not have a main function")
                raise AttributeError(f"Agent {agent_id} does not have a main function")
        
        except Exception as e:
            agent_info["status"] = "error"
            agent_info["error"] = str(e)
            self.logger.error(f"Error running agent {agent_id}: {e}")
            raise
    
    def run_agent_subprocess(self, agent_id: str, *args) -> subprocess.CompletedProcess:
        """
        Run the agent as a separate process.
        
        Args:
            agent_id: The ID of the agent to run
            *args: Command-line arguments to pass to the agent
            
        Returns:
            The completed process object
        """
        if agent_id not in self.active_agents:
            self.logger.error(f"Agent {agent_id} not found for subprocess execution")
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_info = self.active_agents[agent_id]
        file_path = agent_info["file_path"]
        
        self.logger.info(f"Running agent as subprocess: {agent_id}")
        
        # Convert all args to strings
        string_args = [str(arg) for arg in args]
        command = ["python", file_path] + string_args
        self.logger.info(f"Executing command: {' '.join(command)}")
        
        # Run the agent as a separate process
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            agent_info["status"] = "completed"
            self.logger.info(f"Subprocess agent {agent_id} completed successfully")
        else:
            agent_info["status"] = "error"
            agent_info["error"] = result.stderr
            self.logger.error(f"Error running agent {agent_id}: {result.stderr}")
        
        # Update last active timestamp
        self.active_agents[agent_id]["last_active"] = time.time()
        
        return result
    
    def cleanup_agent(self, agent_id: str, delay_seconds: float = 0) -> bool:
        """
        Clean up the agents resources once it has completed its purpose.
        
        Args:
            agent_id: The ID of the agent to clean up
            delay_seconds: Delay in seconds before cleaning up (0 means immediate cleanup)
            
        Returns:
            True if cleanup was successful or scheduled, False otherwise
        """
        if agent_id not in self.active_agents:
            self.logger.warning(f"Agent {agent_id} not found for cleanup")
            return False
        
        if delay_seconds > 0:
            self.logger.info(f"Scheduling cleanup of agent {agent_id} in {delay_seconds} seconds")
            # Schedule the cleanup after the specified delay
            timer = threading.Timer(delay_seconds, self._do_cleanup_agent, args=[agent_id])
            timer.daemon = True  # Make sure the timer doesn't block program exit
            timer.start()
            return True
        else:
            # Do immediate cleanup
            self.logger.info(f"Performing immediate cleanup for agent {agent_id}")
            return self._do_cleanup_agent(agent_id)
    
    def _do_cleanup_agent(self, agent_id: str) -> bool:
        """
        Internal method to actually perform the agent cleanup.
        
        Args:
            agent_id: The ID of the agent to clean up
            
        Returns:
            True if cleanup was successful, False otherwise
        """
        if agent_id not in self.active_agents:
            self.logger.warning(f"Agent {agent_id} not found for cleanup")
            return False
        
        agent_info = self.active_agents[agent_id]
        file_path = agent_info["file_path"]
        
        try:
            # Remove the agents file
            if os.path.exists(file_path):
                self.logger.info(f"Removing agent file: {file_path}")
                os.remove(file_path)
                self.logger.info(f"Removed agent file: {file_path}")
            
            # Remove the agent from active agents
            del self.active_agents[agent_id]
            self.logger.info(f"Cleaned up agent: {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up agent {agent_id}: {e}")
            return False
    
    def cleanup_all_agents(self) -> int:
        """
        Clean up all agents.
        
        Returns:
            The number of agents that were cleaned up
        """
        agent_ids = list(self.active_agents.keys())
        self.logger.info(f"Cleaning up all agents ({len(agent_ids)} total)")
        count = 0
        
        for agent_id in agent_ids:
            if self.cleanup_agent(agent_id):
                count += 1
        
        self.logger.info(f"Cleaned up {count} agents")
        return count
    
    def generate_agent_code(self, task_description: str, dependencies: list = None) -> str:
        """
        Generate code for an agent based on a task description.
        This is a simple example - in a real system, you might use an LLM
        or other code generation techniques.
        
        Args:
            task_description: Description of what the agent should do
            dependencies: List of dependencies required by the agent
            
        Returns:
            The generated agent code as a string
        """
        self.logger.info(f"Generating agent code for task: {task_description}")
        dependencies = dependencies or []
        dependencies_imports = "\n".join([f"import {dep}" for dep in dependencies])
        
        # Create a simple agent template
        agent_code = f"""
# Generated Agent
# Task: {task_description}

{dependencies_imports}
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(*args, **kwargs):
    \"\"\"
    Main function for the agent.
    
    Args:
        *args, **kwargs: Arguments passed to the agent
    
    Returns:
        The result of the agent's execution
    \"\"\"
    logger.info("Agent started with args: {{}}, kwargs: {{}}".format(args, kwargs))
    
    try:
        # Task implementation:
        logger.info("Executing task: {task_description}")
        
        # Special handling for greeting agents
        if "greeting" in "{task_description}".lower():
            greeting = "Hello! I am your greeting agent. Nice to meet you!"
            print(greeting)
            logger.info(f"Greeting message displayed: {{greeting}}")
            return greeting
        
        # Add task-specific code here
        result = "Task completed successfully"
        
        logger.info("Task completed")
        return result
    
    except Exception as e:
        logger.error(f"Error executing task: {{e}}")
        raise

if __name__ == "__main__":
    # Handle command-line arguments
    args = sys.argv[1:]
    main(*args)
"""
        self.logger.info(f"Agent code generated successfully")
        return agent_code
    
    def get_agent_status(self, agent_id: str) -> dict:
        """
        Get the current status of an agent.
        
        Args:
            agent_id: The ID of the agent to check
            
        Returns:
            A dictionary with agent status information or None if agent not found
        """
        if agent_id not in self.active_agents:
            self.logger.warning(f"Agent {agent_id} not found for status check")
            return None
        
        agent_info = self.active_agents[agent_id].copy()
        agent_info['exists'] = os.path.exists(agent_info['file_path'])
        
        self.logger.info(f"Agent {agent_id} status: {agent_info['status']}, file exists: {agent_info['exists']}")
        return agent_info
    
    def ensure_cleanup(self) -> int:
        """
        Ensures that all agent files are cleaned up, including any that might
        have been missed in previous cleanup attempts.
        
        Returns:
            Number of files cleaned up
        """
        self.logger.info("Ensuring all agent files are cleaned up")
        count = 0
        
        # First try the standard cleanup
        count += self.cleanup_all_agents()
        
        # Then check if any files remain in the agent directory
        if os.path.exists(self.agents_dir):
            files = [f for f in os.listdir(self.agents_dir) if f.endswith('.py')]
            if files:
                self.logger.warning(f"Found {len(files)} agent files still remaining after cleanup")
                for file in files:
                    file_path = os.path.join(self.agents_dir, file)
                    try:
                        os.remove(file_path)
                        count += 1
                        self.logger.info(f"Forcibly removed agent file: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Error removing agent file {file_path}: {e}")
        
        self.logger.info(f"Cleanup complete, removed {count} files in total")
        return count
    
    def _cleanup_inactive_agents(self):
        """Clean up inactive agents based on the configured timeout."""
        current_time = time.time()
        agents_to_remove = []
        
        self.logger.info(f"Checking for inactive agents - timeout setting: {self.config['inactive_timeout']} seconds")
        
        for agent_id, agent_data in self.active_agents.items():
            # Using the timeout from self.config that was properly initialized in __init__
            timeout = self.config['inactive_timeout']
            idle_time = current_time - agent_data['last_active']
            
            self.logger.info(f"Agent {agent_id}: status={agent_data['status']}, idle_time={idle_time:.1f}s, timeout={timeout}s")
            
            # Special handling for 0-second timeout - clean up any inactive agent immediately
            if timeout == 0 and agent_data['status'] in ['completed', 'error']:
                self.logger.info(f"Agent {agent_id} is inactive with 0-second timeout - cleaning up immediately")
                agents_to_remove.append(agent_id)
            # Regular timeout-based cleanup
            elif idle_time > timeout:
                self.logger.info(f"Agent {agent_id} inactive for {idle_time:.1f}s (timeout: {timeout}s) - cleaning up")
                agents_to_remove.append(agent_id)
        
        for agent_id in agents_to_remove:
            self.logger.info(f"Removing agent {agent_id}")
            self._remove_agent(agent_id)
    
    def _remove_agent(self, agent_id: str) -> bool:
        """
        Internal method to remove an agent.
        
        Args:
            agent_id: The ID of the agent to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        return self._do_cleanup_agent(agent_id)
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the cleanup timer before exiting
        if self.cleanup_timer:
            self.cleanup_timer.cancel()
        self.cleanup_all_agents()
    
    def get_active_agents(self) -> dict:
        """
        Get a dictionary of all active agents with their statuses.
        
        Returns:
            A dictionary of agent_id -> status information
        """
        result = {}
        current_time = time.time()
        
        for agent_id, agent_data in self.active_agents.items():
            idle_time = current_time - agent_data['last_active']
            timeout = self.config['inactive_timeout']  # Use the same timeout value consistently
            result[agent_id] = {
                'status': agent_data['status'],
                'idle_time': idle_time,
                'time_left': max(0, timeout - idle_time)
            }
        
        return result 