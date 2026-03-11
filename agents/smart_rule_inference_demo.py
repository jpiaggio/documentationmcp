#!/usr/bin/env python3
"""
Smart Business Rule Inference - Demonstration

Shows how to automatically extract business rules from code:
1. Validation rules (min/max, ranges)
2. Temporal dependencies (ordering, state machines)
3. Permission hierarchies (access control)
4. Error handling constraints
"""

import sys
import os
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, os.path.dirname(__file__))

from smart_rule_inference import SmartRuleInference
from enhanced_business_extractor import EnhancedBusinessExtractor


# Example 1: E-Commerce Order Processing
ECOMMERCE_EXAMPLE = """
class OrderProcessor:
    def process_order(self, order):
        # Validation rules: min/max amounts
        if order.amount < 1.0:
            raise ValueError("Order amount must be at least $1.00")
        if order.amount > 999999.99:
            raise ValueError("Order amount exceeds maximum limit of $999,999.99")
        
        # State transitions
        order.status = 'pending'
        
        # Temporal dependency: must validate before processing
        self._validate_inventory(order)
        
        # Process payment
        order.status = 'processing'
        gateway = PaymentGateway()
        try:
            result = gateway.charge(order.amount, order.customer_token)
        except PaymentError as e:
            order.status = 'failed'
            raise
        
        # Update status after payment
        order.status = 'completed'
        self._send_confirmation(order)
    
    def _validate_inventory(self, order):
        for item in order.items:
            if item.quantity <= 0:
                raise ValueError("Item quantity must be positive")
            if item.quantity > 1000:
                raise ValueError("Item quantity exceeds warehouse capacity")
    
    def _send_confirmation(self, order):
        if not order.customer.email:
            raise ValueError("Customer email required for notification")
        # Send email notification


class OrderAuthorization:
    def can_delete_order(self, user, order):
        # Permission hierarchy 1: Admin can delete any order
        if user.role == 'admin':
            return True
        
        # Permission hierarchy 2: Customer can delete own order
        if order.customer_id == user.id:
            # But only if order is not yet shipped
            if order.status not in ['shipped', 'delivered']:
                return True
        
        return False
    
    def can_view_order(self, user, order):
        # Simpler permission: admin or owner
        if user.role == 'admin':
            return True
        if order.customer_id == user.id:
            return True
        return False
    
    def can_modify_order(self, user, order):
        # Can only modify pending orders
        if order.status != 'pending':
            return False
        
        # And must be owner
        if order.customer_id != user.id:
            return False
        
        return True
"""


# Example 2: Payment Gateway Integration
PAYMENT_EXAMPLE = """
def process_payment(payment_data):
    # Validation: Amount must be in valid range
    min_amount = 0.01
    max_amount = 10000.00
    
    if payment_data.amount < min_amount:
        raise ValueError(f"Amount must be at least {min_amount}")
    if payment_data.amount > max_amount:
        raise ValueError(f"Amount cannot exceed {max_amount}")
    
    # Credit card validation
    if not validate_card_number(payment_data.card_number):
        raise ValueError("Invalid card number")
    
    if payment_data.cvv < 100 or payment_data.cvv > 9999:
        raise ValueError("Invalid CVV")
    
    # Temporal dependency: authentication before charging
    authenticate_user(payment_data.user_id)
    
    # State machine: init -> auth -> charged -> settled
    state = 'init'
    state = 'auth'
    
    gateway = StripeGateway()
    try:
        charge = gateway.create_charge(
            amount=payment_data.amount,
            currency='USD',
            card_token=payment_data.token
        )
        state = 'charged'
    except StripeError as e:
        state = 'failed'
        raise PaymentProcessingError(f"Charge failed: {e}")
    
    # Settlement only happens after charge succeeds
    try:
        gateway.settle_charge(charge.id)
        state = 'settled'
    except Exception as e:
        raise PaymentSettlementError(f"Settlement failed: {e}")
    
    return charge
"""


# Example 3: User Management with Roles
USER_MANAGEMENT_EXAMPLE = """
class RoleManager:
    ROLE_HIERARCHY = {
        'viewer': 0,
        'editor': 1,
        'moderator': 2,
        'admin': 3
    }
    
    def promote_user(self, user, new_role, current_user):
        # Permission: Only admins can promote
        if current_user.role != 'admin':
            raise PermissionDenied("Only admins can change user roles")
        
        # Constraint: Can't promote to a higher role than yourself
        if self.ROLE_HIERARCHY[new_role] > self.ROLE_HIERARCHY[current_user.role]:
            raise PermissionDenied("Cannot promote user above your own role")
        
        # Temporal: new role takes effect immediately
        user.role = new_role
        user.updated_at = datetime.now()
    
    def revoke_user_access(self, user):
        # Admin-only permission
        if not self.is_admin(user):
            raise PermissionDenied("Admin required")
        
        user.is_active = False
        user.deactivated_at = datetime.now()
    
    def is_admin(self, user):
        return user.role == 'admin'

def require_role(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = kwargs.get('user') or args[1] if len(args) > 1 else None
            
            role_hierarchy = {
                'viewer': 0, 'editor': 1, 'moderator': 2, 'admin': 3
            }
            
            if user.role_level < role_hierarchy[required_role]:
                raise PermissionDenied(f"Requires {required_role} role")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
"""


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demonstrate_smart_inference():
    """Run comprehensive demonstration of smart rule inference."""
    
    inferencer = SmartRuleInference()
    extractor = EnhancedBusinessExtractor()
    
    examples = [
        ("E-Commerce Order Processing", ECOMMERCE_EXAMPLE),
        ("Payment Gateway Integration", PAYMENT_EXAMPLE),
        ("User Role Management", USER_MANAGEMENT_EXAMPLE),
    ]
    
    for example_name, code in examples:
        print_section(example_name)
        
        # Run smart inference
        results = inferencer.infer_all_rules(code, f"{example_name}.py")
        
        # Display validation rules
        if results['validation_rules']:
            print("✓ VALIDATION RULES (Constraints on values):")
            for rule in results['validation_rules']:
                print(f"  • Field: {rule['field_name']}")
                print(f"    Constraint: {rule['operation']} {rule['value']}")
                if rule.get('description'):
                    print(f"    Details: {rule['description']}")
            print()
        
        # Display temporal dependencies
        if results['temporal_dependencies']:
            print("⏱️  TEMPORAL DEPENDENCIES (Ordering requirements):")
            for dep in results['temporal_dependencies']:
                print(f"  • {dep['precondition']}")
                print(f"    ↓ must happen before ↓")
                print(f"  • {dep['postcondition']}")
                print(f"    Type: {dep['dependency_type']}")
                if dep.get('evidence'):
                    print(f"    Evidence: {dep['evidence'][0]}")
            print()
        
        # Display permission rules
        if results['permission_rules']:
            print("🔒 PERMISSION HIERARCHY (Access control):")
            for rule in results['permission_rules']:
                action_str = f"{rule['action']}" if rule['action'] else "access"
                print(f"  • {rule['actor_type']} can {action_str} {rule['resource']}")
                if rule.get('condition'):
                    print(f"    Condition: {rule['condition']}")
            print()
        
        # Display constraint rules
        if results['constraint_rules']:
            print("🚫 CONSTRAINTS (from error handling):")
            for rule in results['constraint_rules']:
                print(f"  • {rule['constraint']}")
                print(f"    Triggered by: {rule['triggered_by']}")
                print(f"    Severity: {rule['severity']}")
            print()
        
        print()


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("  SMART BUSINESS RULE INFERENCE DEMONSTRATION")
    print("  Extract implicit business rules from code")
    print("="*60)
    
    demonstrate_smart_inference()
    
    print_section("Statistics Summary")
    
    all_examples = [ECOMMERCE_EXAMPLE, PAYMENT_EXAMPLE, USER_MANAGEMENT_EXAMPLE]
    total_validation = 0
    total_temporal = 0
    total_permission = 0
    total_constraints = 0
    
    inferencer = SmartRuleInference()
    
    for code in all_examples:
        results = inferencer.infer_all_rules(code, "example.py")
        total_validation += len(results['validation_rules'])
        total_temporal += len(results['temporal_dependencies'])
        total_permission += len(results['permission_rules'])
        total_constraints += len(results['constraint_rules'])
    
    print(f"📊 Total Rules Inferred Across All Examples:")
    print(f"   • Validation Rules:        {total_validation}")
    print(f"   • Temporal Dependencies:   {total_temporal}")
    print(f"   • Permission Rules:        {total_permission}")
    print(f"   • Constraint Rules:        {total_constraints}")
    print(f"   • TOTAL:                   {total_validation + total_temporal + total_permission + total_constraints}")
    
    print("\n" + "="*60)
    print("  KEY FEATURES")
    print("="*60)
    print("""
✓ AUTOMATIC VALIDATION DETECTION
  → Min/max value constraints
  → Range validations
  → Format/pattern checks
  → Type constraints

⏱️  TEMPORAL DEPENDENCY DISCOVERY
  → State machine transitions
  → Sequential operation ordering
  → Setup/cleanup requirements
  → Precondition/postcondition pairs

🔒 PERMISSION HIERARCHY MAPPING
  → Role-based access control
  → Resource-specific permissions
  → Permission hierarchies
  → Conditional access rules

🚫 ERROR HANDLING CONSTRAINTS
  → Validation error triggers
  → Exception-based constraints
  → Error severity levels
  → Recovery procedures
    """)
    
    print("="*60)
    print("  INTEGRATION WITH EXISTING SYSTEM")
    print("="*60)
    print("""
The Smart Rule Inference integrates seamlessly with:

• EnhancedBusinessExtractor - Get all smart insights with standard analysis
• Neo4j Graph Database - Store inferred rules for relationship analysis
• MCP Servers - Use as tools for LLM-assisted analysis
• Cartographer Agent - Analyze entire codebases automatically

Example usage:

    from enhanced_business_extractor import EnhancedBusinessExtractor
    
    extractor = EnhancedBusinessExtractor()
    insights = extractor.extract_all_enhanced_insights(source_code, "file.py")
    
    # Access smart inferences
    validation_rules = insights['smart_insights']['validation_rules']
    temporal_deps = insights['smart_insights']['temporal_dependencies']
    permissions = insights['smart_insights']['permission_rules']
    constraints = insights['smart_insights']['constraint_rules']
    """)
    
    print("="*60)


if __name__ == "__main__":
    main()
