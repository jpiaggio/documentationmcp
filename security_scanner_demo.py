"""
Quick start demo for Security & Compliance Scanner.

Run this script to demonstrate the scanner capabilities.
"""

from pathlib import Path
from security.orchestrator import SecurityOrchestrator


def demo_basic_scan():
    """Demo: Basic security scan."""
    print("=" * 80)
    print("🔒 SECURITY & COMPLIANCE SCANNER - QUICK START")
    print("=" * 80)
    print()
    
    # Create orchestrator for current workspace
    workspace = Path.cwd()
    orchestrator = SecurityOrchestrator(workspace)
    
    print(f"📍 Scanning workspace: {workspace}")
    print()
    
    # Run scan
    assessment = orchestrator.scan(
        included_paths=[Path(".")],
        excluded_paths=[Path(".venv"), Path(".git"), Path("__pycache__")],
        check_env_files=True,
        check_config_files=True,
        verbose=True,
    )
    
    # Display results
    print()
    print("=" * 80)
    print("📊 ASSESSMENT RESULTS")
    print("=" * 80)
    print()
    print(assessment.summary)
    print()
    
    # Save reports
    reports_dir = workspace / "security_reports"
    report_paths = orchestrator.generate_reports(
        reports_dir,
        formats=["json", "html", "sarif"]
    )
    
    print()
    print("=" * 80)
    print("📁 GENERATED REPORTS")
    print("=" * 80)
    for format_type, path in report_paths.items():
        print(f"  {format_type.upper():<8}: {path}")
    print()
    
    # Display key findings
    if assessment.vulnerability_findings:
        print("=" * 80)
        print("🚨 TOP VULNERABILITIES")
        print("=" * 80)
        
        # Group by severity
        by_severity = {}
        for finding in assessment.vulnerability_findings:
            sev = finding.severity.name
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(finding)
        
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            if severity in by_severity:
                findings = by_severity[severity]
                print(f"\n{severity} ({len(findings)} issues):")
                for i, finding in enumerate(findings[:3], 1):
                    print(f"  {i}. {finding.title}")
                    print(f"     Location: {finding.location.file_path}:{finding.location.line_number}")
                    print(f"     CWE: {finding.cwe_id}")
                    print()
    
    print("=" * 80)
    print("✅ Scan complete! Review detailed reports for remediation steps.")
    print("=" * 80)


if __name__ == "__main__":
    demo_basic_scan()
