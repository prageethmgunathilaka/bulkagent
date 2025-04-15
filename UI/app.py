from flask import Flask, render_template, request, jsonify
import sys
import os
import time
import importlib
import config as config_module
import atexit

# Add the parent directory to the path so we can import the agent_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_manager import AgentManager
from config import DEFAULT_CONFIG
from active_agents import init_blueprint

app = Flask(__name__)
# Create a single instance of AgentManager to be used by the application
agent_manager = AgentManager(config=DEFAULT_CONFIG)

# Register the active agents blueprint
active_agents_blueprint = init_blueprint(agent_manager)
app.register_blueprint(active_agents_blueprint)

# Log active agents on startup
print(f"Initial active agents: {list(agent_manager.active_agents.keys())}")

# Make sure the cleanup timer is running
if not hasattr(agent_manager, 'cleanup_timer') or agent_manager.cleanup_timer is None:
    agent_manager._start_cleanup_timer()
    print("Started agent cleanup timer")

# Register a function to be called when the application exits
@atexit.register
def cleanup_on_exit():
    print("Application exiting, cleaning up agents...")
    if hasattr(agent_manager, 'cleanup_timer') and agent_manager.cleanup_timer:
        agent_manager.cleanup_timer.cancel()
    agent_manager.cleanup_all_agents()

@app.route('/')
def index():
    """Render the main UI page."""
    return render_template('index.html')

@app.route('/api/create-agent', methods=['POST'])
def create_agent():
    """Create a new agent with provided instructions."""
    data = request.json
    instructions = data.get('instructions', '')
    agent_name = data.get('name', None)
    
    # Generate agent code based on instructions
    if "code:" in instructions:
        # User provided custom code
        agent_code = instructions.split("code:", 1)[1].strip()
    else:
        # Generate code from instructions
        dependencies = data.get('dependencies', '').split(',') if data.get('dependencies') else []
        dependencies = [d.strip() for d in dependencies if d.strip()]
        agent_code = agent_manager.generate_agent_code(instructions, dependencies)
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code, agent_name)
    
    # Make sure the last_active timestamp is set to now
    if agent_id in agent_manager.active_agents:
        agent_manager.active_agents[agent_id]['last_active'] = time.time()
    
    return jsonify({
        'status': 'success',
        'agent_id': agent_id,
        'message': f'Agent {agent_id} created successfully'
    })

if __name__ == '__main__':
    # Use the port from the config, explicitly reload the config to ensure latest value
    importlib.reload(config_module)  # Force reload the config module
    
    # Get the latest config values
    port = config_module.DEFAULT_CONFIG.get('ui_port', 5000)
    host = config_module.DEFAULT_CONFIG.get('ui_host', '0.0.0.0')
    debug = config_module.DEFAULT_CONFIG.get('ui_debug', True)
    
    print(f"Starting Agent Manager UI on http://{host}:{port}")
    
    # Try to start the server, handle common port-in-use errors
    try:
        app.run(debug=debug, host=host, port=port)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\nERROR: Port {port} is already in use.")
            print("Try using a different port in config.py or stopping the process using this port.")
            print("Would you like to try a different port automatically? (y/n)")
            choice = input("> ")
            if choice.lower() == 'y':
                # Try ports 8001, 8002, etc.
                for alt_port in range(port + 1, port + 10):
                    print(f"Trying port {alt_port}...")
                    try:
                        app.run(debug=debug, host=host, port=alt_port)
                        break
                    except OSError:
                        print(f"Port {alt_port} also in use, trying next...")
            else:
                print("Exiting. Please update the 'ui_port' setting in config.py")
        else:
            # Re-raise other exceptions
            raise 