# Cartographer MCP Server (In-Memory - No Docker Required!)

This MCP server allows you to query your code structure without needing Docker or Neo4j. It uses a simple in-memory graph database that loads cartographer results directly.

## Features

✅ **No Docker Required** - Runs entirely in-memory  
✅ **No External Databases** - No setup needed  
✅ **Fast** - In-memory queries are instant  
✅ **Full Code Graph Analysis** - Modules, functions, classes, dependencies  

## Tools Available

- **load_cartographer_data** - Load cartographer results as JSON
- **list_modules** - Show all modules
- **list_functions** - Show all functions
- **list_classes** - Show all classes
- **get_module_contents** - Get contents of a module
- **get_module_dependencies** - Get what a module depends on
- **find_function** - Locate a function
- **find_class** - Locate a class
- **get_dependency_graph** - Visualize dependencies
- **graph_stats** - Get graph statistics

## Quick Start

### Step 1: Run the MCP Server with Your Repository

```bash
cd /Users/juani/github-projects/documentationmcp/documentationmcp
python3 run_cartographer_mcp.py /path/to/your/repo
```

This will:
1. Scan your repository with the cartographer agent
2. Convert results to JSON format
3. Load data into the in-memory graph
4. Start the MCP server

### Step 2: Use with Claude or Other MCP Clients

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cartographer": {
      "command": "python3",
      "args": ["/Users/juani/github-projects/documentationmcp/documentationmcp/run_cartographer_mcp.py", "/path/to/repo"]
    }
  }
}
```

Then ask Claude:
- "List all modules in my project"
- "What functions are in synthesis_agent?"
- "Show me the dependencies of cartographer_agent"
- "Where is the SynthesisAgent class?"

## Usage Examples

### List All Modules
```
Tool: list_modules
Output: Found 5 modules:
- __init__ (/path/to/agents/__init__.py)
- cartographer_agent (/path/to/agents/cartographer_agent.py)
- synthesis_agent (/path/to/agents/synthesis_agent.py)
...
```

### Get Module Contents
```
Tool: get_module_contents
Args: module_name = "synthesis_agent"
Output: Contents of module 'synthesis_agent':

Functions:
  - __init__
  - synthesize
  - _build_exec_summary_prompt
  - ...

Classes:
  - SynthesisAgent
```

### Find Function
```
Tool: find_function
Args: function_name = "cartographer_agent"
Output: Found function 'cartographer_agent':
- Module: cartographer_agent
```

### Get Dependencies
```
Tool: get_module_dependencies
Args: module_name = "cartographer_agent"
Output: Dependencies of module 'cartographer_agent':
- os
- sys
- concurrent
- tree_sitter_python
- tree_sitter
```

### View Dependency Graph
```
Tool: get_dependency_graph
Args: module_name = "synthesis_agent"
Output: Dependency Graph for 'synthesis_agent':

Depends On:
  -> typing
```

## How It Works

1. **Cartographer Agent** scans your Python repository and extracts:
   - Module/file information
   - Functions and their signatures
   - Classes and their methods
   - Import statements and dependencies

2. **JSON Conversion** transforms Cypher statements into JSON:
   ```json
   {
     "modules": [
       {
         "name": "synthesis_agent",
         "path": "/path/to/synthesis_agent.py",
         "functions": [...],
         "classes": [...],
         "dependencies": [...]
       }
     ]
   }
   ```

3. **In-Memory Graph** stores this data in a simple graph structure with:
   - Nodes: Modules, Functions, Classes
   - Edges: CONTAINS (module→item), DEPENDS_ON (module→dependency)

4. **Query Tools** traverse this graph to answer questions about your code

## Advantages Over Neo4j Version

- ✅ No Docker installation needed
- ✅ No database setup required
- ✅ Faster for small-medium projects
- ✅ Works offline
- ✅ Easy to debug (all data is Python objects)

## Limitations

- Limited to projects that fit in memory (typically fine for < 10k functions)
- No persistence (data is lost when server stops)
- No multi-user support

For very large projects or persistent storage, use the Neo4j version.

## Troubleshooting

### "Module not found" error
Make sure you're running from the correct directory:
```bash
cd /Users/juani/github-projects/documentationmcp/documentationmcp
```

### No data loaded
Ensure your repository has Python files:
```bash
find /path/to/repo -name "*.py" | head
```

### MCP server not starting
Check Python version (3.9+):
```bash
python3 --version
```

Reinstall MCP package:
```bash
pip3 install mcp
```

## Integration with Claude Desktop

1. Find your configuration file:
   - **macOS/Linux**: `~/.config/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the server:
```json
{
  "mcpServers": {
    "cartographer-graph": {
      "command": "python3",
      "args": ["/path/to/run_cartographer_mcp.py", "/path/to/your/repo"],
      "disabled": false
    }
  }
}
```

3. Restart Claude Desktop

4. Ask now in any conversation!

## Example Queries

Ask Claude:
- "What's the overall structure of my project?"
- "List all classes defined in this codebase"
- "Show me all the functions in the synthesis_agent module"
- "What does the cartographer_agent module depend on?"
- "Find the SynthesisAgent class"
- "Show dependency relationships for the utils module"
- "How many modules are in this project?"

Enjoy exploring your codebase!
