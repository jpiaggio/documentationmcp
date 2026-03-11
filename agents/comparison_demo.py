#!/usr/bin/env python3
"""
Comparison Demo: Keyword-Based vs Semantic Analysis

Shows the differences between the old keyword-matching approach
and the new semantic analysis approach.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from business_rules_extractor import BusinessRulesExtractor
from enhanced_business_extractor import EnhancedBusinessExtractor


# Sample code demonstrating business logic
SAMPLE_CODE = '''
class Order:
    """Represents a customer order."""
    def __init__(self, customer_id, items):
        self.customer_id = customer_id
        self.items = items
        self.status = "pending"
    
    def validate_order(self):
        """Validate order before processing."""
        if not self.items:
            raise ValueError("Order must contain items")
        
        total = sum(item.price for item in self.items)
        if total > 1000:
            raise ValueError("Order total exceeds limit")
        
        return True
    
    def process_payment(self, payment_method):
        """Process payment through the payment gateway."""
        if payment_method.is_expired():
            raise PermissionError("Payment method expired")
        
        # Call Stripe API to process
        stripe_response = stripe.charge(
            amount=self.calculate_total(),
            customer_id=self.customer_id,
            payment_method=payment_method
        )
        
        if stripe_response.success:
            self.status = "paid"
            self.emit_event("order_paid")
            return True
        else:
            self.status = "payment_failed"
            self.emit_event("order_failed")
            return False
    
    def ship_order(self):
        """Ship the order to customer."""
        if self.status != "paid":
            raise ValueError("Cannot ship unpaid order")
        
        for item in self.items:
            item.decrease_inventory()
        
        self.status = "shipped"
        self.emit_event("order_shipped")
        
        # Notify customer
        send_email(
            to=self.customer.email,
            subject="Your order has shipped",
            template="order_shipped"
        )
    
    def emit_event(self, event_name):
        """Emit business event."""
        kafka.publish(f"orders.{event_name}", {
            "order_id": self.id,
            "timestamp": now(),
            "status": self.status
        })
    
    def calculate_total(self):
        """Calculate total order amount."""
        return sum(item.price * item.quantity for item in self.items)
'''


def compare_extraction():
    """Compare keyword-based vs semantic extraction."""
    
    print("=" * 80)
    print("COMPARISON: Keyword-Based vs Semantic Analysis")
    print("=" * 80)
    
    # Run both extractors
    keyword_extractor = BusinessRulesExtractor()
    semantic_extractor = EnhancedBusinessExtractor()
    
    keyword_results = keyword_extractor.extract_all_business_insights(SAMPLE_CODE, 'order.py')
    semantic_results = semantic_extractor.extract_all_enhanced_insights(SAMPLE_CODE, 'order.py')
    
    # Compare workflows
    print("\n\n📋 WORKFLOWS\n" + "-" * 80)
    print(f"\nKeyword-Based: {len(keyword_results.get('processes', []))} found")
    for w in keyword_results.get('processes', [])[:3]:
        print(f"  - {w['name']}")
    
    print(f"\nSemantic-Based: {len(semantic_results.get('workflows', []))} found")
    for w in semantic_results.get('workflows', [])[:3]:
        print(f"  - {w['name']}")
        if w.get('functions_called'):
            print(f"    Calls: {', '.join(w['functions_called'][:5])}")
    
    # Compare entities
    print("\n\n📦 BUSINESS ENTITIES\n" + "-" * 80)
    print(f"\nKeyword-Based: {len(keyword_results.get('entities', []))} found")
    for e in keyword_results.get('entities', [])[:3]:
        print(f"  - {e['name']} ({e.get('entity_type', 'unknown')})")
    
    print(f"\nSemantic-Based: {len(semantic_results.get('entities', []))} found")
    for e in semantic_results.get('entities', [])[:3]:
        print(f"  - {e['name']} ({e.get('entity_type', 'unknown')})")
    
    # Compare rules
    print("\n\n⚖️ BUSINESS RULES\n" + "-" * 80)
    print(f"\nKeyword-Based: {len(keyword_results.get('rules', []))} found")
    for r in keyword_results.get('rules', [])[:3]:
        if 'condition' in r:
            print(f"  - Validation: {r['condition'][:60]}")
        elif 'message' in r:
            print(f"  - Constraint: {r['message'][:60]}")
    
    print(f"\nSemantic-Based: {len(semantic_results.get('rules', []))} found")
    for r in semantic_results.get('rules', [])[:3]:
        if 'condition' in r:
            print(f"  - {r['condition'][:60]}")
            if r.get('if_branch'):
                print(f"    Operations: {', '.join(r['if_branch'][:3])}")
    
    # Compare integrations
    print("\n\n🔗 INTEGRATIONS\n" + "-" * 80)
    print(f"\nKeyword-Based: {len(keyword_results.get('integrations', []))} found")
    systems = set()
    for i in keyword_results.get('integrations', []):
        systems.add(i['system'])
    for s in sorted(systems)[:5]:
        print(f"  - {s}")
    
    print(f"\nSemantic-Based: {len(semantic_results.get('integrations', []))} found")
    systems = set()
    for i in semantic_results.get('integrations', []):
        systems.add(i['system'])
    for s in sorted(systems)[:5]:
        print(f"  - {s} ({i.get('category', 'unknown')})")
    
    # Compare authorization
    print("\n\n🔐 AUTHORIZATION CHECKS\n" + "-" * 80)
    print(f"\nKeyword-Based: {len(keyword_results.get('roles', []))} found")
    for r in keyword_results.get('roles', [])[:3]:
        print(f"  - {r['role']}")
    
    print(f"\nSemantic-Based: {len(semantic_results.get('authorization', []))} found")
    for a in semantic_results.get('authorization', [])[:3]:
        if 'condition' in a:
            print(f"  - {a['condition'][:50]}")
        else:
            print(f"  - Function: {a.get('function', 'unknown')}")
    
    # Key improvements
    print("\n\n🚀 KEY IMPROVEMENTS\n" + "-" * 80)
    improvements = [
        ("Call Graph Analysis", "Knows which functions call which → Better workflow understanding"),
        ("Data Flow Tracking", "Tracks variable assignments → Understands data movement"),
        ("Control Flow Analysis", "Understands if/else branches → Better rule detection"),
        ("Type Inference", "Infers variable types → Better entity recognition"),
        ("Pattern Recognition", "Detects state machines, workflows → Semantic understanding"),
        ("Condition Parsing", "Parses actual conditions → More accurate business rules"),
        ("Integration Mapping", "Links calls to systems → Accurate integration tracking"),
    ]
    
    for improvement, description in improvements:
        print(f"\n  ✨ {improvement}")
        print(f"     {description}")


if __name__ == '__main__':
    compare_extraction()
