"""
Context-Aware Suggestions Engine

Provides intelligent recommendations by analyzing:
1. Duplicate validation logic across files
2. Unhandled error cases in main control flow
3. Functions that could be consolidated
4. Contradicting business rules
"""

import ast
import os
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
from difflib import SequenceMatcher


@dataclass
class ValidationLogic:
    """Represents a validation rule."""
    name: str
    file: str
    line: int
    code_snippet: str
    parameters: List[str]
    rules: List[str]
    error_message: str
    

@dataclass
class ErrorHandler:
    """Represents error handling in code."""
    function: str
    file: str
    line: int
    exception_types: List[str]
    handlers: List[str]
    

@dataclass
class FunctionCandidate:
    """Function that could be consolidated."""
    name: str
    file: str
    line: int
    similarity_score: float
    other_functions: List[Tuple[str, str, float]]  # (name, file, score)
    

@dataclass
class BusinessRuleConflict:
    """Represents a contradiction between rules."""
    rule_a: Dict[str, Any]
    rule_b: Dict[str, Any]
    conflict_type: str  # 'contradictory', 'overlapping', 'inconsistent'
    severity: str  # 'critical', 'warning', 'info'
    explanation: str


class ContextAwareSuggestionsEngine:
    """Generate context-aware recommendations based on codebase analysis."""
    
    def __init__(self, codebase_path: str):
        self.codebase_path = codebase_path
        self.validation_rules: Dict[str, List[ValidationLogic]] = defaultdict(list)
        self.error_handlers: Dict[str, List[ErrorHandler]] = defaultdict(list)
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.business_rules: List[Dict[str, Any]] = []
        
        self.suggestions = {
            'duplicate_validation': [],
            'unhandled_errors': [],
            'consolidation_opportunities': [],
            'rule_conflicts': []
        }
    
    def analyze_codebase(self, file_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze codebase and generate suggestions."""
        print(f"\n🔍 Context-Aware Suggestions Engine")
        print(f"   Analyzing: {self.codebase_path}")
        
        # Discover Python files
        if file_list is None:
            file_list = self._discover_python_files()
        
        print(f"   Found {len(file_list)} Python files")
        
        # Analyze each file
        for file_path in file_list:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"   ⚠️  Error analyzing {file_path}: {e}")
        
        # Generate suggestions
        self._identify_duplicate_validation()
        self._identify_unhandled_errors()
        self._identify_consolidation_opportunities()
        self._identify_rule_conflicts()
        
        return self._compile_results()
    
    def _discover_python_files(self) -> List[str]:
        """Discover all Python files in codebase."""
        files = []
        for root, dirs, filenames in os.walk(self.codebase_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']]
            
            for filename in filenames:
                if filename.endswith('.py'):
                    files.append(os.path.join(root, filename))
        
        return sorted(files)
    
    def _analyze_file(self, file_path: str):
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except:
            return
        
        try:
            tree = ast.parse(source_code)
        except:
            return
        
        rel_path = os.path.relpath(file_path, self.codebase_path)
        
        # Extract validation functions
        self._extract_validation_logic(tree, rel_path, source_code)
        
        # Extract error handlers
        self._extract_error_handlers(tree, rel_path, source_code)
        
        # Extract function definitions
        self._extract_functions(tree, rel_path, source_code)
        
        # Extract business rules
        self._extract_business_rules(tree, rel_path, source_code)
    
    def _extract_validation_logic(self, tree: ast.AST, file_path: str, source_code: str):
        """Extract validation logic from code."""
        validation_keywords = [
            'validate', 'verify', 'check', 'assert', 'is_valid',
            'validate_', 'check_', 'verify_', 'ensure_'
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name.lower()
                
                # Check if function name suggests validation
                is_validation = any(kw in func_name for kw in validation_keywords)
                
                if is_validation or self._contains_validation_patterns(node, source_code):
                    # Extract the function's logic
                    params = [arg.arg for arg in node.args.args]
                    
                    # Find error messages/assertions
                    error_messages = self._extract_error_messages(node)
                    rules = self._extract_validation_rules(node)
                    
                    # Get code snippet
                    start_line = node.lineno
                    end_line = node.end_lineno or node.lineno
                    lines = source_code.split('\n')[start_line-1:end_line]
                    snippet = '\n'.join(lines[:3])  # First 3 lines
                    
                    val_logic = ValidationLogic(
                        name=node.name,
                        file=file_path,
                        line=node.lineno,
                        code_snippet=snippet,
                        parameters=params,
                        rules=rules,
                        error_message=error_messages[0] if error_messages else ''
                    )
                    
                    self.validation_rules[file_path].append(val_logic)
    
    def _extract_error_handlers(self, tree: ast.AST, file_path: str, source_code: str):
        """Extract error handling logic."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Get parent function
                parent_func = self._get_parent_function(tree, node)
                if parent_func:
                    exception_types = []
                    handlers = []
                    
                    for handler in node.handlers:
                        if handler.type:
                            exc_name = self._get_exception_name(handler.type)
                            exception_types.append(exc_name)
                        handlers.append(self._get_handler_body(handler, source_code))
                    
                    err_handler = ErrorHandler(
                        function=parent_func.name,
                        file=file_path,
                        line=node.lineno,
                        exception_types=exception_types,
                        handlers=handlers
                    )
                    
                    self.error_handlers[file_path].append(err_handler)
    
    def _extract_functions(self, tree: ast.AST, file_path: str, source_code: str):
        """Extract function definitions and their characteristics."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private/dunder methods
                if node.name.startswith('_'):
                    continue
                
                key = f"{file_path}::{node.name}"
                
                # Extract function body characteristics
                body_size = len(node.body)
                calls = self._extract_function_calls(node)
                conditions = self._count_conditions(node)
                
                self.functions[key] = {
                    'name': node.name,
                    'file': file_path,
                    'line': node.lineno,
                    'complexity': body_size + conditions,
                    'calls': calls,
                    'has_error_handling': any(isinstance(n, ast.Try) for n in ast.walk(node)),
                    'parameters': len(node.args.args)
                }
    
    def _extract_business_rules(self, tree: ast.AST, file_path: str, source_code: str):
        """Extract business rules from code."""
        business_keywords = {
            'payment_rule': ['payment', 'amount', 'discount', 'tax'],
            'eligibility_rule': ['eligible', 'qualify', 'permission', 'access'],
            'workflow_rule': ['status', 'state', 'transition', 'workflow'],
            'rate_limit_rule': ['rate', 'limit', 'throttle', 'quota'],
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                source_lines = source_code.split('\n')
                func_source = source_lines[node.lineno-1:node.end_lineno or node.lineno]
                func_text = '\n'.join(func_source)
                
                for rule_type, keywords in business_keywords.items():
                    if any(kw in func_text.lower() for kw in keywords):
                        # Extract comparison operations
                        comparisons = self._extract_comparisons(node)
                        
                        self.business_rules.append({
                            'type': rule_type,
                            'function': node.name,
                            'file': file_path,
                            'line': node.lineno,
                            'keywords': [kw for kw in keywords if kw in func_text.lower()],
                            'comparisons': comparisons,
                            'logic': comparisons  # Store the logical conditions
                        })
    
    def _identify_duplicate_validation(self):
        """Identify duplicate validation logic across files."""
        print("\n   🔍 Scanning for duplicate validation logic...")
        
        all_validations = []
        for file_path, validations in self.validation_rules.items():
            all_validations.extend([(file_path, v) for v in validations])
        
        # Compare validations
        for i, (file_a, val_a) in enumerate(all_validations):
            for file_b, val_b in all_validations[i+1:]:
                if file_a != file_b:
                    # Compare validation logic
                    similarity = self._calculate_code_similarity(
                        val_a.code_snippet, 
                        val_b.code_snippet
                    )
                    
                    # Also check rule similarity
                    rule_similarity = self._calculate_rule_similarity(
                        val_a.rules,
                        val_b.rules
                    )
                    
                    combined_similarity = (similarity + rule_similarity) / 2
                    
                    if combined_similarity > 0.7:
                        self.suggestions['duplicate_validation'].append({
                            'severity': 'medium' if combined_similarity > 0.85 else 'low',
                            'type': 'duplicate_validation',
                            'message': f"This validation logic duplicates that rule found in {file_b}",
                            'function_a': val_a.name,
                            'file_a': file_a,
                            'line_a': val_a.line,
                            'function_b': val_b.name,
                            'file_b': file_b,
                            'line_b': val_b.line,
                            'similarity': combined_similarity,
                            'details': {
                                'rule_a': val_a.rules[:2],
                                'rule_b': val_b.rules[:2],
                                'recommendation': f"Consider extracting shared validation logic to utils/{os.path.basename(file_a)}"
                            }
                        })
    
    def _identify_unhandled_errors(self):
        """Identify unhandled error cases."""
        print("   🔍 Scanning for unhandled error cases...")
        
        # Check each function for comprehensive error handling
        for func_key, func_info in self.functions.items():
            file_path = func_info['file']
            
            # Check if function has error-prone operations
            handlers = self.error_handlers.get(file_path, [])
            func_has_handler = any(h.function == func_info['name'] for h in handlers)
            
            # Check for high-risk operations
            has_io = 'io' in func_info['calls'] or 'read' in func_info['calls']
            has_network = any(call in func_info['calls'] for call in ['request', 'api', 'http'])
            has_db = 'db' in func_info['calls'] or 'query' in func_info['calls']
            
            if (has_io or has_network or has_db) and not func_has_handler:
                self.suggestions['unhandled_errors'].append({
                    'severity': 'high' if has_network else 'medium',
                    'type': 'unhandled_error',
                    'message': f"This error case isn't handled in your main flow",
                    'function': func_info['name'],
                    'file': file_path,
                    'line': func_info['line'],
                    'risky_operations': [],
                    'details': {
                        'has_io': has_io,
                        'has_network': has_network,
                        'has_db': has_db,
                        'recommendation': f"Add try-except block to handle potential errors in {func_info['name']}"
                    }
                })
    
    def _identify_consolidation_opportunities(self):
        """Identify functions that could be consolidated."""
        print("   🔍 Scanning for consolidation opportunities...")
        
        # Find similar functions
        func_list = list(self.functions.items())
        
        for i, (key_a, func_a) in enumerate(func_list):
            for key_b, func_b in func_list[i+1:]:
                # Skip if same file
                if func_a['file'] == func_b['file']:
                    continue
                
                # Check similarity in parameters and complexity
                param_similarity = 1 - abs(func_a['parameters'] - func_b['parameters']) / max(1, max(func_a['parameters'], func_b['parameters']))
                complexity_similarity = 1 - abs(func_a['complexity'] - func_b['complexity']) / max(1, max(func_a['complexity'], func_b['complexity']))
                
                call_similarity = self._calculate_call_similarity(
                    func_a['calls'],
                    func_b['calls']
                )
                
                combined_similarity = (param_similarity + complexity_similarity + call_similarity) / 3
                
                if combined_similarity > 0.65 and combined_similarity < 1.0:
                    self.suggestions['consolidation_opportunities'].append({
                        'severity': 'low' if combined_similarity < 0.8 else 'info',
                        'type': 'consolidation',
                        'message': f"These {3} functions could be consolidated",
                        'functions': [
                            {'name': func_a['name'], 'file': func_a['file'], 'line': func_a['line']},
                            {'name': func_b['name'], 'file': func_b['file'], 'line': func_b['line']}
                        ],
                        'similarity': combined_similarity,
                        'details': {
                            'param_similarity': param_similarity,
                            'complexity_similarity': complexity_similarity,
                            'call_similarity': call_similarity,
                            'recommendation': f"Create a shared utility function that both {func_a['name']} and {func_b['name']} can use"
                        }
                    })
    
    def _identify_rule_conflicts(self):
        """Identify contradicting business rules."""
        print("   🔍 Scanning for rule conflicts...")
        
        # Analyze business rules for conflicts
        for i, rule_a in enumerate(self.business_rules):
            for rule_b in self.business_rules[i+1:]:
                conflict = self._detect_rule_conflict(rule_a, rule_b)
                
                if conflict:
                    self.suggestions['rule_conflicts'].append({
                        'severity': conflict['severity'],
                        'type': 'rule_conflict',
                        'message': f"This business rule contradicts this other one",
                        'rule_a': {
                            'function': rule_a['function'],
                            'file': rule_a['file'],
                            'line': rule_a['line'],
                            'type': rule_a['type']
                        },
                        'rule_b': {
                            'function': rule_b['function'],
                            'file': rule_b['file'],
                            'line': rule_b['line'],
                            'type': rule_b['type']
                        },
                        'conflict_type': conflict['type'],
                        'explanation': conflict['explanation'],
                        'details': {
                            'rule_a_keywords': rule_a.get('keywords', []),
                            'rule_b_keywords': rule_b.get('keywords', []),
                            'recommendation': conflict['recommendation']
                        }
                    })
    
    def _compile_results(self) -> Dict[str, Any]:
        """Compile all suggestions into a report."""
        report = {
            'metadata': {
                'codebase': self.codebase_path,
                'total_files_analyzed': len(self.validation_rules) + len(self.error_handlers),
                'total_validations': sum(len(v) for v in self.validation_rules.values()),
                'total_handlers': sum(len(h) for h in self.error_handlers.values()),
                'total_functions': len(self.functions),
                'total_rules': len(self.business_rules)
            },
            'suggestions': self.suggestions,
            'summary': {
                'duplicate_validation_found': len(self.suggestions['duplicate_validation']),
                'unhandled_errors_found': len(self.suggestions['unhandled_errors']),
                'consolidation_opportunities': len(self.suggestions['consolidation_opportunities']),
                'rule_conflicts_found': len(self.suggestions['rule_conflicts']),
                'total_suggestions': sum(len(v) for v in self.suggestions.values())
            }
        }
        
        return report
    
    # ==================== Helper Methods ====================
    
    def _contains_validation_patterns(self, node: ast.FunctionDef, source_code: str) -> bool:
        """Check if function contains validation patterns."""
        patterns = ['>=', '<=', '==', '!=', 'assert', 'raise', 'if not']
        
        source_lines = source_code.split('\n')
        func_source = source_lines[node.lineno-1:node.end_lineno or node.lineno]
        func_text = '\n'.join(func_source).lower()
        
        return any(pattern in func_text for pattern in patterns)
    
    def _extract_error_messages(self, node: ast.FunctionDef) -> List[str]:
        """Extract error messages from assertions and raises."""
        messages = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.Assert) and n.msg:
                try:
                    msg = ast.unparse(n.msg)
                    messages.append(msg)
                except:
                    pass
            elif isinstance(n, ast.Raise):
                if n.exc and hasattr(n.exc, 'args'):
                    try:
                        msg = ast.unparse(n.exc)
                        messages.append(msg)
                    except:
                        pass
        
        return messages
    
    def _extract_validation_rules(self, node: ast.FunctionDef) -> List[str]:
        """Extract validation rules from comparisons and checks."""
        rules = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.Compare):
                try:
                    rule = ast.unparse(n)
                    rules.append(rule)
                except:
                    pass
        
        return rules
    
    def _get_parent_function(self, tree: ast.AST, target: ast.AST) -> Optional[ast.FunctionDef]:
        """Find parent function of a node."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for child in ast.walk(node):
                    if child is target:
                        return node
        return None
    
    def _get_exception_name(self, exc_type: ast.expr) -> str:
        """Get exception type name."""
        if isinstance(exc_type, ast.Name):
            return exc_type.id
        try:
            return ast.unparse(exc_type)
        except:
            return 'Exception'
    
    def _get_handler_body(self, handler: ast.ExceptHandler, source_code: str) -> str:
        """Get handler body as text."""
        if handler.body:
            try:
                return ast.unparse(handler.body[0])
            except:
                return 'pass'
        return ''
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls from a function."""
        calls = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    calls.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    calls.append(n.func.attr)
        
        return calls
    
    def _count_conditions(self, node: ast.FunctionDef) -> int:
        """Count conditional statements."""
        count = 0
        for n in ast.walk(node):
            if isinstance(n, (ast.If, ast.For, ast.While, ast.With)):
                count += 1
        return count
    
    def _extract_comparisons(self, node: ast.FunctionDef) -> List[str]:
        """Extract comparison operations from function."""
        comparisons = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.Compare):
                try:
                    comp = ast.unparse(n)
                    comparisons.append(comp)
                except:
                    pass
        
        return comparisons
    
    def _calculate_code_similarity(self, code_a: str, code_b: str) -> float:
        """Calculate similarity between two code snippets."""
        matcher = SequenceMatcher(None, code_a, code_b)
        return matcher.ratio()
    
    def _calculate_rule_similarity(self, rules_a: List[str], rules_b: List[str]) -> float:
        """Calculate similarity between two sets of rules."""
        if not rules_a or not rules_b:
            return 0.0
        
        # Simple matching - count how many rules are similar
        matches = 0
        for rule_a in rules_a[:3]:  # Check first 3 rules
            for rule_b in rules_b[:3]:
                similarity = self._calculate_code_similarity(rule_a, rule_b)
                if similarity > 0.7:
                    matches += 1
        
        return matches / max(len(rules_a), len(rules_b))
    
    def _calculate_call_similarity(self, calls_a: List[str], calls_b: List[str]) -> float:
        """Calculate similarity between function call lists."""
        set_a = set(calls_a)
        set_b = set(calls_b)
        
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _detect_rule_conflict(self, rule_a: Dict, rule_b: Dict) -> Optional[Dict]:
        """Detect if two rules conflict."""
        # Same rule type in different files = potential conflict
        if rule_a['type'] == rule_b['type'] and rule_a['file'] != rule_b['file']:
            # Check for opposite comparisons
            logic_a = ' '.join(rule_a.get('comparisons', []))
            logic_b = ' '.join(rule_b.get('comparisons', []))
            
            # Look for contradictory patterns
            contradictions = [
                ('> 0', '<= 0'),
                ('>= 100', '< 100'),
                ('approved', 'rejected'),
                ('enabled', 'disabled'),
            ]
            
            for contra_a, contra_b in contradictions:
                if contra_a in logic_a and contra_b in logic_b:
                    return {
                        'type': 'contradictory',
                        'severity': 'critical',
                        'explanation': f"Rule requires {contra_a} but other rule requires {contra_b}",
                        'recommendation': f"Align business rule logic between {rule_a['file']} and {rule_b['file']}"
                    }
                elif contra_b in logic_a and contra_a in logic_b:
                    return {
                        'type': 'contradictory',
                        'severity': 'critical',
                        'explanation': f"Rule requires {contra_b} but other rule requires {contra_a}",
                        'recommendation': f"Align business rule logic between {rule_a['file']} and {rule_b['file']}"
                    }
        
        # Different types but same keywords = overlapping rules
        if rule_a['type'] != rule_b['type']:
            shared_keywords = set(rule_a.get('keywords', [])) & set(rule_b.get('keywords', []))
            if len(shared_keywords) >= 2:
                return {
                    'type': 'overlapping',
                    'severity': 'warning',
                    'explanation': f"Rules overlap on keywords: {', '.join(shared_keywords)}",
                    'recommendation': f"Review interaction between {rule_a['type']} and {rule_b['type']}"
                }
        
        return None
    
    def print_summary(self):
        """Print human-readable summary of suggestions."""
        print("\n" + "="*70)
        print("📋 CONTEXT-AWARE SUGGESTIONS SUMMARY")
        print("="*70)
        
        # Duplicate Validation
        if self.suggestions['duplicate_validation']:
            print(f"\n🔴 Duplicate Validation Logic ({len(self.suggestions['duplicate_validation'])})")
            for sugg in self.suggestions['duplicate_validation'][:3]:
                print(f"   • {sugg['message']}")
                print(f"     {sugg['file_a']}::{sugg['function_a']} (line {sugg['line_a']})")
                print(f"     {sugg['file_b']}::{sugg['function_b']} (line {sugg['line_b']})")
                print(f"     Similarity: {sugg['similarity']:.1%}")
        
        # Unhandled Errors
        if self.suggestions['unhandled_errors']:
            print(f"\n🔴 Unhandled Error Cases ({len(self.suggestions['unhandled_errors'])})")
            for sugg in self.suggestions['unhandled_errors'][:3]:
                print(f"   • {sugg['function']} ({sugg['file']}::{sugg['line']})")
                print(f"     {sugg['message']}")
                if sugg['details']['has_network']:
                    print(f"     ⚠️  Network operation without error handling")
        
        # Consolidation Opportunities
        if self.suggestions['consolidation_opportunities']:
            print(f"\n🟡 Consolidation Opportunities ({len(self.suggestions['consolidation_opportunities'])})")
            for sugg in self.suggestions['consolidation_opportunities'][:3]:
                print(f"   • {sugg['message']}")
                for func in sugg['functions']:
                    print(f"     - {func['file']}::{func['name']} (line {func['line']})")
                print(f"     Similarity: {sugg['similarity']:.1%}")
        
        # Rule Conflicts
        if self.suggestions['rule_conflicts']:
            print(f"\n🔴 Business Rule Conflicts ({len(self.suggestions['rule_conflicts'])})")
            for sugg in self.suggestions['rule_conflicts'][:3]:
                print(f"   • {sugg['message']}")
                print(f"     {sugg['rule_a']['file']}::{sugg['rule_a']['function']}")
                print(f"     vs {sugg['rule_b']['file']}::{sugg['rule_b']['function']}")
                print(f"     {sugg['explanation']}")
        
        print("\n" + "="*70)
        total = sum(len(v) for v in self.suggestions.values())
        print(f"Total Suggestions: {total}")
        print("="*70 + "\n")


def run_context_aware_analysis(codebase_path: str) -> Dict[str, Any]:
    """Run context-aware suggestion analysis."""
    engine = ContextAwareSuggestionsEngine(codebase_path)
    results = engine.analyze_codebase()
    engine.print_summary()
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python context_aware_suggestions.py <codebase_path>")
        sys.exit(1)
    
    codebase_path = sys.argv[1]
    results = run_context_aware_analysis(codebase_path)
    
    # Print detailed results
    import json
    print("\nDetailed Results:")
    print(json.dumps({
        'summary': results.get('summary'),
        'metadata': results.get('metadata')
    }, indent=2))
