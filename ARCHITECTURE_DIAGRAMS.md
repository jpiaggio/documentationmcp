"""
Visual System Architecture & Data Flow

This file documents the complete data flow and system architecture using ASCII diagrams.
"""

# ============================================================================
# SYSTEM ARCHITECTURE
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BUSINESS CARTOGRAPHER SYSTEM                         │
└─────────────────────────────────────────────────────────────────────────────┘

SOURCE: Your Codebase
┌─────────────────────────────┐
│  Python / Java / Mixed      │
│  ├─ Business Logic          │
│  ├─ Data Models             │
│  ├─ API Endpoints           │
│  ├─ Workflow Classes        │
│  └─ External Integrations   │
└────────────────┬────────────┘
                 │
                 ▼
EXTRACTION LAYER
┌──────────────────────────────────────────────────────────────────┐
│  cartographer_agent.py                                           │
│  ├─ Business Rules Extractor (business_rules_extractor.py)     │
│  │  ├─ Pattern Recognition                                      │
│  │  ├─ Keyword Matching                                         │
│  │  └─ Business Logic Identification                            │
│  └─ Generates Cypher Statements (4000+ per repo)              │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
INTERMEDIATE: Cypher Statements
┌─────────────────────────────┐
│ MERGE (m:BusinessModule)    │
│ MERGE (e:BusinessEntity)    │
│ MERGE (j:JourneyStep)       │
│ MERGE (r:BusinessRule)      │
│ MERGE (i:ExternalSystem)    │
│ MERGE (ev:BusinessEvent)    │
│ ... (1000s of statements)   │
└────────────────┬────────────┘
                 │
        ┌────────┴────────┬──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
    Neo4j DB      JSON Export         CSV Export
    (Graph)     (Queries/APIs)     (Spreadsheet)
        │                 │                  │
        └────────┬────────┴──────────────────┘
                 │
                 ▼
ANALYSIS LAYER
┌──────────────────────────────────────────────────────┐
│  business_journey_analyzer.py                        │
│  ├─ Parse Cypher Statements                         │
│  ├─ Build Business Graph                            │
│  ├─ Extract Journey Path                            │
│  ├─ Summarize Rules & Constraints                   │
│  ├─ Identify Integrations                           │
│  ├─ List Processes & Events                         │
│  └─ Generate Business Context (Markdown)            │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
OUTPUT: Business Context
┌──────────────────────────────────────────┐
│ Customer Journey Path                    │
│ Business Entities Summary                │
│ Rules & Constraints Count                │
│ Integration Topology                     │
│ Process Descriptions                     │
│ Event & State Transitions                │
│ AI-Friendly Markdown Context             │
└────────────────┬─────────────────────────┘
                 │
                 ▼
MCP/TOOL LAYER
┌──────────────────────────────────────────────────────┐
│  mcp_business_server.py                              │
│  ├─ Tool 1: analyze_customer_journey()              │
│  ├─ Tool 2: get_business_entities()                 │
│  ├─ Tool 3: get_integration_points()                │
│  ├─ Tool 4: get_business_rules()                    │
│  ├─ Tool 5: get_platform_processes()                │
│  ├─ Tool 6: explain_step()                          │
│  ├─ Tool 7: get_platform_overview()                 │
│  └─ Tool 8: trace_data_flow()                       │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
AI / CLAUDE API
┌────────────────────────────────────────────────────┐
│  Claude / AI Agents / Automated Systems            │
│  ├─ Understands Customer Journeys                  │
│  ├─ Knows All Business Rules                       │
│  ├─ Aware of Integrations                          │
│  ├─ Maps Data Flows                                │
│  ├─ Identifies Access Controls                     │
│  └─ Answers Business Questions                     │
└────────────────────────────────────────────────────┘
"""

# ============================================================================
# DATA TRANSFORMATION FLOW
# ============================================================================

"""
INPUT: Raw Code
─────────────────

class Order:
    def __init__(self, customer_id, items, total):
        self.customer_id = customer_id
        self.items = items
        self.total = total
        self.status = "CONFIRMED"

def checkout_workflow(customer_id, items):
    customer = get_customer(customer_id)
    if not customer.is_active:
        raise CustomerInactiveError()
    
    order = Order(customer_id, items, calc_total(items))
    stripe.process_payment(customer, order.total)
    email.send_confirmation(customer.email, order)
    return order


PROCESSING: Pattern Extraction
────────────────────────────────

Step 1: Keyword Matching
├─ "Order" + "class_declaration" → BusinessEntity
├─ "checkout_workflow" + "def_name" → BusinessProcess
├─ "customer.is_active" in conditional → ValidationRule
├─ "stripe.process_payment" → Integration(stripe)
└─ "email.send_confirmation" → Integration(email)

Step 2: Structure Analysis
├─ Properties: customer_id, items, total, status → Entity fields
├─ State: "CONFIRMED" assignment → StateTransition
├─ Function params: customer_id, items → EntityReferences
└─ Call sequences: stripe → email → EventTrigger

Step 3: Business Rule Extraction
├─ "if not customer.is_active" → Validation rule
├─ "CONFIRMED" status → State value
├─ Dependencies: Order depends on Customer


OUTPUT: Business Graph
──────────────────────

Cypher Statements:
MERGE (m:BusinessModule {name: 'checkout'})
MERGE (e:BusinessEntity {name: 'Order', properties: ['customer_id', 'items', 'total', 'status']})
MERGE (m)-[:MANAGES]->(e)
MERGE (j:JourneyStep {name: 'CHECKOUT', sequence: 2})
MERGE (m)-[:CONTAINS_STEP]->(j)
MERGE (r:BusinessRule {type: 'VALIDATION', condition: 'customer.is_active'})
MERGE (m)-[:ENFORCES]->(r)
MERGE (i:ExternalSystem {name: 'stripe'})
MERGE (m)-[:INTEGRATES_WITH]->(i)
MERGE (ev:BusinessEvent {name: 'order_confirmed'})
MERGE (m)-[:TRIGGERS]->(ev)


ANALYSIS: Business Context
──────────────────────────

Journey Steps Found:
├─ AUTHENTICATE (from is_active check)
├─ CHECKOUT (from function name)
├─ VALIDATE (from condition)
├─ NOTIFY (from email.send_confirmation)
└─ UPDATE_STATUS (from status = "CONFIRMED")

Entities Identified:
├─ Order (with properties: customer_id, items, total, status)
└─ Customer (referenced in validation)

Rules Discovered:
├─ VALIDATION: customer.is_active required
└─ State transitions to CONFIRMED

Integrations Detected:
├─ stripe (payment processing)
└─ email (notifications)

Events Triggered:
└─ order_confirmed (implicit in workflow)


FINAL CONTEXT: For AI Understanding
────────────────────────────────────

{
  "journey_path": "AUTHENTICATE → CHECKOUT → VALIDATE → NOTIFY → UPDATE_STATUS",
  "entities": {
    "order": ["customer_id", "items", "total", "status"],
    "customer": [...]
  },
  "business_rules": {
    "validations": 1,
    "constraints": 0,
    "thresholds": 0
  },
  "integrations": ["stripe", "email"],
  "processes": ["checkout_workflow"],
  "events": ["order_confirmed"]
}

AI Understanding Achieved:
✅ Knows what checkout does
✅ Knows what rules must pass
✅ Knows external dependencies
✅ Knows data entities involved
✅ Can answer business questions
"""

# ============================================================================
# EXTRACTION PATTERN EXAMPLES
# ============================================================================

"""
PATTERN 1: Journey Step Recognition
────────────────────────────────────

Code:
  def authenticate_user(username, password):
  def browse_products(category):
  def add_to_cart(product_id):
  def process_checkout(cart):

Pattern Matching:
  authenticate_* → AUTHENTICATE
  browse_* → BROWSE
  *_cart → SELECT_PRODUCT
  checkout_* → CHECKOUT

Extracted:
  JourneyStep(AUTHENTICATE, sequence: 0)
  JourneyStep(BROWSE, sequence: 1)
  JourneyStep(SELECT_PRODUCT, sequence: 2)
  JourneyStep(CHECKOUT, sequence: 3)


PATTERN 2: Business Entity Recognition
───────────────────────────────────────

Code:
  class Customer:
      def __init__(self, customer_id, email, balance):
  
  class Order:
      def __init__(self, order_id, items, total):

Pattern Matching:
  Class name contains "customer" → BUSINESS_ENTITY
  Extract properties: customer_id, email, balance
  
  Class name contains "order" → BUSINESS_ENTITY
  Extract properties: order_id, items, total

Extracted:
  BusinessEntity(Customer, properties: [customer_id, email, balance])
  BusinessEntity(Order, properties: [order_id, items, total])


PATTERN 3: Business Rule Extraction
────────────────────────────────────

Code:
  if not customer.is_active:
      raise CustomerInactiveError()
  
  if order.total > 10000:
      raise MaxOrderError()
  
  if account_age < 7:
      raise MinAgeError()

Pattern Matching:
  Conditional + error raise → VALIDATION or CONSTRAINT
  Variable > number → THRESHOLD
  Variable < number → THRESHOLD

Extracted:
  BusinessRule(VALIDATION, condition: "customer.is_active")
  BusinessRule(THRESHOLD, variable: "order.total", value: "10000")
  BusinessRule(CONSTRAINT, variable: "account_age", min: "7")


PATTERN 4: Integration Detection
─────────────────────────────────

Code:
  stripe.process_payment(amount)
  email.send_notification(user_email)
  kafka_queue.emit(event)
  http_client.call(url)

Pattern Matching:
  Function call to known integration keyword
  stripe → payment gateway
  email → communication
  kafka → message queue
  http_client → external API

Extracted:
  ExternalSystem(stripe, type: payment)
  ExternalSystem(email, type: communication)
  ExternalSystem(kafka_queue, type: messaging)
  ExternalSystem(http_client, type: api)
"""

# ============================================================================
# QUERY EXAMPLES
# ============================================================================

"""
CYPHER QUERY 1: Complete Customer Journey
──────────────────────────────────────────

MATCH (j:JourneyStep)
RETURN j.name, j.sequence
ORDER BY j.sequence

Result:
┌────────────────┬──────────┐
│     name       │ sequence │
├────────────────┼──────────┤
│ AUTHENTICATE   │    0     │
│ BROWSE         │    1     │
│ SELECT_PRODUCT │    2     │
│ CHECKOUT       │    3     │
│ NOTIFY         │    4     │
│ UPDATE_STATUS  │    5     │
│ SHIP           │    6     │
│ DELIVER        │    7     │
│ CANCEL         │    8     │
└────────────────┴──────────┘


CYPHER QUERY 2: Business Rules for Checkout
────────────────────────────────────────────

MATCH (m:BusinessModule)-[:ENFORCES]->(r:BusinessRule)
WHERE m.name = 'checkout'
RETURN r.type, COUNT(*) as count

Result:
┌──────────────┬───────┐
│     type     │ count │
├──────────────┼───────┤
│ VALIDATION   │  12   │
│ CONSTRAINT   │   4   │
│ THRESHOLD    │   2   │
└──────────────┴───────┘


CYPHER QUERY 3: Integration Topology
──────────────────────────────────────

MATCH (m:BusinessModule)-[:INTEGRATES_WITH]->(i:ExternalSystem)
RETURN i.name as system, COUNT(m) as usage_count
ORDER BY usage_count DESC

Result:
┌─────────────┬─────────────┐
│   system    │ usage_count │
├─────────────┼─────────────┤
│ stripe      │      8      │
│ email       │      6      │
│ kafka       │      4      │
│ inventory   │      3      │
└─────────────┴─────────────┘


CYPHER QUERY 4: Entity Relationships
─────────────────────────────────────

MATCH (e1:BusinessEntity)-[r]->(e2:BusinessEntity)
RETURN e1.name, TYPE(r), e2.name

Result:
┌───────────┬─────────────┬──────────┐
│   e1      │ relationship│   e2     │
├───────────┼─────────────┼──────────┤
│ Customer  │ HAS_MANY    │ Order    │
│ Order     │ CONTAINS    │ Item     │
│ Item      │ HAS_PRICE   │ Product  │
│ Order     │ LINKS_TO    │ Payment  │
└───────────┴─────────────┴──────────┘
"""

# ============================================================================
# TOOL DEFINITIONS FOR MCP
# ============================================================================

"""
Tool 1: analyze_customer_journey
─────────────────────────────────

Input: None

Output: {
  "journey_path": "AUTHENTICATE → BROWSE → CHECKOUT → SHIP → DELIVER",
  "steps": ["AUTHENTICATE", "BROWSE", "CHECKOUT", "SHIP", "DELIVER"],
  "description": "The customer journey has 5 main steps..."
}

Use Case: Understand the complete customer flow


Tool 2: get_business_entities
──────────────────────────────

Input: entity_type (optional)

Output: {
  "entities_by_type": {
    "customer": ["Customer", "Profile"],
    "order": ["Order", "CartItem"],
    "product": ["Product", "Inventory"]
  },
  "total_entity_types": 3
}

Use Case: Understand data models and entities


Tool 3: get_integration_points
───────────────────────────────

Input: None

Output: {
  "integrations": ["stripe", "email", "kafka"],
  "integration_count": 3,
  "by_type": {
    "payments": ["stripe"],
    "communications": ["email"],
    "messaging": ["kafka"]
  }
}

Use Case: Find external dependencies and system connections


Tool 4: get_business_rules
──────────────────────────

Input: rule_type (optional: VALIDATION, CONSTRAINT, THRESHOLD)

Output: {
  "total_rules": 246,
  "by_type": {
    "VALIDATION": 200,
    "CONSTRAINT": 35,
    "THRESHOLD": 11
  }
}

Use Case: Understand constraints and validation rules


Tool 5: get_platform_processes
───────────────────────────────

Input: None

Output: {
  "processes": [
    "checkout_workflow",
    "order_fulfillment",
    "return_process",
    "payment_reconciliation"
  ],
  "total": 4
}

Use Case: Discover business workflows and processes


Tool 6: explain_step
────────────────────

Input: step ("CHECKOUT", "NOTIFY", etc.)

Output: {
  "step": "CHECKOUT",
  "description": "Customer reviews order, applies promotions, enters shipping",
  "sequence": 3,
  "previous_step": "SELECT_PRODUCT",
  "next_step": "NOTIFY"
}

Use Case: Understand what happens at each journey step


Tool 7: get_platform_overview
──────────────────────────────

Input: None

Output: {
  "journey": { ... },
  "entities": { ... },
  "integrations": { ... },
  "rules": { ... },
  "processes": { ... },
  "business_context": "markdown formatted context..."
}

Use Case: Get comprehensive platform understanding


Tool 8: trace_data_flow
───────────────────────

Input: start_step, end_step (optional)

Output: {
  "flow": "CHECKOUT → NOTIFY → UPDATE_STATUS → SHIP",
  "steps": [...],
  "description": "Data flows through 4 steps starting from CHECKOUT"
}

Use Case: Understand how data moves through the system
"""
