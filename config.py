# Agent System Configuration

# Directory where temporary agent files will be stored
TEMP_AGENTS_DIR = "temp_agents"

# Default delay in seconds before cleaning up agent files
DEFAULT_CLEANUP_DELAY = 5  # Changed from 30 to 0 for immediate cleanup

# Whether to enable automatic cleanup on program exit
ENABLE_AUTO_CLEANUP = True

# Ensure this setting exists and has some correct name 
DEFAULT_CONFIG = {
    # ... other settings ...
    'inactive_timeout': 5,  # Changed from 30 to 0 for immediate cleanup
    # UI settings
    'ui_port': 8001,         # Default port for the web UI
    'ui_host': '0.0.0.0',    # Default host for the web UI
    'ui_debug': True,        # Enable Flask debug mode
    # ....... other settings ...
} 