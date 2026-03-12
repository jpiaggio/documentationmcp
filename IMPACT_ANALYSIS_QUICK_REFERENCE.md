# Impact Analysis Quick Reference Guide

## 🎯 For Lead Engineers

### **If you're making architectural decisions:**

| Decision | Impact to Assess | Tool | Time |
|----------|-----------------|------|------|
| Add new dependency | Will it create circular deps? | #6 Architecture Drift Detector | 5 min |
| Refactor module | What breaks downstream? | #1 Selective Impact Analysis | 10 min |
| Change API | Who integrates with this? | #11 API Compatibility Checker | 5 min |
| Optimize service | How much will this cost? | #13 Performance Profiler + #15 Cost Attribution | 15 min |

### **If you're planning sprints:**

- Use #2 (Health Dashboard) → Identify technical debt hotspots
- Use #5 (Refactoring Recommendations) → Prioritize which modules to refactor
- Use #9 (Test Gap Analyzer) → Know which tests to write
- Use #14 (Team Expertise) → Assign tasks to right people

### **If you're worried about reliability:**

- Use #6 (Architecture Drift) → Prevent illegal dependencies
- Use #7 (Security Scanning) → Catch vulnerabilities early
- Use #3 (Smart Diffs) → Understand PR risk before merge
- Use #18 (Vulnerability Mgmt) → Keep dependencies safe

---

## 🎯 For Software Developers

### **When you start a new task:**

1. **Understand impact** (5 min):
   ```
   Run Selective Impact Analysis on the file you'll modify
   → Learn which modules depend on your changes
   → Understand test complexity needed
   ```

2. **Plan reviewers** (2 min):
   ```
   Run Smart Diff Analysis
   → Get suggested reviewers based on expertise
   → Know which tests will be affected
   ```

3. **Write code with confidence** (ongoing):
   ```
   Get real-time feedback on:
   → Circular dependencies created
   → Performance impact
   → Test coverage gaps
   ```

### **Before submitting PR:**

- [ ] Smart Diff Analysis completed (suggests reviewers)
- [ ] Impact Analysis done (you know downstream effects)
- [ ] Security scan passes (no exposed secrets)
- [ ] Architecture Drift check clean (no illegal dependencies)

### **Code review feedback you want:**

From #3 (Smart Diff Analysis):
- ✅ Should have automated test suggestions
- ✅ Should identify circular dependencies
- ✅ Should suggest specific code reviewers
- ✅ Should estimate review time

---

## 🎯 For Product Directors

### **Strategic Questions Asked Daily:**

| Question | Use This | Instantly Know |
|----------|----------|---|
| Can we release this feature? | #3 Smart Diffs + #7 Security | Risk level, review time |
| How much will this cost to build? | #19 Feature Cost Estimator | Dev time + infrastructure cost |
| What's draining our budget? | #15 Cost Attribution | Which services cost most |
| Are we adding technical debt? | #2 Health Dashboard | Technical debt trend |
| Will this break customer experience? | #1 Impact Analysis | Affected customer journeys |
| How quickly can we pivot? | #6 Architecture Drift | Architectural flexibility |
| Can we maintain this in 12 months? | #20 Continuous Monitoring | Architecture health trend |

### **Three KPIs you should track:**

1. **Code Quality Score** (from #2 Dashboard)
   - Target: 75+ / 100
   - Trend: Improving 2-3 points/quarter

2. **Mean Time to Deploy** (from #3 Smart Diffs)
   - Current: 4 hours
   - Target: 1 hour (with better impact analysis)

3. **Production Incidents from Code** (from #7 Security + #16 ML Predictor)
   - Current: 2 per month
   - Target: 0.5 per month

### **Questions to ask your Tech Lead:**

1. "Are we tracking architecture drift?" → See #6
2. "Can we predict code quality issues?" → See #16
3. "Which modules are slowing us down?" → See #13
4. "Do we have single points of failure?" → See #14

---

## ⚡ Git Communication: 30-Second Version

When analyzing code in 800+ module codebase:

### **DO:**
- ✅ `git diff --name-only main..feature` (changed files, not full code)
- ✅ Cache previous analysis results (1 hour TTL)
- ✅ Use parallel processing (8 cores, 100 modules each)
- ✅ Tag releases (`git tag v2.0.0`)

### **DON'T:**
- ❌ Clone entire repo history (use `--depth 10`)
- ❌ Query git for each module individually
- ❌ Analyze all 800 modules every run
- ❌ Keep full code in memory (signatures + docstrings only)

### **Example: Fast PR Analysis**

```bash
#!/bin/bash
# < 5 seconds for any PR

git diff --stat main..feature-branch  # What changed (1 sec)
git diff --name-only main..feature-branch | grep -E "(payment|security|auth)" # Risk areas (1 sec)
git log main..feature-branch --oneline | grep "!" # Breaking changes (1 sec)
# Instant summary with NO deep analysis needed
```

---

## 📊 Pick Your First Improvement

**The Perfect First Choice:**

- **You're managing code quality?** → Start with #2 (Health Dashboard) + #3 (Smart Diffs)
- **You worry about bugs?** → Start with #7 (Security) + #6 (Architecture)
- **You want faster deploys?** → Start with #3 (Smart Diffs) + #1 (Impact Analysis)
- **You track costs?** → Start with #15 (Cost Attribution) + #13 (Performance)
- **You're onboarding people?** → Start with #14 (Expertise Mapping) + #8 (Documentation Sync)

---

## 🎓 Using Impact Analysis Framework (2-minute version)

When proposing ANY change, ask:

```
POSITIVE IMPACTS:
- Performance: From X to Y (% improvement)
- Scale: Can handle N% more load
- Cost: Saves $X/month

NEGATIVE IMPACTS & RISKS:
- Risk: What could go wrong?
- Mitigation: How do we prevent it?
- Effort: How much to mitigate?

CASCADING IMPACTS:
- Direct: This change
- First order: What else is affected
- Business: How does this reach customers?

STAKEHOLDERS:
- Who wins / who loses?
- What's the sentiment risk?

TIMELINE:
- Phase 1, 2, 3... (phased rollout)
- Rollback plan (can we undo?)

METRICS:
- How do we know if it worked?
```

**Example: 2-minute assessment of "refactor auth service":**

```
POSITIVE: Faster login (200ms → 100ms), better security
NEGATIVE: Risk of auth failures during rollout (mitigated by canary)
CASCADE: Better login → higher signup → more revenue
STAKEHOLDERS: Customers win, ops team gets new things to monitor
TIMELINE: 3 weeks, canary rollout
METRICS: Login latency, auth error rate, signup rate
```

---

## 🚀 Implementation Timeline

### Week 1: Understand Your Baseline
- Get Health Dashboard running → Know current state
- Run impact analysis on last 5 PRs → Understand risk patterns

### Week 2-3: Implement Smart Diffs
- Show reviewers automatically
- Identify affected modules automatically
- 50% reduction in review time

### Month 2: Add Security Scanning
- Catch vulnerabilities before production
- Know about dependencies automatically
- Compliance audit prep

### Month 3+: Scale with Advanced Features
- Architecture drift detection
- Performance optimization
- Cost attribution

---

## 📞 Decision Maker's Cheat Sheet

❓ **When someone says "let's refactor X":**
- Ask: "What impact analysis did you run?"
- Tool: #1 Selective Impact Analysis
- Question: "Will this affect customer journeys?"

❓ **When you see code coverage is 60%:**
- Ask: "Which modules are critical and undertested?"
- Tool: #9 Test Gap Analyzer
- Question: "What's our risk if payment service fails?"

❓ **When infrastructure costs spike:**
- Ask: "Which service caused this?"
- Tool: #15 Cost Attribution by Module
- Question: "Can we optimize or should we accept the cost?"

❓ **When deployment takes 4 hours:**
- Ask: "Which PRs have highest risk?"
- Tool: #3 Smart Diff Analysis
- Question: "Can we parallelize reviews?"

❓ **When senior engineer wants to leave:**
- Ask: "Does anyone else understand their modules?"
- Tool: #14 Team Expertise Mapping
- Question: "Do we have single points of failure?"

---

## ✅ Success Metric Examples

### For Engineering Teams
- **Code Review Time**: 120 min → 30 min (with #3)
- **Bug Escape Rate**: 2 per month → 0.5 per month (with #7 + #16)
- **Architecture Violations**: 12 per quarter → 0 (with #6)
- **Technical Debt**: Growing 5% per quarter → Shrinking 3% per quarter (with #2)

### For Product Teams
- **Feature Delivery Time**: 3 months → 1 month (with better planning)
- **Confidence in Deployment**: 70% → 95% (with impact analysis)
- **Customer-Impacting Incidents**: 2 per month → 0.2 per month
- **Team Velocity**: +20-30% (with #14 better task assignment)

### For Finance
- **Infrastructure Costs**: $45K/month → $35K/month (with #13 + #15)
- **Developer Productivity**: +25% (less firefighting)
- **Cost per Feature**: $8K → $5K (faster dev cycle)

---

**For detailed information, see:** [IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md](IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md)
