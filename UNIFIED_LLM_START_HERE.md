# 🎯 Unified LLM Query Interface - START HERE

> **Single API to query code using LLMs**  
> Combines structural, business logic, semantic, and graph queries into one unified interface.

---

## Quick Start (5 minutes)

### Option 1: Try the Demo
```bash
python3 unified_llm_quick_start.py /path/to/your/repo
```
Interactive examples of all query types.

### Option 2: Use with Claude
```bash
python3 run_unified_llm_server.py /path/to/your/repo
```
Then add to `claude_desktop_config.json` and ask Claude directly.

### Option 3: Use in Python
```python
from agents.unified_llm_query_interface import UnifiedLLMQueryInterface

interface = UnifiedLLMQueryInterface("/path/to/repo")
result = interface.query("Show me payment processes")
print(result.results)
```

---

## What It Does

```
                    Your Code Repo
                         ↓
         UnifiedLLMQueryInterface
         ↙         ↓         ↘
   Structural   Business    Semantic
   (code nav)   (rules)     (LLM)
         ↖         ↓         ↙
            Smart Routing
                 ↓
        Consistent Results
                 ↓
         Claude / GPT / LLMs
```

### Five Query Methods

1. **Natural Language** - Ask anything, gets routed automatically
2. **Structural** - Navigate code: modules, functions, dependencies  
3. **Business Logic** - Understand purpose: rules, journeys, entities
4. **Semantic** - Deep analysis: what code REALLY does, risks, impact
5. **Graph** - Explore relationships: data flows, circular dependencies

---

## One-Line Examples

```python
interface.query("What are the business rules?")        # Auto-route
interface.list_modules()                               # All modules
interface.find_function("process_payment")             # Find function
interface.get_business_rules()                         # All rules
interface.get_customer_journey()                       # User flow
interface.analyze_code_semantics(code)                 # Code meaning
interface.ask_question("What are risks?", code)        # Ask LLM
interface.trace_data_flow("Customer", "Payment")       # Data flow
interface.find_circular_dependencies()                 # Circular refs
```

---

## Documentation Map

### 📖 Full Guide
**[UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md)** (30 min read)
- Complete reference of all methods
- Usage examples for each query type
- Integration with Claude
- Advanced customization
- Troubleshooting

### ⚡ Quick Reference  
**[UNIFIED_LLM_QUICK_REF.md](UNIFIED_LLM_QUICK_REF.md)** (5 min read)
- One-line method examples
- Installation steps
- Common workflows
- Performance tips

### 📋 Delivery Summary
**[UNIFIED_LLM_DELIVERY.md](UNIFIED_LLM_DELIVERY.md)** (10 min read)
- What was created
- Architecture overview
- Comparison before/after
- Next steps

### 🎮 Interactive Demo
**[unified_llm_quick_start.py](unified_llm_quick_start.py)** (run it!)
- 8 interactive examples
- Demonstrates all query types
- Guide through features

---

## Core Files

| File | Lines | Purpose |
|------|-------|---------|
| `agents/unified_llm_query_interface.py` | 600+ | Main interface class |
| `run_unified_llm_server.py` | 150+ | MCP server wrapper |
| `unified_llm_quick_start.py` | 400+ | Interactive examples |
| `UNIFIED_LLM_QUERY_GUIDE.md` | 600+ | Full documentation |
| `UNIFIED_LLM_QUICK_REF.md` | 200+ | Quick reference |

---

## Results Format

All queries return the same structure:

```python
result = interface.query("something")

result.query           # str: Your original query
result.query_type      # QueryType: STRUCTURAL|BUSINESS|SEMANTIC|GRAPH|NATURAL
result.success         # bool: Did it work?
result.results         # List[Dict]: Actual results
result.metadata        # Dict: Extra info (counts, cache_hit, error)
result.cache_hit       # bool: Was cached?
result.confidence      # float: 0-1 confidence score
result.to_dict()       # Serialize to JSON
```

---

## Query Methods Overview

### Natural Language Query (Auto-Routing)
```python
result = interface.query("List all modules")
# Keywords auto-route: "list" → list_modules()
```

### Structural Queries
```python
interface.list_modules()           # All modules in repo
interface.find_function("name")    # Find a function
interface.get_dependencies("mod")  # Get module dependencies
```

### Business Logic Queries  
```python
interface.get_business_rules()     # All rules + constraints
interface.get_customer_journey()   # Complete user flow
interface.get_business_entities()  # Entities like Customer, Order
```

### Semantic Queries (Uses LLM)
```python
interface.analyze_code_semantics(code)        # Purpose + risks
interface.ask_question("What are risks?")     # Ask LLM directly
```

### Graph Queries
```python
interface.trace_data_flow("A", "B")           # Data paths between entities
interface.find_circular_dependencies()        # Circular references
```

---

## Setup

### For Claude/MCP Clients

1. **Start the server:**
   ```bash
   python3 run_unified_llm_server.py /path/to/your/repo
   ```

2. **Configure Claude** (`~/.config/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "unified-llm": {
         "command": "python3",
         "args": [
           "/full/path/to/run_unified_llm_server.py",
           "/path/to/your/repo"
         ]
       }
     }
   }
   ```

3. **Ask Claude:**
   > "List all modules in my project"
   > "What are the business rules for orders?"

### For Direct Python Usage

```python
from agents.unified_llm_query_interface import UnifiedLLMQueryInterface

# Initialize once
interface = UnifiedLLMQueryInterface("/path/to/repo")

# Query
result = interface.query("What are business rules?")
if result.success:
    for item in result.results:
        print(item)
```

### For Interactive Exploration

```bash
python3 unified_llm_quick_start.py /path/to/repo
```

---

## Key Features

### ✅ Smart Routing
Natural language queries automatically route to the best method

### ✅ Consistent Results  
All queries return the same `QueryResult` format

### ✅ Smart Caching
Expensive queries cached automatically for instant results

### ✅ MCP Compatible
Works with Claude, Gemini, and other MCP clients

### ✅ Multiple LLM Providers
Supports Claude, Gemini, and other providers

### ✅ Zero New Dependencies
Uses existing cartographer, business analyzer, and LLM components

---

## Common Workflows

### Understand a Feature
```python
rules = interface.get_business_rules("FEATURE_NAME")
entities = interface.get_business_entities()
flow = interface.trace_data_flow("Entity1", "Entity2")
```

### Identify Risks
```python
cycles = interface.find_circular_dependencies()
code_analysis = interface.analyze_code_semantics(code)
risks = interface.ask_question("What are the risks?", code)
```

### Document the System
```python
journey = interface.get_customer_journey()
entities = interface.get_business_entities()
rules = interface.get_business_rules()
```

---

## Examples with Claude

Once configured, you can ask:

**Structural Questions:**
- "List all modules in my project"
- "Find the process_payment function"
- "What does the order module depend on?"

**Business Questions:**
- "What are the business rules for orders?"
- "Show me the customer journey"
- "What entities exist in the system?"

**Semantic Questions:**
- "What does this payment code really do?"
- "What are the risks in our authentication?"
- "Explain how order processing works"

**Relationship Questions:**
- "How does customer data flow to payments?"
- "Find circular dependencies"
- "Trace the payment flow"

---

## What You Get

| Aspect | What It Enables |
|--------|-----------------|
| **Code Navigation** | Find modules, functions, classes instantly |
| **Business Understanding** | Understand rules, journeys, entities |
| **Code Insights** | Semantic analysis of what code REALLY does |
| **Risk Analysis** | Identify risks, issues, circular dependencies |
| **Documentation** | Auto-generate docs from analysis |
| **LLM Integration** | Use Claude, Gemini, or other models |

---

## Next Steps

### 1. **Right Now** (5 min)
```bash
python3 unified_llm_quick_start.py /path/to/your/repo
```

### 2. **This Week** (30 min)
- Read [UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md)
- Set up MCP server for Claude
- Try asking Claude questions

### 3. **This Sprint** (ongoing)
- Integrate into your workflows
- Create custom query routes
- Use for documentation generation

---

## Architecture

```
┌────────────────────────────┐
│   Your Code Repository     │
└────────────────────────────┘
           ↓
┌────────────────────────────┐
│ UnifiedLLMQueryInterface   │
│  • 5 query methods         │
│  • Natural language router │
│  • Smart caching           │
│  • Result aggregation      │
└──────────┬──────────┬──────┘
           ↓          ↓
    ┌───────────┐ ┌─────────┐
    │ MCP Server│ │ Python  │
    └─────┬─────┘ └────┬────┘
          ↓            ↓
    ┌─────────────────────────┐
    │ Claude/Gemini/LLMs      │
    └─────────────────────────┘
```

---

## File Navigation

**Want to understand the code?**
→ Read: [UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md)

**Want quick method reference?**
→ Read: [UNIFIED_LLM_QUICK_REF.md](UNIFIED_LLM_QUICK_REF.md)

**Want to see delivery details?**
→ Read: [UNIFIED_LLM_DELIVERY.md](UNIFIED_LLM_DELIVERY.md)

**Want to try it?**
→ Run: `python3 unified_llm_quick_start.py /path/to/repo`

**Want to use it with Claude?**
→ Run: `python3 run_unified_llm_server.py /path/to/repo`

**Want to use in Python?**
→ Import: `from agents.unified_llm_query_interface import UnifiedLLMQueryInterface`

---

## Questions?

**How do I...** | **See:**
---|---
Use the interface? | [UNIFIED_LLM_QUICK_REF.md](UNIFIED_LLM_QUICK_REF.md)
Set up for Claude? | [UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md) - "Claude Integration"
Understand results? | [UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md) - "Result Structure"
Create custom queries? | [UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md) - "Advanced"
Troubleshoot issues? | [UNIFIED_LLM_QUERY_GUIDE.md](UNIFIED_LLM_QUERY_GUIDE.md) - "Troubleshooting"

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Date:** March 2026  

Ready to query your code? → `python3 unified_llm_quick_start.py /path/to/repo`
