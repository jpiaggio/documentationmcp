# Quick Reference: Business Cartographer Commands

## Essential Commands

### 1. Analyze Your Repository
```bash
python3 agents/cartographer_agent.py /path/to/your/repo
```
**Output**: 1000s of Cypher statements (business insights)
**Time**: 1-5 minutes depending on repo size

### 2. Generate Business Context
```bash
python3 agents/business_journey_analyzer.py /path/to/your/repo
```
**Output**: Markdown file with business context summary
**Use**: Documentation, AI context, stakeholder communication

### 3. Start MCP Server
```bash
python3 agents/mcp_business_server.py /path/to/your/repo
```
**Output**: JSON with all business insights + tool definitions
**Use**: Integration with Claude, AI agents, other tools

### 4. Load into Neo4j
```bash
python3 agents/cartographer_agent.py /path/to/your/repo | cypher-shell -u neo4j -p password
```
**Output**: Neo4j database populated with business graph
**Use**: Complex queries, relationship analysis, visualization

## Python API Usage

### Quick Integration
```python
from agents.mcp_business_server import BusinessRulesMCPServer

# Initialize server
server = BusinessRulesMCPServer('/path/to/repo')

# Get customer journey
journey = server.analyze_customer_journey()
print(journey['journey_path'])

# Get business entities
entities = server.get_business_entities()
print(entities['entities_by_type'])

# Get integrations
integrations = server.get_integration_points()
print(integrations['integrations'])

# Get business rules
rules = server.get_business_rules()
print(rules['by_type'])

# Get complete overview
overview = server.get_platform_overview()
print(overview['business_context'])
```

### With Claude API
```python
from anthropic import Anthropic
from agents.mcp_business_server import BusinessRulesMCPServer

server = BusinessRulesMCPServer('/path/to/repo')
client = Anthropic()

# Get MCP tools
tools = server.get_tools()

# Use with Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    tools=tools,
    messages=[{
        "role": "user",
        "content": "What is the customer journey?"
    }]
)

# Automatically call tools based on Claude's response
for content in response.content:
    if hasattr(content, 'name'):
        result = server.handle_tool_call(content.name, content.input)
        print(result)
```

## Common Workflows

### Work Flow 1: Understand a Platform
```bash
# Step 1: Extract insights
python3 agents/cartographer_agent.py ~/my-platform 2>/dev/null > insights.cypher

# Step 2: Analyze
python3 agents/business_journey_analyzer.py ~/my-platform > platform.md

# Step 3: Read overview
cat platform.md

# Step 4: Use with AI
python3 agents/mcp_business_server.py ~/my-platform
```

### Work Flow 2: Generate Documentation
```bash
# Extract business context
python3 agents/business_journey_analyzer.py ~/my-platform > docs/business-architecture.md

# Use context for docs
cat docs/business-architecture.md
```

### Work Flow 3: Graph Analysis
```bash
# Generate and load Cypher
python3 agents/cartographer_agent.py ~/my-platform | cypher-shell -u neo4j -p pwd

# Query relationships
cypher> MATCH (j:JourneyStep) RETURN j.name ORDER BY j.sequence
cypher> MATCH (r:BusinessRule) WHERE r.type='VALIDATION' RETURN COUNT(*)
cypher> MATCH (i:ExternalSystem) RETURN DISTINCT i.name
```

### Work Flow 4: AI-Driven Analysis
```bash
# Start server
python3 agents/mcp_business_server.py ~/my-platform &

# Use in application
from agents.mcp_business_server import BusinessRulesMCPServer
server = BusinessRulesMCPServer('~/my-platform')

# Query for specific business questions
rules = server.get_business_rules()
journey = server.analyze_customer_journey()
integrations = server.get_integration_points()
```

## File Structure

```
documentationmcp/
├── agents/
│   ├── cartographer_agent.py              [MAIN - Entry point]
│   ├── business_rules_extractor.py        [NEW - Extraction]
│   ├── business_journey_analyzer.py       [NEW - Analysis]
│   └── mcp_business_server.py             [NEW - MCP Tools]
├── BUSINESS_JOURNEY_README.md             [Guide]
├── AI_BUSINESS_PLATFORM_GUIDE.md          [Deep dive]
├── ECOMMERCE_EXAMPLE.md                   [Real example]
├── SYSTEM_SUMMARY.md                      [Overview]
├── CHANGELOG.md                           [What's new]
├── ARCHITECTURE_DIAGRAMS.md               [Visual guide]
├── BUSINESS_CARTOGRAPHER_INDEX.md         [Navigation]
└── QUICK_REFERENCE.md                     [This file]
```

## Tool Reference

### MCP Tool: analyze_customer_journey()
Returns complete customer journey path
```json
{
  "journey_path": "AUTHENTICATE → BROWSE → CHECKOUT → SHIP → DELIVER",
  "steps": ["AUTHENTICATE", "BROWSE", "CHECKOUT", "SHIP", "DELIVER"],
  "total_steps": 5
}
```

### MCP Tool: get_business_entities()
Returns all business entities
```json
{
  "entities_by_type": {
    "customer": ["Customer", "Profile"],
    "order": ["Order", "CartItem"],
    "product": ["Product"]
  },
  "total_entity_types": 3,
  "total_entities": 7
}
```

### MCP Tool: get_integration_points()
Returns external system integrations
```json
{
  "integrations": ["stripe", "email", "kafka"],
  "integration_count": 3,
  "by_type": {
    "payments": ["stripe"],
    "communications": ["email"],
    "messaging": ["kafka"]
  }
}
```

### MCP Tool: get_business_rules()
Returns business constraints and validations
```json
{
  "total_rules": 246,
  "by_type": {
    "VALIDATION": 200,
    "CONSTRAINT": 35,
    "THRESHOLD": 11
  }
}
```

### MCP Tool: explain_step(step)
Explains what happens at a journey step
```json
{
  "step": "CHECKOUT",
  "description": "Customer reviews order and enters shipping info",
  "sequence": 3,
  "previous_step": "SELECT_PRODUCT",
  "next_step": "NOTIFY"
}
```

### MCP Tool: trace_data_flow(start_step, end_step?)
Shows data flow through journey steps
```json
{
  "flow": "CHECKOUT → NOTIFY → UPDATE_STATUS → SHIP",
  "steps": ["CHECKOUT", "NOTIFY", "UPDATE_STATUS", "SHIP"],
  "step_count": 4
}
```

## Flag Options

### cartographer_agent.py
```bash
# Business rules mode (default)
python3 agents/cartographer_agent.py /path/to/repo

# Technical analysis mode (old behavior)
python3 agents/cartographer_agent.py /path/to/repo --technical
```

## Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the right directory
cd /path/to/documentationmcp/documentationmcp

# Or provide full paths
python3 /full/path/agents/cartographer_agent.py /path/to/repo
```

### Tree-sitter Java not available
```bash
# Install Java support (optional)
pip3 install tree-sitter-java

# Or just use Python analysis (default)
python3 agents/cartographer_agent.py /python/repo
```

### Neo4j connection failed
```bash
# Check Neo4j is running
neo4j status

# Or start it
neo4j start

# Then load data
python3 agents/cartographer_agent.py /repo | cypher-shell
```

## Performance Tips

1. **For large repos**: Use `max_workers` parameter
   ```python
   cartographer_agent(repo, max_workers=16)
   ```

2. **For Neo4j loading**: Batch imports
   ```bash
   python3 agents/cartographer_agent.py /repo > big_file.cypher
   cypher-shell < big_file.cypher
   ```

3. **For analysis**: Cache results
   ```bash
   python3 agents/cartographer_agent.py /repo > cache.cypher
   python3 agents/business_journey_analyzer.py /repo > cache.md
   ```

## Integration Examples

### With TypeScript/Node.js
```javascript
const { exec } = require('child_process');

exec('python3 agents/mcp_business_server.py /repo', (error, stdout) => {
  const insights = JSON.parse(stdout);
  console.log(insights.journey);
});
```

### With REST API
```python
from flask import Flask
from agents.mcp_business_server import BusinessRulesMCPServer

app = Flask(__name__)
server = BusinessRulesMCPServer('/path/to/repo')

@app.route('/api/journey')
def journey():
    return server.analyze_customer_journey()

@app.route('/api/rules')
def rules():
    return server.get_business_rules()

@app.route('/api/integrations')
def integrations():
    return server.get_integration_points()
```

### With Documentation
```python
# Extract business context as markdown
from agents.business_journey_analyzer import BusinessJourneyAnalyzer

with open('insights.cypher') as f:
    statements = f.readlines()

analyzer = BusinessJourneyAnalyzer(statements)
context = analyzer.get_business_context()

with open('docs/ARCHITECTURE.md', 'w') as f:
    f.write(context)
```

## Next Steps

1. **Run on your repo**: `python3 agents/cartographer_agent.py ~/my-project`
2. **Read the overview**: `cat SYSTEM_SUMMARY.md`
3. **Check examples**: `cat ECOMMERCE_EXAMPLE.md`
4. **Integrate with AI**: Use `mcp_business_server.py` with Claude
5. **Load to Neo4j**: Build graph visualization

---

## Enterprise Enhancements (v2.0)

### Three Technical Must-Haves

**1. Incremental Indexing** (80-90% cost savings)
```python
from agents.incremental_indexer import IncrementalIndexer

indexer = IncrementalIndexer('/repo')
files, stats = indexer.get_files_to_process(['.py'])
# Only analyzes changed files on subsequent runs!
```

**2. Context Pruning** (70-80% token reduction)
```python
from agents.context_pruner import ContextPruner

pruner = ContextPruner('python')
elements = pruner.prune_file('module.py', code)
# Returns only signatures + docstrings, not full bodies
```

**3. Enhanced MCP Server** (Multi-module support)
```python
from agents.enhanced_mcp_server import create_server

server = create_server()
result = server.analyze_multiple_modules([
    {'path': '/backend', 'name': 'API'},
    {'path': '/worker', 'name': 'Jobs'}
], parallel_workers=4)
```

### Quick Cost Calculator

```
Without Enhancements:
  500 files × 50 API calls/file = 25,000 API calls/day

With Enhancements:
  Day 1: 25,000 API calls (full index)
  Day 2-30: 2,500 API calls (10% change only)
  
Monthly Savings: 270,000 API calls = $27 saved! 💰
Annual Savings: $324+ (grows with repo size)
```

### 7 New MCP Tools

| Tool | Purpose |
|------|---------|
| `analyze_module` | Single module with incremental indexing |
| `analyze_multiple_modules` | Parallel multi-module analysis ⚡ |
| `get_module_context` | Pruned context (signatures only) |
| `query_business_rules` | Extract business rules |
| `get_customer_journey_map` | Journey + entities + integrations |
| `get_indexing_status` | Check cache & savings |
| `fetch_full_code` | On-demand full code |

### Documentation

- **ENTERPRISE_ENHANCEMENTS_GUIDE.md** - Full technical guide
- **MCP_TOOL_SCHEMA.json** - Complete tool definitions
- **IMPLEMENTATION_SUMMARY.md** - What's new
- **example_enterprise_usage.py** - Practical examples

---

**For detailed information**: See BUSINESS_CARTOGRAPHER_INDEX.md
