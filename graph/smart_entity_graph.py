"""
Smart Entity Graph System

Learns and models relationships between entities with support for:
- Entity relationship modeling (Customer → Order → Payment)
- Cardinality tracking (1:1, 1:N, M:N)
- Temporal relationships (what happens before/after)
- Circular dependency detection
- Path analysis and traversal
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, deque
from enum import Enum
import json
from datetime import datetime


class Cardinality(Enum):
    """Relationship cardinality types."""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_ONE = "N:1"
    MANY_TO_MANY = "M:N"


class TemporalType(Enum):
    """Temporal relationship types."""
    BEFORE = "before"      # A happens before B
    AFTER = "after"        # A happens after B
    CONCURRENT = "concurrent"  # A and B happen at same time
    TRIGGERED_BY = "triggered_by"  # A triggers B
    BLOCKED_BY = "blocked_by"  # A is blocked by B
    DEPENDS_ON = "depends_on"  # A depends on B
    EVENTUALLY = "eventually"  # A eventually leads to B


@dataclass
class Entity:
    """Represents a business entity."""
    name: str
    entity_type: str  # e.g., 'Customer', 'Order', 'Payment'
    properties: Dict[str, str] = field(default_factory=dict)
    parent_entity: Optional[str] = None  # Aggregate root reference
    instances_count: int = 0  # Observed number of instances
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EntityRelationship:
    """Represents a relationship between two entities."""
    source: str  # Entity name
    target: str  # Entity name
    relationship_type: str  # e.g., 'CREATES', 'CONTAINS', 'BELONGS_TO'
    cardinality: Cardinality
    direction: str = "forward"  # 'forward', 'backward', 'bidirectional'
    properties: Dict[str, Any] = field(default_factory=dict)
    evidence_count: int = 0  # How many times we observed this relationship
    confidence: float = 0.5  # 0.0 to 1.0 confidence score
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary."""
        d = asdict(self)
        d['cardinality'] = self.cardinality.value
        return d


@dataclass
class TemporalRelationship:
    """Represents temporal/causal relationships between entities."""
    source: str  # Entity name
    target: str  # Entity name
    temporal_type: TemporalType
    description: str = ""
    evidence: List[str] = field(default_factory=list)  # Code references proving this relationship
    confidence: float = 0.5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary."""
        d = asdict(self)
        d['temporal_type'] = self.temporal_type.value
        return d


@dataclass
class CircularDependency:
    """Represents a circular dependency chain."""
    cycle: List[str]  # Entity names forming the cycle
    dependency_types: List[str]  # Types of relationships in the cycle
    severity: str  # 'critical', 'high', 'medium', 'low'
    found_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class SmartEntityGraph:
    """
    Manages a graph of entities with relationships, cardinality info,
    and temporal dependencies.
    """
    
    def __init__(self):
        """Initialize the entity graph."""
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[EntityRelationship] = []
        self.temporal_relationships: List[TemporalRelationship] = []
        self.circular_dependencies: List[CircularDependency] = []
        
        # Index structures for fast lookup
        self._relationships_by_source: Dict[str, List[int]] = defaultdict(list)
        self._relationships_by_target: Dict[str, List[int]] = defaultdict(list)
        self._temporal_by_source: Dict[str, List[int]] = defaultdict(list)
        self._temporal_by_target: Dict[str, List[int]] = defaultdict(list)
    
    def add_entity(self, name: str, entity_type: str, 
                   properties: Optional[Dict[str, str]] = None,
                   parent_entity: Optional[str] = None) -> Entity:
        """Add an entity to the graph."""
        if name in self.entities:
            # Update existing entity
            entity = self.entities[name]
            if properties:
                entity.properties.update(properties)
            if parent_entity:
                entity.parent_entity = parent_entity
            return entity
        
        entity = Entity(
            name=name,
            entity_type=entity_type,
            properties=properties or {},
            parent_entity=parent_entity
        )
        self.entities[name] = entity
        return entity
    
    def add_relationship(self, source: str, target: str, 
                        relationship_type: str,
                        cardinality: Cardinality,
                        direction: str = "forward",
                        properties: Optional[Dict[str, Any]] = None,
                        confidence: float = 0.5) -> EntityRelationship:
        """Add a relationship between two entities."""
        # Ensure entities exist
        if source not in self.entities:
            self.add_entity(source, "Unknown")
        if target not in self.entities:
            self.add_entity(target, "Unknown")
        
        # Check if relationship already exists
        for i, rel in enumerate(self.relationships):
            if rel.source == source and rel.target == target and rel.relationship_type == relationship_type:
                # Update existing relationship
                rel.evidence_count += 1
                rel.confidence = min(1.0, rel.confidence + 0.1)
                return rel
        
        # Create new relationship
        rel = EntityRelationship(
            source=source,
            target=target,
            relationship_type=relationship_type,
            cardinality=cardinality,
            direction=direction,
            properties=properties or {},
            evidence_count=1,
            confidence=confidence
        )
        
        idx = len(self.relationships)
        self.relationships.append(rel)
        self._relationships_by_source[source].append(idx)
        self._relationships_by_target[target].append(idx)
        
        return rel
    
    def add_temporal_relationship(self, source: str, target: str,
                                 temporal_type: TemporalType,
                                 description: str = "",
                                 evidence: Optional[List[str]] = None,
                                 confidence: float = 0.5) -> TemporalRelationship:
        """Add a temporal relationship between entities."""
        # Ensure entities exist
        if source not in self.entities:
            self.add_entity(source, "Unknown")
        if target not in self.entities:
            self.add_entity(target, "Unknown")
        
        temporal_rel = TemporalRelationship(
            source=source,
            target=target,
            temporal_type=temporal_type,
            description=description,
            evidence=evidence or [],
            confidence=confidence
        )
        
        idx = len(self.temporal_relationships)
        self.temporal_relationships.append(temporal_rel)
        self._temporal_by_source[source].append(idx)
        self._temporal_by_target[target].append(idx)
        
        return temporal_rel
    
    def get_entity_paths(self, start: str, end: str, max_depth: int = 5) -> List[List[str]]:
        """
        Find all paths between two entities.
        Returns list of paths, where each path is a list of entity names.
        """
        if start not in self.entities or end not in self.entities:
            return []
        
        paths = []
        visited = set()
        current_path = [start]
        
        def dfs(current: str, target: str, depth: int):
            if depth > max_depth:
                return
            
            if current == target:
                paths.append(current_path[:])
                return
            
            # Get all relationships from current entity
            for rel_idx in self._relationships_by_source.get(current, []):
                rel = self.relationships[rel_idx]
                next_entity = rel.target
                
                if next_entity not in visited or next_entity == target:
                    visited.add(next_entity)
                    current_path.append(next_entity)
                    dfs(next_entity, target, depth + 1)
                    current_path.pop()
                    visited.discard(next_entity)
        
        dfs(start, end, 0)
        return paths
    
    def detect_circular_dependencies(self) -> List[CircularDependency]:
        """
        Detect circular dependencies in the entity graph.
        Uses DFS to find cycles.
        """
        if self.circular_dependencies:  # Only compute once per graph state
            return self.circular_dependencies
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs_cycle(node: str, path: List[str], rel_types: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for rel_idx in self._relationships_by_source.get(node, []):
                rel = self.relationships[rel_idx]
                next_node = rel.target
                
                if next_node not in visited:
                    dfs_cycle(next_node, path, rel_types + [rel.relationship_type])
                
                elif next_node in rec_stack:
                    # Found a cycle
                    cycle_start_idx = path.index(next_node)
                    cycle = path[cycle_start_idx:] + [next_node]
                    cycle_rel_types = rel_types[cycle_start_idx:] + [rel.relationship_type]
                    
                    # Determine severity
                    severity = self._calculate_cycle_severity(cycle)
                    
                    circ_dep = CircularDependency(
                        cycle=cycle,
                        dependency_types=cycle_rel_types,
                        severity=severity
                    )
                    
                    if circ_dep not in cycles:
                        cycles.append(circ_dep)
            
            path.pop()
            rec_stack.discard(node)
        
        for entity_name in self.entities:
            if entity_name not in visited:
                dfs_cycle(entity_name, [], [])
        
        self.circular_dependencies = cycles
        return cycles
    
    def _calculate_cycle_severity(self, cycle: List[str]) -> str:
        """Calculate severity of a circular dependency."""
        if len(cycle) <= 2:
            return "critical"  # Direct cycle is worst
        elif len(cycle) <= 4:
            return "high"
        elif len(cycle) <= 6:
            return "medium"
        else:
            return "low"
    
    def get_entity_timeline(self, entity_name: str) -> Dict[str, Any]:
        """
        Get the temporal sequence of relationships for an entity.
        Shows what typically happens before/after this entity.
        """
        if entity_name not in self.entities:
            return {}
        
        before = []
        after = []
        triggers = []
        dependencies = []
        
        # Temporal relationships where this entity is the target (things before it)
        for rel_idx in self._temporal_by_target.get(entity_name, []):
            temporal_rel = self.temporal_relationships[rel_idx]
            if temporal_rel.temporal_type in [TemporalType.BEFORE, TemporalType.TRIGGERED_BY]:
                before.append({
                    'entity': temporal_rel.source,
                    'type': temporal_rel.temporal_type.value,
                    'description': temporal_rel.description
                })
        
        # Temporal relationships where this entity is the source (things after it)
        for rel_idx in self._temporal_by_source.get(entity_name, []):
            temporal_rel = self.temporal_relationships[rel_idx]
            if temporal_rel.temporal_type in [TemporalType.AFTER, TemporalType.TRIGGERED_BY]:
                after.append({
                    'entity': temporal_rel.target,
                    'type': temporal_rel.temporal_type.value,
                    'description': temporal_rel.description
                })
            elif temporal_rel.temporal_type == TemporalType.DEPENDS_ON:
                dependencies.append({
                    'entity': temporal_rel.target,
                    'description': temporal_rel.description
                })
        
        return {
            'entity': entity_name,
            'happens_before': before,
            'happens_after': after,
            'triggers': [t for t in after if t['type'] == 'triggered_by'],
            'depends_on': dependencies
        }
    
    def get_cardinality_summary(self) -> Dict[str, Any]:
        """Get summary of relationships grouped by cardinality."""
        summary = {
            Cardinality.ONE_TO_ONE: [],
            Cardinality.ONE_TO_MANY: [],
            Cardinality.MANY_TO_ONE: [],
            Cardinality.MANY_TO_MANY: [],
        }
        
        for rel in self.relationships:
            summary[rel.cardinality].append({
                'source': rel.source,
                'target': rel.target,
                'type': rel.relationship_type,
                'confidence': rel.confidence,
                'evidence': rel.evidence_count
            })
        
        return {
            'one_to_one': summary[Cardinality.ONE_TO_ONE],
            'one_to_many': summary[Cardinality.ONE_TO_MANY],
            'many_to_one': summary[Cardinality.MANY_TO_ONE],
            'many_to_many': summary[Cardinality.MANY_TO_MANY],
            'total_relationships': len(self.relationships)
        }
    
    def get_related_entities(self, entity_name: str, 
                            depth: int = 1) -> Dict[str, List[str]]:
        """Get entities related to the given entity at specified depth."""
        if entity_name not in self.entities:
            return {}
        
        result = {'direct': [], 'depth_2': [], 'depth_3': []}
        visited = {entity_name}
        current_level = {entity_name}
        
        for d in range(1, min(depth + 1, 4)):
            next_level = set()
            for entity in current_level:
                for rel_idx in self._relationships_by_source.get(entity, []):
                    rel = self.relationships[rel_idx]
                    if rel.target not in visited:
                        next_level.add(rel.target)
                        visited.add(rel.target)
                        
                        level_key = 'direct' if d == 1 else f'depth_{d}'
                        if level_key in result:
                            result[level_key].append(rel.target)
            
            current_level = next_level
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire graph to dictionary."""
        return {
            'entities': {name: entity.to_dict() for name, entity in self.entities.items()},
            'relationships': [rel.to_dict() for rel in self.relationships],
            'temporal_relationships': [rel.to_dict() for rel in self.temporal_relationships],
            'circular_dependencies': [cd.to_dict() for cd in self.circular_dependencies],
            'stats': {
                'total_entities': len(self.entities),
                'total_relationships': len(self.relationships),
                'total_temporal_relationships': len(self.temporal_relationships),
                'total_circular_dependencies': len(self.circular_dependencies)
            }
        }
    
    def to_cypher(self) -> List[str]:
        """Convert graph to Neo4j Cypher statements."""
        statements = []
        
        # Create entities
        for entity in self.entities.values():
            props = ", ".join([f"{k}: '{v}'" for k, v in entity.properties.items()])
            props_str = f", {props}" if props else ""
            stmt = f"MERGE (e:{entity.entity_type} {{name: '{entity.name}'{props_str}}})"
            statements.append(stmt)
        
        # Create relationships
        for rel in self.relationships:
            cardinality_str = rel.cardinality.value
            stmt = f"MATCH (s:{self.entities[rel.source].entity_type} {{name: '{rel.source}'}}), " \
                   f"(t:{self.entities[rel.target].entity_type} {{name: '{rel.target}'}}) " \
                   f"MERGE (s)-[:{rel.relationship_type} {{cardinality: '{cardinality_str}', " \
                   f"confidence: {rel.confidence}}}]->(t)"
            statements.append(stmt)
        
        # Create temporal relationships
        for temp_rel in self.temporal_relationships:
            stmt = f"MATCH (s:{self.entities[temp_rel.source].entity_type} {{name: '{temp_rel.source}'}}), " \
                   f"(t:{self.entities[temp_rel.target].entity_type} {{name: '{temp_rel.target}'}}) " \
                   f"MERGE (s)-[:{temp_rel.temporal_type.value} {{description: '{temp_rel.description}'}}]->(t)"
            statements.append(stmt)
        
        return statements
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        """Convert to JSON and optionally save to file."""
        json_str = json.dumps(self.to_dict(), indent=2, default=str)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def visualize_dot(self) -> str:
        """Generate GraphViz DOT format for visualization."""
        lines = ["digraph EntityGraph {", "  rankdir=LR;", "  node [shape=box];"]
        
        # Add entities as nodes
        for entity in self.entities.values():
            label = f"{entity.name}\\n({entity.entity_type})"
            lines.append(f'  "{entity.name}" [label="{label}"];')
        
        # Add relationships as edges
        for rel in self.relationships:
            cardinality = rel.cardinality.value
            style = f"label=\"{cardinality}\"" if rel.confidence > 0.7 else f"label=\"{cardinality}\" style=dashed"
            lines.append(f'  "{rel.source}" -> "{rel.target}" [{style}];')
        
        # Add temporal relationships with special styling
        for temp_rel in self.temporal_relationships:
            lines.append(f'  "{temp_rel.source}" -> "{temp_rel.target}" [label="{temp_rel.temporal_type.value}" style=dotted color=blue];')
        
        lines.append("}")
        return "\n".join(lines)
