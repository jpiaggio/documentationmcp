"""
LLM Code Analysis Demonstration

Shows all capabilities:
1. Deep semantic understanding of code
2. Business logic explanation  
3. Pattern validation with reasoning
4. Business impact analysis
5. Interactive Q&A about code
"""

import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.llm_code_analyzer import (
    LLMCodeAnalyzer, BusinessLogicExplainer, PatternValidator
)
from agents.unified_analyzer import UnifiedCodeAnalyzer, InterativeLLMAnalysis


def demo_semantic_understanding():
    """
    DEMO 1: Deep Semantic Understanding
    
    Shows how LLM understands WHAT code is really doing,
    not just the syntax.
    """
    print("\n" + "="*70)
    print("DEMO 1: DEEP SEMANTIC UNDERSTANDING")
    print("="*70)
    print("\nQuestion: What is this function REALLY doing (not just syntax)?")
    print("-"*70)
    
    sample_code = '''
def process_customer_order(customer_id, items, payment_info):
    """Process an order from customer."""
    # Validate customer exists
    customer = get_customer(customer_id)
    if not customer:
        raise CustomerNotFoundError(customer_id)
    
    # Check customer payment methods
    if not customer.has_valid_payment_method():
        notify_user("Please add a payment method")
        return None
    
    # Calculate total and tax
    subtotal = sum(item.price for item in items)
    tax = subtotal * TAX_RATE
    total = subtotal + tax
    
    # Create order
    order = create_order(customer_id, items, total)
    
    # Process payment
    try:
        charge_result = charge_payment_method(customer.payment_method, total, payment_info)
        if not charge_result.success:
            order.status = "payment_failed"
            notify_customer(customer.email, f"Payment failed: {charge_result.reason}")
            return None
    except PaymentGatewayError as e:
        log_error(f"Payment gateway error: {e}")
        order.status = "payment_error"
        return None
    
    # Update order status
    order.status = "confirmed"
    order.payment_id = charge_result.payment_id
    order.save()
    
    # Notify customer
    send_order_confirmation(customer.email, order)
    
    # Update inventory
    for item in items:
        update_inventory(item.id, -item.quantity)
    
    return order
'''
    
    # This would need actual API key to run in demo
    print("\n📝 Function Code (abbreviated for display):")
    print(f"```python\n{sample_code[:500]}...\n```")
    
    print("\n🤖 LLM Analysis Would Show:")
    print("""
✓ INTERPRETED PURPOSE:
  "Validates customer eligibility, calculates and charges payment, 
   creates confirmed order, and updates inventory"

✓ KEY OPERATIONS:
  - Validate customer exists and has payment method
  - Calculate order total with tax
  - Charge payment method
  - Create order record
  - Update inventory based on items
  - Notify customer of confirmation

✓ BUSINESS VALUE:
  "This is the CORE revenue function - it converts shopping carts 
   into actual paid orders. Without this, no revenue."

✓ RISKS:
  - Payment failures could leave incomplete orders
  - Inventory could be updated before payment confirms
  - No retry logic if payment gateway fails temporarily
  - Customer not notified if inventory update fails

✓ COMPLEXITY: complex
✓ CONFIDENCE: 0.95
""")


def demo_business_logic_explanation():
    """
    DEMO 2: Business Logic Explanation
    
    Explains complex logic in simple, business terms.
    """
    print("\n" + "="*70)
    print("DEMO 2: BUSINESS LOGIC EXPLANATION")
    print("="*70)
    print("\nQuestion: Explain this complex validation logic in simple terms")
    print("-"*70)
    
    complex_logic = '''
def calculate_discount_and_final_price(customer, items, include_shipping=True):
    # Base price
    subtotal = sum(item.price * item.quantity for item in items)
    
    # Apply customer loyalty discount
    if customer.loyalty_tier == "gold":
        discount_rate = 0.15
    elif customer.loyalty_tier == "silver":
        discount_rate = 0.10
    elif customer.loyalty_tier == "bronze":
        discount_rate = 0.05
    else:
        discount_rate = 0
    
    # But cap volume discounts
    volume_discount = 0
    if sum(item.quantity for item in items) >= 10:
        volume_discount = 0.05
    elif sum(item.quantity for item in items) >= 5:
        volume_discount = 0.03
    
    # Use the better discount (not both)
    applied_discount = max(discount_rate, volume_discount)
    
    # But loyalty gold gets both
    if customer.loyalty_tier == "gold":
        applied_discount = discount_rate + volume_discount
    
    discount_amount = subtotal * applied_discount
    subtotal_after_discount = subtotal - discount_amount
    
    # Shipping
    if include_shipping:
        if subtotal_after_discount > 100:
            shipping = 0
        elif subtotal_after_discount > 50:
            shipping = 5
        else:
            shipping = 10
    else:
        shipping = 0
    
    # Tax on discounted amount
    tax = (subtotal_after_discount + shipping) * 0.08
    
    final = subtotal_after_discount + shipping + tax
    
    return {
        'subtotal': subtotal,
        'discount': discount_amount,
        'shipping': shipping,
        'tax': tax,
        'final': final,
        'discount_rate': applied_discount
    }
'''
    
    print("\n📝 Complex Logic (abbreviated):")
    print(f"```python\n{complex_logic[:300]}...\n```")
    
    print("\n🤖 LLM Would Explain:")
    print("""
SUMMARY:
"This calculates the final price by giving rewards to loyal and bulk 
buyers, then applying shipping and tax."

WHAT HAPPENS:
1. Start with the base cost of all items
2. Give bigger discounts to more loyal customers
3. Give bigger discounts to bulk buyers  
4. Gold members get BOTH discounts (best deal)
5. Free shipping over $100, cheaper over $50
6. Add tax on the final amount

WHY IT MATTERS:
"This is how we incentivize customer loyalty and bulk purchases - 
making it cheaper for good customers."

POTENTIAL ISSUES:
- Logic is complex and hard to maintain
- Rules for shipping/discounts mixed together
- Gold loyalty tier gets special treatment (hard to understand why)
- No handling of minimum order amounts

IMPROVEMENT SUGGESTIONS:
1. Split discount logic from shipping logic
2. Use a discount tier table instead of if/else
3. Add comments explaining the business rules
4. Consider a dedicated DiscountEngine class
""")


def demo_pattern_validation():
    """
    DEMO 3: Pattern Validation
    
    Validates if extracted patterns are real using L LM reasoning.
    """
    print("\n" + "="*70)
    print("DEMO 3: PATTERN VALIDATION WITH LLM REASONING")
    print("="*70)
    print("\nQuestion: Are these extracted patterns REAL and VALID?")
    print("-"*70)
    
    print("\n📊 Extracted Patterns to Validate:")
    patterns = {
        "customer_authentication": [
            "authenticate_user(username, password) at line 42",
            "verify_jwt_token(token) at line 156",
            "check_session_valid(session_id) at line 203"
        ],
        "payment_processing": [
            "charge_payment_gateway(amount, card) at line 78",
            "retry_payment_on_failure(payment_id) at line 145",
            "handle_declined_payment(reason) at line 189"
        ],
        "logging_everywhere": [
            "log_debug() called 47 times",
            "log_error() called 12 times",
            "log_info() called 5 times"
        ]
    }
    
    print("\n🤖 LLM Validation Results:")
    
    results = {
        "customer_authentication": {
            "is_valid": True,
            "confidence": 0.98,
            "reasoning": "Clear pattern of authentication at multiple levels. This is a real and important pattern.",
            "recommendations": ["Could consolidate into central auth service"]
        },
        "payment_processing": {
            "is_valid": True,
            "confidence": 0.92,
            "reasoning": "Real pattern showing payment flow with error handling and retry logic.",
            "recommendations": ["Add circuit breaker for gateway failures", "Consider idempotency tokens"]
        },
        "logging_everywhere": {
            "is_valid": False,
            "confidence": 0.75,
            "reasoning": "This is not really a 'business pattern' - it's just scattered logging calls. Not a cohesive pattern.",
            "recommendations": ["Use structured logging instead", "Centralize logging configuration"]
        }
    }
    
    for pattern_name, data in patterns.items():
        result = results.get(pattern_name, {})
        status = "✓ VALID" if result.get("is_valid") else "✗ INVALID"
        confidence = result.get("confidence", 0)
        
        print(f"\n{status} {pattern_name.upper()}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Reasoning: {result.get('reasoning', '')}")
        print(f"   Evidence: {len(data)} occurrences")
        if result.get("recommendations"):
            print(f"   Recommendations: {', '.join(result['recommendations'][:2])}")


def demo_business_impact():
    """
    DEMO 4: Business Impact Analysis
    
    Analyzes how code impacts the business.
    """
    print("\n" + "="*70)
    print("DEMO 4: BUSINESS IMPACT ANALYSIS")
    print("="*70)
    print("\nQuestion: What's the business impact of this code?")
    print("-"*70)
    
    function = '''
def process_refund(order_id, reason):
    """Process a refund for an order."""
    order = get_order(order_id)
    
    # Calculate refund amount (minus 15% restocking fee)
    refund_amount = order.total * 0.85
    
    # Process the refund
    result = payment_gateway.refund(
        order.payment_id,
        refund_amount
    )
    
    # Update order status
    order.status = "refunded"
    order.refund_amount = refund_amount
    order.refund_reason = reason
    order.save()
    
    # Notify customer
    send_refund_notification(order.customer.email, refund_amount)
    
    return result
'''
    
    print("\n📝 Function:")
    print(f"```python\n{function}\n```")
    
    print("\n🎯 LLM Business Impact Analysis:")
    print(f"""
AFFECTED USERS:
  - Customers (direct): Get refunds for returned items
  - Customer Support: Processes refund requests
  - Finance/Accounting: Tracks refund transactions
  - Payment team: Handles payment gateway refunds

IMPACT CATEGORY: Financial (direct monetary impact)

FAILURE IMPACT:
  ✗ Customer doesn't get refund → Customer churn
  ✗ Payment gateway fails → Hung transaction
  ✗ Notification fails → Customer doesn't know about refund
  ✗ Order status doesn't update → Accounting inconsistency

CRITICALITY: CRITICAL
  "This is a customer-facing financial function. Failures directly 
   impact customer satisfaction and retention."

DEPENDENT SYSTEMS:
  - Payment Gateway (Stripe/PayPal)
  - Email notification system
  - Order database
  - Customer database
  - Accounting/Finance system

BUSINESS VALUE:
  "Enables customer returns and handling - essential for e-commerce. 
   High-value because customer satisfaction impacts lifetime value."

RISK LEVEL: HIGH
  Risk 1: 15% restocking fee is hard-coded (not configurable)
  Risk 2: No verification that refund is allowed (already returned?)
  Risk 3: Refund sent immediately without approval process
  Risk 4: No handling of partial refunds
""")


def demo_interactive_qa():
    """
    DEMO 5: Interactive Q&A
    
    Ask LLM questions about code in natural language.
    """
    print("\n" + "="*70)
    print("DEMO 5: INTERACTIVE Q&A ABOUT CODE")
    print("="*70)
    print("\nAsking questions about code.. (simulated responses)")
    print("-"*70)
    
    questions = [
        "What happens if the database is down?",
        "How do we handle race conditions here?",
        "Is there any customer data exposed?",
        "What's the most critical part of this code?",
        "How would this perform with 1 million users?"
    ]
    
    simulated_answers = {
        "What happens if the database is down?": 
            "This code would fail immediately when trying to get_customer(). "
            "We should add retry logic and a fallback cache.",
        
        "How do we handle race conditions here?": 
            "There's a potential race condition if two requests process payment "
            "simultaneously. We should use database locks.",
        
        "Is there any customer data exposed?": 
            "Yes - customer payment info is passed directly. We should use tokenization.",
        
        "What's the most critical part of this code?": 
            "The payment processing. If that fails, the entire order fails.",
        
        "How would this perform with 1 million users?": 
            "Not well - this is synchronous. We should queue refunds asynchronously."
    }
    
    for question in questions:
        print(f"\n❓ Q: {question}")
        answer = simulated_answers.get(question, "Analyzing...")
        print(f"   🤖 A: {answer}")


def demo_comprehensive_analysis():
    """
    DEMO 6: Comprehensive Report
    
    Shows complete analysis combining all approaches.
    """
    print("\n" + "="*70)
    print("DEMO 6: COMPREHENSIVE CODE ANALYSIS REPORT")
    print("="*70)
    print("\n📄 Generated Report Content:")
    print("-"*70)
    
    report = """
# Code Analysis Report: payment_service.py

## Executive Summary

This code implements the core payment processing logic for the e-commerce system.
It's responsible for converting shopping carts into paid orders - this is a CRITICAL
revenue-generating function.

### Key Statistics
- Functions Analyzed: 12
- Structural Complexity: HIGH
- Business Criticality: CRITICAL  
- Overall Risk Level: HIGH
- Valid Patterns Detected: 8/10 (80%)
- Documentation Quality: LOW

## What This Code Does (In Business Terms)

### Primary Purpose
"Validates customers, calculates order totals, charges their payment methods,
creates confirmed orders, and notifies customers of success or failure."

### Key Business Activities
1. Verify customer exists and can pay
2. Calculate total with taxes and discounts
3. Charge the payment method
4. Create order record
5. Reserve inventory
6. Send order confirmation

### Secondary Functions
- Handle payment failures gracefully
- Retry failed payments
- Issue refunds
- Apply discounts

## Business Impact Analysis

### Who This Affects
- **Customers**: Direct impact - determines if their order goes through
- **Finance**: Tracks revenue and refunds
- **Operations**: Drives fulfillment and inventory
- **Customer Service**: Handles payment issues

### Financial Impact
- **Revenue Source**: This directly generates revenue
- **Risk Area**: Payment failures impact conversion
- **Value**: ~50% of customer lifetime value depends on smooth payments

### Failure Scenarios and Impact
| Scenario | Impact | Severity |
|----------|--------|----------|
| Payment gateway down | Orders fail, lost sales | CRITICAL |
| Payment succeeds but order not created | Customer charged but no product | CRITICAL |
| Inventory not reserved before payment | Overselling products | HIGH |
| Refund fails | Customer keeps money AND product | HIGH |
| Email notification fails | Customer doesn't know status | MEDIUM |

## Detected Patterns & Validation

### Pattern 1: Payment Processing ✓ VALID (99% confidence)
Multiple functions coordinating payment with retry logic.
**Recommendation**: Implement circuit breaker pattern for gateway failures.

### Pattern 2: Customer Validation ✓ VALID (95% confidence)  
Consistent validation at entry points.
**Recommendation**: Use middleware for centralized auth.

### Pattern 3: Error Handling ✗ INVALID (45% confidence)
Error handling is inconsistent - some functions suppress errors, others throw.
**Recommendation**: Establish consistent error handling strategy.

## Risk Assessment

### Critical Risks
1. **Race Condition in Inventory**: Two orders might reserve same product
2. **Partial Failure**: Payment charged but order not created
3. **No Idempotency**: Duplicate requests could double-charge
4. **Hard-coded Fees**: 15% restocking fee can't be changed per customer

### High Risks
1. **No Payment Gateway Failover**: Single point of failure
2. **Synchronous Processing**: Blocks user waiting for slow operations
3. **No Circuit Breaker**: Cascading failures possible
4. **Limited Logging**: Hard to troubleshoot failures

### Medium Risks
1. **Notification Failures**: Customer won't know status
2. **No Monitoring**: Can't detect issues proactively
3. **Performance**: Not optimized for scale

## Improvement Recommendations

### Priority 1 (Critical - Do First)
1. Add database-level locks to prevent inventory race conditions
2. Implement idempotency keys so duplicate requests are safe
3. Add comprehensive logging of payment flow
4. Create payment queue (process asynchronously)

### Priority 2 (High - Do Soon)  
1. Implement circuit breaker for payment gateway
2. Add retry with exponential backoff
3. Separate payment processing into separate service
4. Add monitoring and alerting

### Priority 3 (Medium - Do Next)
1. Centralize discount/fee logic
2. Implement comprehensive error handling
3. Add payment gateway failover
4. Performance optimization

## Documentation Quality

This code lacks sufficient documentation. Missing:
- Why certain design decisions were made
- What happens in edge cases
- How to debug payment issues
- Payment flow diagram
- Configuration documentation
- Integration with other systems

## Recommendations

### For Business
- Add payment monitoring and alerting dashboard
- Create playbook for payment failures
- Track payment funnel metrics
- Monitor refund rates and reasons

### For Development
- Refactor for clarity and maintainability
- Add comprehensive unit and integration tests
- Implement payment reconciliation process
- Create payment service documentation

## Conclusion

This is a well-intentioned implementation of critical business logic, but it needs
significant hardening for production use. The core logic is sound, but:
- Too many sequential steps (should be asynchronous)
- Missing error handling and retry logic
- No protection against race conditions
- Insufficient monitoring

**Recommendation**: Prioritize the critical risks before scaling beyond current load.
"""
    
    print(report)


def main():
    """Run all demos."""
    print("\n\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🤖 LLM CODE ANALYSIS - Comprehensive Demonstration ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    demo_semantic_understanding()
    demo_business_logic_explanation()
    demo_pattern_validation()
    demo_business_impact()
    demo_interactive_qa()
    demo_comprehensive_analysis()
    
    print("\n" + "="*70)
    print("✅ ALL DEMOS COMPLETED")
    print("="*70)
    print("""
🎓 Key Takeaways:

1. SEMANTIC UNDERSTANDING
   Instead of analyzing syntax, ask LLM "what is this REALLY doing?"
   Gets at business intent, not implementation details

2. BUSINESS LANGUAGE
   Explain code in business terms for non-technical stakeholders
   "Validates customers and charges them" not "queries DB and calls API"

3. PATTERN VALIDATION
   Use LLM reasoning to verify extracted patterns are real and meaningful
   Not just based on code frequency, but semantic reasoning

4. BUSINESS IMPACT
   Analyze who is affected, what breaks, financial implications
   Prioritize accordingly for development effort

5. INTERACTIVE ANALYSIS
   Ask natural language questions about code
   Get answers that explain not just what, but why
   Continuous conversation for deeper understanding

🚀 Integration Steps:
1. Export ANTHROPIC_API_KEY environment variable
2. Use UnifiedCodeAnalyzer for deep analysis
3. Use InteractiveLLMAnalysis for Q&A
4. Generate documentation automatically
5. Validate patterns with LLM reasoning
""")


if __name__ == "__main__":
    main()
