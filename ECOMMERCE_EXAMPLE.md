"""
Example: E-Commerce Platform Business Rules Extraction

This example shows how the cartographer system extracts business logic from
an e-commerce platform and makes it available to AI for understanding.
"""

# ============================================================================
# EXAMPLE E-COMMERCE CODE
# ============================================================================

# File: core/checkout.py

def checkout_workflow(customer_id, items):
    """
    Main checkout workflow that processes customer orders.
    
    Journey: SELECT_PRODUCT → CHECKOUT → VALIDATE → PAY → NOTIFY → UPDATE_STATUS
    """
    customer = get_customer(customer_id)
    
    # Step 1: AUTHENTICATE/VALIDATE
    if not customer.is_active:
        raise CustomerInactiveError("Customer account is not active")
    
    if len(items) == 0:
        raise EmptyCartError("Cannot checkout with empty cart")
    
    # Step 2: BUSINESS RULES enforcement
    total = calculate_total(items)
    
    # THRESHOLD rule: max purchase amount
    if total > 10000:
        raise MaxOrderError("Order total exceeds maximum of $10,000")
    
    # CONSTRAINT rule: minimum purchase
    if total < 10:
        raise MinOrderError("Minimum order amount is $10")
    
    # CONSTRAINT rule: eligibility
    if customer.account_age_days < 7:
        raise NewAccountError("New accounts must wait 7 days before checkout")
    
    # CONSTRAINT rule: balance check
    if customer.account_balance < total:
        raise InsufficientFundsError(f"Balance {customer.account_balance} < {total}")
    
    # Step 3: INTEGRATION - Payment Gateway
    payment_result = stripe_payment_gateway.process_payment(
        customer.payment_method,
        total,
        order_id=generate_order_id()
    )
    
    if not payment_result.success:
        raise PaymentFailedError(f"Payment failed: {payment_result.error}")
    
    # Step 4: CREATE order entity
    order = Order(
        customer_id=customer_id,
        items=items,
        total=total,
        payment_id=payment_result.transaction_id,
        status="CONFIRMED"
    )
    order.save()
    
    # Step 5: UPDATE_STATUS - Mark order as confirmed
    order.status = "CONFIRMED"
    order.confirmed_at = datetime.now()
    order.save()
    
    # Step 6: INTEGRATION - Email notification
    email_service.send_order_confirmation(
        customer.email,
        order.order_id,
        order.total
    )
    
    # Step 7: INTEGRATION - Inventory system
    inventory_system.reserve_items(items, order.order_id)
    
    # Step 8: TRIGGER event for async processing
    event_bus.emit(OrderConfirmedEvent(order.order_id))
    
    return order


# File: core/fulfillment.py

def order_fulfillment_workflow(order_id):
    """
    Handles order fulfillment from warehouse to customer.
    
    Journey: UPDATE_STATUS → SHIP → DELIVER
    """
    order = Order.get(order_id)
    
    # VALIDATION rule: order must be confirmed
    if order.status != "CONFIRMED":
        raise InvalidOrderStatusError(f"Cannot fulfill order with status {order.status}")
    
    # BUSINESS RULE: fulfillment timeout
    if order.confirmed_at < datetime.now() - timedelta(days=30):
        raise FulfillmentTimeoutError("Order exceeds 30-day fulfillment window")
    
    # ROLE-BASED: only managers can override processing
    processed_by = get_current_user()
    if processed_by.role not in ["manager", "admin"]:
        # Process automatically
        order.status = "PROCESSING"
    else:
        # Manager override allowed
        order.status = "PRIORITY_PROCESSING"
    
    order.processing_started_at = datetime.now()
    order.save()
    
    # Step: SHIP
    for item in order.items:
        warehouse = find_nearest_warehouse(item.sku, order.shipping_address)
        warehouse.pick_item(item.sku, item.quantity)
    
    # INTEGRATION: Create shipment with carrier
    carrier = determine_carrier(order.shipping_address)
    shipment = carrier.create_shipment(
        order_id=order.order_id,
        address=order.shipping_address,
        items=order.items
    )
    
    order.status = "SHIPPED"
    order.shipment_id = shipment.tracking_number
    order.shipped_at = datetime.now()
    order.save()
    
    # INTEGRATION: Send notification
    email_service.send_shipment_notification(
        customer_email=order.customer.email,
        tracking_number=shipment.tracking_number,
        carrier=carrier.name
    )
    
    # TRIGGER: Shipment event for tracking
    event_bus.emit(OrderShippedEvent(order_id, shipment.tracking_number))
    
    return shipment


# File: core/returns.py

def process_return(order_id, items_to_return):
    """
    Process customer returns and initiate refunds.
    
    Journey: CANCEL/RETURN
    """
    order = Order.get(order_id)
    
    # CONSTRAINT rule: return window
    days_since_delivery = (datetime.now() - order.delivered_at).days
    if days_since_delivery > 30:
        raise ReturnWindowExpiredError("Returns must be within 30 days of delivery")
    
    # CONSTRAINT rule: return limit per order
    if len(order.returns) >= 3:
        raise ReturnLimitExceededError("Maximum 3 return requests per order")
    
    # THRESHOLD rule: restocking fee
    total_return_qty = sum(item.quantity for item in items_to_return)
    if total_return_qty > order.total_quantity * 0.5:
        restocking_fee = get_return_subtotal(items_to_return) * 0.15
    else:
        restocking_fee = 0
    
    # Create return request
    return_request = ReturnRequest(
        order_id=order_id,
        items=items_to_return,
        requested_at=datetime.now(),
        status="PENDING_APPROVAL"
    )
    
    # ROLE-BASED: Auto-approve for specific items
    if all(item.is_full_return_eligible for item in items_to_return):
        return_request.status = "APPROVED"
        return_request.approved_at = datetime.now()
    else:
        # Requires manager approval
        return_request.status = "PENDING_REVIEW"
        email_service.notify_managers(
            f"Return request {return_request.id} requires review"
        )
    
    return_request.save()
    
    if return_request.status == "APPROVED":
        # INTEGRATION: Process refund
        refund = stripe_payment_gateway.create_refund(
            original_transaction_id=order.payment_id,
            amount=get_return_subtotal(items_to_return) - restocking_fee
        )
        
        # UPDATE_STATUS
        return_request.status = "REFUNDED"
        return_request.refund_id = refund.transaction_id
        return_request.refunded_at = datetime.now()
        return_request.save()
        
        # TRIGGER: Refund event
        event_bus.emit(OrderRefundedEvent(order_id, refund.amount))
        
        # INTEGRATION: Notify customer
        email_service.send_refund_notification(
            order.customer.email,
            refund.amount,
            refund.transaction_id
        )
    
    return return_request


# ============================================================================
# WHAT CARTOGRAPHER EXTRACTS
# ============================================================================

"""
From the above code, cartographer extracts:

1. CUSTOMER JOURNEY STEPS:
   ✓ AUTHENTICATE (customer.is_active check)
   ✓ BROWSE/CHECKOUT (checkout_workflow entry point)
   ✓ VALIDATE (multiple validation rules)
   ✓ UPDATE_STATUS (order.status assignments)
   ✓ NOTIFY (email service calls)
   ✓ SHIP (fulfillment_workflow)
   ✓ DELIVER (shipment tracking)
   ✓ CANCEL/RETURN (process_return)

2. BUSINESS ENTITIES:
   ✓ Customer (customer object, eligibility)
   ✓ Order (items, total, status, payment_id)
   ✓ Item/CartItem (SKU, quantity)
   ✓ Payment (payment_method, transaction_id)
   ✓ Shipment (tracking_number, carrier)
   ✓ ReturnRequest (return items, refund status)

3. BUSINESS RULES:
   ✓ Account must be active
   ✓ Cart must have items
   ✓ Order total 10-10,000
   ✓ Account age 7+ days
   ✓ Sufficient balance
   ✓ Order status validation for fulfillment
   ✓ Fulfillment within 30 days
   ✓ Return window 30 days from delivery
   ✓ Max 3 returns per order
   ✓ 15% restocking fee for large returns
   ... and many more!

4. INTEGRATIONS:
   ✓ stripe_payment_gateway (payments)
   ✓ email_service (notifications)
   ✓ inventory_system (stock management)
   ✓ carrier/shipping_service (fulfillment)
   ✓ event_bus (async events)

5. ROLE-BASED ACCESS:
   ✓ manager/admin (order overrides, approvals)
   ✓ default users (standard checkout)

6. STATE TRANSITIONS (EVENTS):
   ✓ ORDER CONFIRMED (payment processing)
   ✓ ORDER SHIPPED (fulfillment)
   ✓ ORDER DELIVERED (delivery confirmation)
   ✓ ORDER REFUNDED (return processing)
   ✓ ORDER PROCESSING (status update)

7. ERROR SCENARIOS (CONSTRAINTS):
   ✓ Inactive customer
   ✓ Empty cart
   ✓ Order exceeds max
   ✓ Order below minimum
   ✓ New account (7-day wait)
   ✓ Insufficient funds
   ✓ Invalid order status
   ✓ Return window expired
   ✓ Return limit exceeded
   ✓ Payment failed

"""

# ============================================================================
# HOW AI USES THIS
# ============================================================================

"""
BEFORE (without cartographer):
=========================================
AI Developer: I need to understand checkout...
Human: Read files: checkout.py, payment.py, email.py, inventory.py...
AI: *reads 1000+ lines of code*
Human: Now understand this takes 2-3 hours per feature

AFTER (with cartographer):
=========================================
AI Developer: I need to understand checkout
Server: Here's the business context...

{
  "journey": [
    "AUTHENTICATE",
    "VALIDATE",
    "CHECKOUT",
    "PAY",
    "NOTIFY",
    "UPDATE_STATUS",
    "SHIP",
    "DELIVER"
  ],
  "business_rules": {
    "checkout": [
      "customer.is_active",
      "items.length > 0",
      "total >= $10",
      "total <= $10,000",
      "account_age >= 7 days",
      "balance >= total"
    ],
    "fulfillment": [
      "order.status == 'CONFIRMED'",
      "days_since_confirmed < 30"
    ],
    "returns": [
      "days_since_delivery <= 30",
      "returns_count < 3"
    ]
  },
  "integrations": {
    "payments": ["stripe"],
    "notifications": ["email"],
    "fulfillment": ["inventory", "carrier"]
  },
  "entities": {
    "customer": ["is_active", "account_age_days", "balance"],
    "order": ["status", "items", "total", "payment_id"],
    "return": ["status", "refund_amount", "approval_status"]
  }
}

AI: *understands completely in seconds*
AI: "I see the workflow, constraints, and integrations. Here's my analysis..."
"""

# ============================================================================
# PRACTICAL USE CASES
# ============================================================================

"""
USE CASE 1: Feature Request Analysis
=====================================
User: "Can customers return items after 45 days?"

AI (with cartographer):
  process_return() shows: "days_since_delivery > 30" raises ReturnWindowExpiredError
  Result: "No, the system enforces a 30-day return window. To support this,
           we'd need to change the constraint in process_return() and consider
           restocking fee implications."

USE CASE 2: Bug Investigation
================================
Issue: "Some orders stuck in PROCESSING status"

AI (with cartographer):
  Understands the state machine:
  CONFIRMED → PROCESSING/PRIORITY_PROCESSING → SHIPPED → DELIVERED
  
  Identifies the role-based logic:
  if role in ["manager", "admin"]:
    status = "PRIORITY_PROCESSING"
  else:
    status = "PROCESSING"
  
  Result: "Check if there's a filter for PRIORITY_PROCESSING orders.
           They may not be getting processed by the fulfillment system."

USE CASE 3: Compliance Audit
==============================
Compliance Officer: "Show me all financial constraints"

AI (with cartographer):
  Business Rules show:
  - create_refund() for original transaction amount minus restocking fee
  - Refund integrity tied to original payment_id
  - Email notifications for all transactions
  - 30-day fulfillment window
  
  Result: "All refunds are tied to original transactions with audit trail.
           System maintains 30-day SLA. Ready for audit."

USE CASE 4: Integration Testing
==================================
QA: "What are all external integrations?"

AI (with cartographer):
  Integrations extracted:
  - stripe_payment_gateway.process_payment()
  - stripe_payment_gateway.create_refund()
  - email_service.send_order_confirmation()
  - email_service.send_shipment_notification()
  - email_service.send_refund_notification()
  - inventory_system.reserve_items()
  - carrier.create_shipment()
  - event_bus.emit() [multiple events]
  
  Result: "5 external integrations identified. Here's the test matrix..."

USE CASE 5: Performance Optimization
======================================
DevOps: "Where's the bottleneck in checkout?"

AI (with cartographer):
  Identifies sequential integration calls:
  1. stripe_payment_gateway.process_payment() - BLOCKING
  2. Order.save()
  3. email_service.send_order_confirmation() - BLOCKING
  4. inventory_system.reserve_items() - BLOCKING
  5. event_bus.emit() - ASYNC
  
  Result: "Email and inventory calls are synchronous. Consider async with
           retry logic. Event bus is already async (good)."
"""
