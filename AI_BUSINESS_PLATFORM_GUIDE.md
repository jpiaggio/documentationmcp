# AI-Driven Business Platform Analysis with Cartographer MCP

## Overview

Your enhanced cartographer system is now designed to help AI understand **how your platform works from a business perspective**, not just code structure. This is perfect for:

- **Providing context to AI agents** about customer journeys
- **Understanding business rules** without reading code
- **Mapping integrations** and external dependencies
- **Explaining platform capabilities** to stakeholders
- **Generating documentation** from actual implementation
- **Training AI models** on your business logic

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│            Repository with Business Logic               │
│                  (Python/Java code)                     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  cartographer_agent.py       │
        │  (Business Rules Extraction) │
        └──────────────────┬───────────┘
                           │
                           ▼
        ┌──────────────────────────────┐
        │  Cypher Statements           │
        │  (4500+ insights per repo)   │
        └──────────────────┬───────────┘
                           │
    ┌──────────┬───────────┼───────────┬──────────┐
    │          │           │           │          │
    ▼          ▼           ▼           ▼          ▼
 Neo4j    MongoDB      CSV         JSON     Business
 Graph    Storage      Export      Export   Reports
    │          │           │           │          │
    └──────────┼───────────┼───────────┼──────────┘
               │           │           │
               ▼           ▼           ▼
         Business Journey Analyzer
         (business_journey_analyzer.py)
         │
         ▼
    MCP Business Server
    (mcp_business_server.py)
         │
         ▼
    AI / Claude / Agents
    Can now understand your platform!
```

## Components

### 1. **cartographer_agent.py** - Business Rules Extractor
Scans code and extracts:
- Customer journey steps
- Business entities
- Business processes
- Business rules & constraints
- Integration points
- State transitions and events
- Role-based access patterns

```bash
# Run business rules extraction
python3 agents/cartographer_agent.py /path/to/repo
# Outputs 1000s of Cypher statements
```

### 2. **business_rules_extractor.py** - Pattern Recognition
Uses regex and code analysis to identify:
- Workflow keywords (checkout_workflow, process_order, etc.)
- Business entities (User, Order, Payment, etc.)
- Journey steps (AUTHENTICATE, CHECKOUT, etc.)
- Business rules (validation, constraints, thresholds)
- Integrations (stripe, email, kafka, etc.)
- Events (order_created, payment_processed, etc.)
- Roles (admin, customer, vendor, etc.)

### 3. **business_journey_analyzer.py** - Graph Analysis
Parses Cypher statements and builds insights:
- Complete customer journey mapping
- Entity relationship summary
- Integration topology
- Business rule count and types
- Process discovery
- Data flow tracing

```bash
# Analyze and generate business context
python3 agents/business_journey_analyzer.py /path/to/repo
# Outputs: Business context suitable for AI understanding
```

### 4. **mcp_business_server.py** - MCP Server
Exposes insights as tools for AI:
- `analyze_customer_journey()` - Get complete journey
- `get_business_entities()` - List entities and properties
- `get_integration_points()` - External dependencies
- `get_business_rules()` - Constraints and validations
- `get_platform_processes()` - All workflows
- `explain_step()` - Explain journey step
- `trace_data_flow()` - See data movement
- `get_platform_overview()` - Comprehensive summary

## What Gets Extracted

### Customer Journey Patterns
```
AUTHENTICATE → BROWSE → SELECT_PRODUCT → CHECKOUT → NOTIFY 
→ UPDATE_STATUS → SHIP → DELIVER → CANCEL
```

### Business Entities
- **Customer**: profile, preferences, history
- **Order**: items, total, status, shipping address
- **Product**: inventory, pricing, categories
- **Payment**: method, status, amount
- **Shipment**: tracking, carrier, expected delivery

### Business Rules (248 rules in sample)
- **VALIDATION**: customer must be active, balance sufficient
- **CONSTRAINT**: max quantity per order, age restrictions
- **THRESHOLD**: max retries, rate limits, timeout values

### Integrations (2+ each platform)
- Payment gateways (Stripe, PayPal)
- Email providers
- Message queues
- Analytics platforms
- CRM systems

### Business Processes
- `checkout_workflow` - Complete purchase
- `order_fulfillment` - Pack and ship
- `return_process` - Handle returns
- `notification_system` - Send communications
- `payment_reconciliation` - Match transactions

## Usage Examples

### Example 1: Understanding an E-Commerce Platform

```bash
python3 agents/cartographer_agent.py ~/projects/ecommerce 2>/dev/null | \
    python3 agents/business_journey_analyzer.py
```

Output:
```
## Platform Business Context

### Customer Journey
Path: AUTHENTICATE → BROWSE → SELECT_PRODUCT → CHECKOUT → NOTIFY → ...
Total Steps: 8

### Business Entities
- Customer: User, Profile, Preferences
- Order: Order, OrderItem, ShoppingCart
- Product: Product, Inventory, Catalog
- Payment: Payment, Transaction, Refund

### Business Rules
Total Rules: 546
- VALIDATION: 420
- CONSTRAINT: 98
- THRESHOLD: 28

### External Integrations
- Stripe (payments)
- SendGrid (email)
- RabbitMQ (messaging)

### Business Processes
- checkout_workflow
- order_fulfillment
- return_process
- notification_system
```

### Example 2: Providing Context to Claude

```python
# Get business context from your platform
from agents.mcp_business_server import BusinessRulesMCPServer

server = BusinessRulesMCPServer('/path/to/repo')

# Use in prompt
prompt = f"""
Here's the business architecture of our platform:

{server.get_platform_overview()['business_context']}

Now, can you:
1. Explain the customer journey?
2. Identify bottlenecks?
3. Suggest improvements?
"""

# Send to Claude API
response = claude.messages.create(messages=[{"role": "user", "content": prompt}])
```

### Example 3: Data Flow Analysis

```bash
python3 -c "
from agents.mcp_business_server import BusinessRulesMCPServer

server = BusinessRulesMCPServer('.')
result = server.trace_data_flow('CHECKOUT', 'DELIVER')
print(f'Data flows through: {result[\"flow\"]}')
print(f'Steps involved: {len(result[\"steps\"])}')
"
```

## Integration Points

### With Claude API
```python
tools = mcp_server.get_tools()
# Claude can now call:
# - analyze_customer_journey
# - get_business_rules
# - explain_step
# etc.
```

### With Neo4j
```bash
# Generate Cypher statements
python3 agents/cartographer_agent.py /path/to/repo | \
    cypher-shell -u neo4j -p password

# Query graph
cypher> MATCH (j:JourneyStep) RETURN j.name ORDER BY j.sequence
```

### With Documentation Generators
```bash
# Extract insights to JSON
python3 agents/cartographer_agent.py /path/to/repo > insights.json

# Convert to documentation
python3 -c "
import json
with open('insights.json') as f:
    insights = json.load(f)
    
# Generate markdown docs
print('# Platform Architecture')
print(f'## Customer Journey: {insights[\"journey_path\"]}')
print(f'## Integrations: {insights[\"integrations\"]}')
"
```

## Best Practices for Maximum Extraction

### 1. Use Clear Business Names
```python
# Good ✅
def checkout_workflow(customer):
    validate_customer_eligibility(customer)
    process_payment(customer.payment_method)
    
# Also extracted but less clear ❌
def do_stuff(c):
    check(c)
    pay(c.m)
```

### 2. Document Business Rules Explicitly
```python
# Good ✅
if customer.age < 18:
    raise EligibilityError("Customers must be 18+")

if order.total > customer.credit_limit:
    raise InsufficientCreditError()

# Extracted but less specific ❌
if not valid(customer):
    return False
```

### 3. Label Business Entities
```python
# Good ✅
class CustomerProfile:
    """Manages customer account and preferences"""
    def __init__(self, customer_id):
        self.customer = Customer.get(customer_id)
        
# Also works but less explicit ❌
class CP:
    def __init__(self, cid):
        self.c = get(cid)
```

### 4. Mark Integrations
```python
# Good ✅
payment_gateway = StripePaymentGateway()
email_service = SendgridEmailService()
message_queue = RabbitMQQueue()

# Works but less discoverable ❌
pg = setup_payment()
es = setup_email()
```

## What AI Understands From This

With the business insights extracted, AI can now:

✅ **Understand customer journeys** without reading code
✅ **Identify business constraints** that affect behavior
✅ **Map data flow** through the system
✅ **Recognize integration dependencies** 
✅ **Understand role-based logic** and permissions
✅ **Trace impact** of changes
✅ **Generate documentation** automatically
✅ **Suggest optimizations** based on rules and constraints
✅ **Answer "why does this work this way?"** questions
✅ **Onboard developers** faster

## Example: AI Understanding Your Checkout Process

**Without this tool:**
> "I need to read 50 files to understand how checkout works..."

**With this tool:**
```python
server.explain_step("CHECKOUT")
# {
#   "step": "CHECKOUT",
#   "description": "Customer reviews order, applies promotions, enters shipping",
#   "previous_step": "SELECT_PRODUCT",
#   "next_step": "NOTIFY"
# }

rules = server.get_business_rules("VALIDATION")
# {
#   "total_rules": 200,
#   "types": {"VALIDATION": 200, "CONSTRAINT": 35, "THRESHOLD": 11},
#   "description": "200 validation rules enforce checkout process"
# }

integrations = server.get_integration_points()
# {
#   "integrations": ["stripe", "email", "inventory_system"],
#   "checkout_systems": ["stripe"]
# }
```

AI now has complete context without reading any code!

## Next Steps

1. **Run analysis on your repo**
   ```bash
   python3 agents/cartographer_agent.py /path/to/your/repo
   ```

2. **Load into Neo4j**
   ```bash
   python3 agents/cartographer_agent.py /path/to/your/repo | cypher-shell
   ```

3. **Generate business context**
   ```bash
   python3 agents/business_journey_analyzer.py /path/to/your/repo
   ```

4. **Create MCP server**
   ```bash
   python3 agents/mcp_business_server.py /path/to/your/repo
   ```

5. **Use with Claude or other AI**
   ```python
   server = BusinessRulesMCPServer('/path/to/repo')
   # Now use server.get_tools() with your favorite AI
   ```

## Summary

Your platform is now **intelligible to AI** at the business level, not just the code level. This enables:
- Faster onboarding
- Better documentation
- More informed refactoring decisions
- Compliance verification
- Business process optimization
- Natural language understanding of system behavior
