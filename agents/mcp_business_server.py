"""
MCP Server for Business Rules & Customer Journey Analysis

This MCP server exposes cartographer insights as tools that AI can use to understand
platform architecture, customer journeys, and business rules.

Tools Available:
- analyze_customer_journey: Get the complete customer journey through platform
- get_business_entities: List all business entities and their properties
- get_integration_points: Find all external system integrations
- get_business_rules: Retrieve business constraints and validation rules
- get_platform_processes: List all business processes
- explain_journey_step: Explain what happens at a specific journey step
"""

from typing import Any
import json
import sys
from pathlib import Path

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent))

from business_rules_extractor import BusinessRulesExtractor
from business_journey_analyzer import BusinessJourneyAnalyzer
import cartographer_agent


class BusinessRulesMCPServer:
    """MCP Server for business rules and journey analysis."""
    
    def __init__(self, repository_path: str):
        """Initialize the server with a repository to analyze."""
        self.repo_path = repository_path
        self.cypher_statements = []
        self.analyzer = None
        self._analyze_repository()
    
    def _analyze_repository(self):
        """Analyze the repository and build the business graph."""
        print(f"Analyzing repository: {self.repo_path}", file=sys.stderr)
        self.cypher_statements = cartographer_agent.cartographer_agent(
            self.repo_path,
            file_ext='.py,.java',
            max_workers=8,
            use_business_rules=True
        )
        self.analyzer = BusinessJourneyAnalyzer(self.cypher_statements)
        print(f"Analyzed {len(self.cypher_statements)} insights", file=sys.stderr)
    
    def get_tools(self) -> list:
        """Return available tools for the MCP server."""
        return [
            {
                "name": "analyze_customer_journey",
                "description": "Get the complete customer journey through the platform with all steps",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_business_entities",
                "description": "List all business entities (Customer, Order, Product, etc.) and their properties",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "description": "Filter by entity type (optional)"
                        }
                    }
                }
            },
            {
                "name": "get_integration_points",
                "description": "Find all external system integrations (payment gateways, email, APIs, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_business_rules",
                "description": "Retrieve business constraints, validations, and threshold rules",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "rule_type": {
                            "type": "string",
                            "description": "Filter by rule type: VALIDATION, CONSTRAINT, THRESHOLD (optional)"
                        }
                    }
                }
            },
            {
                "name": "get_platform_processes",
                "description": "List all business processes and workflows",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "explain_step",
                "description": "Explain what happens at a specific customer journey step",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "Journey step name (e.g., CHECKOUT, NOTIFY, SHIP)"
                        }
                    },
                    "required": ["step"]
                }
            },
            {
                "name": "get_platform_overview",
                "description": "Get a comprehensive overview of the entire platform's business architecture",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "trace_data_flow",
                "description": "Trace how data flows through a specific journey step or process",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_step": {
                            "type": "string",
                            "description": "Starting journey step"
                        },
                        "end_step": {
                            "type": "string",
                            "description": "Ending journey step (optional)"
                        }
                    },
                    "required": ["start_step"]
                }
            }
        ]
    
    def analyze_customer_journey(self) -> dict:
        """Get the complete customer journey."""
        journey = self.analyzer.get_customer_journey()
        return {
            "journey_path": journey['journey_path'],
            "steps": journey['steps'],
            "description": f"The customer journey has {journey['total_steps']} main steps: {' → '.join(journey['steps'])}"
        }
    
    def get_business_entities(self, entity_type: str = None) -> dict:
        """Get business entities."""
        entities = self.analyzer.get_business_entities()
        
        if entity_type:
            filtered = {entity_type: entities['entities_by_type'].get(entity_type, [])}
            return {
                "entities": filtered,
                "total": len(filtered.get(entity_type, []))
            }
        
        return entities
    
    def get_integration_points(self) -> dict:
        """Get external integrations."""
        integrations = self.analyzer.get_integrations()
        return {
            "integrations": integrations['integrations'],
            "total_systems": integrations['integration_count'],
            "by_type": integrations['integration_types'],
            "description": f"Platform integrates with {integrations['integration_count']} external systems"
        }
    
    def get_business_rules(self, rule_type: str = None) -> dict:
        """Get business rules."""
        rules = self.analyzer.get_business_rules_summary()
        
        if rule_type:
            count = rules['rule_types'].get(rule_type, 0)
            return {
                "rule_type": rule_type,
                "count": count,
                "description": f"Found {count} {rule_type} rules"
            }
        
        return {
            "total_rules": rules['rule_count'],
            "by_type": rules['rule_types'],
            "description": f"Platform enforces {rules['rule_count']} business rules"
        }
    
    def get_platform_processes(self) -> dict:
        """Get business processes."""
        processes = self.analyzer.get_business_processes()
        return {
            "processes": processes['processes'],
            "total": processes['process_count'],
            "description": f"Platform has {processes['process_count']} named business processes"
        }
    
    def explain_step(self, step: str) -> dict:
        """Explain a journey step."""
        journey = self.analyze_customer_journey()
        
        if step not in journey['steps']:
            return {
                "error": f"Step '{step}' not found in journey",
                "available_steps": journey['steps']
            }
        
        step_index = journey['steps'].index(step)
        
        # Provide business context for each step
        step_context = {
            "AUTHENTICATE": "User logs in to their account with credentials",
            "BROWSE": "Customer explores products, categories, searches for items",
            "SELECT_PRODUCT": "Customer adds products to cart or wishlist",
            "CHECKOUT": "Customer reviews order, applies promotions, enters shipping",
            "NOTIFY": "System sends confirmation emails, SMS, or notifications",
            "UPDATE_STATUS": "Order status changes, triggers downstream processes",
            "SHIP": "Inventory picked, package prepared, shipment sent to carrier",
            "DELIVER": "Package delivered to customer, delivery confirmed",
            "CANCEL": "Order or return initiated, refund processed"
        }
        
        return {
            "step": step,
            "sequence": step_index + 1,
            "description": step_context.get(step, "Business process step"),
            "previous_step": journey['steps'][step_index - 1] if step_index > 0 else None,
            "next_step": journey['steps'][step_index + 1] if step_index < len(journey['steps']) - 1 else None
        }
    
    def get_platform_overview(self) -> dict:
        """Get comprehensive platform overview."""
        return {
            "journey": self.analyze_customer_journey(),
            "entities": self.get_business_entities(),
            "integrations": self.get_integration_points(),
            "rules": self.get_business_rules(),
            "processes": self.get_platform_processes(),
            "business_context": self.analyzer.get_business_context()
        }
    
    def trace_data_flow(self, start_step: str, end_step: str = None) -> dict:
        """Trace data flow through journey steps."""
        journey = self.analyze_customer_journey()
        
        if start_step not in journey['steps']:
            return {"error": f"Start step '{start_step}' not found"}
        
        start_idx = journey['steps'].index(start_step)
        end_idx = len(journey['steps'])
        
        if end_step:
            if end_step not in journey['steps']:
                return {"error": f"End step '{end_step}' not found"}
            end_idx = journey['steps'].index(end_step) + 1
        
        flow_steps = journey['steps'][start_idx:end_idx]
        
        return {
            "flow": " → ".join(flow_steps),
            "steps": flow_steps,
            "step_count": len(flow_steps),
            "description": f"Data flows through {len(flow_steps)} steps starting from {start_step}"
        }
    
    def handle_tool_call(self, tool_name: str, tool_input: dict = None) -> dict:
        """Handle tool calls from MCP client."""
        tool_input = tool_input or {}
        
        if tool_name == "analyze_customer_journey":
            return self.analyze_customer_journey()
        elif tool_name == "get_business_entities":
            return self.get_business_entities(tool_input.get("entity_type"))
        elif tool_name == "get_integration_points":
            return self.get_integration_points()
        elif tool_name == "get_business_rules":
            return self.get_business_rules(tool_input.get("rule_type"))
        elif tool_name == "get_platform_processes":
            return self.get_platform_processes()
        elif tool_name == "explain_step":
            return self.explain_step(tool_input.get("step", ""))
        elif tool_name == "get_platform_overview":
            return self.get_platform_overview()
        elif tool_name == "trace_data_flow":
            return self.trace_data_flow(
                tool_input.get("start_step", ""),
                tool_input.get("end_step")
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}


def print_example_ai_prompt():
    """Print an example of how AI would use this."""
    prompt = """
# Example: AI Understanding Platform via Business Rules MCP

## Step 1: AI calls analyze_customer_journey()
{
  "journey_path": "AUTHENTICATE → BROWSE → SELECT_PRODUCT → CHECKOUT → NOTIFY → UPDATE_STATUS → SHIP → DELIVER",
  "steps": ["AUTHENTICATE", "BROWSE", "SELECT_PRODUCT", "CHECKOUT", "NOTIFY", "UPDATE_STATUS", "SHIP", "DELIVER"],
  "description": "The customer journey has 8 main steps..."
}

## Step 2: AI calls get_business_entities()
{
  "entities_by_type": {
    "customer": ["Customer", "Profile"],
    "order": ["Order", "Cart"],
    "product": ["Product", "Inventory"]
  },
  "total_entity_types": 3
}

## Step 3: AI calls get_integration_points()
{
  "integrations": ["stripe", "email", "kafka"],
  "by_type": {
    "payments": ["stripe"],
    "communications": ["email"]
  }
}

## Step 4: AI calls get_business_rules()
{
  "total_rules": 246,
  "by_type": {
    "VALIDATION": 200,
    "CONSTRAINT": 35,
    "THRESHOLD": 11
  }
}

---

With this information, AI now understands:
✓ Complete customer journey
✓ What business entities exist and how they relate
✓ External dependencies (payments, email, etc.)
✓ Business constraints and rules
✓ All without reading a single line of code!
    """
    print(prompt)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mcp_business_server.py <repo_path>", file=sys.stderr)
        print_example_ai_prompt()
        sys.exit(1)
    
    repo_path = sys.argv[1]
    server = BusinessRulesMCPServer(repo_path)
    
    print("Available Tools:", file=sys.stderr)
    for tool in server.get_tools():
        print(f"  - {tool['name']}", file=sys.stderr)
    
    print("\n--- Platform Overview ---\n")
    overview = server.get_platform_overview()
    print(json.dumps(overview, indent=2))
