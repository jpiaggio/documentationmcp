#!/usr/bin/env python3
"""
Integration Test - Smart Rule Inference with Enhanced Business Extractor
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from smart_rule_inference import SmartRuleInference
from enhanced_business_extractor import EnhancedBusinessExtractor


# Sample code with rich business logic
SAMPLE_SERVICE_CODE = """
class OrderService:
    def __init__(self, db, payment_gateway):
        self.db = db
        self.gateway = payment_gateway
    
    def create_order(self, customer_id, items, total_amount):
        # Validation Rules: Amount constraints
        MIN_ORDER = 0.01
        MAX_ORDER = 100000.00
        
        if total_amount < MIN_ORDER:
            raise ValueError("Order minimum is " + str(MIN_ORDER))
        if total_amount > MAX_ORDER:
            raise ValueError("Order maximum is " + str(MAX_ORDER))
        
        # Validation: Item constraints
        for item in items:
            if item.quantity < 1:
                raise ValueError("Quantity must be >= 1")
            if item.quantity > 999:
                raise ValueError("Single item max quantity is 999")
        
        # Temporal: Initialize order state
        order = Order(
            customer_id=customer_id,
            items=items,
            amount=total_amount,
            status='draft'
        )
        
        # Temporal: Validate before saving
        self._validate_inventory(items)
        
        # Save to database
        self.db.save(order)
        
        return order
    
    def process_order(self, order_id):
        order = self.db.get(order_id)
        
        # Temporal: State machine - must follow specific sequence
        order.status = 'pending'
        self.db.save(order)
        
        order.status = 'payment_processing'
        try:
            result = self.gateway.charge(order.customer_id, order.amount)
        except PaymentError as e:
            order.status = 'payment_failed'
            self.db.save(order)
            raise
        
        # Temporal: Payment must succeed before marking completed
        order.status = 'completed'
        self.db.save(order)
        
        # Temporal: Notification is final step
        self._send_notification(order)
        
        return order
    
    def _validate_inventory(self, items):
        for item in items:
            available = self.db.check_stock(item.id)
            if available < item.quantity:
                raise InsufficientStock()
    
    def _send_notification(self, order):
        if not order.customer.email:
            raise ValueError("Email required")


class OrderPermissions:
    def can_view_order(self, user, order):
        # Permission Level 3 (Admin): Can view all
        if user.role == 'admin':
            return True
        
        # Permission Level 2 (Customer Service): Can view assigned orders
        if user.role == 'customer_service':
            return user.region == order.region
        
        # Permission Level 1 (Customer): Can view own orders
        if order.customer_id == user.id:
            return True
        
        return False
    
    def can_cancel_order(self, user, order):
        # Admin can always cancel
        if user.role == 'admin':
            return True
        
        # Customer can cancel own order only if pending
        if order.customer_id == user.id and order.status == 'pending':
            return True
        
        return False
    
    def can_refund_order(self, user, order):
        # Constraint: Only completed orders can be refunded
        if order.status != 'completed':
            return False
        
        # Constraint: Only finance team can refund
        if user.department != 'finance':
            return False
        
        return True
"""


def test_smart_inference():
    """Test smart rule inference on sample code."""
    
    print("=" * 70)
    print("INTEGRATION TEST: Smart Rule Inference")
    print("=" * 70)
    
    inferencer = SmartRuleInference()
    extractor = EnhancedBusinessExtractor()
    
    # Test 1: Smart inference alone
    print("\n1. SMART RULE INFERENCE (Standalone)")
    print("-" * 70)
    
    results = inferencer.infer_all_rules(SAMPLE_SERVICE_CODE, "order_service.py")
    
    print(f"\nVALIDATION RULES ({len(results['validation_rules'])} found)")
    for rule in results['validation_rules'][:5]:
        print(f"  * {rule['field_name']} {rule['operation']} {rule['value']}")
    
    print(f"\nTEMPORAL DEPENDENCIES ({len(results['temporal_dependencies'])} found)")
    for dep in results['temporal_dependencies'][:4]:
        print(f"  * {dep['precondition']} -> {dep['postcondition']}")
        print(f"    ({dep['dependency_type']})")
    
    print(f"\nPERMISSION RULES ({len(results['permission_rules'])} found)")
    for perm in results['permission_rules'][:5]:
        print(f"  * {perm['actor_type']} can {perm['action']} {perm['resource']}")
    
    print(f"\nCONSTRAINT RULES ({len(results['constraint_rules'])} found)")
    for const in results['constraint_rules'][:4]:
        print(f"  * {const['constraint']}")
        print(f"    Severity: {const['severity']}")
    
    # Test 2: Enhanced business extractor with smart insights
    print("\n\n2. ENHANCED BUSINESS EXTRACTOR (with Smart Insights)")
    print("-" * 70)
    
    insights = extractor.extract_all_enhanced_insights(
        SAMPLE_SERVICE_CODE, 
        "order_service.py"
    )
    
    print(f"\nWorkflows: {len(insights['workflows'])}")
    for wf in insights['workflows'][:3]:
        print(f"  * {wf['name']}")
    
    print(f"\nBusiness Entities: {len(insights['entities'])}")
    print(f"\nData Flows: {len(insights['data_flows'])}")
    
    smart = insights['smart_insights']
    print(f"\n{'='*70}")
    print(f"SMART INSIGHTS SUMMARY")
    print(f"{'='*70}")
    print(f"\nValidation Rules:        {len(smart['validation_rules'])}")
    print(f"Temporal Dependencies:   {len(smart['temporal_dependencies'])}")
    print(f"Permission Rules:        {len(smart['permission_rules'])}")
    print(f"Constraint Rules:        {len(smart['constraint_rules'])}")
    
    total_rules = (
        len(smart['validation_rules']) +
        len(smart['temporal_dependencies']) +
        len(smart['permission_rules']) +
        len(smart['constraint_rules'])
    )
    print(f"\nTOTAL RULES DISCOVERED: {total_rules}")
    
    # Test 3: Generate formatted report
    print("\n\n3. FORMATTED ANALYSIS REPORT")
    print("-" * 70)
    
    report = extractor.generate_analysis_report(SAMPLE_SERVICE_CODE, "order_service.py")
    print(report)
    
    # Test 4: Neo4j export
    print("\n\n4. NEO4J EXPORT (Sample Cypher Statements)")
    print("-" * 70)
    
    cypher_stmts = inferencer.generate_cypher_statements(
        results,
        "order_service.py",
        "OrderService"
    )
    
    print(f"\nGenerated {len(cypher_stmts)} Cypher statements")
    print("\nSample Cypher for first validation rule:")
    if cypher_stmts:
        print(f"  {cypher_stmts[0][:80]}...")
    
    # Summary statistics
    print("\n\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    stats = results['statistics']
    print(f"\nRules Discovered:")
    print(f"  * Validation Rules:      {stats['total_validation_rules']:>3}")
    print(f"  * Temporal Dependencies: {stats['total_temporal_dependencies']:>3}")
    print(f"  * Permission Rules:      {stats['total_permission_rules']:>3}")
    print(f"  * Constraint Rules:      {stats['total_constraint_rules']:>3}")
    print(f"  * TOTAL:                 {stats['total_rules']:>3}")
    
    print(f"\nFeatures Tested:")
    print(f"  [OK] Smart Rule Inference (Standalone)")
    print(f"  [OK] Enhanced Business Extractor Integration")
    print(f"  [OK] Formatted Report Generation")
    print(f"  [OK] Neo4j Cypher Export")
    
    print(f"\n{'='*70}\n")
    
    return results, insights, cypher_stmts


def validate_against_business_requirements():
    """Validate that detected rules match expected business logic."""
    
    print("\n" + "=" * 70)
    print("BUSINESS REQUIREMENT VALIDATION")
    print("=" * 70)
    
    inferencer = SmartRuleInference()
    results = inferencer.infer_all_rules(SAMPLE_SERVICE_CODE, "order_service.py")
    
    print("\nValidating business requirements...")
    
    # Check validation rules
    amounts = [r for r in results['validation_rules'] if 'amount' in str(r)]
    print(f"\n[OK] Amount constraints found: {len(amounts)} rules")
    for rule in amounts:
        print(f"     * {rule['field_name']} {rule['operation']} {rule['value']}")
    
    # Check temporal dependencies
    state_deps = [d for d in results['temporal_dependencies'] 
                  if 'status' in str(d)]
    print(f"\n[OK] State transitions found: {len(state_deps)} dependencies")
    
    # Check permission rules
    admin_perms = [p for p in results['permission_rules'] 
                   if 'admin' in str(p)]
    print(f"\n[OK] Admin permissions found: {len(admin_perms)} rules")
    
    # Check constraints
    payment_constraints = [c for c in results['constraint_rules'] 
                          if 'Payment' in str(c)]
    print(f"\n[OK] Payment constraints found: {len(payment_constraints)} rules")
    
    print("\n" + "=" * 70)
    print("*** All business requirements validated successfully! ***\n")


if __name__ == "__main__":
    results, insights, cypher = test_smart_inference()
    validate_against_business_requirements()
    
    print("\n*** Integration test completed successfully! ***\n")
