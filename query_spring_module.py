#!/usr/bin/env python3
"""
Query business rules and semantic information about a Java Spring Framework module.
Analyzes Java class structure, methods, and annotations.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Set

def extract_java_class_info(source: str) -> Dict:
    """Extract Java class information including annotations, methods, and fields."""
    
    # Find class declaration
    class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\S+))?(?:\s+implements\s+(\S+))?'
    class_match = re.search(class_pattern, source)
    
    if not class_match:
        return {}
    
    class_info = {
        'name': class_match.group(1),
        'extends': class_match.group(2) or None,
        'implements': class_match.group(3) or None,
        'annotations': [],
        'methods': [],
        'fields': [],
        'javadoc': ''
    }
    
    # Extract javadoc comment before class
    javadoc_pattern = r'/\*\*(.*?)\*/'
    javadoc_match = re.search(javadoc_pattern, source[:class_match.start()], re.DOTALL)
    if javadoc_match:
        # Clean up javadoc
        javadoc_text = javadoc_match.group(1)
        lines = [line.strip().lstrip('*').strip() for line in javadoc_text.split('\n')]
        class_info['javadoc'] = ' '.join(filter(None, lines))
    
    # Extract class-level annotations
    annotations_pattern = r'@(\w+)(?:\([^)]*\))?'
    for match in re.finditer(annotations_pattern, source[:class_match.start()]):
        class_info['annotations'].append(match.group(1))
    
    # Extract methods
    method_pattern = r'(?:/\*\*(.*?)\*/\s*)?(?:@\w+\s*)*(?:public|protected|private)?\s+(?:static\s+)?(?:synchronized\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\((.*?)\)\s*(?:throws\s+[\w.,\s]+?)?\{'
    
    for match in re.finditer(method_pattern, source, re.DOTALL):
        javadoc = match.group(1) or ""
        return_type = match.group(2)
        method_name = match.group(3)
        params = match.group(4)
        
        # Clean javadoc
        if javadoc:
            lines = [line.strip().lstrip('*').strip() for line in javadoc.split('\n')]
            javadoc = ' '.join(filter(None, lines))
        
        class_info['methods'].append({
            'name': method_name,
            'return_type': return_type,
            'params': params.strip() if params else '',
            'javadoc': javadoc[:100] + '...' if len(javadoc) > 100 else javadoc
        })
    
    # Extract fields
    field_pattern = r'(?:public|protected|private)?\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*[=;]'
    
    for match in re.finditer(field_pattern, source):
        field_type = match.group(1)
        field_name = match.group(2)
        
        class_info['fields'].append({
            'name': field_name,
            'type': field_type
        })
    
    return class_info

def extract_imports(source: str) -> Set[str]:
    """Extract imported packages."""
    imports = set()
    import_pattern = r'^import\s+([\w\.]+(?:\.\*)?);'
    
    for line in source.split('\n'):
        match = re.match(import_pattern, line)
        if match:
            imports.add(match.group(1))
    
    return imports

def query_spring_module(file_path: str):
    """Query business rules from a Spring Framework Java module."""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Read the source
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Extract information
    class_info = extract_java_class_info(source)
    imports = extract_imports(source)
    
    if not class_info:
        print(f"❌ No Java class found in {file_path}")
        return
    
    # Display results
    print(f"\n{'='*80}")
    print(f"Spring Framework Module Analysis")
    print(f"{'='*80}\n")
    
    print(f"📦 CLASS INFORMATION:")
    print(f"{'─'*80}")
    print(f"  Class Name: {class_info['name']}")
    if class_info['extends']:
        print(f"  Extends: {class_info['extends']}")
    if class_info['implements']:
        print(f"  Implements: {class_info['implements']}")
    
    if class_info['annotations']:
        print(f"  Annotations: {', '.join(class_info['annotations'])}")
    
    if class_info['javadoc']:
        print(f"\n  📝 Description:")
        for line in class_info['javadoc'].split('\n'):
            print(f"     {line}")
    
    # Display fields
    if class_info['fields']:
        print(f"\n🔧 FIELDS (Properties):")
        print(f"{'─'*80}")
        for field in class_info['fields']:
            print(f"  {field['type']:20} {field['name']}")
    
    # Display methods
    if class_info['methods']:
        print(f"\n⚙️  METHODS (Business Operations):")
        print(f"{'─'*80}")
        
        # Categorize methods
        constructors = [m for m in class_info['methods'] if m['name'] == class_info['name']]
        regular_methods = [m for m in class_info['methods'] if m['name'] != class_info['name']]
        
        if constructors:
            print(f"\n  Constructors:")
            for method in constructors:
                params_display = method['params'][:40] + '...' if len(method['params']) > 40 else method['params']
                print(f"    • {method['name']}({params_display})")
                if method['javadoc']:
                    print(f"      {method['javadoc']}")
        
        if regular_methods:
            print(f"\n  Methods:")
            for method in regular_methods[:15]:  # Show first 15
                params_display = method['params'][:40] + '...' if len(method['params']) > 40 else method['params']
                print(f"    • {method['return_type']} {method['name']}({params_display})")
                if method['javadoc']:
                    print(f"      {method['javadoc']}")
            
            if len(regular_methods) > 15:
                print(f"\n    ... and {len(regular_methods) - 15} more methods")
    
    # Display imports
    spring_imports = [imp for imp in imports if 'springframework' in imp or 'org.springframework' in imp]
    other_imports = [imp for imp in imports if 'springframework' not in imp and 'org.springframework' not in imp]
    
    if spring_imports or other_imports:
        print(f"\n📚 DEPENDENCIES:")
        print(f"{'─'*80}")
        
        if spring_imports:
            print(f"\n  Spring Framework Dependencies:")
            for imp in sorted(spring_imports)[:10]:
                print(f"    • {imp}")
            if len(spring_imports) > 10:
                print(f"    ... and {len(spring_imports) - 10} more")
        
        if other_imports:
            print(f"\n  External Libraries:")
            external = [i for i in other_imports if not i.startswith('java.')]
            for imp in sorted(external)[:10]:
                print(f"    • {imp}")
            if len(external) > 10:
                print(f"    ... and {len(external) - 10} more")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"{'─'*80}")
    print(f"  File: {file_path.name}")
    print(f"  Total Methods: {len(class_info['methods'])}")
    print(f"  Total Fields: {len(class_info['fields'])}")
    print(f"  Spring Dependencies: {len(spring_imports)}")
    print(f"  External Dependencies: {len(other_imports)}")
    
    # Infer purpose
    print(f"\n💼 INFERRED BUSINESS PURPOSE:")
    print(f"{'─'*80}")
    
    class_name = class_info['name']
    if 'Handler' in class_name:
        print(f"  • Handles HTTP requests and responses")
    if 'Controller' in class_name:
        print(f"  • Manages request routing and response generation")
    if 'Service' in class_name:
        print(f"  • Provides business logic and operations")
    if 'Repository' in class_name:
        print(f"  • Manages data persistence and retrieval")
    if 'Config' in class_name:
        print(f"  • Configures Spring application components")
    if 'Mapper' in class_name:
        print(f"  • Maps between different data models")
    if 'Converter' in class_name or 'Adapter' in class_name:
        print(f"  • Converts or adapts between different formats")
    if 'Exception' in class_name or 'Error' in class_name:
        print(f"  • Handles error conditions and exceptions")
    if 'Factory' in class_name:
        print(f"  • Creates instances of related classes")
    
    # Business actions
    action_methods = {}
    for method in class_info['methods']:
        name_lower = method['name'].lower()
        if 'get' in name_lower or 'find' in name_lower or 'query' in name_lower:
            key = '🔍 Retrieve/Query'
        elif 'set' in name_lower or 'update' in name_lower:
            key = '✏️  Modify/Update'
        elif 'add' in name_lower or 'create' in name_lower or 'save' in name_lower:
            key = '➕ Create/Insert'
        elif 'remove' in name_lower or 'delete' in name_lower:
            key = '❌ Delete/Remove'
        elif 'handle' in name_lower or 'process' in name_lower:
            key = '⚙️  Process/Handle'
        elif 'validate' in name_lower or 'check' in name_lower:
            key = '✓ Validate/Check'
        else:
            continue
        
        if key not in action_methods:
            action_methods[key] = []
        action_methods[key].append(method['name'])
    
    if action_methods:
        print(f"\n  Operations by type:")
        for action, methods in sorted(action_methods.items()):
            print(f"    {action}")
            for method in methods[:3]:
                print(f"      - {method}()")
            if len(methods) > 3:
                print(f"      ... and {len(methods) - 3} more")
    
    print(f"\n{'='*80}\n")


def main():
    if len(sys.argv) < 2:
        print("Query Business Rules from a Spring Framework Java Module")
        print("\nUsage: python query_spring_module.py <path/to/Module.java>")
        print("\nExamples:")
        print("  python query_spring_module.py /path/to/spring-framework/spring-webflux/src/main/java/org/springframework/web/reactive/BindingContext.java")
        print("  python query_spring_module.py /path/to/spring-framework/spring-core/src/main/java/org/springframework/core/io/Resource.java")
        sys.exit(1)
    
    file_path = sys.argv[1]
    query_spring_module(file_path)


if __name__ == "__main__":
    main()
