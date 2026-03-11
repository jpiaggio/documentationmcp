"""
Smart Business Rule Inference Engine

Automatically extract implicit business rules from code:
- Validation logic (min/max values, allowed ranges)
- Temporal dependencies (ordering, state machines)
- Constraints from error handling
- Permission hierarchies and access control

This module combines AST analysis with pattern recognition to infer
non-obvious business rules that are encoded in the implementation.
"""

import ast
import re
import sys
import os
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from enum import Enum


class RuleType(Enum):
    """Types of business rules that can be inferred."""
    VALIDATION_RANGE = "validation_range"  # min/max values
    VALIDATION_PATTERN = "validation_pattern"  # regex/format constraints
    TEMPORAL_DEPENDENCY = "temporal_dependency"  # ordering requirements
    STATE_TRANSITION = "state_transition"  # allowed state changes
    ERROR_CONSTRAINT = "error_constraint"  # constraints from error handling
    PERMISSION_RULE = "permission_rule"  # access control rules
    BUSINESS_RULE = "business_rule"  # general constraints


@dataclass
class ValidationRule:
    """Inferred validation rule."""
    rule_type: str  # field name or variable being validated
    field_name: str
    operation: str  # '>', '<', '>=', '<=', '==', '!=', 'in', 'match'
    value: Any
    line: int
    severity: str = "REQUIRED"  # REQUIRED, WARNING, INFO
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TemporalDependency:
    """Inferred temporal ordering requirement."""
    precondition: str  # what must happen first
    postcondition: str  # what must happen after
    line: int
    dependency_type: str  # 'sequential', 'conditional', 'state_machine'
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PermissionRule:
    """Inferred permission/access control rule."""
    resource: str  # what is being protected
    actor_type: str  # who can access (user, admin, etc.)
    action: str  # what action (read, write, delete, etc.)
    condition: Optional[str] = None  # additional conditions
    line: int = 0
    hierarchy_level: int = 0  # for hierarchical permissions
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ConstraintRule:
    """Inferred constraint from error handling."""
    constraint: str  # description of constraint
    triggered_by: str  # what condition triggers the error
    error_message: Optional[str] = None
    line: int = 0
    severity: str = "ERROR"  # ERROR, WARNING
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SmartRuleInference:
    """Infer business rules from code analysis."""
    
    def __init__(self):
        # Validation operators and their patterns
        self.comparison_operators = {
            '>': 'greater_than',
            '<': 'less_than',
            '>=': 'greater_equal',
            '<=': 'less_equal',
            '==': 'equals',
            '!=': 'not_equals',
            'in': 'in_range',
        }
        
        # Permission keywords to detect access control
        self.permission_keywords = {
            'can_', 'is_', 'has_', 'allow', 'deny', 'require', 'permission',
            'admin', 'role', 'access', 'authorize', 'authenticated'
        }
        
        # State machine patterns
        self.state_keywords = {
            'state', 'status', 'phase', 'stage', 'step', 'mode',
            'pending', 'active', 'completed', 'cancelled', 'failed'
        }
        
        # Temporal execution patterns
        self.temporal_keywords = {
            'before', 'after', 'first', 'then', 'finally', 'once',
            'initialize', 'setup', 'cleanup', 'finalize'
        }
        
        # Results storage
        self.validation_rules: List[ValidationRule] = []
        self.temporal_dependencies: List[TemporalDependency] = []
        self.permission_rules: List[PermissionRule] = []
        self.constraint_rules: List[ConstraintRule] = []
    
    def infer_all_rules(self, source_code: str, filename: str) -> Dict[str, Any]:
        """Main entry point: infer all types of rules from code."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return {
                'validation_rules': [],
                'temporal_dependencies': [],
                'permission_rules': [],
                'constraint_rules': [],
                'error': str(e)
            }
        
        # Clear previous results
        self.validation_rules = []
        self.temporal_dependencies = []
        self.permission_rules = []
        self.constraint_rules = []
        
        # Analyze the code
        self._extract_validation_rules(tree, source_code, filename)
        self._extract_temporal_dependencies(tree, source_code, filename)
        self._extract_permission_rules(tree, source_code, filename)
        self._extract_constraint_rules(tree, source_code, filename)
        
        return {
            'validation_rules': [r.to_dict() for r in self.validation_rules],
            'temporal_dependencies': [d.to_dict() for d in self.temporal_dependencies],
            'permission_rules': [p.to_dict() for p in self.permission_rules],
            'constraint_rules': [c.to_dict() for c in self.constraint_rules],
            'statistics': self._generate_statistics(),
            'filename': filename,
        }
    
    def _extract_validation_rules(self, tree: ast.AST, source_code: str, filename: str):
        """Extract validation logic (min/max values, ranges, patterns)."""
        
        for node in ast.walk(tree):
            # Pattern 1: Direct comparisons in if statements
            if isinstance(node, ast.If):
                self._analyze_condition_for_validations(node.test, source_code)
            
            # Pattern 2: Boolean comparisons in assignments
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Compare):
                    self._analyze_comparison(node.value, source_code, node.lineno)
            
            # Pattern 3: Method calls that suggest validation
            if isinstance(node, ast.Call):
                if self._is_validation_call(node):
                    self._analyze_validation_call(node, source_code)
    
    def _analyze_condition_for_validations(self, test: ast.expr, source_code: str):
        """Analyze if condition for validation patterns."""
        if isinstance(test, ast.Compare):
            self._analyze_comparison(test, source_code, test.lineno)
        elif isinstance(test, ast.BoolOp):
            # Handle 'and'/'or' conditions
            for value in test.values:
                self._analyze_condition_for_validations(value, source_code)
        elif isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            # Handle 'not' conditions
            self._analyze_condition_for_validations(test.operand, source_code)
    
    def _analyze_comparison(self, compare: ast.Compare, source_code: str, line: int):
        """Extract validation rules from comparison operations."""
        # Get the left side (what's being validated)
        left_arg = ast.unparse(compare.left)
        
        # Process each comparison in the chain
        for comp_op, comp_value in zip(compare.ops, compare.comparators):
            op_str = ast.unparse(comp_op)
            right_arg = ast.unparse(comp_value)
            
            # Try to extract numeric values
            try:
                if isinstance(comp_value, ast.Constant) and isinstance(comp_value.value, (int, float)):
                    rule = ValidationRule(
                        rule_type="comparison",
                        field_name=left_arg,
                        operation=op_str,
                        value=comp_value.value,
                        line=line,
                        description=f"{left_arg} {op_str} {comp_value.value}"
                    )
                    self.validation_rules.append(rule)
            except:
                pass
    
    def _is_validation_call(self, call: ast.Call) -> bool:
        """Check if a function call looks like validation."""
        if isinstance(call.func, ast.Attribute):
            method_name = call.func.attr.lower()
        elif isinstance(call.func, ast.Name):
            method_name = call.func.id.lower()
        else:
            return False
        
        validation_keywords = [
            'validate', 'check', 'verify', 'assert', 'ensure',
            'match', 'matches', 'conform', 'valid', 'is_valid'
        ]
        return any(kw in method_name for kw in validation_keywords)
    
    def _analyze_validation_call(self, call: ast.Call, source_code: str):
        """Analyze validation function calls."""
        # Extract arguments
        for arg in call.args:
            arg_str = ast.unparse(arg)
            if isinstance(call.func, ast.Name):
                func_name = call.func.id
                rule = ValidationRule(
                    rule_type="validation_call",
                    field_name=arg_str,
                    operation=func_name,
                    value=None,
                    line=call.lineno,
                    description=f"Validates {arg_str} using {func_name}"
                )
                self.validation_rules.append(rule)
    
    def _extract_temporal_dependencies(self, tree: ast.AST, source_code: str, filename: str):
        """Detect ordering requirements and state machines."""
        
        # Collect all function definitions and their execution order
        function_sequences: Dict[str, List[str]] = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get function body statements
                statements = []
                for stmt in node.body:
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        if isinstance(stmt.value.func, ast.Name):
                            statements.append(stmt.value.func.id)
                        elif isinstance(stmt.value.func, ast.Attribute):
                            statements.append(stmt.value.func.attr)
                
                # Look for temporal patterns
                for i in range(len(statements) - 1):
                    current_stmt = statements[i]
                    next_stmt = statements[i + 1]
                    
                    # Check for temporal keywords
                    if self._has_temporal_significance(current_stmt, next_stmt):
                        dependency = TemporalDependency(
                            precondition=current_stmt,
                            postcondition=next_stmt,
                            line=node.lineno,
                            dependency_type='sequential',
                            evidence=[f"In {node.name}: {current_stmt} → {next_stmt}"]
                        )
                        self.temporal_dependencies.append(dependency)
                
                # Look for state transitions
                self._extract_state_transitions(node, source_code)
    
    def _has_temporal_significance(self, stmt1: str, stmt2: str) -> bool:
        """Check if two statements likely have temporal dependency."""
        # Initialize/setup patterns must come before other operations
        setup_keywords = {'init', 'setup', 'prepare', 'create', 'open'}
        cleanup_keywords = {'close', 'cleanup', 'finalize', 'destroy', 'end'}
        
        stmt1_lower = stmt1.lower()
        stmt2_lower = stmt2.lower()
        
        # Setup should come before other operations
        if any(kw in stmt1_lower for kw in setup_keywords):
            return not any(kw in stmt2_lower for kw in setup_keywords)
        
        # Operations should come before cleanup
        if any(kw in stmt2_lower for kw in cleanup_keywords):
            return not any(kw in stmt1_lower for kw in cleanup_keywords)
        
        # Check for state transitions
        if any(kw in stmt1_lower for kw in self.state_keywords):
            return any(kw in stmt2_lower for kw in self.state_keywords)
        
        return False
    
    def _extract_state_transitions(self, func: ast.AST, source_code: str):
        """Extract state machine patterns from code."""
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        
        # Look for assignments to state/status variables
        state_vars: Dict[str, List[str]] = defaultdict(list)
        
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                # Check if this is assigning to a state variable
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if any(kw in var_name.lower() for kw in self.state_keywords):
                            # Extract the value being assigned
                            if isinstance(node.value, ast.Constant):
                                state_vars[var_name].append(node.value.value)
                            elif isinstance(node.value, ast.Name):
                                state_vars[var_name].append(node.value.id)
        
        # Create state transition rules
        for var_name, states in state_vars.items():
            for i in range(len(states) - 1):
                dependency = TemporalDependency(
                    precondition=f"{var_name} == {states[i]}",
                    postcondition=f"{var_name} == {states[i + 1]}",
                    line=0,
                    dependency_type='state_machine',
                    evidence=[f"State transition: {states[i]} → {states[i + 1]}"]
                )
                self.temporal_dependencies.append(dependency)
    
    def _extract_permission_rules(self, tree: ast.AST, source_code: str, filename: str):
        """Map permission hierarchies and access control."""
        
        for node in ast.walk(tree):
            # Pattern 1: Permission check functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if self._is_permission_function(node.name):
                    self._analyze_permission_function(node, source_code)
            
            # Pattern 2: Role-based access patterns
            if isinstance(node, ast.If):
                self._extract_permission_from_condition(node, source_code)
    
    def _is_permission_function(self, func_name: str) -> bool:
        """Check if function is permission-related."""
        func_lower = func_name.lower()
        return any(kw in func_lower for kw in self.permission_keywords)
    
    def _analyze_permission_function(self, func: ast.FunctionDef, source_code: str):
        """Extract permission rules from permission functions."""
        func_name = func.name
        
        # Extract parameters - these are often the actors/resources
        params = [arg.arg for arg in func.args.args]
        
        # Look for boolean returns
        for node in ast.walk(func):
            if isinstance(node, ast.Return):
                if node.value:
                    return_val = ast.unparse(node.value)
                    
                    # Extract permission rule
                    action = self._extract_action_from_function_name(func_name)
                    resource = self._extract_resource(func_name, params)
                    
                    rule = PermissionRule(
                        resource=resource or func_name,
                        actor_type=params[0] if params else "user",
                        action=action,
                        line=func.lineno,
                    )
                    self.permission_rules.append(rule)
    
    def _extract_permission_from_condition(self, if_node: ast.If, source_code: str):
        """Extract permission rules from conditional logic."""
        condition_str = ast.unparse(if_node.test)
        
        # Look for permission-related conditions
        if any(kw in condition_str.lower() for kw in self.permission_keywords):
            # Extract the resource and action
            # Look for patterns like: if user.is_admin() or if can_delete(item)
            
            rule = PermissionRule(
                resource=self._extract_resource(condition_str, []),
                actor_type="user",
                action=self._extract_action_from_condition(condition_str),
                condition=condition_str,
                line=if_node.lineno,
            )
            self.permission_rules.append(rule)
    
    def _extract_action_from_function_name(self, func_name: str) -> str:
        """Extract action verb from function name."""
        actions = ['create', 'read', 'update', 'delete', 'write', 'execute', 'manage']
        func_lower = func_name.lower()
        for action in actions:
            if action in func_lower:
                return action
        return "access"
    
    def _extract_action_from_condition(self, condition_str: str) -> str:
        """Extract action from condition string."""
        actions = ['delete', 'edit', 'read', 'write', 'create', 'execute', 'manage']
        condition_lower = condition_str.lower()
        for action in actions:
            if action in condition_lower:
                return action
        return "access"
    
    def _extract_resource(self, name: str, params: List[str]) -> str:
        """Extract resource name from function/variable name."""
        resources = ['user', 'post', 'comment', 'order', 'payment', 'document', 'file', 'item']
        name_lower = name.lower()
        for resource in resources:
            if resource in name_lower:
                return resource
        return params[1] if len(params) > 1 else "resource"
    
    def _extract_constraint_rules(self, tree: ast.AST, source_code: str, filename: str):
        """Extract constraints from error handling."""
        
        for node in ast.walk(tree):
            # Pattern 1: Try-except blocks
            if isinstance(node, ast.Try):
                self._analyze_try_block(node, source_code)
            
            # Pattern 2: Raise statements
            if isinstance(node, ast.Raise):
                self._analyze_raise_statement(node, source_code)
    
    def _analyze_try_block(self, try_node: ast.Try, source_code: str):
        """Extract constraints from exception handling."""
        
        # Analyze each handler
        for handler in try_node.handlers:
            if handler.type:
                error_type = ast.unparse(handler.type)
                
                # The body of try tells us what operation triggers the error
                try_operations = []
                for stmt in try_node.body[:2]:  # Get first couple statements
                    try_operations.append(ast.unparse(stmt)[:50])
                
                if try_operations:
                    rule = ConstraintRule(
                        constraint=f"Must handle {error_type}",
                        triggered_by=" then ".join(try_operations),
                        error_message=handler.name,
                        line=try_node.lineno,
                        severity="ERROR"
                    )
                    self.constraint_rules.append(rule)
    
    def _analyze_raise_statement(self, raise_node: ast.Raise, source_code: str):
        """Extract constraints from raise statements."""
        if raise_node.exc:
            error_desc = ast.unparse(raise_node.exc)
            
            # Extract what condition triggered the error
            rule = ConstraintRule(
                constraint=f"Raises {error_desc.split('(')[0]}",
                triggered_by="condition_check",
                line=raise_node.lineno,
                severity="ERROR"
            )
            self.constraint_rules.append(rule)
    
    def _generate_statistics(self) -> Dict[str, int]:
        """Generate statistics about inferred rules."""
        return {
            'total_validation_rules': len(self.validation_rules),
            'total_temporal_dependencies': len(self.temporal_dependencies),
            'total_permission_rules': len(self.permission_rules),
            'total_constraint_rules': len(self.constraint_rules),
            'total_rules': (
                len(self.validation_rules) + 
                len(self.temporal_dependencies) + 
                len(self.permission_rules) + 
                len(self.constraint_rules)
            ),
        }
    
    def generate_cypher_statements(self, rules: Dict[str, Any], 
                                   filename: str, module_name: str) -> List[str]:
        """Convert inferred rules to Neo4j Cypher statements."""
        statements = []
        
        # Validation rules
        for rule in rules.get('validation_rules', []):
            cypher = (
                f"CREATE (vr:ValidationRule {{"
                f"field: '{rule['field_name']}',"
                f"operation: '{rule['operation']}',"
                f"value: {rule['value']},"
                f"module: '{module_name}'"
                f"}}) "
                f"CREATE (f:{module_name}_File {{name: '{filename}'}}) "
                f"CREATE (f)-[:DEFINES_VALIDATION]->(vr)"
            )
            statements.append(cypher)
        
        # Temporal dependencies
        for dep in rules.get('temporal_dependencies', []):
            cypher = (
                f"CREATE (td:TemporalDependency {{"
                f"precondition: '{dep['precondition']}',"
                f"postcondition: '{dep['postcondition']}',"
                f"type: '{dep['dependency_type']}',"
                f"module: '{module_name}'"
                f"}}) "
                f"CREATE (f:{module_name}_File {{name: '{filename}'}}) "
                f"CREATE (f)-[:REQUIRES_ORDERING]->(td)"
            )
            statements.append(cypher)
        
        # Permission rules
        for rule in rules.get('permission_rules', []):
            cypher = (
                f"CREATE (pr:PermissionRule {{"
                f"resource: '{rule['resource']}',"
                f"action: '{rule['action']}',"
                f"actor_type: '{rule['actor_type']}',"
                f"module: '{module_name}'"
                f"}}) "
                f"CREATE (f:{module_name}_File {{name: '{filename}'}}) "
                f"CREATE (f)-[:ENFORCES_PERMISSION]->(pr)"
            )
            statements.append(cypher)
        
        # Constraint rules
        for rule in rules.get('constraint_rules', []):
            cypher = (
                f"CREATE (cr:ConstraintRule {{"
                f"constraint: '{rule['constraint']}',"
                f"triggered_by: '{rule['triggered_by']}',"
                f"severity: '{rule['severity']}',"
                f"module: '{module_name}'"
                f"}}) "
                f"CREATE (f:{module_name}_File {{name: '{filename}'}}) "
                f"CREATE (f)-[:ENFORCES_CONSTRAINT]->(cr)"
            )
            statements.append(cypher)
        
        return statements


def run_smart_rule_inference(source_code: str, filename: str) -> Dict[str, Any]:
    """Convenience function to run inference."""
    inferencer = SmartRuleInference()
    return inferencer.infer_all_rules(source_code, filename)


if __name__ == "__main__":
    # Example usage
    test_code = """
    def process_order(order):
        if order.amount < 0:
            raise ValueError("Amount cannot be negative")
        
        if order.amount > 10000:
            raise ValueError("Amount exceeds limit")
        
        order.status = 'pending'
        process_payment(order)
        order.status = 'completed'
        send_confirmation(order)
    
    def can_delete_post(user, post):
        if user.is_admin():
            return True
        if post.owner == user:
            return True
        return False
    """
    
    inferencer = SmartRuleInference()
    results = inferencer.infer_all_rules(test_code, "example.py")
    
    print("=== Validation Rules ===")
    for rule in results['validation_rules']:
        print(f"  {rule['field_name']} {rule['operation']} {rule['value']}")
    
    print("\n=== Temporal Dependencies ===")
    for dep in results['temporal_dependencies']:
        print(f"  {dep['precondition']} → {dep['postcondition']}")
    
    print("\n=== Permission Rules ===")
    for perm in results['permission_rules']:
        print(f"  {perm['actor_type']} can {perm['action']} {perm['resource']}")
    
    print("\n=== Constraint Rules ===")
    for const in results['constraint_rules']:
        print(f"  {const['constraint']} ({const['severity']})")
