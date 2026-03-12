# Phase 2 Implementation Plan (Months 3-4)

## 📋 Overview

Phase 2 builds the **foundation improvements** that enable better code quality management and team organization:

| # | Improvement | Timeline | Complexity | Status |
|---|---|---|---|---|
| 2 | Codebase Health Dashboard | 3-4 days | Medium | Starting |
| 6 | Architecture Drift Detection | 5-7 days | Medium-High | Planned |
| 14 | Team Expertise Mapping | 2-3 days | Medium | Planned |

**Total Phase 2 Timeline:** 10-14 days (roughly 2-3 weeks)

---

## 🎯 Phase 2 Goals

### Primary Goals
1. **Establish quality metrics foundation** - Real-time visibility into codebase health
2. **Enforce architectural integrity** - Prevent design decay over time
3. **Map team knowledge** - Identify expertise distribution and knowledge gaps

### Business Impact
- 20-30% faster feature development by reducing technical friction
- Prevent "architectural drift" that causes monolith decay
- Reduce team bus factor risk by identifying knowledge gaps

### Success Metrics
- Health Dashboard displays within 5 seconds for 1000+ modules
- Architecture violations caught before code review (100% prevention)
- Team expertise map 90%+ accurate vs manual surveys

---

## 📦 Phase 2 Deliverables

### 1. Codebase Health Dashboard (#2) - Starting Now

**What's Included:**
```
agents/codebase_health_monitor.py          - Core health metrics engine
agents/health_dashboard_server.py           - FastAPI dashboard server
templates/health_dashboard.html             - Web UI for health metrics
docs/HEALTH_DASHBOARD_SETUP.md             - Setup instructions
```

**Key Metrics:**
- Overall health score (0-100)
- Complexity hotspots (>20 cyclomatic complexity)
- Circular dependencies count
- Test coverage trends (%)
- Dead code percentage
- Documentation coverage ratio
- Security issues count
- Performance concerns flagged

**API Endpoints:**
```
GET /api/health/summary                    # Overall health metrics
GET /api/health/modules                    # Per-module health scores
GET /api/health/trends                     # 30-day trend data
GET /api/health/recommendations            # Prioritized improvements
```

**Timeline:** 3-4 days
- Day 1: Metrics engine core functions
- Day 2: Analysis implementation & data aggregation
- Day 3: Dashboard server & API
- Day 4: UI refinement & performance optimization

---

### 2. Architecture Drift Detection (#6) - Following Health Dashboard

**What's Included:**
```
agents/architecture_validator.py           - Core drift validator
agents/architecture_rules_engine.py         - Rule definition & checking
config/architecture_rules.yaml              - Architectural rules
detectors/
  - circular_dependency_detector.py         - Detect cycles
  - cross_layer_detector.py                 - Detect layer violations
  - naming_convention_detector.py           - Check naming rules
  - dependency_cardinality_detector.py      - Check import patterns
docs/ARCHITECTURE_DRIFT_SETUP.md           - Setup & configuration
```

**Detectable Violations:**
- Circular dependencies (A→B→A)
- Cross-layer violations (UI directly accessing DB)
- Naming convention violations (expected patterns)
- Dependency cardinality issues (too many imports)
- Microservice isolation violations
- Deprecated component usage

**Configuration Example:**
```yaml
architecture_rules:
  layers:
    - name: api
      depends_on: [services]
    - name: services
      depends_on: [repositories]
    - name: repositories
      depends_on: [database]
  
  forbidden_patterns:
    - UI -> Database      # Must go through API
    - Payment -> Order    # Circular risk
  
  naming_conventions:
    services: "*Service.py"
    repositories: "*Repository.py"
```

**Timeline:** 5-7 days
- Day 1: Rule engine framework & YAML parsing
- Day 2-3: Individual detectors (circular, layers, naming, cardinality)
- Day 4: Integration & violation reporting
- Day 5-7: Testing, performance tuning, documentation

---

### 3. Team Expertise Mapping (#14) - Following Architecture Drift

**What's Included:**
```
agents/expertise_mapper.py                 - Core expertise analysis
agents/expertise_dashboard.py               - Expertise visualization
utils/git_history_analyzer.py              - Git commit analysis
templates/expertise_matrix.html             - Web UI for expertise
docs/EXPERTISE_MAPPING_SETUP.md            - Setup instructions
```

**Key Insights:**
- Primary code domains (where they contribute most)
- Language expertise distribution
- Code review quality metrics
- Mentorship relationships
- Knowledge gaps & single points of failure
- Team availability by domain

**Output Format:**
```json
{
  "alice": {
    "primary_domains": ["payment_service", "fraud_detection"],
    "languages": ["Python", "SQL"],
    "recent_changes": 127,
    "review_quality": 0.94,
    "mentorship_score": 0.87
  },
  "team_gaps": ["Kubernetes", "Frontend Performance"],
  "bus_factors": ["Charlie (payment_service)"],
  "mentoring_recommendations": [...]
}
```

**Timeline:** 2-3 days
- Day 1: Git history analyzer & change aggregation
- Day 2: Expertise metrics calculation & dashboard
- Day 3: Testing & refinement

---

## 🛠️ Implementation Order

```
Week 1:
├─ Mon: Phase 2 architecture planning + Codebase Health Dashboard setup
├─ Tue: Health Dashboard metrics implementations
├─ Wed: Health Dashboard API & dashboard UI
├─ Thu: Health Dashboard testing & optimization
└─ Fri: Health Dashboard integration testing

Week 2:
├─ Mon: Architecture Drift Detection setup & rule engine
├─ Tue: Circular dependency detector + layer violation detector
├─ Wed: Naming convention + cardinality detectors
├─ Thu: Integration & reporting
└─ Fri: Architecture validation testing

Week 3:
├─ Mon: Team Expertise Mapping setup
├─ Tue: Git history analysis & expertise calculation
├─ Wed: Dashboard UI & visualization
└─ Thu: Testing & refinement
```

---

## 📊 Integration Architecture

```
Cartographer MCP Server
├── Phase 1 Agents (Quick Wins)
│   ├── Selective Impact Analyzer (#1)
│   ├── Smart Diff Analyzer (#3)
│   └── Security Scanner (#7)
│
├── Phase 2 Agents (Foundation) ← YOU ARE HERE
│   ├── Codebase Health Monitor (#2)
│   ├── Architecture Validator (#6)
│   └── Expertise Mapper (#14)
│
├── Shared Utilities
│   ├── git_analyzer (efficient queries)
│   ├── metrics_calculator
│   ├── graph_builder
│   └── cache_manager
│
└── Data Layer
    ├── Neo4j (dependency graph)
    ├── Metrics cache (Redis/local)
    └── Git repository
```

---

## 🔧 Setup Instructions

### Prerequisites
- Python 3.8+
- Neo4j database (for dependency graph)
- Fast API for dashboard servers
- Git repository with commit history

### Installation
```bash
# 1. Install dependencies
pip install fastapi uvicorn networkx

# 2. Initialize Phase 2 components
python scripts/setup_phase2.py

# 3. Build codebase graph (if not already done)
python scripts/build_dependency_graph.py

# 4. Start Phase 2 services
python agents/codebase_health_monitor.py &
python agents/architecture_validator.py &
python agents/expertise_mapper.py &
```

### Configuration
```bash
# Copy config template
cp config/architecture_rules.yaml.example config/architecture_rules.yaml

# Customize your rules
nano config/architecture_rules.yaml

# Set environment variables
export CARTOGRAPHER_REPO_PATH=/path/to/repo
export CARTOGRAPHER_NEO4J_URL=bolt://localhost:7687
export CARTOGRAPHER_CACHE_TYPE=redis  # or local
```

---

## 📈 Success Criteria

### Health Dashboard
- ✅ Generates report for 1000+ modules in <5 seconds
- ✅ Identifies all hotspots with >20 complexity
- ✅ Tracks trends across 30-day window
- ✅ Provides actionable recommendations

### Architecture Drift Detection
- ✅ Detects 100% of circular dependencies
- ✅ Catches layer violations immediately
- ✅ Identifies all naming convention violations
- ✅ Pre-commit hook integration working

### Team Expertise Mapping
- ✅ Maps expertise for all team members
- ✅ Identifies single points of failure
- ✅ Generates mentoring recommendations
- ✅ 90%+ accuracy vs manual surveys

---

## ⚠️ Common Challenges & Solutions

### Challenge 1: Health Dashboard Performance
**Problem:** Calculating metrics for 1000+ modules takes too long
**Solution:** 
- Cache metrics results (1-hour TTL)
- Implement incremental metric calculation
- Use Neo4j native query functions for graph analysis

### Challenge 2: Architecture Rules Complexity
**Problem:** Rules keep growing, becoming hard to maintain
**Solution:**
- Start with 5-10 core rules
- Use composable rule engine
- Version rules alongside release cycles

### Challenge 3: Expertise Map Accuracy
**Problem:** Git history doesn't capture current expertise
**Solution:**
- Combine git history with code review data
- Include self-reported expertise surveys
- Track skill decay (no commits in 6 months = lower weight)

---

## 🚀 Next Steps (Phase 3 Preview)

After Phase 2 completion, Phase 3 will add:
- **#4 Multi-Language Support** (JavaScript, TypeScript, Go, Rust, C#)
- **#13 Performance Profiling & Optimization**
- **#16 ML-Based Code Quality Predictor**

---

## 📊 ROI Timeline

```
Phase 2 Investment: 10-14 days
Phase 2 Benefits:
- Month 1: Setup, learning curve (0% benefit)
- Month 2: Team adoption, initial insights (20% benefit)
- Month 3: Actionable metrics, prevented issues (60% benefit)
- Month 4+: Regular dashboard usage, prevented bugs (80-90% benefit)

Estimated ROI:
- Bugs prevented: 10-15 per quarter
- Development time saved: 50-100 hours per quarter
- Technical debt reduction: 20-30% faster deployments
```

---

## 📞 Support & Questions

**Q: Should we complete all three Phase 2 improvements in parallel?**
A: No - implement sequentially: Health Dashboard → Architecture Drift → Expertise Mapping. 
Each builds on previous insights, and sequential implementation reduces risk.

**Q: What if our architecture rules are unclear?**
A: Start with basic rules (no circular dependencies, layer violations). Expand iteratively
based on team feedback after 1-2 weeks of usage.

**Q: Can we skip Team Expertise Mapping?**
A: Recommended to complete all three. Team expertise is critical for mentorship and 
succession planning, especially in growing teams.

---

**Status:** Ready to begin
**Last Updated:** March 11, 2026
**Next Review:** After Health Dashboard completion
