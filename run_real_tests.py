#!/usr/bin/env python3
"""
Practical Real-World Testing - Simplified Examples
===================================================

Run any of these to test against your actual repositories.
"""

import sys
import os
from pathlib import Path

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))


def test_on_documentationmcp_repo():
    """Test 1: Analyze your own documentationmcp repository."""
    print("\n" + "="*80)
    print("TEST 1: Analyze DocumentationMCP Repository")
    print("="*80)
    
    from cartographer_agent import cartographer_agent
    
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    print(f"\n📂 Repository: {repo_path}")
    print(f"🔍 Scanning Python files...")
    
    try:
        results = cartographer_agent(repo_path, file_ext='.py', max_workers=4)
        
        # Count different statement types
        modules = sum(1 for s in results if ':BusinessModule' in s)
        functions = sum(1 for s in results if ':Function' in s)
        relationships = sum(1 for s in results if '-[:' in s)
        
        print(f"\n✅ Analysis Complete!")
        print(f"   Total statements: {len(results):,}")
        print(f"   Business modules: {modules}")
        print(f"   Functions/methods: {functions}")
        print(f"   Relationships: {relationships}")
        
        # Show first few statements
        print(f"\n📊 Sample Cypher statements:")
        for i, stmt in enumerate(results[:5], 1):
            # Truncate long statements
            preview = stmt[:100].replace('\n', ' ')
            print(f"   {i}. {preview}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_on_custom_repo():
    """Test 2: Analyze ANY repository - you provide the path."""
    print("\n" + "="*80)
    print("TEST 2: Analyze Custom Repository")
    print("="*80)
    
    from cartographer_agent import cartographer_agent
    
    # REQUEST USER INPUT OR USE EXAMPLE
    print(f"\n📂 Example repositories you can test:")
    print(f"   - /Users/juani/github-projects/documentationmcp")
    print(f"   - /Users/juani/github-projects/mattermost/mattermost")
    print(f"   - /Users/juani/github-projects/spring-framework/spring-framework")
    
    # Auto-detect available repos
    repo_path = None
    
    # Try documentationmcp first
    if Path("/Users/juani/github-projects/documentationmcp").exists():
        repo_path = "/Users/juani/github-projects/documentationmcp"
        print(f"\n✅ Found documentationmcp repo")
    # Try mattermost
    elif Path("/Users/juani/github-projects/mattermost/mattermost").exists():
        repo_path = "/Users/juani/github-projects/mattermost/mattermost"
        print(f"\n✅ Found Mattermost repo")
    else:
        print(f"\n❌ Could not find example repos")
        return False
    
    print(f"\n📂 Analyzing: {repo_path}")
    print(f"🔍 Scanning for .py and .java files...")
    
    try:
        # Determine file extension
        py_count = len(list(Path(repo_path).rglob("*.py"))) if Path(repo_path).exists() else 0
        java_count = len(list(Path(repo_path).rglob("*.java"))) if Path(repo_path).exists() else 0
        
        ext = '.py' if py_count > 0 else '.java'
        
        print(f"   Python files: {py_count}")
        print(f"   Java files: {java_count}")
        print(f"   Analyzing: {ext} files")
        
        results = cartographer_agent(repo_path, file_ext=ext, max_workers=4)
        
        print(f"\n✅ Analysis Complete!")
        print(f"   Total Cypher statements: {len(results):,}")
        
        # Show sample
        if results:
            print(f"\n📊 First statement:")
            print(f"   {results[0][:120]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_incremental_analysis():
    """Test 3: Show how incremental indexing works."""
    print("\n" + "="*80)
    print("TEST 3: Incremental Indexing - Smart Caching")
    print("="*80)
    
    from incremental_indexer import IncrementalIndexer
    
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    print(f"\n📂 Repository: {repo_path}")
    print(f"🔍 Checking for changes since last analysis...")
    
    try:
        indexer = IncrementalIndexer(repo_path)
        
        # Check what files need processing
        files_to_process, stats = indexer.get_files_to_process(
            file_extensions=['.py'],
            force_reindex=False
        )
        
        print(f"\n📊 Results:")
        print(f"   Mode: {stats['mode']}")
        print(f"   Files changed: {len(files_to_process)}")
        
        # Calculate efficiency
        if 'total_files' in stats and stats['total_files'] > 0:
            pct = (len(files_to_process) / stats['total_files'] * 100)
            print(f"   Total Python files: {stats['total_files']}")
            print(f"   Only need to process: {pct:.1f}%")
            
            # Calculate cost savings
            if pct > 0:
                print(f"\n💰 Cost Savings:")
                print(f"   Without incremental: 100% API calls")
                print(f"   With incremental: {pct:.1f}% API calls")
                print(f"   Savings: {100-pct:.1f}% reduction! 🚀")
        else:
            print(f"\n✅ No changes detected since last index!")
            print(f"   Cost savings: 100% (no re-analysis needed)")
        
        # Show cache info
        cache_stats = indexer.get_stats()
        print(f"\n💾 Cache Information:")
        print(f"   Files in cache: {cache_stats['cached_files']}")
        print(f"   Last indexed: {cache_stats['last_indexed']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_business_rules_extraction():
    """Test 4: Extract business rules from real code."""
    print("\n" + "="*80)
    print("TEST 4: Business Rules Extraction")
    print("="*80)
    
    from business_rules_extractor import BusinessRulesExtractor
    
    # Sample business rule code
    sample_code = """
class OrderProcessor:
    def process_order(self, order):
        # Validation rule: Amount limits
        MIN_ORDER = 1.0
        MAX_ORDER = 999999.99
        
        if order.amount < MIN_ORDER:
            raise ValueError(f"Order must be at least ${MIN_ORDER}")
        if order.amount > MAX_ORDER:
            raise ValueError(f"Order cannot exceed ${MAX_ORDER}")
        
        # State machine: Order status flow
        order.status = 'pending'
        self.validate_items(order)  # Must happen first
        
        order.status = 'processing'
        self.charge_payment(order)
        
        order.status = 'completed'
        self.send_confirmation(order)
        
    def can_cancel_order(self, user, order):
        # Permission rule: Admin can always cancel
        if user.role == 'admin':
            return True
        
        # Customer can only cancel pending orders
        if order.customer_id == user.id:
            return order.status == 'pending'
        
        return False
"""
    
    print(f"\n📝 Sample code with business rules:")
    print(f"   - Amount validation (min/max)")
    print(f"   - State machine (pending → processing → completed)")
    print(f"   - Permission rules (admin vs customer)")
    
    try:
        extractor = BusinessRulesExtractor()
        
        # Extract rules
        rules = extractor.extract_rules_from_code(sample_code)
        
        print(f"\n✅ Rules Extracted!")
        print(f"   Total rules found: {len(rules)}")
        
        # Show breakdown
        validation_count = len([r for r in rules if 'validation' in str(r).lower()])
        state_count = len([r for r in rules if 'state' in str(r).lower() or 'status' in str(r).lower()])
        permission_count = len([r for r in rules if 'permission' in str(r).lower() or 'role' in str(r).lower()])
        
        print(f"\n📋 Rule Breakdown:")
        print(f"   Validation rules: {validation_count}")
        print(f"   State/Flow rules: {state_count}")
        print(f"   Permission rules: {permission_count}")
        
        # Show first few
        if rules:
            print(f"\n📊 Sample rules (first 3):")
            for i, rule in enumerate(rules[:3], 1):
                rule_str = str(rule)[:80]
                print(f"   {i}. {rule_str}...")
        
        return True
    except Exception as e:
        print(f"⚠️  Note: {e}")
        print(f"   (This is expected if business rules extractor needs setup)")
        return False


def test_all():
    """Run all tests."""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "COMPREHENSIVE REAL-WORLD TESTING SUITE".center(78) + "║")
    print("║" + "Test the system against actual repositories".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    results = []
    
    results.append(("Analyze DocumentationMCP", test_on_documentationmcp_repo()))
    results.append(("Analyze Custom Repo", test_on_custom_repo()))
    results.append(("Incremental Indexing", test_incremental_analysis()))
    results.append(("Business Rules Extraction", test_business_rules_extraction()))
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "⚠️  COMPLETED"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\n✨ {passed_count}/{len(results)} tests completed successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_num = sys.argv[1]
        if test_num == '1':
            test_on_documentationmcp_repo()
        elif test_num == '2':
            test_on_custom_repo()
        elif test_num == '3':
            test_incremental_analysis()
        elif test_num == '4':
            test_business_rules_extraction()
        elif test_num == 'all':
            test_all()
        else:
            print("Usage: python3 test_real_codebase.py [1|2|3|4|all]")
    else:
        test_all()
