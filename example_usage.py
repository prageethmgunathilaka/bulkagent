from agent_manager import AgentManager
from config import ENABLE_AUTO_CLEANUP, DEFAULT_CONFIG
import time
import logging

def main():
    # Create the agent manager
    agent_manager = AgentManager(config=DEFAULT_CONFIG)
    
    try:
        # Example 1: Create a data processing agent
        data_processing_code = """
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(input_file=None, output_file=None):
    """Process data from input file and write to output file."""
    logger.info(f"Processing data from {input_file} to {output_file}")
    
    # Simple example: Create a dataframe and perform operations
    data = pd.DataFrame({
        'A': np.random.rand(10),
        'B': np.random.rand(10)
    })
    
    # Process the data
    data['C'] = data['A'] + data['B']
    data['D'] = data['A'] * data['B']
    
    logger.info("Data processing completed")
    logger.info(f"Sample of processed data:\\n{data.head()}")
    
    return "Data processing completed successfully"

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    main(*args)
"""
        
        # Create the agent
        data_agent_id = agent_manager.create_agent(data_processing_code, "data_processor")
        
        # Run the agent
        result = agent_manager.run_agent(data_agent_id, "input.csv", "output.csv")
        print(f"Data agent result: {result}")
        
        # Example 2: Generate and run a file organization agent
        task_description = "Organize files in a directory by file type"
        dependencies = ["os", "shutil", "datetime"]
        
        # Generate the agent code
        organizer_code = agent_manager.generate_agent_code(task_description, dependencies)
        
        # Enhance the generated code for the specific task
        organizer_code += """
def main(directory=None):
    if not directory:
        directory = "."
    
    logger.info(f"Organizing files in {directory}")
    
    # Implementation for the organizer
    import os
    import shutil
    from collections import defaultdict
    
    # Count files by extension
    extensions = defaultdict(int)
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            ext = os.path.splitext(filename)[1].lower() or "no_extension"
            extensions[ext] += 1
    
    # Print summary
    for ext, count in extensions.items():
        logger.info(f"Found {count} files with extension {ext}")
    
    return extensions

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    main(*args)
"""
        
        # Create the file organizer agent
        organizer_id = agent_manager.create_agent(organizer_code, "file_organizer")
        
        # Run the file organizer agent
        result = agent_manager.run_agent(organizer_id, ".")
        print(f"File organizer found these extensions: {result}")
        
        # Keep the program running to let agents stay alive
        print("\nAgents are now running. They will be cleaned up after being inactive for the configured timeout period.")
        print(f"Inactive timeout is set to {DEFAULT_CONFIG['inactive_timeout']} seconds.")
        print("Press Ctrl+C to exit the program and clean up all agents immediately.")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
                # You could periodically list active agents here
                # print(f"Active agents: {list(agent_manager.active_agents.keys())}")
        except KeyboardInterrupt:
            print("\nExiting program and cleaning up agents...")
    finally:
        # This will always execute, even if an exception occurs
        if ENABLE_AUTO_CLEANUP:
            agent_manager.cleanup_all_agents()

if __name__ == "__main__":
    main() 