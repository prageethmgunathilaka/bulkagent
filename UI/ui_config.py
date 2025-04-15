import sys
import os

# Add the parent directory to the path so we can import the configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_CONFIG

# Get UI-specific settings with defaults
UI_CONFIG = {
    'port': DEFAULT_CONFIG.get('ui_port', 8001),
    'host': DEFAULT_CONFIG.get('ui_host', '0.0.0.0'),
    'debug': DEFAULT_CONFIG.get('ui_debug', True),
}

# You can override settings here if needed for the UI specifically
# UI_CONFIG['port'] = 8080  # Override the port 