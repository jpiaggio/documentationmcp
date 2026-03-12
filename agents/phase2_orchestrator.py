"""
Phase 2 Integrated Workflow
Combines all Phase 2 improvements into unified codebase analysis workflow.

Phase 2 Improvements:
- #2 Codebase Health Dashboard
- #6 Architecture Drift Detection  
- #14 Team Expertise Mapping

This module orchestrates all three and generates comprehensive reports.
"""

import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

from codebase_health_monitor import CodebaseHealthMonitor, HealthReport
from architecture_validator import ArchitectureValidator, ArchitectureValidationReport, ArchitectureRules, LayerDefinition
from expertise_mapper import ExpertiseMapper, ExpertiseMap


@dataclass
class Phase2Report:
    """Comprehensive Phase 2 analysis report."""
    timestamp: str
    health_report: HealthReport
    architecture_report: ArchitectureValidationReport
    expertise_map: ExpertiseMap
    executive_summary: str
    critical_issues: Dict  # Issues requiring immediate attention
    recommendations_prioritized: list


class Phase2Orchestrator:
    """Orchestrates all Phase 2 improvements."""
    
    def __init__(self, repo_path: str, architecture_rules: Optional[ArchitectureRules] = None):
        """
        Initialize Phase 2 orchestrator.
        
        Args:
            repo_path: Path to repository
            architecture_rules: Custom architecture rules
        """
        self.repo_path = repo_path
        
        # Initialize all Phase 2 agents
        self.health_monitor = CodebaseHealthMonitor(repo_path)
        self.architecture_validator = ArchitectureValidator(repo_path, architecture_rules)
        self.expertise_mapper = ExpertiseMapper(repo_path)
    
    def run_complete_analysis(self) -> Phase2Report:
        """
        Run complete Phase 2 analysis with all three improvements.
        
        Returns:
            Comprehensive Phase 2 report
        """
        print("\n" + "="*80)
        print("🚀 PHASE 2: FOUNDATION IMPROVEMENTS")
        print("="*80)
        
        # Run all three analyses in parallel (conceptually)
        print("\n[1/3] 📊 Analyzing Codebase Health...")
        health_report = self.health_monitor.generate_health_report()
        
        print("[2/3] 🏗️ Validating Architecture...")
        architecture_report = self.architecture_validator.validate_architecture()
        
        print("[3/3] 👥 Mapping Team Expertise...")
        expertise_map = self.expertise_mapper.map_team_expertise()
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            health_report, architecture_report, expertise_map
        )
        
        # Identify critical issues
        critical_issues = self._identify_critical_issues(
            health_report, architecture_report, expertise_map
        )
        
        # Generate prioritized recommendations
        recommendations = self._generate_prioritized_recommendations(
            health_report, architecture_report, expertise_map
        )
        
        report = Phase2Report(
            timestamp=datetime.now().isoformat(),
            health_report=health_report,
            architecture_report=architecture_report,
            expertise_map=expertise_map,
            executive_summary=executive_summary,
            critical_issues=critical_issues,
            recommendations_prioritized=recommendations
        )
        
        return report
    
    def generate_html_report(self, report: Phase2Report, output_path: str):
        """
        Generate HTML report from Phase 2 analysis.
        
        Args:
            report: Phase2Report from run_complete_analysis()
            output_path: Path to save HTML report
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phase 2 Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .section {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 32px; font-weight: bold; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .status-good {{ color: #10b981; }}
        .status-warning {{ color: #f59e0b; }}
        .status-critical {{ color: #ef4444; }}
        .violation {{ border-left: 4px solid #ef4444; padding: 15px; margin-bottom: 10px; background: #fef2f2; }}
        .recommendation {{ border-left: 4px solid #3b82f6; padding: 15px; margin-bottom: 10px; background: #eff6ff; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        tr:hover {{ background: #f9fafb; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Phase 2: Foundation Improvements Report</h1>
            <p>Comprehensive codebase, architecture, and team analysis</p>
            <p>Generated: {report.timestamp}</p>
        </div>
        
        <div class="section">
            <h2>📋 Executive Summary</h2>
            <p>{report.executive_summary}</p>
        </div>
        
        <!-- Health Report Section -->
        <div class="section">
            <h2>📊 Codebase Health Dashboard</h2>
            <div class="metric">
                <div class="metric-value {self._get_health_class(report.health_report.overall_health)}">
                    {report.health_report.overall_health:.1f}
                </div>
                <div class="metric-label">Overall Health</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.health_report.test_coverage:.1f}%</div>
                <div class="metric-label">Test Coverage</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.health_report.documentation_coverage:.1f}%</div>
                <div class="metric-label">Documentation</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.health_report.circular_dependencies}</div>
                <div class="metric-label">Circular Dependencies</div>
            </div>
            
            <h3>Key Metrics</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                    <th>Status</th>
                    <th>Recommendation</th>
                </tr>
        """
        
        for metric_name, metric in report.health_report.health_metrics.items():
            status_class = f"status-{metric.status.lower()}"
            html_content += f"""
                <tr>
                    <td>{metric.name}</td>
                    <td>{metric.value:.1f}</td>
                    <td><span class="{status_class}">{metric.status}</span></td>
                    <td>{metric.recommendation or 'N/A'}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h3>🔥 Top Complexity Hotspots</h3>
            <table>
                <tr>
                    <th>Module</th>
                    <th>Complexity</th>
                    <th>LOC</th>
                    <th>Priority</th>
                </tr>
        """
        
        for hotspot in report.health_report.complexity_hotspots[:10]:
            html_content += f"""
                <tr>
                    <td>{hotspot.module_name}</td>
                    <td>{hotspot.complexity_score:.1f}</td>
                    <td>{hotspot.lines_of_code}</td>
                    <td>{hotspot.refactoring_priority}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </div>
        
        <!-- Architecture Report Section -->
        <div class="section">
            <h2>🏗️ Architecture Validation</h2>
            <div class="metric">
                <div class="metric-value {self._get_compliance_class(report.architecture_report.compliance_score)}">
                    {report.architecture_report.compliance_score:.1f}
                </div>
                <div class="metric-label">Compliance Score</div>
            </div>
            <div class="metric">
                <div class="metric-value status-critical">{report.architecture_report.critical_violations}</div>
                <div class="metric-label">Critical Issues</div>
            </div>
            <div class="metric">
                <div class="metric-value status-warning">{report.architecture_report.high_violations}</div>
                <div class="metric-label">High Issues</div>
            </div>
            
            <h3>Violations by Type</h3>
            <ul>
                <li>Circular Dependencies: {report.architecture_report.circular_dependencies}</li>
                <li>Layer Violations: {report.architecture_report.layer_violations}</li>
                <li>Naming Violations: {report.architecture_report.naming_violations}</li>
            </ul>
            
            <h3>Top Violations</h3>
        """
        
        for violation in report.architecture_report.violations[:10]:
            severity_class = f"status-{violation.severity.value.lower()}"
            html_content += f"""
            <div class="violation">
                <strong><span class="{severity_class}">{violation.severity.value}</span> - {violation.violation_type}</strong><br>
                <strong>Module:</strong> {violation.module_name}<br>
                <strong>Description:</strong> {violation.violation_description}<br>
                <strong>Impact:</strong> {violation.impact}<br>
                <strong>Remediation:</strong> {violation.remediation}
            </div>
            """
        
        html_content += """
        </div>
        
        <!-- Expertise Map Section -->
        <div class="section">
            <h2>👥 Team Expertise Map</h2>
            <div class="metric">
                <div class="metric-value">{len(report.expertise_map.team_members)}</div>
                <div class="metric-label">Team Members</div>
            </div>
            <div class="metric">
                <div class="metric-value {self._get_health_class(report.expertise_map.team_health_score)}">
                    {report.expertise_map.team_health_score:.1f}
                </div>
                <div class="metric-label">Team Health Score</div>
            </div>
            
            <h3>Team Members & Expertise</h3>
            <table>
                <tr>
                    <th>Member</th>
                    <th>Commits</th>
                    <th>Primary Domains</th>
                    <th>Languages</th>
                    <th>Confidence</th>
                </tr>
        """.format(**{
            'team_members': len(report.expertise_map.team_members),
            'health_score': report.expertise_map.team_health_score,
        })
        
        for member_name, profile in list(report.expertise_map.team_members.items())[:10]:
            html_content += f"""
                <tr>
                    <td>{member_name}</td>
                    <td>{profile.recent_changes}</td>
                    <td>{', '.join(profile.primary_domains[:3]) or 'N/A'}</td>
                    <td>{', '.join(profile.primary_languages) or 'N/A'}</td>
                    <td>{profile.expertise_confidence:.1%}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h3>🚨 Critical Issues</h3>
        """
        
        if report.expertise_map.bus_factor.at_risk_modules:
            html_content += f"""
            <h4>Single Points of Failure ({len(report.expertise_map.bus_factor.at_risk_modules)})</h4>
            <ul>
        """
            for module in report.expertise_map.bus_factor.at_risk_modules[:10]:
                html_content += f"<li>{module}</li>"
            html_content += "</ul>"
        
        if report.expertise_map.knowledge_gaps:
            html_content += f"""
            <h4>Knowledge Gaps ({len(report.expertise_map.knowledge_gaps)})</h4>
            <ul>
        """
            for gap in report.expertise_map.knowledge_gaps[:10]:
                html_content += f"<li>{gap.criticality}: {gap.area}</li>"
            html_content += "</ul>"
        
        html_content += """
        </div>
        
        <!-- Critical Issues Section -->
        <div class="section">
            <h2>🔴 Critical Issues Requiring Immediate Attention</h2>
        """
        
        for issue in report.critical_issues:
            html_content += f"""
            <div class="violation">
                <strong>⚠️ {issue['type']}</strong><br>
                {issue['description']}
            </div>
            """
        
        html_content += """
        </div>
        
        <!-- Recommendations Section -->
        <div class="section">
            <h2>💡 Prioritized Recommendations (Next Steps)</h2>
        """
        
        for i, rec in enumerate(report.recommendations_prioritized, 1):
            priority_class = (
                "status-critical" if rec['priority'] == 'CRITICAL' else
                "status-warning" if rec['priority'] == 'HIGH' else
                "status-good"
            )
            html_content += f"""
            <div class="recommendation">
                <strong>[{i}] <span class="{priority_class}">{rec['priority']}</span> - {rec['title']}</strong><br>
                <strong>Impact:</strong> {rec['impact']}<br>
                <strong>Effort:</strong> {rec['effort']}<br>
                <strong>Action:</strong> {rec['action']}
            </div>
            """
        
        html_content += """
        </div>
    </div>
</body>
</html>
        """
        
        # Write HTML report
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved to: {output_path}")
    
    # ========== Private Methods ==========
    
    def _generate_executive_summary(
        self,
        health_report: HealthReport,
        architecture_report: ArchitectureValidationReport,
        expertise_map: ExpertiseMap
    ) -> str:
        """Generate executive summary of all findings."""
        summary_parts = []
        
        # Health summary
        if health_report.overall_health < 50:
            summary_parts.append(
                f"🔴 **Codebase Health**: Critical status ({health_report.overall_health:.1f}/100). "
                f"Immediate action needed on complexity hotspots and test coverage."
            )
        elif health_report.overall_health < 70:
            summary_parts.append(
                f"🟡 **Codebase Health**: Warning status ({health_report.overall_health:.1f}/100). "
                f"Several areas need attention."
            )
        else:
            summary_parts.append(
                f"✅ **Codebase Health**: Good ({health_report.overall_health:.1f}/100). "
                f"Continue maintaining and improving."
            )
        
        # Architecture summary
        if architecture_report.critical_violations > 0:
            summary_parts.append(
                f"🔴 **Architecture**: {architecture_report.critical_violations} critical violations detected. "
                f"Compliance score: {architecture_report.compliance_score:.1f}/100. Refactoring required."
            )
        elif architecture_report.high_violations > 0:
            summary_parts.append(
                f"🟡 **Architecture**: {architecture_report.high_violations} high-severity violations. "
                f"Plan refactoring work."
            )
        else:
            summary_parts.append(
                f"✅ **Architecture**: Compliant ({architecture_report.compliance_score:.1f}/100)"
            )
        
        # Team summary
        if expertise_map.team_health_score < 50:
            summary_parts.append(
                f"🔴 **Team Health**: Low ({expertise_map.team_health_score:.1f}/100). "
                f"Significant knowledge gaps and single points of failure."
            )
        elif expertise_map.team_health_score < 70:
            summary_parts.append(
                f"🟡 **Team Health**: Moderate ({expertise_map.team_health_score:.1f}/100). "
                f"Some knowledge sharing and cross-training needed."
            )
        else:
            summary_parts.append(
                f"✅ **Team Health**: Good ({expertise_map.team_health_score:.1f}/100). "
                f"Well-distributed expertise."
            )
        
        return "\n\n".join(summary_parts)
    
    def _identify_critical_issues(
        self,
        health_report: HealthReport,
        architecture_report: ArchitectureValidationReport,
        expertise_map: ExpertiseMap
    ) -> Dict:
        """Identify critical issues across all three areas."""
        critical = {
            'health': [],
            'architecture': [],
            'expertise': []
        }
        
        # Health critical issues
        if health_report.overall_health < 40:
            critical['health'].append({
                'type': 'Critical Health Degradation',
                'description': f'Overall health score {health_report.overall_health:.1f}/100 indicates serious issues.'
            })
        
        if health_report.circular_dependencies > 10:
            critical['health'].append({
                'type': 'Excessive Circular Dependencies',
                'description': f'{health_report.circular_dependencies} circular dependency cycles detected.'
            })
        
        # Architecture critical issues
        for violation in architecture_report.violations:
            if violation.severity.value == 'CRITICAL':
                critical['architecture'].append({
                    'type': 'CRITICAL Architecture Violation',
                    'description': f'{violation.violation_description} - {violation.impact}'
                })
        
        # Expertise critical issues
        if len(expertise_map.bus_factor.at_risk_modules) > 0:
            critical['expertise'].append({
                'type': 'Single Points of Failure',
                'description': f'{len(expertise_map.bus_factor.at_risk_modules)} modules have only one expert.'
            })
        
        return critical
    
    def _generate_prioritized_recommendations(
        self,
        health_report: HealthReport,
        architecture_report: ArchitectureValidationReport,
        expertise_map: ExpertiseMap
    ) -> list:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Health recommendations
        if health_report.complexity_hotspots:
            top_hotspot = health_report.complexity_hotspots[0]
            recommendations.append({
                'priority': 'CRITICAL',
                'title': f'Refactor High-Complexity Module: {top_hotspot.module_name}',
                'impact': 'Reduce defects and improve maintainability',
                'effort': f'{top_hotspot.estimated_refactor_time_hours:.1f} hours',
                'action': f'Break down {top_hotspot.module_name} (complexity: {top_hotspot.complexity_score:.1f})'
            })
        
        # Architecture recommendations
        critical_arch_violat = [v for v in architecture_report.violations if v.severity.value == 'CRITICAL']
        if critical_arch_violat:
            first_violat = critical_arch_violat[0]
            recommendations.append({
                'priority': 'CRITICAL',
                'title': f'Fix Architecture Violation: {first_violat.violation_type}',
                'impact': 'Restore architectural integrity',
                'effort': '2-3 days',
                'action': first_violat.remediation
            })
        
        # Team expertise recommendations
        if expertise_map.bus_factor.recommended_actions:
            recommendations.append({
                'priority': 'HIGH',
                'title': 'Distribute Knowledge to Reduce Bus Factor',
                'impact': 'Reduce risk of key person dependency',
                'effort': '2-3 weeks',
                'action': expertise_map.bus_factor.recommended_actions[0]
            })
        
        return recommendations
    
    def _get_health_class(self, score: float) -> str:
        """Get CSS class for health score."""
        if score >= 70:
            return "status-good"
        elif score >= 50:
            return "status-warning"
        else:
            return "status-critical"
    
    def _get_compliance_class(self, score: float) -> str:
        """Get CSS class for compliance score."""
        if score >= 80:
            return "status-good"
        elif score >= 60:
            return "status-warning"
        else:
            return "status-critical"


def main():
    """Demo: Run complete Phase 2 analysis."""
    import sys
    from dataclasses import asdict
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    output_html = sys.argv[2] if len(sys.argv) > 2 else 'phase2_report.html'
    
    # Run orchestrator
    orchestrator = Phase2Orchestrator(repo_path)
    report = orchestrator.run_complete_analysis()
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 2 ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nExecutive Summary:\n{report.executive_summary}")
    
    # Generate HTML report
    orchestrator.generate_html_report(report, output_html)


if __name__ == '__main__':
    from dataclasses import dataclass
    main()
