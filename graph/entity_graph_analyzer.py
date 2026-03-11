"""
Entity Graph Analyzer

Extracts entities and relationships from code by analyzing:
- Class definitions and hierarchies
- Method calls and dependencies
- Data structures and their interactions
- Business logic flow
"""

import ast
import re
import sys
import os
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_entity_graph import (
    SmartEntityGraph, Cardinality, TemporalType, EntityRelationship
)


@dataclass
class EntityPattern:
    """Pattern for identifying entities in code."""
    name: str
    keywords: List[str]
    entity_type: str


class EntityGraphAnalyzer:
    """Analyzes code to extract entities and build entity graphs."""
    
    # Common business entity patterns
    ENTITY_PATTERNS = [
        EntityPattern("Customer", ["customer", "user", "account"], "Customer"),
        EntityPattern("Order", ["order", "purchase"], "Order"),
        EntityPattern("Payment", ["payment", "transaction", "charge"], "Payment"),
        EntityPattern("Product", ["product", "item", "sku"], "Product"),
        EntityPattern("Inventory", ["inventory", "stock", "warehouse"], "Inventory"),
        EntityPattern("Invoice", ["invoice", "bill"], "Invoice"),
        EntityPattern("Shipment", ["shipment", "delivery", "shipping"], "Shipment"),
        EntityPattern("Review", ["review", "rating", "feedback"], "Review"),
        EntityPattern("Subscription", ["subscription", "plan"], "Subscription"),
        EntityPattern("Category", ["category", "class", "type"], "Category"),
    ]
    
    def __init__(self):
        """Initialize the analyzer."""
        self.graph = SmartEntityGraph()
        self.entities_found: Dict[str, List[str]] = defaultdict(list)
        self.class_hierarchy: Dict[str, str] = {}  # child -> parent
        self.method_calls: Dict[str, List[str]] = defaultdict(list)  # class -> called methods
        self.attribute_types: Dict[str, str] = {}  # attribute -> type
    
    def analyze_code(self, source_code: str, filename: str = "") -> SmartEntityGraph:
        """
        Main entry point to analyze code and extract entities.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Syntax error in {filename}: {e}")
            return self.graph
        
        # First pass: extract entities and build class information
        self._extract_entities(tree)
        
        # Second pass: analyze relationships
        self._analyze_relationships(tree)
        
        # Third pass: infer temporal relationships
        self._infer_temporal_relationships(tree)
        
        return self.graph
    
    def _extract_entities(self, tree: ast.AST):
        """Extract entities (classes) from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this class matches our entity patterns
                entity_type = self._identify_entity_type(node.name)
                
                self.graph.add_entity(
                    name=node.name,
                    entity_type=entity_type or "Entity",
                    properties={'base_classes': str([b.id if hasattr(b, 'id') else str(b) for b in node.bases])}
                )
                
                # Extract class attributes
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        attr_name = item.target.id
                        attr_type = self._get_type_hint(item.annotation)
                        self.attribute_types[f"{node.name}.{attr_name}"] = attr_type
                    
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                attr_name = target.id
                                # Try to infer type from assignment
                                attr_type = self._infer_type_from_value(item.value)
                                self.attribute_types[f"{node.name}.{attr_name}"] = attr_type
    
    def _identify_entity_type(self, class_name: str) -> Optional[str]:
        """Identify if a class matches a known entity pattern."""
        class_lower = class_name.lower()
        
        for pattern in self.ENTITY_PATTERNS:
            for keyword in pattern.keywords:
                if keyword in class_lower:
                    return pattern.entity_type
        
        return None
    
    def _analyze_relationships(self, tree: ast.AST):
        """Analyze relationships between entities."""
        classes_by_name = {}
        
        # First pass: collect all classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_by_name[node.name] = node
        
        # Second pass: analyze relationships
        for class_name, class_node in classes_by_name.items():
            # Check parent classes (inheritance)
            for base in class_node.bases:
                base_name = self._get_name_from_node(base)
                if base_name and base_name in classes_by_name:
                    self.graph.add_relationship(
                        source=class_name,
                        target=base_name,
                        relationship_type="EXTENDS",
                        cardinality=Cardinality.ONE_TO_ONE,
                        confidence=0.95
                    )
            
            # Analyze attributes for relationships
            for attr_name, attr_type in self.attribute_types.items():
                if attr_name.startswith(class_name + "."):
                    target_class = attr_type.strip("[]")  # Remove array notation
                    if target_class in classes_by_name:
                        # Determine cardinality from attribute type
                        is_collection = "[]" in attr_type or "List" in attr_type or "Set" in attr_type
                        cardinality = Cardinality.ONE_TO_MANY if is_collection else Cardinality.ONE_TO_ONE
                        
                        self.graph.add_relationship(
                            source=class_name,
                            target=target_class,
                            relationship_type="HAS",
                            cardinality=cardinality,
                            properties={'attribute': attr_name.split('.')[-1]},
                            confidence=0.85
                        )
            
            # Analyze method calls for functional relationships
            self._analyze_method_calls(class_node, class_name, classes_by_name)
    
    def _analyze_method_calls(self, class_node: ast.ClassDef, 
                             class_name: str, 
                             classes_by_name: Dict[str, ast.ClassDef]):
        """Analyze method calls within a class."""
        for node in ast.walk(class_node):
            if isinstance(node, ast.Call):
                # Check for calls to other class methods
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        called_on = node.func.value.id
                        method = node.func.attr
                        
                        # Check if called_on is a known class
                        if called_on in classes_by_name and called_on != class_name:
                            self.graph.add_relationship(
                                source=class_name,
                                target=called_on,
                                relationship_type="CALLS",
                                cardinality=Cardinality.MANY_TO_ONE,
                                properties={'method': method},
                                confidence=0.8
                            )
    
    def _infer_temporal_relationships(self, tree: ast.AST):
        """Infer temporal/causal relationships from code patterns."""
        temporal_patterns = {
            'create': (TemporalType.TRIGGERED_BY, "creates a new"),
            'process': (TemporalType.TRIGGERED_BY, "processes"),
            'validate': (TemporalType.DEPENDS_ON, "validates"),
            'execute': (TemporalType.TRIGGERED_BY, "executes"),
            'check': (TemporalType.DEPENDS_ON, "checks"),
            'approve': (TemporalType.DEPENDS_ON, "requires approval of"),
            'cancel': (TemporalType.TRIGGERED_BY, "cancels"),
            'update': (TemporalType.TRIGGERED_BY, "updates"),
            'notify': (TemporalType.TRIGGERED_BY, "notifies about"),
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name_lower = node.name.lower()
                
                # Check if function name matches temporal patterns
                for pattern_word, (temporal_type, description) in temporal_patterns.items():
                    if pattern_word in func_name_lower:
                        # Extract entity references from function body
                        entities = self._extract_entity_references(node)
                        
                        # Create temporal relationships between entities
                        for i, entity1 in enumerate(entities):
                            for entity2 in entities[i+1:]:
                                self.graph.add_temporal_relationship(
                                    source=entity1,
                                    target=entity2,
                                    temporal_type=temporal_type,
                                    description=f"{description} {entity2.lower()}",
                                    evidence=[f"{node.name}() at line {node.lineno}"],
                                    confidence=0.7
                                )
    
    def _extract_entity_references(self, node: ast.AST) -> List[str]:
        """Extract entity references from a code node."""
        entities = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                # Check if this variable name matches an entity
                for pattern in self.ENTITY_PATTERNS:
                    if pattern.entity_type.lower() in child.id.lower():
                        if child.id not in entities:
                            entities.append(child.id)
            
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                    # Check if function name implies entity creation/manipulation
                    for pattern in self.ENTITY_PATTERNS:
                        if any(k in func_name.lower() for k in pattern.keywords):
                            if func_name not in entities:
                                entities.append(func_name)
        
        return entities
    
    def _get_type_hint(self, annotation: ast.expr) -> str:
        """Extract type hint from annotation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                base = annotation.value.id
                if isinstance(annotation.slice, ast.Name):
                    inner = annotation.slice.id
                    return f"{base}[{inner}]"
                return base
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        
        return "Unknown"
    
    def _infer_type_from_value(self, value: ast.expr) -> str:
        """Infer type from assignment value."""
        if isinstance(value, ast.List):
            return "List"
        elif isinstance(value, ast.Dict):
            return "Dict"
        elif isinstance(value, ast.Set):
            return "Set"
        elif isinstance(value, ast.Constant):
            return type(value.value).__name__
        elif isinstance(value, ast.Call):
            if isinstance(value.func, ast.Name):
                return value.func.id
        
        return "Unknown"
    
    def _get_name_from_node(self, node: ast.expr) -> Optional[str]:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name_from_node(node.value)
            if value:
                return f"{value}.{node.attr}"
        
        return None
    
    def analyze_from_text(self, code_text: str) -> SmartEntityGraph:
        """Analyze code from text."""
        return self.analyze_code(code_text)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate analysis report."""
        circular_deps = self.graph.detect_circular_dependencies()
        
        return {
            'summary': {
                'total_entities': len(self.graph.entities),
                'total_relationships': len(self.graph.relationships),
                'total_temporal_relationships': len(self.graph.temporal_relationships),
                'circular_dependencies_found': len(circular_deps)
            },
            'entities': list(self.graph.entities.keys()),
            'relationships': [
                {
                    'source': rel.source,
                    'target': rel.target,
                    'type': rel.relationship_type,
                    'cardinality': rel.cardinality.value,
                    'confidence': rel.confidence
                }
                for rel in self.graph.relationships
            ],
            'circular_dependencies': [
                {
                    'cycle': cd.cycle,
                    'severity': cd.severity,
                    'types': cd.dependency_types
                }
                for cd in circular_deps
            ],
            'cardinality_summary': self.graph.get_cardinality_summary()
        }
