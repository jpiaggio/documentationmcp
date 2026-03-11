# Smart Entity Graph - Quick Reference Guide

Quick-start reference for building and querying entity graphs.

## 30-Second Tutorial

```python
from graph.smart_entity_graph import SmartEntityGraph, Cardinality, TemporalType

# Create graph
graph = SmartEntityGraph()

# Add entities
graph.add_entity("Customer", "Customer")
graph.add_entity("Order", "Order")
graph.add_entity("Payment", "Payment")

# Add relationships with cardinality
graph.add_relationship("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY)
graph.add_relationship("Order", "Payment", "HAS", Cardinality.ONE_TO_MANY)

# Add temporal relationships
graph.add_temporal_relationship("Order", "Payment", TemporalType.TRIGGERED_BY)

# Analyze
paths = graph.get_entity_paths("Customer", "Payment")  # Customer → Order → Payment
cycles = graph.detect_circular_dependencies()  # Check for circular dependencies
timeline = graph.get_entity_timeline("Order")  # What happens before/after?

print(f"✓ Graph ready: {len(graph.entities)} entities, {len(graph.relationships)} relationships")
```

## Entity Operations

### Adding Entities
```python
# Simple entity
graph.add_entity("Customer", "Customer")

# With properties
graph.add_entity("Order", "Order", 
    properties={"status": "pending_processing_shipped"})

# With parent aggregate
graph.add_entity("OrderItem", "OrderItem", 
    parent_entity="Order")
```

### Updating Entities
Entities are automatically updated if you add them again with new properties:
```python
e1 = graph.add_entity("Product", "Product")
e2 = graph.add_entity("Product", "Product", 
    properties={"category": "electronics"})
# e1 and e2 reference same object, updated with new properties
```

## Relationship Operations

### Cardinality Cheat Sheet
```python
from graph.smart_entity_graph import Cardinality

# 1:1 - One-to-one (unique pairs)
Cardinality.ONE_TO_ONE      # Customer has Account
graph.add_relationship("Customer", "Account", "HAS", Cardinality.ONE_TO_ONE)

# 1:N - One-to-many (one parent, multiple children)
Cardinality.ONE_TO_MANY     # Customer places Orders
graph.add_relationship("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY)

# N:1 - Many-to-one (multiple children, one parent)
Cardinality.MANY_TO_ONE     # Payments belong to Order
graph.add_relationship("Payment", "Order", "BELONGS_TO", Cardinality.MANY_TO_ONE)

# M:N - Many-to-many (multiple relationships each side)
Cardinality.MANY_TO_MANY    # Products in Orders
graph.add_relationship("Product", "Order", "IN", Cardinality.MANY_TO_MANY)
```

### Adding Relationships
```python
# Basic
graph.add_relationship("A", "B", "RELATES", Cardinality.ONE_TO_ONE)

# With confidence score
graph.add_relationship("A", "B", "RELATES", Cardinality.ONE_TO_ONE, 
    confidence=0.95)  # 0.0 = uncertain, 1.0 = certain

# With metadata
graph.add_relationship("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY,
    properties={"created_at": "2024-01-01"})

# Bidirectional
graph.add_relationship("Person", "Team", "MEMBER_OF", Cardinality.MANY_TO_MANY,
    direction="bidirectional")
```

## Temporal Relationship Operations

### Types
```python
from graph.smart_entity_graph import TemporalType

TemporalType.BEFORE        # A happens before B
TemporalType.AFTER         # A happens after B
TemporalType.CONCURRENT    # A and B at same time
TemporalType.TRIGGERED_BY  # A triggers B
TemporalType.BLOCKED_BY    # A blocks B
TemporalType.DEPENDS_ON    # A depends on B
TemporalType.EVENTUALLY    # A eventually leads to B
```

### Adding Temporal Relationships
```python
# Customer must exist before Order
graph.add_temporal_relationship("Customer", "Order", TemporalType.BEFORE,
    description="Customer must be authenticated first")

# Order triggers Payment
graph.add_temporal_relationship("Order", "Payment", TemporalType.TRIGGERED_BY,
    description="Order creation triggers payment processing",
    confidence=0.9)

# Shipment blocks without Payment
graph.add_temporal_relationship("Payment", "Shipment", TemporalType.DEPENDS_ON,
    description="Shipment waits for successful payment",
    evidence=["payment_service.py:42", "shipment_service.py:156"])
```

## Query & Analysis

### Find Paths
```python
# All paths between two entities
paths = graph.get_entity_paths("Customer", "Shipment", max_depth=5)
for path in paths:
    print(" → ".join(path))
# Output:
# Customer → Order → Shipment
# Customer → Order → OrderItem → Product → Inventory

# Single path for quick lookup
if paths:
    shortest = min(paths, key=len)
```

### Related Entities
```python
# Get neighbors at different distances
related = graph.get_related_entities("Customer", depth=3)

related['direct']   # Direct outgoing: ['Order', 'Payment', 'Review']
related['depth_2']  # 2 hops: ['OrderItem', 'Shipment', 'Invoice']
related['depth_3']  # 3 hops: ['Product']
```

### Entity Timeline
```python
# What happens before/after/dependent on an entity?
timeline = graph.get_entity_timeline("Order")

timeline['happens_before']  # [{'entity': 'Customer', 'type': 'before'}]
timeline['happens_after']   # [{'entity': 'Payment', 'type': 'triggered_by'}]
timeline['depends_on']      # [{'entity': 'Inventory', ...}]
```

### Detect Circular Dependencies
```python
cycles = graph.detect_circular_dependencies()

if cycles:
    for cycle in cycles:
        print(f"⚠️  {' → '.join(cycle.cycle)}")
        print(f"   Severity: {cycle.severity}")  # critical, high, medium, low
else:
    print("✓ No circular dependencies")
```

### Cardinality Summary
```python
summary = graph.get_cardinality_summary()

for rel in summary['one_to_one']:
    print(f"{rel['source']} ←[1:1]→ {rel['target']}")

print(f"Total: {summary['total_relationships']} relationships")
```

## Export Formats

### JSON Export
```python
# To string
json_str = graph.to_json()

# To file
graph.to_json("entity_graph.json")

# Load back
import json
with open("entity_graph.json") as f:
    data = json.load(f)
```

### Neo4j Cypher Export
```python
# Generate Cypher statements
cypher_stmts = graph.to_cypher()

# Execute against Neo4j
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687")
with driver.session() as session:
    for stmt in cypher_stmts:
        session.run(stmt)
```

### GraphViz DOT Export
```python
# Generate DOT format
dot = graph.visualize_dot()

# Save and render
with open("graph.dot", "w") as f:
    f.write(dot)

# Render to PNG
# $ dot -Tpng graph.dot -o graph.png

# Or use online viewer: https://dreampuf.github.io/GraphvizOnline/
```

## Code Analysis

### Extract Entities from Source Code
```python
from graph.entity_graph_analyzer import EntityGraphAnalyzer

analyzer = EntityGraphAnalyzer()

# From file
with open("models.py") as f:
    code = f.read()
graph = analyzer.analyze_code(code, "models.py")

# From string
graph = analyzer.analyze_code(source_code_string)
```

### Generate Analysis Report
```python
report = analyzer.generate_report()

print(f"Entities: {report['summary']['total_entities']}")
print(f"Relationships: {report['summary']['total_relationships']}")
print(f"Temporal deps: {report['summary']['total_temporal_relationships']}")
print(f"Cycles: {report['summary']['circular_dependencies_found']}")

# List entities discovered
for entity in report['entities']:
    print(f"  • {entity}")

# List relationships
for rel in report['relationships']:
    print(f"  {rel['source']} →[{rel['cardinality']}]→ {rel['target']}")
```

## Common Patterns

### E-Commerce Graph
```python
from graph.smart_entity_graph import SmartEntityGraph, Cardinality, TemporalType

graph = SmartEntityGraph()

# Entities
for e in ["Customer", "Order", "OrderItem", "Product", "Payment", "Shipment"]:
    graph.add_entity(e, e)

# Relationships  
graph.add_relationship("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY)
graph.add_relationship("Order", "OrderItem", "CONTAINS", Cardinality.ONE_TO_MANY)
graph.add_relationship("OrderItem", "Product", "REFERENCES", Cardinality.MANY_TO_ONE)
graph.add_relationship("Order", "Payment", "HAS", Cardinality.ONE_TO_MANY)
graph.add_relationship("Order", "Shipment", "GENERATES", Cardinality.ONE_TO_MANY)

# Temporal
graph.add_temporal_relationship("Order", "Payment", TemporalType.TRIGGERED_BY)
graph.add_temporal_relationship("Payment", "Shipment", TemporalType.DEPENDS_ON)
```

### Microservice Architecture
```python
# Services as entities
graph.add_entity("UserService", "Service")
graph.add_entity("OrderService", "Service")
graph.add_entity("PaymentService", "Service")

# Service dependencies
graph.add_relationship("OrderService", "UserService", "DEPENDS_ON", Cardinality.MANY_TO_ONE)
graph.add_relationship("OrderService", "PaymentService", "CALLS", Cardinality.MANY_TO_ONE)

# Detect if OrderService creates circular dependency
cycles = graph.detect_circular_dependencies()
```

### Workflow States
```python
# States as entities
states = ["Pending", "Processing", "Completed", "Failed", "Cancelled"]
for state in states:
    graph.add_entity(state, "OrderState")

# State transitions as temporal relationships
graph.add_temporal_relationship("Pending", "Processing", TemporalType.TRIGGERED_BY)
graph.add_temporal_relationship("Processing", "Completed", TemporalType.TRIGGERED_BY)
graph.add_temporal_relationship("Processing", "Failed", TemporalType.EVENTUALLY)
```

## Troubleshooting

### Issue: Import errors
```python
# Make sure you're in the correct directory
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph.smart_entity_graph import SmartEntityGraph
```

### Issue: No relationships found
```python
# Check entities exist first
if "Customer" not in graph.entities:
    graph.add_entity("Customer", "Customer")

# Ensure both source and target are added before relationship
graph.add_entity("Order", "Order")
graph.add_relationship("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY)
```

### Issue: Many cycles detected
```python
# This might indicate architectural issues
# Analyze severity:
cycles = graph.detect_circular_dependencies()
critical = [c for c in cycles if c.severity == "critical"]
high = [c for c in cycles if c.severity == "high"]

print(f"Critical: {len(critical)} cycles (fix immediately)")
print(f"High: {len(high)} cycles (refactor recommended)")
```

## Performance Tips

### For Large Graphs (1000+ entities)
```python
# Build index separately if analyzing frequently
# Build once:
graph.detect_circular_dependencies()  # Caches results

# Use get_related_entities instead of get_entity_paths for single hops
related = graph.get_related_entities("Start", depth=1)
```

### For Code Analysis
```python
# Analyze large codebases in chunks
from pathlib import Path
analyzer = EntityGraphAnalyzer()

for py_file in Path(".").glob("**/*.py"):
    with open(py_file) as f:
        code = f.read()
    analyzer.analyze_code(code, str(py_file))
    
# Or use concurrency (be careful with memory)
from concurrent.futures import ThreadPoolExecutor
```

## Common Commands Cheat Sheet

```python
# Add entity
graph.add_entity(name, type)

# Add relationship
graph.add_relationship(source, target, type, cardinality)

# Add temporal
graph.add_temporal_relationship(source, target, temporal_type)

# Query
graph.get_entity_paths(start, end)
graph.get_related_entities(entity, depth=n)
graph.get_entity_timeline(entity)

# Analyze  
graph.detect_circular_dependencies()
graph.get_cardinality_summary()

# Export
graph.to_json()
graph.to_cypher()
graph.visualize_dot()

# Code analysis
analyzer = EntityGraphAnalyzer()
graph = analyzer.analyze_code(code)
report = analyzer.generate_report()
```

## Resources

- **Full Guide**: [SMART_ENTITY_GRAPH_GUIDE.md](SMART_ENTITY_GRAPH_GUIDE.md)
- **Demo**: Run `python3 agents/entity_graph_demo.py`
- **Implementation**: [graph/smart_entity_graph.py](graph/smart_entity_graph.py)
- **Code Analysis**: [graph/entity_graph_analyzer.py](graph/entity_graph_analyzer.py)

---

**Need help?** Check the comprehensive guide for detailed explanations and examples.
