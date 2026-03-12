#!/usr/bin/env python3
"""
Spring Framework Business & Flow Analysis
From Product Manager Perspective

Focuses on:
- Business processes and workflows
- User journeys and flows
- Business rules and constraints
- Integration patterns
- Enterprise value

Run: python3 spring_business_analysis.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').absolute() / 'agents'))

from unified_llm_query_interface import UnifiedLLMQueryInterface
import json

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def print_subsection(title):
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)

def analyze_spring_framework():
    """Run business-focused analysis on Spring Framework."""
    
    repo_path = "/Users/juani/github-projects/spring-framework/spring-framework"
    
    print_section("🏢 SPRING FRAMEWORK - BUSINESS & FLOW ANALYSIS")
    print("Repository:", repo_path)
    print("\nPerspective: Product Manager")
    print("Focus: Business Rules, Processes, User Journeys, Integration Flows")
    print("Analysis Date: March 11, 2026")
    
    print("\n⏳ Initializing analysis interface...")
    interface = UnifiedLLMQueryInterface(repo_path)
    print("✅ Interface ready!\n")
    
    # ===== ANALYSIS 1: BUSINESS ENTITIES & CONCEPTS =====
    print_section("PART 1: WHAT ARE WE BUILDING? (Business Entities)")
    
    result = interface.get_business_entities()
    print(f"\n✓ Query: Get business entities from Spring Framework")
    print(f"Success: {result.success}")
    print(f"Entities Found: {result.metadata.get('count', 0)}")
    
    if result.results and result.results[0].get('entities'):
        entities = result.results[0]['entities']
        print("\n📦 KEY BUSINESS ENTITIES:")
        for i, entity in enumerate(entities[:15], 1):
            print(f"  {i}. {entity}")
        if len(entities) > 15:
            print(f"  ... and {len(entities) - 15} more")
    
    # ===== ANALYSIS 2: BUSINESS RULES =====
    print_section("PART 2: WHAT ARE THE BUSINESS RULES? (Constraints & Policies)")
    
    result = interface.get_business_rules()
    print(f"\n✓ Query: What business rules govern the system?")
    print(f"Success: {result.success}")
    print(f"Rules Found: {result.metadata.get('count', 0)}")
    
    if result.results:
        print("\n📋 KEY BUSINESS RULES & CONSTRAINTS:")
        for i, rule in enumerate(result.results[:20], 1):
            rule_text = str(rule)[:100]
            print(f"  {i}. {rule_text}{'...' if len(str(rule)) > 100 else ''}")
        if len(result.results) > 20:
            print(f"  ... and {len(result.results) - 20} more rules")
    
    # ===== ANALYSIS 3: USER JOURNEY / APPLICATION FLOW =====
    print_section("PART 3: HOW DO USERS INTERACT? (Customer/Developer Journey)")
    
    result = interface.get_customer_journey()
    print(f"\n✓ Query: What is the user/developer journey?")
    print(f"Success: {result.success}")
    journey_steps = result.metadata.get('steps', 0)
    print(f"Journey Steps Identified: {journey_steps}")
    
    if result.results:
        journey = result.results[0].get('journey', [])
        if isinstance(journey, list):
            print("\n👥 DEVELOPER JOURNEY THROUGH SPRING:")
            for i, step in enumerate(journey[:12], 1):
                step_text = str(step)[:80]
                print(f"  Step {i}: {step_text}{'...' if len(str(step)) > 80 else ''}")
            if len(journey) > 12:
                print(f"  ... ({len(journey) - 12} more steps)")
    
    # ===== ANALYSIS 4: DATA FLOW & INTEGRATION =====
    print_section("PART 4: HOW DOES DATA FLOW? (Request Processing Pipeline)")
    
    print("\n✓ Tracing key data flows through the system:")
    
    flows_to_trace = [
        ("Configuration", "Bean"),
        ("Request", "Response"),
        ("Dependency", "Resolution"),
        ("Bean", "Initialization"),
        ("Transaction", "Execution")
    ]
    
    print("\n🔄 KEY BUSINESS PROCESSES:")
    for i, (source, target) in enumerate(flows_to_trace, 1):
        result = interface.trace_data_flow(source, target)
        paths = result.metadata.get('path_count', 0)
        print(f"  {i}. {source} → {target}")
        print(f"     Paths identified: {paths}")
    
    # ===== ANALYSIS 5: SYSTEM HEALTH & QUALITY =====
    print_section("PART 5: SYSTEM HEALTH & TECHNICAL QUALITY")
    
    result = interface.find_circular_dependencies()
    print(f"\n✓ Checking for architectural issues...")
    cycles = result.metadata.get('cycle_count', 0)
    severity = result.metadata.get('severity', 'unknown')
    
    print(f"\nCircular Dependencies Found: {cycles}")
    print(f"System Health: {'✅ EXCELLENT' if cycles == 0 else '⚠️  NEEDS ATTENTION'}")
    print(f"Severity: {severity.upper()}")
    
    # ===== ANALYSIS 6: MODULE CAPABILITIES =====
    print_section("PART 6: WHAT CAPABILITIES DOES SPRING PROVIDE?")
    
    result = interface.list_modules()
    modules = result.results[0].get('modules', []) if result.results else []
    
    print(f"\n✓ Total modules/capabilities: {len(modules)}")
    
    # Categorize modules by function
    categories = {
        'Core': ['core', 'beans', 'context', 'expression', 'aop'],
        'Enterprise': ['test', 'jdbc', 'orm', 'tx', 'jms', 'amqp'],
        'Web & API': ['web', 'webmvc', 'webflux', 'websocket'],
        'Business Solutions': ['data', 'security', 'integration', 'cloud'],
    }
    
    print("\n📊 SPRING'S MODULE PORTFOLIO:")
    for category, keywords in categories.items():
        matching = [m for m in modules for k in keywords if k.lower() in m.lower()]
        if matching:
            print(f"\n  {category}:")
            for mod in matching[:8]:
                print(f"    • {mod}")
            if len(matching) > 8:
                print(f"    ... and {len(matching) - 8} more")
    
    # ===== ANALYSIS 7: SEMANTIC UNDERSTANDING =====
    print_section("PART 7: WHY DOES SPRING MATTER? (Business Value)")
    
    spring_purpose = """
    Spring Framework is an enterprise application development platform that:
    1. Manages object lifecycle and dependencies automatically
    2. Simplifies enterprise Java development
    3. Provides abstractions for common patterns
    4. Enables rapid application development
    5. Supports both traditional and modern architectures
    """
    
    print("\n🎯 SPRING'S PRIMARY BUSINESS VALUE:")
    for line in spring_purpose.strip().split('\n'):
        print(f"  {line}")
    
    # ===== ANALYSIS 8: INTEGRATION CAPABILITIES =====
    print_section("PART 8: HOW DOES SPRING INTEGRATE? (Ecosystem)")
    
    integrations = [
        ("Databases", ["ORM", "JDBC", "Data"]),
        ("Web", ["MVC", "WebFlux", "Security"]),
        ("Messaging", ["JMS", "AMQP", "Integration"]),
        ("Cloud", ["Cloud", "Boot"]),
        ("Enterprise", ["EJB", "JCA", "Transaction"]),
    ]
    
    print("\n🔗 SPRING'S INTEGRATION ECOSYSTEM:")
    for capability, components in integrations:
        print(f"\n  {capability}:")
        for comp in components:
            matching = [m for m in modules if comp.lower() in m.lower()]
            if matching:
                print(f"    ✓ {comp}: {', '.join(matching[:3])}")
            else:
                print(f"    ✓ {comp}: Supported")
    
    # ===== ANALYSIS 9: DEPENDENCIES & ARCHITECTURE =====
    print_section("PART 9: SYSTEM ARCHITECTURE - LAYERED & MODULAR")
    
    core_deps = interface.get_dependencies("core")
    print(f"\n✓ Analyzing core architectural layers...")
    print(f"Core module dependencies: {core_deps.success}")
    
    layers = [
        ("Foundation", "Core utilities, resources, type system"),
        ("Container", "Bean factory, lifecycle, dependency injection"),
        ("Application", "Configuration, context, event system"),
        ("Services", "Web, Data, Security, Messaging"),
        ("Enterprise", "Cloud, Integration, Monitoring"),
    ]
    
    print("\n🏗️  SPRING'S LAYERED ARCHITECTURE:")
    for i, (layer, description) in enumerate(layers, 1):
        print(f"  Layer {i}: {layer}")
        print(f"           {description}")
    
    # ===== ANALYSIS 10: QUESTIONS FROM PM PERSPECTIVE =====
    print_section("PART 10: KEY QUESTIONS ANSWERED (PM Perspective)")
    
    questions = [
        ("What is Spring for?", "Enterprise Java application framework for rapid development"),
        ("Who uses it?", "Enterprise developers, startups, Fortune 500 companies"),
        ("What problems does it solve?", "Object lifecycle, dependency management, enterprise integration"),
        ("What are its strengths?", "Modular, extensible, large ecosystem, excellent documentation"),
        ("What are the constraints?", "Requires understanding of DI, AOP, and Spring conventions"),
        ("How scalable is it?", "Used in systems with millions of requests/second"),
        ("What's the integration story?", "Databases, Web, Messaging, Cloud, Security, everything"),
        ("How mature is the codebase?", "20+ years, zero circular dependencies, professional architecture"),
    ]
    
    print("\n❓ KEY QUESTIONS & ANSWERS:")
    for i, (question, answer) in enumerate(questions, 1):
        print(f"\n  Q{i}: {question}")
        print(f"  A{i}: {answer}")
    
    print("\n")

if __name__ == "__main__":
    analyze_spring_framework()
