#!/usr/bin/env python3
"""
Simple Cartographer Graph Query Tool (Python 3.9 compatible)
No MCP library needed - works standalone with simple CLI interface
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set


class SimpleGraph:
    """Simple in-memory graph database for code structure."""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[tuple] = []
    
    def add_node(self, node_id: str, node_type: str, **properties):
        """Add a node to the graph."""
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            **properties
        }
    
    def add_edge(self, source_id: str, edge_type: str, target_id: str):
        """Add an edge to the graph."""
        if source_id in self.nodes and target_id in self.nodes:
            self.edges.append((source_id, edge_type, target_id))
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def find_nodes(self, **filters) -> List[Dict]:
        """Find nodes matching filters."""
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
    
    def get_outgoing(self, node_id: str, edge_type: Optional[str] = None) -> List[tuple]:
        """Get outgoing edges from a node."""
        results = []
        for source, etype, target in self.edges:
            if source == node_id and (edge_type is None or etype == edge_type):
                target_node = self.nodes.get(target)
                if target_node:
                    results.append((etype, target_node))
        return results
    
    def get_incoming(self, node_id: str, edge_type: Optional[str] = None) -> List[tuple]:
        """Get incoming edges to a node."""
        results = []
        for source, etype, target in self.edges:
            if target == node_id and (edge_type is None or etype == edge_type):
                source_node = self.nodes.get(source)
                if source_node:
                    results.append((etype, source_node))
        return results
    
    def clear(self):
        """Clear the graph."""
        self.nodes.clear()
        self.edges.clear()
    
    def stats(self) -> Dict:
        """Get graph statistics."""
        modules = len(self.find_nodes(type='Module'))
        business_modules = len(self.find_nodes(type='BusinessModule'))
        functions = len(self.find_nodes(type='Function'))
        methods = len(self.find_nodes(type='Method'))
        classes = len(self.find_nodes(type='Class'))
        total_modules = modules + business_modules
        return {
            'modules': total_modules,
            'business_modules': business_modules,
            'regular_modules': modules,
            'functions': functions,
            'methods': methods,
            'classes': classes,
            'nodes': total_modules + functions + methods + classes,
            'edges': len(self.edges)
        }


class CartographerQuery:
    """Query interface for cartographer graph."""
    
    def __init__(self, repo_path: str, file_ext: str = '.py,.java'):
        self.graph = SimpleGraph()
        self.repo_path = repo_path
        self.file_ext = file_ext
        self.load_from_repo()
    
    def load_from_repo(self):
        """Load cartographer data from a repository."""
        print(f"Scanning repository: {self.repo_path}", file=sys.stderr)
        print(f"File extensions: {self.file_ext}", file=sys.stderr)
        
        # Run cartographer agent with file extension parameter
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
sys.path.insert(0, '.')
from agents.cartographer_agent import cartographer_agent

cypher_statements = cartographer_agent(r'{self.repo_path}', file_ext='{self.file_ext}', max_workers=4)
for stmt in cypher_statements:
    print(stmt)
"""],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return
        
        # Parse output
        lines = result.stdout.split('\n') + result.stderr.split('\n')
        cypher_stmts = [l.strip() for l in lines if l.strip().startswith('MERGE')]
        
        self.load_from_cypher(cypher_stmts)
    
    def load_from_cypher(self, cypher_statements: List[str]):
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
                self.graph.add_node(node_id, node_type, **props)
            
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
                    
                    self.graph.add_edge(source_id, rel_type, target_id)
        
        stats = self.graph.stats()
        print(f"Loaded {stats['nodes']} nodes and {stats['edges']} edges", file=sys.stderr)
    
    def list_modules(self) -> str:
        """List all modules."""
        modules = self.graph.find_nodes(type='Module')
        business_modules = self.graph.find_nodes(type='BusinessModule')
        all_modules = modules + business_modules
        
        if not all_modules:
            return "No modules found."
        
        output = f"Found {len(all_modules)} modules:\n\n"
        for mod in sorted(all_modules, key=lambda x: x.get('name', '')):
            mod_type = mod.get('type', 'Module')
            domain = mod.get('domain', '')
            domain_str = f" [{domain}]" if domain else ""
            output += f"- {mod['name']}{domain_str} ({mod_type}) ({mod.get('path', 'N/A')})\n"
        return output
    
    def list_functions(self) -> str:
        """List all functions."""
        functions = self.graph.find_nodes(type='Function')
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
    
    def list_classes(self) -> str:
        """List all classes."""
        classes = self.graph.find_nodes(type='Class')
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
    
    def get_module_contents(self, module_name: str) -> str:
        """Get contents of a module."""
        module_id = f"module:{module_name}"
        items = self.graph.get_outgoing(module_id, 'CONTAINS')
        
        if not items:
            return f"Module '{module_name}' not found or is empty."
        
        output = f"Contents of module '{module_name}':\n\n"
        
        functions = [item for etype, item in items if item['type'] == 'Function']
        methods = [item for etype, item in items if item['type'] == 'Method']
        classes = [item for etype, item in items if item['type'] == 'Class']
        
        if functions:
            output += "Functions:\n"
            for func in sorted(functions, key=lambda x: x['name']):
                output += f"  - {func['name']}\n"
        
        if methods:
            output += "\nMethods:\n"
            for method in sorted(methods, key=lambda x: x['name']):
                output += f"  - {method['name']}\n"
        
        if classes:
            output += "\nClasses:\n"
            for cls in sorted(classes, key=lambda x: x['name']):
                output += f"  - {cls['name']}\n"
        
        return output
    
    def get_module_dependencies(self, module_name: str) -> str:
        """Get module dependencies."""
        module_id = f"module:{module_name}"
        deps = self.graph.get_outgoing(module_id, 'DEPENDS_ON')
        
        if not deps:
            return f"Module '{module_name}' has no dependencies or not found."
        
        output = f"Dependencies of module '{module_name}':\n\n"
        for etype, dep in sorted(deps, key=lambda x: x[1]['name']):
            output += f"- {dep['name']}\n"
        return output
    
    def find_function(self, function_name: str) -> str:
        """Find a function."""
        functions = self.graph.find_nodes(type='Function', name=function_name)
        
        if not functions:
            return f"Function '{function_name}' not found."
        
        output = f"Found function '{function_name}':\n\n"
        for func in functions:
            output += f"- Module: {func.get('module', 'N/A')}\n"
        return output
    
    def find_class(self, class_name: str) -> str:
        """Find a class."""
        classes = self.graph.find_nodes(type='Class', name=class_name)
        
        if not classes:
            return f"Class '{class_name}' not found."
        
        output = f"Found class '{class_name}':\n\n"
        for cls in classes:
            output += f"- Module: {cls.get('module', 'N/A')}\n"
        return output
    
    def get_dependency_graph(self, module_name: str) -> str:
        """Get dependency graph."""
        module_id = f"module:{module_name}"
        deps = self.graph.get_outgoing(module_id, 'DEPENDS_ON')
        dependents = self.graph.get_incoming(module_id, 'DEPENDS_ON')
        
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
    
    def stats(self) -> str:
        """Get graph statistics."""
        s = self.graph.stats()
        output = f"""Graph Statistics:

- Total Modules: {s['modules']}
  - Business Modules: {s['business_modules']}
  - Regular Modules: {s['regular_modules']}
- Functions: {s['functions']}
- Methods: {s['methods']}
- Classes: {s['classes']}
- Total Nodes: {s['nodes']}
- Total Edges: {s['edges']}
"""
        return output


def main():
    """Interactive query interface."""
    if len(sys.argv) < 2:
        print("Usage: cartographer_query.py <repo_path> [--java|--python|--all] [command] [args...]")
        print("\nOptions:")
        print("  --java      - Analyze Java files only")
        print("  --python    - Analyze Python files only (default)")
        print("  --all       - Analyze both Python and Java files")
        print("\nCommands:")
        print("  list-modules              - List all modules")
        print("  list-functions            - List all functions")
        print("  list-classes              - List all classes")
        print("  get-module <name>         - Get module contents")
        print("  get-deps <name>           - Get module dependencies")
        print("  find-function <name>      - Find a function")
        print("  find-class <name>         - Find a class")
        print("  dep-graph <name>          - Get dependency graph")
        print("  stats                     - Get graph statistics")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    # Parse file extension option
    file_ext = '.py,.java'  # Default: analyze both
    next_arg_idx = 2
    
    if len(sys.argv) > 2 and sys.argv[2].startswith('--'):
        option = sys.argv[2]
        if option == '--java':
            file_ext = '.java'
        elif option == '--python':
            file_ext = '.py'
        elif option == '--all':
            file_ext = '.py,.java'
        next_arg_idx = 3
    
    query = CartographerQuery(repo_path, file_ext=file_ext)
    
    if len(sys.argv) <= next_arg_idx:
        # Interactive mode
        print_help()
        while True:
            try:
                cmd = input("\n> ").strip()
                if not cmd:
                    continue
                if cmd == 'quit' or cmd == 'exit':
                    break
                result = execute_command(query, cmd)
                print(result)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Command mode
        cmd = " ".join(sys.argv[next_arg_idx:])
        result = execute_command(query, cmd)
        print(result)


def print_help():
    """Print help message."""
    print("""Cartographer Graph Query Tool
    
Available commands:
  list-modules              - List all modules
  list-functions            - List all functions  
  list-classes              - List all classes
  get-module <name>         - Get module contents
  get-deps <name>           - Get module dependencies
  find-function <name>      - Find a function
  find-class <name>         - Find a class
  dep-graph <name>          - Get dependency graph
  stats                     - Get graph statistics
  help                      - Show this help
  quit/exit                 - Exit
""")


def execute_command(query: CartographerQuery, cmd: str) -> str:
    """Execute a command."""
    parts = cmd.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else None
    
    if command == 'help':
        print_help()
        return ""
    elif command == 'stats':
        return query.stats()
    elif command == 'list-modules':
        return query.list_modules()
    elif command == 'list-functions':
        return query.list_functions()
    elif command == 'list-classes':
        return query.list_classes()
    elif command == 'get-module':
        if not args:
            return "Error: module name required"
        return query.get_module_contents(args)
    elif command == 'get-deps':
        if not args:
            return "Error: module name required"
        return query.get_module_dependencies(args)
    elif command == 'find-function':
        if not args:
            return "Error: function name required"
        return query.find_function(args)
    elif command == 'find-class':
        if not args:
            return "Error: class name required"
        return query.find_class(args)
    elif command == 'dep-graph':
        if not args:
            return "Error: module name required"
        return query.get_dependency_graph(args)
    else:
        return f"Unknown command: {command}. Type 'help' for available commands."


if __name__ == "__main__":
    main()
