# Security & Compliance Scanner - Quick Reference

## 🎯 One-Minute Overview

A comprehensive security scanner that detects:
- SQL injection & XSS vulnerabilities
- Exposed credentials (API keys, passwords, tokens)
- GDPR violations (unencrypted data, missing consent)
- HIPAA violations (unencrypted PHI, access controls)
- Risk scoring (0-100) with automated recommendations

## 📍 File Locations

```
security/
├── core/              # Base classes & data models
├── detectors/         # SQL, XSS, Credentials, Compliance scanners
├── reporters/         # JSON, HTML, SARIF report generators
└── risk/              # Risk scoring engine
```

## 🚀 Quick Start (30 seconds)

```python
from pathlib import Path
from security.orchestrator import SecurityOrchestrator

# Scan your project
scanner = SecurityOrchestrator(Path.cwd())
assessment = scanner.scan()

# Generate reports
scanner.generate_reports(Path("./reports"))

# Print results
print(f"Risk: {assessment.overall_risk_level}")
print(f"Score: {assessment.risk_score}/100")
```

Or run the demo:
```bash
python3 security_scanner_demo.py
```

## 📊 What Gets Detected

### SQL Injection (CWE-89)
```python
# ❌ VULNERABLE
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
```

### XSS (CWE-79)
```javascript
// ❌ VULNERABLE
element.innerHTML = userInput;
```

### Exposed Credentials
```text
❌ Found in source code:
  - API_KEY = 'sk_live_abc123'
  - password = 'secret123'
  - SSH private key
  - JWT tokens
```

### GDPR Violations
```text
❌ Unencrypted personal data
❌ No consent mechanism
❌ No data deletion
❌ Indefinite retention
```

### HIPAA Violations
```text
❌ Unencrypted PHI
❌ No access control
❌ HTTP instead of HTTPS
❌ No audit logs
```

## 🔍 Scanner Methods

### 1. SQL Injection Detection
- Language: Python, Java, JavaScript
- Detects: String concatenation, f-strings, % formatting
- Severity: CRITICAL (CWE-89)

### 2. XSS Detection
- Language: JavaScript, Python (templates), Java (JSP)
- Detects: innerHTML, dangerouslySetInnerHTML, eval
- Severity: HIGH (CWE-79)

### 3. Credential Exposure
- Sources: Code files, .env, config files, git history, environment
- Detects: AWS keys, API keys, passwords, SSH keys, tokens, JWT
- Severity: CRITICAL
- False positive filtering: demo/test/placeholder values excluded

### 4. Compliance Scanning
- GDPR: 5 article checks (Articles 5, 7, 17, 32)
- HIPAA: Technical & administrative safeguards
- Detects: Unencrypted data, missing controls, access logs

## 📈 Risk Levels

| Level | Score | Action |
|-------|-------|--------|
| 🔴 CRITICAL | 80-100 | Stop deployment now |
| 🟠 HIGH | 60-79 | Fix before production |
| 🟡 MEDIUM | 40-59 | Fix soon |
| 🟢 LOW | 20-39 | Fix when possible |
| ⚪ INFO | 0-19 | Monitor |

## 📝 Report Types

1. **JSON** (`security_report.json`)
   - Machine-readable
   - All details
   - CI/CD friendly

2. **HTML** (`security_report.html`)
   - Interactive dashboard
   - Color-coded severity
   - Remediation steps included

3. **SARIF** (`security_report.sarif`)
   - Standard format
   - GitHub code scanning
   - CI/CD integration

## ⚙️ Configuration Options

```python
scanner.scan(
    included_paths=[Path("src")],      # What to scan
    excluded_paths=[Path(".venv")],    # What to skip
    scan_git_history=True,             # Check commits
    check_env_files=True,              # Check .env
    check_config_files=True,           # Check config
    verbose=True,                      # Debug logging
)
```

## 🔧 Common Tasks

### Scan Specific Directory
```python
scanner.scan(included_paths=[Path("src/api")])
```

### Ignore Test Files
```python
scanner.scan(excluded_paths=[Path("tests"), Path("test_*.py")])
```

### Generate Only HTML Report
```python
scanner.generate_reports(reports_dir, formats=["html"])
```

### Get Detailed Assessment
```python
assessment = scanner.get_assessment()
print(f"Critical: {assessment.critical_count}")
print(f"High: {assessment.high_count}")
print(f"Compliance violations: {len(assessment.compliance_violations)}")
```

## 🔑 Key Classes

### SecurityOrchestrator
Main entry point for scanning
```python
scanner = SecurityOrchestrator(workspace_root)
assessment = scanner.scan()
scanner.generate_reports(output_dir)
```

### RiskAssessment
Contains all findings and violations
```python
assessment.vulnerability_findings    # List of vulnerabilities
assessment.compliance_violations     # List of compliance issues
assessment.risk_score               # 0-100
assessment.overall_risk_level       # CRITICAL, HIGH, etc.
assessment.recommendations          # Action items
```

### VulnerabilityFinding
Individual security finding
```python
finding.title                       # Human-readable title
finding.severity                   # Severity level
finding.location.file_path         # File path
finding.location.line_number       # Line number
finding.remediation                # How to fix
finding.cwe_id                     # CWE reference
finding.confidence                 # Detection confidence
```

## 📚 Remediation Quick Links

### SQL Injection Fix
Use parameterized queries:
```python
# ✅ Python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ✅ Java
PreparedStatement pstmt = connection.prepareStatement("SELECT * FROM users WHERE id = ?");
pstmt.setInt(1, userId);

# ✅ JavaScript
db.query("SELECT * FROM users WHERE id = ?", [userId]);
```

### XSS Fix
Use safe output encoding:
```javascript
// ✅ Use textContent (text-only)
element.textContent = userInput;

// ✅ Sanitize HTML
element.innerHTML = DOMPurify.sanitize(userInput);
```

### Credential Fix
Move to environment variables:
```python
# ❌ Don't do this
API_KEY = "sk_live_abc123"

# ✅ Do this
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
```

### GDPR/HIPAA Fix
1. Encrypt data at rest (AES-256)
2. Encrypt in transit (TLS 1.2+)
3. Add access controls & audit logging
4. Create data processing agreements
5. Implement right to erasure

## 📱 Integration Examples

### GitHub Actions
```yaml
- name: Security Scan
  run: python3 security_scanner_demo.py
  
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: security_reports/security_report.sarif
```

### GitLab CI
```yaml
security_scan:
  script:
    - python3 security_scanner_demo.py
  artifacts:
    reports:
      sast: security_reports/security_report.sarif
```

## 🎓 Severity Reference

- **CRITICAL (CWE-89, CWE-79, CWE-798)**: Stop! Fix immediately
- **HIGH**: Fix before deploying to production
- **MEDIUM**: Address within next sprint
- **LOW**: Schedule for later
- **INFO**: For awareness

## 💡 Best Practices

1. **Regular Scanning**: Run on every commit
2. **Baseline**: Establish acceptable risk level
3. **Tracking**: Create issues for findings
4. **Remediation**: Document fixes applied
5. **Review**: Regular security reviews
6. **Training**: Update team on findings
7. **Rotation**: Rotate exposed credentials immediately

## ❓ FAQ

**Q: Why are demo credentials being flagged?**
A: They're still credentials. Use environment variables.

**Q: How do I reduce false positives?**
A: The scanner has built-in filtering for demo/test values.

**Q: Can I customize Scanner rules?**
A: Yes! Extend BaseScanner or customize patterns.

**Q: Does it scan binary files?**
A: No, only text files with target code patterns.

**Q: How deep does git history scanning go?**
A: Configurable (default: 50 commits recent).

**Q: Can I integrate with GitHub/GitLab?**
A: Yes! Use SARIF report format with native integrations.

---

**Version**: 1.0.0 | Last Updated: March 2026
