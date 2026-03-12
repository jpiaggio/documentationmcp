import os
import sys
import concurrent.futures
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from business_rules_extractor import BusinessRulesExtractor, generate_business_cypher

# Multi-language analyzer support
try:
    from multi_language_analyzer import MultiLanguageAnalyzer
    HAS_MULTI_LANG = True
except ImportError as e:
    print(f"Warning: multi_language_analyzer not available: {e}", file=sys.stderr)
    HAS_MULTI_LANG = False
    MultiLanguageAnalyzer = None

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

def get_language_for_file(filepath):
    """Determine language based on file extension."""
    ext = Path(filepath).suffix.lower()
    if ext == '.java':
        return 'java' if has_java else None
    elif ext == '.py':
        return 'python' if has_python else None
    # New language support
    elif ext in ('.js', '.jsx', '.mjs'):
        return 'javascript'
    elif ext in ('.ts', '.tsx'):
        return 'typescript'
    elif ext == '.go':
        return 'go'
    elif ext == '.cs':
        return 'csharp'
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
    """Process a single module file for business insights.
    
    Supports: Python, Java, JavaScript, TypeScript, Go, C#
    """
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Error reading {module_path}: {e}", file=sys.stderr)
        return []
    
    try:
        # For Python/Java with business rules, use existing extractor
        if use_business_rules and language in ('python', 'java'):
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            insights = business_extractor.extract_all_business_insights(source_code, module_path)
            cypher = generate_business_cypher(insights, module_name, module_path)
            return cypher
        
        # For new languages, use multi-language analyzer
        elif language in ('javascript', 'typescript', 'go', 'csharp') and HAS_MULTI_LANG:
            return process_module_multi_lang(module_path, language)
        
        else:
            # Fallback to technical analysis for Python/Java
            root_node = parse_code(source_code, language)
            functions_classes = extract_functions_and_classes(root_node, source_code, language)
            imports = extract_imports(root_node, source_code, language)
            cypher = generate_cypher(module_path, functions_classes, imports)
            return cypher
            
    except Exception as e:
        print(f"Error processing {module_path}: {e}", file=sys.stderr)
        return []


def process_module_multi_lang(module_path, language):
    """Process a module using the multi-language analyzer.
    
    Generates Cypher queries from the analysis results.
    """
    try:
        analyzer = MultiLanguageAnalyzer()
        analysis = analyzer.analyze_file(module_path)
        
        if 'error' in analysis:
            print(f"Error analyzing {module_path}: {analysis['error']}", file=sys.stderr)
            return []
        
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        cypher_statements = []
        
        # Module node
        cypher_statements.append(
            f"MERGE (m:Module {{name: '{module_name}', path: '{module_path}', language: '{language}'}})"
        )
        
        # Entity nodes
        entities = analysis.get('entities', [])
        for entity in entities:
            entity_type = entity.get('type', 'unknown').title()
            entity_name = entity.get('name', '').replace("'", "''")
            
            cypher_statements.append(
                f"MERGE (n:{entity_type} {{name: '{entity_name}', module: '{module_name}', language: '{language}'}}) "
                f"MERGE (m)-[:CONTAINS]->(n)"
            )
        
        # Dependencies
        imports = analysis.get('imports', [])
        dependencies = analysis.get('dependencies', [])
        
        for dep in dependencies:
            dep_module = dep.replace("'", "''")
            cypher_statements.append(
                f"MERGE (dep:Module {{name: '{dep_module}', language: '{language}'}}) "
                f"MERGE (m)-[:DEPENDS_ON]->(dep)"
            )
        
        return cypher_statements
        
    except Exception as e:
        print(f"Error in multi-language processing of {module_path}: {e}", file=sys.stderr)
        return []

def cartographer_agent(repo_root, file_ext='.py', max_workers=8, use_business_rules=True):
    """Process repository files and generate insights.
    
    Supports multiple languages: Python, Java, JavaScript, TypeScript, Go, C#
    
    Args:
        repo_root: Path to repository root
        file_ext: File extensions to scan for:
                  '.py' (default), '.java', '.js', '.ts', '.go', '.cs'
                  or comma-separated like '.py,.java,.js'
                  or 'all' to detect all supported types
        max_workers: Number of parallel workers
        use_business_rules: If True, extract business insights; if False, technical analysis
    """
    from functools import partial
    
    cypher_queries = []
    module_paths_with_lang = []
    
    # Determine which extensions to scan for
    extensions = []
    
    if file_ext.lower() == 'all':
        # Support all languages
        extensions = ['.py', '.java', '.js', '.jsx', '.mjs', '.ts', '.tsx', '.go', '.cs']
    elif ',' in file_ext:
        extensions = [ext.strip() for ext in file_ext.split(',')]
    else:
        extensions = [file_ext]
    
    # Normalize extensions
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    print(f"Scanning for extensions: {', '.join(extensions)}", file=sys.stderr)
    
    # Walk repository and collect files
    for root, _, files in os.walk(repo_root):
        # Skip common non-code directories
        skip_dirs = {
            '.git', '.svn', 'node_modules', '__pycache__', '.venv',
            '.env', 'dist', 'build', 'target', 'bin', 'obj', '.gradle',
            'vendor', 'packages', '.nuget', 'bower_components'
        }
        
        for file in files:
            file_ext_lower = Path(file).suffix.lower()
            
            if file_ext_lower in extensions:
                filepath = os.path.join(root, file)
                
                # Determine language based on extension
                if file_ext_lower == '.py':
                    lang = 'python'
                elif file_ext_lower == '.java':
                    lang = 'java'
                elif file_ext_lower in ('.js', '.jsx', '.mjs'):
                    lang = 'javascript'
                elif file_ext_lower in ('.ts', '.tsx'):
                    lang = 'typescript'
                elif file_ext_lower == '.go':
                    lang = 'go'
                elif file_ext_lower == '.cs':
                    lang = 'csharp'
                else:
                    lang = 'unknown'
                
                if lang != 'unknown':
                    module_paths_with_lang.append((filepath, lang))
    
    print(f"Found {len(module_paths_with_lang)} files to analyze", file=sys.stderr)
    
    # Process files with ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [partial(process_module, path, language, use_business_rules) for path, language in module_paths_with_lang]
        results = list(executor.map(lambda task: task(), tasks))
        for cypher_list in results:
            if cypher_list:
                cypher_queries.extend(cypher_list)
    
    return cypher_queries

# Main execution
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python cartographer_agent.py <repo_path> [--technical] [--ext EXTENSIONS]", file=sys.stderr)
        print("  --technical: Use technical analysis instead of business rules", file=sys.stderr)
        print("  --ext EXTENSIONS: File extensions to scan (e.g., '.py,.java,.js' or 'all')", file=sys.stderr)
        print("", file=sys.stderr)
        print("Supported languages:", file=sys.stderr)
        print("  Python (.py), Java (.java), JavaScript (.js/.jsx/.mjs),", file=sys.stderr)
        print("  TypeScript (.ts/.tsx), Go (.go), C# (.cs)", file=sys.stderr)
        sys.exit(1)
    
    repo_path = sys.argv[1]
    use_business = '--technical' not in sys.argv
    
    # Parse extension argument
    file_extensions = '.py'  # Default
    for i, arg in enumerate(sys.argv):
        if arg == '--ext' and i + 1 < len(sys.argv):
            file_extensions = sys.argv[i + 1]
            break
    
    print(f"Scanning repository: {repo_path}", file=sys.stderr)
    print(f"Extensions: {file_extensions}", file=sys.stderr)
    print(f"Mode: {'Business Rules Extraction' if use_business else 'Technical Analysis'}", file=sys.stderr)
    print(f"Multi-language support: {'Available' if HAS_MULTI_LANG else 'Not available'}", file=sys.stderr)
    
    try:
        cypher_statements = cartographer_agent(repo_path, file_ext=file_extensions, use_business_rules=use_business)
        print(f"Generated {len(cypher_statements)} insights", file=sys.stderr)
        
        for stmt in cypher_statements:
            print(stmt)
    except Exception as e:
        print(f"Error processing repository: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)