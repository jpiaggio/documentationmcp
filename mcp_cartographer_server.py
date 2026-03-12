#!/usr/bin/env python3
"""
MCP Server for querying cartographer results using an in-memory graph database.
"""

import json
import sys
import asyncio
from typing import Any, Optional

from mcp.server import Server
from mcp.types import Tool

# Global graph instance
class SimpleGraph:
    """Simple in-memory graph database for code structure."""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
    
    def add_node(self, node_id: str, node_type: str, **properties):
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            **properties
        }
    
    def add_edge(self, source_id: str, edge_type: str, target_id: str):
        if source_id in self.nodes and target_id in self.nodes:
            self.edges.append((source_id, edge_type, target_id))
    
    def get_node(self, node_id: str):
        return self.nodes.get(node_id)
    
    def find_nodes(self, **filters):
        results = []
        for node in self.nodes.values():
            match = True
            for key, value in filters.items():
                if node.get(key) != value:
                    match = False
                    break
            if match:
                results.append(node)
        return results
    
    def get_outgoing(self, node_id: str, edge_type: Optional[str] = None):
        results = []
        for source, etype, target in self.edges:
            if source == node_id and (edge_type is None or etype == edge_type):
                target_node = self.nodes.get(target)
                if target_node:
                    results.append((etype, target_node))
        return results
    
    def get_incoming(self, node_id: str, edge_type: Optional[str] = None):
        results = []
        for source, etype, target in self.edges:
            if target == node_id and (edge_type is None or etype == edge_type):
                source_node = self.nodes.get(source)
                if source_node:
                    results.append((etype, source_node))
        return results
    
    def clear(self):
        self.nodes.clear()
        self.edges.clear()
    
    def stats(self):
        modules = len(self.find_nodes(type='Module'))
        functions = len(self.find_nodes(type='Function'))
        classes = len(self.find_nodes(type='Class'))
        return {
            'modules': modules,
            'functions': functions,
            'classes': classes,
            'nodes': modules + functions + classes,
            'edges': len(self.edges)
        }


graph = SimpleGraph()

# Create MCP server
server = Server("cartographer-graph")


def load_from_cypher(cypher_statements):
    """Load from Cypher statements."""
    import re
    
    for stmt in cypher_statements:
        if not stmt.strip():
            continue
        
        # Extract node definitions
        node_pattern = r'\((\w+):(\w+)\s*\{([^}]+)\}\)'
        nodes_match = re.findall(node_pattern, stmt)
        
        node_map = {}
        for var, node_type, props_str in nodes_match:
            props = {}
            prop_pattern = r"(\w+):\s*'([^']*?)'"
            for prop_name, prop_value in re.findall(prop_pattern, props_str):
                props[prop_name] = prop_value
            
            node_map[var] = (node_type, props)
            
            # Create node
            name = props.get('name', props.get('module', 'unknown'))
            node_id = f"{node_type.lower()}:{name}"
            graph.add_node(node_id, node_type, **props)
        
        # Extract relationships
        rel_pattern = r'\((\w+)\)-\[:(\w+)\]->\((\w+)\)'
        rels_match = re.findall(rel_pattern, stmt)
        
        for source_var, rel_type, target_var in rels_match:
            if source_var in node_map and target_var in node_map:
                source_type, source_props = node_map[source_var]
                target_type, target_props = node_map[target_var]
                
                source_name = source_props.get('name', source_props.get('module', 'unknown'))
                target_name = target_props.get('name', target_props.get('module', 'unknown'))
                
                source_id = f"{source_type.lower()}:{source_name}"
                target_id = f"{target_type.lower()}:{target_name}"
                
                graph.add_edge(source_id, rel_type, target_id)


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="list_modules",
            description="List all modules in the code graph",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="list_functions",
            description="List all functions in the code graph",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="list_classes",
            description="List all classes in the code graph",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="get_module_contents",
            description="Get all functions and classes in a specific module",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module to query"
                    }
                },
                "required": ["module_name"]
            }
        ),
        Tool(
            name="get_module_dependencies",
            description="Get all modules that a specific module depends on",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module to query"
                    }
                },
                "required": ["module_name"]
            }
        ),
        Tool(
            name="find_function",
            description="Find a function by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function to find"
                    }
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="find_class",
            description="Find a class by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "Name of the class to find"
                    }
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="get_dependency_graph",
            description="Get the dependency graph for a module",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module"
                    }
                },
                "required": ["module_name"]
            }
        ),
        Tool(
            name="graph_stats",
            description="Get statistics about the loaded graph",
            inputSchema={"type": "object", "properties": {}, "required": []}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    """Handle tool calls."""
    
    if name == "load_cartographer_data":
        data = arguments.get("data_json", "")
        try:
            data_obj = json.loads(data)
            return f"Loaded {len(graph.nodes)} nodes"
        except:
            return "Failed to load data"
    
    elif name == "list_modules":
        modules = graph.find_nodes(type='Module')
        if not modules:
            return "No modules found."
        output = f"Found {len(modules)} modules:\n\n"
        for mod in sorted(modules, key=lambda x: x.get('name', '')):
            output += f"- {mod['name']} ({mod.get('path', 'N/A')})\n"
        return output
    
    elif name == "list_functions":
        functions = graph.find_nodes(type='Function')
        if not functions:
            return "No functions found."
        by_module = {}
        for func in functions:
            module = func.get('module', 'unknown')
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(func)
        output = f"Found {len(functions)} functions:\n\n"
        for module in sorted(by_module.keys()):
            output += f"{module}:\n"
            for func in sorted(by_module[module], key=lambda x: x['name']):
                output += f"  - {func['name']}\n"
        return output
    
    elif name == "list_classes":
        classes = graph.find_nodes(type='Class')
        if not classes:
            return "No classes found."
        by_module = {}
        for cls in classes:
            module = cls.get('module', 'unknown')
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(cls)
        output = f"Found {len(classes)} classes:\n\n"
        for module in sorted(by_module.keys()):
            output += f"{module}:\n"
            for cls in sorted(by_module[module], key=lambda x: x['name']):
                output += f"  - {cls['name']}\n"
        return output
    
    elif name == "get_module_contents":
        module_name = arguments.get("module_name", "")
        module_id = f"module:{module_name}"
        items = graph.get_outgoing(module_id, 'CONTAINS')
        if not items:
            return f"Module '{module_name}' not found or is empty."
        output = f"Contents of module '{module_name}':\n\n"
        functions = [item for etype, item in items if item['type'] == 'Function']
        classes = [item for etype, item in items if item['type'] == 'Class']
        if functions:
            output += "Functions:\n"
            for func in sorted(functions, key=lambda x: x['name']):
                output += f"  - {func['name']}\n"
        if classes:
            output += "\nClasses:\n"
            for cls in sorted(classes, key=lambda x: x['name']):
                output += f"  - {cls['name']}\n"
        return output
    
    elif name == "get_module_dependencies":
        module_name = arguments.get("module_name", "")
        module_id = f"module:{module_name}"
        deps = graph.get_outgoing(module_id, 'DEPENDS_ON')
        if not deps:
            return f"Module '{module_name}' has no dependencies or not found."
        output = f"Dependencies of module '{module_name}':\n\n"
        for etype, dep in sorted(deps, key=lambda x: x[1]['name']):
            output += f"- {dep['name']}\n"
        return output
    
    elif name == "find_function":
        function_name = arguments.get("function_name", "")
        functions = graph.find_nodes(type='Function', name=function_name)
        if not functions:
            return f"Function '{function_name}' not found."
        output = f"Found function '{function_name}':\n\n"
        for func in functions:
            output += f"- Module: {func.get('module', 'N/A')}\n"
        return output
    
    elif name == "find_class":
        class_name = arguments.get("class_name", "")
        classes = graph.find_nodes(type='Class', name=class_name)
        if not classes:
            return f"Class '{class_name}' not found."
        output = f"Found class '{class_name}':\n\n"
        for cls in classes:
            output += f"- Module: {cls.get('module', 'N/A')}\n"
        return output
    
    elif name == "get_dependency_graph":
        module_name = arguments.get("module_name", "")
        module_id = f"module:{module_name}"
        deps = graph.get_outgoing(module_id, 'DEPENDS_ON')
        dependents = graph.get_incoming(module_id, 'DEPENDS_ON')
        output = f"Dependency Graph for '{module_name}':\n\n"
        if deps:
            output += "Depends On:\n"
            for etype, dep in sorted(deps, key=lambda x: x[1]['name']):
                output += f"  -> {dep['name']}\n"
        if dependents:
            output += "\nDepended By:\n"
            for etype, dependent in sorted(dependents, key=lambda x: x[1]['name']):
                output += f"  <- {dependent['name']}\n"
        if not deps and not dependents:
            output += "No dependencies found.\n"
        return output
    
    elif name == "graph_stats":
        s = graph.stats()
        output = f"""Graph Statistics:

- Modules: {s['modules']}
- Functions: {s['functions']}
- Classes: {s['classes']}
- Total Nodes: {s['nodes']}
- Total Edges: {s['edges']}
"""
        return output
    
    return f"Unknown tool: {name}"


if __name__ == "__main__":
    # Run the server
    server.run(["stdio"])
