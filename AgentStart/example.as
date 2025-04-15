// Example AgentStart program with Python/Java-like syntax

// Import agent types if needed
import "agent_types"

// Main function
func main() {
    // Create agents with common interface
    agent fileHandler = create
    agent dbAgent = create
    
    // File operations
    tell fileHandler {
        "action": "write", 
        "path": "output.txt", 
        "content": "Hello from AgentStart!"
    }
    
    // Wait for completion
    wait fileHandler
    
    // Database operations
    tell dbAgent "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
    wait dbAgent
    
    tell dbAgent "INSERT INTO users (name) VALUES ('John'), ('Alice'), ('Bob')"
    wait dbAgent
    
    tell dbAgent "SELECT * FROM users"
    
    // Get results
    var result = ask dbAgent
    
    // Print results
    if (result.status == "success") {
        for (row in result.rows) {
            print("User: " + row[1])
        }
    }
    
    // Clean up agents
    free fileHandler
    free dbAgent
}

// Call main
main() 