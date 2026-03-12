"""
C#/.NET Language Analyzer using tree-sitter.

Supports:
- C# (.cs files)
- .NET Framework/Core/Standard
- Classes, interfaces, structs, records
- Properties, fields, methods
- Attributes and decorators
- Async/await patterns
- LINQ and extension methods
- Dependency injection patterns
- Nullable reference types

Extracts:
- Namespaces
- Types (classes, interfaces, structs, records, enums)
- Properties and fields
- Methods and constructors
- Attributes and annotations
- Interface implementations
- Generic types and constraints
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
    from tree_sitter_c_sharp import language as get_csharp_language
    HAS_CSHARP_SUPPORT = True
except ImportError as e:
    print(f"Warning: tree-sitter-c_sharp not available: {e}", file=sys.stderr)
    HAS_CSHARP_SUPPORT = False


@dataclass
class CSharpEntity:
    """Represents a C# entity (class, method, property, etc)."""
    type: str  # class, interface, struct, record, enum, method, property, field, etc
    name: str
    start_line: int
    end_line: int
    namespace: str = ""
    access_modifier: str = "internal"  # public, private, protected, internal
    is_static: bool = False
    is_abstract: bool = False
    is_virtual: bool = False
    is_async: bool = False
    parent: Optional[str] = None
    implements: List[str] = None
    generics: Optional[str] = None  # e.g., "T, U where T: IDisposable"
    attributes: List[str] = None
    return_type: Optional[str] = None
    parameters: List[str] = None
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.implements is None:
            self.implements = []
        if self.attributes is None:
            self.attributes = []
        if self.parameters is None:
            self.parameters = []
        if self.properties is None:
            self.properties = {}

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class CSharpAnalyzer:
    """Analyzer for C#/.NET codebases."""

    def __init__(self):
        """Initialize C# analyzer."""
        if not HAS_CSHARP_SUPPORT:
            raise RuntimeError(
                "tree-sitter-c_sharp not available. "
                "Install with: pip install tree-sitter-c_sharp"
            )

        csharp_language_capsule = get_csharp_language()
        self.language = Language(csharp_language_capsule)
        self.parser = Parser()
        self.parser.language = self.language
        self.source_code = ""
        self.entities: List[CSharpEntity] = []
        self.usings: List[Dict[str, Any]] = []
        self.namespace = ""
        self.async_patterns: List[Dict[str, Any]] = []

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a C# file.

        Args:
            filepath: Path to the C# file to analyze

        Returns:
            Dictionary containing:
            - entities: Classes, interfaces, methods, properties, fields
            - usings: Using statements (imports)
            - namespace: Current namespace
            - async_patterns: Async/await pattern locations
            - module_structure: File-level structure
            - public_api: Public members
            - dependencies: External assemblies/namespaces
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        return self.analyze(code, filepath)

    def analyze(self, source_code: str, filepath: str = "") -> Dict[str, Any]:
        """
        Analyze C# source code.

        Args:
            source_code: The source code to analyze
            filepath: Optional filepath for context

        Returns:
            Dictionary with analysis results
        """
        self.source_code = source_code
        self.entities = []
        self.usings = []
        self.namespace = ""
        self.async_patterns = []

        # Parse the code
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node

        # Extract namespace and usings
        self._extract_namespace_and_usings(root)

        # Extract all entities
        self._extract_entities(root)

        # Find async patterns
        self._find_async_patterns(root)

        # Build public API
        public_api = [e.name for e in self.entities if e.access_modifier == "public"]

        # Extract dependencies
        dependencies = self._extract_dependencies()

        return {
            "filepath": filepath,
            "language": "C#",
            "namespace": self.namespace,
            "usings": self.usings,
            "entities": [e.to_dict() for e in self.entities],
            "module_structure": {
                "namespace": self.namespace,
                "num_usings": len(self.usings),
                "num_classes": sum(1 for e in self.entities if e.type == "class"),
                "num_interfaces": sum(1 for e in self.entities if e.type == "interface"),
                "num_structs": sum(1 for e in self.entities if e.type == "struct"),
                "num_records": sum(1 for e in self.entities if e.type == "record"),
                "num_methods": sum(1 for e in self.entities if e.type == "method"),
                "num_properties": sum(1 for e in self.entities if e.type == "property"),
            },
            "public_api": public_api,
            "async_count": len(self.async_patterns),
            "async_patterns": self.async_patterns,
            "dependencies": dependencies,
            "statistics": {
                "lines_of_code": len(source_code.split('\n')),
                "num_classes": sum(1 for e in self.entities if e.type == "class"),
                "num_interfaces": sum(1 for e in self.entities if e.type == "interface"),
                "num_methods": sum(1 for e in self.entities if e.type == "method"),
                "num_properties": sum(1 for e in self.entities if e.type == "property"),
                "num_attributes": sum(len(e.attributes) for e in self.entities),
            }
        }

    def _extract_namespace_and_usings(self, root):
        """Extract namespace declaration and using statements."""
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            if node.type == "file_scoped_namespace_declaration" or node.type == "namespace_declaration":
                name_node = node.child_by_field_name("name")
                if name_node:
                    self.namespace = self._get_source_text(name_node)

            elif node.type == "using_directive":
                self._parse_using_directive(node)

            for child in node.children:
                walk(child)

        walk(root)

    def _parse_using_directive(self, node):
        """Parse a using directive (import)."""
        source_text = self._get_source_text(node)
        # Extract namespace from "using XYZ.ABC.DEF;"
        match = re.search(r"using\s+(static\s+)?([^;]+)", source_text)
        if match:
            is_static = match.group(1) is not None
            namespace = match.group(2).strip()

            self.usings.append({
                "namespace": namespace,
                "is_static": is_static,
                "line": node.start_point[0] + 1,
            })

    def _extract_entities(self, root):
        """Extract all entities (classes, methods, properties, etc)."""
        visited: Set[int] = set()

        def walk(node, parent_name: Optional[str] = None, parent_ns: Optional[str] = None):
            if id(node) in visited:
                return
            visited.add(id(node))

            # Extract class declarations
            if node.type == "class_declaration":
                self._extract_class_declaration(node, parent_name, parent_ns)

            # Extract interface declarations
            elif node.type == "interface_declaration":
                self._extract_interface_declaration(node, parent_name, parent_ns)

            # Extract struct declarations
            elif node.type == "struct_declaration":
                self._extract_struct_declaration(node, parent_name, parent_ns)

            # Extract record declarations
            elif node.type == "record_declaration":
                self._extract_record_declaration(node, parent_name, parent_ns)

            # Extract enum declarations
            elif node.type == "enum_declaration":
                self._extract_enum_declaration(node, parent_name, parent_ns)

            # Extract method declarations
            elif node.type == "method_declaration":
                self._extract_method_declaration(node, parent_name, parent_ns)

            # Extract property declarations
            elif node.type == "property_declaration":
                self._extract_property_declaration(node, parent_name, parent_ns)

            # Extract field declarations
            elif node.type == "field_declaration":
                self._extract_field_declaration(node, parent_name, parent_ns)

            for child in node.children:
                walk(child, parent_name, parent_ns)

        walk(root)

    def _extract_class_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract a class declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        # Extract base types (inheritance)
        base_types = self._extract_base_types(node)

        # Extract attributes
        attributes = self._extract_attributes(node)

        # Get access modifier
        access_modifier = self._get_access_modifier(node)

        # Check if static or abstract
        is_static = "static" in self._get_source_text(node)[:100]
        is_abstract = "abstract" in self._get_source_text(node)[:100]

        entity = CSharpEntity(
            type="class",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            is_static=is_static,
            is_abstract=is_abstract,
            parent=parent_name,
            implements=base_types,
            attributes=attributes,
        )
        self.entities.append(entity)

        # Extract class members
        self._extract_class_members(node, name, parent_ns)

    def _extract_interface_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract an interface declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        # Extract base interfaces
        base_types = self._extract_base_types(node)

        # Extract attributes
        attributes = self._extract_attributes(node)

        access_modifier = self._get_access_modifier(node)

        entity = CSharpEntity(
            type="interface",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            parent=parent_name,
            implements=base_types,
            attributes=attributes,
        )
        self.entities.append(entity)

        # Extract interface members
        self._extract_class_members(node, name, parent_ns)

    def _extract_struct_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract a struct declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        base_types = self._extract_base_types(node)
        attributes = self._extract_attributes(node)
        access_modifier = self._get_access_modifier(node)

        entity = CSharpEntity(
            type="struct",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            parent=parent_name,
            implements=base_types,
            attributes=attributes,
        )
        self.entities.append(entity)

        self._extract_class_members(node, name, parent_ns)

    def _extract_record_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract a record declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        base_types = self._extract_base_types(node)
        attributes = self._extract_attributes(node)
        access_modifier = self._get_access_modifier(node)

        entity = CSharpEntity(
            type="record",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            parent=parent_name,
            implements=base_types,
            attributes=attributes,
        )
        self.entities.append(entity)

        self._extract_class_members(node, name, parent_ns)

    def _extract_enum_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract an enum declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        access_modifier = self._get_access_modifier(node)

        entity = CSharpEntity(
            type="enum",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            parent=parent_name,
        )
        self.entities.append(entity)

    def _extract_class_members(self, class_node, class_name: str, parent_ns: Optional[str]):
        """Extract methods, properties, and fields from a type."""
        for child in class_node.children:
            if child.type == "declaration_list":
                for member in child.children:
                    if member.type == "method_declaration":
                        self._extract_method_declaration(member, class_name, parent_ns)
                    elif member.type == "property_declaration":
                        self._extract_property_declaration(member, class_name, parent_ns)
                    elif member.type == "field_declaration":
                        self._extract_field_declaration(member, class_name, parent_ns)

    def _extract_method_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract a method declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        access_modifier = self._get_access_modifier(node)
        is_static = "static" in self._get_source_text(node)[:100]
        is_abstract = "abstract" in self._get_source_text(node)[:100]
        is_virtual = "virtual" in self._get_source_text(node)[:100]
        is_async = "async" in self._get_source_text(node)[:100]

        # Get return type
        return_type_node = node.child_by_field_name("return_type")
        return_type = self._get_source_text(return_type_node) if return_type_node else "void"

        # Get parameters
        parameters = self._extract_method_parameters(node)

        attributes = self._extract_attributes(node)

        entity = CSharpEntity(
            type="method",
            name=f"{parent_name}.{name}" if parent_name else name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            is_static=is_static,
            is_abstract=is_abstract,
            is_virtual=is_virtual,
            is_async=is_async,
            parent=parent_name,
            return_type=return_type,
            parameters=parameters,
            attributes=attributes,
        )
        self.entities.append(entity)

    def _extract_property_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract a property declaration."""
        name = self._get_member_name(node)
        if not name:
            return

        access_modifier = self._get_access_modifier(node)
        is_static = "static" in self._get_source_text(node)[:100]

        # Get property type
        type_node = node.child_by_field_name("type")
        prop_type = self._get_source_text(type_node) if type_node else "object"

        # Check for getter/setter
        has_get = "get" in self._get_source_text(node)
        has_set = "set" in self._get_source_text(node)
        is_auto = "{" in self._get_source_text(node) and self._get_source_text(node).count("{") == 1

        attributes = self._extract_attributes(node)

        entity = CSharpEntity(
            type="property",
            name=f"{parent_name}.{name}" if parent_name else name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            namespace=parent_ns or self.namespace,
            access_modifier=access_modifier,
            is_static=is_static,
            parent=parent_name,
            return_type=prop_type,
            properties={
                "has_getter": has_get,
                "has_setter": has_set,
                "is_auto_property": is_auto,
            },
            attributes=attributes,
        )
        self.entities.append(entity)

    def _extract_field_declaration(self, node, parent_name: Optional[str], parent_ns: Optional[str]):
        """Extract a field declaration."""
        # Fields can have multiple declarators
        type_node = node.child_by_field_name("type")
        field_type = self._get_source_text(type_node) if type_node else "object"

        access_modifier = self._get_access_modifier(node)
        is_static = "static" in self._get_source_text(node)[:100]
        is_readonly = "readonly" in self._get_source_text(node)[:100]

        # Get field names
        for child in node.children:
            if child.type == "field_declarator" or child.type == "variable_declarator":
                field_name = self._get_source_text(child).split("=")[0].strip()
                if field_name and not field_name.startswith("{"):
                    entity = CSharpEntity(
                        type="field",
                        name=f"{parent_name}.{field_name}" if parent_name else field_name,
                        start_line=node.start_point[0] + 1,
                        end_line=node.end_point[0] + 1,
                        namespace=parent_ns or self.namespace,
                        access_modifier=access_modifier,
                        is_static=is_static,
                        parent=parent_name,
                        return_type=field_type,
                        properties={"is_readonly": is_readonly},
                    )
                    self.entities.append(entity)

    def _extract_base_types(self, node) -> List[str]:
        """Extract base types (interfaces/classes this type implements/inherits)."""
        base_types = []
        base_list_node = node.child_by_field_name("bases")

        if base_list_node:
            for child in base_list_node.children:
                if child.type == "base_class" or child.type == "type_identifier":
                    base_type = self._get_source_text(child).strip()
                    if base_type and base_type != ",":
                        base_types.append(base_type)

        return base_types

    def _extract_attributes(self, node) -> List[str]:
        """Extract attributes from a node."""
        attributes = []

        for child in node.children:
            if child.type == "attribute_list":
                for attr in child.children:
                    if attr.type == "attribute":
                        attr_text = self._get_source_text(attr)
                        # Clean up the attribute text
                        attr_text = attr_text.strip().strip("[]")
                        attributes.append(attr_text)

        return attributes

    def _extract_method_parameters(self, node) -> List[str]:
        """Extract method parameters."""
        parameters = []
        params_node = node.child_by_field_name("parameters")

        if params_node:
            for child in params_node.children:
                if child.type == "parameter":
                    param_name = self._get_source_text(child).split()[-1]
                    parameters.append(param_name)

        return parameters

    def _find_async_patterns(self, root):
        """Find async/await patterns."""
        visited: Set[int] = set()

        def walk(node):
            if id(node) in visited:
                return
            visited.add(id(node))

            # Find await expressions
            if node.type == "await_expression":
                self.async_patterns.append({
                    "type": "await",
                    "line": node.start_point[0] + 1,
                    "text": self._get_source_text(node)[:60],
                })

            # Find Task returns
            elif node.type == "identifier":
                text = self._get_source_text(node)
                if text in ("Task", "Task<T>", "ValueTask"):
                    self.async_patterns.append({
                        "type": "task_return",
                        "line": node.start_point[0] + 1,
                        "text": text,
                    })

            for child in node.children:
                walk(child)

        walk(root)

    def _extract_dependencies(self) -> List[str]:
        """Extract external dependencies from usings."""
        dependencies = []
        seen = set()

        for using in self.usings:
            namespace = using.get("namespace", "")
            if namespace:
                # Get the root namespace (first part before .)
                root_ns = namespace.split(".")[0]
                if root_ns and root_ns not in seen:
                    dependencies.append(root_ns)
                    seen.add(root_ns)

        return sorted(dependencies)

    def _get_member_name(self, node) -> Optional[str]:
        """Get the name of a type member."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_source_text(name_node)

        # For declarations with identifiers
        for child in node.children:
            if child.type == "identifier":
                return self._get_source_text(child)

        return None

    def _get_access_modifier(self, node) -> str:
        """Get the access modifier (public, private, protected, internal)."""
        source = self._get_source_text(node)[:200]
        if "public" in source:
            return "public"
        elif "private" in source:
            return "private"
        elif "protected" in source:
            if "internal" in source:
                return "protected internal"
            return "protected"
        elif "internal" in source:
            return "internal"
        return "internal"  # Default in C#

    def _get_source_text(self, node) -> str:
        """Get the source text for a node."""
        if not node or node.start_byte >= node.end_byte:
            return ""
        return self.source_code[node.start_byte:node.end_byte]


# Convenience function for single-file analysis
def analyze_csharp_file(filepath: str) -> Dict[str, Any]:
    """Analyze a single C# file."""
    analyzer = CSharpAnalyzer()
    return analyzer.analyze_file(filepath)
