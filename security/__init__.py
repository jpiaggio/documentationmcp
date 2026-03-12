"""
Security & Compliance Scanning Framework

Provides comprehensive vulnerability detection, compliance checking, and risk assessment
for codebases. Supports SQL injection, XSS, credential exposure, GDPR/HIPAA compliance.
"""

from .core.vulnerability import (
    VulnerabilityType,
    Severity,
    VulnerabilityFinding,
    ComplianceViolation,
    RiskAssessment,
)
from .core.scanner import BaseScanner, ScannerRegistry, SecurityContext
from .detectors.sql_injection import SQLInjectionScanner
from .detectors.xss import XSSScanner
from .detectors.credentials import CredentialScanner
from .detectors.compliance import ComplianceScanner
from .risk.risk_engine import RiskScoringEngine, RiskLevel
from .reporters.json_reporter import JSONReporter
from .reporters.html_reporter import HTMLReporter
from .reporters.sarif_reporter import SARIFReporter
from .orchestrator import SecurityOrchestrator

__version__ = "1.0.0"
__all__ = [
    "VulnerabilityType",
    "Severity",
    "VulnerabilityFinding",
    "ComplianceViolation",
    "RiskAssessment",
    "BaseScanner",
    "ScannerRegistry",
    "SecurityContext",
    "SQLInjectionScanner",
    "XSSScanner",
    "CredentialScanner",
    "ComplianceScanner",
    "RiskScoringEngine",
    "RiskLevel",
    "JSONReporter",
    "HTMLReporter",
    "SARIFReporter",
    "SecurityOrchestrator",
]
