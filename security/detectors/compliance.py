"""
GDPR and HIPAA compliance scanner.

Detects code patterns that violate GDPR, HIPAA, and other regulations.
"""

import re
from pathlib import Path
from typing import List, Optional, Set, Dict
from ..core.vulnerability import (
    VulnerabilityFinding,
    ComplianceViolation,
    VulnerabilityType,
    Severity,
    Location,
    ComplianceFramework,
)
from ..core.scanner import BaseScanner, SecurityContext


class ComplianceScanner(BaseScanner):
    """Detects GDPR and HIPAA compliance violations."""
    
    # GDPR Compliance Checks
    GDPR_CHECKS = {
        "unencrypted_pii": {
            "pattern": r'(?i)(email|phone|ssn|social.security|credit.card|dob|date.of.birth)\s*=',
            "requirement": "Article 32: Security of Processing",
            "description": "Personal data stored without encryption",
            "severity": Severity.CRITICAL,
        },
        "missing_consent": {
            "pattern": r'setcookie|localStorage|sessionStorage',
            "requirement": "Article 7: Conditions for Consent",
            "description": "Cookies or local storage without explicit consent mechanism",
            "severity": Severity.HIGH,
        },
        "missing_deletion": {
            "pattern": r'(?i)(todo|fixme).*delete.*user|remove.*personal',
            "requirement": "Article 17: Right to Erasure",
            "description": "No data deletion mechanism found (TODO/FIXME)",
            "severity": Severity.MEDIUM,
        },
        "data_retention": {
            "pattern": r'(?i)(forever|never.delete|permanent)',
            "requirement": "Article 5: Data Minimization",
            "description": "Data retention policy unclear - indefinite storage",
            "severity": Severity.MEDIUM,
        },
        "missing_audit": {
            "pattern": r'(?i)(copy|download|export).*data(?!.*log)',
            "requirement": "Article 5: Accountability",
            "description": "Data operations without audit logging",
            "severity": Severity.HIGH,
        },
    }
    
    # HIPAA Compliance Checks
    HIPAA_CHECKS = {
        "unencrypted_phi": {
            "pattern": r'(?i)(patient|health|medical|diagnosis|prescription)\s*=\s*["\']',
            "requirement": "HIPAA Technical Safeguards",
            "description": "Protected Health Information (PHI) stored without encryption",
            "severity": Severity.CRITICAL,
        },
        "missing_access_control": {
            "pattern": r'(?i)(if|function|def).*(?!.*auth|permission)',
            "requirement": "HIPAA Technical Safeguards",
            "description": "Data access without authentication/authorization",
            "severity": Severity.CRITICAL,
        },
        "unencrypted_transmission": {
            "pattern": r'(?i)http:(?!s).*patient|health|medical',
            "requirement": "HIPAA Technical Safeguards",
            "description": "PHI transmitted over unencrypted connection",
            "severity": Severity.CRITICAL,
        },
        "missing_audit_log": {
            "pattern": r'(?i)phi.*access(?!.*log)',
            "requirement": "HIPAA Technical Safeguards",
            "description": "PHI access without audit logging",
            "severity": Severity.HIGH,
        },
    }
    
    # Data categories that trigger compliance requirements
    DATA_CATEGORIES = {
        "gdpr": {
            "personal_identifiers": r'(?i)(email|phone|ssn|social.security|national.id)',
            "biometric": r'(?i)(biometric|fingerprint|face)',
            "health": r'(?i)(health|medical|patient|diagnosis)',
            "location": r'(?i)(latitude|longitude|gps|location)',
            "race": r'(?i)(race|ethnicity|origin)',
            "religion": r'(?i)(religion|belief)',
            "union": r'(?i)(union|membership)',
        },
        "hipaa": {
            "patient_records": r'(?i)(patient|medical.record)',
            "health_info": r'(?i)(diagnosis|treatment|prescription)',
            "biometric": r'(?i)(dna|biometric)',
        },
    }
    
    REMEDIATION = """Ensure GDPR and HIPAA compliance:

GDPR Requirements:
  1. Article 5: Lawfulness - Only process data with valid legal basis
  2. Article 7: Consent - Obtain explicit opt-in consent before processing
  3. Article 17: Right to Erasure - Implement data deletion functionality
  4. Article 32: Encryption - Encrypt personal data in transit and at rest
  5. Article 33: Breach Notification - Implement incident response procedures

HIPAA Requirements:
  1. Technical Safeguards - Encryption, access controls, audit logs
  2. Physical Safeguards - Secure facility access and device management
  3. Administrative Safeguards - Policies, training, workforce security
  4. Transmission Security - Encrypt PHI in transit (TLS/SSL)
  5. Audit Controls - Log all PHI access and modifications

Implementation Checklist:
  ✓ Identify all personal/health data processing
  ✓ Document legal basis for processing
  ✓ Implement encryption for data at rest (AES-256)
  ✓ Implement encryption for data in transit (TLS 1.2+)
  ✓ Create user consent management
  ✓ Implement data deletion/anonymization
  ✓ Setup comprehensive audit logging
  ✓ Create Data Processing Agreements (DPA)
  ✓ Document Data Protection Impact Assessment (DPIA)
  ✓ Train staff on data protection
"""
    
    def get_scanner_name(self) -> str:
        return "GDPR & HIPAA Compliance Scanner"
    
    def get_scanner_description(self) -> str:
        return "Detects GDPR and HIPAA compliance violations in code and configuration"
    
    def scan(self) -> List[VulnerabilityFinding]:
        """Scan workspace for compliance violations."""
        self.findings = []
        self.violations = []
        
        files_to_scan = self.context.get_files_to_scan()
        
        for file_path in files_to_scan:
            try:
                content = file_path.read_text(errors='ignore')
                self._scan_gdpr_compliance(content, file_path)
                self._scan_hipaa_compliance(content, file_path)
            except Exception as e:
                self.logger.error(f"Error scanning {file_path}: {e}")
        
        return self.findings
    
    def _scan_gdpr_compliance(self, content: str, file_path: Path) -> None:
        """Scan for GDPR compliance issues."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self._is_comment_line(line):
                continue
            
            # Check for unencrypted personal data
            for check_name, check_info in self.GDPR_CHECKS.items():
                if re.search(check_info["pattern"], line, re.IGNORECASE):
                    self._add_gdpr_violation(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        check_name=check_name,
                        check_info=check_info,
                    )
    
    def _scan_hipaa_compliance(self, content: str, file_path: Path) -> None:
        """Scan for HIPAA compliance issues."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if self._is_comment_line(line):
                continue
            
            # Check for unencrypted PHI
            for check_name, check_info in self.HIPAA_CHECKS.items():
                if re.search(check_info["pattern"], line, re.IGNORECASE):
                    self._add_hipaa_violation(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        check_name=check_name,
                        check_info=check_info,
                    )
    
    def _detect_data_categories(self, content: str, framework: str) -> Set[str]:
        """Detect what data categories are being processed."""
        categories = set()
        
        for category, pattern in self.DATA_CATEGORIES.get(framework, {}).items():
            if re.search(pattern, content, re.IGNORECASE):
                categories.add(category)
        
        return categories
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if line is a comment."""
        stripped = line.strip()
        return (stripped.startswith('#') or 
                stripped.startswith('//') or 
                stripped.startswith('/*'))
    
    def _add_gdpr_violation(
        self,
        file_path: Path,
        line_number: int,
        line_content: str,
        check_name: str,
        check_info: Dict,
    ) -> None:
        """Add a GDPR compliance violation."""
        violation = ComplianceViolation(
            id=f"gdpr_{check_name}_{file_path.name}_{line_number}",
            framework=ComplianceFramework.GDPR,
            requirement=check_info["requirement"],
            violation_description=check_info["description"],
            affected_locations=[Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            )],
            severity=check_info["severity"],
            remediation_steps=[
                "Encrypt personal data at rest using AES-256",
                "Encrypt data in transit using TLS 1.2+",
                "Document lawful basis for processing",
                "Implement consent management",
                "Create Data Processing Agreement",
            ],
        )
        self.add_violation(violation)
        
        # Also add as finding for backward compatibility
        finding = VulnerabilityFinding(
            id=violation.id,
            vulnerability_type=VulnerabilityType.GDPR_VIOLATION,
            severity=check_info["severity"],
            title=f"GDPR {check_info['requirement']}",
            description=check_info["description"],
            location=Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            ),
            remediation=self.REMEDIATION,
            tags={"gdpr", "compliance", "privacy"},
        )
        self.add_finding(finding)
    
    def _add_hipaa_violation(
        self,
        file_path: Path,
        line_number: int,
        line_content: str,
        check_name: str,
        check_info: Dict,
    ) -> None:
        """Add a HIPAA compliance violation."""
        violation = ComplianceViolation(
            id=f"hipaa_{check_name}_{file_path.name}_{line_number}",
            framework=ComplianceFramework.HIPAA,
            requirement=check_info["requirement"],
            violation_description=check_info["description"],
            affected_locations=[Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            )],
            severity=check_info["severity"],
            remediation_steps=[
                "Implement encryption (AES-256) for PHI at rest",
                "Use TLS 1.2+ for PHI in transit",
                "Implement access controls and authentication",
                "Enable comprehensive audit logging",
                "Implement incident response procedures",
            ],
        )
        self.add_violation(violation)
        
        # Also add as finding for backward compatibility
        finding = VulnerabilityFinding(
            id=violation.id,
            vulnerability_type=VulnerabilityType.HIPAA_VIOLATION,
            severity=check_info["severity"],
            title=f"HIPAA {check_info['requirement']}",
            description=check_info["description"],
            location=Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            ),
            remediation=self.REMEDIATION,
            tags={"hipaa", "compliance", "healthcare"},
        )
        self.add_finding(finding)
