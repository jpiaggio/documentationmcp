"""
Business Rules and Customer Journey Extractor

Extracts non-technical, business-level insights from code:
- Customer journeys and workflows
- Business rules and constraints
- Decision logic and branching
- Business entities and relationships
- Integration points with external systems
- Business events and state transitions
"""

import re
import os
from typing import List, Dict, Tuple

class BusinessRulesExtractor:
    """Extract business logic and customer journeys from source code."""
    
    def __init__(self):
        # Patterns for detecting business-relevant code
        self.workflow_keywords = [
            'workflow', 'process', 'journey', 'pipeline', 'flow',
            'state', 'status', 'stage', 'phase', 'step',
            'transition', 'state_machine'
        ]
        
        self.business_entity_keywords = [
            'user', 'customer', 'order', 'payment', 'invoice',
            'account', 'product', 'cart', 'subscription', 'transaction',
            'member', 'profile', 'session', 'cart_item', 'shipment'
        ]
        
        self.business_event_keywords = [
            'created', 'updated', 'deleted', 'completed', 'cancelled',
            'approved', 'rejected', 'submitted', 'processed', 'pending',
            'failed', 'succeeded', 'triggered', 'fired'
        ]
        
        self.integration_keywords = [
            'payment_gateway', 'stripe', 'paypal', 'sms', 'email',
            'notification', 'webhook', 'api_call', 'kafka', 'queue',
            'external_service', 'http_request', 'api_client'
        ]
        
        self.business_rule_keywords = [
            'validate', 'verify', 'check', 'constraint', 'rule',
            'eligibility', 'permission', 'access_control', 'rate_limit',
            'quota', 'threshold', 'timeout', 'retry', 'fallback'
        ]
    
    def extract_business_processes(self, source_code: str, filename: str) -> List[Dict]:
        """Extract workflow/process definitions from code."""
        processes = []
        
        # Look for function/method definitions related to workflows
        for keyword in self.workflow_keywords:
            pattern = rf'(?:def|function|class)\s+\w*{keyword}\w*\s*\('
            matches = re.finditer(pattern, source_code, re.IGNORECASE)
            for match in matches:
                # Extract the function/method name and context
                start = match.start()
                end = min(start + 200, len(source_code))
                context = source_code[start:end]
                
                name_match = re.search(r'(?:def|function|class)\s+(\w+)', context)
                if name_match:
                    processes.append({
                        'type': 'WORKFLOW',
                        'name': name_match.group(1),
                        'keyword': keyword,
                        'file': filename,
                        'context': context.split('\n')[0]
                    })
        
        return processes
    
    def extract_business_entities(self, source_code: str, filename: str) -> List[Dict]:
        """Extract business entities and their properties."""
        entities = []
        
        # Look for class definitions and data models
        class_pattern = r'class\s+(\w+)\s*(?:\(([^)]*)\))?:'
        for match in re.finditer(class_pattern, source_code):
            class_name = match.group(1)
            
            # Check if this looks like a business entity
            for entity_keyword in self.business_entity_keywords:
                if entity_keyword.lower() in class_name.lower():
                    # Extract properties/attributes
                    class_start = match.start()
                    class_end = min(class_start + 500, len(source_code))
                    class_body = source_code[class_start:class_end]
                    
                    # Find field definitions
                    properties = re.findall(r'self\.(\w+)\s*=', class_body)
                    
                    entities.append({
                        'type': 'BUSINESS_ENTITY',
                        'name': class_name,
                        'entity_type': entity_keyword,
                        'properties': list(set(properties)),
                        'file': filename,
                        'parent_class': match.group(2) if match.group(2) else None
                    })
                    break
        
        return entities
    
    def extract_customer_journey_steps(self, source_code: str, filename: str) -> List[Dict]:
        """Extract steps in a customer journey/workflow."""
        steps = []
        
        # Look for sequential operations that represent journey steps
        step_indicators = [
            (r'(\w+)\s*=\s*get_user|fetch_user', 'AUTHENTICATE'),
            (r'(\w+)\s*=\s*browse|search|list', 'BROWSE'),
            (r'(\w+)\s*=\s*select|add.*cart', 'SELECT_PRODUCT'),
            (r'(\w+)\s*=\s*(?:checkout|process_payment|submit_order)', 'CHECKOUT'),
            (r'(?:send_email|send_notification|notify)', 'NOTIFY'),
            (r'(?:update_status|update_state|transition)', 'UPDATE_STATUS'),
            (r'(?:create_shipment|ship|dispatch)', 'SHIP'),
            (r'(?:deliver|received|delivered)', 'DELIVER'),
            (r'(?:refund|return|cancel)', 'CANCEL'),
        ]
        
        for pattern, step_name in step_indicators:
            for match in re.finditer(pattern, source_code, re.IGNORECASE):
                step_start = max(0, match.start() - 100)
                step_end = min(match.end() + 100, len(source_code))
                context = source_code[step_start:step_end]
                
                steps.append({
                    'type': 'JOURNEY_STEP',
                    'step': step_name,
                    'file': filename,
                    'context': ' '.join(context.split())[:150]
                })
        
        return steps
    
    def extract_business_rules(self, source_code: str, filename: str) -> List[Dict]:
        """Extract business rules and constraints."""
        rules = []
        
        # Pattern 1: Validation logic
        validation_pattern = r'(?:if|elif)\s+(?:not\s+)?(\w+.*?)[:\)]\s*(?:#.*?)?$'
        for match in re.finditer(validation_pattern, source_code, re.MULTILINE):
            condition = match.group(1).strip()
            
            # Filter out overly generic conditions
            if any(kw in condition.lower() for kw in self.business_rule_keywords):
                rules.append({
                    'type': 'BUSINESS_RULE',
                    'rule_type': 'VALIDATION',
                    'condition': condition[:100],
                    'file': filename
                })
        
        # Pattern 2: Error messages and business logic
        error_pattern = r'raise\s+\w+\("([^"]+)"\)'
        for match in re.finditer(error_pattern, source_code):
            error_msg = match.group(1)
            if any(keyword in error_msg.lower() for keyword in ['invalid', 'insufficient', 'expired', 'not eligible', 'cannot']):
                rules.append({
                    'type': 'BUSINESS_RULE',
                    'rule_type': 'CONSTRAINT',
                    'message': error_msg,
                    'file': filename
                })
        
        # Pattern 3: Logic with magic numbers (thresholds, limits)
        threshold_pattern = r'(\w+)\s*(?:>=|<=|==|>|<)\s*(\d+(?:\.\d+)?)'
        for match in re.finditer(threshold_pattern, source_code):
            variable = match.group(1)
            threshold = match.group(2)
            
            rules.append({
                'type': 'BUSINESS_RULE',
                'rule_type': 'THRESHOLD',
                'variable': variable,
                'value': threshold,
                'file': filename
            })
        
        return rules
    
    def extract_integrations(self, source_code: str, filename: str) -> List[Dict]:
        """Extract external system integrations."""
        integrations = []
        
        for keyword in self.integration_keywords:
            # Look for imports, function calls, or configuration
            pattern = rf'(?:import|from|{keyword})[^\\n]*{keyword}'
            matches = re.finditer(pattern, source_code, re.IGNORECASE)
            
            for match in matches:
                line_start = source_code.rfind('\n', 0, match.start()) + 1
                line_end = source_code.find('\n', match.end())
                line = source_code[line_start:line_end]
                
                integrations.append({
                    'type': 'INTEGRATION',
                    'system': keyword,
                    'reference': line.strip(),
                    'file': filename
                })
        
        return integrations
    
    def extract_business_events(self, source_code: str, filename: str) -> List[Dict]:
        """Extract business events and state transitions."""
        events = []
        
        # Look for event-like patterns
        event_pattern = r'(?:emit|publish|trigger|on_|handle_)\w+|\.(\w+_event)\('
        for match in re.finditer(event_pattern, source_code, re.IGNORECASE):
            event_context_start = max(0, match.start() - 80)
            event_context_end = min(match.end() + 80, len(source_code))
            context = source_code[event_context_start:event_context_end]
            
            # Extract event name
            event_name = match.group(0).replace('(', '').replace(')', '').strip()
            
            events.append({
                'type': 'BUSINESS_EVENT',
                'event': event_name,
                'file': filename,
                'context': ' '.join(context.split())[:120]
            })
        
        # Look for state transitions
        state_pattern = r'(?:status|state)\s*=\s*["\'](\w+)["\']'
        for match in re.finditer(state_pattern, source_code):
            state_value = match.group(1)
            
            state_context_start = max(0, match.start() - 100)
            state_context_end = min(match.end() + 50, len(source_code))
            context = source_code[state_context_start:state_context_end]
            
            events.append({
                'type': 'STATE_TRANSITION',
                'state': state_value,
                'file': filename,
                'context': ' '.join(context.split())[:120]
            })
        
        return events
    
    def extract_role_based_logic(self, source_code: str, filename: str) -> List[Dict]:
        """Extract role-based access and permissions."""
        roles = []
        
        # Look for role/permission checks
        role_pattern = r'(?:is_|has_|role_|permission_)(\w+)|\.(\w+)\s*(?:==|in)\s*["\'](\w+)["\']'
        for match in re.finditer(role_pattern, source_code, re.IGNORECASE):
            role_name = match.group(1) or match.group(3) or match.group(2)
            
            if role_name and len(role_name) > 2:
                role_context = max(0, match.start() - 60)
                context = source_code[role_context:match.end() + 60]
                
                roles.append({
                    'type': 'ROLE_PERMISSION',
                    'role': role_name.lower(),
                    'file': filename,
                    'context': ' '.join(context.split())[:100]
                })
        
        return roles
    
    def extract_all_business_insights(self, source_code: str, filename: str) -> Dict:
        """Extract all business-level insights from code."""
        return {
            'processes': self.extract_business_processes(source_code, filename),
            'entities': self.extract_business_entities(source_code, filename),
            'journey_steps': self.extract_customer_journey_steps(source_code, filename),
            'rules': self.extract_business_rules(source_code, filename),
            'integrations': self.extract_integrations(source_code, filename),
            'events': self.extract_business_events(source_code, filename),
            'roles': self.extract_role_based_logic(source_code, filename),
        }


def generate_business_cypher(insights: Dict, module_name: str, filepath: str) -> List[str]:
    """Generate Cypher statements for business insights."""
    cypher_statements = []
    
    # Create module node
    cypher_statements.append(
        f"MERGE (m:BusinessModule {{name: '{module_name}', path: '{filepath}', domain: 'business'}})"
    )
    
    # Business Processes
    for process in insights.get('processes', []):
        cypher_statements.append(
            f"MERGE (p:BusinessProcess {{name: '{process['name']}', keyword: '{process['keyword']}'}})\n"
            f"MERGE (m)-[:IMPLEMENTS]->(p)"
        )
    
    # Business Entities
    for entity in insights.get('entities', []):
        props_str = ', '.join(entity.get('properties', [])[:5])  # Limit to 5 props
        cypher_statements.append(
            f"MERGE (e:BusinessEntity {{name: '{entity['name']}', type: '{entity['entity_type']}', properties: '{props_str}'}})\n"
            f"MERGE (m)-[:MANAGES]->(e)"
        )
    
    # Customer Journey Steps
    journey_steps = insights.get('journey_steps', [])
    if journey_steps:
        unique_steps = {}
        for step in journey_steps:
            if step['step'] not in unique_steps:
                unique_steps[step['step']] = step
        
        for i, (step_name, step_data) in enumerate(sorted(unique_steps.items())):
            cypher_statements.append(
                f"MERGE (j:JourneyStep {{name: '{step_name}', sequence: {i}}})\n"
                f"MERGE (m)-[:CONTAINS_STEP]->(j)"
            )
    
    # Business Rules
    for rule in insights.get('rules', []):
        if rule['rule_type'] == 'VALIDATION':
            cypher_statements.append(
                f"MERGE (r:BusinessRule {{type: 'VALIDATION', condition: '{rule['condition'][:50]}'}})\n"
                f"MERGE (m)-[:ENFORCES]->(r)"
            )
        elif rule['rule_type'] == 'CONSTRAINT':
            cypher_statements.append(
                f"MERGE (c:Constraint {{type: 'CONSTRAINT', message: '{rule['message'][:60]}'}})\n"
                f"MERGE (m)-[:ENFORCES]->(c)"
            )
        elif rule['rule_type'] == 'THRESHOLD':
            cypher_statements.append(
                f"MERGE (t:Threshold {{variable: '{rule['variable']}', value: '{rule['value']}'}})\n"
                f"MERGE (m)-[:DEFINES]->(t)"
            )
    
    # Integrations
    for integration in insights.get('integrations', []):
        cypher_statements.append(
            f"MERGE (int:ExternalSystem {{name: '{integration['system']}'}})\n"
            f"MERGE (m)-[:INTEGRATES_WITH]->(int)"
        )
    
    # Business Events
    for event in insights.get('events', []):
        if event['type'] == 'BUSINESS_EVENT':
            cypher_statements.append(
                f"MERGE (ev:BusinessEvent {{name: '{event['event']}'}})\n"
                f"MERGE (m)-[:TRIGGERS]->(ev)"
            )
        elif event['type'] == 'STATE_TRANSITION':
            cypher_statements.append(
                f"MERGE (st:State {{name: '{event['state']}'}})\n"
                f"MERGE (m)-[:TRANSITIONS_TO]->(st)"
            )
    
    # Roles and Permissions
    for role in insights.get('roles', []):
        cypher_statements.append(
            f"MERGE (rol:Role {{name: '{role['role']}'}})\n"
            f"MERGE (m)-[:REQUIRES_ROLE]->(rol)"
        )
    
    return cypher_statements


if __name__ == '__main__':
    # Example usage
    extractor = BusinessRulesExtractor()
    
    # Test with a sample
    sample_code = '''
    def checkout_workflow(customer_id, items):
        """Customer checkout workflow"""
        customer = get_customer(customer_id)
        
        validate(customer.is_active)
        validate(len(items) > 0)
        
        if customer.account_balance < calculate_total(items):
            raise InsufficientFundsError("Customer balance too low")
        
        payment_gateway.process_payment(customer, items)
        order = create_order(customer, items)
        
        send_email_notification(customer.email, order)
        update_inventory(items)
        
        return order
    '''
    
    insights = extractor.extract_all_business_insights(sample_code, 'checkout.py')
    for category, items in insights.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item}")
