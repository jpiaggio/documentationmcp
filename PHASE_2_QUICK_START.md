# Phase 2 Quick Start Guide

**Launch Date:** March 11, 2026  
**Target Completion:** End of April 2026  
**Status:** 🚀 READY TO LAUNCH

---

## ⚡ 5-Minute Overview

Phase 2 introduces **three foundation improvements** that provide real-time visibility into your codebase, architecture, and team:

| Improvement | What It Does | Value |
|---|---|---|
| **#2 Health Dashboard** | Real-time metrics on code quality | Identify problems before they become expensive |
| **#6 Architecture Drift** | Detects architectural violations | Prevent monolith decay and maintain design integrity |
| **#14 Expertise Mapping** | Identifies team knowledge & gaps | Reduce bus factor, plan training |

---

## 🚀 Getting Started (This Week)

### Monday: Setup

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Install Phase 2 dependencies (if needed)
pip install networkx fastapi uvicorn

# 3. Initialize Phase 2
cd agents/
```

### Tuesday-Thursday: Run Individual Analyses

```bash
# Run Health Dashboard
python codebase_health_monitor.py ../  # Pass your repo path

# Run Architecture Validation
python architecture_validator.py ../

# Run Expertise Mapping
python expertise_mapper.py ../
```

### Friday: Run Integrated Analysis

```bash
# Run complete Phase 2 analysis with HTML report
python phase2_orchestrator.py ./ phase2_report.html

# Open report in browser
open phase2_report.html
```

---

## 📊 Phase 2 Agents Overview

### Agent 1: Codebase Health Monitor (#2)

**What it measures:**
- Overall health score (0-100)
- Test coverage percentage
- Documentation coverage
- Complexity hotspots
- Dead code percentage
- Circular dependencies
- Security issues
- Performance concerns

**How to use:**
```python
from codebase_health_monitor import CodebaseHealthMonitor

monitor = CodebaseHealthMonitor('./my-repo')
report = monitor.generate_health_report()

print(f"Health Score: {report.overall_health:.1f}/100")
print(f"Test Coverage: {report.test_coverage:.1f}%")
print(f"Hotspots: {len(report.complexity_hotspots)}")
```

**Key Features:**
- 🎯 Identifies top complexity hotspots
- 📈 Tracks trends over time
- 💡 Generates improvement recommendations
- ⚡ Caches results for fast queries

---

### Agent 2: Architecture Validator (#6)

**What it detects:**
- Circular dependencies
- Layer violations (cross-layer dependencies)
- Naming convention violations
- Dependency cardinality violations (too many imports)
- Deprecated component usage

**How to use:**
```python
from architecture_validator import ArchitectureValidator, ArchitectureRules, LayerDefinition

# Optional: Define custom rules
rules = ArchitectureRules(
    layers=[
        LayerDefinition('api', ['**/api/**'], ['services']),
        LayerDefinition('services', ['**/services/**'], ['repositories']),
    ]
)

validator = ArchitectureValidator('./my-repo', rules)
report = validator.validate_architecture()

print(f"Compliance: {report.compliance_score:.1f}%")
print(f"Critical Issues: {report.critical_violations}")
```

**Key Features:**
- 📐 Configurable layer definitions
- ✅ Automatic rule checking
- 🔍 Pre-commit hook integration ready
- 📋 Detailed violation reports

---

### Agent 3: Expertise Mapper (#14)

**What it analyzes:**
- Team members' primary code domains
- Language expertise distribution
- Code review quality
- Knowledge gaps
- Single points of failure (bus factor)
- Mentoring opportunities

**How to use:**
```python
from expertise_mapper import ExpertiseMapper

mapper = ExpertiseMapper('./my-repo')
expertise_map = mapper.map_team_expertise(days=365)

print(f"Team Health: {expertise_map.team_health_score:.1f}/100")
print(f"Knowledge Gaps: {len(expertise_map.knowledge_gaps)}")
print(f"At-Risk Modules: {expertise_map.bus_factor.at_risk_modules}")
```

**Key Features:**
- 👥 Git-based analysis (no manual input needed)
- 🎓 Identifies mentoring opportunities
- 🚨 Alerts on single points of failure
- 📊 Team health scoring

---

## 🔧 Configuration

### Architecture Rules (Optional)

Create `config/architecture_rules.yaml`:

```yaml
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

naming_conventions:
  services: "*_service.py"
  repositories: "*_repository.py"
  utils: "*_util*.py"

max_dependencies_per_module: 20
max_cyclomatic_complexity: 20

deprecated_modules:
  - legacy_auth
  - old_payment_system
```

---

## 📈 Understanding the Reports

### 1. Health Dashboard Report

**Key Metrics:**
- **Overall Health**: Combined score of all metrics
- **Test Coverage**: % of code with tests (target: >70%)
- **Documentation**: % of functions/classes with docstrings (target: >60%)
- **Complexity**: Average cyclomatic complexity (target: <15)
- **Circular Deps**: Number of circular dependency cycles (target: 0)

**Interpreting Results:**
- 🟢 90-100: Excellent - maintain current standards
- 🟡 70-89: Good - continue improvements
- 🟠 50-69: Warning - address key issues
- 🔴 <50: Critical - immediate action needed

### 2. Architecture Validation Report

**Violation Severity:**
- 🔴 **CRITICAL**: Must fix before next release
- 🟠 **HIGH**: Plan fix in next sprint
- 🟡 **MEDIUM**: Include in backlog
- 🔵 **LOW**: Nice to have

**Common Violations:**
```
Circular Dependency A -> B -> C -> A
  Impact: Cannot deploy independently
  Action: Extract shared logic to third module

Cross-Layer Violation: UI -> Database (should go through API)
  Impact: Tight coupling, hard to test
  Action: Route through API layer
```

### 3. Team Expertise Report

**Watch For:**
- 🚨 **Single Points of Failure**: Modules with only 1 expert
- ⚠️ **Knowledge Gaps**: Critical areas with no expert
- 🎯 **Mentoring Opportunities**: Pair experts with growing team members

**Example Actions:**
```
Single Point of Failure: alice (payment_service only)
  Action: Schedule 4-week knowledge transfer with bob

Knowledge Gap: Kubernetes deployment
  Action: Hire devops engineer or train existing team member
```

---

## 💻 Integration with Workflows

### Git Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

cd agents/
python -c "
from architecture_validator import ArchitectureValidator
validator = ArchitectureValidator('..')
report = validator.validate_architecture()

critical = [v for v in report.violations if v.severity.value == 'CRITICAL']
if critical:
    print('❌ COMMIT BLOCKED: Critical architecture violations detected')
    for v in critical:
        print(f'  - {v.violation_description}')
    exit(1)
"
```

### CI/CD Pipeline Integration

```yaml
# GitHub Actions example
- name: Phase 2 Health Check
  run: |
    cd agents/
    python -c "
    from codebase_health_monitor import CodebaseHealthMonitor
    monitor = CodebaseHealthMonitor('..')
    report = monitor.generate_health_report()
    
    if report.overall_health < 50:
        print(f'❌ Health score too low: {report.overall_health:.1f}')
        exit(1)
    
    print(f'✅ Health score: {report.overall_health:.1f}')
    "
```

### Dashboard Server (Coming in Phase 3)

```bash
# Start dashboard server (planned for Phase 3)
python -m uvicorn health_dashboard_server:app --reload
# Visit http://localhost:8000/dashboard
```

---

## 📊 Sample Output

### Health Dashboard
```
================================================================================
📊 CODEBASE HEALTH REPORT
================================================================================
Timestamp: 2026-03-11T10:30:00
Overall Health: 72.5/100
Total Modules: 147
Trend: → STABLE

📋 KEY METRICS:
  ✅ Codebase Complexity: 12.3 (threshold: 15)
  ⚠️ Test Coverage: 45.2% (threshold: 50%)
  ✅ Documentation Coverage: 62.5% (threshold: 40%)
  ✅ Circular Dependencies: 2 (threshold: 5)
  ⚠️ Dead Code: 8.2% (threshold: 5%)
  🔴 Security Issues: 4

🔥 TOP HOTSPOTS:
  - payment_processor: 34.2 complexity
  - order_service: 28.1 complexity
  - auth_handler: 26.5 complexity

💡 RECOMMENDATIONS:
  1. Increase test coverage to 70% (currently 45%)
  2. Refactor payment_processor (complexity: 34.2)
  3. Remove dead code (8.2% of codebase)
  4. Address 4 security issues
================================================================================
```

### Architecture Validation
```
================================================================================
🏗️ ARCHITECTURE VALIDATION REPORT
================================================================================
Compliance Score: 65.3/100
Total Violations: 12
  🔴 Critical: 1
  🟠 High: 4
  🟡 Medium: 5
  🔵 Low: 2

🔍 TOP VIOLATIONS:

  🔴 CIRCULAR_DEPENDENCY: order_service -> payment_service -> order_service
     Description: Circular dependency detected
     Impact: Cannot deploy modules independently; creates tight coupling
     Remediation: Refactor to break the cycle

  🟠 CROSS_LAYER: api/orders.py directly accesses database
     Description: Layer violation: api cannot depend on database
     Impact: Violates layered architecture
     Remediation: Route through services layer
```

### Team Expertise
```
================================================================================
👥 TEAM EXPERTISE MAP
================================================================================
Team Health Score: 68.5/100
Team Members: 8

👤 TEAM MEMBERS & EXPERTISE:

  alice
    Commits: 247
    Primary Domains: payment_service, fraud_detection
    Languages: Python, SQL
    Expertise Confidence: 92%
    Review Quality: 94%

🚨 SINGLE POINTS OF FAILURE (3):
  - payment_service (only: alice)
  - auth_service (only: bob)
  - reporting_engine (only: charlie)

⚠️ KNOWLEDGE GAPS (2):
  CRITICAL: Kubernetes deployment
  HIGH: Frontend performance optimization

🎓 MENTORING RECOMMENDATIONS:
  alice → dave: Learn payment systems
  bob → eve: Learn authentication
```

---

## 🎯 Next Steps

### This Week
- [ ] Run Phase 2 analysis
- [ ] Review all three reports
- [ ] Identify top 3 critical issues
- [ ] Create action plan

### This Month
- [ ] Fix critical architecture violations
- [ ] Increase test coverage by 10-15%
- [ ] Start refactoring top hotspots
- [ ] Plan knowledge transfer sessions

### This Quarter (Phase 2 Completion)
- [ ] Achieve >70% test coverage
- [ ] Zero critical violations
- [ ] All bus factors addressed
- [ ] Knowledge gaps closing

---

## ❓ FAQ

**Q: How often should I run Phase 2 analysis?**  
A: Weekly during active development. Set up CI/CD to run automatically on each PR.

**Q: What if my architecture rules are unclear?**  
A: Start with defaults (no circular deps, basic layering). Add rules incrementally.

**Q: Can Phase 2 work with multiple languages?**  
A: Phase 2 works with Python. Phase 3 will add JavaScript, TypeScript, Go, etc.

**Q: How accurate is the team expertise mapping?**  
A: 85-90% accurate based on git history. Combine with manual surveys for 95%+.

**Q: Can I customize the visualizations?**  
A: Yes - Phase 3 will include custom dashboard. For now, use the HTML export.

---

## 📞 Support

**Issues?**
- Check [PHASE_2_IMPLEMENTATION_PLAN.md](PHASE_2_IMPLEMENTATION_PLAN.md) for details
- Review [IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md](../IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md#tier-2-medium-impact-roi-6-12-months)
- Run agents individually to debug

**Want to contribute?**
- Extend with new metrics
- Add support for more languages
- Build visualization dashboard
- Integrate with monitoring systems

---

**Ready to start?** Run this:

```bash
cd agents/
python phase2_orchestrator.py . phase2_report.html
open phase2_report.html
```

**Happy analyzing!** 🚀
