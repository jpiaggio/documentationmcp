# Security & Compliance Scanning System

## Overview

A comprehensive, production-ready security and compliance scanning framework that detects vulnerabilities and ensures regulatory compliance in codebases.

## ✨ Key Features

### 1. **SQL Injection Detection** 🛡️
- Identifies unparameterized SQL queries
- Detects string concatenation with user input
- Supports Python, Java, JavaScript analysis
- CWE-89 tracking

```python
# ❌ Vulnerable
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

# ✅ Safe
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 2. **XSS (Cross-Site Scripting) Detection** 🔗
- Detects unescaped template variables
- Identifies innerHTML assignments with user input
- React dangerouslySetInnerHTML detection
- CWE-79 tracking

```javascript
// ❌ Vulnerable
element.innerHTML = userInput;

// ✅ Safe
element.textContent = userInput;  // Safe - text only
element.innerHTML = DOMPurify.sanitize(userInput);  // HTML sanitized
```

### 3. **Exposed Credential Scanning** 🔑
- **API Keys**: AWS, Stripe, GitHub tokens
- **Passwords**: Hardcoded database passwords
- **Private Keys**: SSH, RSA, PGP keys
- **Tokens**: JWT, Slack, Discord tokens
- **Environment Variables**: Sensitive env var detection
- **Git History**: Recent commits (configurable depth)
- **Config Files**: .env, YAML, JSON, TOML files

Detects:
- AWS Access/Secret Keys
- API Keys (patterns: sk_live, pk_live, ghp_)
- Passwords and authentication strings
- SSH/Private Keys
- JWT Tokens
- Database connection strings

### 4. **GDPR Compliance Checking** 📋
Articles checked:
- Article 5: Data Minimization & Accountability
- Article 7: Conditions for Consent
- Article 17: Right to Erasure
- Article 32: Security of Processing

Detects:
- Unencrypted personal data storage
- Missing consent mechanisms
- Missing data deletion functionality
- Indefinite data retention
- Missing audit logging for data access

### 5. **HIPAA Compliance Checking** 🏥
Technical & Administrative Safeguards:
- Unencrypted Protected Health Information (PHI)
- Missing access controls
- Unencrypted PHI transmission
- Missing audit logs for PHI access
- Patient data exposure risks

### 6. **Risk Scoring Engine** 📊
- **Overall Risk Score**: 0-100 scale
- **Risk Levels**: CRITICAL, HIGH, MEDIUM, LOW, INFO
- **Metrics**: Vulnerability counts, density, CWE distribution
- **Confidence Scoring**: Per-finding confidence adjustment
- **Compliance Tracking**: Framework-specific violation counts

### 7. **Multi-Format Report Generation** 📈
- **JSON**: Machine-readable detailed findings
- **HTML**: Interactive dashboard with styling
- **SARIF**: Standard Analysis Results Format for CI/CD integration

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from security.orchestrator import SecurityOrchestrator

# Create scanner for your workspace
scanner = SecurityOrchestrator(Path("/path/to/project"))

# Run scan
assessment = scanner.scan(
    included_paths=[Path("src"), Path("lib")],
    excluded_paths=[Path(".venv"), Path("node_modules")],
    check_env_files=True,
    check_config_files=True,
    scan_git_history=True,
)

# Generate reports
reports = scanner.generate_reports(
    Path("./security_reports"),
    formats=["json", "html", "sarif"]
)

# View results
print(f"Risk Level: {assessment.overall_risk_level}")
print(f"Risk Score: {assessment.risk_score}/100")
print(f"Vulnerabilities: {assessment.critical_count} Critical, {assessment.high_count} High")
```

### Demo Script

```bash
python3 security_scanner_demo.py
```

## 📦 Architecture

### Module Structure

```
security/
├── __init__.py                 # Main exports
├── orchestrator.py             # Main entry point
├── core/
│   ├── vulnerability.py        # Data models
│   └── scanner.py              # Base scanner & registry
├── detectors/
│   ├── sql_injection.py       # SQL injection scanner
│   ├── xss.py                 # XSS vulnerability scanner
│   ├── credentials.py         # Credential exposure scanner
│   └── compliance.py          # GDPR/HIPAA compliance
├── risk/
│   └── risk_engine.py         # Risk scoring & assessment
└── reporters/
    ├── json_reporter.py       # JSON output
    ├── html_reporter.py       # HTML dashboard
    └── sarif_reporter.py      # SARIF standard format
```

### Scanner Plugin Architecture

New scanners can be added by:

```python
from security.core.scanner import BaseScanner, SecurityContext

class CustomScanner(BaseScanner):
    def get_scanner_name(self) -> str:
        return "Custom Scanner"
    
    def get_scanner_description(self) -> str:
        return "Description of what this scanner does"
    
    def scan(self) -> List[VulnerabilityFinding]:
        # Implement your scanning logic
        pass

# Register with orchestrator
orchestrator.registry.register("custom", CustomScanner)
```

## 🎯 Scanner Details

### SQL Injection Scanner

**Patterns Detected:**
- String concatenation: `execute("SELECT * FROM users WHERE id = " + user_id)`
- f-strings: `execute(f"SELECT * FROM {table_name}")`
- Format strings: `execute("SELECT * FROM {}".format(user_input))`
- % formatting: `execute("SELECT * FROM users WHERE id = %s" % user_id)`

**Language Support:** Python, Java, JavaScript

**CWE:** CWE-89

### XSS Scanner

**Patterns Detected:**
- innerHTML assignments: `element.innerHTML = userInput`
- Template literals: `` element.innerHTML = `<div>${userInput}</div>` ``
- dangerouslySetInnerHTML: `<div dangerouslySetInnerHTML={{__html: userInput}} />`
- jQuery html(): `$('#element').html(userInput)`

**Language Support:** JavaScript, Python (templates), Java (JSP)

**CWE:** CWE-79

### Credential Scanner

**Detection Methods:**
1. **Pattern Matching**
   - AWS keys, API keys, tokens
   - Passwords and secrets
   - Private key headers

2. **Environment Variables**
   - Scans running environment
   - Detects sensitive env vars

3. **File Scanning**
   - Source code files
   - Config files (.env, .yaml, .json)
   - Git history (recent commits)

**False Positive Handling:**
- Skips demo/test/placeholder values
- Excludes common variable names
- Reduces false positives through confidence scoring

### Compliance Scanner

**GDPR Checks:**
- Unencrypted personal data
- Missing consent mechanisms
- Missing right to erasure
- Indefinite retention
- Unaudited access

**HIPAA Checks:**
- Unencrypted PHI
- Missing access controls
- Unencrypted transmission
- Missing audit logs

**Data Categories Tracked:**
- Personal identifiers (email, phone, SSN)
- Biometric data
- Health/medical information
- Location data
- Race/ethnicity/religion

## 📊 Risk Assessment

### Risk Scoring Formula

```
Risk Score = (Σ findings × severity_weight × vulnerability_multiplier × confidence) / total_findings

Severity Weights:
  CRITICAL: 100
  HIGH: 50
  MEDIUM: 25
  LOW: 10
  INFO: 5

Vulnerability Multipliers:
  SQL Injection: 1.5x
  XSS: 1.4x
  Exposed Credentials: 1.6-1.8x
  GDPR/HIPAA Violations: 1.5-1.7x
```

### Risk Levels

| Level | Score | Action |
|-------|-------|--------|
| CRITICAL | 80-100 | Stop deployment, immediate action |
| HIGH | 60-79 | Fix before production |
| MEDIUM | 40-59 | Address in near term |
| LOW | 20-39 | Schedule fixes |
| INFO | 0-19 | Monitor |

## 🔧 Configuration

### SecurityContext Options

```python
from security.core.scanner import SecurityContext

context = SecurityContext(
    workspace_root=Path("/project"),
    included_paths=[Path("src")],           # Paths to scan
    excluded_paths=[Path(".venv")],         # Paths to skip
    language_hints=["python", "java"],      # Languages to detect
    max_file_size=1_000_000,                # Max file size (1MB)
    follow_symlinks=False,                  # Follow symlinks
    scan_git_history=True,                  # Scan git commits
    git_depth=50,                           # Number of commits
    check_env_files=True,                   # Scan .env files
    check_config_files=True,                # Scan config files
    verbose=False,                          # Verbose logging
)
```

## 📈 Output Formats

### JSON Report
```json
{
  "metadata": {
    "timestamp": "2026-03-12T10:30:00",
    "scan_duration_seconds": 12.5,
    "scanned_files": 150
  },
  "summary": {
    "overall_risk_level": "HIGH",
    "risk_score": 72.5,
    "summary_text": "..."
  },
  "vulnerabilities": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "findings": [...]
  },
  "compliance": {
    "total_violations": 3,
    "violations": [...]
  }
}
```

### HTML Dashboard
- Interactive vulnerability browser
- Severity-based filtering
- Details and remediation steps
- Risk metrics visualization
- Compliance violation summaries

### SARIF Format
- Standard Analysis Results Format
- CI/CD pipeline integration
- GitHub code scanning support
- OASIS standard compliance

## 🔐 Security & Privacy

### What We Don't Store
- Actual credential values (redacted in reports)
- Personal data content (only metadata flagged)
- Application source code beyond findings

### Data Handling
- In-memory processing only
- Findings stored in assessment objects
- Reports written to specified output directory
- No external API calls or telemetry

## 🧪 Testing

### Run Demo

```bash
cd /path/to/documentationmcp
python3 security_scanner_demo.py
```

### Test on Sample Code

The demo script includes sample vulnerable code patterns. Results will show:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Exposed credentials (if .env files exist)
- GDPR/HIPAA compliance issues

## 📚 Report Generation

### Generate All Reports

```python
scanner = SecurityOrchestrator(Path.cwd())
assessment = scanner.scan()
reports = scanner.generate_reports(
    Path("./reports"),
    formats=["json", "html", "sarif"]
)

# Open HTML report
import webbrowser
webbrowser.open(str(reports["html"]))
```

### CI/CD Integration (SARIF)

```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    python3 security_scanner_demo.py
    
- name: Upload to Code Scanning
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: './security_reports/security_report.sarif'
```

## 🛠️ Extension Points

### Custom Detectors

```python
from security.core.scanner import BaseScanner, SecurityContext
from security.core.vulnerability import VulnerabilityFinding, Severity, Location

class InsecureCryptoScanner(BaseScanner):
    def scan(self):
        # Your detection logic
        pass
```

### Custom Risk Calculations

```python
from security.risk.risk_engine import RiskScoringEngine

engine = RiskScoringEngine()
engine.SEVERITY_WEIGHTS[Severity.CRITICAL] = 150  # Custom weight
```

## 📖 Reading Reports

### Vulnerability Fields

- **ID**: Unique identifier
- **Type**: SQL Injection, XSS, Credentials, etc.
- **Severity**: CRITICAL, HIGH, MEDIUM, LOW, INFO
- **Location**: File path and line number
- **CWE**: Common Weakness Enumeration
- **CVSS**: CVSS score (where applicable)
- **Confidence**: Detection confidence (0-100%)
- **Remediation**: Step-by-step fix instructions

### Compliance Violation Fields

- **Framework**: GDPR, HIPAA, PCI-DSS, etc.
- **Requirement**: Specific regulation/article
- **Affected Locations**: All locations violating the requirement
- **Data Categories**: Types of data affected
- **Remediation Steps**: Compliance fix steps

## 🚀 Next Steps

1. **Integrate into CI/CD**: Run on every commit in GitHub Actions, GitLab CI, etc.
2. **Set Baseline**: Establish expected risk level for your project
3. **Regular Reviews**: Schedule weekly/monthly security assessments
4. **Remediation Tracking**: Create issues for findings
5. **Policy Updates**: Update security policies based on findings

## 📞 Support

For issues or questions:
- Review detailed findings in generated HTML reports
- Check remediation steps in JSON reports
- Consult CWE/OWASP resources for vulnerability details

---

**Version**: 1.0.0
**Last Updated**: March 2026
