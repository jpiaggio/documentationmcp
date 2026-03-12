#!/usr/bin/env python3
"""
PiggyMetrics Architecture Analysis using Gemini LLM
Analyzes the microservices architecture loaded in Neo4j
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai package not installed. Install with: pip install google-generativeai")
    sys.exit(1)

try:
    from neo4j import GraphDatabase
except ImportError:
    print("neo4j package not installed. Install with: pip install neo4j")
    sys.exit(1)


class PiggyMetricsAnalyzer:
    def __init__(self, gemini_key: str = None, neo4j_uri: str = "bolt://localhost:7687",
                 username: str = "neo4j", password: str = "piggymetrics"):
        """Initialize Gemini and Neo4j connections."""
        self.gemini_key = gemini_key or os.getenv("GOOGLE_API_KEY")
        if not self.gemini_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=self.gemini_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        self.modules = self._load_modules_from_neo4j()
    
    def _load_modules_from_neo4j(self) -> dict:
        """Load module information from Neo4j."""
        modules = {}
        with self.neo4j_driver.session() as session:
            result = session.run("MATCH (m:Module) RETURN m.id, m.name, m.path ORDER BY m.id")
            for record in result:
                module_id = record["m.id"]
                modules[module_id] = {
                    "name": record["m.name"],
                    "path": record["m.path"]
                }
        return modules
    
    def analyze_architecture(self) -> str:
        """Get Gemini's analysis of PiggyMetrics architecture."""
        modules_info = "\n".join([
            f"  • {mid}: {info['name']}"
            for mid, info in self.modules.items()
        ])
        
        prompt = f"""
You are an expert microservices architect analyzing the PiggyMetrics project structure.

PiggyMetrics is a personal finance management system with the following microservices:
{modules_info}

Based on this Spring Boot microservices architecture, provide a comprehensive analysis covering:

1. **Architecture Overview**: What type of architecture is this and why?
2. **Service Responsibilities**: What does each microservice do based on its name and domain?
3. **Key Interactions**: How do these services likely interact with each other?
4. **Data Flow**: Describe the typical data flow for a financial transaction
5. **Design Patterns**: What Spring Cloud patterns are likely used here (Eureka, OAuth2, Config Server)?
6. **Scalability**: Which services would benefit from scaling horizontally?
7. **Resilience**: What failure points exist and how to handle them?
8. **Development Challenges**: What are the main challenges in developing this system?
9. **Improvement Opportunities**: What could be improved in the architecture?
10. **Technology Stack**: Based on the services, what technologies are likely used?

Provide detailed, technical insights suitable for developers and architects.
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def analyze_specific_service(self, service_name: str) -> str:
        """Get detailed analysis of a specific service."""
        if service_name not in self.modules:
            return f"Service '{service_name}' not found. Available services: {', '.join(self.modules.keys())}"
        
        prompt = f"""
You are analyzing the '{service_name}' microservice from the PiggyMetrics project.

Based on the service name and Spring Boot/Cloud context, provide:

1. **Primary Responsibility**: What does this service do?
2. **Key Features**: What features should it implement?
3. **Data Model**: What data entities does it likely manage?
4. **API Endpoints**: Likely REST API endpoints (as we saw in the README)
5. **Dependencies**: Which other services does it depend on?
6. **Security**: What OAuth2 scopes and authentication does it need?
7. **Common Operations**: What are typical use cases?
8. **Performance Considerations**: Any performance patterns to apply?
9. **Testing Strategy**: How to test this service properly?
10. **Failure Scenarios**: How should it handle failures from dependent services?

Be specific and technical in your analysis.
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_interaction_diagram(self) -> str:
        """Generate ASCII diagram of service interactions."""
        prompt = """
Based on a typical personal finance microservices application with these services:
- gateway: API Gateway (entry point)
- auth-service: OAuth2 authentication
- account-service: Account and transaction management
- statistics-service: Analytics and reporting
- notification-service: Email/notification delivery
- config: Centralized configuration (Spring Cloud Config)
- registry: Service discovery (Eureka)
- monitoring: Health checks and monitoring
- turbine-stream-service: Circuit breaker monitoring

Create a detailed ASCII diagram showing:
1. Client/User entry point
2. API Gateway routing
3. Service interactions and dependencies
4. Database per service pattern
5. Message queues if any
6. Monitoring and observability

Make it clear and easy to understand.
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def get_implementation_recommendations(self) -> str:
        """Get recommendations for implementing analysis tools."""
        prompt = """
A developer wants to analyze and monitor the PiggyMetrics microservices application 
(10 services including gateway, auth, account, statistics, notification, config, registry, monitoring, turbine-stream).

Provide specific recommendations for:

1. **Code Analysis Tools**: How to analyze 800+ Java modules across 10 services
2. **Dependency Analysis**: Tools to visualize service dependencies and detect circular dependencies
3. **MCP Integration**: How to build MCP tools for service analysis
4. **Neo4j Usage**: How to structure a Neo4j graph for this microservices application
5. **LLM Integration**: Best ways to use AI (Claude/Gemini) for code understanding
6. **Architecture Visualization**: Tools to visualize the current architecture
7. **Quality Metrics**: How to measure and track service health
8. **Documentation**: How to auto-generate architecture documentation
9. **Testing Strategy**: Distributed testing across services
10. **Deployment Strategy**: Recommendations for container orchestration

Be practical and include specific tools/libraries where applicable.
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def close(self):
        """Close Neo4j connection."""
        self.neo4j_driver.close()


def main():
    """Main entry point."""
    print("=" * 80)
    print("PiggyMetrics Architecture Analysis with Gemini")
    print("=" * 80)
    
    try:
        analyzer = PiggyMetricsAnalyzer()
        
        print(f"\n✓ Connected to Neo4j")
        print(f"✓ Loaded {len(analyzer.modules)} microservices")
        print(f"✓ Initialized Gemini API")
        
        # 1. Architecture analysis
        print("\n" + "=" * 80)
        print("1. ARCHITECTURE ANALYSIS")
        print("=" * 80)
        analysis = analyzer.analyze_architecture()
        print(analysis)
        
        # 2. Account service deep dive
        print("\n" + "=" * 80)
        print("2. ACCOUNT SERVICE ANALYSIS")
        print("=" * 80)
        account_analysis = analyzer.analyze_specific_service("account-service")
        print(account_analysis)
        
        # 3. Service interaction diagram
        print("\n" + "=" * 80)
        print("3. SERVICE INTERACTION DIAGRAM")
        print("=" * 80)
        diagram = analyzer.generate_interaction_diagram()
        print(diagram)
        
        # 4. Implementation recommendations
        print("\n" + "=" * 80)
        print("4. ANALYSIS & IMPLEMENTATION RECOMMENDATIONS")
        print("=" * 80)
        recommendations = analyzer.get_implementation_recommendations()
        print(recommendations)
        
        print("\n" + "=" * 80)
        print("Analysis Complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'analyzer' in locals():
            analyzer.close()


if __name__ == "__main__":
    main()
