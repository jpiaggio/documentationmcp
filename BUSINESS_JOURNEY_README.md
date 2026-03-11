# Business Rules & Customer Journey Cartographer

## Overview

The enhanced cartographer agent now focuses on **non-technical, business-level analysis** to map entire platforms' customer journeys and business logic. Instead of code structure and function calls, it extracts business insights that help AI understand:

- How customers move through your platform
- What business rules govern operations
- Which external systems are integrated
- How entities relate and interact
- What decisions shape customer experience

## What Gets Mapped

### 1. **Customer Journey Steps** 📍
Automatically identifies and maps key stages in customer workflows:
- **AUTHENTICATE** - User login/verification
- **BROWSE** - Product/content exploration  
- **SELECT_PRODUCT** - Adding to cart/wishlist
- **CHECKOUT** - Purchase initiation
- **NOTIFY** - Customer communications
- **UPDATE_STATUS** - Order/workflow state changes
- **SHIP** - Fulfillment dispatch
- **DELIVER** - Delivery completion
- **CANCEL** - Return/cancellation flows

### 2. **Business Entities** 🏢
Identifies domain entities and their properties:
- Customer, User, Account
- Order, Cart, CartItem
- Product, Inventory
- Payment, Invoice, Transaction
- Subscription, Shipment
- And more...

Each entity is mapped with its properties and relationships.

### 3. **Business Rules & Constraints** ⚖️
Extracts operational constraints:
- **Validations** - What must be true for operations
- **Constraints** - What prevents actions (insufficient balance, expired status, etc.)
- **Thresholds** - Rate limits, quotas, min/max values
- **Eligibility Rules** - Who can do what

### 4. **Business Processes** 🔄
Maps named workflows:
- Checkout process
- Refund workflow
- Onboarding flow
- Approval pipelines
- State machines

### 5. **Integrations** 🔌
Identifies external system connections:
- Payment gateways (Stripe, PayPal)
- Email/SMS providers
- Message queues (Kafka)
- Webhooks and APIs
- CRM systems
- Analytics platforms

### 6. **Business Events** 📢
Maps state transitions and event triggers:
- Order created
- Payment processed
- User registered
- Status updated
- Events that trigger actions

### 7. **Role-Based Access** 👥
Identifies authorization patterns:
- Admin, User, Guest roles
- Permission checks
- Access control logic
- Privilege-based workflows

## Understanding the Graph

The generated Neo4j graph creates relationships:

```
BusinessModule
  ├─ IMPLEMENTS → BusinessProcess (e.g., "checkout_workflow")
  ├─ MANAGES → BusinessEntity (e.g., "Order" with properties)
  ├─ CONTAINS_STEP → JourneyStep (e.g., "CHECKOUT", "NOTIFY")
  ├─ ENFORCES → BusinessRule (validations and constraints)
  ├─ DEFINES → Threshold (e.g., max_retries = 3)
  ├─ INTEGRATES_WITH → ExternalSystem (e.g., "stripe")
  ├─ TRIGGERS → BusinessEvent (e.g., "payment_processed")
  └─ REQUIRES_ROLE → Role (e.g., "admin")
```

## Customer Journey Example

For an e-commerce platform:

```
Customer
  → [AUTHENTICATE] User logs in
  → [BROWSE] Searches products
  → [SELECT_PRODUCT] Adds to cart
  → [CHECKOUT] Reviews order
  → [VALIDATE] Check balance, eligibility
  → [INTEGRATE] Payment Gateway processes payment
  → [UPDATE_STATUS] Order marked as confirmed
  → [NOTIFY] Confirmation email sent
  → [SHIP] Inventory updated, shipment created
  → [DELIVER] Order delivered
```

Along this journey, dozens of business rules apply:
- Min/max purchase amounts
- Inventory checks
- Regional shipping restrictions
- Payment method eligibility
- Subscription status validation
- Fraud detection rules

## Usage

### Extract Business Rules
```bash
python agents/cartographer_agent.py /path/to/repo
```

### Generate Business Insights
The agent creates Cypher statements that populate a Neo4j graph:

```cypher
MERGE (m:BusinessModule {name: 'checkout', path: '.../checkout.py'})
MERGE (p:BusinessProcess {name: 'checkout_workflow'})
MERGE (m)-[:IMPLEMENTS]->(p)

MERGE (e:BusinessEntity {name: 'Order', type: 'order'})
MERGE (m)-[:MANAGES]->(e)

MERGE (j:JourneyStep {name: 'CHECKOUT', sequence: 3})
MERGE (m)-[:CONTAINS_STEP]->(j)

MERGE (r:BusinessRule {type: 'VALIDATION', condition: 'customer.is_active'})
MERGE (m)-[:ENFORCES]->(r)

MERGE (int:ExternalSystem {name: 'stripe'})
MERGE (m)-[:INTEGRATES_WITH]->(int)
```

## The Business Graph in Action

### Query: What steps does a customer go through?
```cypher
MATCH (j:JourneyStep)-[:IN_PROCESS]-(p:BusinessProcess)
RETURN p.name, COLLECT(j.name) as steps
ORDER BY j.sequence
```

### Query: What business rules protect this operation?
```cypher
MATCH (p:BusinessProcess)-[:GOVERNED_BY]-(r:BusinessRule)
WHERE p.name = 'checkout_workflow'
RETURN r.condition, r.type
```

### Query: What integrations does checkout depend on?
```cypher
MATCH (m:BusinessModule)-[:IMPLEMENTS]-(p:BusinessProcess),
      (m)-[:INTEGRATES_WITH]-(i:ExternalSystem)
WHERE p.name = 'checkout_workflow'
RETURN COLLECT(i.name)
```

### Query: Which entities are modified during this journey?
```cypher
MATCH (j:JourneyStep)-[:MODIFIES]-(e:BusinessEntity)
RETURN j.name, COLLECT(e.name)
ORDER BY j.sequence
```

## Key Use Cases

1. **Platform Documentation** - Provide AI with complete platform architecture
2. **Integration Planning** - See what we connect to and where
3. **Compliance Mapping** - Trace data flows and access controls
4. **Change Impact Analysis** - Understand what breaks when rules change
5. **Customer Journey Optimization** - Identify friction points and opportunities
6. **Business Process Modernization** - Find legacy, complex, or inefficient flows
7. **Onboarding New Developers** - Show them "how it actually works"
8. **Decision Logic Documentation** - Explicit business rule traceability

## Extraction Examples

### Business Process Detection
```python
def checkout_workflow(customer_id):  # Detected: WORKFLOW
    # Cypher: MERGE (p:BusinessProcess {name: 'checkout_workflow'})
```

### Entity Recognition
```python
class Order:  # Detected: BUSINESS_ENTITY
    # Cypher: MERGE (e:BusinessEntity {name: 'Order', type: 'order'})
```

### Rule Extraction
```python
if customer.balance < total:  # Detected: THRESHOLD rule
    raise InsufficientFundsError()  # Detected: CONSTRAINT

if not is_eligible(customer):  # Detected: VALIDATION
    return False
```

### Integration Detection
```python
stripe.charge(customer, amount)  # Detected: INTEGRATES_WITH stripe
send_email(user.email, receipt)  # Detected: INTEGRATES_WITH email
```

### Event/State Detection
```python
order.status = "CONFIRMED"  # Detected: STATE_TRANSITION
emit_event("order_paid")    # Detected: BUSINESS_EVENT
```

## Next Steps

To make your platform fully intelligible to AI:

1. **Enrich your code comments** - Add business context (why, not just what)
2. **Use consistent naming** - Follow patterns the extractor recognizes
3. **Document business rules** - Make constraints explicit
4. **Mark integrations** - Label external service calls
5. **Comment decision logic** - Explain the "why" behind conditionals

The more explicit your business logic is in the code, the richer the insights extracted.
