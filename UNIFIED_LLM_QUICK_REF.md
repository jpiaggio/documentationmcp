# Unified LLM Query Interface - Quick Reference

**TL;DR:** Single API combining all query methods. Ask naturally, get results.

---

## One-Line Examples

```python
from agents.unified_llm_query_interface import UnifiedLLMQueryInterface

interface = UnifiedLLMQueryInterface("/path/to/repo")

# Most natural way:
result = interface.query("What are the business rules for orders?")

# Specific queries:
result = interface.list_modules()                    # All modules
result = interface.find_function("process_payment")  # Find function
result = interface.get_business_rules()              # All rules
result = interface.get_customer_journey()            # User flow
result = interface.analyze_code_semantics(code)      # Code meaning
result = interface.ask_question("What are risks?")   # LLM questions
result = interface.trace_data_flow("A", "B")         # Entity paths
result = interface.find_circular_dependencies()      # Circular refs
```

---

## Installation & Setup

### 1. Direct Usage (Python)
```bash
python3 -c "from agents.unified_llm_query_interface import *; ..."
```

### 2. MCP Server (for Claude)
```bash
python3 run_unified_llm_server.py /path/to/repo
```

**Add to `~/.config/Claude/claude_desktop_config.json`:**
```json
{
  "mcpServers": {
    "unified-llm": {
      "command": "python3",
      "args": [
        "/path/to/documentationmcp/run_unified_llm_server.py",
        "/path/to/your/repo"
      ]
    }
  }
}
```

### 3. Interactive Demo
```bash
python3 unified_llm_quick_start.py /path/to/repo
```

---

## Method Reference

### Natural Language (Router)
```python
result = interface.query("your question here")
# Auto-routes based on keywords
```

### Structural (Code Navigation)
| Method | Purpose | Example |
|--------|---------|---------|
| `list_modules()` | List all modules | `list_modules()` |
| `find_function(name)` | Find a function | `find_function("pay")` |
| `get_dependencies(mod)` | Module dependencies | `get_dependencies("payment")` |

### Business Logic
| Method | Purpose | Example |
|--------|---------|---------|
| `get_business_rules(type?)` | All rules + filter | `get_business_rules("VALIDATION")` |
| `get_customer_journey()` | User flow steps | `get_customer_journey()` |
| `get_business_entities(type?)` | Entities + filter | `get_business_entities("Order")` |

### Semantic (LLM-Powered)
| Method | Purpose | Example |
|--------|---------|---------|
| `analyze_code_semantics(code)` | Code purpose/risks | `analyze_code_semantics(func_code)` |
| `ask_question(q, code?)` | Ask about code/system | `ask_question("What risks?", code)` |

### Graph (Relationships)
| Method | Purpose | Example |
|--------|---------|---------|
| `trace_data_flow(src, tgt)` | Entity flow paths | `trace_data_flow("Order","Payment")` |
| `find_circular_dependencies()` | Circular refs | `find_circular_dependencies()` |

---

## Result Format

All methods return `QueryResult`:

```python
result.query           # Original query string
result.query_type      # STRUCTURAL|BUSINESS|SEMANTIC|GRAPH|NATURAL
result.success         # Boolean
result.results         # List[Dict] - actual data
result.metadata        # Dict - context info
result.cache_hit       # Boolean - was cached?
result.confidence      # Float 0-1
result.to_dict()       # Convert to dict
```

---

## Natural Language Keywords

**Auto-routes to right method based on keywords:**

```
"list", "modules"           → list_modules()
"find", "function"          → find_function()
"business rule", "constraint" → get_business_rules()
"journey", "flow", "process" → get_customer_journey()
"entity", "object"          → get_business_entities()
"risk", "danger", "issue"   → ask_question()
"circular", "cycle"         → find_circular_dependencies()
"trace", "flow"             → trace_data_flow()
```

---

## Claude Integration

Once in `claude_desktop_config.json`:

```
You: "List all business rules"
Claude: I'll query that for you.
→ Uses: get_business_rules()
Claude: Found 23 rules including...

You: "What risks are in the payment handler?"
Claude: I'll analyze that code.
→ Uses: analyze_code_semantics() + ask_question()
Claude: The payment system has several risks...

You: "How does order processing work?"
Claude: Let me get the complete flow.
→ Uses: get_customer_journey() + trace_data_flow()
Claude: Order processing has 7 steps...
```

---

## Caching

Automatically caches expensive queries:

```python
# First call - computed
result1 = interface.list_modules()
# result1.cache_hit == False

# Second call - cached instantly
result2 = interface.list_modules()
# result2.cache_hit == True
```

**Cached:** `list_modules()`, `get_business_rules()`, `get_customer_journey()`, `find_circular_dependencies()`

**Not cached:** `find_function()`, `analyze_code_semantics()`, `ask_question()`

---

## Common Workflows

### Understand a Feature
```python
# 1. Get business rules
rules = interface.get_business_rules("FEATURE_NAME")

# 2. Find related entities
entities = interface.get_business_entities()

# 3. Trace data flow
flow = interface.trace_data_flow("Entity1", "Entity2")

# 4. Analyze code
analysis = interface.analyze_code_semantics(code)
```

### Find Issues
```python
# 1. Circular dependencies
cycles = interface.find_circular_dependencies()

# 2. Analyze risky modules
for module in modules:
    analysis = interface.ask_question(
        f"What risks in {module}?"
    )

# 3. Validate rules
rules = interface.get_business_rules()
```

### Documentation
```python
# 1. Get journey
journey = interface.get_customer_journey()

# 2. Get entities
entities = interface.get_business_entities()

# 3. Get rules
rules = interface.get_business_rules()

# 4. Generate docs from results
```

---

## Files

| File | Purpose |
|------|---------|
| `agents/unified_llm_query_interface.py` | Main interface class |
| `run_unified_llm_server.py` | MCP server wrapper |
| `unified_llm_quick_start.py` | Interactive examples |
| `UNIFIED_LLM_QUERY_GUIDE.md` | Full documentation |

---

## Typical Usage

```python
from agents.unified_llm_query_interface import UnifiedLLMQueryInterface

# Initialize (scans repo once)
interface = UnifiedLLMQueryInterface("/path/to/repo")

# Use naturally
result = interface.query("Show me payment processing")

# Or be specific
if result.success:
    for item in result.results:
        print(item)
```

---

## Error Handling

```python
result = interface.query("something")

if not result.success:
    error = result.metadata['error']
    print(f"Error: {error}")
else:
    # Use results
    for item in result.results:
        process(item)
```

---

## Performance Tips

1. **Natural language** = slowest (must route)
2. **Specific methods** = fastest
3. **Use caching** = get same results instantly
4. **Batch queries** = multiple in one method call
5. **Avoid LLM analysis** = slowest (API calls)

```python
# ❌ Slow - 100 semantic analyses
for code in codes:
    interface.analyze_code_semantics(code)

# ✅ Better - 1 semantic analysis
analysis = interface.analyze_code_semantics(important_code)
```

---

**See `UNIFIED_LLM_QUERY_GUIDE.md` for full documentation**
