#!/usr/bin/env python3
"""Find and query Spring Framework modules"""

import sys
import subprocess
from pathlib import Path

def find_spring_modules(search_term: str = None, limit: int = 10) -> list:
    """Find Spring Framework main source Java files."""
    spring_root = Path("/Users/juani/github-projects/spring-framework/spring-framework")
    
    results = []
    counter = 0
    
    for java_file in spring_root.glob("*/src/main/java/**/*.java"):
        if counter >= limit:
            break
        
        # Skip test files and package-info
        if "test" in str(java_file) or "package-info" in java_file.name:
            continue
        
        if search_term and search_term.lower() not in java_file.name.lower():
            continue
        
        results.append(java_file)
        counter += 1
    
    return results

def main():
    if len(sys.argv) > 1:
        search_term = sys.argv[1]
    else:
        search_term = None
    
    print("Finding Spring Framework modules...")
    modules = find_spring_modules(search_term=search_term, limit=15)
    
    if not modules:
        print(f"No modules found matching: {search_term}")
        return
    
    print(f"\n✨ Found {len(modules)} Spring Framework modules:\n")
    
    for i, module in enumerate(modules, 1):
        # Get the class name
        class_name = module.stem
        # Get the relative path
        rel_path = module.relative_to(module.parents[5])  # Get relative to spring-framework
        
        print(f"{i}. {class_name}")
        print(f"   Path: {rel_path}")
        print(f"   Full: {module}")
        print()
    
    if search_term:
        print(f"💡 Tip: To analyze a module, run:")
        print(f"   python query_spring_module.py \"{modules[0]}\"")
    else:
        print(f"💡 Tip: Search for specific modules:")
        print(f"   python find_spring_modules.py Handler")
        print(f"   python find_spring_modules.py Controller")
        print(f"   python find_spring_modules.py Service")

if __name__ == "__main__":
    main()
