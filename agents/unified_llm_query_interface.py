"""
Unified LLM Query Interface

Combines all three query methods into a single, cohesive API that LLMs can use:
1. MCP Tools (Cartographer, Business Rules, Neo4j)
2. Direct LLM Analysis (Semantic understanding)
3. Graph Database Queries (Cypher)

This interface provides:
- Natural language query processing
- Structured query execution
- Result aggregation and ranking
- Smart caching for performance
"""

import json
import sys
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent))

from incremental_indexer import IncrementalIndexer
from context_pruner import ContextPruner
from business_rules_extractor import BusinessRulesExtractor
from business_journey_analyzer import BusinessJourneyAnalyzer
from semantic_analyzer import SemanticAnalyzer
from unified_analyzer import UnifiedCodeAnalyzer
import cartographer_agent


class QueryType(Enum):
    """Types of queries the interface can handle."""
    STRUCTURAL = "structural"      # Module, function, class queries
    BUSINESS_LOGIC = "business"    # Business rules, journeys, entities
    SEMANTIC = "semantic"          # Code meaning, risks, impact
    GRAPH = "graph"                # Graph relationships, paths
    NATURAL_LANGUAGE = "natural"   # Free-form questions


@dataclass
class QueryResult:
    """Standardized result format for all query types."""
    query: str
    query_type: QueryType
    success: bool
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    raw_response: Optional[str] = None
    confidence: float = 1.0
    cache_hit: bool = False
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            **asdict(self),
            'query_type': self.query_type.value
        }


class UnifiedLLMQueryInterface:
    """
    Unified interface for all LLM query operations.
    
    Usage:
        interface = UnifiedLLMQueryInterface("/path/to/repo")
        
        # Structural queries
        result = interface.list_modules()
        result = interface.find_function("process_payment")
        result = interface.get_dependencies("payment_module")
        
        # Business logic queries
        result = interface.get_business_rules()
        result = interface.get_customer_journey()
        
        # Semantic queries
        result = interface.analyze_code_semantics("function_code")
        result = interface.ask_question("What are the risks in this payment handler?")
        
        # Graph queries
        result = interface.trace_data_flow("Customer", "Payment")
        result = interface.find_circular_dependencies()
        
        # Natural language (combines all methods)
        result = interface.query("How does the payment process work?")
    """
    
    def __init__(self, repository_path: str, llm_provider: str = "claude"):
        """Initialize the unified interface."""
        self.repo_path = repository_path
        self.llm_provider = llm_provider
        
        # Initialize all components
        self.indexer = IncrementalIndexer(repository_path)
        self.context_pruner = ContextPruner(repository_path)
        self.business_extractor = BusinessRulesExtractor()
        self.semantic_analyzer = SemanticAnalyzer()
        self.unified_analyzer = UnifiedCodeAnalyzer()
        
        # Cache for expensive operations
        self.cache = {}
        self.cypher_statements = []
        self.journey_analyzer = None
        
        # Analyze repository on init
        self._initialize_analysis()
    
    def _initialize_analysis(self):
        """Perform initial repository analysis."""
        print(f"Initializing analysis for {self.repo_path}...", file=sys.stderr)
        
        # Run cartographer to get Cypher statements
        self.cypher_statements = cartographer_agent.cartographer_agent(
            self.repo_path,
            file_ext='.py,.java',
            max_workers=8,
            use_business_rules=True
        )
        
        # Initialize business journey analyzer
        self.journey_analyzer = BusinessJourneyAnalyzer(self.cypher_statements)
        
        print(f"✓ Analyzed {len(self.cypher_statements)} insights", file=sys.stderr)
    
    # ============================================================
    # STRUCTURAL QUERIES (Code navigation)
    # ============================================================
    
    def list_modules(self) -> QueryResult:
        """List all modules in the repository."""
        cache_key = "list_modules"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Extract from cartographer results
            modules = self._extract_modules_from_cypher()
            
            result = QueryResult(
                query="List all modules",
                query_type=QueryType.STRUCTURAL,
                success=True,
                results=[{"modules": modules}],
                metadata={"count": len(modules)}
            )
            
            self.cache[cache_key] = result
            return result
        except Exception as e:
            return QueryResult(
                query="List all modules",
                query_type=QueryType.STRUCTURAL,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    def find_function(self, function_name: str) -> QueryResult:
        """Find a function by name."""
        try:
            # Search through analyzed code
            results = []
            for cypher in self.cypher_statements:
                if function_name.lower() in cypher.lower() and "FUNCTION" in cypher:
                    results.append({
                        "function": function_name,
                        "statement": cypher
                    })
            
            return QueryResult(
                query=f"Find function: {function_name}",
                query_type=QueryType.STRUCTURAL,
                success=len(results) > 0,
                results=results,
                metadata={"found": len(results) > 0}
            )
        except Exception as e:
            return QueryResult(
                query=f"Find function: {function_name}",
                query_type=QueryType.STRUCTURAL,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    def get_dependencies(self, module_name: str) -> QueryResult:
        """Get dependencies of a module."""
        try:
            deps = self._extract_dependencies(module_name)
            
            return QueryResult(
                query=f"Get dependencies: {module_name}",
                query_type=QueryType.STRUCTURAL,
                success=True,
                results=[{"module": module_name, "dependencies": deps}],
                metadata={"count": len(deps)}
            )
        except Exception as e:
            return QueryResult(
                query=f"Get dependencies: {module_name}",
                query_type=QueryType.STRUCTURAL,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    # ============================================================
    # BUSINESS LOGIC QUERIES
    # ============================================================
    
    def get_business_rules(self, rule_type: Optional[str] = None) -> QueryResult:
        """Get business rules and constraints."""
        cache_key = f"business_rules_{rule_type or 'all'}"
        if cache_key in self.cache:
            result = self.cache[cache_key]
            result.cache_hit = True
            return result
        
        try:
            rules = []
            for cypher in self.cypher_statements:
                if "RULE" in cypher or "CONSTRAINT" in cypher:
                    if rule_type is None or rule_type.upper() in cypher:
                        rules.append({"rule": cypher})
            
            result = QueryResult(
                query=f"Get business rules{f' ({rule_type})' if rule_type else ''}",
                query_type=QueryType.BUSINESS_LOGIC,
                success=len(rules) > 0,
                results=rules,
                metadata={"count": len(rules), "filter": rule_type}
            )
            
            self.cache[cache_key] = result
            return result
        except Exception as e:
            return QueryResult(
                query="Get business rules",
                query_type=QueryType.BUSINESS_LOGIC,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    def get_customer_journey(self) -> QueryResult:
        """Get the complete customer journey."""
        cache_key = "customer_journey"
        if cache_key in self.cache:
            result = self.cache[cache_key]
            result.cache_hit = True
            return result
        
        try:
            if self.journey_analyzer:
                journey = self.journey_analyzer.analyze_journey()
                
                result = QueryResult(
                    query="Get customer journey",
                    query_type=QueryType.BUSINESS_LOGIC,
                    success=True,
                    results=[{"journey": journey}],
                    metadata={"steps": len(journey) if isinstance(journey, list) else 1}
                )
            else:
                result = QueryResult(
                    query="Get customer journey",
                    query_type=QueryType.BUSINESS_LOGIC,
                    success=False,
                    results=[],
                    metadata={"error": "Journey analyzer not initialized"}
                )
            
            self.cache[cache_key] = result
            return result
        except Exception as e:
            return QueryResult(
                query="Get customer journey",
                query_type=QueryType.BUSINESS_LOGIC,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    def get_business_entities(self, entity_type: Optional[str] = None) -> QueryResult:
        """Get all business entities."""
        try:
            entities = []
            for cypher in self.cypher_statements:
                if "ENTITY" in cypher:
                    if entity_type is None or entity_type.upper() in cypher:
                        entities.append({"entity": cypher})
            
            return QueryResult(
                query=f"Get business entities{f' ({entity_type})' if entity_type else ''}",
                query_type=QueryType.BUSINESS_LOGIC,
                success=len(entities) > 0,
                results=entities,
                metadata={"count": len(entities)}
            )
        except Exception as e:
            return QueryResult(
                query="Get business entities",
                query_type=QueryType.BUSINESS_LOGIC,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    # ============================================================
    # SEMANTIC QUERIES (Code understanding)
    # ============================================================
    
    def analyze_code_semantics(self, code: str, filename: Optional[str] = None) -> QueryResult:
        """Analyze code semantically to understand its purpose."""
        try:
            analysis = self.unified_analyzer.analyze_code_deeply(code, filename or "code")
            
            return QueryResult(
                query="Analyze code semantics",
                query_type=QueryType.SEMANTIC,
                success=True,
                results=[analysis],
                metadata={"filename": filename}
            )
        except Exception as e:
            return QueryResult(
                query="Analyze code semantics",
                query_type=QueryType.SEMANTIC,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    def ask_question(self, question: str, code: Optional[str] = None) -> QueryResult:
        """Ask a question about code or the system."""
        try:
            if code:
                answer = self.unified_analyzer.ask_question_about_code(code, question)
            else:
                answer = f"Question about system: {question}"
            
            return QueryResult(
                query=question,
                query_type=QueryType.SEMANTIC,
                success=True,
                results=[{"answer": answer}],
                metadata={"has_code": code is not None}
            )
        except Exception as e:
            return QueryResult(
                query=question,
                query_type=QueryType.SEMANTIC,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    # ============================================================
    # GRAPH QUERIES (Relationship exploration)
    # ============================================================
    
    def trace_data_flow(self, source: str, target: str) -> QueryResult:
        """Trace data flow between two entities."""
        try:
            paths = self._find_paths_in_cypher(source, target)
            
            return QueryResult(
                query=f"Trace data flow: {source} -> {target}",
                query_type=QueryType.GRAPH,
                success=len(paths) > 0,
                results=[{"paths": paths}],
                metadata={"path_count": len(paths)}
            )
        except Exception as e:
            return QueryResult(
                query=f"Trace data flow: {source} -> {target}",
                query_type=QueryType.GRAPH,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    def find_circular_dependencies(self) -> QueryResult:
        """Find circular dependencies in the code."""
        try:
            cycles = self._extract_cycles_from_cypher()
            
            return QueryResult(
                query="Find circular dependencies",
                query_type=QueryType.GRAPH,
                success=True,
                results=[{"cycles": cycles}],
                metadata={"cycle_count": len(cycles), "severity": "high" if cycles else "ok"}
            )
        except Exception as e:
            return QueryResult(
                query="Find circular dependencies",
                query_type=QueryType.GRAPH,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    # ============================================================
    # NATURAL LANGUAGE QUERY (Combines all methods)
    # ============================================================
    
    def query(self, natural_language_query: str) -> QueryResult:
        """
        Execute a natural language query that intelligently routes to the right method.
        
        Examples:
        - "List all modules" -> list_modules()
        - "What are the business rules?" -> get_business_rules()
        - "How does payment flow work?" -> get_customer_journey() + trace_data_flow()
        - "Find the process_payment function" -> find_function()
        - "What are the risks in the payment handler?" -> analyze_code_semantics()
        """
        query_lower = natural_language_query.lower()
        results = []
        
        try:
            # Route based on keywords
            if any(kw in query_lower for kw in ["list", "all modules", "modules"]):
                results.append(self.list_modules())
            
            if any(kw in query_lower for kw in ["business rule", "constraint", "validation"]):
                results.append(self.get_business_rules())
            
            if any(kw in query_lower for kw in ["journey", "flow", "process", "step"]):
                results.append(self.get_customer_journey())
            
            if any(kw in query_lower for kw in ["entity", "object", "entities"]):
                results.append(self.get_business_entities())
            
            if any(kw in query_lower for kw in ["risk", "danger", "problem", "issue"]):
                # This is semantic - need code or context
                results.append(QueryResult(
                    query=natural_language_query,
                    query_type=QueryType.SEMANTIC,
                    success=False,
                    results=[],
                    metadata={"note": "Provide code context for semantic analysis"}
                ))
            
            if any(kw in query_lower for kw in ["circular", "cycle", "dependency"]):
                results.append(self.find_circular_dependencies())
            
            if any(kw in query_lower for kw in ["trace", "flow", "connected"]):
                # Need entities specified
                results.append(QueryResult(
                    query=natural_language_query,
                    query_type=QueryType.GRAPH,
                    success=False,
                    results=[],
                    metadata={"note": "Specify source and target for tracing"}
                ))
            
            # If no route matched, treat as semantic question
            if not results:
                results.append(self.ask_question(natural_language_query))
            
            # Aggregate results
            all_results = []
            for r in results:
                if r.success:
                    all_results.extend(r.results)
            
            return QueryResult(
                query=natural_language_query,
                query_type=QueryType.NATURAL_LANGUAGE,
                success=len(all_results) > 0,
                results=all_results,
                metadata={
                    "routes_executed": len(results),
                    "successful_routes": sum(1 for r in results if r.success)
                }
            )
        except Exception as e:
            return QueryResult(
                query=natural_language_query,
                query_type=QueryType.NATURAL_LANGUAGE,
                success=False,
                results=[],
                metadata={"error": str(e)}
            )
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _extract_modules_from_cypher(self) -> List[str]:
        """Extract module names from Cypher statements."""
        modules = set()
        for cypher in self.cypher_statements:
            # Simple extraction - can be enhanced
            if "Module" in cypher:
                # Extract module name from MATCH or CREATE patterns
                parts = cypher.split()
                for i, part in enumerate(parts):
                    if part == "Module" and i + 1 < len(parts):
                        modules.add(parts[i + 1])
        return list(modules)
    
    def _extract_dependencies(self, module_name: str) -> List[str]:
        """Extract dependencies for a module."""
        deps = set()
        for cypher in self.cypher_statements:
            if module_name in cypher and "->" in cypher:
                # Extract dependency relationships
                if "DEPENDS_ON" in cypher or "->" in cypher:
                    deps.add(cypher)
        return list(deps)
    
    def _find_paths_in_cypher(self, source: str, target: str) -> List[str]:
        """Find paths between two entities in Cypher."""
        paths = []
        for cypher in self.cypher_statements:
            if source in cypher and target in cypher:
                paths.append(cypher)
        return paths
    
    def _extract_cycles_from_cypher(self) -> List[str]:
        """Extract circular dependencies."""
        cycles = []
        for cypher in self.cypher_statements:
            if "CYCLE" in cypher or "CIRCULAR" in cypher:
                cycles.append(cypher)
        return cycles


# ============================================================
# MCP Server Integration
# ============================================================

def create_mcp_tools(interface: UnifiedLLMQueryInterface) -> List[Dict[str, Any]]:
    """Create MCP tool definitions for the unified interface."""
    return [
        {
            "name": "query",
            "description": "Execute a natural language query (automatically routes to best method)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Your question or query about the code/system"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "list_modules",
            "description": "List all modules in the repository",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "find_function",
            "description": "Find a function by name",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the function to find"
                    }
                },
                "required": ["function_name"]
            }
        },
        {
            "name": "get_dependencies",
            "description": "Get dependencies of a module",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "module_name": {
                        "type": "string",
                        "description": "Name of the module"
                    }
                },
                "required": ["module_name"]
            }
        },
        {
            "name": "get_business_rules",
            "description": "Get all business rules and constraints",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_type": {
                        "type": "string",
                        "description": "Optional filter by rule type"
                    }
                }
            }
        },
        {
            "name": "get_customer_journey",
            "description": "Get the complete customer journey through the system",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "get_business_entities",
            "description": "Get all business entities",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entity_type": {
                        "type": "string",
                        "description": "Optional filter by entity type"
                    }
                }
            }
        },
        {
            "name": "analyze_code_semantics",
            "description": "Analyze code semantically to understand its purpose",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code snippet to analyze"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional filename for context"
                    }
                },
                "required": ["code"]
            }
        },
        {
            "name": "ask_question",
            "description": "Ask a question about code or the system",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Your question"
                    },
                    "code": {
                        "type": "string",
                        "description": "Optional code context"
                    }
                },
                "required": ["question"]
            }
        },
        {
            "name": "trace_data_flow",
            "description": "Trace data flow between two entities",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source entity"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target entity"
                    }
                },
                "required": ["source", "target"]
            }
        },
        {
            "name": "find_circular_dependencies",
            "description": "Find circular dependencies in the code",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python3 unified_llm_query_interface.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    interface = UnifiedLLMQueryInterface(repo_path)
    
    # Example queries
    print("\n" + "="*60)
    print("UNIFIED LLM QUERY INTERFACE")
    print("="*60)
    
    print("\n1. List Modules:")
    result = interface.list_modules()
    print(json.dumps(result.to_dict(), indent=2))
    
    print("\n2. Natural Language Query:")
    result = interface.query("What are the business rules for orders?")
    print(json.dumps(result.to_dict(), indent=2))
    
    print("\n3. Find Circular Dependencies:")
    result = interface.find_circular_dependencies()
    print(json.dumps(result.to_dict(), indent=2))
