"""
Codebase Health Dashboard
Improvement #2 from IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md

Real-time metrics showing technical debt, complexity hotspots, and health indicators.
- Overall health score (0-100)
- Complexity hotspots detection
- Circular dependencies tracking
- Test coverage analysis
- Dead code percentage
- Documentation coverage ratio
- Security issues count
- Performance concerns flagged
"""

import os
import json
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
from datetime import datetime, timedelta
import ast
import re
from pathlib import Path


@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    value: float
    threshold: float
    status: str  # "GOOD", "WARNING", "CRITICAL"
    description: str
    recommendation: Optional[str] = None


@dataclass
class ComplexityHotspot:
    """Module with high complexity."""
    module_name: str
    complexity_score: float
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    fan_in: int  # How many modules import this
    fan_out: int  # How many modules this imports
    refactoring_priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    estimated_refactor_time_hours: float


@dataclass
class HealthReport:
    """Complete codebase health snapshot."""
    timestamp: str
    overall_health: float  # 0-100 score
    total_modules: int
    health_metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    complexity_hotspots: List[ComplexityHotspot] = field(default_factory=list)
    circular_dependencies: int = 0
    unused_modules: List[str] = field(default_factory=list)
    dead_code_percentage: float = 0.0
    test_coverage: float = 0.0
    documentation_coverage: float = 0.0
    security_issues: int = 0
    performance_concerns: int = 0
    trend: str = "stable"  # "improving", "stable", "declining"
    recommendations: List[str] = field(default_factory=list)
    metrics_history: Dict[str, List[float]] = field(default_factory=dict)


@dataclass
class ModuleHealth:
    """Health metrics for a single module."""
    module_name: str
    health_score: float
    complexity_score: float
    test_coverage: float
    documentation_coverage: float
    is_hotspot: bool
    issues: List[str] = field(default_factory=list)


class CodebaseHealthMonitor:
    """Monitors and reports codebase health metrics."""
    
    def __init__(self, repo_path: str, cache_dir: Optional[str] = None):
        """
        Initialize the health monitor.
        
        Args:
            repo_path: Path to the repository
            cache_dir: Optional cache directory for metrics history
        """
        self.repo_path = repo_path
        self.cache_dir = cache_dir or os.path.join(repo_path, '.cartographer_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.metrics_history_file = os.path.join(self.cache_dir, 'health_metrics_history.json')
        self.metrics_history: Dict[str, List[float]] = self._load_metrics_history()
        
        # Thresholds for health metrics
        self.thresholds = {
            'avg_complexity': {'warning': 15, 'critical': 25},
            'test_coverage': {'warning': 50, 'critical': 30},
            'documentation': {'warning': 40, 'critical': 20},
            'circular_deps': {'warning': 5, 'critical': 10},
            'dead_code': {'warning': 5, 'critical': 15},
            'security_issues': {'warning': 3, 'critical': 10},
        }
    
    def generate_health_report(self) -> HealthReport:
        """
        Generate comprehensive codebase health snapshot.
        
        Returns:
            HealthReport with all health metrics and recommendations
        """
        print("📊 Generating codebase health report...")
        
        # Scan all Python modules
        modules = self._scan_modules()
        total_modules = len(modules)
        
        # Calculate individual metrics
        module_health = self._calculate_module_health(modules)
        complexity_hotspots = self._identify_complexity_hotspots(module_health)
        circular_deps = self._detect_circular_dependencies(modules)
        unused_modules = self._identify_unused_modules(modules)
        dead_code_pct = self._estimate_dead_code_percentage(modules)
        test_coverage = self._calculate_test_coverage(modules)
        doc_coverage = self._calculate_documentation_coverage(modules)
        security_issues = self._estimate_security_issues(modules)
        performance_concerns = self._identify_performance_concerns(modules)
        
        # Calculate health metrics
        health_metrics = self._calculate_health_metrics(
            complexity_hotspots, test_coverage, doc_coverage,
            circular_deps, dead_code_pct, security_issues
        )
        
        # Calculate overall health score
        overall_health = self._calculate_overall_health_score(health_metrics)
        
        # Determine trend
        trend = self._determine_trend(overall_health)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            health_metrics, complexity_hotspots, unused_modules,
            circular_deps, dead_code_pct, security_issues
        )
        
        report = HealthReport(
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            total_modules=total_modules,
            health_metrics=health_metrics,
            complexity_hotspots=complexity_hotspots[:10],  # Top 10
            circular_dependencies=len(circular_deps),
            unused_modules=unused_modules,
            dead_code_percentage=dead_code_pct,
            test_coverage=test_coverage,
            documentation_coverage=doc_coverage,
            security_issues=security_issues,
            performance_concerns=performance_concerns,
            trend=trend,
            recommendations=recommendations,
            metrics_history=self.metrics_history
        )
        
        # Save to cache
        self._save_report(report)
        
        return report
    
    def get_module_health(self, module_name: str) -> ModuleHealth:
        """
        Get health metrics for a specific module.
        
        Args:
            module_name: Name of the module to analyze
            
        Returns:
            ModuleHealth with module-specific metrics
        """
        module_path = self._normalize_module_path(module_name)
        
        if not os.path.exists(module_path):
            return ModuleHealth(
                module_name=module_name,
                health_score=0,
                complexity_score=0,
                test_coverage=0,
                documentation_coverage=0,
                is_hotspot=False,
                issues=["Module not found"]
            )
        
        # Calculate metrics
        complexity = self._calculate_complexity(module_path)
        test_cov = self._get_test_coverage_for_module(module_name)
        doc_cov = self._get_documentation_coverage(module_path)
        
        # Identify issues
        issues = []
        if complexity > 20:
            issues.append(f"High complexity ({complexity})")
        if test_cov < 50:
            issues.append(f"Low test coverage ({test_cov}%)")
        if doc_cov < 30:
            issues.append(f"Poor documentation ({doc_cov}%)")
        
        health_score = (
            (100 - min(complexity * 3, 100)) * 0.4 +  # Complexity weight
            test_cov * 0.4 +  # Test coverage weight
            doc_cov * 0.2  # Documentation weight
        )
        
        return ModuleHealth(
            module_name=module_name,
            health_score=health_score,
            complexity_score=complexity,
            test_coverage=test_cov,
            documentation_coverage=doc_cov,
            is_hotspot=complexity > 20,
            issues=issues
        )
    
    def get_health_trends(self, days: int = 30) -> Dict[str, List[float]]:
        """
        Get health metric trends over time.
        
        Args:
            days: Number of days of history to return
            
        Returns:
            Dictionary of metric names to time series data
        """
        return {
            name: values[-days:] if len(values) > days else values
            for name, values in self.metrics_history.items()
        }
    
    # ========== Private Methods ==========
    
    def _scan_modules(self) -> Dict[str, str]:
        """Scan all Python modules in repository."""
        modules = {}
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    module_name = rel_path.replace('/', '.').replace('.py', '')
                    modules[module_name] = file_path
        
        return modules
    
    def _calculate_module_health(self, modules: Dict[str, str]) -> Dict[str, ModuleHealth]:
        """Calculate health for each module."""
        module_health = {}
        for module_name, module_path in modules.items():
            module_health[module_name] = self.get_module_health(module_name)
        return module_health
    
    def _identify_complexity_hotspots(
        self, module_health: Dict[str, ModuleHealth]
    ) -> List[ComplexityHotspot]:
        """Identify modules with high complexity."""
        hotspots = []
        
        for module_name, health in module_health.items():
            if health.complexity_score > 15:  # Threshold
                hotspot = ComplexityHotspot(
                    module_name=module_name,
                    complexity_score=health.complexity_score,
                    lines_of_code=self._count_lines(module_name),
                    cyclomatic_complexity=int(health.complexity_score),
                    cognitive_complexity=int(health.complexity_score * 0.8),
                    fan_in=0,  # Would calculate from dependency graph
                    fan_out=0,  # Would calculate from dependency graph
                    refactoring_priority=self._determine_refactor_priority(health.complexity_score),
                    estimated_refactor_time_hours=health.complexity_score / 2.5
                )
                hotspots.append(hotspot)
        
        # Sort by complexity
        hotspots.sort(key=lambda x: x.complexity_score, reverse=True)
        return hotspots
    
    def _detect_circular_dependencies(self, modules: Dict[str, str]) -> List[List[str]]:
        """Detect circular dependencies (simplified)."""
        # This is a simplified implementation
        # In production, use Neo4j or networkx for full cycle detection
        circular_deps = []
        
        # Parse imports and build dependency graph
        import_graph = defaultdict(set)
        for module_name, module_path in modules.items():
            try:
                with open(module_path, 'r') as f:
                    content = f.read()
                    # Simple regex for imports (not perfect but works)
                    imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                    for imp in imports:
                        imported = imp[0] or imp[1]
                        import_graph[module_name].add(imported)
            except:
                pass
        
        # Simple DFS for cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in import_graph.get(node, set()):
                if neighbor in import_graph:  # Only if it's a module we track
                    if neighbor not in visited:
                        if has_cycle(neighbor, path):
                            return True
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        circular_deps.append(cycle)
                        return True
            
            rec_stack.remove(node)
            return False
        
        for module in import_graph:
            if module not in visited:
                has_cycle(module, [])
        
        return circular_deps
    
    def _identify_unused_modules(self, modules: Dict[str, str]) -> List[str]:
        """Identify modules that are never imported."""
        unused = []
        import_graph = defaultdict(set)
        
        # Build import graph
        for module_name, module_path in modules.items():
            try:
                with open(module_path, 'r') as f:
                    content = f.read()
                    imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                    for imp in imports:
                        imported = imp[0] or imp[1]
                        import_graph[imported].update([module_name])
            except:
                pass
        
        # Find modules with no importers (excluding test files)
        for module_name in modules:
            if module_name not in import_graph and 'test' not in module_name:
                unused.append(module_name)
        
        return unused[:10]  # Top 10
    
    def _estimate_dead_code_percentage(self, modules: Dict[str, str]) -> float:
        """Estimate percentage of dead code."""
        # Simplified: count functions that are defined but not called
        total_functions = 0
        uncalled_functions = 0
        
        for module_path in modules.values():
            try:
                with open(module_path, 'r') as f:
                    tree = ast.parse(f.read())
                    
                    # Count function definitions
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    total_functions += len(functions)
                    
                    # Simple heuristic: private functions (starts with _) might be unused
                    for func in functions:
                        if func.name.startswith('_') and not func.name.startswith('__'):
                            uncalled_functions += 1
            except:
                pass
        
        if total_functions == 0:
            return 0.0
        
        return min((uncalled_functions / total_functions) * 100, 100.0)
    
    def _calculate_test_coverage(self, modules: Dict[str, str]) -> float:
        """Calculate overall test coverage percentage."""
        # Simplified: ratio of test files to source files
        test_files = sum(1 for m in modules if 'test' in m)
        source_files = len(modules) - test_files
        
        if source_files == 0:
            return 0.0
        
        coverage = (test_files / source_files) * 100
        return min(coverage, 100.0)
    
    def _calculate_documentation_coverage(self, modules: Dict[str, str]) -> float:
        """Calculate documentation coverage percentage."""
        documented_functions = 0
        total_functions = 0
        
        for module_path in modules.values():
            try:
                with open(module_path, 'r') as f:
                    tree = ast.parse(f.read())
                    
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            total_functions += 1
                            
                            # Check if has docstring
                            if (ast.get_docstring(node) and 
                                len(ast.get_docstring(node)) > 20):
                                documented_functions += 1
            except:
                pass
        
        if total_functions == 0:
            return 0.0
        
        return (documented_functions / total_functions) * 100
    
    def _estimate_security_issues(self, modules: Dict[str, str]) -> int:
        """Estimate count of potential security issues."""
        security_issues = 0
        
        for module_path in modules.values():
            try:
                with open(module_path, 'r') as f:
                    content = f.read()
                    
                    # Simple pattern detection
                    if re.search(r'eval\s*\(', content):  # eval usage
                        security_issues += 1
                    if re.search(r'pickle\s*\.|\.load\s*\(', content):  # pickle usage
                        security_issues += 1
                    if re.search(r'password\s*=|secret\s*=|key\s*=', content, re.IGNORECASE):
                        if not re.search(r'os\.environ|getenv', content):
                            security_issues += 1
                    if re.search(r'SELECT\s+.*WHERE.*\+|f".*{.*}".*WHERE', content):
                        security_issues += 1  # Potential SQL injection
            except:
                pass
        
        return security_issues
    
    def _identify_performance_concerns(self, modules: Dict[str, str]) -> int:
        """Identify potential performance concerns."""
        concerns = 0
        
        for module_path in modules.values():
            try:
                with open(module_path, 'r') as f:
                    content = f.read()
                    
                    # Nested loops (potential O(n²) complexity)
                    if content.count('for ') >= 3 and content.count('for ') <= 5:
                        concerns += 1
                    
                    # Global file I/O in loops
                    if ('for ' in content and 
                        ('open(' in content or 'read' in content)):
                        concerns += 1
            except:
                pass
        
        return concerns
    
    def _calculate_complexity(self, module_path: str) -> float:
        """Calculate cyclomatic complexity of a module."""
        try:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())
            
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            return complexity
        except:
            return 0.0
    
    def _count_lines(self, module_name: str) -> int:
        """Count lines of code in a module."""
        try:
            module_path = self._normalize_module_path(module_name)
            with open(module_path, 'r') as f:
                return len(f.readlines())
        except:
            return 0
    
    def _get_test_coverage_for_module(self, module_name: str) -> float:
        """Get test coverage for a specific module (simplified)."""
        # Look for corresponding test file
        test_module_name = f"test_{module_name}"
        if os.path.exists(self._normalize_module_path(test_module_name)):
            return 80.0  # Assumed good if test file exists
        return 30.0
    
    def _get_documentation_coverage(self, module_path: str) -> float:
        """Calculate documentation coverage for a module."""
        try:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())
            
            total_items = 0
            documented_items = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1
            
            if total_items == 0:
                return 100.0
            
            return (documented_items / total_items) * 100
        except:
            return 0.0
    
    def _determine_refactor_priority(self, complexity: float) -> str:
        """Determine refactoring priority based on complexity."""
        if complexity > 30:
            return "CRITICAL"
        elif complexity > 20:
            return "HIGH"
        elif complexity > 15:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_health_metrics(
        self,
        complexity_hotspots: List[ComplexityHotspot],
        test_coverage: float,
        doc_coverage: float,
        circular_deps: List[List[str]],
        dead_code_pct: float,
        security_issues: int
    ) -> Dict[str, HealthMetric]:
        """Calculate all health metrics."""
        metrics = {}
        
        # Complexity metric
        avg_complexity = (
            sum(h.complexity_score for h in complexity_hotspots) / len(complexity_hotspots)
            if complexity_hotspots else 0
        )
        complexity_status = (
            "CRITICAL" if avg_complexity > 25 else
            "WARNING" if avg_complexity > 15 else
            "GOOD"
        )
        metrics['complexity'] = HealthMetric(
            name='Codebase Complexity',
            value=avg_complexity,
            threshold=15,
            status=complexity_status,
            description=f'Average cyclomatic complexity: {avg_complexity:.1f}',
            recommendation='Consider refactoring high-complexity modules' if complexity_status != 'GOOD' else None
        )
        
        # Test coverage metric
        coverage_status = (
            "CRITICAL" if test_coverage < 30 else
            "WARNING" if test_coverage < 50 else
            "GOOD"
        )
        metrics['test_coverage'] = HealthMetric(
            name='Test Coverage',
            value=test_coverage,
            threshold=50,
            status=coverage_status,
            description=f'Test coverage: {test_coverage:.1f}%',
            recommendation='Increase test coverage by writing more unit tests' if coverage_status != 'GOOD' else None
        )
        
        # Documentation metric
        doc_status = (
            "CRITICAL" if doc_coverage < 20 else
            "WARNING" if doc_coverage < 40 else
            "GOOD"
        )
        metrics['documentation'] = HealthMetric(
            name='Documentation Coverage',
            value=doc_coverage,
            threshold=40,
            status=doc_status,
            description=f'Documented items: {doc_coverage:.1f}%',
            recommendation='Add docstrings to undocumented functions and classes' if doc_status != 'GOOD' else None
        )
        
        # Circular dependencies metric
        deps_status = (
            "CRITICAL" if len(circular_deps) > 10 else
            "WARNING" if len(circular_deps) > 5 else
            "GOOD"
        )
        metrics['circular_dependencies'] = HealthMetric(
            name='Circular Dependencies',
            value=len(circular_deps),
            threshold=5,
            status=deps_status,
            description=f'Circular dependency cycles: {len(circular_deps)}',
            recommendation='Refactor to eliminate circular dependencies' if deps_status != 'GOOD' else None
        )
        
        # Dead code metric
        dead_code_status = (
            "CRITICAL" if dead_code_pct > 15 else
            "WARNING" if dead_code_pct > 5 else
            "GOOD"
        )
        metrics['dead_code'] = HealthMetric(
            name='Dead Code Percentage',
            value=dead_code_pct,
            threshold=5,
            status=dead_code_status,
            description=f'Estimated dead code: {dead_code_pct:.1f}%',
            recommendation='Remove unused functions and classes' if dead_code_status != 'GOOD' else None
        )
        
        # Security issues metric
        security_status = (
            "CRITICAL" if security_issues > 10 else
            "WARNING" if security_issues > 3 else
            "GOOD"
        )
        metrics['security'] = HealthMetric(
            name='Security Issues',
            value=security_issues,
            threshold=3,
            status=security_status,
            description=f'Potential security issues: {security_issues}',
            recommendation='Address security vulnerabilities' if security_status != 'GOOD' else None
        )
        
        return metrics
    
    def _calculate_overall_health_score(self, metrics: Dict[str, HealthMetric]) -> float:
        """Calculate overall health score (0-100)."""
        weights = {
            'complexity': 0.25,
            'test_coverage': 0.35,
            'documentation': 0.15,
            'circular_dependencies': 0.15,
            'dead_code': 0.05,
            'security': 0.05,
        }
        
        score = 0.0
        for metric_name, metric in metrics.items():
            weight = weights.get(metric_name, 0)
            
            # Normalize metric to 0-100 scale
            if metric_name == 'test_coverage':
                normalized = metric.value  # Already 0-100
            elif metric_name == 'documentation':
                normalized = metric.value  # Already 0-100
            else:
                # Invert for issues (higher value = worse = lower score)
                normalized = max(0, 100 - (metric.value * 5))
            
            score += normalized * weight
        
        return score
    
    def _determine_trend(self, current_health: float) -> str:
        """Determine if health is improving, stable, or declining."""
        if 'overall_health' not in self.metrics_history:
            return 'stable'
        
        history = self.metrics_history['overall_health']
        if len(history) < 2:
            return 'stable'
        
        # Compare average of last 5 measurements with previous 5
        if len(history) < 10:
            recent = sum(history[-len(history)//2:]) / max(1, len(history)//2)
            previous = sum(history[:len(history)//2]) / max(1, len(history)//2)
        else:
            recent = sum(history[-5:]) / 5
            previous = sum(history[-10:-5]) / 5
        
        if recent > previous + 5:
            return 'improving'
        elif recent < previous - 5:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_recommendations(
        self,
        metrics: Dict[str, HealthMetric],
        hotspots: List[ComplexityHotspot],
        unused: List[str],
        circular_deps: List[List[str]],
        dead_code: float,
        security_issues: int
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Add recommendations from metrics
        for metric in metrics.values():
            if metric.recommendation:
                recommendations.append(metric.recommendation)
        
        # Specific hotspot recommendations
        if hotspots:
            top_hotspot = hotspots[0]
            recommendations.append(
                f"🔴 CRITICAL: {top_hotspot.module_name} has high complexity "
                f"({top_hotspot.complexity_score:.1f}). "
                f"Refactoring this will improve maintainability significantly."
            )
        
        # Unused modules
        if unused:
            recommendations.append(
                f"Remove {len(unused)} unused modules: {', '.join(unused[:3])}{'...' if len(unused) > 3 else ''}"
            )
        
        # Circular dependencies
        if circular_deps:
            recommendations.append(
                f"Resolve {len(circular_deps)} circular dependencies to improve modularity"
            )
        
        # Dead code
        if dead_code > 5:
            recommendations.append(
                f"Remove dead code ({dead_code:.1f}% of codebase)"
            )
        
        # Security
        if security_issues > 3:
            recommendations.append(
                f"Address {security_issues} potential security issues"
            )
        
        return recommendations
    
    def _normalize_module_path(self, module_name: str) -> str:
        """Convert module name to file path."""
        return os.path.join(self.repo_path, module_name.replace('.', '/') + '.py')
    
    def _normalize_module_name(self, file_path: str) -> str:
        """Convert file path to module name."""
        rel_path = os.path.relpath(file_path, self.repo_path)
        return rel_path.replace('/', '.').replace('.py', '')
    
    def _save_report(self, report: HealthReport):
        """Save report to cache."""
        report_file = os.path.join(self.cache_dir, 'latest_health_report.json')
        
        # Convert report to dict
        report_dict = asdict(report)
        
        # Convert complex objects to dicts
        report_dict['health_metrics'] = {
            name: asdict(metric)
            for name, metric in report.health_metrics.items()
        }
        report_dict['complexity_hotspots'] = [
            asdict(hotspot)
            for hotspot in report.complexity_hotspots
        ]
        
        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        # Update metrics history
        self.metrics_history.setdefault('overall_health', []).append(report.overall_health)
        self.metrics_history.setdefault('test_coverage', []).append(report.test_coverage)
        self.metrics_history.setdefault('documentation', []).append(report.documentation_coverage)
        self.metrics_history.setdefault('circular_deps', []).append(report.circular_dependencies)
        
        self._save_metrics_history()
    
    def _load_metrics_history(self) -> Dict[str, List[float]]:
        """Load metrics history from cache."""
        if not os.path.exists(self.metrics_history_file):
            return {}
        
        try:
            with open(self.metrics_history_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_metrics_history(self):
        """Save metrics history to cache."""
        with open(self.metrics_history_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)


def main():
    """Demo: Generate health report for current directory."""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    monitor = CodebaseHealthMonitor(repo_path)
    report = monitor.generate_health_report()
    
    print("\n" + "="*80)
    print("📊 CODEBASE HEALTH REPORT")
    print("="*80)
    print(f"Timestamp: {report.timestamp}")
    print(f"Overall Health: {report.overall_health:.1f}/100")
    print(f"Total Modules: {report.total_modules}")
    print(f"Trend: {'📈' if report.trend == 'improving' else '📉' if report.trend == 'declining' else '→'} {report.trend.upper()}")
    
    print("\n📋 KEY METRICS:")
    for name, metric in report.health_metrics.items():
        status_emoji = '✅' if metric.status == 'GOOD' else '⚠️' if metric.status == 'WARNING' else '🔴'
        print(f"  {status_emoji} {metric.name}: {metric.value:.1f} (threshold: {metric.threshold})")
    
    print(f"\n⚠️ CIRCULAR DEPENDENCIES: {report.circular_dependencies}")
    print(f"📍 COMPLEXITY HOTSPOTS: {len(report.complexity_hotspots)}")
    print(f"💀 DEAD CODE: {report.dead_code_percentage:.1f}%")
    print(f"🔒 SECURITY ISSUES: {report.security_issues}")
    
    if report.complexity_hotspots:
        print("\n🔥 TOP HOTSPOTS:")
        for hotspot in report.complexity_hotspots[:5]:
            print(f"  - {hotspot.module_name}: {hotspot.complexity_score:.1f} complexity")
    
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
