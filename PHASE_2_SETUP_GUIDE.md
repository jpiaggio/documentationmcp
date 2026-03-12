# Phase 2 Detailed Setup & Implementation Guide

**Status:** Ready for Implementation  
**Start Date:** March 11, 2026  
**Target Completion:** April 30, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation & Setup](#installation--setup)
3. [Agent Configuration](#agent-configuration)
4. [Running Analyses](#running-analyses)
5. [Interpreting Results](#interpreting-results)
6. [Integration Points](#integration-points)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)

---

## Prerequisites

### System Requirements
- Python 3.8+ ✅
- Git repository ✅
- 2GB free disk space for caching
- 5-10 minutes for initial analysis

### Python Dependencies
```bash
pip install networkx    # For graph analysis
pip install requests    # For API calls (Phase 3)
```

### Already Installed
- `ast` (Python standard library) - for code analysis
- `subprocess` - for git integration
- `json` - for report serialization

---

## Installation & Setup

### Step 1: Verify Agent Files

Check that all Phase 2 agents are in place:

```bash
ls -la agents/
# Expected files:
# ✅ codebase_health_monitor.py
# ✅ architecture_validator.py
# ✅ expertise_mapper.py
# ✅ phase2_orchestrator.py
```

### Step 2: Activate Virtual Environment

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Step 3: Create Cache Directories

```bash
mkdir -p .cartographer_cache
mkdir -p config
```

### Step 4: Initialize Configuration

```bash
# Copy default architecture rules
cat > config/architecture_rules.yaml << 'EOF'
layers:
  - name: api
    patterns:
      - "**/api/**"
      - "*/routes/**"
    depends_on:
      - services
      - utilities

  - name: services
    patterns:
      - "**/services/**"
      - "*/business/**"
    depends_on:
      - repositories
      - utilities

  - name: repositories
    patterns:
      - "**/repositories/**"
      - "*/data/**"
    depends_on:
      - utilities

  - name: utilities
    patterns:
      - "**/utils/**"
      - "**/utilities/**"
    depends_on: []

naming_conventions:
  services: "*_service.py"
  repositories: "*_repository.py"
  utils: "*_util*.py"

max_dependencies_per_module: 20
max_cyclomatic_complexity: 20

deprecated_modules: []
EOF
```

### Step 5: Verify Installation

```bash
cd agents/
python -c "
import codebase_health_monitor
import architecture_validator
import expertise_mapper
import phase2_orchestrator
print('✅ All Phase 2 agents loaded successfully')
"
```

---

## Agent Configuration

### Health Dashboard Configuration

The `CodebaseHealthMonitor` works with default settings. No configuration needed, but you can customize:

```python
# Custom initialization
from codebase_health_monitor import CodebaseHealthMonitor

monitor = CodebaseHealthMonitor(
    repo_path='./',
    cache_dir='./.cartographer_cache'
)

# Custom thresholds
monitor.thresholds = {
    'avg_complexity': {'warning': 20, 'critical': 30},
    'test_coverage': {'warning': 60, 'critical': 40},
    'documentation': {'warning': 50, 'critical': 30},
}
```

### Architecture Validator Configuration

Load custom rules:

```python
from architecture_validator import (
    ArchitectureValidator,
    ArchitectureRules,
    LayerDefinition
)

# Define custom rules
rules = ArchitectureRules(
    layers=[
        LayerDefinition(
            name='api',
            patterns=['**/api/**', '**/routes/**'],
            depends_on=['services', 'utilities']
        ),
        LayerDefinition(
            name='services',
            patterns=['**/services/**'],
            depends_on=['repositories', 'utilities']
        ),
        LayerDefinition(
            name='repositories',
            patterns=['**/repositories/**'],
            depends_on=['utilities']
        ),
        LayerDefinition(
            name='utilities',
            patterns=['**/utils/**'],
            depends_on=[]
        ),
    ],
    naming_conventions={
        'services': '*service.py',
        'repositories': '*repository.py',
    },
    max_dependencies_per_module=20,
    max_cyclomatic_complexity=20,
    deprecated_modules=['legacy_auth', 'old_payment']
)

# Initialize with custom rules
validator = ArchitectureValidator('./', rules)
report = validator.validate_architecture()
```

### Expertise Mapper Configuration

No configuration needed. Analyzes git history automatically:

```python
from expertise_mapper import ExpertiseMapper

# Analyze last 365 days of git history
mapper = ExpertiseMapper('./')
expertise_map = mapper.map_team_expertise(days=365)

# You can also analyze specific time periods
last_3_months = mapper.map_team_expertise(days=90)
```

---

## Running Analyses

### Quick Run: Individual Agents

#### 1. Health Dashboard

```bash
cd agents/
python codebase_health_monitor.py ../
```

**Output:**
- Console summary
- `.cartographer_cache/latest_health_report.json`
- `.cartographer_cache/health_metrics_history.json`

#### 2. Architecture Validation

```bash
cd agents/
python architecture_validator.py ../
```

**Output:**
- Console listing all violations
- Organized by severity (CRITICAL, HIGH, MEDIUM, LOW)

#### 3. Team Expertise Mapping

```bash
cd agents/
python expertise_mapper.py ../
```

**Output:**
- Team member expertise profiles
- Module ownership
- Knowledge gaps
- Bus factor analysis

### Complete Analysis: Integrated Orchestrator

```bash
cd agents/
python phase2_orchestrator.py . ../phase2_report.html
```

**Output:**
- HTML report: `phase2_report.html`
- Comprehensive metrics dashboard
- Open in browser: `open ../phase2_report.html`

### Programmatic Usage

```python
# Example: Custom analysis flow
from agents.phase2_orchestrator import Phase2Orchestrator

orchestrator = Phase2Orchestrator('./')
report = orchestrator.run_complete_analysis()

# Access individual reports
health_report = report.health_report
architecture_report = report.architecture_report
expertise_map = report.expertise_map

# Process results
print(f"Health: {health_report.overall_health:.1f}")
print(f"Compliance: {architecture_report.compliance_score:.1f}")
print(f"Team Health: {expertise_map.team_health_score:.1f}")

# Save reports
import json

with open('phase2_results.json', 'w') as f:
    json.dump({
        'health': json.loads(json.dumps(health_report.__dict__, default=str)),
        'architecture': json.loads(json.dumps(architecture_report.__dict__, default=str)),
        'team': json.loads(json.dumps(expertise_map.__dict__, default=str))
    }, f, indent=2)
```

---

## Interpreting Results

### Health Dashboard Results

**Score Interpretation:**
- **90-100**: Excellent state. Continue current practices.
- **70-89**: Good health. Address minor issues in next sprint.
- **50-69**: Warning. Plan improvements for next 2 weeks.
- **<50**: Critical. Immediate action required.

**Key Metrics Deep Dive:**

1. **Complexity Score**
   - Low: <10 (Excellent)
   - Medium: 10-20 (Good)
   - High: 20-30 (Needs refactoring)
   - Critical: >30 (Urgent refactoring)

2. **Test Coverage**
   - <30%: Critical - Add tests immediately
   - 30-50%: Low - Increase test writing
   - 50-70%: Medium - Continue improvements
   - >70%: Good - Maintain standards

3. **Documentation**
   - <20%: Critical gap
   - 20-40%: Needs improvement
   - 40-60%: Good
   - >60%: Excellent

**Action Items by Metric:**

```
Complexity Hotspots > 25:
  ├─ Design review
  ├─ Extract methods
  ├─ Reduce parameters
  └─ Simplify logic

Low Test Coverage:
  ├─ Identify critical paths
  ├─ Write unit tests
  ├─ Add integration tests
  └─ Target 70%+ coverage

Dead Code > 10%:
  ├─ Identify unused functions
  ├─ Check for orphaned modules
  ├─ Document dependencies
  └─ Remove or deprecate

Circular Dependencies:
  ├─ Identify dependency cycles
  ├─ Extract shared logic
  ├─ Refactor modules
  └─ Validate with architect
```

### Architecture Validation Results

**Violation Response Matrix:**

| Severity | Action | Timeline | Impact |
|----------|--------|----------|--------|
| CRITICAL | Block PR | Immediate | Release blocker |
| HIGH | Must fix | This sprint | Design debt |
| MEDIUM | Should fix | Next sprint | Tech debt |
| LOW | Nice to fix | Backlog | Polish |

**Common Violation Resolutions:**

1. **Circular Dependencies**
   ```python
   # Problem: A imports B, B imports A
   
   # Solution: Extract common logic to C
   # A imports C
   # B imports C
   # No circular reference
   ```

2. **Cross-Layer Violations**
   ```python
   # Problem: UI directly calls Database
   
   # Solution: Route through API/Services
   # UI → API → Services → Database
   ```

3. **High Cardinality (Too Many Dependencies)**
   ```python
   # Problem: Module X imports 25+ other modules
   
   # Solution:
   # 1. Extract related imports to facade
   # 2. Use dependency injection
   # 3. Split module into smaller pieces
   ```

### Expertise Map Results

**Team Health Score Interpretation:**
- **80-100**: Healthy - Knowledge well distributed
- **60-79**: Fair - Some concentration areas
- **40-59**: Poor - Significant knowledge gaps
- **<40**: Critical - Single points of failure

**Knowledge Gap Assessment:**

```
Gap Type            | Severity | Action
--------------------|----------|------------------------------------------
No expertise in X   | CRITICAL | Hire or intensive training (4-8 weeks)
Only 1 expert in Y  | HIGH     | Knowledge transfer (2-3 weeks)
2 experts in Z      | MEDIUM   | Cross-training recommended
Emerging tech gaps  | LOW      | Plan learning for next quarter
```

**Bus Factor Chart:**

```
Modules with only 1 expert = Bus Factor of 1
Modules with 2 experts = Bus Factor of 2
Modules with 3+ experts = Bus Factor of 3+ (Good)

Target: Bus Factor ≥ 2 for all business-critical modules
```

---

## Integration Points

### Pre-Commit Hook

```bash
# Create .git/hooks/pre-commit
#!/bin/bash

cd agents/
python -c "
from architecture_validator import ArchitectureValidator

validator = ArchitectureValidator('..')
report = validator.validate_architecture()

critical = [v for v in report.violations 
            if v.severity.value == 'CRITICAL']

if critical:
    print('❌ Commit blocked: Critical architecture violations')
    for v in critical:
        print(f'  {v.violation_description}')
    exit(1)

print('✅ Architecture validation passed')
" || exit 1
```

### CI/CD Integration

**GitHub Actions:**
```yaml
name: Phase 2 Health Check

on: [pull_request, push]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install networkx
      
      - name: Run Phase 2 Analysis
        run: |
          cd agents/
          python -c "
          from phase2_orchestrator import Phase2Orchestrator
          
          orc = Phase2Orchestrator('..')
          report = orc.run_complete_analysis()
          
          # Fail if health too low
          if report.health_report.overall_health < 60:
              print(f'❌ Health score too low: {report.health_report.overall_health:.1f}')
              exit(1)
          
          # Fail if critical violations
          critical = [v for v in report.architecture_report.violations 
                      if v.severity.value == 'CRITICAL']
          if critical:
              print(f'❌ {len(critical)} critical violations')
              exit(1)
          
          print('✅ All Phase 2 checks passed')
          "
```

**GitLab CI:**
```yaml
phase2_analysis:
  stage: quality
  script:
    - cd agents/
    - python phase2_orchestrator.py . ../phase2_report.html
  artifacts:
    paths:
      - phase2_report.html
    expire_in: 1 week
```

### Dashboard/Reporting

**Generate Regular Reports:**
```bash
#!/bin/bash
# generate_weekly_phase2_report.sh

cd agents/
python phase2_orchestrator.py . ../reports/phase2_$(date +%Y%m%d).html

# Upload to S3
aws s3 cp ../reports/phase2_$(date +%Y%m%d).html s3://reports/
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'networkx'"

**Solution:**
```bash
pip install networkx
```

### Issue: "Permission denied: .git/hooks/pre-commit"

**Solution:**
```bash
chmod 755 .git/hooks/pre-commit
```

### Issue: Analysis taking too long

**Solution:**
```python
# Reduce analysis scope
mapper = ExpertiseMapper('./')
expertise_map = mapper.map_team_expertise(days=90)  # Instead of 365

# Or cache results
import os
if os.path.exists('.cartographer_cache/latest_health_report.json'):
    print("Using cached report")
```

### Issue: False positives in architecture violations

**Solution:**
```python
# Refine rules to reduce false positives
rules.max_dependencies_per_module = 25  # Increased from 20
rules.forbidden_patterns = {}  # Clear strict patterns

# Re-run with less strict rules
```

### Issue: Team expertise map shows "No owner" for modules

**Solution:**
```bash
# Ensure git history exists
git log -5

# If no history, run on full repository
# The mapper uses git history for analysis
```

---

## Performance Tuning

### Speed Up Analysis

**1. Reduce Time Period for Expertise Mapping**
```python
# Analyze last 90 days instead of 365
mapper.map_team_expertise(days=90)  # Faster
```

**2. Cache Health Results**
```python
# Health dashboard caches results
# Re-run takes 2-3 seconds vs 30-60 seconds
```

**3. Parallel Processing (Future)**
```python
# Phase 3 update will add parallel processing
# For now, run each agent separately
```

### Memory Optimization

**Large Repositories (1000+ modules):**
```python
# Process incrementally
modules = []
for chunk in chunks(all_modules, 100):
    modules.extend(analyzer.analyze_batch(chunk))
```

---

## Metrics Export

### Export to JSON

```python
import json
from phase2_orchestrator import Phase2Orchestrator

orc = Phase2Orchestrator('./')
report = orc.run_complete_analysis()

# Convert to JSON-serializable format
output = {
    'timestamp': report.timestamp,
    'health': {
        'score': report.health_report.overall_health,
        'test_coverage': report.health_report.test_coverage,
        'documentation': report.health_report.documentation_coverage,
    },
    'architecture': {
        'compliance': report.architecture_report.compliance_score,
        'violations': {
            'critical': report.architecture_report.critical_violations,
            'high': report.architecture_report.high_violations,
        }
    },
    'team': {
        'health': report.expertise_map.team_health_score,
        'members': len(report.expertise_map.team_members),
    }
}

with open('phase2_metrics.json', 'w') as f:
    json.dump(output, f, indent=2)
```

### Export to CSV (for Excel/Analytics)

```python
import csv

# Health metrics
with open('health_metrics.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Metric', 'Value', 'Threshold', 'Status'])
    for name, metric in report.health_report.health_metrics.items():
        writer.writerow([name, metric.value, metric.threshold, metric.status])

# Complexity hotspots
with open('hotspots.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Module', 'Complexity', 'LOC', 'Priority'])
    for hs in report.health_report.complexity_hotspots:
        writer.writerow([hs.module_name, hs.complexity_score, hs.lines_of_code, hs.refactoring_priority])
```

---

## Next Steps

1. **This Week**: Run Phase 2 analysis
2. **This Sprint**: Address CRITICAL violations
3. **This Month**: 
   - Increase test coverage by 15%
   - Resolve all CRITICAL issues
   - Plan bus factor mitigation
4. **Next Quarter**: Complete Phase 2 improvements

---

**Questions?** See [PHASE_2_QUICK_START.md](PHASE_2_QUICK_START.md) for quick reference.
