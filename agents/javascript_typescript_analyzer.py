"""
JavaScript/TypeScript Analyzer using tree-sitter.

Supports:
- JavaScript (.js, .jsx, .mjs)
- TypeScript (.ts, .tsx)

Extracts:
- Classes, interfaces, types, enums
- Functions and arrow functions
- Imports and exports
- Decorators
- Async/await patterns
- Module structure
"""

import os
import sys
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from tree_sitter import Parser, Language
    from tree_sitter_javascript import language as get_javascript_language
    HAS_JS_SUPPORT = True
except ImportError as e:
    print(f"Warning: tree-sitter JavaScript not available: {e}", file=sys.stderr)
    HAS_JS_SUPPORT = False


@dataclass
class JSEntity:
    """Represents a JavaScript/TypeScript entity."""
    type: str  # class, function, interface, enum, type, async_function
    name: str
    start_line: int
    end_line: int
    parent: Optional[str] = None
    is_exported: bool = False
    is_default_export: bool = False
    decorators: List[str] = None
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
        if self.properties is None:
            self.properties = {}

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class JavaScriptTypeScriptAnalyzer:
    """Analyzer for JavaScript and TypeScript codebases."""

    def __init__(self):
        """Initialize JavaScript/TypeScript analyzer."""
        if not HAS_JS_SUPPORT:
            raise RuntimeError(
                "tree-sitter-javascript not available. "
                "Install with: pip install tree-sitter-javascript"
            )

        js_language_capsule = get_javascript_language()
        self.language = Language(js_language_capsule)
        self.parser = Parser()
        self.parser.language = self.language
        self.source_code = ""
        self.entities: List[JSEntity] = []
        self.imports: List[Dict[str, Any]] = []
        self.exports: List[Dict[str, Any]] = []

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a JavaScript/TypeScript file.

        Args:
            filepath: Path to the file to analyze

        Returns:
            Dictionary containing:
            - entities: List of classes, functions, interfaces, etc.
            - imports: List of import statements
            - exports: List of export statements
            - module_structure: Module-level information
            - async_patterns: Locations of async/await usage
            - dependencies: External module dependencies
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        return self.analyze(code, filepath)

    def analyze(self, source_code: str, filepath: str = "") -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript source code.

        Args:
            source_code: The source code to analyze
            filepath: Optional filepath for context

        Returns:
            Dictionary with analysis results
        """
        self.source_code = source_code
        self.entities = []
        self.imports = []
        self.exports = []

        # Parse the code
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node

        # Extract all entities
        self._extract_entities(root)

        # Extract imports and exports
        self._extract_imports_exports(root)

        # Extract async patterns
        async_patterns = self._find_async_patterns(root)

        # Build dependency list
        dependencies = self._extract_dependencies()

        return {
            "filepath": filepath,
            "file_type": self._detect_file_type(filepath),
            "entities": [e.to_dict() for e in self.entities],
            "imports": self.imports,
            "exports": self.exports,
            "module_structure": {
                "has_default_export": any(e.get("is_default_export") for e in self.exports),
                "num_exports": len(self.exports),
                "num_imports": len(self.imports),
            },
            "async_patterns": async_patterns,
            "dependencies": dependencies,
            "statistics": {
                "lines_of_code": len(source_code.split('\n')),
                "num_classes": sum(1 for e in self.entities if e.type == "class"),
                "num_functions": sum(1 for e in self.entities if e.type in ("function", "async_function")),
                "num_interfaces": sum(1 for e in self.entities if e.type == "interface"),
                "num_types": sum(1 for e in self.entities if e.type == "type_alias"),
            }
        }

    def _detect_file_type(self, filepath: str) -> str:
        """Detect if file is TypeScript or JavaScript."""
        if filepath.endswith(".ts") or filepath.endswith(".tsx"):
            return "TypeScript"
        return "JavaScript"

    def _extract_entities(self, node, parent_name: Optional[str] = None):
        """Recursively extract classes, functions, interfaces."""
        if not node:
            return

        node_type = node.type

        # Detect exported status
        is_exported = self._is_exported_node(node)
        is_default_export = self._is_default_export(node)

        # Extract classes
        if node_type == "class_declaration":
            name = self._get_node_name(node)
            if name:
                decorators = self._get_decorators(node)
                entity = JSEntity(
                    type="class",
                    name=name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=parent_name,
                    is_exported=is_exported,
                    is_default_export=is_default_export,
                    decorators=decorators,
                )
                self.entities.append(entity)
                # Extract class members
                self._extract_class_members(node, name)

        # Extract interfaces (TypeScript)
        elif node_type == "interface_declaration":
            name = self._get_node_name(node)
            if name:
                entity = JSEntity(
                    type="interface",
                    name=name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=parent_name,
                    is_exported=is_exported,
                    is_default_export=is_default_export,
                )
                self.entities.append(entity)

        # Extract type aliases (TypeScript)
        elif node_type == "type_alias_declaration":
            name = self._get_node_name(node)
            if name:
                entity = JSEntity(
                    type="type_alias",
                    name=name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=parent_name,
                    is_exported=is_exported,
                    is_default_export=is_default_export,
                )
                self.entities.append(entity)

        # Extract enums (TypeScript)
        elif node_type == "enum_declaration":
            name = self._get_node_name(node)
            if name:
                entity = JSEntity(
                    type="enum",
                    name=name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=parent_name,
                    is_exported=is_exported,
                    is_default_export=is_default_export,
                )
                self.entities.append(entity)

        # Extract function declarations
        elif node_type == "function_declaration":
            name = self._get_node_name(node)
            if name:
                is_async = self._is_async_function(node)
                entity = JSEntity(
                    type="async_function" if is_async else "function",
                    name=name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent=parent_name,
                    is_exported=is_exported,
                    is_default_export=is_default_export,
                    decorators=self._get_decorators(node),
                )
                self.entities.append(entity)

        # Extract variable declarations (arrow functions, const)
        elif node_type == "variable_declaration":
            self._extract_from_variable_declaration(node, parent_name)

        # Recursively process children
        for child in node.children:
            self._extract_entities(child, parent_name)

    def _extract_class_members(self, class_node, class_name: str):
        """Extract methods and properties from a class."""
        for child in class_node.children:
            if child.type == "class_body":
                for member in child.children:
                    if member.type == "method_definition":
                        method_name = self._get_node_name(member)
                        if method_name:
                            is_async = self._is_async_function(member)
                            entity = JSEntity(
                                type="async_method" if is_async else "method",
                                name=f"{class_name}.{method_name}",
                                start_line=member.start_point[0] + 1,
                                end_line=member.end_point[0] + 1,
                                parent=class_name,
                                decorators=self._get_decorators(member),
                            )
                            self.entities.append(entity)

                    elif member.type == "field_definition":
                        field_name = self._get_node_name(member)
                        if field_name:
                            entity = JSEntity(
                                type="property",
                                name=f"{class_name}.{field_name}",
                                start_line=member.start_point[0] + 1,
                                end_line=member.end_point[0] + 1,
                                parent=class_name,
                            )
                            self.entities.append(entity)

    def _extract_from_variable_declaration(self, node, parent_name: Optional[str] = None):
        """Extract arrow functions and const functions from variable declarations."""
        for child in node.children:
            if child.type == "variable_declarator":
                var_name = None
                # Get the variable name
                for declarator_child in child.children:
                    if declarator_child.type == "identifier":
                        var_name = self._get_source_text(declarator_child)
                        break

                if var_name:
                    # Check if it's an arrow function
                    for declarator_child in child.children:
                        if declarator_child.type == "arrow_function":
                            is_async = self._is_async_function(declarator_child)
                            entity = JSEntity(
                                type="async_function" if is_async else "arrow_function",
                                name=var_name,
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                parent=parent_name,
                            )
                            self.entities.append(entity)
                            break

                        elif declarator_child.type == "function_expression":
                            is_async = self._is_async_function(declarator_child)
                            entity = JSEntity(
                                type="async_function" if is_async else "function",
                                name=var_name,
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                parent=parent_name,
                            )
                            self.entities.append(entity)
                            break

    def _extract_imports_exports(self, root):
        """Extract import and export statements."""
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            if node.type == "import_statement":
                import_info = self._parse_import_statement(node)
                if import_info:
                    self.imports.append(import_info)

            elif node.type == "export_statement":
                export_info = self._parse_export_statement(node)
                if export_info:
                    self.exports.append(export_info)

            elif node.type == "export_named_declaration":
                export_info = self._parse_named_export(node)
                if export_info:
                    self.exports.append(export_info)

            elif node.type == "export_default_declaration":
                export_info = self._parse_default_export(node)
                if export_info:
                    self.exports.append(export_info)

            for child in node.children:
                walk(child)

        walk(root)

    def _parse_import_statement(self, node) -> Optional[Dict[str, Any]]:
        """Parse an import statement."""
        source_text = self._get_source_text(node)
        if not source_text:
            return None

        # Extract the module source (string after 'from')
        match = re.search(r"from\s+['\"]([^'\"]+)['\"]", source_text)
        module_source = match.group(1) if match else ""

        # Extract imported items
        imported_items = []
        match = re.search(r"import\s+({[^}]+}|[\w\s,]+|['\"])", source_text)
        if match:
            imported_items_str = match.group(1)
            if imported_items_str.startswith("{"):
                # Named imports: {a, b, c}
                items = imported_items_str.strip("{}").split(",")
                imported_items = [item.strip().split(" as ")[0] for item in items]
            elif not imported_items_str.startswith("'") and not imported_items_str.startswith('"'):
                # Default import: import x
                imported_items = [imported_items_str.strip()]

        return {
            "source": module_source,
            "items": imported_items,
            "line": node.start_point[0] + 1,
            "is_default": len(imported_items) == 1 and not "{" in source_text,
        }

    def _parse_export_statement(self, node) -> Optional[Dict[str, Any]]:
        """Parse an export statement."""
        source_text = self._get_source_text(node)
        if not source_text:
            return None

        return {
            "type": "re-export",
            "source": source_text,
            "line": node.start_point[0] + 1,
        }

    def _parse_named_export(self, node) -> Optional[Dict[str, Any]]:
        """Parse a named export declaration."""
        exported_name = self._get_node_name(node)
        if not exported_name:
            # Try to get from child declaration
            for child in node.children:
                if child.type in ("class_declaration", "function_declaration", "variable_declaration"):
                    exported_name = self._get_node_name(child)
                    break

        if exported_name:
            return {
                "name": exported_name,
                "type": "named",
                "line": node.start_point[0] + 1,
            }
        return None

    def _parse_default_export(self, node) -> Optional[Dict[str, Any]]:
        """Parse a default export."""
        for child in node.children:
            if child.type in ("class_declaration", "function_declaration", "identifier"):
                exported_name = self._get_node_name(child)
                if exported_name:
                    return {
                        "name": exported_name,
                        "type": "default",
                        "line": node.start_point[0] + 1,
                    }

        return {
            "name": "default",
            "type": "default",
            "line": node.start_point[0] + 1,
        }

    def _find_async_patterns(self, root) -> List[Dict[str, Any]]:
        """Find async/await patterns in the code."""
        patterns: List[Dict[str, Any]] = []
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            # Find await expressions
            if node.type == "await_expression":
                patterns.append({
                    "type": "await",
                    "line": node.start_point[0] + 1,
                    "text": self._get_source_text(node),
                })

            # Find Promise chains (.then, .catch)
            elif node.type == "member_expression":
                text = self._get_source_text(node)
                if ".then(" in text or ".catch(" in text or ".finally(" in text:
                    patterns.append({
                        "type": "promise_chain",
                        "line": node.start_point[0] + 1,
                        "text": text[:50],  # First 50 chars
                    })

            for child in node.children:
                walk(child)

        walk(root)
        return patterns

    def _extract_dependencies(self) -> List[str]:
        """Extract external module dependencies from imports."""
        dependencies = set()
        for imp in self.imports:
            source = imp.get("source", "")
            if source and not source.startswith("."):
                # It's an external dependency
                # Extract the package name (part before /, or whole if no /)
                package = source.split("/")[0]
                if source.startswith("@"):
                    # Scoped package
                    package = "/".join(source.split("/")[:2])
                dependencies.add(package)

        return sorted(list(dependencies))

    def _get_node_name(self, node) -> Optional[str]:
        """Get the name of a node (class name, function name, etc)."""
        # Try name field first
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_source_text(name_node)

        # For identifiers, return directly
        if node.type == "identifier":
            return self._get_source_text(node)

        # Search for identifier child
        for child in node.children:
            if child.type == "identifier":
                return self._get_source_text(child)

        return None

    def _get_source_text(self, node) -> str:
        """Get the source text for a node."""
        if not node or node.start_byte >= node.end_byte:
            return ""
        return self.source_code[node.start_byte:node.end_byte]

    def _is_async_function(self, node) -> bool:
        """Check if a function is async."""
        source = self._get_source_text(node)
        return source.strip().startswith("async")

    def _is_exported_node(self, node) -> bool:
        """Check if a node is exported."""
        # Walk up the tree to check for export
        parent = node.parent
        while parent:
            if parent.type in ("export_statement", "export_named_declaration"):
                return True
            parent = parent.parent
        return False

    def _is_default_export(self, node) -> bool:
        """Check if a node is a default export."""
        parent = node.parent
        while parent:
            if parent.type == "export_default_declaration":
                return True
            parent = parent.parent
        return False

    def _get_decorators(self, node) -> List[str]:
        """Extract decorators from a node (TypeScript/Python style)."""
        decorators = []
        # Look for decorator nodes
        for child in node.children:
            if child.type == "decorator":
                decorator_text = self._get_source_text(child).strip("@").strip()
                decorators.append(decorator_text)
        return decorators


# Convenience function for single-file analysis
def analyze_javascript_file(filepath: str) -> Dict[str, Any]:
    """Analyze a single JavaScript/TypeScript file."""
    analyzer = JavaScriptTypeScriptAnalyzer()
    return analyzer.analyze_file(filepath)
