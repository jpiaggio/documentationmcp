"""
Selective Dependency Impact Analysis
Improvement #1 from IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md

Analyzes which modules, systems, and business processes are affected by code changes.
- Identifies direct dependents (imports this file)
- Identifies transitive dependents (2+ hops away)
- Maps business process impacts
- Identifies affected customer journeys
- Calculates risk levels
"""

import os
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import re
import ast


@dataclass
class DependencyNode:
    """Represents a module and its dependencies."""
    module_name: str
    module_type: str  # "service", "utility", "core", "api"
    dependencies: Set[str]
    dependents: Set[str]
    business_functions: List[str]
    criticality: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    is_service_boundary: bool = False


@dataclass
class ImpactResult:
    """Result of impact analysis."""
    direct_dependents: List[str]  # Modules that directly import this file
    transitive_dependents: List[str]  # Modules 2+ hops away
    business_impacts: List[str]  # Business processes affected
    affected_customer_journeys: List[str]
    risk_level: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    estimated_test_time_hours: float
    affected_teams: List[str]
    customer_impact_summary: str
    circular_dependencies_introduced: List[List[str]]
    change_propagation_depth: int  # How many levels deep does change propagate?
    suggested_test_matrix: Dict[str, List[str]]  # Module -> required tests


class SelectiveImpactAnalyzer:
    """Analyzes the impact of changing a module on the codebase."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the impact analyzer.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = repo_path
        self.dependency_graph: Dict[str, DependencyNode] = {}
        self.business_map = self._initialize_business_map()
        self._build_dependency_graph()
    
    def analyze_change_impact(self, file_path: str, change_type: str = "modification") -> ImpactResult:
        """
        Analyze the impact of changing a specific file.
        
        Args:
            file_path: Path to the file being changed
            change_type: Type of change - "modification", "deletion", "api_change"
            
        Returns:
            ImpactResult with detailed impact analysis
        """
        module_name = self._normalize_module_name(file_path)
        
        # Get direct and transitive dependents
        direct_dependents = self._get_direct_dependents(module_name)
        transitive_dependents = self._get_transitive_dependents(module_name, hops=2)
        
        # Calculate severity based on change type
        if change_type == "deletion":
            severity = "CRITICAL"
        elif change_type == "api_change":
            severity = "HIGH" if len(direct_dependents) > 5 else "MEDIUM"
        else:  # modification
            severity = "MEDIUM"
        
        # Analyze business impact
        business_impacts = self._analyze_business_impact(module_name, direct_dependents)
        affected_journeys = self._get_affected_customer_journeys(business_impacts)
        
        # Calculate risk
        risk_level = self._calculate_risk_level(
            direct_dependents, transitive_dependents, business_impacts
        )
        
        # Estimate testing effort
        test_time = self._estimate_test_time(direct_dependents, transitive_dependents)
        
        # Identify affected teams
        affected_teams = self._identify_affected_teams(direct_dependents)
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(module_name)
        
        # Build suggested test matrix
        test_matrix = self._build_test_matrix(module_name, direct_dependents)
        
        # Calculate propagation depth
        propagation_depth = self._calculate_propagation_depth(module_name)
        
        customer_impact = self._generate_customer_impact_summary(
            affected_journeys, risk_level
        )
        
        return ImpactResult(
            direct_dependents=direct_dependents,
            transitive_dependents=transitive_dependents,
            business_impacts=business_impacts,
            affected_customer_journeys=affected_journeys,
            risk_level=risk_level,
            estimated_test_time_hours=test_time,
            affected_teams=affected_teams,
            customer_impact_summary=customer_impact,
            circular_dependencies_introduced=circular_deps,
            change_propagation_depth=propagation_depth,
            suggested_test_matrix=test_matrix
        )
    
    def _build_dependency_graph(self):
        """Build the module dependency graph from the repository."""
        # Scan Python files to extract imports
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_name = self._normalize_module_name(file_path)
                    
                    # Extract dependencies
                    dependencies = self._extract_dependencies(file_path)
                    
                    # Determine module type
                    module_type = self._determine_module_type(file_path)
                    
                    # Create node
                    node = DependencyNode(
                        module_name=module_name,
                        module_type=module_type,
                        dependencies=set(dependencies),
                        dependents=set(),
                        business_functions=self._extract_business_functions(file_path),
                        criticality=self._assess_criticality(file_path, dependencies),
                    )
                    
                    self.dependency_graph[module_name] = node
        
        # Build reverse dependencies
        for module_name, node in self.dependency_graph.items():
            for dep in node.dependencies:
                if dep in self.dependency_graph:
                    self.dependency_graph[dep].dependents.add(module_name)
    
    def _extract_dependencies(self, file_path: str) -> List[str]:
        """Extract import statements from a Python file."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST to get imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.append(node.module)
            except SyntaxError:
                # Fallback to regex parsing
                imports = re.findall(r'^\s*(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
                dependencies.extend([imp for imp in imports])
        
        except Exception as e:
            pass
        
        return list(set(dependencies))
    
    def _normalize_module_name(self, file_path: str) -> str:
        """Convert file path to module name."""
        # Remove repo path prefix
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        # Convert path to module name
        module_name = rel_path.replace(os.sep, '.').replace('.py', '')
        return module_name
    
    def _get_direct_dependents(self, module_name: str) -> List[str]:
        """Get modules that directly import this module."""
        if module_name not in self.dependency_graph:
            return []
        
        return list(self.dependency_graph[module_name].dependents)
    
    def _get_transitive_dependents(self, module_name: str, hops: int = 2) -> List[str]:
        """Use BFS to find all modules that depend on this module (within N hops)."""
        visited = set()
        queue = deque([(module_name, 0)])
        transitive = set()
        
        while queue:
            current, depth = queue.popleft()
            
            if depth > 0 and depth <= hops:
                transitive.add(current)
            
            if depth < hops and current in self.dependency_graph:
                dependents = self.dependency_graph[current].dependents
                for dep in dependents:
                    if dep not in visited:
                        visited.add(dep)
                        queue.append((dep, depth + 1))
        
        # Remove direct dependents from transitive
        direct = set(self._get_direct_dependents(module_name))
        return list(transitive - direct)
    
    def _analyze_business_impact(self, module_name: str, dependents: List[str]) -> List[str]:
        """Map changed module to business processes."""
        impacts = set()
        
        # Direct impact from the module itself
        if module_name in self.business_map:
            impacts.update(self.business_map[module_name])
        
        # Transitive impact through dependents
        for dependent in dependents:
            if dependent in self.business_map:
                impacts.update(self.business_map[dependent])
        
        return list(impacts)
    
    def _get_affected_customer_journeys(self, business_impacts: List[str]) -> List[str]:
        """Map business impacts to customer journeys."""
        journey_map = {
            'payment': ['Checkout', 'Refund', 'Dispute Resolution'],
            'order': ['Order Placement', 'Order Tracking', 'Returns'],
            'auth': ['Login', 'Registration', 'Password Reset'],
            'user': ['Profile Management', 'Account Settings'],
            'inventory': ['Product Discovery', 'Stock Check', 'Availability Check'],
            'notification': ['Order Alerts', 'Promotional Emails'],
            'analytics': ['Reporting', 'Dashboards'],
        }
        
        journeys = set()
        for impact in business_impacts:
            impact_lower = impact.lower()
            for key, journey_list in journey_map.items():
                if key in impact_lower:
                    journeys.update(journey_list)
        
        return list(journeys)
    
    def _calculate_risk_level(self, direct: List[str], transitive: List[str], 
                             business_impacts: List[str]) -> str:
        """Calculate overall risk level."""
        # Risk based on scope of impact
        total_impact = len(direct) + len(transitive)
        
        if total_impact > 10 or any('payment' in b.lower() or 'auth' in b.lower() 
                                     for b in business_impacts):
            return "CRITICAL"
        elif total_impact > 5 or len(business_impacts) > 2:
            return "HIGH"
        elif total_impact > 2 or len(business_impacts) > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _estimate_test_time(self, direct: List[str], transitive: List[str]) -> float:
        """Estimate testing effort in hours."""
        # Unit tests for direct dependents: 15 min each
        # Integration tests for transitive: 30 min each
        # System tests: 2 hours
        
        unit_test_time = len(direct) * 0.25
        integration_test_time = len(transitive) * 0.5
        system_test_time = 2.0 if (len(direct) + len(transitive)) > 5 else 1.0
        
        return unit_test_time + integration_test_time + system_test_time
    
    def _identify_affected_teams(self, dependents: List[str]) -> List[str]:
        """Map dependents to teams."""
        team_map = {
            'payment': ['Payments Team', 'Backend Team'],
            'order': ['Order Fulfillment', 'Backend Team'],
            'auth': ['Security Team', 'Backend Team'],
            'frontend': ['Frontend Team', 'UI Team'],
            'api': ['API Team', 'Integration Team'],
            'database': ['Data Engineering', 'Infrastructure'],
        }
        
        teams = set()
        for dependent in dependents:
            for key, team_list in team_map.items():
                if key in dependent.lower():
                    teams.update(team_list)
        
        # Default team
        if not teams:
            teams.add('Development Team')
        
        return list(teams)
    
    def _detect_circular_dependencies(self, module_name: str) -> List[List[str]]:
        """Detect circular dependencies involving this module."""
        cycles = []
        
        if module_name not in self.dependency_graph:
            return cycles
        
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node, target):
            if node in rec_stack and node == target:
                cycles.append(path.copy())
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in self.dependency_graph:
                for neighbor in self.dependency_graph[node].dependencies:
                    if neighbor in self.dependency_graph:
                        dfs(neighbor, target)
            
            path.pop()
            rec_stack.remove(node)
        
        dfs(module_name, module_name)
        return cycles
    
    def _build_test_matrix(self, module_name: str, dependents: List[str]) -> Dict[str, List[str]]:
        """Build a suggestion matrix for what tests should be run."""
        test_matrix = {
            'unit_tests': [f"test_{module_name}"],
            'integration_tests': [f"test_integration_{d}" for d in dependents[:5]],
            'regression_tests': ['test_existing_functionality'],
            'security_tests': ['test_security_validation'] if 'auth' in module_name else [],
        }
        
        return {k: v for k, v in test_matrix.items() if v}
    
    def _calculate_propagation_depth(self, module_name: str) -> int:
        """Calculate how many levels deep changes propagate through the graph."""
        if module_name not in self.dependency_graph:
            return 0
        
        visited = set()
        queue = deque([(module_name, 0)])
        max_depth = 0
        
        while queue:
            current, depth = queue.popleft()
            max_depth = max(max_depth, depth)
            
            if current in self.dependency_graph:
                for dependent in self.dependency_graph[current].dependents:
                    if dependent not in visited:
                        visited.add(dependent)
                        queue.append((dependent, depth + 1))
        
        return max_depth
    
    def _generate_customer_impact_summary(self, journeys: List[str], risk_level: str) -> str:
        """Generate a human-readable customer impact summary."""
        if not journeys:
            return "No direct customer impact identified."
        
        impact_text = f"This change affects {len(journeys)} customer journeys: "
        impact_text += ", ".join(journeys[:3])
        
        if len(journeys) > 3:
            impact_text += f" (and {len(journeys) - 3} more)"
        
        impact_text += f". Risk Level: {risk_level}"
        
        return impact_text
    
    def _determine_module_type(self, file_path: str) -> str:
        """Determine the type of module based on file location."""
        if 'core' in file_path:
            return 'core'
        elif 'service' in file_path or 'services' in file_path:
            return 'service'
        elif 'api' in file_path:
            return 'api'
        elif 'util' in file_path or 'utils' in file_path:
            return 'utility'
        else:
            return 'general'
    
    def _extract_business_functions(self, file_path: str) -> List[str]:
        """Extract business-relevant functions from file."""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Functions with business-relevant names
                    if any(keyword in node.name.lower() 
                           for keyword in ['process', 'calculate', 'validate', 'check', 'create', 'update']):
                        functions.append(node.name)
        except:
            pass
        
        return functions[:5]  # Limit to 5
    
    def _assess_criticality(self, file_path: str, dependencies: List[str]) -> str:
        """Assess how critical a module is."""
        if any(keyword in file_path.lower() for keyword in ['payment', 'auth', 'security', 'core']):
            return 'CRITICAL'
        elif len(dependencies) > 10:
            return 'HIGH'
        elif len(dependencies) > 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _initialize_business_map(self) -> Dict[str, List[str]]:
        """Initialize mapping of modules to business processes."""
        return {
            'agents.payment': ['Payment Processing', 'Billing'],
            'agents.order': ['Order Management', 'Fulfillment'],
            'agents.auth': ['Authentication', 'Authorization'],
            'agents.user': ['User Management', 'Profile'],
            'mcp_cartographer_server': ['Code Analysis', 'Dependency Mapping'],
            'mcp_neo4j_server': ['Graph Database', 'Query Engine'],
        }
    
    def generate_report(self, result: ImpactResult) -> str:
        """Generate a comprehensive impact analysis report."""
        report = []
        report.append("=" * 80)
        report.append("SELECTIVE IMPACT ANALYSIS REPORT")
        report.append("=" * 80)
        
        # Executive Summary
        report.append(f"\n🎯 RISK LEVEL: {result.risk_level}")
        report.append(f"📊 PROPAGATION DEPTH: {result.change_propagation_depth} levels")
        
        # Direct Impact
        report.append(f"\n📍 DIRECT DEPENDENTS ({len(result.direct_dependents)})")
        for dep in result.direct_dependents[:10]:
            report.append(f"  • {dep}")
        if len(result.direct_dependents) > 10:
            report.append(f"  ... and {len(result.direct_dependents) - 10} more")
        
        # Transitive Impact
        if result.transitive_dependents:
            report.append(f"\n🔄 TRANSITIVE DEPENDENTS ({len(result.transitive_dependents)})")
            for dep in result.transitive_dependents[:5]:
                report.append(f"  • {dep}")
            if len(result.transitive_dependents) > 5:
                report.append(f"  ... and {len(result.transitive_dependents) - 5} more")
        
        # Business Impact
        if result.business_impacts:
            report.append(f"\n💼 BUSINESS IMPACTS")
            for impact in result.business_impacts:
                report.append(f"  • {impact}")
        
        # Customer Journeys
        if result.affected_customer_journeys:
            report.append(f"\n👥 AFFECTED CUSTOMER JOURNEYS ({len(result.affected_customer_journeys)})")
            for journey in result.affected_customer_journeys:
                report.append(f"  • {journey}")
        
        # Teams
        report.append(f"\n👨‍💼 AFFECTED TEAMS")
        for team in result.affected_teams:
            report.append(f"  • {team}")
        
        # Testing Effort
        report.append(f"\n🧪 TESTING EFFORT")
        report.append(f"  Estimated Time: {result.estimated_test_time_hours:.1f} hours")
        if result.suggested_test_matrix:
            report.append(f"  Suggested Tests:")
            for test_type, tests in result.suggested_test_matrix.items():
                report.append(f"    {test_type}: {', '.join(tests[:2])}")
        
        # Circular Dependencies
        if result.circular_dependencies_introduced:
            report.append(f"\n⚠️  CIRCULAR DEPENDENCIES DETECTED")
            for cycle in result.circular_dependencies_introduced:
                report.append(f"  Cycle: {' → '.join(cycle)}")
        
        # Customer Impact Summary
        report.append(f"\n📱 CUSTOMER IMPACT")
        report.append(f"  {result.customer_impact_summary}")
        
        report.append("\n" + "=" * 80)
        return '\n'.join(report)


def main():
    """Demo of Selective Impact Analyzer."""
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    analyzer = SelectiveImpactAnalyzer(repo_path)
    
    # Analyze impact of changing agents/smart_diff_analyzer.py
    test_file = "agents/smart_diff_analyzer.py"
    result = analyzer.analyze_change_impact(test_file)
    
    print(analyzer.generate_report(result))
    
    # Also output as JSON
    print("\n\nJSON OUTPUT (partial):")
    output = {
        'direct_dependents': result.direct_dependents,
        'business_impacts': result.business_impacts,
        'affected_customer_journeys': result.affected_customer_journeys,
        'risk_level': result.risk_level,
        'affected_teams': result.affected_teams,
        'estimated_test_time_hours': result.estimated_test_time_hours,
        'propagation_depth': result.change_propagation_depth,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
