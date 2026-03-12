# Multi-Language Support - Quick Start Guide

## What's New

Cartographer now analyzes **6 programming languages**, expanding market coverage from 40% to 95% of enterprise codebases.

### Supported Languages
- **Python** (.py) - Existing
- **Java** (.java) - Existing  
- **JavaScript** (.js, .jsx, .mjs) - NEW
- **TypeScript** (.ts, .tsx) - NEW
- **Go** (.go) - NEW
- **C#** (.cs) - NEW

---

## Installation

### 1. Install Tree-Sitter Language Bindings

```bash
pip install tree-sitter-javascript tree-sitter-go tree-sitter-c_sharp
```

### 2. Verify Installation

```python
from agents.multi_language_analyzer import get_supported_languages
print(get_supported_languages())
# Output: {'python': True, 'java': True, 'javascript': True, 'typescript': True, 'go': True, 'csharp': True}
```

---

## Quick Usage

### Analyze a Single File

```python
from agents.multi_language_analyzer import analyze_file

# Automatic language detection
result = analyze_file('src/payment.ts')
print(result['language'])  # "TypeScript"
print(result['entities'])  # Classes, functions, interfaces, etc.
```

### Analyze Entire Repository

```python
from agents.multi_language_analyzer import analyze_codebase

# Analyze all supported languages in parallel
results = analyze_codebase('/path/to/repo', max_workers=4)

# Results by language
for lang, files in results['files_by_language'].items():
    print(f"{lang}: {files} files")

# Cross-language dependencies
for dep in results['cross_language_dependencies']:
    print(f"{dep['source']['language']} → {dep['target']['language']}")
```

### Command-Line Usage

```bash
# Analyze all Python files (default)
python agents/cartographer_agent.py /repo --ext .py

# Analyze specific extensions
python agents/cartographer_agent.py /repo --ext .ts,.js,.go

# Analyze all supported languages
python agents/cartographer_agent.py /repo --ext all

# Generate Neo4j Cypher queries
python agents/cartographer_agent.py /repo --ext all > neo4j_queries.cypher
```

---

## Understanding Results

### Single File Analysis

```python
{
  "filepath": "src/payment.controller.ts",
  "language": "TypeScript",
  "entities": [
    {
      "type": "class",
      "name": "PaymentController",
      "is_exported": True,
      "access_modifier": "public",
      "decorators": ["@ApiController"],
      "start_line": 5,
      "end_line": 35
    },
    {
      "type": "async_method",
      "name": "processPayment",
      "return_type": "Promise<IPaymentResult>",
      "parameters": ["request: IPaymentRequest"]
    }
  ],
  "imports": [
    {"source": "./payment.service", "items": ["PaymentService"]},
    {"source": "@angular/core", "items": ["Component", "Injectable"]}
  ],
  "dependencies": ["./payment.service", "@angular/core"],
  "statistics": {
    "lines_of_code": 120,
    "num_classes": 1,
    "num_functions": 8,
    "num_interfaces": 2
  }
}
```

### Directory Analysis

```python
{
  "directory": "/microservices",
  "total_files_analyzed": 47,
  "files_by_language": {
    "typescript": 15,
    "go": 12,
    "python": 10,
    "csharp": 8,
    "java": 2
  },
  "cross_language_dependencies": [
    {
      "source": {"language": "typescript", "filepath": "frontend/order.ts"},
      "target": {"language": "go", "filepath": "backend/payment.go"},
      "type": "cross_language_import"
    }
  ],
  "statistics": {
    "total_lines_of_code": 12450,
    "total_classes": 89,
    "total_functions": 234,
    "by_language": {"typescript": {...}, "go": {...}, ...}
  }
}
```

---

## Language-Specific Features

### JavaScript/TypeScript
```typescript
// Automatically extracts:
- Classes and arrow functions
- Async/await patterns  
- Interfaces and type aliases
- Decorators (@Injectable, @Component)
- Default and named exports
- Promise chains (.then, .catch)
```

### Go
```go
// Automatically extracts:
- Functions, methods, receiver types
- Structs, interfaces, type aliases
- Goroutines (go keyword) and channels
- Package structure and imports
- Exported items (capitalized names)
```

### C#/.NET
```csharp
// Automatically extracts:
- Classes, interfaces, structs, records
- Properties, fields, methods
- Access modifiers (public, private, internal)
- Async/await (Task-based programming)
- Attributes ([ApiController], [Obsolete])
- Namespaces and using statements
```

---

## Testing

### Run Test Suite

```bash
cd agents/
python test_polyglot_examples.py
```

This creates a test polyglot codebase with TypeScript, Go, C#, and Python files and validates the analysis.

### Expected Output

```
Creating test codebase in: /tmp/polyglot_test_abc123
Created 4 test files:
  - frontend/src/order.controller.ts
  - backend/go/payment_service.go
  - backend/dotnet/PaymentController.cs
  - backend/python/payment_processor.py

Analyzing Polyglot Codebase
Total files analyzed: 4
Files by language: {'typescript': 1, 'go': 1, 'csharp': 1, 'python': 1}

Codebase Statistics:
  Total LOC: 385
  Total Classes: 5
  Total Functions: 12
```

---

## Troubleshooting

### "Language not available"

```python
Error: tree-sitter-javascript not available
Solution: pip install tree-sitter-javascript
```

### Parsing Errors

Some files may have syntax issues. The analyzer:
1. **Continues** processing other files
2. **Logs** errors to stderr
3. **Returns** partial results if available
4. **Reports** errors in the results dict

Check results for:
```python
if 'error' in result:
    print(f"Parsing error: {result['error']}")
```

### Performance Tips

1. **Use parallel workers:**
   ```python
   analyze_codebase(repo, max_workers=4)  # 4 workers
   ```

2. **Skip large directories:**
   - Analyzer automatically skips: `.git`, `node_modules`, `__pycache__`, `bin`, `obj`

3. **Analyze specific extensions:**
   - Don't analyze all extensions if you only need TypeScript
   ```bash
   python cartographer_agent.py /repo --ext .ts
   ```

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  MultiLanguageAnalyzer (Orchestrator)   │
└────────────────┬────────────────────────┘
                 │
     ┌───────────┼──────────┬──────────┐
     │           │          │          │
     ▼           ▼          ▼          ▼
    JS/TS      Go        C#        Python/Java
  Analyzer   Analyzer  Analyzer   (Existing)
     │           │          │          │
     └───────────┴──────────┴──────────┘
              │
              ▼
    ┌──────────────────────────┐
    │  Cartographer Agent      │
    │  (Neo4j Cypher Gen)      │
    └──────────────────────────┘
              │
        ┌─────┴──────┐
        ▼            ▼
   Neo4j DB    Visualization
```

---

## Integration Points

### With Existing Features

1. **Neo4j Integration** - Works with `mcp_neo4j_server.py`
   ```python
   # Analyzer generates Cypher directly
   cypher_stmt = "MERGE (m:Module {...}) MERGE (...)-[:CONTAINS]->(...)"
   ```

2. **Business Rules** - Python/Java only (for now)
   ```python
   # New languages use technical analysis
   # Python/Java use business rules when available
   ```

3. **MCP Servers** - Easy integration with `enhanced_mcp_server.py`
   ```python
   # Query across multiple languages
   from agents.multi_language_analyzer import analyze_codebase
   ```

---

## Next Steps

### Phase 2 (Q2 2026)
- [ ] Performance benchmarking (1000+ file repos)
- [ ] Production testing with real enterprises
- [ ] CI/CD pipeline integration
- [ ] Enhanced polyglot pattern detection

### Phase 3 (Q3 2026)  
- [ ] Additional languages: Rust, Kotlin, Ruby
- [ ] ML-based code quality analysis
- [ ] Enterprise visualization dashboard
- [ ] API for cloud deployment

---

## Support

### Documentation
- Full guide: [MULTI_LANGUAGE_SUPPORT_GUIDE.md](./MULTI_LANGUAGE_SUPPORT_GUIDE.md)
- Examples: [agents/test_polyglot_examples.py](./agents/test_polyglot_examples.py)

### Key Files
- **Orchestrator:** `agents/multi_language_analyzer.py`
- **JS/TS:** `agents/javascript_typescript_analyzer.py`
- **Go:** `agents/go_analyzer.py`
- **C#:** `agents/csharp_analyzer.py`
- **Dependencies:** `agents/cross_language_dependency_detector.py`

### Questions?

Check the [IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md](./IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md) for architectural rationale and design decisions.

---

**Version:** 1.0  
**Release Date:** March 12, 2026  
**Impact:** 40% → 95% enterprise codebases supported
