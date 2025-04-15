# AgentStart Programming Language Reference

## Introduction

AgentStart is a programming language designed for creating, managing, and coordinating agent-based systems. Each agent runs in its own thread, allowing for concurrent execution of tasks while maintaining a simple, unified interface.

## Core Concepts

- **Agents**: Independent entities that run in separate threads and can process tasks
- **Common Interface**: All agents share the same basic operations (tell, ask, wait, free)
- **Thread-based**: Each agent runs in its own thread for concurrent execution
- **Simple Syntax**: Python/Java-like syntax with familiar control structures

## Language Syntax

### Agent Operations

// Create a new agent
agent myAgent = create

// Send instructions to an agent
tell myAgent "Do this task"
tell myAgent {"action": "write", "path": "file.txt", "content": "Hello"}

// Get results from an agent
result = ask myAgent

// Wait for agent to complete its task
wait myAgent

// Terminate an agent and free resources
free myAgent

### Control Structures

// Conditional statements
if (condition) {
    // code to execute
} else if (anotherCondition) {
    // code to execute
} else {
    // code to execute
}

// For loop
for (i = 0; i < 10; i++) {
    // code to execute
}

// For-in loop (iteration)
for (item in items) {
    // code to execute
}

// While loop
while (condition) {
    // code to execute
}

### Functions

// Function definition
func processData(data) {
    // Process the data
    return result
}

// Function call
result = processData(myData)

## Built-in Agent Types

### FileAgent

Specialized for file operations:

// Create a file agent
agent fileHandler = create from "agent_types.FileAgent"

// Write to a file
tell fileHandler {
    "action": "write",
    "path": "output.txt",
    "content": "Hello world!"
}

// Read from a file
tell fileHandler {
    "action": "read",
    "path": "input.txt"
}

// List files in a directory
tell fileHandler {
    "action": "list",
    "path": "/path/to/directory"
}

### DatabaseAgent

Specialized for SQLite database operations:

// Create a database agent
agent dbAgent = create from "agent_types.DatabaseAgent"

// Execute SQL directly
tell dbAgent "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
tell dbAgent "INSERT INTO users (name) VALUES ('Alice'), ('Bob')"
tell dbAgent "SELECT * FROM users"

// Or use structured commands
tell dbAgent {
    "action": "query",
    "sql": "SELECT * FROM users WHERE id = ?",
    "params": [1]
}

## Complete Example

// Main function
func main() {
    // Create agents
    agent fileHandler = create from "agent_types.FileAgent"
    agent dbAgent = create from "agent_types.DatabaseAgent"
    
    // File operations
    tell fileHandler {
        "action": "write", 
        "path": "data.txt", 
        "content": "Sample data"
    }
    
    wait fileHandler
    
    // Database operations
    tell dbAgent "CREATE TABLE data (id INTEGER PRIMARY KEY, value TEXT)"
    wait dbAgent
    
    tell dbAgent "INSERT INTO data (value) VALUES ('Sample data')"
    wait dbAgent
    
    tell dbAgent "SELECT * FROM data"
    var result = ask dbAgent
    
    // Process results
    if (result.status == "success") {
        for (row in result.rows) {
            print("Data: " + row[1])
        }
    }
    
    // Clean up
    free fileHandler
    free dbAgent
}

// Run the main function
main()

## Compilation and Execution

AgentStart programs use the `.as` file extension. To compile and run:

// Compile only
python -m AgentStart.compiler your_program.as

// Compile and run
python -m AgentStart.compiler your_program.as --run

## Error Handling

// Try to execute code that might fail
try {
    tell agentA "potentially risky operation"
    result = ask agentA
} catch (error) {
    print("An error occurred: " + error)
} finally {
    // Clean up regardless of success or failure
    free agentA
}

## Agent Status Checking

// Check agent status
status = myAgent.state  // "ready", "busy", "done", "failed"

if (status == "ready") {
    tell myAgent "new task"
}

## Advanced Usage

### Agent Pipelines

// Create a data processing pipeline
agent reader = create
agent processor = create
agent writer = create

// Set up the pipeline
tell reader {"action": "read", "path": "input.txt"}
wait reader
data = ask reader

tell processor {"action": "process", "data": data}
wait processor
result = ask processor

tell writer {"action": "write", "path": "output.txt", "content": result}
wait writer

### Parallel Processing

// Create multiple worker agents
agents = []
for (i = 0; i < 5; i++) {
    agent worker = create
    agents.push(worker)
    tell worker {"action": "process", "item": items[i]}
}

// Wait for all to complete
for (worker in agents) {
    wait worker
    results.push(ask worker)
    free worker
}

## Implementation Details

### Core Components

The AgentStart language is implemented with several key components:

1. **agent_core.py**: Defines the base `Agent` class with the common interface
2. **agent_types.py**: Specialized agent types for specific tasks (FileAgent, DatabaseAgent)
3. **parser.py**: Translates AgentStart syntax to executable Python code
4. **compiler.py**: Compiles .as files to Python and can execute them

### Testing Framework

The implementation includes comprehensive tests to ensure all components work correctly:

- **test_agent_core.py**: Tests for the basic Agent functionality
- **test_agent_types.py**: Tests for specialized agent types
- **test_parser.py**: Tests for the parser component
- **test_compiler.py**: Tests for the compiler component
- **test_integration.py**: End-to-end integration tests

To run all tests, execute:
```
python run_tests.py
```

Or run individual test modules:
```
python -m unittest AgentStart.test.test_agent_core
```

### Thread Management

Each agent runs in its own thread, which is automatically managed:

- Threads are created when agents are first told to do something
- Threads are properly terminated when agents are freed
- The main program can wait for agent tasks to complete using the `wait` command

### Communication Protocol

Agents communicate through thread-safe queues:

- Task instructions go into the task_queue
- Results come back through the result_queue
- Structured data (dictionaries) is used for complex operations

### Error Handling

Agents have built-in error handling capabilities:

- Exceptions in agent threads don't crash the main program
- Errors are reported through the result mechanism
- The agent state changes to "failed" when errors occur 