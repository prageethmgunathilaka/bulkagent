from agent_manager import AgentManager
from config import DEFAULT_CONFIG
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Create the agent manager with our config
    agent_manager = AgentManager(config=DEFAULT_CONFIG)
    
    try:
        # Create a greeting agent
        greeting_code = """
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(*args):
    greeting = "Hello! I am your greeting agent. Nice to meet you!"
    print(greeting)
    return greeting

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    main(*args)
"""
        
        # Create the agent
        greeting_agent_id = agent_manager.create_agent(greeting_code, "greeting_agent")
        
        # Run the agent as subprocess
        result = agent_manager.run_agent_subprocess(greeting_agent_id, "Hello", "World")
        print(f"Subprocess stdout: {result.stdout}")
        
        # Don't call cleanup_agent here - we want the inactive timeout to handle it
        print(f"\nAgent cleanup will happen after {DEFAULT_CONFIG['inactive_timeout']} seconds of inactivity")
        print("The program will continue running...\n")
        
        # Demonstrate that program continues while agent exists
        print("Doing other work...")
        for i in range(1, 6):
            print(f"Working... {i}/5")
            time.sleep(1)
        
        print("\nYou can check the 'temp_agents' directory to see if the agent file still exists.")
        print(f"It should remain for another {DEFAULT_CONFIG['inactive_timeout']-5} seconds approximately.")
        
        # Let's monitor the active agents
        print("\nMonitoring active agents (press Ctrl+C to exit):")
        try:
            while True:
                agents = agent_manager.get_active_agents()
                if agents:
                    for agent_id, status in agents.items():
                        print(f"Agent {agent_id}: idle for {status['idle_time']:.1f}s, cleanup in {status['time_left']:.1f}s")
                else:
                    print("No active agents remaining.")
                    break
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nMonitoring interrupted by user.")
    
    finally:
        # We're not forcing cleanup here - let's comment this out
        # Don't do this: agent_manager.cleanup_all_agents()
        pass

if __name__ == "__main__":
    main() 