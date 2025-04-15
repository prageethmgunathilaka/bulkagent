#!/usr/bin/env python3
"""
UI Launcher Script - Start the Agent Manager web interface
"""
import sys
import os
import importlib
from flask import Flask

# Add the parent directory to path so we can import the config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Get the absolute path to the temp_agents directory
from config import TEMP_AGENTS_DIR

# Set Flask environment variable to ignore the temp_agents directory
os.environ["WERKZEUG_WATCH_IGNORE"] = f"{TEMP_AGENTS_DIR}/*"

# Get the UI port from config or environment variable (env var takes precedence)
port = int(os.environ.get('AGENT_UI_PORT', config.DEFAULT_CONFIG.get('ui_port', 8001)))
host = os.environ.get('AGENT_UI_HOST', config.DEFAULT_CONFIG.get('ui_host', '0.0.0.0'))
debug = os.environ.get('AGENT_UI_DEBUG', str(config.DEFAULT_CONFIG.get('ui_debug', True))).lower() == 'true'

print(f"\n===== Agent Manager UI =====")
print(f"Configuration:")
print(f"  - Port: {port}")
print(f"  - Host: {host}")
print(f"  - Debug: {debug}")
print(f"============================\n")

# Import and run the Flask app
from app import app

try:
    print(f"Starting Agent Manager UI on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
except OSError as e:
    if 'Address already in use' in str(e):
        print(f"\nERROR: Port {port} is already in use.")
        print("Options:")
        print("1. Update the 'ui_port' setting in config.py")
        print("2. Set the AGENT_UI_PORT environment variable")
        print("3. Stop the process using this port")
        
        print("\nWould you like to try a different port automatically? (y/n)")
        choice = input("> ")
        if choice.lower() == 'y':
            # Try ports incrementally
            for alt_port in range(port + 1, port + 100):
                print(f"Trying port {alt_port}...")
                try:
                    app.run(host=host, port=alt_port, debug=debug, use_reloader=False)
                    break
                except OSError:
                    print(f"Port {alt_port} also in use, trying next...")
        else:
            print("Exiting.")
    else:
        # Re-raise other exceptions
        raise 