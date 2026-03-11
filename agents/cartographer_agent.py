import os
import sys
import concurrent.futures

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from business_rules_extractor import BusinessRulesExtractor, generate_business_cypher

# Load the Python and Java grammars for tree-sitter
print("Initializing tree-sitter...", file=sys.stderr)

try:
    # Try to load tree-sitter-python first
    from tree_sitter_python import language as get_python_language
    from tree_sitter import Parser, Language
    
    # Get the Python language PyCapsule and wrap in Language object
    python_language_capsule = get_python_language()
    print(f"Python language capsule type: {type(python_language_capsule)}", file=sys.stderr)
    
    PY_LANGUAGE = Language(python_language_capsule)
    print("Using tree-sitter-python language", file=sys.stderr)
    has_python = True
    # Create Python parser
    python_parser = Parser()
    python_parser.language = PY_LANGUAGE
    
except Exception as e:
    print(f"Warning: Could not import tree-sitter-python: {e}", file=sys.stderr)
    has_python = False
    python_parser = None

# Try to load Java language
try:
    from tree_sitter_java import language as get_java_language
    from tree_sitter import Language
    
    java_language_capsule = get_java_language()
    JAVA_LANGUAGE = Language(java_language_capsule)
    print("Using tree-sitter-java language", file=sys.stderr)
    has_java = True
    # Create Java parser
    java_parser = Parser()
    java_parser.language = JAVA_LANGUAGE
except Exception as e:
    print(f"Warning: Could not import tree-sitter-java: {e}", file=sys.stderr)
    has_java = False
    java_parser = None

# Initialize business rules extractor
business_extractor = BusinessRulesExtractor()

# Functions for language detection
def get_language_for_file(filepath):
    """Determine language based on file extension."""
    if filepath.endswith('.java'):
        return 'java' if has_java else None
    elif filepath.endswith('.py'):
        return 'python' if has_python else None
    return None

def get_parser(language):
    """Get the parser for the specified language."""
    if language == 'java':
        return java_parser
    elif language == 'python':
        return python_parser
    return python_parser  # Default to Python parser

def parse_code(source_code, language='python'):
    """Parse code using the appropriate parser for the language."""
    parser = get_parser(language)
    if parser is None:
        raise RuntimeError(f"Parser not available for language: {language}")
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    return root_node

def extract_functions_and_classes(root_node, source_code, language='python'):
    """Extract functions and classes from code. Supports Python and Java."""
    results = []
    cursor = root_node.walk()
    
    # Define node types based on language
    if language == 'java':
        class_types = ('class_declaration', 'interface_declaration', 'enum_declaration')
        method_types = ('method_declaration', 'constructor_declaration')
        name_field = 'name'
    else:  # python
        class_types = ('class_definition',)
        method_types = ('function_definition',)
        name_field = 'name'
    
    # Walk the tree using recursion
    visited = set()
    def walk_tree(node):
        if id(node) in visited:
            return
        visited.add(id(node))
        
        if language == 'java':
            # For Java: methods and classes
            if node.type in class_types:
                name_node = node.child_by_field_name(name_field)
                if name_node:
                    name = source_code[name_node.start_byte:name_node.end_byte]
                    results.append({
                        'type': node.type,
                        'name': name,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1
                    })
            elif node.type in method_types:
                name_node = node.child_by_field_name(name_field)
                if name_node:
                    name = source_code[name_node.start_byte:name_node.end_byte]
                    results.append({
                        'type': 'method_declaration',
                        'name': name,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1
                    })
        else:
            # For Python: functions and classes
            if node.type in ('function_definition', 'class_definition'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    name = source_code[name_node.start_byte:name_node.end_byte]
                    results.append({
                        'type': node.type,
                        'name': name,
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1
                    })
        
        for child in node.children:
            walk_tree(child)
    
    walk_tree(root_node)
    return results

def extract_imports(root_node, source_code, language='python'):
    """Extract imports from code. Supports Python and Java."""
    imports = []
    visited = set()
    
    def walk_tree(node):
        if id(node) in visited:
            return
        visited.add(id(node))
        
        if language == 'java':
            if node.type == 'import_declaration':
                import_text = source_code[node.start_byte:node.end_byte]
                imports.append(import_text)
        else:  # python
            if node.type in ('import_statement', 'import_from_statement'):
                import_text = source_code[node.start_byte:node.end_byte]
                imports.append(import_text)
        
        for child in node.children:
            walk_tree(child)
    
    walk_tree(root_node)
    return imports

def generate_cypher(module_path, functions_classes, imports):
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    cypher_statements = []
    # Module node
    cypher_statements.append(
        f"MERGE (m:Module {{name: '{module_name}', path: '{module_path}'}})"
    )
    # Function/Class nodes
    for item in functions_classes:
        # Map node types to labels
        node_type = item['type']
        if node_type in ('function_definition',):
            label = 'Function'
        elif node_type in ('method_declaration', 'constructor_declaration'):
            label = 'Method'
        elif node_type in ('class_definition', 'class_declaration', 'interface_declaration', 'enum_declaration'):
            label = 'Class'
        else:
            label = 'Function'  # Default
        
        cypher_statements.append(
            f"MERGE (n:{label} {{name: '{item['name']}', module: '{module_name}'}}) "
            f"MERGE (m)-[:CONTAINS]->(n)"
        )
    # Imports as DEPENDS_ON edges
    for imp in imports:
        # Naive extraction of module name from import statement
        tokens = imp.replace('import', '').replace('from', '').replace('as', '').split()
        if tokens:
            dep_module = tokens[0].split('.')[0]
            if dep_module != module_name:
                cypher_statements.append(
                    f"MERGE (dep:Module {{name: '{dep_module}'}}) "
                    f"MERGE (m)-[:DEPENDS_ON]->(dep)"
                )
    return cypher_statements

def process_module(module_path, language='python', use_business_rules=True):
    """Process a single module file for business insights (Python or Java)."""
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Error reading {module_path}: {e}", file=sys.stderr)
        return []
    
    try:
        # Extract business-level insights
        if use_business_rules:
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            insights = business_extractor.extract_all_business_insights(source_code, module_path)
            cypher = generate_business_cypher(insights, module_name, module_path)
            return cypher
        else:
            # Fallback to technical analysis
            root_node = parse_code(source_code, language)
            functions_classes = extract_functions_and_classes(root_node, source_code, language)
            imports = extract_imports(root_node, source_code, language)
            cypher = generate_cypher(module_path, functions_classes, imports)
            return cypher
    except Exception as e:
        print(f"Error processing {module_path}: {e}", file=sys.stderr)
        return []

def cartographer_agent(repo_root, file_ext='.py', max_workers=8, use_business_rules=True):
    """Process repository files and generate insights.
    
    Args:
        repo_root: Path to repository root
        file_ext: File extension to scan for ('.py' or '.java', or '.py,.java' for both)
        max_workers: Number of parallel workers
        use_business_rules: If True, extract business insights; if False, technical analysis
    """
    from functools import partial
    
    cypher_queries = []
    module_paths_with_lang = []
    
    # Determine which extensions to scan for
    extensions = []
    if ',' in file_ext:
        extensions = [ext.strip() for ext in file_ext.split(',')]
    else:
        extensions = [file_ext]
    
    # Walk repository and collect files
    for root, _, files in os.walk(repo_root):
        for file in files:
            for ext in extensions:
                if file.endswith(ext):
                    filepath = os.path.join(root, file)
                    # Determine language based on extension
                    lang = 'python' if ext == '.py' else 'java' if ext == '.java' else 'python'
                    module_paths_with_lang.append((filepath, lang))
                    break
    
    # Process files with ThreadPoolExecutor, passing language and business_rules parameters
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create partial functions with parameters for each file
        tasks = [partial(process_module, path, language, use_business_rules) for path, language in module_paths_with_lang]
        results = list(executor.map(lambda task: task(), tasks))
        for cypher_list in results:
            cypher_queries.extend(cypher_list)
    
    return cypher_queries

# Main execution
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python cartographer_agent.py <repo_path> [--technical]", file=sys.stderr)
        print("  --technical: Use technical analysis instead of business rules", file=sys.stderr)
        sys.exit(1)
    
    repo_path = sys.argv[1]
    use_business = '--technical' not in sys.argv
    
    print(f"Scanning repository: {repo_path}", file=sys.stderr)
    print(f"Mode: {'Business Rules Extraction' if use_business else 'Technical Analysis'}", file=sys.stderr)
    
    try:
        cypher_statements = cartographer_agent(repo_path, use_business_rules=use_business)
        print(f"Generated {len(cypher_statements)} insights", file=sys.stderr)
        
        for stmt in cypher_statements:
            print(stmt)
    except Exception as e:
        print(f"Error processing repository: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)