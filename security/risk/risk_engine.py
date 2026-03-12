"""
Risk scoring and severity assessment engine.

Calculates overall risk scores and severity levels based on findings.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
from ..core.vulnerability import VulnerabilityFinding, ComplianceViolation, Severity, VulnerabilityType


class RiskLevel(Enum):
    """Overall risk levels."""
    CRITICAL = "CRITICAL"  # Requires immediate action
    HIGH = "HIGH"           # Should be addressed soon
    MEDIUM = "MEDIUM"       # Should be addressed
    LOW = "LOW"             # Should be addressed eventually
    INFO = "INFO"           # Informational


@dataclass
class RiskMetrics:
    """Risk assessment metrics."""
    total_vulnerabilities: int = 0
    critical_vulnerabilities: int = 0
    high_vulnerabilities: int = 0
    medium_vulnerabilities: int = 0
    low_vulnerabilities: int = 0
    info_vulnerabilities: int = 0
    
    gdpr_violations: int = 0
    hipaa_violations: int = 0
    pci_violations: int = 0
    
    highest_cwe_risk: str = ""
    vulnerability_density: float = 0.0  # Vulns per 1000 lines
    
    def __str__(self) -> str:
        return (
            f"Critical: {self.critical_vulnerabilities} | "
            f"High: {self.high_vulnerabilities} | "
            f"Medium: {self.medium_vulnerabilities} | "
            f"Low: {self.low_vulnerabilities}"
        )


class RiskScoringEngine:
    """Calculates risk scores and severity levels."""
    
    # Risk weights for different vulnerability types
    SEVERITY_WEIGHTS = {
        Severity.CRITICAL: 100,
        Severity.HIGH: 50,
        Severity.MEDIUM: 25,
        Severity.LOW: 10,
        Severity.INFO: 5,
    }
    
    # Additional multipliers for certain vulnerability types
    VULNERABILITY_MULTIPLIERS = {
        VulnerabilityType.SQL_INJECTION: 1.5,
        VulnerabilityType.XSS_CROSS_SITE_SCRIPTING: 1.4,
        VulnerabilityType.COMMAND_INJECTION: 1.5,
        VulnerabilityType.INSECURE_DESERIALIZATION: 1.4,
        VulnerabilityType.EXPOSED_API_KEY: 1.6,
        VulnerabilityType.EXPOSED_PASSWORD: 1.6,
        VulnerabilityType.EXPOSED_PRIVATE_KEY: 1.8,
        VulnerabilityType.GDPR_VIOLATION: 1.5,
        VulnerabilityType.HIPAA_VIOLATION: 1.7,
    }
    
    # Confidence-based adjustments
    CONFIDENCE_THRESHOLD = 0.70
    
    # Risk score thresholds
    SCORE_RANGES = {
        RiskLevel.CRITICAL: (80, 100),
        RiskLevel.HIGH: (60, 79),
        RiskLevel.MEDIUM: (40, 59),
        RiskLevel.LOW: (20, 39),
        RiskLevel.INFO: (0, 19),
    }
    
    def __init__(self, scanned_file_count: int = 1, estimated_lines_of_code: int = 1000):
        self.scanned_file_count = scanned_file_count
        self.estimated_lines_of_code = estimated_lines_of_code
        self.findings: List[VulnerabilityFinding] = []
        self.violations: List[ComplianceViolation] = []
    
    def calculate_risk_score(
        self,
        findings: List[VulnerabilityFinding],
        violations: List[ComplianceViolation],
    ) -> float:
        """Calculate overall risk score (0-100)."""
        self.findings = findings
        self.violations = violations
        
        if not findings and not violations:
            return 0.0
        
        total_score = 0.0
        
        # Score findings
        for finding in findings:
            score = self._score_finding(finding)
            total_score += score
        
        # Score violations
        for violation in violations:
            score = self._score_violation(violation)
            total_score += score
        
        # Normalize to 0-100 scale
        normalized_score = min(total_score / len(findings + violations) if findings or violations else 0, 100.0)
        
        return round(normalized_score, 1)
    
    def calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """Get risk level from score."""
        for level, (min_score, max_score) in self.SCORE_RANGES.items():
            if min_score <= risk_score <= max_score:
                return level
        return RiskLevel.INFO
    
    def calculate_metrics(
        self,
        findings: List[VulnerabilityFinding],
        violations: List[ComplianceViolation],
    ) -> RiskMetrics:
        """Calculate risk metrics."""
        metrics = RiskMetrics()
        
        # Count findings by severity
        metrics.total_vulnerabilities = len(findings)
        metrics.critical_vulnerabilities = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        metrics.high_vulnerabilities = sum(1 for f in findings if f.severity == Severity.HIGH)
        metrics.medium_vulnerabilities = sum(1 for f in findings if f.severity == Severity.MEDIUM)
        metrics.low_vulnerabilities = sum(1 for f in findings if f.severity == Severity.LOW)
        metrics.info_vulnerabilities = sum(1 for f in findings if f.severity == Severity.INFO)
        
        # Count compliance violations
        metrics.gdpr_violations = sum(1 for v in violations if str(v.framework.value) == "gdpr")
        metrics.hipaa_violations = sum(1 for v in violations if str(v.framework.value) == "hipaa")
        
        # Calculate vulnerability density
        if self.estimated_lines_of_code > 0:
            metrics.vulnerability_density = (metrics.total_vulnerabilities / self.estimated_lines_of_code) * 1000
        
        # Find highest CWE risk
        cwe_risks = {}
        for finding in findings:
            if finding.cwe_id:
                cwe_risks[finding.cwe_id] = cwe_risks.get(finding.cwe_id, 0) + self.SEVERITY_WEIGHTS[finding.severity]
        
        if cwe_risks:
            metrics.highest_cwe_risk = max(cwe_risks, key=cwe_risks.get)
        
        return metrics
    
    def get_risk_summary(
        self,
        risk_score: float,
        risk_level: RiskLevel,
        metrics: RiskMetrics,
    ) -> str:
        """Generate a text summary of the risk assessment."""
        summary = f"{risk_level.value} RISK LEVEL (Score: {risk_score}/100)\n\n"
        
        summary += "VULNERABILITY SUMMARY:\n"
        summary += f"  🔴 Critical: {metrics.critical_vulnerabilities}\n"
        summary += f"  🟠 High: {metrics.high_vulnerabilities}\n"
        summary += f"  🟡 Medium: {metrics.medium_vulnerabilities}\n"
        summary += f"  🔵 Low: {metrics.low_vulnerabilities}\n"
        summary += f"  ⚪ Info: {metrics.info_vulnerabilities}\n\n"
        
        summary += "COMPLIANCE VIOLATIONS:\n"
        summary += f"  GDPR: {metrics.gdpr_violations}\n"
        summary += f"  HIPAA: {metrics.hipaa_violations}\n\n"
        
        if metrics.highest_cwe_risk:
            summary += f"HIGHEST RISK CWE: {metrics.highest_cwe_risk}\n"
            summary += f"VULNERABILITY DENSITY: {metrics.vulnerability_density:.2f} per 1000 LOC\n\n"
        
        summary += self._get_recommendations(risk_level, metrics)
        
        return summary
    
    def _score_finding(self, finding: VulnerabilityFinding) -> float:
        """Score a single finding."""
        base_score = self.SEVERITY_WEIGHTS[finding.severity]
        
        # Apply vulnerability type multiplier
        multiplier = self.VULNERABILITY_MULTIPLIERS.get(finding.vulnerability_type, 1.0)
        
        # Apply confidence adjustment
        confidence_adjustment = finding.confidence
        
        return base_score * multiplier * confidence_adjustment
    
    def _score_violation(self, violation: ComplianceViolation) -> float:
        """Score a compliance violation."""
        base_score = self.SEVERITY_WEIGHTS[violation.severity]
        
        # Compliance violations get higher multiplier
        multiplier = 1.3
        
        # Higher score for more affected locations
        location_adjustment = 1.0 + (len(violation.affected_locations) * 0.1)
        
        return base_score * multiplier * location_adjustment
    
    def _get_recommendations(self, risk_level: RiskLevel, metrics: RiskMetrics) -> str:
        """Generate risk-based recommendations."""
        recommendations = "RECOMMENDATIONS:\n"
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations += (
                "  ⚠️  IMMEDIATE ACTION REQUIRED\n"
                "  1. Stop deployment until critical issues are fixed\n"
                "  2. Conduct security code review\n"
                "  3. Implement fixes in priority order\n"
            )
        elif risk_level == RiskLevel.HIGH:
            recommendations += (
                "  ⚠️  Address issues before production deployment\n"
                "  1. Create security backlog items\n"
                "  2. Schedule security review meeting\n"
                "  3. Implement fixes in next sprint\n"
            )
        elif risk_level == RiskLevel.MEDIUM:
            recommendations += (
                "  ⚠️  Address issues in near-term\n"
                "  1. Add to product backlog\n"
                "  2. Plan for next sprints\n"
                "  3. Regular reviews\n"
            )
        else:
            recommendations += (
                "  ✓ Continue monitoring\n"
                "  1. Schedule regular reviews\n"
                "  2. Keep frameworks updated\n"
            )
        
        if metrics.critical_vulnerabilities > 0:
            recommendations += (
                "\n  CRITICAL ITEMS:\n"
                "  - Review and fix SQL injection risks\n"
                "  - Review and fix exposed credentials\n"
                "  - Implement input validation\n"
            )
        
        if metrics.gdpr_violations > 0 or metrics.hipaa_violations > 0:
            recommendations += (
                "\n  COMPLIANCE ITEMS:\n"
                "  - Implement data encryption\n"
                "  - Add audit logging\n"
                "  - Create Data Processing Agreements\n"
                "  - Schedule privacy review\n"
            )
        
        return recommendations
