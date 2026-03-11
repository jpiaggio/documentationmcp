#!/usr/bin/env python3
"""
Analysis script for Spring Framework using Unified LLM Query Interface
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "agents"))

from unified_llm_query_interface import UnifiedLLMQueryInterface

def analyze_spring_framework():
    """Analyze the Spring Framework repository."""
    
    print("\n" + "="*70)
    print("  SPRING FRAMEWORK ANALYSIS")
    print("="*70)
    
    repo_path = "/Users/juani/github-projects/spring-framework/spring-framework"
    
    print(f"\n📂 Repository: {repo_path}")
    print("🔄 Initializing Unified LLM Query Interface...")
    
    try:
        interface = UnifiedLLMQueryInterface(repo_path)
        print("✅ Interface initialized\n")
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return None
    
    results = {}
    
    # 1. List Modules
    print("1️⃣  LISTING ALL MODULES...")
    try:
        modules = interface.list_modules()
        results['modules'] = modules.to_dict()
        print(f"   ✓ Query Success: {modules.success}")
        print(f"   ✓ Modules Found: {modules.metadata.get('count', 0)}")
        if modules.results:
            print(f"   ✓ Sample Data Available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Find Specific Functions
    print("\n2️⃣  SEARCHING FOR FUNCTIONS...")
    search_terms = ["process", "handle", "execute", "initialize"]
    for term in search_terms:
        try:
            func = interface.find_function(term)
            if func.success:
                print(f"   ✓ '{term}': Found {len(func.results)} results")
        except Exception as e:
            print(f"   ✗ '{term}': Error - {e}")
    
    # 3. Get Circular Dependencies
    print("\n3️⃣  DETECTING CIRCULAR DEPENDENCIES...")
    try:
        cycles = interface.find_circular_dependencies()
        results['cycles'] = cycles.to_dict()
        cycle_count = cycles.metadata.get('cycle_count', 0)
        severity = cycles.metadata.get('severity', 'unknown')
        print(f"   ✓ Cycles Found: {cycle_count}")
        print(f"   ✓ Severity Level: {severity}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 4. Get Business Rules
    print("\n4️⃣  EXTRACTING BUSINESS RULES...")
    try:
        rules = interface.get_business_rules()
        results['rules'] = rules.to_dict()
        rule_count = rules.metadata.get('count', 0)
        print(f"   ✓ Rules Found: {rule_count}")
        if rules.results and rule_count > 0:
            print(f"   ✓ Sample Rules: {len(rules.results)} available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 5. Get Business Entities
    print("\n5️⃣  IDENTIFYING BUSINESS ENTITIES...")
    try:
        entities = interface.get_business_entities()
        results['entities'] = entities.to_dict()
        entity_count = entities.metadata.get('count', 0)
        print(f"   ✓ Entities Found: {entity_count}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 6. Trace Data Flow
    print("\n6️⃣  TRACING DATA DEPENDENCIES...")
    try:
        flow = interface.trace_data_flow("Request", "Response")
        results['data_flow'] = flow.to_dict()
        path_count = flow.metadata.get('path_count', 0)
        print(f"   ✓ Paths Found: {path_count}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 7. Natural Language Queries
    print("\n7️⃣  NATURAL LANGUAGE QUERIES...")
    queries = [
        "What are the main modules?",
        "How are dependencies organized?",
        "What are the business rules?"
    ]
    
    for query_text in queries:
        try:
            query_result = interface.query(query_text)
            print(f"   ✓ Query: '{query_text[:40]}...' -> Success: {query_result.success}")
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
    
    print("\n" + "="*70)
    print("  ANALYSIS COMPLETE")
    print("="*70)
    
    return results

if __name__ == "__main__":
    results = analyze_spring_framework()
    if results:
        print("\n✅ Analysis data saved and ready for report generation")
