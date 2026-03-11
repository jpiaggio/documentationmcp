#!/usr/bin/env python3
"""
Unified LLM Query Interface - Quick Start Examples

This script demonstrates all the ways to use the unified interface.
Run with: python3 unified_llm_quick_start.py /path/to/your/repo
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "agents"))

from unified_llm_query_interface import UnifiedLLMQueryInterface


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(result):
    """Print a query result nicely."""
    print(f"\n📊 Query Type: {result.query_type.value.upper()}")
    print(f"✓ Success: {result.success}")
    print(f"💾 Cached: {result.cache_hit}")
    print(f"📈 Confidence: {result.confidence:.0%}")
    
    if result.success and result.results:
        print(f"\n📋 Results ({len(result.results)} items):")
        for i, item in enumerate(result.results[:3], 1):  # Show first 3
            print(f"\n  {i}. {json.dumps(item, indent=5)}")
        if len(result.results) > 3:
            print(f"\n  ... and {len(result.results) - 3} more")
    else:
        print(f"\n⚠️  Error: {result.metadata.get('error', 'No results')}")
    
    print(f"\n📍 Metadata: {json.dumps(result.metadata, indent=2)}")


def example_1_natural_language(interface):
    """Example 1: Natural Language Queries"""
    print_header("EXAMPLE 1: Natural Language Queries")
    print("\nThe interface automatically routes natural language to the right method:")
    
    queries = [
        "List all modules",
        "What are the business rules?",
        "Show me the customer journey",
        "Find circular dependencies",
    ]
    
    for query in queries:
        print(f"\n> {query}")
        result = interface.query(query)
        print_result(result)
        input("Press Enter to continue...")


def example_2_structural_queries(interface):
    """Example 2: Structural Code Navigation"""
    print_header("EXAMPLE 2: Structural Code Navigation")
    print("\nQuery code structure: modules, functions, classes, dependencies")
    
    print("\n1️⃣  List all modules in repository:")
    result = interface.list_modules()
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n2️⃣  Find a specific function:")
    # Try to find a function (will depend on your repo)
    result = interface.find_function("process_payment")
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n3️⃣  Get dependencies of a module:")
    result = interface.get_dependencies("payment")
    print_result(result)
    input("Press Enter to continue...")


def example_3_business_logic(interface):
    """Example 3: Business Logic & Entities"""
    print_header("EXAMPLE 3: Business Logic & Entities")
    print("\nUnderstand what the system does from a business perspective:")
    
    print("\n1️⃣  Get all business rules:")
    result = interface.get_business_rules()
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n2️⃣  Get filtered business rules (VALIDATION only):")
    result = interface.get_business_rules("VALIDATION")
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n3️⃣  Get the customer journey:")
    result = interface.get_customer_journey()
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n4️⃣  Get business entities:")
    result = interface.get_business_entities()
    print_result(result)
    input("Press Enter to continue...")


def example_4_semantic_analysis(interface):
    """Example 4: Deep Code Understanding"""
    print_header("EXAMPLE 4: Deep Code Understanding")
    print("\nUnderstand code PURPOSE, RISKS, and BUSINESS IMPACT (uses LLM):")
    
    # Example payment code
    sample_code = '''
def process_payment(customer, amount):
    """Process customer payment through Stripe."""
    # Validate amount
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    # Charge customer
    charge = stripe.charge(customer.stripe_id, amount)
    
    # Record transaction
    transaction = Transaction(
        customer_id=customer.id,
        amount=amount,
        status="completed"
    )
    transaction.save()
    
    # Send confirmation
    send_email(customer.email, f"Payment of ${amount} processed")
    
    return charge
'''
    
    print("\n1️⃣  Analyze code semantically:")
    print("\nAnalyzing this code:")
    print(sample_code)
    result = interface.analyze_code_semantics(sample_code, "payment.py")
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n2️⃣  Ask a question about code:")
    result = interface.ask_question(
        "What are the potential risks in this payment handler?",
        sample_code
    )
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n3️⃣  Ask about the system (no code needed):")
    result = interface.ask_question("Why is error handling important in payment systems?")
    print_result(result)
    input("Press Enter to continue...")


def example_5_graph_queries(interface):
    """Example 5: Relationship Exploration"""
    print_header("EXAMPLE 5: Relationship Exploration")
    print("\nExplore how entities relate and flow through the system:")
    
    print("\n1️⃣  Trace data flow (Customer -> Payment):")
    result = interface.trace_data_flow("Customer", "Payment")
    print_result(result)
    input("Press Enter to continue...")
    
    print("\n2️⃣  Find circular dependencies:")
    result = interface.find_circular_dependencies()
    print_result(result)
    input("Press Enter to continue...")


def example_6_smart_caching(interface):
    """Example 6: Smart Caching"""
    print_header("EXAMPLE 6: Smart Caching")
    print("\nResults are automatically cached for repeated queries:")
    
    print("\n1️⃣  First call (computed, not cached):")
    result1 = interface.list_modules()
    print(f"  Cache hit: {result1.cache_hit} ❌ (not cached)")
    print(f"  Results: {len(result1.results)} queries")
    
    print("\n2️⃣  Second call (returns cached instantly):")
    result2 = interface.list_modules()
    print(f"  Cache hit: {result2.cache_hit} ✅ (cached!)")
    print(f"  Results: {len(result2.results)} queries (same as before)")
    
    print("\n✨ Cached queries:")
    print("   - list_modules()")
    print("   - get_business_rules()")
    print("   - get_customer_journey()")
    print("   - find_circular_dependencies()")


def example_7_result_structure(interface):
    """Example 7: Understanding Result Structure"""
    print_header("EXAMPLE 7: Understanding Result Structure")
    print("\nAll queries return a QueryResult with consistent structure:")
    
    result = interface.list_modules()
    
    print("\n📊 QueryResult structure:")
    print(f"  .query: {result.query}")
    print(f"  .query_type: {result.query_type}")
    print(f"  .success: {result.success}")
    print(f"  .results: List[{len(result.results)} items]")
    print(f"  .metadata: {result.metadata}")
    print(f"  .cache_hit: {result.cache_hit}")
    print(f"  .confidence: {result.confidence}")
    
    print("\n🔄 Convert to dict for JSON:")
    result_dict = result.to_dict()
    print(json.dumps(result_dict, indent=2)[:500] + "...")


def example_8_combined_workflow(interface):
    """Example 8: Complex Real-World Workflow"""
    print_header("EXAMPLE 8: Combined Workflow - Payment System Analysis")
    print("\nCombine multiple queries for comprehensive understanding:")
    
    print("\n📋 STEP 1: Get business rules for payments")
    rules = interface.get_business_rules("PAYMENT")
    print(f"   Found {rules.metadata['count']} payment rules")
    
    print("\n📋 STEP 2: Understand the payment journey")
    journey = interface.get_customer_journey()
    print(f"   Journey has {journey.metadata['steps']} steps")
    
    print("\n📋 STEP 3: Trace payment data flow")
    flow = interface.trace_data_flow("Customer", "Payment")
    print(f"   Found {flow.metadata['path_count']} flow paths")
    
    print("\n✅ Summary:")
    print(f"   Total business rules analyzed: {rules.metadata['count']}")
    print(f"   Journey steps covered: {journey.metadata['steps']}")
    print(f"   Data flow paths identified: {flow.metadata['path_count']}")
    print("\n   This gives a complete picture of payment processing!")


def main():
    """Run all examples."""
    if len(sys.argv) < 2:
        print("Usage: python3 unified_llm_quick_start.py /path/to/repo")
        print("\nExamples:")
        print("  python3 unified_llm_quick_start.py /path/to/spring-framework")
        print("  python3 unified_llm_quick_start.py /path/to/my-project")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 13 + "UNIFIED LLM QUERY INTERFACE - QUICK START" + " " * 14 + "║")
    print("╚" + "=" * 68 + "╝")
    
    print(f"\n📂 Repository: {repo_path}")
    print("\n🔄 Initializing interface (this may take a minute)...")
    
    try:
        interface = UnifiedLLMQueryInterface(repo_path)
        print("✅ Interface ready!\n")
    except Exception as e:
        print(f"\n❌ Error initializing interface: {e}")
        sys.exit(1)
    
    examples = [
        ("Natural Language Queries", example_1_natural_language),
        ("Structural Code Queries", example_2_structural_queries),
        ("Business Logic Queries", example_3_business_logic),
        ("Semantic Analysis (LLM)", example_4_semantic_analysis),
        ("Graph & Relationships", example_5_graph_queries),
        ("Smart Caching", example_6_smart_caching),
        ("Result Structure", example_7_result_structure),
        ("Combined Workflow", example_8_combined_workflow),
    ]
    
    print("\n📚 EXAMPLES:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "=" * 70)
    print("Which example would you like to run?")
    print("(Enter number 1-8, or 'all' for all examples, or 'q' to quit)")
    print("=" * 70)
    
    while True:
        choice = input("\n> ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Goodbye!")
            break
        elif choice == 'all':
            for name, example_func in examples:
                try:
                    example_func(interface)
                except KeyboardInterrupt:
                    print("\n⏸️  Skipped to next example")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(examples):
                    name, example_func = examples[idx]
                    try:
                        example_func(interface)
                    except KeyboardInterrupt:
                        print("\n⏸️  Example interrupted")
                    except Exception as e:
                        print(f"\n❌ Error: {e}")
                else:
                    print("❌ Invalid choice. Enter a number 1-8")
            except ValueError:
                print("❌ Invalid input. Enter a number 1-8, 'all', or 'q'")


if __name__ == "__main__":
    main()
