# Business Cartographer Documentation Index

## Quick Navigation

### 🚀 Getting Started
- **[SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md)** - Complete overview and quick start
- **[CHANGELOG.md](CHANGELOG.md)** - What's new in this version
- **[BUSINESS_JOURNEY_README.md](BUSINESS_JOURNEY_README.md)** - Business analysis focus

### 📚 In-Depth Guides
- **[AI_BUSINESS_PLATFORM_GUIDE.md](AI_BUSINESS_PLATFORM_GUIDE.md)** - Comprehensive MCP and AI integration guide
- **[ECOMMERCE_EXAMPLE.md](ECOMMERCE_EXAMPLE.md)** - Real-world e-commerce platform example

### 💻 Code Components
- `agents/cartographer_agent.py` - Main extraction engine (now business-focused)
- `agents/business_rules_extractor.py` - Business insight extraction
- `agents/business_journey_analyzer.py` - Analysis and graph building
- `agents/mcp_business_server.py` - MCP server for AI tools

---

## What This System Does

### Transforms This ❌
```python
def checkout(customer_id, items):
    # 50+ lines of business logic
    # 10+ business rules embedded
    # 3+ external integrations
    # Multiple state transitions
```

### Into This ✅
```json
{
  "customer_journey": "AUTHENTICATE → BROWSE → CHECKOUT → PAY → SHIP → DELIVER",
  "business_rules": {
    "validations": 120,
    "constraints": 45,
    "thresholds": 15
  },
  "integrations": ["stripe", "email", "inventory"],
  "state_transitions": ["CONFIRMED", "PROCESSING", "SHIPPED"],
  "entities": ["Customer", "Order", "Payment", "Shipment"]
}
```

**Result**: AI understands your entire platform without reading any code!

---

## Five-Minute Quick Start

### 1. Extract Business Rules (2 min)
```bash
python3 agents/cartographer_agent.py /path/to/your/repo
# Extracts 1000s of business insights
```

### 2. Analyze Insights (1 min)
```bash
python3 agents/business_journey_analyzer.py /path/to/your/repo
# Generates business context summary
```

### 3. Start MCP Server (1 min)
```bash
python3 agents/mcp_business_server.py /path/to/your/repo
# Ready for Claude/AI integration
```

### 4. Use with AI (1 min)
```python
from agents.mcp_business_server import BusinessRulesMCPServer

server = BusinessRulesMCPServer('/path/to/repo')
journey = server.analyze_customer_journey()
print(journey['journey_path'])
# Output: AUTHENTICATE → BROWSE → CHECKOUT → SHIP → DELIVER
```

---

## What Gets Extracted

### 📍 Customer Journey
Complete path customer takes through platform:
- AUTHENTICATE - User login
- BROWSE - Product exploration
- SELECT_PRODUCT - Add to cart
- CHECKOUT - Purchase
- NOTIFY - Communications
- UPDATE_STATUS - Process updates
- SHIP - Fulfillment
- DELIVER - Delivery
- CANCEL - Returns

### 💼 Business Entities
Domain objects and their relationships:
- Customer (with properties: is_active, balance)
- Order (with properties: items, total, status)
- Product, Payment, Shipment, etc.

### ⚖️ Business Rules
Constraints that govern platform:
- **Validations**: Conditions that must be true
- **Constraints**: Things that prevent actions (return window 30 days)
- **Thresholds**: Limits and quotas (max order $10,000)
- **Roles**: Access control (admin vs customer)

### 🔌 Integrations
External system connections:
- Payment gateways (Stripe, PayPal)
- Communication (Email, SMS, Slack)
- Fulfillment (Inventory, Shipping)
- Analytics, Monitoring, etc.

### 📊 Business Processes
Named workflows:
- Checkout workflow
- Order fulfillment
- Return processing
- Payment reconciliation
- Etc.

### 👥 Role-Based Access
Authorization patterns:
- Who can perform actions
- Permission boundaries
- Privilege escalation rules

---

## Use Cases

### 🤖 For AI Agents / Claude
Use the MCP server to give Claude complete platform context:
```python
tools = server.get_tools()
# Claude now has tools to understand:
# - Customer journeys
# - Business rules
# - Integrations
# - Data flows
```

### 📖 For Documentation
Auto-generate platform documentation:
```bash
python3 agents/business_journey_analyzer.py /repo > platform-docs.md
```

### 🧪 For QA / Testing
Generate comprehensive test matrices:
- All business rules to test
- All integrations to mock
- All journey paths to verify

### 🔍 For Compliance
Audit business logic:
- Data flow tracking
- Access control verification
- Rule enforcement validation

### 👨‍💼 For Product Teams
Understand platform capabilities:
- What customers can/can't do
- Where business rules prevent actions
- Integration dependencies

### 👨‍💻 For New Developers
Fast onboarding:
- Understand architecture in minutes
- See customer journey clearly
- Know all business rules upfront

---

## Advanced Usage

### Load into Neo4j Graph Database
```bash
python3 agents/cartographer_agent.py /repo | cypher-shell -u neo4j -p password
```

Then query business relationships:
```cypher
# Find all journey steps in order
MATCH (j:JourneyStep) RETURN j.name ORDER BY j.sequence

# Find all business rules for checkout
MATCH (m:BusinessModule)-[:ENFORCES]->(r:BusinessRule)
WHERE m.name = 'checkout'
RETURN r.condition, r.type

# Find external integrations
MATCH (m:BusinessModule)-[:INTEGRATES_WITH]->(i:ExternalSystem)
RETURN m.name, COLLECT(i.name)
```

### Integrate with Claude API
```python
from anthropic import Anthropic
from agents.mcp_business_server import BusinessRulesMCPServer

server = BusinessRulesMCPServer('/path/to/repo')
client = Anthropic()

# Get business tools
tools = server.get_tools()

# Now Claude can understand your platform
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "What is the customer journey in our platform?"
    }]
)
```

### Generate Business Rules Report
```python
from agents.business_journey_analyzer import BusinessJourneyAnalyzer

analyzer = BusinessJourneyAnalyzer(cypher_statements)

# Get business context for documentation
context = analyzer.get_business_context()
print(context)

# Or analyze specific aspects
journey = analyzer.get_customer_journey()
rules = analyzer.get_business_rules_summary()
integrations = analyzer.get_integrations()
```

---

## File Organization

### Documentation Files
```
BUSINESS_JOURNEY_README.md       ← Understanding the graph
AI_BUSINESS_PLATFORM_GUIDE.md    ← Comprehensive guide
ECOMMERCE_EXAMPLE.md             ← Real-world example
SYSTEM_SUMMARY.md                ← Quick reference
CHANGELOG.md                      ← What's new
BUSINESS_CARTOGRAPHER_INDEX.md   ← You are here
```

### Code Files
```
agents/
├── cartographer_agent.py         ← Main entry point
├── business_rules_extractor.py   ← Pattern recognition
├── business_journey_analyzer.py  ← Graph analysis
└── mcp_business_server.py        ← MCP tools server
```

---

## Key Concepts

### 🎯 Business-First Approach
Unlike traditional code analysis tools, this system focuses on:
- **What** the business does (not how code is structured)
- **Why** rules exist (not implementation details)
- **Who** does what (not class hierarchies)
- **Where** data flows (not function calls)

### 🔄 Journey Mapping
Customer paths through the system:
```
Entry → Step1 → Step2 → Step3 → ... → Exit
```

Each step may have:
- Business rules that must pass
- Integrations that are called
- State transitions that occur
- Data entities that are created/modified

### 📊 Neo4j Graph Structure
Relationships between business concepts:
```
BusinessModule
├─ IMPLEMENTS → BusinessProcess
├─ MANAGES → BusinessEntity
├─ CONTAINS_STEP → JourneyStep
├─ ENFORCES → BusinessRule
├─ INTEGRATES_WITH → ExternalSystem
├─ TRIGGERS → BusinessEvent
└─ REQUIRES_ROLE → Role
```

---

## Frequently Asked Questions

### Q: How much code does it analyze?
**A**: All Python and Java files in the repository. Scans for business patterns and keywords.

### Q: How long does analysis take?
**A**: Typically 1-5 minutes for a typical codebase, depending on size and complexity.

### Q: Can I use this with existing Neo4j databases?
**A**: Yes! Load the Cypher statements into any Neo4j instance and query the graph.

### Q: What if my code doesn't follow the patterns?
**A**: The system is pattern-based but also uses keyword matching. Add business context comments for better extraction.

### Q: Can I customize what gets extracted?
**A**: Yes! Edit the keyword lists in `business_rules_extractor.py` to match your domain.

### Q: Is this just for Python?
**A**: Started with Python, has Java support, easily extends to other languages.

### Q: How do I integrate with Claude?
**A**: Use the MCP server tools or call the API directly from your application.

---

## Support & Next Steps

1. **Read SYSTEM_SUMMARY.md** for comprehensive overview
2. **Check ECOMMERCE_EXAMPLE.md** to see real-world usage
3. **Study AI_BUSINESS_PLATFORM_GUIDE.md** for integration details
4. **Run on your repository** to see it in action
5. **Load into Neo4j** for advanced graph queries
6. **Connect to Claude** for AI-powered platform understanding

---

## Summary

Your platform is now **intelligible to AI** without reading code. You have:

✅ Complete customer journey mapping
✅ All business rules extracted
✅ Integration topology
✅ Entity relationships
✅ State machines and events
✅ Role-based access patterns

**All in structured, queryable format!**

Start with SYSTEM_SUMMARY.md →
