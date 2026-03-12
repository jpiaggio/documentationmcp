"""
Smart Diff Analysis with Context
Improvement #3 from IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md

Provides context-aware change analysis for code reviews:
- Business impact assessment
- Suggested reviewers based on expertise
- Test impact analysis
- Architectural concerns
- Approval requirements
"""

import os
import json
import subprocess
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class ReviewerSuggestion:
    """Suggestion for a code reviewer."""
    name: str
    expertise: List[str]
    reason: str
    confidence: float  # 0-1
    recent_changes_count: int


@dataclass
class TestImpact:
    """Impact on tests from code changes."""
    existing_tests_affected: int
    estimated_test_time_minutes: int
    new_test_files_needed: List[str]
    high_risk_test_areas: List[str]


@dataclass
class ChangesConcern:
    """Identified concern or risk in changes."""
    concern_type: str  # e.g., "circular_dependency", "coupling", "validation_removed"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str
    affected_modules: List[str]
    mitigation: Optional[str] = None


@dataclass
class SmartDiffResult:
    """Complete diff analysis result."""
    lines_added: int
    lines_deleted: int
    files_modified: int
    complexity_change: int
    business_impact: Dict
    suggested_reviewers: List[ReviewerSuggestion]
    test_impact: TestImpact
    concerns: List[ChangesConcern]
    approval_requirements: Dict[str, bool]
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


class SmartDiffAnalyzer:
    """Analyzes code diffs with business and architectural context."""
    
    def __init__(self, repo_path: str, expertise_map: Optional[Dict] = None):
        """
        Initialize the diff analyzer.
        
        Args:
            repo_path: Path to the git repository
            expertise_map: Optional dict mapping developers to their expertise areas
        """
        self.repo_path = repo_path
        self.expertise_map = expertise_map or self._load_expertise_map()
        self.critical_modules = self._identify_critical_modules()
        
    def analyze_pr_changes(self, commit_range: str) -> SmartDiffResult:
        """
        Provide context-aware analysis of PR changes.
        
        Args:
            commit_range: Git commit range (e.g., "main..feature-branch")
            
        Returns:
            SmartDiffResult with comprehensive change analysis
        """
        # Get basic diff stats
        lines_added, lines_deleted = self._get_line_statistics(commit_range)
        files_modified = self._get_modified_files(commit_range)
        
        # Complex analysis
        complexity_change = self._calculate_complexity_change(files_modified)
        business_impact = self._analyze_business_impact(files_modified)
        suggested_reviewers = self._suggest_reviewers(files_modified)
        test_impact = self._analyze_test_impact(files_modified)
        concerns = self._identify_concerns(files_modified, commit_range)
        approval_requirements = self._determine_approval_requirements(concerns, files_modified)
        risk_level = self._calculate_risk_level(concerns, files_modified)
        
        return SmartDiffResult(
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            files_modified=len(files_modified),
            complexity_change=complexity_change,
            business_impact=business_impact,
            suggested_reviewers=suggested_reviewers,
            test_impact=test_impact,
            concerns=concerns,
            approval_requirements=approval_requirements,
            risk_level=risk_level
        )
    
    def _get_line_statistics(self, commit_range: str) -> Tuple[int, int]:
        """Get added/deleted line counts."""
        try:
            output = subprocess.check_output(
                ["git", "diff", "--stat", commit_range],
                cwd=self.repo_path,
                text=True
            )
            
            added, deleted = 0, 0
            for line in output.split('\n'):
                if '+' in line and '-' in line:
                    # Parse lines like: "file.py | 10 +++++++----"
                    parts = line.split('|')
                    if len(parts) == 2:
                        stats = parts[1].strip()
                        plus_count = stats.count('+')
                        minus_count = stats.count('-')
                        added += plus_count
                        deleted += minus_count
            
            return added, deleted
        except subprocess.CalledProcessError:
            return 0, 0
    
    def _get_modified_files(self, commit_range: str) -> List[str]:
        """Get list of modified files."""
        try:
            output = subprocess.check_output(
                ["git", "diff", "--name-only", commit_range],
                cwd=self.repo_path,
                text=True
            )
            return [f for f in output.strip().split('\n') if f]
        except subprocess.CalledProcessError:
            return []
    
    def _calculate_complexity_change(self, files: List[str]) -> int:
        """
        Estimate complexity change from modified files.
        Returns: +/- complexity score change
        """
        complexity_change = 0
        
        # Simple heuristic: analyze imports, function definitions, nested depth
        for file_path in files:
            full_path = os.path.join(self.repo_path, file_path)
            if file_path.endswith('.py') and os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Count nested blocks as complexity indicator
                    max_indent = 0
                    for line in content.split('\n'):
                        if line.strip() and not line.strip().startswith('#'):
                            indent = len(line) - len(line.lstrip())
                            max_indent = max(max_indent, indent)
                    
                    complexity_change += max_indent // 4  # Each indent level = 1 complexity
                except:
                    pass
        
        return complexity_change
    
    def _analyze_business_impact(self, files: List[str]) -> Dict:
        """Analyze business-level impact of changes."""
        affected_features = set()
        customer_journeys = set()
        
        # Map files to business features (customizable)
        business_map = {
            'payment': {'features': ['Payment Processing'], 'journeys': ['Checkout', 'Refund']},
            'order': {'features': ['Order Management'], 'journeys': ['Order Placement', 'Order Tracking']},
            'auth': {'features': ['Authentication'], 'journeys': ['Login', 'Registration']},
            'user': {'features': ['User Management'], 'journeys': ['Profile', 'Settings']},
            'inventory': {'features': ['Inventory Management'], 'journeys': ['Stock Check']},
        }
        
        for file_path in files:
            for key, value in business_map.items():
                if key in file_path.lower():
                    affected_features.update(value['features'])
                    customer_journeys.update(value['journeys'])
        
        return {
            'affected_features': list(affected_features),
            'customer_journeys_affected': len(customer_journeys),
            'affected_journey_names': list(customer_journeys),
            'risk_level': 'HIGH' if len(affected_features) > 2 else 'MEDIUM' if len(affected_features) > 0 else 'LOW'
        }
    
    def _suggest_reviewers(self, files: List[str]) -> List[ReviewerSuggestion]:
        """Suggest reviewers based on their expertise in modified areas."""
        reviewer_scores = defaultdict(lambda: {'score': 0, 'expertise': set(), 'changes': 0})
        
        # Score each potential reviewer
        for file_path in files:
            # Extract module name from file path
            module = file_path.split('/')[0] if '/' in file_path else file_path.split('.')[0]
            
            for reviewer, expertise_list in self.expertise_map.items():
                if any(area.lower() in file_path.lower() or area.lower() in module.lower() 
                       for area in expertise_list):
                    reviewer_scores[reviewer]['score'] += 10
                    reviewer_scores[reviewer]['expertise'].add(
                        next((area for area in expertise_list 
                             if area.lower() in file_path.lower()), 'general')
                    )
                    reviewer_scores[reviewer]['changes'] += 1
        
        suggestions = []
        for reviewer, data in reviewer_scores.items():
            if data['score'] > 0:
                # Get recent change count (mock data)
                recent_changes = data['changes'] * 5  # Simple mock
                
                suggestions.append(ReviewerSuggestion(
                    name=reviewer,
                    expertise=list(data['expertise']),
                    reason=f"Modified {data['changes']} files in their expertise area",
                    confidence=min(1.0, data['score'] / 50),
                    recent_changes_count=recent_changes
                ))
        
        # Sort by confidence descending
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:3]  # Top 3 suggestions
    
    def _analyze_test_impact(self, files: List[str]) -> TestImpact:
        """Analyze impact on test suite."""
        affected_tests = 0
        test_files_needed = []
        high_risk_areas = []
        
        # Map files to test files
        for file_path in files:
            base_name = os.path.basename(file_path)
            test_file = f"test_{base_name}"
            
            # Check if test file exists
            test_path = os.path.join(self.repo_path, test_file)
            if os.path.exists(test_path):
                affected_tests += 1
            else:
                test_files_needed.append(test_file)
            
            # Identify high-risk areas
            if any(risk_area in file_path.lower() for risk_area in ['payment', 'auth', 'security']):
                high_risk_areas.append(file_path)
        
        estimated_time = affected_tests * 3 + len(test_files_needed) * 15
        
        return TestImpact(
            existing_tests_affected=affected_tests,
            estimated_test_time_minutes=estimated_time,
            new_test_files_needed=test_files_needed,
            high_risk_test_areas=high_risk_areas
        )
    
    def _identify_concerns(self, files: List[str], commit_range: str) -> List[ChangesConcern]:
        """Identify architectural and code quality concerns."""
        concerns = []
        
        # Check for critical module modifications
        for file_path in files:
            if any(critical in file_path for critical in self.critical_modules):
                concerns.append(ChangesConcern(
                    concern_type='critical_module_modified',
                    severity='HIGH',
                    description=f"Critical module '{file_path}' has been modified",
                    affected_modules=[file_path],
                    mitigation='Require security review and extensive testing'
                ))
        
        # Check for large imports or removals
        if len(files) > 10:
            concerns.append(ChangesConcern(
                concern_type='large_change_set',
                severity='MEDIUM',
                description=f"{len(files)} files modified - potential scope creep",
                affected_modules=files,
                mitigation='Consider breaking into smaller PRs'
            ))
        
        # Check for validation/logic removals (heuristic)
        for file_path in files:
            full_path = os.path.join(self.repo_path, file_path)
            if file_path.endswith('.py') and os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Flag if validation patterns are removed
                    if 'assert' in content or 'validate' in content:
                        concerns.append(ChangesConcern(
                            concern_type='validation_check',
                            severity='MEDIUM',
                            description=f"Validation patterns detected in {file_path}",
                            affected_modules=[file_path],
                            mitigation='Ensure validation logic is preserved'
                        ))
                except:
                    pass
        
        return concerns
    
    def _determine_approval_requirements(self, concerns: List[ChangesConcern], 
                                       files: List[str]) -> Dict[str, bool]:
        """Determine required approvals based on changes."""
        requirements = {
            'security_review': False,
            'performance_review': False,
            'architecture_review': False,
            'owner_approval': False
        }
        
        # Security review if critical modules or security-related files
        if any('security' in f.lower() or 'auth' in f.lower() or 'payment' in f.lower() 
               for f in files):
            requirements['security_review'] = True
        
        # Architecture review if .py files in core modules
        if any(f.startswith('core/') or f.startswith('agents/') for f in files):
            requirements['architecture_review'] = True
        
        # Owner approval if many concerns
        if len(concerns) > 2:
            requirements['owner_approval'] = True
        
        return requirements
    
    def _calculate_risk_level(self, concerns: List[ChangesConcern], 
                             files: List[str]) -> str:
        """Calculate overall risk level of changes."""
        if not concerns:
            return 'LOW'
        
        has_critical = any(c.severity == 'CRITICAL' for c in concerns)
        if has_critical:
            return 'CRITICAL'
        
        has_high = any(c.severity == 'HIGH' for c in concerns)
        if has_high:
            return 'HIGH'
        
        return 'MEDIUM'
    
    def _identify_critical_modules(self) -> List[str]:
        """Identify which modules are critical and need extra review."""
        return ['payment', 'auth', 'security', 'database', 'core']
    
    def _load_expertise_map(self) -> Dict[str, List[str]]:
        """Load team expertise mapping (mock data)."""
        return {
            'Alice': ['payment', 'fraud_detection', 'python'],
            'Bob': ['order_service', 'inventory', 'sql'],
            'Charlie': ['authentication', 'security', 'encryption'],
            'Diana': ['frontend', 'api', 'performance'],
            'Eve': ['database', 'migration', 'optimization'],
        }
    
    def generate_report(self, result: SmartDiffResult) -> str:
        """Generate a human-readable diff analysis report."""
        report = []
        report.append("=" * 70)
        report.append("SMART DIFF ANALYSIS REPORT")
        report.append("=" * 70)
        
        # Summary
        report.append(f"\n📊 CHANGE SUMMARY")
        report.append(f"  Lines Added: {result.lines_added}")
        report.append(f"  Lines Deleted: {result.lines_deleted}")
        report.append(f"  Files Modified: {result.files_modified}")
        report.append(f"  Complexity Change: {result.complexity_change:+d}")
        report.append(f"  Risk Level: {result.risk_level}")
        
        # Business Impact
        report.append(f"\n💼 BUSINESS IMPACT")
        for feature in result.business_impact['affected_features']:
            report.append(f"  • {feature}")
        report.append(f"  Customer Journeys Affected: {result.business_impact['customer_journeys_affected']}")
        
        # Reviewers
        report.append(f"\n👥 SUGGESTED REVIEWERS")
        for reviewer in result.suggested_reviewers:
            report.append(f"  • {reviewer.name}")
            report.append(f"    Expertise: {', '.join(reviewer.expertise)}")
            report.append(f"    Reason: {reviewer.reason}")
        
        # Test Impact
        report.append(f"\n🧪 TEST IMPACT")
        report.append(f"  Existing Tests Affected: {result.test_impact.existing_tests_affected}")
        report.append(f"  Estimated Test Time: {result.test_impact.estimated_test_time_minutes} minutes")
        if result.test_impact.new_test_files_needed:
            report.append(f"  New Test Files Needed:")
            for test_file in result.test_impact.new_test_files_needed:
                report.append(f"    • {test_file}")
        
        # Concerns
        if result.concerns:
            report.append(f"\n⚠️  IDENTIFIED CONCERNS")
            for concern in result.concerns:
                report.append(f"  [{concern.severity}] {concern.concern_type}")
                report.append(f"    {concern.description}")
                if concern.mitigation:
                    report.append(f"    Mitigation: {concern.mitigation}")
        
        # Approvals
        report.append(f"\n✅ APPROVAL REQUIREMENTS")
        for approval, required in result.approval_requirements.items():
            status = "✓" if required else "✗"
            report.append(f"  {status} {approval.replace('_', ' ').title()}")
        
        report.append("\n" + "=" * 70)
        return '\n'.join(report)


def main():
    """Demo of Smart Diff Analyzer."""
    # Initialize analyzer
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    analyzer = SmartDiffAnalyzer(repo_path)
    
    # Analyze a commit range (using head commit)
    try:
        result = analyzer.analyze_pr_changes("HEAD~5..HEAD")
        
        # Print report
        print(analyzer.generate_report(result))
        
        # Also output as JSON for programmatic access
        print("\n\nJSON OUTPUT:")
        output = {
            'summary': asdict(result),
            'reviewers': [asdict(r) for r in result.suggested_reviewers],
            'concerns': [asdict(c) for c in result.concerns],
        }
        print(json.dumps(output, indent=2, default=str))
        
    except Exception as e:
        print(f"Error analyzing diffs: {e}")


if __name__ == "__main__":
    main()
