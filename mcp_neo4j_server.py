#!/usr/bin/env python3
"""
MCP Server for querying Neo4j graph database with cartographer results.
"""

import json
import sys
from typing import Any, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

try:
    from neo4j import GraphDatabase, Driver, Session
except ImportError:
    print("neo4j package not installed. Install with: pip install neo4j", file=sys.stderr)
    sys.exit(1)

# Initialize MCP Server
mcp = Server("neo4j-cartographer")

# Global Neo4j driver
neo4j_driver: Optional[Driver] = None


def connect_neo4j(uri: str, username: str, password: str) -> Driver:
    """Connect to Neo4j database."""
    global neo4j_driver
    try:
        neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
        # Test connection
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1")
            result.consume()
        print(f"Connected to Neo4j at {uri}", file=sys.stderr)
        return neo4j_driver
    except Exception as e:
        print(f"Error connecting to Neo4j: {e}", file=sys.stderr)
        raise


def execute_query(query: str) -> dict:
    """Execute a Cypher query and return results."""
    if not neo4j_driver:
        return {"error": "Not connected to Neo4j. Call neo4j_connect first."}
    
    try:
        with neo4j_driver.session() as session:
            result = session.run(query)
            records = [dict(record) for record in result]
            return {
                "success": True,
                "count": len(records),
                "data": records
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def neo4j_connect(uri: str, username: str = "neo4j", password: str = "password") -> TextContent:
    """Connect to a Neo4j database.
    
    Args:
        uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
        username: Database username
        password: Database password
    
    Returns:
        Connection status message
    """
    try:
        connect_neo4j(uri, username, password)
        return TextContent(type="text", text=f"Successfully connected to Neo4j at {uri}")
    except Exception as e:
        return TextContent(type="text", text=f"Failed to connect to Neo4j: {e}")


@mcp.tool()
def list_modules() -> TextContent:
    """List all modules in the code graph."""
    query = "MATCH (m:Module) RETURN m.name, m.path ORDER BY m.name"
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    modules = result.get("data", [])
    if not modules:
        return TextContent(type="text", text="No modules found in the database.")
    
    output = f"Found {len(modules)} modules:\n\n"
    for mod in modules:
        output += f"- {mod.get('m.name', 'N/A')} ({mod.get('m.path', 'N/A')})\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def list_functions() -> TextContent:
    """List all functions in the code graph."""
    query = "MATCH (f:Function) RETURN f.name, f.module ORDER BY f.module, f.name"
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    functions = result.get("data", [])
    if not functions:
        return TextContent(type="text", text="No functions found in the database.")
    
    output = f"Found {len(functions)} functions:\n\n"
    current_module = None
    for func in functions:
        module = func.get('f.module', 'N/A')
        if module != current_module:
            output += f"\n{module}:\n"
            current_module = module
        output += f"  - {func.get('f.name', 'N/A')}\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def list_classes() -> TextContent:
    """List all classes in the code graph."""
    query = "MATCH (c:Class) RETURN c.name, c.module ORDER BY c.module, c.name"
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    classes = result.get("data", [])
    if not classes:
        return TextContent(type="text", text="No classes found in the database.")
    
    output = f"Found {len(classes)} classes:\n\n"
    current_module = None
    for cls in classes:
        module = cls.get('c.module', 'N/A')
        if module != current_module:
            output += f"\n{module}:\n"
            current_module = module
        output += f"  - {cls.get('c.name', 'N/A')}\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def get_module_contents(module_name: str) -> TextContent:
    """Get all functions and classes in a specific module.
    
    Args:
        module_name: Name of the module to query
    
    Returns:
        Functions and classes in the module
    """
    query = f"""
    MATCH (m:Module {{name: '{module_name}'}})
    OPTIONAL MATCH (m)-[:CONTAINS]->(item)
    RETURN item.name as name, 
           CASE WHEN item:Function THEN 'Function' 
                WHEN item:Class THEN 'Class' 
                ELSE 'Unknown' END as type
    ORDER BY type, name
    """
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    items = result.get("data", [])
    if not items:
        return TextContent(type="text", text=f"Module '{module_name}' not found or is empty.")
    
    output = f"Contents of module '{module_name}':\n\n"
    for item in items:
        if item.get('name'):
            output += f"- {item.get('type')}: {item.get('name')}\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def get_module_dependencies(module_name: str) -> TextContent:
    """Get all modules that a specific module depends on.
    
    Args:
        module_name: Name of the module to query
    
    Returns:
        List of dependencies
    """
    query = f"""
    MATCH (m:Module {{name: '{module_name}'}})-[:DEPENDS_ON]->(dep:Module)
    RETURN DISTINCT dep.name as dependency
    ORDER BY dependency
    """
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    deps = result.get("data", [])
    if not deps:
        return TextContent(type="text", text=f"Module '{module_name}' has no dependencies or not found.")
    
    output = f"Dependencies of module '{module_name}':\n\n"
    for dep in deps:
        output += f"- {dep.get('dependency', 'N/A')}\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def find_function(function_name: str) -> TextContent:
    """Find a function by name.
    
    Args:
        function_name: Name of the function to find
    
    Returns:
        Modules containing the function
    """
    query = f"""
    MATCH (f:Function {{name: '{function_name}'}})
    RETURN f.module as module, f.name as name
    """
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    functions = result.get("data", [])
    if not functions:
        return TextContent(type="text", text=f"Function '{function_name}' not found.")
    
    output = f"Found function '{function_name}':\n\n"
    for func in functions:
        output += f"- Module: {func.get('module', 'N/A')}\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def find_class(class_name: str) -> TextContent:
    """Find a class by name.
    
    Args:
        class_name: Name of the class to find
    
    Returns:
        Modules containing the class
    """
    query = f"""
    MATCH (c:Class {{name: '{class_name}'}})
    RETURN c.module as module, c.name as name
    """
    result = execute_query(query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    classes = result.get("data", [])
    if not classes:
        return TextContent(type="text", text=f"Class '{class_name}' not found.")
    
    output = f"Found class '{class_name}':\n\n"
    for cls in classes:
        output += f"- Module: {cls.get('module', 'N/A')}\n"
    
    return TextContent(type="text", text=output)


@mcp.tool()
def query_cypher(cypher_query: str) -> TextContent:
    """Execute a custom Cypher query.
    
    Args:
        cypher_query: Cypher query string
    
    Returns:
        Query results as JSON
    """
    result = execute_query(cypher_query)
    
    if not result.get("success"):
        return TextContent(type="text", text=f"Error: {result.get('error')}")
    
    output = f"Query returned {result.get('count', 0)} results:\n\n"
    output += json.dumps(result.get("data", []), indent=2)
    
    return TextContent(type="text", text=output)


@mcp.tool()
def get_dependency_graph(module_name: str) -> TextContent:
    """Get the dependency graph for a module (what it depends on and what depends on it).
    
    Args:
        module_name: Name of the module
    
    Returns:
        Dependency graph visualization
    """
    # Get dependencies
    deps_query = f"""
    MATCH (m:Module {{name: '{module_name}'}})-[:DEPENDS_ON]->(dep:Module)
    RETURN 'depends_on' as relation, dep.name as target
    """
    
    # Get dependents
    dependents_query = f"""
    MATCH (dependent:Module)-[:DEPENDS_ON]->(m:Module {{name: '{module_name}'}})
    RETURN 'depended_by' as relation, dependent.name as target
    """
    
    deps_result = execute_query(deps_query)
    dependents_result = execute_query(dependents_query)
    
    if not deps_result.get("success") or not dependents_result.get("success"):
        return TextContent(type="text", text=f"Error querying dependency graph")
    
    output = f"Dependency Graph for '{module_name}':\n\n"
    
    deps = deps_result.get("data", [])
    if deps:
        output += "Depends On:\n"
        for dep in deps:
            output += f"  -> {dep.get('target', 'N/A')}\n"
    
    dependents = dependents_result.get("data", [])
    if dependents:
        output += "\nDepended By:\n"
        for dependent in dependents:
            output += f"  <- {dependent.get('target', 'N/A')}\n"
    
    if not deps and not dependents:
        output += "No dependencies found.\n"
    
    return TextContent(type="text", text=output)


if __name__ == "__main__":
    # Start the MCP server
    mcp.run(sys.argv[1:] if len(sys.argv) > 1 else ["stdio"])
