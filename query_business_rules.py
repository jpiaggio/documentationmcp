#!/usr/bin/env python3
"""
Query business logic and semantic information about a module.
Analyzes method signatures, docstrings, and code patterns to understand business rules.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Set

def extract_module_source(file_path: str) -> str:
    """Read the actual source code of a module."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def extract_function_info(source: str) -> List[Dict]:
    """Extract function/method signatures and docstrings."""
    functions = []
    
    # Pattern for Python function definitions
    func_pattern = r'def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?\s*:'
    
    for match in re.finditer(func_pattern, source):
        func_name = match.group(1)
        params = match.group(2)
        
        # Get docstring if present
        start_pos = match.end()
        docstring = ""
        
        # Look for docstring following the function definition
        docstring_match = re.search(r'^\s*"""(.*?)"""', source[start_pos:], re.DOTALL | re.MULTILINE)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
        
        functions.append({
            'name': func_name,
            'params': params.strip(),
            'docstring': docstring,
            'signature': f"{func_name}({params})"
        })
    
    return functions

def extract_class_info(source: str) -> List[Dict]:
    """Extract class definitions and docstrings."""
    classes = []
    
    # Pattern for Python class definitions
    class_pattern = r'class\s+(\w+)(?:\((.*?)\))?\s*:'
    
    for match in re.finditer(class_pattern, source):
        class_name = match.group(1)
        base_classes = match.group(2) or ""
        
        # Get docstring if present
        start_pos = match.end()
        docstring = ""
        
        docstring_match = re.search(r'^\s*"""(.*?)"""', source[start_pos:], re.DOTALL | re.MULTILINE)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
        
        classes.append({
            'name': class_name,
            'bases': base_classes.strip(),
            'docstring': docstring
        })
    
    return classes

def extract_imports(source: str) -> Set[str]:
    """Extract imported modules to understand dependencies."""
    imports = set()
    
    # Standard imports
    import_pattern = r'^(?:from\s+(\S+)|import\s+(\S+))'
    
    for line in source.split('\n'):
        match = re.match(import_pattern, line)
        if match:
            module = match.group(1) or match.group(2)
            imports.add(module.split('.')[0].split(',')[0].strip())
    
    return imports

def query_module_business_rules(repo_path: str, module_name: str):
    """Query business rules and semantic information about a module."""
    
    # Find the module file
    module_file = None
    repo_path = Path(repo_path)
    
    # Try different extensions
    for ext in ['.py', '.java']:
        potential_file = repo_path / f"{module_name}{ext}"
        if potential_file.exists():
            module_file = str(potential_file)
            break
    
    if not module_file:
        # Search for the file
        for py_file in repo_path.rglob(f"{module_name}.py"):
            module_file = str(py_file)
            break
    
    if not module_file:
        print(f"❌ Module '{module_name}' not found in {repo_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"Module: {module_name}")
    print(f"File: {module_file}")
    print(f"{'='*70}\n")
    
    # Read and analyze the module
    source = extract_module_source(module_file)
    
    if not source:
        print(f"❌ Could not read module source")
        return
    
    # Extract information
    classes = extract_class_info(source)
    functions = extract_function_info(source)
    imports = extract_imports(source)
    
    # Display class information
    if classes:
        print("📚 CLASSES (Business Models & Entities):")
        print("-" * 70)
        for cls in classes:
            print(f"\n  Class: {cls['name']}")
            if cls['bases']:
                print(f"  Inherits: {cls['bases']}")
            if cls['docstring']:
                print(f"  Description: {cls['docstring']}")
        print()
    
    # Display function information
    if functions:
        print("\n⚙️  FUNCTIONS & METHODS (Business Operations):")
        print("-" * 70)
        for func in functions:
            print(f"\n  Function: {func['signature']}")
            if func['docstring']:
                print(f"  Purpose: {func['docstring']}")
            else:
                print(f"  Purpose: (No documentation)")
        print()
    
    # Display imports (external dependencies that influence business logic)
    if imports:
        print("\n📦 EXTERNAL DEPENDENCIES (Libraries used for business logic):")
        print("-" * 70)
        external_deps = [m for m in sorted(imports) if m not in ['os', 'sys', '__future__']]
        for dep in external_deps:
            print(f"  - {dep}")
        print()
    
    # Summary statistics
    print("\n📊 SUMMARY:")
    print("-" * 70)
    print(f"  Total Classes: {len(classes)}")
    print(f"  Total Functions/Methods: {len(functions)}")
    print(f"  External Dependencies: {len([m for m in imports if m not in ['os', 'sys']])}")
    
    # Infer business logic based on method names
    print("\n💼 INFERRED BUSINESS LOGIC:")
    print("-" * 70)
    
    action_keywords = {
        'get': '🔍 Retrieve/Query',
        'set': '✏️  Modify/Update',
        'add': '➕ Create/Insert',
        'remove': '❌ Delete/Remove',
        'process': '⚙️  Transform/Process',
        'validate': '✓ Validate/Check',
        'load': '📥 Load/Initialize',
        'save': '💾 Persist/Save',
        'parse': '📖 Parse/Analyze',
        'generate': '✨ Generate/Create'
    }
    
    pattern_count = {}
    for func in functions:
        func_lower = func['name'].lower()
        for keyword, description in action_keywords.items():
            if keyword in func_lower:
                if description not in pattern_count:
                    pattern_count[description] = []
                pattern_count[description].append(func['name'])
    
    if pattern_count:
        for pattern, funcs in sorted(pattern_count.items()):
            print(f"  {pattern}:")
            for func in funcs[:3]:  # Show first 3
                print(f"    - {func}()")
            if len(funcs) > 3:
                print(f"    ... and {len(funcs)-3} more")
    else:
        print("  (No clear business logic patterns detected in method names)")


def main():
    if len(sys.argv) < 3:
        print("Query Business Rules and Semantic Information from a Module")
        print("\nUsage: python query_business_rules.py <repo_path> <module_name>")
        print("\nExamples:")
        print("  python query_business_rules.py . cartographer_agent")
        print("  python query_business_rules.py . mcp_cartographer_server")
        print("  python query_business_rules.py /path/to/repo cartographer_query")
        print("\nOutput includes:")
        print("  - Class definitions and inheritance")
        print("  - Method signatures and docstrings")
        print("  - External dependencies")
        print("  - Inferred business logic patterns")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    module_name = sys.argv[2]
    
    query_module_business_rules(repo_path, module_name)


if __name__ == "__main__":
    main()
