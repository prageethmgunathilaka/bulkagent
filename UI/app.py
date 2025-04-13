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

app = Flask(__name__)
# Create a single instance of AgentManager to be used by the application
agent_manager = AgentManager(config=DEFAULT_CONFIG)

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

# Add a new endpoint to trigger cleanup check manually (for debugging)
@app.route('/api/check-cleanup', methods=['POST'])
def check_cleanup():
    """Manually trigger a cleanup check."""
    agent_manager._cleanup_inactive_agents()
    return jsonify({
        'status': 'success',
        'message': 'Cleanup check triggered',
        'remaining_agents': list(agent_manager.active_agents.keys())
    })

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

@app.route('/api/run-agent/<agent_id>', methods=['POST'])
def run_agent(agent_id):
    """Run the specified agent."""
    data = request.json
    args = data.get('args', [])
    kwargs = data.get('kwargs', {})
    
    try:
        if data.get('subprocess', False):
            result = agent_manager.run_agent_subprocess(agent_id, *args)
            output = {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        else:
            result = agent_manager.run_agent(agent_id, *args, **kwargs)
            output = result
            
        return jsonify({
            'status': 'success',
            'result': output,
            'message': f'Agent {agent_id} executed successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get a list of all active agents."""
    agents = agent_manager.get_active_agents()
    return jsonify({
        'status': 'success',
        'agents': agents
    })

@app.route('/api/cleanup-agent/<agent_id>', methods=['POST'])
def cleanup_agent(agent_id):
    """Clean up a specific agent."""
    data = request.json
    delay = data.get('delay', 0)
    
    success = agent_manager.cleanup_agent(agent_id, delay_seconds=delay)
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': f'Agent {agent_id} cleanup ' + 
                  ('scheduled' if delay > 0 else 'completed') if success 
                  else f'Failed to clean up agent {agent_id}'
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