"""
Smart Entity Graph Demo

Demonstrates the complete entity graph system with:
- E-commerce entity relationships (Customer → Order → Payment → Shipment)
- Cardinality tracking (1:1, 1:N, M:N relationships)
- Temporal relationships (what happens before/after)
- Circular dependency detection
- Real-world business logic analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.smart_entity_graph import (
    SmartEntityGraph, Cardinality, TemporalType, EntityRelationship
)
from graph.entity_graph_analyzer import EntityGraphAnalyzer
import json


def demo_ecommerce_graph():
    """
    Demonstrate entity graph with e-commerce domain.
    Shows Customer → Order → Payment → Shipment relationships
    with proper cardinality and temporal constraints.
    """
    print("=" * 70)
    print("SMART ENTITY GRAPH DEMO: E-Commerce Domain")
    print("=" * 70)
    
    # Create graph
    graph = SmartEntityGraph()
    
    # ====== PHASE 1: Add Entities ======
    print("\n📦 PHASE 1: Adding Entities")
    print("-" * 70)
    
    entities = [
        ("Customer", "Customer", {"status": "active_or_inactive", "tier": "bronze_silver_gold"}),
        ("Order", "Order", {"status": "pending_processing_shipped_delivered"}),
        ("OrderItem", "OrderItem", {"status": "pending_fulfilled_cancelled"}),
        ("Payment", "Payment", {"status": "pending_completed_failed_refunded"}),
        ("Shipment", "Shipment", {"status": "pending_in_transit_delivered"}),
        ("Product", "Product", {"status": "active_discontinued"}),
        ("Inventory", "Inventory", {"unit": "quantity"}),
        ("Invoice", "Invoice", {"status": "draft_sent_paid_overdue"}),
        ("Review", "Review", {"rating": "1_to_5_stars"}),
    ]
    
    for entity_name, entity_type, properties in entities:
        graph.add_entity(entity_name, entity_type, properties)
        print(f"✓ Added entity: {entity_name} ({entity_type})")
    
    # ====== PHASE 2: Add Relationships with Cardinality ======
    print("\n\n🔗 PHASE 2: Adding Relationships with Cardinality")
    print("-" * 70)
    
    relationships = [
        # Customer → Order (1:N) - one customer can have many orders
        ("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY, "forward",
         "A customer places multiple orders"),
        
        # Order → OrderItem (1:N) - one order has multiple items
        ("Order", "OrderItem", "CONTAINS", Cardinality.ONE_TO_MANY, "forward",
         "An order contains multiple items"),
        
        # OrderItem → Product (M:N) - many items reference products
        ("OrderItem", "Product", "REFERENCES", Cardinality.MANY_TO_ONE, "forward",
         "Order items reference products"),
        
        # Product → Inventory (1:1) - one product has one inventory record
        ("Product", "Inventory", "TRACKS", Cardinality.ONE_TO_ONE, "forward",
         "Each product tracks inventory"),
        
        # Order → Payment (1:N) - one order can have multiple payments
        ("Order", "Payment", "HAS", Cardinality.ONE_TO_MANY, "forward",
         "An order may have multiple payments (installments)"),
        
        # Order → Shipment (1:N) - one order can have multiple shipments
        ("Order", "Shipment", "GENERATES", Cardinality.ONE_TO_MANY, "forward",
         "An order generates shipment(s)"),
        
        # Order → Invoice (1:N) - one order can generate multiple invoices
        ("Order", "Invoice", "CREATES", Cardinality.ONE_TO_MANY, "forward",
         "An order creates invoice(s)"),
        
        # Customer → Payment (1:N) - customer has multiple payments
        ("Customer", "Payment", "MAKES", Cardinality.ONE_TO_MANY, "forward",
         "A customer makes multiple payments"),
        
        # Product → Review (1:N) - product has multiple reviews
        ("Product", "Review", "RECEIVES", Cardinality.ONE_TO_MANY, "forward",
         "A product receives reviews from customers"),
        
        # Customer → Review (1:N) - customer writes multiple reviews
        ("Customer", "Review", "WRITES", Cardinality.ONE_TO_MANY, "forward",
         "A customer writes multiple reviews"),
    ]
    
    for source, target, rel_type, cardinality, direction, description in relationships:
        graph.add_relationship(
            source=source,
            target=target,
            relationship_type=rel_type,
            cardinality=cardinality,
            direction=direction,
            properties={'description': description},
            confidence=0.9
        )
        print(f"✓ {source} →[{rel_type}]→ {target} | Cardinality: {cardinality.value}")
    
    # ====== PHASE 3: Add Temporal Relationships ======
    print("\n\n⏰ PHASE 3: Adding Temporal Relationships")
    print("-" * 70)
    
    temporal_rels = [
        # What must happen before Order processing
        ("Customer", "Order", TemporalType.BEFORE, "Customer must exist and be authenticated"),
        
        # Order → Payment sequence
        ("Order", "Payment", TemporalType.TRIGGERED_BY, "Order creation triggers payment processing"),
        
        # Payment → Shipment dependency
        ("Payment", "Shipment", TemporalType.DEPENDS_ON, "Shipment depends on successful payment"),
        
        # Order → Inventory check
        ("Order", "Inventory", TemporalType.DEPENDS_ON, "Order fulfillment depends on inventory availability"),
        
        # Shipment → Invoice
        ("Shipment", "Invoice", TemporalType.TRIGGERED_BY, "Shipment completion can trigger invoice generation"),
        
        # Product review after delivery
        ("Shipment", "Review", TemporalType.EVENTUALLY, "Customer can review product after receiving shipment"),
        
        # Payment failure blocks shipment
        ("Payment", "Shipment", TemporalType.BLOCKED_BY, "Shipment is blocked if payment fails"),
    ]
    
    for source, target, temporal_type, description in temporal_rels:
        graph.add_temporal_relationship(
            source=source,
            target=target,
            temporal_type=temporal_type,
            description=description,
            confidence=0.85
        )
        print(f"✓ {source} →[{temporal_type.value}]→ {target}")
        print(f"  └─ {description}")
    
    # ====== PHASE 4: Analyze the Graph ======
    print("\n\n📊 PHASE 4: Graph Analysis")
    print("-" * 70)
    
    # 4a. Cardinality Summary
    print("\n4a. Cardinality Distribution:")
    cardinality_summary = graph.get_cardinality_summary()
    print(f"   1:1 Relationships: {len(cardinality_summary['one_to_one'])}")
    for rel in cardinality_summary['one_to_one']:
        print(f"     └─ {rel['source']} ←[{rel['type']}]→ {rel['target']}")
    
    print(f"\n   1:N Relationships: {len(cardinality_summary['one_to_many'])}")
    for rel in cardinality_summary['one_to_many'][:3]:  # Show first 3
        print(f"     └─ {rel['source']} ←[{rel['type']}]→ {rel['target']}")
    if len(cardinality_summary['one_to_many']) > 3:
        print(f"     └─ ... and {len(cardinality_summary['one_to_many']) - 3} more")
    
    # 4b. Entity Timelines
    print("\n4b. Entity Timelines (Temporal Sequences):")
    for entity_name in ["Customer", "Order", "Payment", "Shipment"]:
        timeline = graph.get_entity_timeline(entity_name)
        if timeline.get('happens_before') or timeline.get('happens_after'):
            print(f"\n   {entity_name}:")
            if timeline.get('happens_before'):
                for rel in timeline['happens_before']:
                    print(f"     ← {rel['entity']} ({rel['type']})")
            if timeline.get('happens_after'):
                for rel in timeline['happens_after']:
                    print(f"     → {rel['entity']} ({rel['type']})")
    
    # 4c. Related Entities
    print("\n\n4c. Related Entities (by distance):")
    related = graph.get_related_entities("Customer", depth=3)
    print(f"   Direct neighbors of Customer: {related['direct']}")
    if related.get('depth_2'):
        print(f"   2 hops from Customer: {related['depth_2']}")
    if related.get('depth_3'):
        print(f"   3 hops from Customer: {related['depth_3']}")
    
    # 4d. Path Finding
    print("\n\n4d. Entity Traversal Paths:")
    paths = graph.get_entity_paths("Customer", "Shipment")
    print(f"   Paths from Customer to Shipment:")
    for i, path in enumerate(paths, 1):
        print(f"     {i}. {' → '.join(path)}")
    
    # 4e. Circular Dependencies
    print("\n\n4e. Circular Dependency Detection:")
    circular_deps = graph.detect_circular_dependencies()
    if circular_deps:
        print(f"   ⚠️  Found {len(circular_deps)} circular dependencies:")
        for i, dep in enumerate(circular_deps, 1):
            print(f"     {i}. {' → '.join(dep.cycle)} (Severity: {dep.severity})")
    else:
        print("   ✓ No circular dependencies detected (Good design!)")
    
    return graph


def demo_code_analysis():
    """
    Demonstrate extracting entities from actual code.
    """
    print("\n\n" + "=" * 70)
    print("CODE-BASED ENTITY EXTRACTION DEMO")
    print("=" * 70)
    
    # Sample e-commerce code
    sample_code = '''
class Customer:
    """Represents a customer in the system."""
    name: str
    email: str
    orders: List[Order] = []
    
    def create_order(self) -> Order:
        """Customer creates an order."""
        order = Order(customer=self)
        self.orders.append(order)
        return order

class Order:
    """Represents a customer order."""
    customer: Customer
    items: List[OrderItem] = []
    payments: List[Payment] = []
    shipment: Shipment = None
    
    def add_item(self, product: Product, quantity: int):
        """Add item to order."""
        inventory = product.inventory
        if inventory.available >= quantity:
            item = OrderItem(order=self, product=product)
            self.items.append(item)
    
    def process_payment(self) -> Payment:
        """Process payment for order."""
        payment = Payment(order=self)
        payment.process()
        self.payments.append(payment)
        return payment
    
    def create_shipment(self) -> Shipment:
        """Create shipment after payment confirmed."""
        if self.is_paid():
            self.shipment = Shipment(order=self)
        return self.shipment

class OrderItem:
    """Line item in an order."""
    order: Order
    product: Product
    quantity: int

class Product:
    """Product catalog item."""
    name: str
    inventory: Inventory
    reviews: List[Review] = []

class Inventory:
    """Inventory tracking for products."""
    product: Product
    available: int
    reserved: int

class Payment:
    """Payment for an order."""
    order: Order
    amount: float
    status: str
    
    def process(self):
        """Validate and process payment."""
        if self.validate():
            self.status = "completed"

class Shipment:
    """Shipment of an order."""
    order: Order
    items: List[OrderItem]
    status: str = "pending"
    
    def mark_delivered(self):
        """Mark shipment as delivered."""
        self.status = "delivered"
        self.notify_customer()
    
    def notify_customer(self):
        """Notify customer of delivery."""
        customer = self.order.customer
        # Send notification...

class Review:
    """Product review."""
    product: Product
    customer: Customer
    rating: int
    text: str
    '''
    
    print("\n📝 Analyzing code sample (E-commerce system)...")
    analyzer = EntityGraphAnalyzer()
    graph = analyzer.analyze_code(sample_code, "ecommerce.py")
    
    print("\n✓ Analysis complete!")
    
    # Generate report
    report = analyzer.generate_report()
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total Entities Found: {report['summary']['total_entities']}")
    print(f"   Total Relationships: {report['summary']['total_relationships']}")
    print(f"   Temporal Relationships: {report['summary']['total_temporal_relationships']}")
    print(f"   Circular Dependencies: {report['summary']['circular_dependencies_found']}")
    
    print(f"\n📋 Entities Discovered:")
    for entity in report['entities']:
        print(f"   • {entity}")
    
    print(f"\n🔗 Relationships Discovered:")
    for rel in report['relationships'][:5]:
        print(f"   {rel['source']} →[{rel['type']}]→ {rel['target']} ({rel['cardinality']})")
    if len(report['relationships']) > 5:
        print(f"   ... and {len(report['relationships']) - 5} more")
    
    if report['circular_dependencies']:
        print(f"\n⚠️  Circular Dependencies Detected:")
        for cd in report['circular_dependencies']:
            print(f"   {' → '.join(cd['cycle'])} [Severity: {cd['severity']}]")
    
    return graph


def demo_export_formats():
    """
    Demonstrate exporting the entity graph in various formats.
    """
    print("\n\n" + "=" * 70)
    print("EXPORT FORMATS DEMO")
    print("=" * 70)
    
    graph = SmartEntityGraph()
    
    # Add minimal graph for export demo
    graph.add_entity("Customer", "Customer")
    graph.add_entity("Order", "Order")
    graph.add_entity("Payment", "Payment")
    
    graph.add_relationship(
        "Customer", "Order", "PLACES",
        Cardinality.ONE_TO_MANY, confidence=0.9
    )
    graph.add_relationship(
        "Order", "Payment", "HAS",
        Cardinality.ONE_TO_MANY, confidence=0.9
    )
    
    # 1. JSON Export
    print("\n1️⃣  JSON Export:")
    json_str = graph.to_json()
    parsed = json.loads(json_str)
    print(f"   Entities: {len(parsed['entities'])}")
    print(f"   Relationships: {len(parsed['relationships'])}")
    
    # 2. Cypher Export
    print("\n2️⃣  Neo4j Cypher Export:")
    cypher_stmts = graph.to_cypher()
    print(f"   Generated {len(cypher_stmts)} Cypher statements")
    print("   Sample statements:")
    for stmt in cypher_stmts[:2]:
        print(f"     {stmt}")
    
    # 3. GraphViz DOT Export
    print("\n3️⃣  GraphViz DOT Export:")
    dot_str = graph.visualize_dot()
    print("   DOT graph generated for visualization")
    print("   Sample DOT content:")
    for line in dot_str.split('\n')[:5]:
        print(f"     {line}")
    
    return graph


def demo_cardinality_inference():
    """
    Demonstrate how cardinality is inferred from relationship patterns.
    """
    print("\n\n" + "=" * 70)
    print("CARDINALITY INFERENCE DEMO")
    print("=" * 70)
    
    graph = SmartEntityGraph()
    
    print("\n📚 Understanding Cardinality:")
    print("   1:1  - One-to-one: Each Customer has exactly one Account")
    print("   1:N  - One-to-many: One Customer can have many Orders")
    print("   N:1  - Many-to-one: Many Payments belong to one Order")
    print("   M:N  - Many-to-many: Many Products can be in many Orders")
    
    # Create examples
    examples = [
        ("Customer", "Account", "HAS", Cardinality.ONE_TO_ONE, 
         "Each customer has one account"),
        ("Customer", "Order", "PLACES", Cardinality.ONE_TO_MANY,
         "One customer places multiple orders"),
        ("OrderItem", "Product", "CONTAINS", Cardinality.MANY_TO_ONE,
         "Many order items reference products"),
        ("Product", "Category", "BELONGS_TO", Cardinality.MANY_TO_MANY,
         "Products belong to multiple categories"),
    ]
    
    print("\n📋 Cardinality Examples:")
    for source, target, rel_type, card, description in examples:
        graph.add_entity(source, source)
        graph.add_entity(target, target)
        graph.add_relationship(
            source, target, rel_type, card, confidence=0.9
        )
        print(f"   {source} →[{rel_type}:{card.value}]→ {target}")
        print(f"      └─ {description}")
    
    cardinality_summary = graph.get_cardinality_summary()
    print(f"\n📊 Cardinality Summary:")
    for card_type in ['one_to_one', 'one_to_many', 'many_to_one', 'many_to_many']:
        rels = cardinality_summary[card_type]
        print(f"   {card_type.upper()}: {len(rels)} relationships")
    
    return graph


def main():
    """Run all demos."""
    print("\n\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🎯 SMART ENTITY GRAPH - Comprehensive Demonstration  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run all demos
    graph1 = demo_ecommerce_graph()
    graph2 = demo_code_analysis()
    graph3 = demo_cardinality_inference()
    demo_export_formats()
    
    print("\n\n" + "=" * 70)
    print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\n🎓 Key Takeaways:")
    print("   1. Entities model business domain objects (Customer, Order, etc.)")
    print("   2. Relationships define how entities connect with cardinality info")
    print("   3. Temporal relationships capture sequence and dependencies")
    print("   4. Circular dependencies are detected and flagged for design review")
    print("   5. Multiple export formats support various tools and frameworks")
    print("\n🚀 Next Steps:")
    print("   • Use in business logic analysis")
    print("   • Integrate with Neo4j for graph database storage")
    print("   • Visualize with GraphViz or Neo4j visualization")
    print("   • Export to documentation and architecture diagrams")
    print("\n")


if __name__ == "__main__":
    main()
