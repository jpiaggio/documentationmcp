"""
Semantic Code Analysis Engine

Uses Abstract Syntax Trees (AST) to understand code semantically instead of 
keyword matching. Provides:
- Function call graph analysis
- Data flow tracking
- Control flow understanding
- Type inference
- Pattern recognition
"""

import ast
import sys
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

try:
    from tree_sitter import Parser, Language
    from tree_sitter_python import language as get_python_language
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False


@dataclass
class CallNode:
    """Represents a function call in the code."""
    caller: str
    callee: str
    line: int
    args: List[str]
    

@dataclass
class FunctionDefinition:
    """Represents a function definition."""
    name: str
    line: int
    params: List[str]
    calls: List[str]  # Functions called within this function
    conditions: List[str]  # Conditions (if statements) in this function
    assignments: Dict[str, str]  # Variable assignments (var -> type hint or inferred type)
    returns: List[str]  # What this function returns


@dataclass
class ControlFlowPath:
    """Represents a path through control flow."""
    condition: str
    operations: List[str]
    branch_type: str  # 'if', 'else', 'loop'


class SemanticAnalyzer:
    """Analyze code semantically using AST."""
    
    def __init__(self, language: str = 'python'):
        self.language = language
        self.has_tree_sitter = HAS_TREE_SITTER
        self.call_graph: Dict[str, List[CallNode]] = defaultdict(list)
        self.functions: Dict[str, FunctionDefinition] = {}
        self.data_flows: List[Tuple[str, str]] = []
        self.control_flows: List[ControlFlowPath] = []
        self.business_patterns: Dict[str, List[Dict]] = defaultdict(list)
        
    def analyze(self, source_code: str, filename: str) -> Dict[str, Any]:
        """Main entry point for semantic analysis."""
        return {
            'call_graph': self._analyze_call_graph(source_code, filename),
            'data_flow': self._analyze_data_flow(source_code, filename),
            'control_flow': self._analyze_control_flow(source_code, filename),
            'business_patterns': self._identify_business_patterns(source_code, filename),
            'type_inference': self._infer_types(source_code, filename),
        }
    
    def _analyze_call_graph(self, source_code: str, filename: str) -> Dict:
        """Build a function call graph showing how functions call each other."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {'calls': [], 'functions': []}
        
        call_graph = {}
        current_function = None
        
        for node in ast.walk(tree):
            # Track function definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = [arg.arg for arg in node.args.args]
                call_graph[node.name] = {
                    'line': node.lineno,
                    'params': params,
                    'calls': [],
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'docstring': ast.get_docstring(node),
                }
        
        # Track function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Get the function being called
                if isinstance(node.func, ast.Name):
                    callee = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    callee = self._extract_attribute_chain(node.func)
                else:
                    continue
                
                # Get arguments
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Name):
                        args.append(arg.id)
                    elif isinstance(arg, ast.Constant):
                        args.append(repr(arg.value))
                
                # Record in appropriate function
                for func_name in call_graph:
                    call_graph[func_name]['calls'].append({
                        'callee': callee,
                        'args': args,
                        'line': node.lineno,
                    })
        
        return {
            'functions': call_graph,
            'filename': filename,
        }
    
    def _extract_attribute_chain(self, node) -> str:
        """Extract attribute chain like obj.method.submeth."""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
    
    def _analyze_data_flow(self, source_code: str, filename: str) -> Dict:
        """Analyze how data flows through functions."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {'flows': []}
        
        data_flows = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Variable assignment: x = y
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # Track what this variable is assigned from
                        source_info = self._extract_value_source(node.value)
                        if source_info:
                            data_flows.append({
                                'target': var_name,
                                'source': source_info,
                                'line': node.lineno,
                                'type': 'assignment',
                            })
            
            elif isinstance(node, ast.AugAssign):
                # Variable modification: x += y
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    source_info = self._extract_value_source(node.value)
                    data_flows.append({
                        'target': var_name,
                        'source': source_info,
                        'line': node.lineno,
                        'type': 'modification',
                    })
        
        return {
            'flows': data_flows,
            'filename': filename,
        }
    
    def _extract_value_source(self, node) -> Optional[str]:
        """Extract what value is coming from."""
        if isinstance(node, ast.Name):
            return f"variable:{node.id}"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return f"function_call:{node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                return f"method_call:{self._extract_attribute_chain(node.func)}"
        elif isinstance(node, ast.Constant):
            return f"literal:{repr(node.value)}"
        elif isinstance(node, ast.BinOp):
            return "computed_value"
        elif isinstance(node, ast.List):
            return "list_literal"
        elif isinstance(node, ast.Dict):
            return "dict_literal"
        return None
    
    def _analyze_control_flow(self, source_code: str, filename: str) -> Dict:
        """Analyze control flow (if/else, loops, etc.)."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {'flows': []}
        
        control_flows = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Extract condition as string
                condition = self._extract_condition(node.test)
                
                # Get operations in each branch
                if_operations = self._extract_operations(node.body)
                else_operations = self._extract_operations(node.orelse) if node.orelse else []
                
                control_flows.append({
                    'type': 'if_else',
                    'condition': condition,
                    'if_branch': if_operations,
                    'else_branch': else_operations,
                    'line': node.lineno,
                })
            
            elif isinstance(node, (ast.For, ast.While)):
                loop_type = 'for_loop' if isinstance(node, ast.For) else 'while_loop'
                condition = self._extract_condition(node.test if isinstance(node, ast.While) else None)
                operations = self._extract_operations(node.body)
                
                control_flows.append({
                    'type': loop_type,
                    'condition': condition,
                    'body': operations,
                    'line': node.lineno,
                })
        
        return {
            'flows': control_flows,
            'filename': filename,
        }
    
    def _extract_condition(self, node) -> str:
        """Extract condition as human-readable string."""
        if node is None:
            return ""
        
        if isinstance(node, ast.Compare):
            left = self._extract_simple_str(node.left)
            conditions = []
            for op, comp in zip(node.ops, node.comparators):
                op_str = self._get_op_string(op)
                right = self._extract_simple_str(comp)
                conditions.append(f"{left} {op_str} {right}")
            return " and ".join(conditions)
        
        elif isinstance(node, ast.BoolOp):
            op_str = "and" if isinstance(node.op, ast.And) else "or"
            values = [self._extract_simple_str(v) for v in node.values]
            return f" {op_str} ".join(values)
        
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return f"not {self._extract_simple_str(node.operand)}"
        
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return f"{node.func.id}(...)"
        
        return "unknown_condition"
    
    def _get_op_string(self, op) -> str:
        """Convert AST operator to string."""
        ops = {
            ast.Eq: '==',
            ast.NotEq: '!=',
            ast.Lt: '<',
            ast.LtE: '<=',
            ast.Gt: '>',
            ast.GtE: '>=',
            ast.Is: 'is',
            ast.IsNot: 'is not',
            ast.In: 'in',
            ast.NotIn: 'not in',
        }
        return ops.get(type(op), str(op))
    
    def _extract_simple_str(self, node) -> str:
        """Extract simple string representation."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        elif isinstance(node, ast.Attribute):
            return self._extract_attribute_chain(node)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return f"{node.func.id}(...)"
        elif isinstance(node, ast.List):
            return "[...]"
        elif isinstance(node, ast.Dict):
            return "{...}"
        return "?"
    
    def _extract_operations(self, body: List) -> List[str]:
        """Extract operations from a body block."""
        operations = []
        for node in body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        operations.append(f"assign:{target.id}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    operations.append(f"call:{node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    operations.append(f"call:{self._extract_attribute_chain(node.func)}")
            elif isinstance(node, ast.Return):
                operations.append("return")
            elif isinstance(node, ast.Raise):
                operations.append("raise")
        return operations
    
    def _infer_types(self, source_code: str, filename: str) -> Dict:
        """Infer variable types from usage patterns."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {'inferred_types': {}}
        
        type_info = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check type annotations
                for arg in node.args.args:
                    if arg.annotation:
                        type_info[f"{node.name}.{arg.arg}"] = self._extract_type(arg.annotation)
                
                # Infer from return type hint
                if node.returns:
                    type_info[f"{node.name}:return"] = self._extract_type(node.returns)
            
            elif isinstance(node, ast.Assign):
                # Infer from assignment
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        inferred = self._infer_type_from_value(node.value)
                        if inferred:
                            type_info[target.id] = inferred
        
        return {
            'inferred_types': type_info,
            'filename': filename,
        }
    
    def _extract_type(self, annotation) -> str:
        """Extract type from type annotation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            container = self._extract_type(annotation.value)
            element = self._extract_type(annotation.slice)
            return f"{container}[{element}]"
        return "unknown"
    
    def _infer_type_from_value(self, node) -> Optional[str]:
        """Infer type from a value node."""
        if isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id  # Assume it's a class or type
        elif isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.Name):
            # Can't easily infer
            return None
        return None
    
    def _identify_business_patterns(self, source_code: str, filename: str) -> Dict:
        """Identify business-relevant patterns in the code."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return {'patterns': []}
        
        patterns = []
        
        # Pattern 1: Workflow functions (have multiple stages)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # A workflow has: validation, processing, notification
                has_validation = self._contains_operation(node, 'validate|assert|check')
                has_processing = self._contains_operation(node, 'process|calculate|compute')
                has_side_effect = self._contains_operation(node, 'save|create|update|delete|send|notify')
                
                if has_validation and has_processing and has_side_effect:
                    patterns.append({
                        'type': 'workflow',
                        'name': node.name,
                        'line': node.lineno,
                        'characteristics': ['validation', 'processing', 'side_effects'],
                    })
                
                # Pattern 2: Authorization/Permission check
                has_permission_check = self._contains_operation(node, 'permission|role|authorized|allowed|access')
                if has_permission_check:
                    patterns.append({
                        'type': 'authorization_logic',
                        'name': node.name,
                        'line': node.lineno,
                    })
                
                # Pattern 3: State machine / status transitions
                has_state_check = self._contains_operation(node, 'status|state|transition|stage')
                if has_state_check and len(node.body) > 5:
                    patterns.append({
                        'type': 'state_machine',
                        'name': node.name,
                        'line': node.lineno,
                    })
        
        return {
            'patterns': patterns,
            'filename': filename,
        }
    
    def _contains_operation(self, node: ast.AST, pattern: str) -> bool:
        """Check if a node contains certain operations."""
        import re
        keywords = pattern.split('|')
        
        code_str = ast.unparse(node) if hasattr(ast, 'unparse') else ""
        for keyword in keywords:
            if keyword.lower() in code_str.lower():
                return True
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if any(keyword.lower() in child.id.lower() for keyword in keywords):
                    return True
        
        return False


def compare_analyses(keyword_results: Dict, semantic_results: Dict) -> Dict:
    """Compare keyword-based vs semantic analysis results."""
    return {
        'keyword_based': keyword_results,
        'semantic_based': semantic_results,
        'improvements': {
            'function_understanding': 'Uses call graph instead of keywords',
            'data_flow': 'Tracks actual variable assignments and flows',
            'control_flow': 'Understands if/else branches and loops',
            'type_awareness': 'Infers types from usage',
            'pattern_recognition': 'Finds complex business patterns',
        }
    }


if __name__ == '__main__':
    # Example usage
    sample_code = '''
def checkout_workflow(customer_id, items):
    """Process customer checkout"""
    # Validation
    customer = get_customer(customer_id)
    if not customer.is_active:
        raise PermissionError("Customer not active")
    
    if not items:
        raise ValueError("No items in checkout")
    
    # Processing
    total = calculate_total(items)
    if customer.balance < total:
        raise InsufficientFundsError("Low balance")
    
    # Side effects
    payment = payment_gateway.process(customer, total)
    order = create_order(customer, items, payment)
    send_email(customer.email, order)
    
    return order
'''
    
    analyzer = SemanticAnalyzer('python')
    result = analyzer.analyze(sample_code, 'example.py')
    
    print("=== Semantic Analysis Results ===\n")
    
    print("Call Graph:")
    for func, info in result['call_graph'].get('functions', {}).items():
        print(f"  {func}:")
        print(f"    Calls: {[c['callee'] for c in info['calls']]}")
    
    print("\nData Flows:")
    for flow in result['data_flow'].get('flows', []):
        print(f"  {flow['target']} <- {flow['source']} (line {flow['line']})")
    
    print("\nControl Flow:")
    for flow in result['control_flow'].get('flows', []):
        print(f"  {flow['type']}: {flow.get('condition', 'N/A')}")
        if 'if_branch' in flow:
            print(f"    If: {flow['if_branch']}")
            print(f"    Else: {flow['else_branch']}")
    
    print("\nBusiness Patterns:")
    for pattern in result['business_patterns'].get('patterns', []):
        print(f"  {pattern['type']}: {pattern['name']}")
