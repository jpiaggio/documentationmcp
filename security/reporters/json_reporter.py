"""
JSON report generator.
"""

import json
from pathlib import Path
from typing import Dict, Any
from ..core.vulnerability import RiskAssessment


class JSONReporter:
    """Generates JSON format security reports."""
    
    def generate_report(self, assessment: RiskAssessment) -> str:
        """Generate JSON report string."""
        return json.dumps(self._assessment_to_dict(assessment), indent=2)
    
    def save_report(self, assessment: RiskAssessment, output_path: Path) -> None:
        """Save JSON report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(self.generate_report(assessment))
    
    def _assessment_to_dict(self, assessment: RiskAssessment) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "metadata": {
                "timestamp": assessment.timestamp.isoformat(),
                "scan_duration_seconds": assessment.scan_duration_seconds,
                "scanned_files": assessment.scanned_files,
            },
            "summary": {
                "overall_risk_level": assessment.overall_risk_level,
                "risk_score": assessment.risk_score,
                "summary_text": assessment.summary,
            },
            "vulnerabilities": {
                "critical": assessment.critical_count,
                "high": assessment.high_count,
                "medium": assessment.medium_count,
                "low": assessment.low_count,
                "total": assessment.critical_count + assessment.high_count + assessment.medium_count + assessment.low_count,
                "findings": [f.to_dict() for f in assessment.vulnerability_findings],
            },
            "compliance": {
                "total_violations": len(assessment.compliance_violations),
                "violations": [v.to_dict() for v in assessment.compliance_violations],
            },
            "recommendations": assessment.recommendations,
        }
