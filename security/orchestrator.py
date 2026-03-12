"""
Security orchestrator - main entry point for security scanning.

Coordinates all scanners, performs risk assessment, and generates reports.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .core.vulnerability import RiskAssessment
from .core.scanner import SecurityContext, ScannerRegistry, BaseScanner
from .detectors.sql_injection import SQLInjectionScanner
from .detectors.xss import XSSScanner
from .detectors.credentials import CredentialScanner
from .detectors.compliance import ComplianceScanner
from .risk.risk_engine import RiskScoringEngine, RiskLevel
from .reporters.json_reporter import JSONReporter
from .reporters.html_reporter import HTMLReporter
from .reporters.sarif_reporter import SARIFReporter


logging.basicConfig(level=logging.INFO)


class SecurityOrchestrator:
    """Orchestrates security scanning across all scanner types."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        self.registry = ScannerRegistry()
        self._register_scanners()
        self.assessment: Optional[RiskAssessment] = None
    
    def _register_scanners(self) -> None:
        """Register all available scanners."""
        self.registry.register("sql_injection", SQLInjectionScanner)
        self.registry.register("xss", XSSScanner)
        self.registry.register("credentials", CredentialScanner)
        self.registry.register("compliance", ComplianceScanner)
    
    def scan(
        self,
        included_paths: Optional[List[Path]] = None,
        excluded_paths: Optional[List[Path]] = None,
        scan_git_history: bool = False,
        check_env_files: bool = True,
        check_config_files: bool = True,
        verbose: bool = False,
    ) -> RiskAssessment:
        """
        Execute full security scan.
        
        Args:
            included_paths: Paths to scan (default: all)
            excluded_paths: Paths to exclude
            scan_git_history: Whether to scan git commit history
            check_env_files: Whether to check .env files
            check_config_files: Whether to check config files
            verbose: Whether to log verbose output
        
        Returns:
            RiskAssessment with all findings and violations
        """
        start_time = time.time()
        
        # Create security context
        context = SecurityContext(
            workspace_root=self.workspace_root,
            included_paths=included_paths or [Path(".")],
            excluded_paths=excluded_paths or [],
            scan_git_history=scan_git_history,
            check_env_files=check_env_files,
            check_config_files=check_config_files,
            verbose=verbose,
        )
        
        self.logger.info(f"Starting security scan of {self.workspace_root}")
        self.logger.info(f"Included paths: {context.included_paths}")
        
        # Get all registered scanners
        scanners = self.registry.get_all_scanners(context)
        
        # Run all scanners
        all_findings = []
        all_violations = []
        files_scanned = set()
        
        for scanner_name, scanner in scanners.items():
            self.logger.info(f"Running {scanner.get_scanner_name()}...")
            
            try:
                findings = scanner.scan()
                all_findings.extend(findings)
                all_violations.extend(scanner.get_violations())
                
                self.logger.info(f"  Found {len(findings)} vulnerabilities")
                
                # Track scanned files
                for finding in findings:
                    files_scanned.add(finding.location.file_path)
            
            except Exception as e:
                self.logger.error(f"Error running {scanner_name}: {e}")
        
        # Calculate risk assessment
        duration = time.time() - start_time
        risk_engine = RiskScoringEngine(
            scanned_file_count=len(files_scanned),
            estimated_lines_of_code=self._estimate_lines_of_code(),
        )
        
        risk_score = risk_engine.calculate_risk_score(all_findings, all_violations)
        risk_level = risk_engine.calculate_risk_level(risk_score)
        metrics = risk_engine.calculate_metrics(all_findings, all_violations)
        summary = risk_engine.get_risk_summary(risk_score, risk_level, metrics)
        
        # Create assessment
        self.assessment = RiskAssessment(
            vulnerability_findings=all_findings,
            compliance_violations=all_violations,
            overall_risk_level=risk_level.value,
            risk_score=risk_score,
            summary=summary,
            recommendations=self._generate_recommendations(all_findings, all_violations),
            scanned_files=len(files_scanned),
            scan_duration_seconds=duration,
            timestamp=datetime.utcnow(),
        )
        
        self.logger.info(f"Scan completed in {duration:.2f}s")
        self.logger.info(f"Risk Level: {risk_level.value} (Score: {risk_score}/100)")
        self.logger.info(f"Total Findings: {self.assessment.total_findings}")
        
        return self.assessment
    
    def generate_reports(
        self,
        output_dir: Path,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Path]:
        """
        Generate reports in specified formats.
        
        Args:
            output_dir: Directory to save reports
            formats: Report formats (json, html, sarif)
        
        Returns:
            Dictionary mapping format to output file path
        """
        if not self.assessment:
            raise ValueError("No assessment available. Run scan() first.")
        
        if formats is None:
            formats = ["json", "html", "sarif"]
        
        output_dir.mkdir(parents=True, exist_ok=True)
        report_paths = {}
        
        # Generate JSON report
        if "json" in formats:
            reporter = JSONReporter()
            output_path = output_dir / "security_report.json"
            reporter.save_report(self.assessment, output_path)
            report_paths["json"] = output_path
            self.logger.info(f"JSON report saved: {output_path}")
        
        # Generate HTML report
        if "html" in formats:
            reporter = HTMLReporter()
            output_path = output_dir / "security_report.html"
            reporter.save_report(self.assessment, output_path)
            report_paths["html"] = output_path
            self.logger.info(f"HTML report saved: {output_path}")
        
        # Generate SARIF report
        if "sarif" in formats:
            reporter = SARIFReporter()
            output_path = output_dir / "security_report.sarif"
            reporter.save_report(self.assessment, output_path)
            report_paths["sarif"] = output_path
            self.logger.info(f"SARIF report saved: {output_path}")
        
        return report_paths
    
    def get_assessment(self) -> Optional[RiskAssessment]:
        """Get the last risk assessment."""
        return self.assessment
    
    def _estimate_lines_of_code(self) -> int:
        """Estimate total lines of code in workspace."""
        total_lines = 0
        code_extensions = {'.py', '.java', '.js', '.ts', '.go', '.rb', '.php', '.cs'}
        
        try:
            for root, dirs, files in self.workspace_root.rglob('*'):
                for file in files:
                    if file.suffix in code_extensions:
                        try:
                            file_path = Path(root) / file
                            lines = len(file_path.read_text(errors='ignore').split('\n'))
                            total_lines += lines
                        except Exception:
                            pass
        except Exception as e:
            self.logger.warning(f"Could not estimate LOC: {e}")
        
        return max(total_lines, 1000)  # Minimum estimate
    
    def _generate_recommendations(
        self,
        findings: List,
        violations: List,
    ) -> List[str]:
        """Generate risk-based recommendations."""
        recommendations = []
        
        # Critical vulnerabilities
        critical_count = sum(1 for f in findings if f.severity.name == "CRITICAL")
        if critical_count > 0:
            recommendations.append(
                f"⚠️  ADDRESS {critical_count} CRITICAL VULNERABILITIES IMMEDIATELY"
            )
            recommendations.append("1. SQL Injection and Command Injection require urgent fixes")
            recommendations.append("2. Scan git history for accidentally committed credentials")
        
        # Compliance violations
        gdpr_count = sum(1 for v in violations if "gdpr" in str(v.framework).lower())
        hipaa_count = sum(1 for v in violations if "hipaa" in str(v.framework).lower())
        
        if gdpr_count > 0 or hipaa_count > 0:
            recommendations.append("📋 IMPLEMENT COMPLIANCE MEASURES")
            if gdpr_count > 0:
                recommendations.append(f"  - Address {gdpr_count} GDPR violations (encrypt data, document consent)")
            if hipaa_count > 0:
                recommendations.append(f"  - Address {hipaa_count} HIPAA violations (technical safeguards)")
        
        # Credentials
        credential_findings = sum(1 for f in findings if "credentials" in str(f.tags).lower())
        if credential_findings > 0:
            recommendations.append("🔑 REMOVE EXPOSED CREDENTIALS AND USE SECRETS MANAGEMENT")
            recommendations.append("  - Move to environment variables or secrets manager")
            recommendations.append("  - Rotate all exposed credentials")
        
        # General best practices
        recommendations.append("✓ Establish regular security scanning in CI/CD pipeline")
        recommendations.append("✓ Conduct code review for high-severity findings")
        
        return recommendations
