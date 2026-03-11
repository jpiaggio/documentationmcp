# Neo4j Cartographer MCP Server

This is an MCP (Model Context Protocol) server that allows you to query cartographer results stored in a Neo4j database.

## Features

- **neo4j_connect**: Connect to a Neo4j database
- **list_modules**: List all modules in the code graph
- **list_functions**: List all functions
- **list_classes**: List all classes
- **get_module_contents**: Get functions and classes in a module
- **get_module_dependencies**: Get dependencies of a module
- **find_function**: Find where a function is defined
- **find_class**: Find where a class is defined
- **query_cypher**: Execute custom Cypher queries
- **get_dependency_graph**: Visualize dependency relationships

## Setup

### 1. Start Neo4j

Using Docker (easiest):
```bash
docker run -p 7687:7687 -p 7474:7474 --name neo4j-cartographer \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Neo4j will be available at:
- Graph database: `bolt://localhost:7687`
- Web browser: `http://localhost:7474`

### 2. Load Cartographer Results

Load results from your repository into Neo4j:

```bash
python3 run_mcp_neo4j.py /path/to/your/repo
```

This will:
1. Run the cartographer agent on your repository
2. Load all Cypher statements into Neo4j
3. Start the MCP server

### 3. Usage with Claude or other MCP clients

Configure your MCP client (e.g., Claude's `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "neo4j-cartographer": {
      "command": "python3",
      "args": ["/path/to/mcp_neo4j_server.py"]
    }
  }
}
```

Then you can ask Claude:
- "List all modules in the project"
- "What are the dependencies of the synthesis_agent module?"
- "Where is the SynthesisAgent class defined?"
- "Show me all functions in the cartographer_agent module"

## Examples

### Via Python Script

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# Query all modules
with driver.session() as session:
    result = session.run("MATCH (m:Module) RETURN m.name, m.path")
    for record in result:
        print(f"{record['m.name']}: {record['m.path']}")

driver.close()
```

### Via Neo4j Browser

1. Open http://localhost:7474
2. Connect with neo4j / password
3. Run queries:

```cypher
// Find all modules
MATCH (m:Module) RETURN m.name, m.path

// Find all functions in a module
MATCH (m:Module {name: 'synthesis_agent'})-[:CONTAINS]->(f:Function)
RETURN f.name

// Find dependency graph
MATCH (m:Module {name: 'cartographer_agent'})-[:DEPENDS_ON]->(dep:Module)
RETURN m.name, dep.name

// Find what depends on a module
MATCH (dependent:Module)-[:DEPENDS_ON]->(m:Module {name: 'utils'})
RETURN dependent.name
```

## MCP Tool Reference

### neo4j_connect
Connect to a Neo4j database.
- `uri`: Connection URI (default: "bolt://localhost:7687")
- `username`: Database username (default: "neo4j")
- `password`: Database password (default: "password")

### list_modules
List all modules in the code graph.

### list_functions
List all functions organized by module.

### list_classes
List all classes organized by module.

### get_module_contents(module_name)
Get all functions and classes in a specific module.
- `module_name`: Name of the module to query

### get_module_dependencies(module_name)
Get all modules that a module depends on.
- `module_name`: Name of the module to query

### find_function(function_name)
Find which module(s) contain a function.
- `function_name`: Name of the function to find

### find_class(class_name)
Find which module(s) contain a class.
- `class_name`: Name of the class to find

### query_cypher(cypher_query)
Execute a custom Cypher query.
- `cypher_query`: Cypher query string

### get_dependency_graph(module_name)
Visualize what a module depends on and what depends on it.
- `module_name`: Name of the module to analyze

## Troubleshooting

### Connection refused
Make sure Neo4j is running:
```bash
docker ps | grep neo4j
```

Start Neo4j if not running:
```bash
docker run -p 7687:7687 -p 7474:7474 --name neo4j-cartographer \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### No modules found
Load the cartographer results first:
```bash
python3 run_mcp_neo4j.py /path/to/your/repo
```

### Python package errors
Install required packages:
```bash
pip install neo4j mcp
```

## Integration with Claude

You can add this MCP server to Claude via the desktop app:

1. Install the MCP desktop app
2. Add the server to your configuration
3. Ask Claude to query your codebase!

Example prompts:
- "List all modules in my project"
- "Show me the contents of the synthesis_agent module"
- "What are the external dependencies of cartographer_agent?"
- "Find the SynthesisAgent class definition"
