"""
Business Rules Query Tool for Customer Journey Analysis

This tool allows you to query the business insights graph created by the
cartographer agent to understand customer journeys and business rules.
"""

import re
import sys
from collections import defaultdict
from typing import List, Dict, Set, Tuple

class BusinessJourneyAnalyzer:
    """Analyze business journey and rules from Cypher statements."""
    
    def __init__(self, cypher_statements: List[str]):
        """Initialize with Cypher statements from cartographer agent."""
        self.statements = cypher_statements
        self.modules = {}
        self.entities = defaultdict(list)
        self.journey_steps = defaultdict(list)
        self.rules = []
        self.integrations = defaultdict(list)
        self.events = defaultdict(list)
        self.processes = defaultdict(list)
        
        self._parse_statements()
    
    def _extract_quoted_value(self, text: str, pattern: str) -> str:
        """Extract a quoted value from text."""
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return ""
    
    def _parse_statements(self):
        """Parse Cypher statements to build graph structure."""
        for stmt in self.statements:
            if 'BusinessModule' in stmt:
                module_name = self._extract_quoted_value(stmt, r"name:\s*'([^']+)'")
                if module_name:
                    self.modules[module_name] = stmt
            
            elif 'BusinessEntity' in stmt:
                entity_name = self._extract_quoted_value(stmt, r"name:\s*'([^']+)'")
                entity_type = self._extract_quoted_value(stmt, r"type:\s*'([^']+)'")
                if entity_name:
                    self.entities[entity_type].append(entity_name)
            
            elif 'JourneyStep' in stmt:
                step_name = self._extract_quoted_value(stmt, r"name:\s*'([^']+)'")
                if step_name:
                    self.journey_steps['all'].append(step_name)
            
            elif 'BusinessRule' in stmt:
                rule_type = self._extract_quoted_value(stmt, r"type:\s*'([^']+)'")
                self.rules.append((rule_type, stmt))
            
            elif 'ExternalSystem' in stmt:
                system_name = self._extract_quoted_value(stmt, r"name:\s*'([^']+)'")
                if system_name:
                    self.integrations[system_name].append(stmt)
            
            elif 'BusinessEvent' in stmt:
                event_name = self._extract_quoted_value(stmt, r"name:\s*'([^']+)'")
                if event_name:
                    self.events[event_name].append(stmt)
            
            elif 'BusinessProcess' in stmt:
                process_name = self._extract_quoted_value(stmt, r"name:\s*'([^']+)'")
                if process_name:
                    self.processes[process_name].append(stmt)
    
    def get_customer_journey(self) -> Dict:
        """Get the typical customer journey."""
        journey_order = [
            'AUTHENTICATE', 'BROWSE', 'SELECT_PRODUCT', 'CHECKOUT',
            'NOTIFY', 'UPDATE_STATUS', 'SHIP', 'DELIVER', 'CANCEL'
        ]
        
        found_steps = []
        for step in journey_order:
            if step in self.journey_steps.get('all', []):
                found_steps.append(step)
        
        return {
            'journey_path': ' → '.join(found_steps),
            'total_steps': len(found_steps),
            'steps': found_steps
        }
    
    def get_business_entities(self) -> Dict:
        """Get all business entities by type."""
        return {
            'entities_by_type': dict(self.entities),
            'total_entity_types': len(self.entities),
            'total_entities': sum(len(v) for v in self.entities.values())
        }
    
    def get_business_rules_summary(self) -> Dict:
        """Get summary of business rules."""
        rule_types = defaultdict(int)
        for rule_type, _ in self.rules:
            rule_types[rule_type] += 1
        
        return {
            'rule_count': len(self.rules),
            'rule_types': dict(rule_types),
            'rules_by_type': {rt: self.rules.count((rt, '')) for rt in rule_types.keys()}
        }
    
    def get_integrations(self) -> Dict:
        """Get all external system integrations."""
        return {
            'integrations': list(self.integrations.keys()),
            'integration_count': len(self.integrations),
            'integration_types': {
                'payments': [i for i in self.integrations.keys() if any(p in i for p in ['stripe', 'paypal', 'payment'])],
                'communications': [i for i in self.integrations.keys() if any(c in i for c in ['email', 'sms', 'notification'])],
                'other': [i for i in self.integrations.keys() if not any(x in i for x in ['stripe', 'paypal', 'payment', 'email', 'sms', 'notification'])]
            }
        }
    
    def get_business_processes(self) -> Dict:
        """Get all business processes."""
        return {
            'processes': list(self.processes.keys()),
            'process_count': len(self.processes)
        }
    
    def get_events_and_transitions(self) -> Dict:
        """Get business events and state transitions."""
        return {
            'events': list(self.events.keys()),
            'event_count': len(self.events)
        }
    
    def analyze_journey_dependencies(self) -> Dict:
        """Analyze what rules and integrations support the customer journey."""
        return {
            'journey': self.get_customer_journey(),
            'entities_involved': self.get_business_entities(),
            'rules_enforced': self.get_business_rules_summary(),
            'integrations_used': self.get_integrations(),
            'processes': self.get_business_processes(),
            'events_triggered': self.get_events_and_transitions()
        }
    
    def get_business_context(self) -> str:
        """Generate business context string for AI understanding."""
        analysis = self.analyze_journey_dependencies()
        
        context = "## Platform Business Context\n\n"
        
        # Customer Journey
        journey = analysis['journey']
        context += f"### Customer Journey\n"
        context += f"Path: {journey['journey_path']}\n"
        context += f"Total Steps: {journey['total_steps']}\n\n"
        
        # Entities
        entities = analysis['entities_involved']
        context += f"### Business Entities\n"
        context += f"Total Entity Types: {entities['total_entity_types']}\n"
        for entity_type, items in entities['entities_by_type'].items():
            context += f"- **{entity_type.title()}** ({len(items)}): {', '.join(items[:5])}"
            if len(items) > 5:
                context += f" +{len(items)-5} more"
            context += "\n"
        context += "\n"
        
        # Rules
        rules = analysis['rules_enforced']
        context += f"### Business Rules\n"
        context += f"Total Rules: {rules['rule_count']}\n"
        for rule_type, count in rules['rule_types'].items():
            context += f"- {rule_type}: {count}\n"
        context += "\n"
        
        # Integrations
        integrations = analysis['integrations_used']
        context += f"### External Integrations\n"
        context += f"Total Systems: {integrations['integration_count']}\n"
        for system in integrations['integrations']:
            context += f"- {system}\n"
        context += "\n"
        
        # Processes
        processes = analysis['processes']
        context += f"### Business Processes\n"
        context += f"Total Processes: {processes['process_count']}\n"
        for process in processes['processes'][:10]:
            context += f"- {process}\n"
        context += "\n"
        
        # Events
        events = analysis['events_triggered']
        context += f"### Business Events\n"
        context += f"Total Events: {events['event_count']}\n"
        for event in events['events'][:10]:
            context += f"- {event}\n"
        
        return context


def analyze_platform(cypher_file_or_statements: str) -> str:
    """Analyze platform from Cypher statements."""
    # Try to read as file first
    try:
        with open(cypher_file_or_statements, 'r') as f:
            content = f.read()
        statements = [line.strip() for line in content.split('\n') if line.strip() and 'MERGE' in line]
    except:
        # Assume it's the statements directly
        if isinstance(cypher_file_or_statements, list):
            statements = cypher_file_or_statements
        else:
            statements = [cypher_file_or_statements]
    
    analyzer = BusinessJourneyAnalyzer(statements)
    return analyzer.get_business_context()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python business_journey_analyzer.py <cypher_statements_file>")
        print("       python business_journey_analyzer.py <repo_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Try to run cartographer and analyze in one go
    if input_path.endswith('.py') or input_path == '.':
        print("Analyzing repository...", file=sys.stderr)
        import subprocess
        result = subprocess.run(
            ['python3', 'agents/cartographer_agent.py', input_path],
            capture_output=True,
            text=True
        )
        statements = [line.strip() for line in result.stdout.split('\n') if line.strip() and 'MERGE' in line]
        
        analyzer = BusinessJourneyAnalyzer(statements)
        print(analyzer.get_business_context())
    else:
        # Read from file
        with open(input_path, 'r') as f:
            statements = [line.strip() for line in f.readlines() if 'MERGE' in line]
        
        analyzer = BusinessJourneyAnalyzer(statements)
        print(analyzer.get_business_context())
