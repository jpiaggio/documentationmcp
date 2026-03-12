"""
HTML dashboard report generator.
"""

from pathlib import Path
from ..core.vulnerability import RiskAssessment, Severity


class HTMLReporter:
    """Generates interactive HTML dashboard reports."""
    
    def generate_report(self, assessment: RiskAssessment) -> str:
        """Generate HTML report string."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security & Compliance Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.2em;
            margin: 15px 0;
        }}
        
        .risk-critical {{
            background: #ff4444;
            color: white;
        }}
        
        .risk-high {{
            background: #ff8844;
            color: white;
        }}
        
        .risk-medium {{
            background: #ffbb33;
            color: white;
        }}
        
        .risk-low {{
            background: #44bb44;
            color: white;
        }}
        
        .risk-info {{
            background: #4488ff;
            color: white;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .section h2::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 30px;
            background: #667eea;
            margin-right: 15px;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric h3 {{
            color: #999;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .metric .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        
        .metric.critical .value {{ color: #ff4444; }}
        .metric.high .value {{ color: #ff8844; }}
        .metric.medium .value {{ color: #ffbb33; }}
        .metric.low .value {{ color: #44bb44; }}
        
        .findings-list {{
            border-left: 4px solid #ddd;
            padding-left: 20px;
        }}
        
        .finding {{
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .finding.critical {{
            border-left: 4px solid #ff4444;
            background: #fff5f5;
        }}
        
        .finding.high {{
            border-left: 4px solid #ff8844;
            background: #fffaf5;
        }}
        
        .finding.medium {{
            border-left: 4px solid #ffbb33;
            background: #fffef5;
        }}
        
        .finding.low {{
            border-left: 4px solid #44bb44;
            background: #f5fff5;
        }}
        
        .finding-title {{
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 8px;
        }}
        
        .finding-location {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        
        .finding-description {{
            color: #555;
            margin-bottom: 10px;
        }}
        
        .finding-severity {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .finding-severity.critical {{
            background: #ff4444;
            color: white;
        }}
        
        .finding-severity.high {{
            background: #ff8844;
            color: white;
        }}
        
        .finding-severity.medium {{
            background: #ffbb33;
            color: white;
        }}
        
        .finding-severity.low {{
            background: #44bb44;
            color: white;
        }}
        
        .code-context {{
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
            overflow-x: auto;
            margin-top: 10px;
        }}
        
        .remediation {{
            background: #e8f5e9;
            border-left: 4px solid #44bb44;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }}
        
        .remediation h4 {{
            color: #2e7d32;
            margin-bottom: 8px;
        }}
        
        .remediation pre {{
            background: white;
            border: 1px solid #c8e6c9;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
            font-size: 0.85em;
        }}
        
        .no-findings {{
            background: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            color: #2e7d32;
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }}
        
        .recommendations {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        
        .recommendations h3 {{
            color: #856404;
            margin-bottom: 15px;
        }}
        
        .recommendations ul {{
            list-style-position: inside;
            color: #333;
        }}
        
        .recommendations li {{
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {self._render_header(assessment)}
        
        <div class="content">
            {self._render_summary(assessment)}
            {self._render_metrics(assessment)}
            {self._render_findings(assessment)}
            {self._render_compliance(assessment)}
            {self._render_recommendations(assessment)}
        </div>
        
        {self._render_footer(assessment)}
    </div>
</body>
</html>"""
    
    def save_report(self, assessment: RiskAssessment, output_path: Path) -> None:
        """Save HTML report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(self.generate_report(assessment))
    
    def _render_header(self, assessment: RiskAssessment) -> str:
        """Render header section."""
        risk_class = self._get_risk_class(assessment.overall_risk_level)
        return f"""<div class="header">
            <h1>Security & Compliance Assessment</h1>
            <div class="risk-badge risk-{risk_class}">
                {assessment.overall_risk_level} - Score: {assessment.risk_score}/100
            </div>
            <p>Comprehensive security analysis and compliance review</p>
        </div>
        """
    
    def _render_summary(self, assessment: RiskAssessment) -> str:
        """Render summary section."""
        return f"""<div class="section">
            <h2>Executive Summary</h2>
            <p>{assessment.summary}</p>
        </div>"""
    
    def _render_metrics(self, assessment: RiskAssessment) -> str:
        """Render metrics section."""
        return f"""<div class="section">
            <h2>Vulnerability Metrics</h2>
            <div class="metrics">
                <div class="metric critical">
                    <h3>Critical</h3>
                    <div class="value">{assessment.critical_count}</div>
                </div>
                <div class="metric high">
                    <h3>High</h3>
                    <div class="value">{assessment.high_count}</div>
                </div>
                <div class="metric medium">
                    <h3>Medium</h3>
                    <div class="value">{assessment.medium_count}</div>
                </div>
                <div class="metric low">
                    <h3>Low</h3>
                    <div class="value">{assessment.low_count}</div>
                </div>
                <div class="metric">
                    <h3>Total Files Scanned</h3>
                    <div class="value">{assessment.scanned_files}</div>
                </div>
            </div>
        </div>"""
    
    def _render_findings(self, assessment: RiskAssessment) -> str:
        """Render findings section."""
        if not assessment.vulnerability_findings:
            return """<div class="section">
                <h2>Vulnerability Findings</h2>
                <div class="no-findings">
                    ✓ No vulnerabilities found
                </div>
            </div>"""
        
        findings_html = '<div class="section"><h2>Vulnerability Findings</h2><div class="findings-list">'
        
        for finding in assessment.vulnerability_findings:
            severity_class = self._get_severity_class(finding.severity)
            findings_html += f"""<div class="finding {severity_class}">
                <span class="finding-severity {severity_class}">{finding.severity.name}</span>
                <div class="finding-title">{finding.title}</div>
                <div class="finding-location">{finding.location.file_path}:{finding.location.line_number}</div>
                <div class="finding-description">{finding.description}</div>
            """
            
            if finding.location.line_content:
                findings_html += f"""<div class="code-context"><pre>{finding.location.line_content}</pre></div>"""
            
            if finding.remediation:
                findings_html += f"""<div class="remediation">
                    <h4>How to Fix</h4>
                    <pre>{finding.remediation}</pre>
                </div>"""
            
            findings_html += "</div>"
        
        findings_html += "</div></div>"
        return findings_html
    
    def _render_compliance(self, assessment: RiskAssessment) -> str:
        """Render compliance section."""
        if not assessment.compliance_violations:
            return """<div class="section">
                <h2>Compliance Violations</h2>
                <div class="no-findings">
                    ✓ No compliance violations found
                </div>
            </div>"""
        
        violations_html = '<div class="section"><h2>Compliance Violations</h2><div class="findings-list">'
        
        for violation in assessment.compliance_violations:
            severity_class = self._get_severity_class(violation.severity)
            violations_html += f"""<div class="finding {severity_class}">
                <span class="finding-severity {severity_class}">{violation.severity.name}</span>
                <div class="finding-title">{violation.framework.value.upper()}: {violation.requirement}</div>
                <div class="finding-description">{violation.violation_description}</div>
            """
            
            if violation.remediation_steps:
                violations_html += """<div class="remediation">
                    <h4>Remediation Steps</h4>
                    <ul>"""
                for step in violation.remediation_steps:
                    violations_html += f"<li>{step}</li>"
                violations_html += """</ul></div>"""
            
            violations_html += "</div>"
        
        violations_html += "</div></div>"
        return violations_html
    
    def _render_recommendations(self, assessment: RiskAssessment) -> str:
        """Render recommendations section."""
        if not assessment.recommendations:
            return ""
        
        recommendations_html = """<div class="section">
            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>"""
        
        for rec in assessment.recommendations:
            recommendations_html += f"<li>{rec}</li>"
        
        recommendations_html += """</ul>
            </div>
        </div>"""
        return recommendations_html
    
    def _render_footer(self, assessment: RiskAssessment) -> str:
        """Render footer section."""
        return f"""<div class="footer">
            <p>Generated on {assessment.timestamp.strftime('%Y-%m-%d %H:%M:%S')} (UTC)</p>
            <p>Scan completed in {assessment.scan_duration_seconds:.2f} seconds</p>
        </div>
        """
    
    def _get_risk_class(self, risk_level: str) -> str:
        """Convert risk level to CSS class name."""
        return risk_level.lower()
    
    def _get_severity_class(self, severity: Severity) -> str:
        """Convert severity to CSS class name."""
        return severity.name.lower()
