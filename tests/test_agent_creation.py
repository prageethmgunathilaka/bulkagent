"""
Test cases for agent creation functionality in the Agent Manager.
"""
import os
import pytest
import sys
import uuid
import time

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_manager import AgentManager
from config import DEFAULT_CONFIG, TEMP_AGENTS_DIR

# Test configuration
TEST_CONFIG = DEFAULT_CONFIG.copy()
TEST_CONFIG['inactive_timeout'] = 60  # Extend timeout for testing


@pytest.fixture
def agent_manager():
    """Create an agent manager instance for testing."""
    # Use a test-specific directory to avoid conflicts
    test_dir = os.path.join(TEMP_AGENTS_DIR, f"test_{uuid.uuid4().hex[:8]}")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create manager with test config
    manager = AgentManager(agents_dir=test_dir, config=TEST_CONFIG)
    
    # Yield the manager for test use
    yield manager
    
    # Cleanup after tests
    manager.cleanup_all_agents()
    try:
        os.rmdir(test_dir)  # Remove test directory if empty
    except:
        pass  # Ignore errors during cleanup


def test_basic_agent_creation(agent_manager):
    """Test basic agent creation functionality."""
    # Simple agent code
    agent_code = """
def main(*args, **kwargs):
    return "Hello from test agent"
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    
    # Verify agent creation
    assert agent_id in agent_manager.active_agents
    
    # Verify file exists
    file_path = agent_manager.active_agents[agent_id]["file_path"]
    assert os.path.exists(file_path)
    
    # Verify agent is executable
    result = agent_manager.run_agent(agent_id)
    assert result == "Hello from test agent"


def test_custom_agent_name(agent_manager):
    """Test agent creation with a custom name."""
    # Simple agent code
    agent_code = """
def main(*args, **kwargs):
    return "Hello from named agent"
"""
    
    # Create agent with custom name
    custom_name = f"custom_agent_{uuid.uuid4().hex[:8]}"
    agent_id = agent_manager.create_agent(agent_code, agent_name=custom_name)
    
    # Verify agent ID matches custom name
    assert agent_id == custom_name
    
    # Verify file exists with custom name
    file_path = agent_manager.active_agents[agent_id]["file_path"]
    assert os.path.basename(file_path) == f"{custom_name}.py"
    
    # Verify agent is executable
    result = agent_manager.run_agent(agent_id)
    assert result == "Hello from named agent"


def test_code_generation(agent_manager):
    """Test agent code generation functionality."""
    # Generate agent code
    task = "Calculate the factorial of a number"
    dependencies = ["math"]
    
    agent_code = agent_manager.generate_agent_code(task, dependencies)
    
    # Verify code contains expected elements
    assert "import math" in agent_code
    assert "def main" in agent_code
    assert task in agent_code
    
    # Create agent with generated code
    agent_id = agent_manager.create_agent(agent_code)
    
    # Verify agent was created
    assert agent_id in agent_manager.active_agents


def test_agent_subprocess_execution(agent_manager):
    """Test agent execution as subprocess."""
    # Agent code that prints output
    agent_code = """
import sys

def main(*args):
    print(f"Arguments received: {args}")
    return "Subprocess execution completed"

if __name__ == "__main__":
    # Handle command-line arguments
    args = sys.argv[1:]
    main(*args)
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    
    # Run as subprocess
    result = agent_manager.run_agent_subprocess(agent_id, "arg1", "arg2")
    
    # Verify subprocess execution
    assert result.returncode == 0
    assert "Arguments received" in result.stdout


def test_agent_last_active_tracking(agent_manager):
    """Test the last active tracking for agents."""
    # Create a simple agent
    agent_code = """
def main(*args, **kwargs):
    return "Active agent test"
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    initial_timestamp = agent_manager.active_agents[agent_id]["last_active"]
    
    # Wait a moment
    time.sleep(1)
    
    # Run the agent
    agent_manager.run_agent(agent_id)
    
    # Verify last_active was updated
    new_timestamp = agent_manager.active_agents[agent_id]["last_active"]
    assert new_timestamp > initial_timestamp


def test_agent_cleanup(agent_manager):
    """Test agent cleanup functionality."""
    # Create a simple agent
    agent_code = """
def main(*args, **kwargs):
    return "Cleanup test agent"
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    file_path = agent_manager.active_agents[agent_id]["file_path"]
    
    # Verify agent exists
    assert os.path.exists(file_path)
    
    # Clean up the agent
    result = agent_manager.cleanup_agent(agent_id)
    assert result is True
    
    # Verify agent is removed
    assert agent_id not in agent_manager.active_agents
    assert not os.path.exists(file_path)


def test_multiple_agents(agent_manager):
    """Test creating and managing multiple agents."""
    # Create multiple agents
    agent_ids = []
    for i in range(5):
        agent_code = f"""
def main(*args, **kwargs):
    return "Agent {i} response"
"""
        agent_id = agent_manager.create_agent(agent_code)
        agent_ids.append(agent_id)
    
    # Verify all agents were created
    assert len(agent_manager.active_agents) == 5
    
    # Run each agent
    for i, agent_id in enumerate(agent_ids):
        result = agent_manager.run_agent(agent_id)
        assert result == f"Agent {i} response"
    
    # Clean up all agents
    count = agent_manager.cleanup_all_agents()
    assert count == 5
    
    # Verify all agents were removed
    assert len(agent_manager.active_agents) == 0


def test_inactive_agent_cleanup(agent_manager):
    """Test that inactive agents are cleaned up after configured timeout."""
    # Override the inactive timeout to a very short duration for testing
    agent_manager.config['inactive_timeout'] = 2  # 2 seconds
    
    # Create a simple agent
    agent_code = """
def main(*args, **kwargs):
    return "Inactive timeout test agent"
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    file_path = agent_manager.active_agents[agent_id]["file_path"]
    
    # Verify agent exists
    assert os.path.exists(file_path)
    assert agent_id in agent_manager.active_agents
    
    # Wait longer than the inactive timeout
    time.sleep(3)  # 3 seconds > 2 seconds timeout
    
    # Trigger cleanup check
    agent_manager._cleanup_inactive_agents()
    
    # Verify agent was automatically removed
    assert agent_id not in agent_manager.active_agents
    assert not os.path.exists(file_path)


def test_active_agent_not_cleaned_up(agent_manager):
    """Test that active agents are not cleaned up before timeout."""
    # Override the inactive timeout to a short duration
    agent_manager.config['inactive_timeout'] = 5  # 5 seconds
    
    # Create a simple agent
    agent_code = """
def main(*args, **kwargs):
    return "Active agent test"
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    
    # Run the agent to update its last_active timestamp
    agent_manager.run_agent(agent_id)
    
    # Wait a bit, but less than the timeout
    time.sleep(2)  # 2 seconds < 5 seconds timeout
    
    # Trigger cleanup check
    agent_manager._cleanup_inactive_agents()
    
    # Verify agent still exists
    assert agent_id in agent_manager.active_agents
    
    # Wait until after the timeout
    time.sleep(4)  # Total 6 seconds > 5 seconds timeout
    
    # Trigger cleanup check again
    agent_manager._cleanup_inactive_agents()
    
    # Verify agent was removed
    assert agent_id not in agent_manager.active_agents


def test_agent_code_exists_until_timeout(agent_manager):
    """Test that agent code files exist until timeout period and not beyond."""
    # Set a very short timeout for testing
    agent_manager.config['inactive_timeout'] = 3  # 3 seconds
    
    # Create a simple agent
    agent_code = """
def main(*args, **kwargs):
    return "Timeout existence test agent"
"""
    
    # Create the agent
    agent_id = agent_manager.create_agent(agent_code)
    file_path = agent_manager.active_agents[agent_id]["file_path"]
    
    # Verify agent file exists immediately after creation
    assert os.path.exists(file_path)
    
    # Wait for a period shorter than the timeout
    time.sleep(1)  # 1 second < 3 seconds timeout
    
    # Verify file still exists before timeout
    assert os.path.exists(file_path)
    
    # Run cleanup - should not affect the agent yet
    agent_manager._cleanup_inactive_agents()
    assert os.path.exists(file_path)
    assert agent_id in agent_manager.active_agents
    
    # Wait until after the timeout period
    time.sleep(3)  # Total 4 seconds > 3 seconds timeout
    
    # Run cleanup - should now remove the agent
    agent_manager._cleanup_inactive_agents()
    
    # Verify file no longer exists after timeout and cleanup
    assert not os.path.exists(file_path)
    assert agent_id not in agent_manager.active_agents 