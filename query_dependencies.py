#!/usr/bin/env python3
"""Module dependency query tool for Cartographer"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Set

def get_module_dependencies(repo_path: str, module_name: str) -> Dict[str, Set[str]]:
    """
    Get all dependencies for a specific module.
    
    Args:
        repo_path: Path to repository to analyze
        module_name: Name of the module to query (e.g., 'cartographer_agent')
    
    Returns:
        Dictionary with 'dependencies' and 'dependents' sets
    """
    # Run cartographer agent to get Cypher statements
    result = subprocess.run(
        [sys.executable, "agents/cartographer_agent.py", repo_path],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    if result.returncode != 0:
        print(f"Error running cartographer agent: {result.stderr}")
        return {"dependencies": set(), "dependents": set()}
    
    lines = result.stdout.split('\n') + result.stderr.split('\n')
    cypher_stmts = [l.strip() for l in lines if l.strip().startswith('MERGE')]
    
    # Parse Cypher statements to find dependencies
    # Track which module we're currently processing
    current_module = None
    module_deps = {}  # module_name -> set of dependencies
    
    for stmt in cypher_stmts:
        # Check if this statement defines a module
        if "MERGE (m:Module {" in stmt:
            # Extract module name
            try:
                start = stmt.find("name: '") + 7
                end = stmt.find("'", start)
                current_module = stmt[start:end]
                if current_module not in module_deps:
                    module_deps[current_module] = set()
            except:
                current_module = None
        
        # Check if this is a dependency statement with current module
        elif current_module and '-[:DEPENDS_ON]->' in stmt:
            try:
                # Extract dependency module name
                start = stmt.find("name: '") + 7
                end = stmt.find("'", start)
                dependency = stmt[start:end]
                if dependency and dependency != current_module:
                    module_deps[current_module].add(dependency)
            except:
                pass
    
    # Get dependencies and dependents for the requested module
    dependencies = module_deps.get(module_name, set())
    
    # Find modules that depend on our target module
    dependents = set()
    for mod, deps in module_deps.items():
        if module_name in deps and mod != module_name:
            dependents.add(mod)
    
    return {
        "dependencies": dependencies,
        "dependents": dependents,
        "module": module_name
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python query_dependencies.py <repo_path> <module_name>")
        print("\nExamples:")
        print("  python query_dependencies.py . mcp_cartographer_server")
        print("  python query_dependencies.py . cartographer_agent")
        print("  python query_dependencies.py /path/to/repo run_cartographer_mcp")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    module_name = sys.argv[2]
    
    print(f"\nQuerying dependencies for: {module_name}")
    print(f"Repository: {repo_path}")
    print("-" * 70)
    
    result = get_module_dependencies(repo_path, module_name)
    dependencies = result["dependencies"]
    dependents = result["dependents"]
    
    # Display dependencies
    if dependencies:
        print(f"\n✅ Modules that '{module_name}' DEPENDS ON:\n")
        for dep in sorted(dependencies):
            print(f"  → {dep}")
        print(f"\nTotal: {len(dependencies)} dependencies")
    else:
        print(f"\n❌ '{module_name}' has no external dependencies")
    
    # Display dependents
    if dependents:
        print(f"\n✅ Modules that DEPEND ON '{module_name}':\n")
        for dep in sorted(dependents):
            print(f"  ← {dep}")
        print(f"\nTotal: {len(dependents)} dependents")
    else:
        print(f"\n❌ No modules depend on '{module_name}'")


if __name__ == "__main__":
    main()

