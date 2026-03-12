# Phase 1 Integration Architecture

**Document Type:** Technical Architecture  
**Audience:** Developers, DevOps, Tech Leads  
**Complexity:** Intermediate

---

## 🏛️ System Architecture

### Agent Integration Model
```
┌─────────────────────────────────────────────────────────┐
│                  Development Workflow                    │
└─────────────────────────────────────────────────────────┘
                            ▼
    ┌───────────────────────────────────────────────┐
    │         Developer Makes Code Change          │
    └───────────────────────────────────────────────┘
                            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │  PHASE 1 AGENTS (Pre-PR/Pre-Commit Analysis)               │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  1. Selective Impact Analyzer                              │
    │     ├─ Scans dependency graph                              │
    │     ├─ Maps to business processes                          │
    │     └─ Estimates testing effort                            │
    │                ▼                                           │
    │  2. Smart Diff Analyzer                                    │
    │     ├─ Analyzes specific PR changes                        │
    │     ├─ Suggests reviewers                                  │
    │     └─ Identifies concerns                                 │
    │                ▼                                           │
    │  3. Security Scanner                                       │
    │     ├─ Detects vulnerabilities                             │
    │     ├─ Finds exposed secrets                               │
    │     └─ Checks compliance                                   │
    └─────────────────────────────────────────────────────────────┘
                            ▼
    ┌─────────────────────────────────────────────┐
    │  Aggregated Reports                         │
    │  ├─ Impact Assessment                       │
    │  ├─ Review Recommendations                  │
    │  └─ Security Status                         │
    └─────────────────────────────────────────────┘
                            ▼
    ┌─────────────────────────────────────────────┐
    │  Decision Point                             │
    │  ├─ Risk LOW? → Fast-track review           │
    │  ├─ Risk HIGH? → Schedule meeting           │
    │  └─ Security issues? → Fix before PR        │
    └─────────────────────────────────────────────┘
                            ▼
    ┌───────────────────────────────────────────────┐
    │  Submit PR with Contextual Metadata          │
    └───────────────────────────────────────────────┘
```

---

## 📦 Component Architecture

### Dependency Map
```
smart_diff_analyzer.py
├─ Scans git diff
├─ Analyzes files modified
├─ Maps to business impacts
└─ Suggests reviewers from expertise_map

selective_impact_analyzer.py
├─ Builds dependency graph
├─ Finds direct dependents
├─ Finds transitive dependents (BFS)
├─ Maps to business processes
└─ Estimates test effort

security_compliance_scanner.py
├─ Scans all Python files
├─ Pattern matches for vulnerabilities
├─ Detects secrets
├─ Checks encryption
└─ Validates compliance rules

External Dependencies:
├─ subprocess (for git commands)
├─ os (file system access)
├─ ast (Python parsing)
├─ re (regex patterns)
└─ json (output formatting)
```

### Data Flow
```
Repository Structure
    ▼
┌─ Selective Impact Analyzer
│  └─ Dependency Graph
│     └─ Impact Analysis
│        └─ Business Mapping
│           ▼
│        Impact Report

┌─ Smart Diff Analyzer
│  └─ Git Diff
│     └─ Changed Files
│        └─ File Analysis
│           └─ Reviewer Mapping
│              ▼
│           Diff Report

┌─ Security Scanner
│  └─ File Content
│     └─ Pattern Matching
│        └─ Secret Detection
│           └─ Compliance Check
│              ▼
│           Security Report

All Reports
    ▼
Aggregated Analysis
    ▼
Dashboard / CI-CD
```

---

## 🔗 Integration Points

### 1. Version Control Integration

```python
# Pre-commit hook
#!/usr/bin/env python3
import subprocess
from agents.security_compliance_scanner import SecurityComplianceScanner

scanner = SecurityComplianceScanner(".")
result = scanner.scan_codebase()

if result.overall_status == "CRITICAL":
    print("❌ Critical security issues. Commit blocked.")
    exit(1)
```

### 2. CI/CD Pipeline Integration

```yaml
# GitHub Actions Example
jobs:
  analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      
      - name: Impact Analysis
        run: python agents/selective_impact_analyzer.py > impact.txt
      
      - name: Diff Analysis
        run: python agents/smart_diff_analyzer.py > diff.txt
      
      - name: Security Scan
        run: python agents/security_compliance_scanner.py > security.txt
      
      - name: Post Results to PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const body = `## Analysis Results\n\n${fs.readFileSync('impact.txt')}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### 3. IDE Integration

```python
# VSCode extension hook
class CodeAnalysisProvider:
    def analyze_on_save(self):
        from agents.selective_impact_analyzer import SelectiveImpactAnalyzer
        analyzer = SelectiveImpactAnalyzer(".")
        result = analyzer.analyze_change_impact(self.current_file)
        return self.show_diagnostics(result)
```

### 4. MCP Server Integration

```python
# Extend mcp_cartographer_server.py
from agents.smart_diff_analyzer import SmartDiffAnalyzer
from agents.selective_impact_analyzer import SelectiveImpactAnalyzer

class EnhancedCartographerServer:
    def __init__(self):
        self.diff_analyzer = SmartDiffAnalyzer(".")
        self.impact_analyzer = SelectiveImpactAnalyzer(".")
    
    def analyze_change(self, file_path):
        """Unified change analysis endpoint"""
        impact = self.impact_analyzer.analyze_change_impact(file_path)
        # Return combined results
        return {
            'impact': impact,
            'risk_score': self.calculate_risk(impact)
        }
```

---

## 📋 Workflow Examples

### Example 1: Pre-PR Validation

```python
#!/usr/bin/env python3
"""Validate changes before PR submission"""

import sys
from agents.selective_impact_analyzer import SelectiveImpactAnalyzer
from agents.smart_diff_analyzer import SmartDiffAnalyzer
from agents.security_compliance_scanner import SecurityComplianceScanner

def validate_changes():
    repo = "."
    
    # 1. Check impact
    print("🔍 Analyzing change impact...")
    impact_analyzer = SelectiveImpactAnalyzer(repo)
    result = impact_analyzer.analyze_change_impact("src/app.py")
    
    if result.risk_level == "CRITICAL":
        print(f"⚠️  WARNING: High-risk change detected")
        print(f"   Affected teams: {result.affected_teams}")
        print(f"   Schedule review meeting before PR")
    
    # 2. Check security
    print("\n🔐 Running security scan...")
    scanner = SecurityComplianceScanner(repo)
    security_result = scanner.scan_codebase()
    
    if security_result.overall_status == "CRITICAL":
        print(f"❌ CRITICAL SECURITY ISSUES FOUND")
        print(f"   Fix before any commit")
        return False
    
    # 3. Prepare diff analysis
    print("\n📝 Analyzing diffs for PR...")
    diff_analyzer = SmartDiffAnalyzer(repo)
    diff_result = diff_analyzer.analyze_pr_changes("main..current")
    
    print(f"\n✅ Pre-PR validation complete")
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Test Time: {result.estimated_test_time_hours:.1f} hours")
    print(f"   Suggested Reviewers: {[r.name for r in diff_result.suggested_reviewers]}")
    
    return True

if __name__ == "__main__":
    if not validate_changes():
        sys.exit(1)
```

### Example 2: Continuous Monitoring

```python
#!/usr/bin/env python3
"""Continuous monitoring of codebase health"""

import time
import json
from datetime import datetime
from agents.security_compliance_scanner import SecurityComplianceScanner

def monitor_security():
    scanner = SecurityComplianceScanner(".")
    
    history = []
    
    while True:
        result = scanner.scan_codebase()
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'status': result.overall_status,
            'risk_score': result.risk_score,
            'security_issues': len(result.security_issues),
            'compliance_issues': len(result.compliance_issues),
        }
        history.append(entry)
        
        # Alert if risk increased
        if len(history) > 1 and entry['risk_score'] > history[-2]['risk_score']:
            print(f"🚨 Risk score increased from {history[-2]['risk_score']:.1f} to {entry['risk_score']:.1f}")
        
        # Save history
        with open('security_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"Scan complete at {entry['timestamp']}: {entry['status']}")
        
        # Run daily
        time.sleep(86400)

if __name__ == "__main__":
    monitor_security()
```

---

## 🔌 Extension Points

### Custom Business Mapping

```python
from agents.selective_impact_analyzer import SelectiveImpactAnalyzer

class CustomImpactAnalyzer(SelectiveImpactAnalyzer):
    def _initialize_business_map(self):
        # Override with your company's business domains
        return {
            'agents.payment': ['Payments', 'Billing', 'Invoicing'],
            'agents.order': ['Orders', 'Fulfillment', 'Shipping'],
            'agents.auth': ['Authentication', 'Authorization', 'SSO'],
            # ... add more
        }
```

### Custom Vulnerability Patterns

```python
from agents.security_compliance_scanner import SecurityComplianceScanner

class CompanySecurityScanner(SecurityComplianceScanner):
    def _initialize_vulnerability_patterns(self):
        patterns = super()._initialize_vulnerability_patterns()
        
        # Add company-specific patterns
        patterns.append({
            'type': 'company_api_misuse',
            'pattern': r'direct_db_access\(\)',  # Company-specific anti-pattern
            'severity': SeverityLevel.HIGH,
            'description': 'Must use API layer, not direct DB access',
            'remediation': 'Route through company API service'
        })
        
        return patterns
```

### Custom Approval Requirements

```python
from agents.smart_diff_analyzer import SmartDiffAnalyzer

class CompanyDiffAnalyzer(SmartDiffAnalyzer):
    def _determine_approval_requirements(self, concerns, files):
        requirements = super()._determine_approval_requirements(concerns, files)
        
        # Company-specific requirements
        if any('compliance' in f.lower() for f in files):
            requirements['legal_review'] = True
        
        if any('privacy' in f.lower() for f in files):
            requirements['privacy_office'] = True
        
        return requirements
```

---

## 📊 Metrics & Monitoring

### Key Metrics to Track

```python
class Analytics:
    metrics = {
        'avg_review_time': 'Average time from PR to merge',
        'bugs_caught_pre_review': 'Issues found by Smart Diff',
        'security_issues_found': 'Security issues caught before prod',
        'test_time_accuracy': 'How accurate are time estimates',
        'reviewer_effectiveness': 'Quality of suggested reviewers',
        'false_positive_rate': 'Security scan false positives',
        'adoption_rate': 'Team adoption of tools',
    }
```

### Reporting Dashboard

```python
# Generate weekly report
def generate_weekly_report():
    return {
        'period': 'Week of 2026-03-08',
        'prs_analyzed': 24,
        'bugs_prevented': 12,
        'security_issues_caught': 3,
        'average_review_time': '2.3 hours',
        'adoption_rate': '95%',
        'top_risk_modules': ['payment_service', 'auth'],
    }
```

---

## 🚀 Deployment Checklist

- [ ] All three agents installed in `agents/` directory
- [ ] No Python dependency conflicts
- [ ] Git access verified for diff analysis
- [ ] File system access permissions configured
- [ ] Business mapping customized for your company
- [ ] Security patterns reviewed and validated
- [ ] CI/CD pipeline integration tested
- [ ] Pre-commit hooks configured
- [ ] Team trained on interpretation
- [ ] Metrics baseline established
- [ ] Runbook created for common issues
- [ ] Escalation path defined

---

## 🔍 Monitoring & Debugging

### Debug Mode
```python
import logging

logging.basicConfig(level=logging.DEBUG)

from agents.selective_impact_analyzer import SelectiveImpactAnalyzer

analyzer = SelectiveImpactAnalyzer("/repo")
result = analyzer.analyze_change_impact("file.py")
# Detailed logs show dependency resolution steps
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No dependents found | Import statements not detected | Check AST parsing compatibility |
| Slow analysis | Large codebase | Use selective scanning on subdirectories |
| Security false positives | Pattern too broad | Refine regex patterns |
| Business mapping outdated | Code structure changed | Update mapping in initialization |

---

## 📚 Documentation References

- [PHASE_1_IMPLEMENTATION_SUMMARY.md](PHASE_1_IMPLEMENTATION_SUMMARY.md) - Implementation details
- [PHASE_1_QUICK_START.md](PHASE_1_QUICK_START.md) - Usage guide
- [IMPROVEMENTS_INDEX.md](IMPROVEMENTS_INDEX.md) - High-level overview
- [IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md](IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md) - Detailed analysis

---

*Next: Phase 2 integration planning*
