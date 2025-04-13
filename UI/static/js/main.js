// Agent Manager UI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the UI
    refreshAgentsList();
    
    // Set up event listeners
    document.getElementById('refresh-agents').addEventListener('click', refreshAgentsList);
    document.getElementById('create-agent-form').addEventListener('submit', createAgent);
    document.getElementById('run-agent-form').addEventListener('submit', runAgent);
    
    // Set up event listeners for cleanup debugging
    document.getElementById('trigger-cleanup').addEventListener('click', triggerCleanupCheck);
    document.getElementById('show-cleanup-debug').addEventListener('click', toggleCleanupDebug);
    
    // Update the inactive timeout value
    const timeoutValue = 30; // Get this from your config somehow
    document.getElementById('inactive-timeout').textContent = timeoutValue;
    
    // Start monitoring cleanup status
    updateCleanupStatus();
    setInterval(updateCleanupStatus, 5000);
});

// Fetch and display the list of active agents
function refreshAgentsList() {
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateAgentsList(data.agents);
                updateAgentDropdown(data.agents);
            } else {
                showError('Failed to load agents: ' + data.message);
            }
        })
        .catch(error => {
            showError('Error: ' + error.message);
        });
}

// Update the agents list in the UI
function updateAgentsList(agents) {
    const agentsList = document.getElementById('agents-list');
    
    if (Object.keys(agents).length === 0) {
        agentsList.innerHTML = '<div class="text-center p-3">No active agents</div>';
        return;
    }
    
    let html = '';
    for (const [agentId, status] of Object.entries(agents)) {
        const statusClass = 'status-' + status.status;
        const timeLeft = Math.round(status.time_left);
        
        html += `
            <div class="list-group-item agent-item">
                <div>
                    <div class="agent-status">
                        <span class="status-indicator ${statusClass}"></span>
                        <strong>${agentId}</strong>
                    </div>
                    <div class="agent-time-left">
                        Idle: ${Math.round(status.idle_time)}s | Cleanup in: ${timeLeft}s
                    </div>
                </div>
                <div class="agent-controls">
                    <button class="btn btn-sm btn-success" onclick="selectAgentToRun('${agentId}')">Run</button>
                    <button class="btn btn-sm btn-danger" onclick="cleanupAgent('${agentId}')">Clean Up</button>
                </div>
            </div>
        `;
    }
    
    agentsList.innerHTML = html;
}

// Update the agent dropdown in the run form
function updateAgentDropdown(agents) {
    const dropdown = document.getElementById('run-agent-id');
    const currentValue = dropdown.value;
    
    // Clear existing options except the placeholder
    while (dropdown.options.length > 1) {
        dropdown.remove(1);
    }
    
    // Add options for each agent
    for (const agentId in agents) {
        const option = document.createElement('option');
        option.value = agentId;
        option.textContent = agentId;
        dropdown.appendChild(option);
    }
    
    // Restore previous selection if it still exists
    if (currentValue && dropdown.querySelector(`option[value="${currentValue}"]`)) {
        dropdown.value = currentValue;
    }
}

// Create a new agent
function createAgent(event) {
    event.preventDefault();
    
    const name = document.getElementById('agent-name').value.trim();
    const instructions = document.getElementById('agent-instructions').value.trim();
    const dependencies = document.getElementById('agent-dependencies').value.trim();
    
    if (!instructions) {
        showError('Instructions are required');
        return;
    }
    
    const requestData = {
        name: name || null,
        instructions: instructions,
        dependencies: dependencies
    };
    
    fetch('/api/create-agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showResult(`Agent created: ${data.agent_id}`);
            refreshAgentsList();
            document.getElementById('create-agent-form').reset();
        } else {
            showError('Failed to create agent: ' + data.message);
        }
    })
    .catch(error => {
        showError('Error: ' + error.message);
    });
}

// Run an agent
function runAgent(event) {
    event.preventDefault();
    
    const agentId = document.getElementById('run-agent-id').value;
    const argsString = document.getElementById('run-agent-args').value.trim();
    const asSubprocess = document.getElementById('run-as-subprocess').checked;
    
    if (!agentId) {
        showError('Please select an agent to run');
        return;
    }
    
    // Parse args
    const args = argsString ? argsString.split(',').map(arg => arg.trim()) : [];
    
    const requestData = {
        args: args,
        kwargs: {},
        subprocess: asSubprocess
    };
    
    showResult('Running agent...');
    
    fetch(`/api/run-agent/${agentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showResult(JSON.stringify(data.result, null, 2));
            refreshAgentsList();
        } else {
            showError('Failed to run agent: ' + data.message);
        }
    })
    .catch(error => {
        showError('Error: ' + error.message);
    });
}

// Select an agent to run
function selectAgentToRun(agentId) {
    document.getElementById('run-agent-id').value = agentId;
    document.getElementById('run-agent-form').scrollIntoView({ behavior: 'smooth' });
}

// Clean up an agent
function cleanupAgent(agentId) {
    if (!confirm(`Are you sure you want to clean up agent ${agentId}?`)) {
        return;
    }
    
    fetch(`/api/cleanup-agent/${agentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ delay: 0 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showResult(data.message);
            refreshAgentsList();
        } else {
            showError('Failed to clean up agent: ' + data.message);
        }
    })
    .catch(error => {
        showError('Error: ' + error.message);
    });
}

// Display a result in the results area
function showResult(message) {
    document.getElementById('results').textContent = message;
}

// Display an error in the results area
function showError(message) {
    document.getElementById('results').textContent = 'ERROR: ' + message;
    document.getElementById('results').classList.add('text-danger');
    setTimeout(() => {
        document.getElementById('results').classList.remove('text-danger');
    }, 3000);
}

// Periodically refresh the agents list
setInterval(refreshAgentsList, 5000);

// Cleanup debugging functionality
function updateCleanupStatus() {
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('active-agents-count').textContent = Object.keys(data.agents).length;
                
                const debugInfo = {
                    agents: data.agents,
                    timestamp: new Date().toISOString()
                };
                
                document.getElementById('cleanup-debug').textContent = 
                    JSON.stringify(debugInfo, null, 2);
            }
        })
        .catch(error => {
            console.error('Error fetching cleanup status:', error);
        });
}

function triggerCleanupCheck() {
    fetch('/api/check-cleanup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showResult('Cleanup check triggered. Remaining agents: ' + data.remaining_agents.join(', '));
            updateCleanupStatus();
            refreshAgentsList();
        } else {
            showError('Failed to trigger cleanup: ' + data.message);
        }
    })
    .catch(error => {
        showError('Error: ' + error.message);
    });
}

function toggleCleanupDebug() {
    const debugElement = document.getElementById('cleanup-debug');
    if (debugElement.style.display === 'none') {
        debugElement.style.display = 'block';
        document.getElementById('show-cleanup-debug').textContent = 'Hide Debug Info';
    } else {
        debugElement.style.display = 'none';
        document.getElementById('show-cleanup-debug').textContent = 'Show Debug Info';
    }
} 