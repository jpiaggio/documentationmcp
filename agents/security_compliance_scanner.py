"""
Security & Compliance Scanning
Improvement #7 from IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md

Integrated security scanning detecting:
- Vulnerable patterns (SQL injection, XSS, etc.)
- Exposed secrets and credentials
- Compliance violations (GDPR, HIPAA, SOC2)
- Insecure cryptography
- Hardcoded passwords
"""

import os
import re
import json
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class SeverityLevel(Enum):
    """Security issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ComplianceStandard(Enum):
    """Supported compliance standards."""
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    SOC2 = "SOC2"
    PCI_DSS = "PCI-DSS"


@dataclass
class SecurityIssue:
    """Represents a security vulnerability."""
    issue_type: str  # e.g., "sql_injection_risk, "exposed_secret"
    severity: SeverityLevel
    location: str  # file:line
    description: str
    evidence: str  # The problematic code snippet
    cwe_id: Optional[str]  # CWE identifier
    remediation: str
    owasp_category: Optional[str]  # e.g., "A1: Injection"


@dataclass
class ComplianceIssue:
    """Represents a compliance violation."""
    standard: ComplianceStandard
    issue_type: str  # e.g., "unencrypted_pii", "missing_audit_log"
    severity: SeverityLevel
    affected_modules: List[str]
    description: str
    remediation_time_days: int
    business_impact: str


@dataclass
class ScanResult:
    """Complete security and compliance scan result."""
    security_issues: List[SecurityIssue]
    compliance_issues: List[ComplianceIssue]
    risk_score: float  # 0-10 CVSS-like scoring
    overall_status: str  # "PASS", "WARNING", "CRITICAL"
    vulnerable_modules: Dict[str, int]  # Module -> issue count
    detected_secrets: List[str]  # Types of secrets found (without values)
    encryption_quality: Dict[str, str]  # Algorithm -> assessment
    recommendations: List[str]
    scan_timestamp: str


class SecurityComplianceScanner:
    """Scans codebase for security vulnerabilities and compliance violations."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the security scanner.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = repo_path
        self.sensitive_patterns = self._initialize_sensitive_patterns()
        self.vulnerability_patterns = self._initialize_vulnerability_patterns()
        self.compliance_rules = self._initialize_compliance_rules()
    
    def scan_codebase(self) -> ScanResult:
        """
        Perform comprehensive security and compliance scan.
        
        Returns:
            ScanResult with all findings
        """
        security_issues = []
        vulnerable_modules = {}
        detected_secrets = set()
        encryption_quality = {}
        
        # Scan all Python files
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Scan for vulnerabilities
                        issues = self._scan_file_for_vulnerabilities(content, rel_path)
                        security_issues.extend(issues)
                        
                        # Track vulnerable modules
                        if issues:
                            vulnerable_modules[rel_path] = len(issues)
                        
                        # Detect secrets
                        secrets = self._detect_secrets(content, rel_path)
                        detected_secrets.update(secrets)
                        
                        # Assess encryption usage
                        encryption = self._assess_encryption(content)
                        if encryption:
                            encryption_quality.update(encryption)
                    
                    except Exception as e:
                        pass
        
        # Analyze compliance
        compliance_issues = self._analyze_compliance(security_issues, vulnerable_modules)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(security_issues, compliance_issues)
        
        # Determine overall status
        overall_status = self._determine_overall_status(security_issues, compliance_issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(security_issues, compliance_issues)
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        return ScanResult(
            security_issues=security_issues,
            compliance_issues=compliance_issues,
            risk_score=risk_score,
            overall_status=overall_status,
            vulnerable_modules=vulnerable_modules,
            detected_secrets=list(detected_secrets),
            encryption_quality=encryption_quality,
            recommendations=recommendations,
            scan_timestamp=timestamp
        )
    
    def _scan_file_for_vulnerabilities(self, content: str, file_path: str) -> List[SecurityIssue]:
        """Scan a file for security vulnerabilities."""
        issues = []
        lines = content.split('\n')
        
        for pattern_info in self.vulnerability_patterns:
            pattern = pattern_info['pattern']
            issue_type = pattern_info['type']
            severity = pattern_info['severity']
            cwe = pattern_info['cwe']
            owasp = pattern_info['owasp']
            remediation = pattern_info['remediation']
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    # Avoid false positives in comments
                    if line.strip().startswith('#'):
                        continue
                    
                    issue = SecurityIssue(
                        issue_type=issue_type,
                        severity=severity,
                        location=f"{file_path}:{line_num}",
                        description=pattern_info['description'],
                        evidence=line.strip(),
                        cwe_id=cwe,
                        remediation=remediation,
                        owasp_category=owasp
                    )
                    issues.append(issue)
        
        return issues
    
    def _detect_secrets(self, content: str, file_path: str) -> Set[str]:
        """Detect exposed secrets and credentials."""
        detected = set()
        
        for secret_type, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.add(secret_type)
        
        return detected
    
    def _assess_encryption(self, content: str) -> Dict[str, str]:
        """Assess encryption practices."""
        encryption_status = {}
        
        # Check for deprecated/weak encryption
        weak_algorithms = {
            'MD5': 'WEAK - Use SHA-256',
            'SHA1': 'WEAK - Use SHA-256',
            'DES': 'CRITICAL - Use AES-256',
            'RSA': {'1024': 'WEAK - Use 2048+', '2048': 'GOOD'},
            'AES': {'128': 'FAIR - Use 256', '256': 'STRONG'}
        }
        
        for algo, status_info in weak_algorithms.items():
            if algo in content:
                if isinstance(status_info, dict):
                    encryption_status[algo] = "Detected (check bit length)"
                else:
                    encryption_status[algo] = status_info
        
        if 'hashlib.md5' in content.lower() or re.search(r'md5\(', content, re.IGNORECASE):
            encryption_status['MD5'] = 'WEAK - Never use'
        
        if 'hashlib.sha256' in content or 'SHA256' in content:
            encryption_status['SHA-256'] = 'STRONG - Recommended'
        
        return encryption_status
    
    def _analyze_compliance(self, security_issues: List[SecurityIssue], 
                          vulnerable_modules: Dict[str, int]) -> List[ComplianceIssue]:
        """Analyze compliance violations."""
        compliance_issues = []
        
        # GDPR: Check for PII handling without protection
        if self._check_for_pii_handling(vulnerable_modules):
            if not self._has_encryption_for_pii():
                compliance_issues.append(ComplianceIssue(
                    standard=ComplianceStandard.GDPR,
                    issue_type='unencrypted_pii',
                    severity=SeverityLevel.CRITICAL,
                    affected_modules=list(vulnerable_modules.keys())[:3],
                    description='Personal data not encrypted at rest or in transit',
                    remediation_time_days=14,
                    business_impact='Regulatory fines up to €20M or 4% revenue'
                ))
        
        # Check for missing audit logs (HIPAA, SOC2)
        if not self._has_audit_logging():
            compliance_issues.append(ComplianceIssue(
                standard=ComplianceStandard.HIPAA,
                issue_type='missing_audit_log',
                severity=SeverityLevel.HIGH,
                affected_modules=['auth', 'database'],
                description='No audit logging detected for sensitive operations',
                remediation_time_days=7,
                business_impact='Failed compliance audit, potential penalties'
            ))
        
        # PCI-DSS: Check for hardcoded secrets
        hardcoded_secrets = [issue for issue in security_issues 
                           if issue.issue_type == 'hardcoded_secret']
        if hardcoded_secrets:
            compliance_issues.append(ComplianceIssue(
                standard=ComplianceStandard.PCI_DSS,
                issue_type='hardcoded_credentials',
                severity=SeverityLevel.CRITICAL,
                affected_modules=[issue.location.split(':')[0] for issue in hardcoded_secrets],
                description='Credentials hardcoded in source code',
                remediation_time_days=1,
                business_impact='PCI-DSS non-compliance, potential card data exposure'
            ))
        
        return compliance_issues
    
    def _generate_recommendations(self, security_issues: List[SecurityIssue],
                                 compliance_issues: List[ComplianceIssue]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        # Group issues by type
        issue_types = set(issue.issue_type for issue in security_issues)
        
        if 'sql_injection_risk' in issue_types:
            recommendations.append('Use parameterized queries for all database operations')
        
        if 'exposed_secret' in issue_types:
            recommendations.append('Rotate all exposed credentials immediately')
            recommendations.append('Implement secret management (vault, env vars)')
        
        if 'hardcoded_password' in issue_types:
            recommendations.append('Move all credentials to environment variables or secrets manager')
        
        if compliance_issues:
            for issue in compliance_issues:
                recommendations.append(f'{issue.standard.value}: {issue.remediation_time_days} days to fix')
        
        critical_issues = [i for i in security_issues if i.severity == SeverityLevel.CRITICAL]
        if critical_issues:
            recommendations.append(f'🚨 URGENT: {len(critical_issues)} critical issues require immediate attention')
        
        return recommendations
    
    def _initialize_sensitive_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting sensitive data."""
        return {
            'api_key': [
                r'api[_-]?key\s*=\s*["\'][\w-]+["\']',
                r'apikey\s*:\s*["\'][\w-]+["\']'
            ],
            'database_password': [
                r'password\s*=\s*["\'][\w@#$%&*-]+["\']',
                r'db[_-]?password\s*=\s*["\'][\w@#$%&*-]+["\']',
                r'mysql://.*:.*@'
            ],
            'private_key': [
                r'-----BEGIN.*PRIVATE KEY-----',
                r'private[_-]?key\s*=\s*["\']'
            ],
            'jwt_token': [
                r'eyJ[\w-_.]+\.eyJ[\w-_.]+\.[\w-_.]+',
                r'jwt\s*=\s*["\']eyJ'
            ],
            'aws_key': [
                r'AKIA[\w-]{16}',
                r'aws[_-]?access[_-]?key[_-]?id\s*=\s*["\']AKIA'
            ]
        }
    
    def _initialize_vulnerability_patterns(self) -> List[Dict]:
        """Initialize patterns for detecting vulnerabilities."""
        return [
            {
                'type': 'sql_injection_risk',
                'pattern': r'execute\s*\(\s*["\'].*[+].*["\']|query\s*\(\s*["\'].*%s',
                'severity': SeverityLevel.CRITICAL,
                'description': 'Potential SQL injection - string concatenation in queries',
                'cwe': 'CWE-89',
                'owasp': 'A1: Injection',
                'remediation': 'Use parameterized queries or prepared statements'
            },
            {
                'type': 'hardcoded_password',
                'pattern': r'password\s*=\s*["\'][\w@#$%&*-]+["\'](?![\s]*#)',
                'severity': SeverityLevel.CRITICAL,
                'description': 'Hardcoded password detected',
                'cwe': 'CWE-798',
                'owasp': 'A2: Broken Authentication',
                'remediation': 'Use environment variables or secrets manager'
            },
            {
                'type': 'exposed_secret',
                'pattern': r'secret\s*=\s*["\'][\w-]{20,}["\']|api[_-]?key\s*=\s*["\'][\w-]{20,}["\']',
                'severity': SeverityLevel.HIGH,
                'description': 'Potential exposed secret or API key',
                'cwe': 'CWE-798',
                'owasp': 'A2: Broken Authentication',
                'remediation': 'Rotate the exposed secret and move to environment variables'
            },
            {
                'type': 'unsafe_deserialization',
                'pattern': r'pickle\.load|yaml\.load\s*\(|json\.loads\s*\(',
                'severity': SeverityLevel.HIGH,
                'description': 'Unsafe deserialization function',
                'cwe': 'CWE-502',
                'owasp': 'A8: Insecure Deserialization',
                'remediation': 'Use safe_load() or validate input before deserialization'
            },
            {
                'type': 'weak_cryptography',
                'pattern': r'hashlib\.md5|hashlib\.sha1|DES\(|Cipher\.new\(["\']des',
                'severity': SeverityLevel.HIGH,
                'description': 'Weak or deprecated cryptographic algorithm',
                'cwe': 'CWE-327',
                'owasp': 'A6: Broken Crypto',
                'remediation': 'Use AES-256 or SHA-256 for encryption/hashing'
            },
            {
                'type': 'command_injection_risk',
                'pattern': r'os\.system\s*\(|subprocess\.call\s*\(|shell=True',
                'severity': SeverityLevel.HIGH,
                'description': 'Potential command injection vulnerability',
                'cwe': 'CWE-78',
                'owasp': 'A1: Injection',
                'remediation': 'Use subprocess.run() with shell=False and avoid string interpolation'
            },
            {
                'type': 'missing_input_validation',
                'pattern': r'request\.args|request\.form|request\.data(?!.*validate)',
                'severity': SeverityLevel.MEDIUM,
                'description': 'User input used without visible validation',
                'cwe': 'CWE-20',
                'owasp': 'A1: Injection',
                'remediation': 'Always validate and sanitize user input'
            }
        ]
    
    def _initialize_compliance_rules(self) -> Dict:
        """Initialize compliance checking rules."""
        return {
            'GDPR': {
                'rules': ['data_retention_periods', 'right_to_be_forgotten'],
                'pii_fields': ['email', 'phone', 'ssn', 'credit_card', 'address', 'date_of_birth']
            },
            'HIPAA': {
                'rules': ['audit_logging', 'access_control', 'encryption_at_rest'],
                'protected_fields': ['medical_record', 'diagnosis', 'medication', 'patient_id']
            },
            'PCI_DSS': {
                'rules': ['no_hardcoded_secrets', 'secure_transmission', 'access_control'],
                'sensitive_data': ['credit_card', 'cvv', 'pin']
            }
        }
    
    def _check_for_pii_handling(self, vulnerable_modules: Dict[str, int]) -> bool:
        """Check if code handles personally identifiable information."""
        pii_indicators = ['user', 'profile', 'customer', 'personal', 'auth']
        return any(any(indicator in module for indicator in pii_indicators) 
                  for module in vulnerable_modules.keys())
    
    def _has_encryption_for_pii(self) -> bool:
        """Check if PII is encrypted."""
        # This is a simplified check
        return False  # Default to false for demo
    
    def _has_audit_logging(self) -> bool:
        """Check if audit logging is implemented."""
        return False  # Default to false for demo
    
    def _calculate_risk_score(self, security_issues: List[SecurityIssue],
                             compliance_issues: List[ComplianceIssue]) -> float:
        """
        Calculate risk score on CVSS-like scale (0-10).
        
        Returns:
            float: Risk score
        """
        score = 0.0
        
        # Security issues scoring
        critical_count = sum(1 for issue in security_issues 
                           if issue.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for issue in security_issues 
                        if issue.severity == SeverityLevel.HIGH)
        
        score += critical_count * 3.0
        score += high_count * 1.5
        
        # Compliance issues
        score += len(compliance_issues) * 2.0
        
        # Cap at 10
        return min(10.0, score)
    
    def _determine_overall_status(self, security_issues: List[SecurityIssue],
                                 compliance_issues: List[ComplianceIssue]) -> str:
        """Determine overall scan status."""
        critical_issues = [i for i in security_issues 
                         if i.severity == SeverityLevel.CRITICAL]
        
        if critical_issues or any(i.severity == SeverityLevel.CRITICAL 
                                 for i in compliance_issues):
            return 'CRITICAL'
        
        if any(i.severity == SeverityLevel.HIGH for i in security_issues):
            return 'WARNING'
        
        return 'PASS'
    
    def generate_report(self, result: ScanResult) -> str:
        """Generate a comprehensive security report."""
        report = []
        report.append("=" * 80)
        report.append("SECURITY & COMPLIANCE SCAN REPORT")
        report.append("=" * 80)
        
        # Summary
        report.append(f"\n📊 SCAN SUMMARY")
        report.append(f"  Status: {result.overall_status}")
        report.append(f"  Risk Score: {result.risk_score:.1f}/10.0")
        report.append(f"  Timestamp: {result.scan_timestamp}")
        
        # Security Issues
        report.append(f"\n🔒 SECURITY ISSUES ({len(result.security_issues)})")
        for issue in result.security_issues[:10]:
            report.append(f"  [{issue.severity.value}] {issue.issue_type}")
            report.append(f"    Location: {issue.location}")
            report.append(f"    {issue.description}")
            report.append(f"    Remediation: {issue.remediation}")
        
        if len(result.security_issues) > 10:
            report.append(f"  ... and {len(result.security_issues) - 10} more issues")
        
        # Compliance Issues
        if result.compliance_issues:
            report.append(f"\n📋 COMPLIANCE ISSUES ({len(result.compliance_issues)})")
            for issue in result.compliance_issues:
                report.append(f"  [{issue.standard.value}] {issue.issue_type}")
                report.append(f"    Severity: {issue.severity.value}")
                report.append(f"    {issue.description}")
                report.append(f"    Remediation Time: {issue.remediation_time_days} days")
        
        # Detected Secrets
        if result.detected_secrets:
            report.append(f"\n🔑 DETECTED SECRETS ({len(result.detected_secrets)})")
            for secret_type in result.detected_secrets:
                report.append(f"  • {secret_type} pattern found")
        
        # Encryption Quality
        if result.encryption_quality:
            report.append(f"\n🔐 ENCRYPTION ASSESSMENT")
            for algo, status in result.encryption_quality.items():
                report.append(f"  {algo}: {status}")
        
        # Vulnerable Modules
        if result.vulnerable_modules:
            report.append(f"\n📁 VULNERABLE MODULES ({len(result.vulnerable_modules)})")
            for module, count in sorted(result.vulnerable_modules.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"  {module}: {count} issues")
        
        # Recommendations
        if result.recommendations:
            report.append(f"\n💡 RECOMMENDATIONS")
            for rec in result.recommendations[:10]:
                report.append(f"  • {rec}")
        
        report.append("\n" + "=" * 80)
        return '\n'.join(report)


def main():
    """Demo of Security Scanner."""
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    scanner = SecurityComplianceScanner(repo_path)
    result = scanner.scan_codebase()
    
    print(scanner.generate_report(result))
    
    # Also output summary as JSON
    print("\n\nJSON SUMMARY (partial):")
    summary = {
        'overall_status': result.overall_status,
        'risk_score': result.risk_score,
        'security_issues_count': len(result.security_issues),
        'compliance_issues_count': len(result.compliance_issues),
        'detected_secrets': result.detected_secrets,
        'vulnerable_modules': result.vulnerable_modules,
        'recommendations': result.recommendations[:5],
    }
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
