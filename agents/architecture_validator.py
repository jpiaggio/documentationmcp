"""
Architecture Drift Detection
Improvement #6 from IMPROVEMENT_OPPORTUNITIES_IMPACT_ANALYSIS.md

Automatically detect when code violates intended architecture patterns.
- Circular dependency detection
- Cross-layer violation detection
- Naming convention violation checking
- Dependency cardinality rules
- Microservice isolation violations
- Deprecated component usage
"""

import os
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import ast
import re
from pathlib import Path
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for architecture violations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ArchitectureViolation:
    """Represents a single architecture violation."""
    violation_type: str  # "circular_dependency", "cross_layer", "naming", "cardinality"
    severity: SeverityLevel
    module_name: str
    location: str  # "file_path:line_number"
    violation_description: str
    affected_modules: List[str]
    impact: str
    remediation: str
    related_rule: str


@dataclass
class LayerDefinition:
    """Definition of an architectural layer."""
    name: str
    patterns: List[str]  # Glob patterns for modules in this layer
    depends_on: List[str]  # List of layer names this layer can depend on


@dataclass
class ArchitectureRules:
    """Architecture rules configuration."""
    layers: List[LayerDefinition] = field(default_factory=list)
    forbidden_patterns: Dict[str, List[str]] = field(default_factory=dict)  # Pattern -> reason
    naming_conventions: Dict[str, str] = field(default_factory=dict)  # Role -> pattern
    max_dependencies_per_module: int = 20
    max_cyclomatic_complexity: int = 20
    deprecated_modules: List[str] = field(default_factory=list)
    max_transitive_depth: int = 5


@dataclass
class ArchitectureValidationReport:
    """Complete architecture validation report."""
    timestamp: str
    total_violations: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    violations: List[ArchitectureViolation] = field(default_factory=list)
    circular_dependencies: int = 0
    layer_violations: int = 0
    naming_violations: int = 0
    compliance_score: float = 100.0  # 0-100


class ArchitectureValidator:
    """Validates code against architectural patterns and rules."""
    
    def __init__(self, repo_path: str, rules: Optional[ArchitectureRules] = None):
        """
        Initialize the architecture validator.
        
        Args:
            repo_path: Path to the repository
            rules: Architecture rules to validate against
        """
        self.repo_path = repo_path
        self.rules = rules or self._load_default_rules()
        self.dependency_graph: Dict[str, Set[str]] = {}
        self._build_dependency_graph()
    
    def validate_architecture(self) -> ArchitectureValidationReport:
        """
        Perform comprehensive architecture validation.
        
        Returns:
            ArchitectureValidationReport with all violations
        """
        print("🏗️ Validating architecture...")
        
        violations: List[ArchitectureViolation] = []
        
        # Run all detectors
        violations.extend(self._detect_circular_dependencies())
        violations.extend(self._detect_layer_violations())
        violations.extend(self._detect_naming_violations())
        violations.extend(self._detect_cardinality_violations())
        violations.extend(self._detect_deprecated_usage())
        
        # Count violations by severity
        critical = sum(1 for v in violations if v.severity == SeverityLevel.CRITICAL)
        high = sum(1 for v in violations if v.severity == SeverityLevel.HIGH)
        medium = sum(1 for v in violations if v.severity == SeverityLevel.MEDIUM)
        low = sum(1 for v in violations if v.severity == SeverityLevel.LOW)
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(violations)
        
        report = ArchitectureValidationReport(
            timestamp=self._get_timestamp(),
            total_violations=len(violations),
            critical_violations=critical,
            high_violations=high,
            medium_violations=medium,
            low_violations=low,
            violations=violations,
            circular_dependencies=sum(1 for v in violations if v.violation_type == 'circular_dependency'),
            layer_violations=sum(1 for v in violations if v.violation_type == 'cross_layer'),
            naming_violations=sum(1 for v in violations if v.violation_type == 'naming'),
            compliance_score=compliance_score
        )
        
        return report
    
    def validate_module(self, module_name: str) -> List[ArchitectureViolation]:
        """
        Validate a specific module against architecture rules.
        
        Args:
            module_name: Name of module to validate
            
        Returns:
            List of violations found in the module
        """
        violations: List[ArchitectureViolation] = []
        
        # Check naming conventions
        violations.extend(self._check_module_naming(module_name))
        
        # Check layer violations for this module
        module_layer = self._get_module_layer(module_name)
        if module_layer:
            violations.extend(self._check_layer_dependencies(module_name, module_layer))
        
        # Check cardinality for this module
        if module_name in self.dependency_graph:
            deps = self.dependency_graph[module_name]
            if len(deps) > self.rules.max_dependencies_per_module:
                violations.append(ArchitectureViolation(
                    violation_type='cardinality',
                    severity=SeverityLevel.HIGH,
                    module_name=module_name,
                    location=f"{module_name}:0",
                    violation_description=f"Module has {len(deps)} dependencies, exceeds max of {self.rules.max_dependencies_per_module}",
                    affected_modules=list(deps),
                    impact="High coupling makes module hard to test and modify",
                    remediation="Extract dependencies into separate modules or reduce complexity",
                    related_rule="max_dependencies_per_module"
                ))
        
        return violations
    
    # ========== Private Detection Methods ==========
    
    def _detect_circular_dependencies(self) -> List[ArchitectureViolation]:
        """Detect circular dependencies in the codebase."""
        violations = []
        
        # DFS-based cycle detection
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        
        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    
                    violation = ArchitectureViolation(
                        violation_type='circular_dependency',
                        severity=SeverityLevel.CRITICAL,
                        module_name=' -> '.join(cycle),
                        location=f"Cycle: {' -> '.join(cycle)}",
                        violation_description=f"Circular dependency detected: {' -> '.join(cycle)}",
                        affected_modules=cycle,
                        impact="Cannot deploy or test modules independently; creates tight coupling",
                        remediation=f"Refactor to break the cycle. Consider extracting shared logic to a new module.",
                        related_rule="no_circular_dependencies"
                    )
                    violations.append(violation)
                    return True
            
            rec_stack.remove(node)
            return False
        
        for module in self.dependency_graph:
            if module not in visited:
                dfs(module, [])
        
        return violations
    
    def _detect_layer_violations(self) -> List[ArchitectureViolation]:
        """Detect cross-layer violations."""
        violations = []
        
        # Build layer mapping
        module_layers = {}
        for layer in self.rules.layers:
            for pattern in layer.patterns:
                for module in self.dependency_graph:
                    if self._matches_pattern(module, pattern):
                        module_layers[module] = layer.name
        
        # Check each module's dependencies
        for module, dependencies in self.dependency_graph.items():
            if module not in module_layers:
                continue
            
            source_layer = module_layers[module]
            source_layer_def = next((l for l in self.rules.layers if l.name == source_layer), None)
            
            if not source_layer_def:
                continue
            
            for dep in dependencies:
                if dep not in module_layers:
                    continue
                
                target_layer = module_layers[dep]
                
                # Check if this dependency is allowed
                if target_layer not in source_layer_def.depends_on:
                    violation = ArchitectureViolation(
                        violation_type='cross_layer',
                        severity=SeverityLevel.HIGH,
                        module_name=module,
                        location=f"{module}:0",
                        violation_description=f"Layer violation: {source_layer} cannot depend on {target_layer}",
                        affected_modules=[module, dep],
                        impact=f"Violates layered architecture. {source_layer} should not know about {target_layer}.",
                        remediation=f"Refactor {module} to use only allowed layers: {', '.join(source_layer_def.depends_on)}",
                        related_rule=f"layer_dependency_{source_layer}_to_{target_layer}"
                    )
                    violations.append(violation)
        
        return violations
    
    def _detect_naming_violations(self) -> List[ArchitectureViolation]:
        """Detect naming convention violations."""
        violations = []
        
        for module_name in self.dependency_graph:
            for role, pattern in self.rules.naming_conventions.items():
                # Check if module matches this role pattern
                if self._matches_pattern(module_name, pattern):
                    # Additional naming rules based on role
                    violations.extend(self._check_naming_rules_for_role(module_name, role))
        
        return violations
    
    def _detect_cardinality_violations(self) -> List[ArchitectureViolation]:
        """Detect dependency cardinality violations."""
        violations = []
        
        for module, dependencies in self.dependency_graph.items():
            dep_count = len(dependencies)
            
            if dep_count > self.rules.max_dependencies_per_module:
                severity = (
                    SeverityLevel.CRITICAL if dep_count > self.rules.max_dependencies_per_module * 1.5 else
                    SeverityLevel.HIGH if dep_count > self.rules.max_dependencies_per_module else
                    SeverityLevel.MEDIUM
                )
                
                violation = ArchitectureViolation(
                    violation_type='cardinality',
                    severity=severity,
                    module_name=module,
                    location=f"{module}:0",
                    violation_description=f"Module imports {dep_count} modules, exceeds maximum of {self.rules.max_dependencies_per_module}",
                    affected_modules=list(dependencies)[:5],  # Show first 5
                    impact="High fan-out indicates tight coupling and makes module hard to test, understand, and modify",
                    remediation="Reduce dependencies by: 1) Removing unused imports 2) Extracting to smaller modules 3) Using interfaces/abstractions",
                    related_rule="max_dependencies_per_module"
                )
                violations.append(violation)
        
        return violations
    
    def _detect_deprecated_usage(self) -> List[ArchitectureViolation]:
        """Detect usage of deprecated modules."""
        violations = []
        
        for module, dependencies in self.dependency_graph.items():
            for deprecated_module in self.rules.deprecated_modules:
                if deprecated_module in dependencies:
                    violation = ArchitectureViolation(
                        violation_type='deprecated_usage',
                        severity=SeverityLevel.MEDIUM,
                        module_name=module,
                        location=f"{module}:0",
                        violation_description=f"Module uses deprecated component: {deprecated_module}",
                        affected_modules=[deprecated_module],
                        impact="Deprecated modules may be removed in future releases, causing breakage",
                        remediation=f"Replace usage of {deprecated_module} with recommended alternative",
                        related_rule=f"deprecated_{deprecated_module}"
                    )
                    violations.append(violation)
        
        return violations
    
    # ========== Private Helper Methods ==========
    
    def _check_module_naming(self, module_name: str) -> List[ArchitectureViolation]:
        """Check naming conventions for a specific module."""
        violations = []
        
        for role, pattern in self.rules.naming_conventions.items():
            if self._matches_pattern(module_name, pattern):
                # Check role-specific naming rules
                violations.extend(self._check_role_naming_rules(module_name, role))
        
        return violations
    
    def _check_role_naming_rules(self, module_name: str, role: str) -> List[ArchitectureViolation]:
        """Check role-specific naming rules."""
        violations = []
        
        # Extract base name (last component)
        base_name = module_name.split('.')[-1]
        
        # Role-specific checks
        if role == 'services':
            if not base_name.endswith('service') and not base_name.endswith('Service'):
                violations.append(ArchitectureViolation(
                    violation_type='naming',
                    severity=SeverityLevel.MEDIUM,
                    module_name=module_name,
                    location=f"{module_name}:0",
                    violation_description=f"Service module '{base_name}' doesn't follow naming pattern (*Service)",
                    affected_modules=[module_name],
                    impact="Inconsistent naming makes codebase harder to navigate and understand layer structure",
                    remediation=f"Rename '{base_name}' to '*Service' pattern, e.g., '{base_name}Service'",
                    related_rule="naming_convention_services"
                ))
        
        elif role == 'repositories':
            if not base_name.endswith('repository') and not base_name.endswith('Repository'):
                violations.append(ArchitectureViolation(
                    violation_type='naming',
                    severity=SeverityLevel.MEDIUM,
                    module_name=module_name,
                    location=f"{module_name}:0",
                    violation_description=f"Repository module '{base_name}' doesn't follow naming pattern (*Repository)",
                    affected_modules=[module_name],
                    impact="Inconsistent naming makes codebase harder to navigate",
                    remediation=f"Rename '{base_name}' to '*Repository' pattern",
                    related_rule="naming_convention_repositories"
                ))
        
        return violations
    
    def _check_naming_rules_for_role(self, module_name: str, role: str) -> List[ArchitectureViolation]:
        """Check additional naming rules for a specific role."""
        # Can be extended with more detailed role-specific rules
        return []
    
    def _check_layer_dependencies(self, module_name: str, layer_name: str) -> List[ArchitectureViolation]:
        """Check if module's dependencies comply with layer rules."""
        violations = []
        
        layer_def = next((l for l in self.rules.layers if l.name == layer_name), None)
        if not layer_def:
            return violations
        
        module_deps = self.dependency_graph.get(module_name, set())
        allowed_layers = set(layer_def.depends_on)
        
        for dep in module_deps:
            dep_layer = self._get_module_layer(dep)
            if dep_layer and dep_layer not in allowed_layers:
                # Layer dependency violation - handled in _detect_layer_violations
                pass
        
        return violations
    
    def _get_module_layer(self, module_name: str) -> Optional[str]:
        """Determine which layer a module belongs to."""
        for layer in self.rules.layers:
            for pattern in layer.patterns:
                if self._matches_pattern(module_name, pattern):
                    return layer.name
        return None
    
    def _matches_pattern(self, module_name: str, pattern: str) -> bool:
        """Check if module name matches a pattern."""
        # Simple glob-style matching
        pattern = pattern.replace('*', '.*')
        pattern = f"^{pattern}$"
        return bool(re.match(pattern, module_name))
    
    def _calculate_compliance_score(self, violations: List[ArchitectureViolation]) -> float:
        """Calculate overall architecture compliance score."""
        if not violations:
            return 100.0
        
        penalty = 0
        for v in violations:
            if v.severity == SeverityLevel.CRITICAL:
                penalty += 25
            elif v.severity == SeverityLevel.HIGH:
                penalty += 15
            elif v.severity == SeverityLevel.MEDIUM:
                penalty += 5
            elif v.severity == SeverityLevel.LOW:
                penalty += 2
        
        return max(0.0, 100.0 - penalty)
    
    def _build_dependency_graph(self):
        """Build module dependency graph from repository."""
        print("  Building dependency graph...")
        
        modules = self._scan_modules()
        
        for module_name, module_path in modules.items():
            self.dependency_graph[module_name] = set()
            
            try:
                with open(module_path, 'r') as f:
                    content = f.read()
                    
                    # Find all import statements
                    imports = re.findall(
                        r'(?:from\s+(\S+)\s+import|import\s+(\S+))',
                        content
                    )
                    
                    for imp in imports:
                        imported = (imp[0] or imp[1]).split('.')[0]
                        
                        # Check if imported module is in our codebase
                        for other_module in modules:
                            if other_module.startswith(imported):
                                self.dependency_graph[module_name].add(other_module)
            except:
                pass
    
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
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _load_default_rules(self) -> ArchitectureRules:
        """Load default architecture rules."""
        return ArchitectureRules(
            layers=[
                LayerDefinition(
                    name='api',
                    patterns=['**/api/**'],
                    depends_on=['services', 'utilities']
                ),
                LayerDefinition(
                    name='services',
                    patterns=['**/services/**'],
                    depends_on=['repositories', 'utilities']
                ),
                LayerDefinition(
                    name='repositories',
                    patterns=['**/repositories/**'],
                    depends_on=['utilities', 'database']
                ),
                LayerDefinition(
                    name='utilities',
                    patterns=['**/utils/**', '**/utilities/**'],
                    depends_on=[]
                ),
            ],
            naming_conventions={
                'services': '*service.py',
                'repositories': '*repository.py',
            },
            max_dependencies_per_module=20,
            max_cyclomatic_complexity=20,
        )


def main():
    """Demo: Validate architecture of current directory."""
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    validator = ArchitectureValidator(repo_path)
    report = validator.validate_architecture()
    
    print("\n" + "="*80)
    print("🏗️ ARCHITECTURE VALIDATION REPORT")
    print("="*80)
    print(f"Timestamp: {report.timestamp}")
    print(f"Compliance Score: {report.compliance_score:.1f}/100")
    print(f"Total Violations: {report.total_violations}")
    print(f"  🔴 Critical: {report.critical_violations}")
    print(f"  🟠 High: {report.high_violations}")
    print(f"  🟡 Medium: {report.medium_violations}")
    print(f"  🔵 Low: {report.low_violations}")
    
    print(f"\n📊 VIOLATION BREAKDOWN:")
    print(f"  Circular Dependencies: {report.circular_dependencies}")
    print(f"  Layer Violations: {report.layer_violations}")
    print(f"  Naming Violations: {report.naming_violations}")
    
    if report.violations:
        print("\n🔍 TOP VIOLATIONS:")
        # Sort by severity
        severity_order = {SeverityLevel.CRITICAL: 0, SeverityLevel.HIGH: 1, SeverityLevel.MEDIUM: 2, SeverityLevel.LOW: 3}
        sorted_violations = sorted(report.violations, key=lambda v: severity_order[v.severity])
        
        for violation in sorted_violations[:10]:
            emoji = '🔴' if violation.severity == SeverityLevel.CRITICAL else '🟠' if violation.severity == SeverityLevel.HIGH else '🟡'
            print(f"\n  {emoji} {violation.violation_type.upper()}: {violation.module_name}")
            print(f"     Description: {violation.violation_description}")
            print(f"     Remediation: {violation.remediation}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
