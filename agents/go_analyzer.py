"""
Go Language Analyzer using tree-sitter.

Supports:
- Go (.go files)
- Go modules
- Interface-based design patterns
- Goroutine patterns
- Dependency management (go.mod)

Extracts:
- Packages and imports
- Types (structs, interfaces, type aliases)
- Functions and methods
- Receiver functions (methods)
- Goroutine patterns
- Module dependencies
"""

import os
import sys
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, asdict
import re

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from tree_sitter import Parser, Language
    from tree_sitter_go import language as get_go_language
    HAS_GO_SUPPORT = True
except ImportError as e:
    print(f"Warning: tree-sitter-go not available: {e}", file=sys.stderr)
    HAS_GO_SUPPORT = False


@dataclass
class GoEntity:
    """Represents a Go entity (function, type, interface, etc)."""
    type: str  # function, method, struct, interface, type_alias, const, var
    name: str
    start_line: int
    end_line: int
    package: str = ""
    receiver: Optional[str] = None  # For methods, e.g., "*Client" or "Server"
    is_exported: bool = False  # Capitalized = exported in Go
    parameters: List[str] = None
    return_types: List[str] = None
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
        if self.return_types is None:
            self.return_types = []
        if self.properties is None:
            self.properties = {}

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class GoAnalyzer:
    """Analyzer for Go codebases."""

    def __init__(self):
        """Initialize Go analyzer."""
        if not HAS_GO_SUPPORT:
            raise RuntimeError(
                "tree-sitter-go not available. "
                "Install with: pip install tree-sitter-go"
            )

        go_language_capsule = get_go_language()
        self.language = Language(go_language_capsule)
        self.parser = Parser()
        self.parser.language = self.language
        self.source_code = ""
        self.entities: List[GoEntity] = []
        self.imports: List[Dict[str, Any]] = []
        self.package_name = ""
        self.goroutine_patterns: List[Dict[str, Any]] = []

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a Go file.

        Args:
            filepath: Path to the Go file to analyze

        Returns:
            Dictionary containing:
            - entities: Functions, methods, types, interfaces
            - imports: Import statements
            - package: Package name
            - goroutine_patterns: go keyword usage locations
            - module_structure: File-level structure info
            - exported_items: Public API (exported items)
            - dependencies: External packages
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        return self.analyze(code, filepath)

    def analyze(self, source_code: str, filepath: str = "") -> Dict[str, Any]:
        """
        Analyze Go source code.

        Args:
            source_code: The source code to analyze
            filepath: Optional filepath for context

        Returns:
            Dictionary with analysis results
        """
        self.source_code = source_code
        self.entities = []
        self.imports = []
        self.goroutine_patterns = []
        self.package_name = ""

        # Parse the code
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node

        # Extract package name
        self._extract_package_name(root)

        # Extract imports
        self._extract_imports(root)

        # Extract entities
        self._extract_entities(root)

        # Find goroutine patterns
        self._find_goroutine_patterns(root)

        # Extract module dependencies
        dependencies = self._extract_dependencies()

        # Build exported items list
        exported_items = [e.name for e in self.entities if e.is_exported]

        return {
            "filepath": filepath,
            "language": "Go",
            "package": self.package_name,
            "entities": [e.to_dict() for e in self.entities],
            "imports": self.imports,
            "module_structure": {
                "package_name": self.package_name,
                "num_imports": len(self.imports),
                "num_exported_items": len(exported_items),
                "num_functions": sum(1 for e in self.entities if e.type in ("function", "method")),
                "num_types": sum(1 for e in self.entities if e.type in ("struct", "interface", "type_alias")),
            },
            "exported_items": exported_items,
            "goroutine_count": len(self.goroutine_patterns),
            "goroutine_patterns": self.goroutine_patterns,
            "dependencies": dependencies,
            "statistics": {
                "lines_of_code": len(source_code.split('\n')),
                "num_structs": sum(1 for e in self.entities if e.type == "struct"),
                "num_interfaces": sum(1 for e in self.entities if e.type == "interface"),
                "num_methods": sum(1 for e in self.entities if e.type == "method"),
                "num_functions": sum(1 for e in self.entities if e.type == "function"),
            }
        }

    def _extract_package_name(self, root):
        """Extract the package name from the file."""
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            if node.type == "package_clause":
                for child in node.children:
                    if child.type == "package_identifier":
                        self.package_name = self._get_source_text(child)
                        return

            for child in node.children:
                walk(child)

        walk(root)

    def _extract_imports(self, root):
        """Extract import statements."""
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            if node.type == "import_declaration":
                self._parse_import_declaration(node)

            elif node.type == "import_spec":
                self._parse_import_spec(node)

            for child in node.children:
                walk(child)

        walk(root)

    def _parse_import_declaration(self, node):
        """Parse an import declaration (bulk import)."""
        for child in node.children:
            if child.type == "import_spec_list":
                for spec in child.children:
                    if spec.type == "import_spec":
                        self._parse_import_spec(spec)
            elif child.type == "import_spec":
                self._parse_import_spec(child)

    def _parse_import_spec(self, node):
        """Parse a single import spec."""
        package_path = None
        alias = None

        for child in node.children:
            if child.type == "package_identifier":
                alias = self._get_source_text(child)
            elif child.type == "import_path":
                package_path = self._get_source_text(child).strip('"')

        if package_path:
            self.imports.append({
                "path": package_path,
                "alias": alias,
                "line": node.start_point[0] + 1,
            })

    def _extract_entities(self, root):
        """Extract all top-level entities (functions, types, etc)."""
        visited: Set[int] = set()

        def walk(node, parent_type: Optional[str] = None):
            if id(node) in visited:
                return
            visited.add(id(node))

            # Function declarations
            if node.type == "function_declaration":
                self._extract_function_declaration(node)

            # Method declarations
            elif node.type == "method_declaration":
                self._extract_method_declaration(node)

            # Type declarations
            elif node.type == "type_declaration":
                self._extract_type_declaration(node)

            # Const and var blocks
            elif node.type in ("const_declaration", "var_declaration"):
                self._extract_const_var_declaration(node)

            for child in node.children:
                walk(child, parent_type)

        walk(root)

    def _extract_function_declaration(self, node):
        """Extract a function declaration."""
        name_node = node.child_by_field_name("name")
        if not name_node:
            return

        name = self._get_source_text(name_node)
        is_exported = name and name[0].isupper()

        # Extract parameters
        params_node = node.child_by_field_name("parameters")
        parameters = self._extract_parameters(params_node) if params_node else []

        # Extract return types
        result_node = node.child_by_field_name("result")
        return_types = self._extract_return_types(result_node) if result_node else []

        entity = GoEntity(
            type="function",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            package=self.package_name,
            is_exported=is_exported,
            parameters=parameters,
            return_types=return_types,
        )
        self.entities.append(entity)

    def _extract_method_declaration(self, node):
        """Extract a method declaration."""
        name_node = node.child_by_field_name("name")
        if not name_node:
            return

        name = self._get_source_text(name_node)
        is_exported = name and name[0].isupper()

        # Extract receiver
        receiver_node = node.child_by_field_name("receiver")
        receiver = self._extract_receiver(receiver_node) if receiver_node else None

        # Extract parameters
        params_node = node.child_by_field_name("parameters")
        parameters = self._extract_parameters(params_node) if params_node else []

        # Extract return types
        result_node = node.child_by_field_name("result")
        return_types = self._extract_return_types(result_node) if result_node else []

        entity = GoEntity(
            type="method",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            package=self.package_name,
            receiver=receiver,
            is_exported=is_exported,
            parameters=parameters,
            return_types=return_types,
        )
        self.entities.append(entity)

    def _extract_type_declaration(self, node):
        """Extract type declarations (struct, interface, type alias)."""
        # Type declarations can contain multiple specs
        for child in node.children:
            if child.type == "type_spec":
                self._extract_type_spec(child)

    def _extract_type_spec(self, node):
        """Extract a single type spec."""
        name_node = node.child_by_field_name("name")
        if not name_node:
            return

        name = self._get_source_text(name_node)
        is_exported = name and name[0].isupper()

        # Determine type
        type_node = node.child_by_field_name("type")
        if not type_node:
            return

        entity_type = "type_alias"
        if type_node.type == "struct_type":
            entity_type = "struct"
            # Extract struct fields
            properties = self._extract_struct_fields(type_node)
        elif type_node.type == "interface_type":
            entity_type = "interface"
            # Extract interface methods
            properties = self._extract_interface_methods(type_node)
        else:
            properties = {}

        entity = GoEntity(
            type=entity_type,
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            package=self.package_name,
            is_exported=is_exported,
            properties=properties,
        )
        self.entities.append(entity)

    def _extract_struct_fields(self, struct_node) -> Dict[str, Any]:
        """Extract fields from a struct type."""
        fields = {}
        for child in struct_node.children:
            if child.type == "field_declaration_list":
                for field in child.children:
                    if field.type == "field_declaration":
                        field_name = self._get_source_text(field).split()[0]
                        fields[field_name] = "field"
        return fields

    def _extract_interface_methods(self, interface_node) -> Dict[str, Any]:
        """Extract methods from an interface type."""
        methods = {}
        for child in interface_node.children:
            if child.type == "method_spec_list":
                for method in child.children:
                    if method.type == "method_spec":
                        # Extract method name
                        name_node = method.child_by_field_name("name")
                        if name_node:
                            method_name = self._get_source_text(name_node)
                            methods[method_name] = "method"
        return methods

    def _extract_const_var_declaration(self, node):
        """Extract const and var declarations."""
        for child in node.children:
            if child.type == "const_spec" or child.type == "var_spec":
                name_node = child.child_by_field_name("name")
                if name_node:
                    name = self._get_source_text(name_node)
                    is_exported = name and name[0].isupper()

                    entity = GoEntity(
                        type="const" if node.type == "const_declaration" else "var",
                        name=name,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        package=self.package_name,
                        is_exported=is_exported,
                    )
                    self.entities.append(entity)

    def _extract_parameters(self, params_node) -> List[str]:
        """Extract parameter names from a parameter list."""
        parameters = []
        if not params_node:
            return parameters

        for child in params_node.children:
            if child.type == "parameter_declaration":
                # Extract parameter names
                name_node = child.child_by_field_name("name")
                if name_node:
                    parameters.append(self._get_source_text(name_node))
        return parameters

    def _extract_return_types(self, result_node) -> List[str]:
        """Extract return types from result node."""
        return_types = []
        if not result_node:
            return return_types

        for child in result_node.children:
            if child.type in ("type_identifier", "pointer_type", "slice_type", "map_type"):
                return_types.append(self._get_source_text(child))
        return return_types

    def _extract_receiver(self, receiver_node) -> Optional[str]:
        """Extract receiver type (for methods)."""
        if not receiver_node:
            return None

        # The receiver is the first parameter in the receiver list
        for child in receiver_node.children:
            if child.type == "parameter_declaration":
                # Get the type
                type_text = self._get_source_text(child).split()
                if len(type_text) > 1:
                    return type_text[1]  # The type is after the name
        return None

    def _find_goroutine_patterns(self, root):
        """Find goroutine (go keyword) usage patterns."""
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            if node.type == "go_statement":
                self.goroutine_patterns.append({
                    "type": "goroutine",
                    "line": node.start_point[0] + 1,
                    "text": self._get_source_text(node)[:60],
                })

            # Also find channel operations
            elif node.type == "send_statement":
                self.goroutine_patterns.append({
                    "type": "channel_send",
                    "line": node.start_point[0] + 1,
                    "text": self._get_source_text(node)[:60],
                })

            for child in node.children:
                walk(child)

        walk(root)

    def _extract_dependencies(self) -> List[str]:
        """Extract external package dependencies from imports."""
        dependencies = []
        for imp in self.imports:
            path = imp.get("path", "")
            if path and not path.startswith("."):
                # Extract main package (before first slash)
                main_package = path.split("/")[0]
                if main_package:
                    dependencies.append(main_package)

        return sorted(list(set(dependencies)))  # Remove duplicates

    def _get_source_text(self, node) -> str:
        """Get the source text for a node."""
        if not node or node.start_byte >= node.end_byte:
            return ""
        return self.source_code[node.start_byte:node.end_byte]


# Convenience function for single-file analysis
def analyze_go_file(filepath: str) -> Dict[str, Any]:
    """Analyze a single Go file."""
    analyzer = GoAnalyzer()
    return analyzer.analyze_file(filepath)
