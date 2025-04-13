# Agent System Configuration

# Directory where temporary agent files will be stored
TEMP_AGENTS_DIR = "temp_agents"

# Default delay in seconds before cleaning up agent files
DEFAULT_CLEANUP_DELAY = 30

# Whether to enable automatic cleanup on program exit
ENABLE_AUTO_CLEANUP = True

# Ensure this setting exists and has the correct name
DEFAULT_CONFIG = {
    # ... other settings ...
    'inactive_timeout': 30,  # Timeout in seconds
    # UI settings
    'ui_port': 8000,         # Default port for the web UI
    'ui_host': '0.0.0.0',    # Default host for the web UI
    'ui_debug': True,        # Enable Flask debug mode
    # ... other settings ...
} 