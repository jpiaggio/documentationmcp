# 🧪 Quick Guide: Testing Against Real Source Code

## Overview

The application includes multiple ways to test and analyze real repositories. Choose the approach that fits your needs.

---

## 🚀 Quick Test Commands

### **Option 1: Simple Analysis (Fastest)**
```bash
python3 agents/cartographer_agent.py /path/to/repo
```
**Best for:** Quick overview of a repository structure
**Time:** ~30 seconds to 5 minutes

### **Option 2: Quick Start (Recommended for New Users)**
```bash
python3 quick_start.py /path/to/repo
```
**Best for:** First-time users, sets up configuration automatically
**Time:** ~5 minutes

### **Option 3: Comprehensive Real Test Suite (My Tests)**
```bash
# Test 1: Analyze repository structure
python3 run_real_tests.py 1

# Test 2: Test custom repository
python3 run_real_tests.py 2

# Test 3: Show incremental indexing (caching benefits)
python3 run_real_tests.py 3

# Test 4: Extract business rules
python3 run_real_tests.py 4

# Run all tests
python3 run_real_tests.py all
```

### **Option 4: Enterprise Workflow (Full Power)**
```bash
python3 agents/integrated_workflow.py .cartographer_config/MyProject.json
```
**Best for:** Production use, multiple repositories, metrics tracking
**Time:** Varies by repo size

---

## 📊 What Each Test Shows

### Test 1: Repository Analysis
```
✅ Analysis Complete!
   Total statements: 5,665
   Business modules: 465
   Relationships: 5200
```
Shows: AST parsing results, module count, relationship mapping

### Test 2: Custom Repository
Tests any repository path you provide. Automatically detects:
- Python vs Java files
- File type distribution
- Code structure

### Test 3: Incremental Indexing
```
📊 Results:
   Mode: no_changes
   Files changed: 0
   Cost savings: 100% (no re-analysis needed)
```
Shows: Cache effectiveness, API cost reduction, efficiency gains

### Test 4: Business Rules
```
📋 Rule Breakdown:
   Validation rules: 3
   State/Flow rules: 2
   Permission rules: 1
```
Shows: Extracted business logic, constraints, state machines

---

## 🎯 Real Repository Examples

### Test Against DocumentationMCP (Your Current Project)
```bash
python3 agents/cartographer_agent.py /Users/juani/github-projects/documentationmcp/documentationmcp

# Or use the test script
python3 run_real_tests.py 1
```

### Test Against Mattermost (Large Real Project)
```bash
python3 agents/cartographer_agent.py /Users/juani/github-projects/mattermost/mattermost

# For Java files
python3 agents/cartographer_agent.py /Users/juani/github-projects/mattermost/mattermost --file-ext=.java
```

### Test Against Spring Framework (Java-based)
```bash
python3 agents/cartographer_agent.py /Users/juani/github-projects/spring-framework/spring-framework --file-ext=.java
```

---

## 💡 Test-Specific Examples

### **Business Rule Extraction**
```bash
# Test manually
python3 agents/smart_rule_inference_demo.py

# Or use test script
python3 run_real_tests.py 4
```

Shows extracted rules like:
- Validation constraints
- Order/state dependencies
- Permission hierarchies
- Error handling rules

### **Entity Graph Analysis**
```bash
# E-commerce example
python3 agents/entity_graph_demo.py
```

Shows:
- Entity relationships
- Cardinality (1:1, 1:N, M:N)
- Temporal dependencies
- Circular dependency detection

### **ML Pattern Recognition**
```bash
python3 agents/ml_quick_start.py
```

Shows:
- Code pattern clustering
- Similarity analysis
- Anomaly detection

---

## 📈 Expected Results

| Test | Files Analyzed | Time | Output |
|------|----------------|------|--------|
| DocumentationMCP | 50+ | 2-3s | 5,665 Cypher statements |
| Mattermost | 200+ | 10-30s | 15,000+ statements |
| Spring Framework | 500+ | 30-60s | 50,000+ statements |

---

## 🔍 Understanding the Output

### Cypher Statements
```cypher
MERGE (m:BusinessModule {name: 'run_cartographer_mcp'})
MERGE (j:JourneyStep {name: 'BROWSE'})
MERGE (m)-[:CONTAINS_STEP]->(j)
```
These represent relationships between code entities, ready for Neo4j imports.

### Cache Statistics
```
Mode: no_changes
Files changed: 0
Cost savings: 100%
```
Shows how much you save by not re-analyzing unchanged files.

### Rules Extracted
```
Validation rules: 3
State/Flow rules: 2
Permission rules: 1
```
Business logic discovered automatically from code.

---

## 🛠️ Advanced Testing

### With Multiple Workers (Parallel Processing)
```bash
python3 agents/cartographer_agent.py /path/to/repo --max-workers=8
```

### Force Reindex (Ignore Cache)
```bash
python3 agents/cartographer_agent.py /path/to/repo --force-reindex
```

### Analyze Specific File Extension
```bash
python3 agents/cartographer_agent.py /path/to/repo --file-ext=.java
python3 agents/cartographer_agent.py /path/to/repo --file-ext=.go
python3 agents/cartographer_agent.py /path/to/repo --file-ext=.rs
```

---

## 📝 Next Steps

1. **Pick a Test:** Choose from the options above
2. **Run It:** Execute the command
3. **Check Output:** Review the results
4. **Analyze:** Look for patterns, rules, and relationships
5. **Scale Up:** Run on larger repositories

---

## 🚨 Troubleshooting

**`ModuleNotFoundError: tree_sitter_java`**
- Java parsing optional - Python files will still work
- Install with: `pip install tree-sitter-java`

**`No changes detected`**
- This is good! Cache is working
- Force reindex with flag if you want fresh analysis

**Slow on large repos**
- Use `--max-workers=8` for parallel processing
- Use incremental indexing (enabled by default)
- Run Test 3 to see cache savings

---

## 📖 Where to Go Next

- [Enterprise Guide](ENTERPRISE_README.md) - Full production setup
- [Smart Rules](SMART_RULE_INFERENCE.md) - Business rule details  
- [Entity Graph](SMART_ENTITY_GRAPH_GUIDE.md) - Relationship modeling
- [Architecture](ARCHITECTURE_DIAGRAMS.md) - System design

---

**Happy Testing! 🎉**
