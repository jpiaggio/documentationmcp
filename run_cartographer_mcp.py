#!/usr/bin/env python3
"""
Helper script to load cartographer results into the in-memory graph and start the MCP server.
"""

import subprocess
import json
import sys
import argparse
from pathlib import Path

def cartographer_to_json(repo_path: str) -> str:
    """Convert cartographer output to JSON format."""
    print(f"Running cartographer agent on {repo_path}...", file=sys.stderr)
    
    result = subprocess.run(
        ["/opt/homebrew/bin/python3.10", "agents/cartographer_agent.py", repo_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running cartographer agent: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    # Parse stderr and stdout
    lines = result.stderr.split('\n') + result.stdout.split('\n')
    
    # Extract info
    modules = {}
    cypher_statements = [l.strip() for l in lines if l.startswith('MERGE')]
    
    print(f"Found {len(cypher_statements)} Cypher statements", file=sys.stderr)
    
    # Simple parsing of Cypher statements to build JSON
    import re
    
    for stmt in cypher_statements:
        # Parse module creation: MERGE (m:Module {name: '...', path: '...'})
        module_match = re.search(r"\(m:Module\s*\{([^}]+)\}\)", stmt)
        if module_match:
            props_str = module_match.group(1)
            props = {}
            for match in re.finditer(r"(\w+):\s*'([^']*)'", props_str):
                props[match.group(1)] = match.group(2)
            
            module_name = props.get('name')
            if module_name:
                if module_name not in modules:
                    modules[module_name] = {
                        'name': module_name,
                        'path': props.get('path', ''),
                        'functions': [],
                        'classes': [],
                        'dependencies': []
                    }
        
        # Parse function/class creation
        item_match = re.search(r"\(n:(\w+)\s*\{([^}]+)\}\)", stmt)
        if item_match:
            item_type = item_match.group(1)
            props_str = item_match.group(2)
            props = {}
            for match in re.finditer(r"(\w+):\s*'([^']*)'", props_str):
                props[match.group(1)] = match.group(2)
            
            item_name = props.get('name')
            module_name = props.get('module')
            
            if module_name and item_name:
                if module_name in modules:
                    if item_type == 'Function':
                        if item_name not in [f['name'] for f in modules[module_name]['functions']]:
                            modules[module_name]['functions'].append({'name': item_name})
                    elif item_type == 'Class':
                        if item_name not in [c['name'] for c in modules[module_name]['classes']]:
                            modules[module_name]['classes'].append({'name': item_name})
        
        # Parse dependencies
        dep_match = re.search(r"\(dep:Module\s*\{name:\s*'([^']+)'\}\)", stmt)
        if dep_match:
            dep_name = dep_match.group(1)
            # Find which module has this dependency
            module_match = re.search(r"\(m:Module\s*\{([^}]+)\}\)", stmt)
            if module_match:
                props_str = module_match.group(1)
                for match in re.finditer(r"(\w+):\s*'([^']*)'", props_str):
                    if match.group(1) == 'name':
                        module_name = match.group(2)
                        if module_name in modules:
                            if dep_name not in modules[module_name]['dependencies']:
                                modules[module_name]['dependencies'].append(dep_name)
    
    # Convert to JSON
    data = {
        'modules': list(modules.values())
    }
    
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Load cartographer results into the in-memory graph MCP"
    )
    parser.add_argument("repo_path", help="Path to the repository to analyze")
    
    args = parser.parse_args()
    
    # Generate JSON from cartographer
    json_data = cartographer_to_json(args.repo_path)
    
    print(f"\nStarting MCP server with loaded data...", file=sys.stderr)
    
    # For now, we'll just print the JSON that can be loaded
    print("\n" + "="*60)
    print("JSON Data (can be loaded with load_cartographer_data tool):")
    print("="*60)
    print(json_data)
    print("="*60 + "\n")
    
    # Start the MCP server
    subprocess.run(["/opt/homebrew/bin/python3.10", "mcp_cartographer_server.py", "stdio"])


if __name__ == "__main__":
    main()
