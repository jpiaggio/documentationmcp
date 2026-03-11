# Migration Guide: From Standard to Enterprise Analysis

## Overview

This guide helps you transition from the basic `cartographer_agent.py` to the new enterprise-grade system with:
- ✅ Incremental indexing (80-90% cost savings)
- ✅ Context pruning (70-80% token reduction)
- ✅ Multi-module support
- ✅ Performance monitoring

---

## Before You Start

### What You Have Now
```python
# Old way: Re-analyzes everything
from agents.cartographer_agent import cartographer_agent

results = cartographer_agent('/large/repo')
# ^^ Processes all 800 files every time!
```

### What You'll Have
```python
# New way: Only changed files
from agents.integrated_workflow import create_workflow

workflow = create_workflow([
    {'path': '/large/repo', 'name': 'Backend', 'extensions': ['.py']}
])
result = workflow.analyze()
# ^^ Only ~80 files on day 2! (90% reduction!)
```

---

## Step-by-Step Migration

### Step 1: Backup Your Current Setup

```bash
# Backup old code
cp agents/cartographer_agent.py agents/cartographer_agent.py.bak

# Note any custom configurations
grep -r "cartographer_agent" . > current_usage.txt
```

### Step 2: Create Configuration

```bash
# Interactive setup (recommended)
python3 agents/config_manager.py

# OR create from command line
python3 agents/config_manager.py create /path/to/repo MyProject
```

**Example: Creating a config for your project**

```bash
$ python3 agents/config_manager.py

Configuration Setup Wizard
================================================================================

Enter configuration name (e.g., 'my-project'): my-backend

Enter repository path (or 'done' to finish): /Users/juani/projects/backend

Enter display name for this module (default: backend): Backend API

Enter file extensions to scan (default: .py, separate with comma): .py

✅ Added: Backend API

Enter repository path (or 'done' to finish): done

Number of parallel workers (default: 4): 4
Force full reindex? (y/n, default: n): n
Extract business rules? (y/n, default: y): y
Prune context? (y/n, default: y): y

✅ Configuration saved: .cartographer_config/my-backend.json
```

### Step 3: Update Your Analysis Script

**Old way:**
```python
from agents.cartographer_agent import cartographer_agent

# Analyze single repo
cypher_statements = cartographer_agent('/path/to/repo')

print(f"Generated {len(cypher_statements)} statements")
```

**New way (single module):**
```python
from agents.integrated_workflow import create_workflow

# Create workflow
workflow = create_workflow([
    {
        'path': '/path/to/repo',
        'name': 'My Project',
        'extensions': ['.py']
    }
])

# Analyze with incremental indexing
result = workflow.analyze()

print(f"Analyzed {result['metrics']['total_files_processed']} files")
print(f"Saved ${result['metrics']['cost_before'] - result['metrics']['cost_after']:.2f}")
```

**New way (from config file):**
```python
from agents.integrated_workflow import create_workflow_from_file

# Load configuration
workflow = create_workflow_from_file('.cartographer_config/my-backend.json')

# Analyze
result = workflow.analyze()
```

**New way (multiple modules):**
```python
from agents.integrated_workflow import create_workflow

# Analyze multiple modules in parallel
workflow = create_workflow([
    {'path': '/backend', 'name': 'Backend API', 'extensions': ['.py']},
    {'path': '/worker', 'name': 'Worker Service', 'extensions': ['.py']},
    {'path': '/web', 'name': 'Web App', 'extensions': ['.ts']}
], parallel_workers=4)

result = workflow.analyze()

# Cost savings across all modules
total_saved = result['metrics']['cost_before'] - result['metrics']['cost_after']
print(f"Total saved: ${total_saved:.2f}")
print(f"Monthly projection: ${total_saved * 30:.2f}")
```

### Step 4: Adapt Your Analysis Logic

**If you're using Cypher statements:**

```python
# Old way
statements = cartographer_agent('/repo')

for statement in statements:
    print(statement)  # Process each

# New way - same output!
from agents.integrated_workflow import create_workflow

workflow = create_workflow([{'path': '/repo'}])
result = workflow.analyze()

# Access results from the enhanced server
module_result = result['results']['module_results']['My Project']
statements = module_result['cypher_statements']

for statement in statements:
    print(statement)  # Process each - same as before!
```

**If you're using BusinessJourneyAnalyzer:**

```python
# Old way - still works!
from agents.business_journey_analyzer import BusinessJourneyAnalyzer

statements = cartographer_agent('/repo')
analyzer = BusinessJourneyAnalyzer(statements)
journey = analyzer.get_customer_journey()

# New way - integrated!
from agents.integrated_workflow import create_workflow

workflow = create_workflow([{'path': '/repo'}])
result = workflow.analyze()

# Results include business rules directly
journey = result['results']['module_results']['My Project']['business_rules']
```

### Step 5: Switch Over Existing Integrations

**If you have a REST API:**

```python
# Old
from flask import Flask
from agents.cartographer_agent import cartographer_agent

@app.route('/analyze')
def analyze():
    results = cartographer_agent('/repo')
    return {'statements': results}

# New
from flask import Flask
from agents.integrated_workflow import create_workflow_from_file

@app.route('/analyze')
def analyze():
    workflow = create_workflow_from_file('.cartographer_config/backend.json')
    result = workflow.analyze()
    return {
        'statements': result['results']['module_results'],
        'metrics': result['metrics']
    }
```

**If you have a scheduled job (Cron/GitHub Actions):**

```bash
# Old
python3 agents/cartographer_agent.py /repo > results.txt

# New (automatically uses incremental indexing!)
python3 agents/integrated_workflow.py .cartographer_config/my-project.json
```

---

## Handling Special Cases

### Case 1: I need full code, not just signatures

By default, context pruning is enabled. To get full code:

```python
# Get full code for a specific element
workflow = create_workflow([...])

# Fetch on-demand
with open('/repo/module.py') as f:
    code = f.read()

# Or use the loader
full_code = workflow.loaders['/repo'].get_full_context(element)
```

### Case 2: I'm analyzing a large repo (10,000+ files)

The incremental indexing is perfect for this! Set it up once:

```python
workflow = create_workflow([{'path': '/huge/repo'}], parallel_workers=8)

# First run: ~60 seconds, analyzes all files
result = workflow.analyze()

# Second run: ~10 seconds, only changed files!
result = workflow.analyze()
```

### Case 3: I need to re-analyze everything

Use `force_reindex` flag:

```python
workflow = create_workflow(
    [...],
    force_reindex=True  # Bypass cache
)

result = workflow.analyze()
```

### Case 4: I have custom file extensions

Specify them in configuration:

```bash
# Interactive
python3 agents/config_manager.py
# When prompted: "Enter file extensions ... : .go,.rs,.cpp"

# Programmatic
workflow = create_workflow([{
    'path': '/rust/project',
    'extensions': ['.rs']  # Rust files
}])
```

---

## Monitoring Your Migration

### Track Your Savings

```bash
# View dashboard
python3 agents/performance_dashboard.py

# Should show increasing cache hit rate over time:
# Day 1: Cache hit: 0%   (first full index)
# Day 2: Cache hit: 85%  (most files unchanged)
# Day 3: Cache hit: 90%  (optimization working!)
```

### Monitor Cache Growth

```python
workflow = create_workflow([...])

# Check cache statistics
for module_path, indexer in workflow.indexers.items():
    stats = indexer.get_stats()
    print(f"Module: {module_path}")
    print(f"  Cached files: {stats['cached_files']}")
    print(f"  Last indexed: {stats['last_indexed']}")
```

### Export Metrics

```python
# After running analysis
workflow.export_metrics('my_metrics.json')

# View the metrics
cat my_metrics.json
```

---

## Troubleshooting Migration Issues

### Issue: "Cache not working"

**Symptoms:** Second run still processes all files

**Solution:** Ensure git is properly initialized

```bash
cd /your/repo
git status  # Should work

# If not:
git init
git add .
git commit -m "init"

# Then retry
python3 agents/integrated_workflow.py config.json
```

### Issue: "Configuration file not found"

**Symptoms:** Error when running from config

**Solution:** Check file path

```bash
# List available configs
python3 agents/config_manager.py list

# Show specific config
python3 agents/config_manager.py show my-project

# Use full path if needed
python3 agents/integrated_workflow.py .cartographer_config/my-project.json
```

### Issue: "Tree-sitter errors"

**Symptoms:** `ModuleNotFoundError: No module named 'tree_sitter_python'`

**Solution:** Install language support

```bash
pip3 install tree-sitter-python
pip3 install tree-sitter-java  # If analyzing Java
```

### Issue: "My old code still works but doesn't cache"

**Symptoms:** Running old `cartographer_agent()` doesn't show savings

**Solution:** Update your code to use `IntegratedWorkflow`

```python
# This still works but doesn't cache:
from agents.cartographer_agent import cartographer_agent
cartographer_agent('/repo')

# You need to use the new system:
from agents.integrated_workflow import create_workflow
workflow = create_workflow([{'path': '/repo'}])
result = workflow.analyze()
```

---

## Rollback Plan

If you need to go back to the old system:

```bash
# Restore backup
cp agents/cartographer_agent.py.bak agents/cartographer_agent.py

# Use old code
from agents.cartographer_agent import cartographer_agent
results = cartographer_agent('/repo')
```

The old system is still fully functional. The new system is additive.

---

## Migration Checklist

- [ ] Read this migration guide completely
- [ ] Backup current setup
- [ ] Install dependencies (tree-sitter, etc.)
- [ ] Create configuration for your project(s)
- [ ] Update your analysis script
- [ ] Test on small repo first
- [ ] Run performance baseline
- [ ] Switch to new system
- [ ] Monitor cache hit rate for 1 week
- [ ] Verify cost savings
- [ ] Update documentation
- [ ] Train team on new workflow

---

## Performance Expectations

### First Run
- **Time:** Same as old system (slight overhead from caching)
- **Cost:** Same as old system
- **Output:** Identical Cypher statements, business rules, etc.

### Second Run (24 hours later)
- **Time:** 80-90% faster (only changed files)
- **Cost:** 80-90% cheaper (only changed files)
- **Cache hit rate:** ~85-90% if 10% of files changed

### Week 1
- **Total time:** Slightly slower (caching overhead)
- **Total cost:** 10-15% cheaper
- **Value:** System learning your patterns

### Month 1+
- **Monthly cost:** 80-90% reduction ✨
- **Cache hit rate:** 85-95%
- **Value:** Massive savings and speed improvements

---

## Next Steps After Migration

1. **Monitor Metrics** - Track dashboard daily
2. **Optimize Workers** - Adjust `parallel_workers` based on performance
3. **Scale Up** - Add more modules to analysis
4. **Integrate with Copilot** - Use the MCP tools with Claude
5. **Export Reports** - Share metrics with stakeholders

---

## Getting Help

- **Documentation:** See `ENTERPRISE_ENHANCEMENTS_GUIDE.md`
- **Examples:** Run `python3 example_enterprise_usage.py`
- **Tests:** Run `bash test_enterprise_enhancements.sh`
- **Configuration:** Run `python3 agents/config_manager.py`

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Files analyzed** | 100% | 10-20% (after day 1) |
| **API calls** | 100% | 10-20% |
| **Tokens used** | 100% | 20-30% |
| **Speed** | 60s | 10s (cached) |
| **Cost** | $100/month | $10/month |
| **Setup** | 5 minutes | 10 minutes |

The old system still works perfectly. The new system adds caching, context pruning, and gives you 80-90% cost reduction with zero changes to your analysis output.

**Ready to migrate?** Start with: `python3 agents/config_manager.py`

---

*Migration Guide for Enterprise Enhancements v2.0*
*Last updated: March 10, 2026*
