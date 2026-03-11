"""
Enhanced Business Rules Extractor - Semantic Version with Smart Rule Inference

Combines AST-based semantic analysis with keyword-based pattern matching
for comprehensive business insight extraction. Includes Smart Rule Inference:
- Automatic validation rule detection (min/max, ranges, patterns)
- Temporal dependency discovery (state machines, ordering)
- Permission hierarchy mapping
- Error handling constraint extraction
"""

import sys
import os
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict

# Import semantic analyzer and smart inference
sys.path.insert(0, os.path.dirname(__file__))
from semantic_analyzer import SemanticAnalyzer
from business_rules_extractor import BusinessRulesExtractor, generate_business_cypher
from smart_rule_inference import SmartRuleInference


@dataclass
class BusinessPattern:
    """Represents a detected business pattern."""
    pattern_type: str
    confidence: float  # 0.0 to 1.0
    name: str
    line: int
    description: str
    evidence: List[str]  # What led to this detection


class EnhancedBusinessExtractor:
    """Enhanced business rules extractor using semantic analysis."""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer('python')
        self.keyword_extractor = BusinessRulesExtractor()
        self.rule_inferencer = SmartRuleInference()
    
    def extract_workflows(self, source_code: str, filename: str) -> List[Dict]:
        """Extract workflow/process definitions using semantic analysis."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        workflows = []
        
        # Use semantic patterns first
        for pattern in results['business_patterns'].get('patterns', []):
            if pattern['type'] == 'workflow':
                # Get the actual function definition
                call_graph = results['call_graph'].get('functions', {})
                func_name = pattern['name']
                if func_name in call_graph:
                    func_info = call_graph[func_name]
                    
                    workflows.append({
                        'type': 'WORKFLOW',
                        'name': func_name,
                        'line': pattern['line'],
                        'characteristics': pattern.get('characteristics', []),
                        'functions_called': [c['callee'] for c in func_info['calls']],
                        'docstring': func_info.get('docstring', ''),
                        'confidence': 'HIGH',  # Semantic detection is more confident
                        'detection_method': 'semantic_analysis',
                    })
        
        return workflows
    
    def extract_business_entities(self, source_code: str, filename: str) -> List[Dict]:
        """Extract business entities with semantic understanding."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        entities = []
        
        # Look at inferred types to find business entities
        inferred_types = results['type_inference'].get('inferred_types', {})
        
        # Also use data flow to identify entity-like structures
        data_flows = results['data_flow'].get('flows', [])
        
        # Entity candidates: classes or objects that hold state
        entity_candidates = set()
        for flow in data_flows:
            # If something is assigned from a function call, it might be an entity
            if 'function_call:' in flow.get('source', ''):
                entity_candidates.add(flow['target'])
        
        # Combine with keyword-based extraction for comprehensiveness
        keyword_entities = self.keyword_extractor.extract_business_entities(source_code, filename)
        
        # Keep all detected entities
        entities.extend(keyword_entities)
        
        # Add semantic insights
        for entity_name in entity_candidates:
            # Check if it looks like a business entity
            entity_type = inferred_types.get(entity_name, 'object')
            if entity_type not in ['int', 'str', 'float', 'bool', 'list', 'dict']:
                entities.append({
                    'type': 'BUSINESS_ENTITY',
                    'name': entity_name,
                    'entity_type': entity_type,
                    'inferred_type': entity_type,
                    'file': filename,
                    'confidence': 'MEDIUM',
                    'detection_method': 'semantic_analysis',
                })
        
        return entities
    
    def extract_data_flows(self, source_code: str, filename: str) -> List[Dict]:
        """Extract how data flows through the system."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        
        flows = []
        for flow in results['data_flow'].get('flows', []):
            flows.append({
                'type': 'DATA_FLOW',
                'target': flow['target'],
                'source': flow['source'],
                'line': flow['line'],
                'operation': flow['type'],
                'file': filename,
            })
        
        return flows
    
    def extract_business_rules(self, source_code: str, filename: str) -> List[Dict]:
        """Extract business rules with semantic validation."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        rules = []
        
        # Get control flow and look for validation patterns
        control_flows = results['control_flow'].get('flows', [])
        
        for flow in control_flows:
            if flow['type'] == 'if_else':
                condition = flow['condition']
                
                # This is a business rule condition
                rules.append({
                    'type': 'BUSINESS_RULE',
                    'rule_type': 'CONDITIONAL',
                    'condition': condition,
                    'line': flow['line'],
                    'if_operations': flow.get('if_branch', []),
                    'else_operations': flow.get('else_branch', []),
                    'file': filename,
                    'detection_method': 'control_flow_analysis',
                })
        
        # Combine with keyword-based for additional rules
        keyword_rules = self.keyword_extractor.extract_business_rules(source_code, filename)
        rules.extend(keyword_rules)
        
        return rules
    
    def extract_integrations(self, source_code: str, filename: str) -> List[Dict]:
        """Extract external system integrations."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        integrations = []
        
        # Look at function calls to external services
        call_graph = results['call_graph'].get('functions', {})
        
        # Common integration patterns
        integration_keywords = {
            'stripe': 'payment_gateway',
            'paypal': 'payment_gateway',
            'email': 'notification',
            'sms': 'notification',
            'kafka': 'event_streaming',
            'redis': 'cache',
            'database': 'data_store',
            'elasticsearch': 'search',
            'api': 'external_api',
        }
        
        for func_name, func_info in call_graph.items():
            for call in func_info['calls']:
                callee = call['callee']
                
                # Check for integrations in function names
                for keyword, category in integration_keywords.items():
                    if keyword.lower() in callee.lower():
                        integrations.append({
                            'type': 'INTEGRATION',
                            'system': keyword,
                            'category': category,
                            'function': callee,
                            'called_from': func_name,
                            'line': call['line'],
                            'file': filename,
                            'detection_method': 'call_graph_analysis',
                        })
        
        # Add keyword-based integrations too
        keyword_integrations = self.keyword_extractor.extract_integrations(source_code, filename)
        integrations.extend(keyword_integrations)
        
        return integrations
    
    def extract_authorization_logic(self, source_code: str, filename: str) -> List[Dict]:
        """Extract authorization and permission checks."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        auth_logic = []
        
        # Look for function patterns that indicate authorization
        patterns = results['business_patterns'].get('patterns', [])
        
        for pattern in patterns:
            if pattern['type'] == 'authorization_logic':
                auth_logic.append({
                    'type': 'AUTHORIZATION',
                    'function': pattern['name'],
                    'line': pattern['line'],
                    'file': filename,
                    'detection_method': 'semantic_pattern_analysis',
                })
        
        # Also check control flow for permission checks
        control_flows = results['control_flow'].get('flows', [])
        for flow in control_flows:
            condition = flow.get('condition', '').lower()
            if any(kw in condition for kw in ['permission', 'role', 'authorized', 'allowed']):
                auth_logic.append({
                    'type': 'AUTHORIZATION',
                    'check_type': 'conditional',
                    'condition': flow['condition'],
                    'line': flow['line'],
                    'file': filename,
                    'detection_method': 'control_flow_analysis',
                })
        
        return auth_logic
    
    def extract_state_machines(self, source_code: str, filename: str) -> List[Dict]:
        """Extract state machine and workflow state transitions."""
        results = self.semantic_analyzer.analyze(source_code, filename)
        state_machines = []
        
        # Look for state patterns
        patterns = results['business_patterns'].get('patterns', [])
        
        for pattern in patterns:
            if pattern['type'] == 'state_machine':
                state_machines.append({
                    'type': 'STATE_MACHINE',
                    'name': pattern['name'],
                    'line': pattern['line'],
                    'file': filename,
                    'detection_method': 'semantic_pattern_analysis',
                })
        
        # Look for state transitions in control flow
        control_flows = results['control_flow'].get('flows', [])
        for flow in control_flows:
            if any(kw in str(flow).lower() for kw in ['status', 'state', 'transition']):
                state_machines.append({
                    'type': 'STATE_TRANSITION',
                    'condition': flow.get('condition', ''),
                    'line': flow['line'],
                    'file': filename,
                    'detection_method': 'control_flow_pattern',
                })
        
        return state_machines
    
    def extract_inferred_validation_rules(self, source_code: str, filename: str) -> List[Dict]:
        """Extract validation rules using smart rule inference."""
        inferred = self.rule_inferencer.infer_all_rules(source_code, filename)
        
        rules = []
        for rule in inferred.get('validation_rules', []):
            rules.append({
                'type': 'VALIDATION_RULE',
                'field': rule['field_name'],
                'operation': rule['operation'],
                'value': rule['value'],
                'line': rule['line'],
                'severity': rule.get('severity', 'REQUIRED'),
                'description': rule.get('description', ''),
                'file': filename,
                'detection_method': 'smart_rule_inference',
            })
        
        return rules
    
    def extract_inferred_temporal_dependencies(self, source_code: str, filename: str) -> List[Dict]:
        """Extract temporal ordering requirements."""
        inferred = self.rule_inferencer.infer_all_rules(source_code, filename)
        
        dependencies = []
        for dep in inferred.get('temporal_dependencies', []):
            dependencies.append({
                'type': 'TEMPORAL_DEPENDENCY',
                'precondition': dep['precondition'],
                'postcondition': dep['postcondition'],
                'dependency_type': dep['dependency_type'],
                'evidence': dep.get('evidence', []),
                'line': dep['line'],
                'file': filename,
                'detection_method': 'smart_rule_inference',
            })
        
        return dependencies
    
    def extract_inferred_permission_rules(self, source_code: str, filename: str) -> List[Dict]:
        """Extract permission hierarchies and access control rules."""
        inferred = self.rule_inferencer.infer_all_rules(source_code, filename)
        
        rules = []
        for rule in inferred.get('permission_rules', []):
            rules.append({
                'type': 'PERMISSION_RULE',
                'resource': rule['resource'],
                'actor_type': rule['actor_type'],
                'action': rule['action'],
                'condition': rule.get('condition'),
                'hierarchy_level': rule.get('hierarchy_level', 0),
                'line': rule['line'],
                'file': filename,
                'detection_method': 'smart_rule_inference',
            })
        
        return rules
    
    def extract_inferred_constraint_rules(self, source_code: str, filename: str) -> List[Dict]:
        """Extract constraints from error handling."""
        inferred = self.rule_inferencer.infer_all_rules(source_code, filename)
        
        constraints = []
        for rule in inferred.get('constraint_rules', []):
            constraints.append({
                'type': 'CONSTRAINT_RULE',
                'constraint': rule['constraint'],
                'triggered_by': rule['triggered_by'],
                'error_message': rule.get('error_message'),
                'severity': rule.get('severity', 'ERROR'),
                'line': rule['line'],
                'file': filename,
                'detection_method': 'smart_rule_inference',
            })
        
        return constraints
    
    def extract_smart_business_insights(self, source_code: str, filename: str) -> Dict:
        """Extract all smart inference insights."""
        return {
            'validation_rules': self.extract_inferred_validation_rules(source_code, filename),
            'temporal_dependencies': self.extract_inferred_temporal_dependencies(source_code, filename),
            'permission_rules': self.extract_inferred_permission_rules(source_code, filename),
            'constraint_rules': self.extract_inferred_constraint_rules(source_code, filename),
        }

    
    def extract_all_enhanced_insights(self, source_code: str, filename: str) -> Dict:
        """Extract all business insights using semantic analysis and smart inference."""
        smart_insights = self.extract_smart_business_insights(source_code, filename)
        
        return {
            'workflows': self.extract_workflows(source_code, filename),
            'entities': self.extract_business_entities(source_code, filename),
            'data_flows': self.extract_data_flows(source_code, filename),
            'rules': self.extract_business_rules(source_code, filename),
            'integrations': self.extract_integrations(source_code, filename),
            'authorization': self.extract_authorization_logic(source_code, filename),
            'state_machines': self.extract_state_machines(source_code, filename),
            'smart_insights': smart_insights,  # Add smart inference results
        }
    
    def generate_analysis_report(self, source_code: str, filename: str) -> str:
        """Generate a human-readable report of semantic analysis findings."""
        insights = self.extract_all_enhanced_insights(source_code, filename)
        
        lines = [
            f"=== Semantic Analysis Report: {filename} ===\n",
        ]
        
        if insights['workflows']:
            lines.append(f"\n📋 WORKFLOWS ({len(insights['workflows'])})")
            for wf in insights['workflows']:
                lines.append(f"  - {wf['name']} (line {wf['line']})")
                lines.append(f"    Calls: {', '.join(wf['functions_called'])}")
        
        if insights['entities']:
            lines.append(f"\n📦 BUSINESS ENTITIES ({len(insights['entities'])})")
            for entity in insights['entities'][:10]:  # Show first 10
                lines.append(f"  - {entity['name']} ({entity.get('entity_type', 'unknown')})")
        
        if insights['data_flows']:
            lines.append(f"\n🔄 DATA FLOWS ({len(insights['data_flows'])})")
            for i, flow in enumerate(insights['data_flows'][:5]):  # Show first 5
                lines.append(f"  - {flow['target']} ← {flow['source']} ({flow['operation']})")
        
        if insights['rules']:
            lines.append(f"\n⚖️ BUSINESS RULES ({len(insights['rules'])})")
            for rule in insights['rules'][:5]:  # Show first 5
                if 'condition' in rule:
                    lines.append(f"  - {rule['condition']}")
        
        if insights['integrations']:
            lines.append(f"\n🔗 INTEGRATIONS ({len(insights['integrations'])})")
            systems = set()
            for integ in insights['integrations']:
                systems.add(integ['system'])
            for system in sorted(systems):
                lines.append(f"  - {system}")
        
        if insights['authorization']:
            lines.append(f"\n🔐 AUTHORIZATION CHECKS ({len(insights['authorization'])})")
            for auth in insights['authorization'][:5]:
                if 'condition' in auth:
                    lines.append(f"  - {auth['condition']}")
                else:
                    lines.append(f"  - {auth['function']}")
        
        # Add smart inference insights
        smart = insights.get('smart_insights', {})
        
        if smart.get('validation_rules'):
            lines.append(f"\n✓ VALIDATION RULES (Smart Inference: {len(smart['validation_rules'])})")
            for rule in smart['validation_rules'][:5]:
                lines.append(f"  - {rule['field']} {rule['operation']} {rule['value']} ({rule['severity']})")
        
        if smart.get('temporal_dependencies'):
            lines.append(f"\n⏱️  TEMPORAL DEPENDENCIES ({len(smart['temporal_dependencies'])})")
            for dep in smart['temporal_dependencies'][:5]:
                lines.append(f"  - {dep['precondition']} → {dep['postcondition']} [{dep['dependency_type']}]")
        
        if smart.get('permission_rules'):
            lines.append(f"\n🔒 PERMISSION HIERARCHY ({len(smart['permission_rules'])})")
            for rule in smart['permission_rules'][:5]:
                lines.append(f"  - {rule['actor_type']} can {rule['action']} {rule['resource']}")
        
        if smart.get('constraint_rules'):
            lines.append(f"\n🚫 CONSTRAINTS (from error handling: {len(smart['constraint_rules'])})")
            for const in smart['constraint_rules'][:5]:
                lines.append(f"  - {const['constraint']} ({const['severity']})")
        
        return "\n".join(lines)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_business_extractor.py <python_file>")
        sys.exit(1)
    
    python_file = sys.argv[1]
    with open(python_file, 'r') as f:
        source_code = f.read()
    
    extractor = EnhancedBusinessExtractor()
    report = extractor.generate_analysis_report(source_code, python_file)
    print(report)
