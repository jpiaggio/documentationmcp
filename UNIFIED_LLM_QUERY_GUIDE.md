# Unified LLM Query Interface Guide

**Status:** ✅ New  
**Date:** March 2026  
**Models:** Claude, Gemini, and other LLM clients

---

## Overview

The **Unified LLM Query Interface** combines all three query methods into a single, cohesive API that LLMs can use seamlessly. Instead of trying to remember which tool does what, you can:

- **Ask natural language questions** that automatically route to the right query method
- **Use specific structured queries** when you know exactly what you need
- **Get intelligent result aggregation** when multiple methods are relevant
- **Benefit from smart caching** to minimize API calls

---

## Everything in One Place

```
Your Code Repository
        ↓
UnifiedLLMQueryInterface
        ↓
   ┌────┴─────┬────────┬──────────┐
   ↓          ↓        ↓          ↓
Structural  Business  Semantic   Graph
Queries     Logic     Analysis   Queries
(modules,   (rules,   (code      (flows,
functions)  journeys) meaning)   paths)
   ↓          ↓        ↓          ↓
   └────┬─────┴────────┴──────────┘
        ↓
   Claude/Other LLMs
```

---

## Quick Start

### Setup

```bash
cd /Users/juani/github-projects/documentationmcp/documentationmcp

# Option 1: Direct Python (for testing)
python3 -c "
from agents.unified_llm_query_interface import UnifiedLLMQueryInterface
interface = UnifiedLLMQueryInterface('/path/to/your/repo')
result = interface.query('List all modules')
print(result.results)
"

# Option 2: MCP Server (for Claude)
python3 run_unified_llm_server.py /path/to/your/repo
```

### Configure for Claude

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "unified-llm": {
      "command": "python3",
      "args": [
        "/Users/juani/github-projects/documentationmcp/documentationmcp/run_unified_llm_server.py",
        "/path/to/your/repo"
      ]
    }
  }
}
```

Then ask Claude:
> "List all modules in my project"  
> "What are the business rules for order processing?"  
> "How does the payment flow work?"  

---

## Query Types

### 1. Natural Language Queries (Easiest)

Let the interface figure out what you need:

```python
result = interface.query("What are the business rules for orders?")
# Automatically routes to: get_business_rules()

result = interface.query("Show me all modules")
# Automatically routes to: list_modules()

result = interface.query("How does payment processing work?")
# Automatically routes to: get_customer_journey() + trace_data_flow()
```

**Supported keywords:**
- **Structural:** "list", "modules", "functions", "classes", "find"
- **Business:** "rule", "constraint", "validation", "entity", "journey"
- **Semantic:** "risk", "danger", "problem", "issue", "meaning", "purpose"
- **Graph:** "circular", "cycle", "dependency", "trace", "flow"

---

### 2. Structural Queries

Navigate your code:

```python
# List all modules
result = interface.list_modules()
# Returns: { modules: [...], count: 42 }

# Find a specific function
result = interface.find_function("process_payment")
# Returns: { function: "process_payment", statement: "...", found: true }

# Get module dependencies
result = interface.get_dependencies("payment_module")
# Returns: { module: "payment_module", dependencies: [...], count: 5 }
```

**Use when:** You need to navigate code structure, understand dependencies.

---

### 3. Business Logic Queries

Understand business purpose:

```python
# Get all business rules
result = interface.get_business_rules()
# Returns: { rules: [...], count: 23, filter: null }

# Filter by rule type
result = interface.get_business_rules("VALIDATION")
# Returns only validation rules

# Get customer journey
result = interface.get_customer_journey()
# Returns: { journey: [...], steps: 7 }

# Get business entities
result = interface.get_business_entities()
# Returns: { entities: [...], count: 12 }

result = interface.get_business_entities("Customer")
# Returns only Customer entity
```

**Use when:** Understanding what the system does from a business perspective.

---

### 4. Semantic Analysis Queries

Deep code understanding:

```python
# Analyze code semantically
code = """
def process_payment(customer, amount):
    charge = stripe.charge(customer.stripe_id, amount)
    transaction = Transaction(customer_id=customer.id, amount=amount)
    transaction.save()
    return charge
"""

result = interface.analyze_code_semantics(code, "payment.py")
# Returns: { analysis: {...}, filename: "payment.py" }

# Ask questions about code
result = interface.ask_question(
    "What are the risks in this payment handler?",
    code=code
)
# Returns: { answer: "..." }

# Ask without code (about system)
result = interface.ask_question("Why is caching important?")
# Returns: { answer: "..." }
```

**Use when:** You need to understand PURPOSE, RISKS, BUSINESS IMPACT of code.

---

### 5. Graph Queries

Explore relationships:

```python
# Trace data flow
result = interface.trace_data_flow("Customer", "Payment")
# Returns: { paths: [...], path_count: 3 }

# Find circular dependencies
result = interface.find_circular_dependencies()
# Returns: { cycles: [...], cycle_count: 2, severity: "high" }
```

**Use when:** Understanding relationships, flows, and dependencies.

---

## Result Structure

All queries return a `QueryResult` object:

```python
@dataclass
class QueryResult:
    query: str                          # Original query
    query_type: QueryType               # STRUCTURAL, BUSINESS, SEMANTIC, GRAPH, NATURAL
    success: bool                       # Did the query succeed?
    results: List[Dict[str, Any]]       # Actual results
    metadata: Dict[str, Any]            # Additional context
    raw_response: Optional[str]         # LLM raw output (if semantic)
    confidence: float                   # Confidence in results (0-1)
    cache_hit: bool                     # Was this cached?
```

**Example result:**

```python
QueryResult(
    query="List all modules",
    query_type=<QueryType.STRUCTURAL: 'structural'>,
    success=True,
    results=[
        {"modules": ["payment", "customer", "order", "shipping"]}
    ],
    metadata={"count": 4},
    cache_hit=False,
    confidence=1.0
)
```

---

## Smart Caching

Expensive operations are automatically cached:

```python
# First call - computes result
result1 = interface.list_modules()
# metadata: {"cache_hit": false}

# Second call - returns cached result instantly
result2 = interface.list_modules()
# metadata: {"cache_hit": true}
```

**Cached queries:**
- `list_modules()`
- `get_business_rules()`
- `get_customer_journey()`
- `find_circular_dependencies()`

**Not cached:**
- `find_function()` - too variable
- `analyze_code_semantics()` - unique per code
- `ask_question()` - unique per question

---

## Python Usage Examples

### Basic Usage

```python
from agents.unified_llm_query_interface import UnifiedLLMQueryInterface

# Initialize
interface = UnifiedLLMQueryInterface("/path/to/repo")

# Ask a natural language question
result = interface.query("What are the payment processes?")

if result.success:
    print(f"Found {len(result.results)} results")
    for item in result.results:
        print(f"  - {item}")
else:
    print(f"Error: {result.metadata.get('error')}")
```

### Structured Queries

```python
# Get business rules
rules = interface.get_business_rules()
print(f"Found {rules.metadata['count']} rules")

# Get customer journey
journey = interface.get_customer_journey()
print(f"Journey has {journey.metadata['steps']} steps")

# Find specific function
func = interface.find_function("charge_customer")
if func.success:
    print(f"Function found: {func.results}")
```

### Semantic Analysis

```python
with open("payment_handler.py") as f:
    code = f.read()

# Analyze code
analysis = interface.analyze_code_semantics(code, "payment_handler.py")
print(f"Code purpose: {analysis.results}")

# Ask questions
risks = interface.ask_question("What security issues might exist?", code)
print(f"Risks identified: {risks.results}")
```

### Complex Workflows

```python
# Understand payment flow
print("1. Getting business rules...")
rules = interface.get_business_rules("VALIDATION")

print("2. Tracing payment flow...")
flow = interface.trace_data_flow("Customer", "Payment")

print("3. Analyzing payment code...")
with open("payment.py") as f:
    analysis = interface.analyze_code_semantics(f.read(), "payment.py")

print("4. Summary:")
print(f"   - Rules: {rules.metadata['count']}")
print(f"   - Flow paths: {flow.metadata['path_count']}")
print(f"   - Code analysis: {analysis.success}")
```

---

## Claude Integration Examples

Once set up in `claude_desktop_config.json`:

### Example 1: Understanding Business Logic

> **You:** List all the business rules for our ordering system  
> **Claude:** I'll query the business rules for you.  
> *[Uses: get_business_rules()]*  
> **Claude:** Found 23 rules including validation for order amount, inventory checks, and payment authorization...

### Example 2: Code Analysis

> **You:** What are the risks in our payment processing code?  
> **Claude:** I'll analyze the payment handler for you.  
> *[Uses: analyze_code_semantics() + ask_question()]*  
> **Claude:** The payment handler has several risks: no retry logic for failed charges, potential race conditions in inventory updates, and missing timeout handling...

### Example 3: Tracing Data Flow

> **You:** How does customer data flow through the system?  
> **Claude:** Let me trace the customer data flow.  
> *[Uses: trace_data_flow() + get_customer_journey()]*  
> **Claude:** Customer data flows through: Customer → Order → Payment → Shipment, with validation at each step...

### Example 4: Complex Questions

> **You:** Explain how order processing works from business perspective  
> **Claude:** I'll analyze your order processing system.  
> *[Uses: get_customer_journey() + get_business_rules() + get_business_entities()]*  
> **Claude:** Order processing involves 7 steps: Order Creation → Validation → Payment Processing → Inventory Reservation → Fulfillment → Shipment → Delivery...

---

## Advanced: Custom Query Routes

The interface automatically routes queries, but you can also create custom routes:

```python
class MyQueryInterface(UnifiedLLMQueryInterface):
    def analyze_payment_flow(self) -> QueryResult:
        """Custom: Analyze payment flow end-to-end."""
        # Combine multiple methods
        rules = self.get_business_rules("PAYMENT")
        journey = self.get_customer_journey()
        flow = self.trace_data_flow("Customer", "PaymentGateway")
        
        # Aggregate results
        return QueryResult(
            query="Analyze payment flow",
            query_type=QueryType.BUSINESS_LOGIC,
            success=True,
            results=[
                {"rules": rules.results},
                {"journey": journey.results},
                {"flow": flow.results}
            ],
            metadata={"combined_results": 3}
        )

# Use it
interface = MyQueryInterface("/path/to/repo")
result = interface.analyze_payment_flow()
```

---

## Troubleshooting

### Query returns no results

**Problem:** Query executes but returns 0 results  
**Solution:** Check the keywords - add more specific terms:

```python
# ❌ Too vague
result = interface.query("stuff")

# ✅ Better
result = interface.query("What are the business rules?")
```

### Cache returns stale data

**Problem:** Query cached but data changed  
**Solution:** Clear cache and re-run:

```python
interface.cache.clear()
result = interface.list_modules()  # Fresh data
```

### Semantic analysis slow

**Problem:** `analyze_code_semantics()` takes a long time  
**Solution:** This calls LLM API - expected. Use sparingly for large code:

```python
# ❌ Slow - entire file
with open("huge_file.py") as f:
    interface.analyze_code_semantics(f.read())

# ✅ Better - single function
function_code = extract_function("process_payment", file)
interface.analyze_code_semantics(function_code)
```

### MCP Server won't start

**Problem:** `run_unified_llm_server.py` fails  
**Solution:** Ensure dependencies installed:

```bash
pip install mcp anthropic
python3 run_unified_llm_server.py /path/to/repo
```

---

## Performance Tips

1. **Use specific queries** when possible (faster than natural language)
2. **Leverage caching** - results are cached automatically
3. **Batch similar queries** - query once for all modules, then filter in results
4. **Limit semantic analysis** - use for critical code only, due to LLM API calls
5. **Initialize once** - `UnifiedLLMQueryInterface` scans repo on init, reuse instance

---

## Next Steps

1. **Try it:** `python3 agents/unified_llm_query_interface.py /path/to/repo`
2. **Set up MCP:** Add to `claude_desktop_config.json`
3. **Ask queries:** Start with natural language, then explore specific methods
4. **Integrate:** Use in your own tools/workflows

---

## File Reference

- **_Main Interface:_** [agents/unified_llm_query_interface.py](agents/unified_llm_query_interface.py)
- **_MCP Server:_** [run_unified_llm_server.py](run_unified_llm_server.py)
- **_Used by:_** Claude, Gemini, any MCP-compatible client

---

## API Reference Quick Look

| Query | Method | Returns |
|-------|--------|---------|
| Natural language | `query(str)` | Routed to best method(s) |
| List modules | `list_modules()` | All modules in repo |
| Find function | `find_function(name)` | Function location |
| Get dependencies | `get_dependencies(module)` | Module dependencies |
| Business rules | `get_business_rules(type?)` | Rules + constraints |
| Customer journey | `get_customer_journey()` | Complete user flow |
| Entities | `get_business_entities(type?)` | Business entities |
| Analyze code | `analyze_code_semantics(code)` | Purpose, risks, impact |
| Ask question | `ask_question(q, code?)` | LLM-powered answer |
| Trace flow | `trace_data_flow(src, tgt)` | Data paths |
| Find cycles | `find_circular_dependencies()` | Circular dependencies |

---

All methods return `QueryResult` with: `query`, `query_type`, `success`, `results`, `metadata`, `cache_hit`.
