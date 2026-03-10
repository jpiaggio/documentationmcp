import os
import concurrent.futures
from tree_sitter import Language, Parser

# Load the Python grammar for tree-sitter
PY_LANGUAGE = Language('build/my-languages.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

def parse_code(source_code):
    tree = parser.parse(bytes(source_code, "utf8"))
    root_node = tree.root_node
    return root_node

def extract_functions_and_classes(root_node, source_code):
    results = []
    for node in root_node.walk():
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
    return results

def extract_imports(root_node, source_code):
    imports = []
    for node in root_node.walk():
        if node.type in ('import_statement', 'import_from_statement'):
            import_text = source_code[node.start_byte:node.end_byte]
            imports.append(import_text)
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
        label = 'Function' if item['type'] == 'function_definition' else 'Class'
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

def process_module(module_path):
    with open(module_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    root_node = parse_code(source_code)
    functions_classes = extract_functions_and_classes(root_node, source_code)
    imports = extract_imports(root_node, source_code)
    cypher = generate_cypher(module_path, functions_classes, imports)
    return cypher

def cartographer_agent(repo_root, file_ext='.py', max_workers=8):
    cypher_queries = []
    module_paths = []
    for root, _, files in os.walk(repo_root):
        for file in files:
            if file.endswith(file_ext):
                module_paths.append(os.path.join(root, file))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_module, module_paths))
        for cypher_list in results:
            cypher_queries.extend(cypher_list)
    return cypher_queries

# Example usage:
# cypher_statements = cartographer_agent('/path/to/repo')
# for stmt in cypher_statements:
#     print(stmt)
