#!/usr/bin/env python3
"""
Test Against Real Source Code Repositories
============================================

This script demonstrates how to run all analysis tools against real repositories.
Choose and uncomment the test case you want to run.
"""

import sys
import os
from pathlib import Path

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from cartographer_agent import cartographer_agent
from smart_rule_inference import SmartRuleInference
from enhanced_business_extractor import EnhancedBusinessExtractor
from incremental_indexer import IncrementalIndexer
from context_pruner import ContextPruner
from performance_dashboard import PerformanceDashboard
from config_manager import ConfigManager
from integrated_workflow import create_workflow_from_file


def test_1_basic_cartographer_analysis():
    """Test 1: Basic cartographer analysis on a repository."""
    print("\n" + "="*80)
    print("TEST 1: Basic Cartographer Analysis")
    print("="*80)
    
    # Add your repo path here
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    print(f"\n📂 Analyzing repository: {repo_path}")
    print(f"📝 File types: .py, .java")
    
    try:
        results = cartographer_agent(repo_path, file_ext='.py', max_workers=4)
        
        # Count different statement types
        modules = sum(1 for s in results if ':Module' in s)
        classes = sum(1 for s in results if ':Class' in s)
        functions = sum(1 for s in results if ':Function' in s)
        
        print(f"\n✅ Analysis Complete!")
        print(f"   Total Cypher statements: {len(results)}")
        print(f"   Modules found: {modules}")
        print(f"   Classes found: {classes}")
        print(f"   Functions found: {functions}")
        
        # Show first few Cypher statements
        print(f"\n📊 Sample Cypher statements (first 10):")
        for i, stmt in enumerate(results[:10], 1):
            print(f"   {i}. {stmt[:80]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_2_incremental_indexing():
    """Test 2: Incremental indexing - only process changed files."""
    print("\n" + "="*80)
    print("TEST 2: Incremental Indexing (Cache-Based Analysis)")
    print("="*80)
    
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    print(f"\n📂 Repository: {repo_path}")
    print(f"🔍 Scanning for changes...")
    
    try:
        indexer = IncrementalIndexer(repo_path)
        
        # First run - full analysis
        files_to_process, stats = indexer.get_files_to_process(
            file_extensions=['.py'],
            force_reindex=False
        )
        
        print(f"\n📊 Results:")
        print(f"   Mode: {stats['mode']}")
        print(f"   Files to process: {len(files_to_process)}")
        if 'total_files' in stats:
            print(f"   Total files in repo: {stats['total_files']}")
            pct = (len(files_to_process) / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
            print(f"   Efficiency: {pct:.1f}% of files need processing")
        
        # Show cache stats
        cache_stats = indexer.get_stats()
        print(f"\n💾 Cache Statistics:")
        print(f"   Cached files: {cache_stats['cached_files']}")
        print(f"   Last indexed: {cache_stats['last_indexed']}")
        
        # Show sample files
        print(f"\n📝 Files to process (first 5):")
        for f in files_to_process[:5]:
            print(f"   - {f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_3_context_pruning():
    """Test 3: Context pruning - extract only signatures and docstrings."""
    print("\n" + "="*80)
    print("TEST 3: Context Pruning (Reduce Token Usage)")
    print("="*80)
    
    file_path = "/Users/juani/github-projects/documentationmcp/documentationmcp/agents/smart_rule_inference.py"
    
    print(f"\n📄 Analyzing file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        pruner = ContextPruner('python')
        elements = pruner.prune_file(file_path, source_code)
        
        print(f"\n✅ Context Pruning Complete!")
        print(f"   Original code size: {len(source_code)} bytes")
        print(f"   Elements extracted: {len(elements)}")
        
        # Calculate reduction
        pruned_size = sum(len(e.get('signature', '')) + len(e.get('docstring', '')) 
                         for e in elements)
        reduction = ((len(source_code) - pruned_size) / len(source_code) * 100)
        
        print(f"   Pruned size: {pruned_size} bytes")
        print(f"   Token reduction: ~{reduction:.1f}%")
        
        # Show sample
        print(f"\n📊 Sample extracted elements (first 5):")
        for i, elem in enumerate(elements[:5], 1):
            sig = elem.get('signature', '?')[:60]
            print(f"   {i}. {sig}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_4_business_rule_discovery():
    """Test 4: Discover business rules from code."""
    print("\n" + "="*80)
    print("TEST 4: Smart Business Rule Discovery")
    print("="*80)
    
    # Sample e-commerce code with business rules
    sample_code = '''
class OrderProcessor:
    def process_order(self, order):
        # Validation: Amount constraints
        if order.amount < 1.0 or order.amount > 999999.99:
            raise ValueError("Invalid order amount")
        
        # State machine: order status transitions
        order.status = 'pending'
        self.validate_inventory(order)
        
        order.status = 'processing'
        self.process_payment(order)
        
        order.status = 'completed'
        self.send_confirmation(order)
    
    def can_delete_order(self, user, order):
        # Permission rules: Admin can delete, customer can delete own pending orders
        if user.is_admin():
            return True
        if order.customer_id == user.id and order.status == 'pending':
            return True
        return False
'''
    
    print(f"\n📝 Analyzing code snippet for business rules...")
    
    try:
        inference = SmartRuleInference()
        rules = inference.infer_rules(sample_code)
        
        print(f"\n✅ Rules Discovered!")
        print(f"   Total rules: {len(rules)}")
        
        if rules.get('validation_rules'):
            print(f"\n📋 Validation Rules ({len(rules['validation_rules'])}):")
            for rule in rules['validation_rules'][:3]:
                print(f"   - {rule}")
        
        if rules.get('temporal_dependencies'):
            print(f"\n⏱️  Temporal Dependencies ({len(rules['temporal_dependencies'])}):")
            for rule in rules['temporal_dependencies'][:3]:
                print(f"   - {rule}")
        
        if rules.get('permission_rules'):
            print(f"\n🔐 Permission Rules ({len(rules['permission_rules'])}):")
            for rule in rules['permission_rules'][:3]:
                print(f"   - {rule}")
        
    except Exception as e:
        print(f"⚠️  Note: {e}")


def test_5_integrated_workflow_analysis():
    """Test 5: Full integrated workflow with configuration."""
    print("\n" + "="*80)
    print("TEST 5: Integrated Workflow Analysis")
    print("="*80)
    
    repo_path = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    project_name = "documentationmcp"
    
    print(f"\n📂 Repository: {repo_path}")
    print(f"🔧 Creating configuration...")
    
    try:
        # Create config
        manager = ConfigManager()
        config = manager.create_default_config(repo_path, project_name)
        
        print(f"✅ Configuration created")
        print(f"   Project: {config['project_name']}")
        print(f"   Modules: {len(config['modules'])}")
        print(f"   Extensions: {config['modules'][0]['extensions']}")
        
        # Save config
        config_path = manager.save_config(config, project_name)
        print(f"   Saved to: {config_path}")
        
        # Could run full workflow here (requires LLM setup)
        print(f"\n💡 Full workflow ready. To run:")
        print(f"   python3 agents/integrated_workflow.py {config_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_6_performance_analysis():
    """Test 6: View performance metrics and savings."""
    print("\n" + "="*80)
    print("TEST 6: Performance Dashboard")
    print("="*80)
    
    try:
        dashboard = PerformanceDashboard()
        metrics = dashboard.get_metrics()
        
        if metrics['analyses'] > 0:
            print(f"\n📊 Analysis History:")
            print(f"   Total analyses: {metrics['analyses']}")
            print(f"   Total API calls: {metrics['total_api_calls']}")
            print(f"   Total tokens: {metrics['total_tokens']:,}")
            print(f"   Cost saved: ~${metrics['savings']:.2f}")
            print(f"   Efficiency: {metrics['efficiency']}%")
        else:
            print(f"\n📊 No analysis history yet. Run analyses to build metrics!")
        
    except Exception as e:
        print(f"⚠️  {e}")


if __name__ == "__main__":
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "REAL-WORLD TESTING SUITE".center(78) + "║")
    print("║" + "Test the application against actual source code".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    print("\n🎯 Available Tests:")
    print("   1. test_1_basic_cartographer_analysis()       - Analyze repo structure")
    print("   2. test_2_incremental_indexing()              - Cache optimization")
    print("   3. test_3_context_pruning()                   - Token reduction")
    print("   4. test_4_business_rule_discovery()           - Find business rules")
    print("   5. test_5_integrated_workflow_analysis()      - Full workflow")
    print("   6. test_6_performance_analysis()              - View metrics")
    
    print("\n" + "-"*80)
    
    # Run tests
    if len(sys.argv) > 1:
        test_num = sys.argv[1]
        if test_num == '1':
            test_1_basic_cartographer_analysis()
        elif test_num == '2':
            test_2_incremental_indexing()
        elif test_num == '3':
            test_3_context_pruning()
        elif test_num == '4':
            test_4_business_rule_discovery()
        elif test_num == '5':
            test_5_integrated_workflow_analysis()
        elif test_num == '6':
            test_6_performance_analysis()
        elif test_num == 'all':
            test_1_basic_cartographer_analysis()
            test_2_incremental_indexing()
            test_3_context_pruning()
            test_4_business_rule_discovery()
            test_5_integrated_workflow_analysis()
            test_6_performance_analysis()
    else:
        # Run all tests by default
        test_1_basic_cartographer_analysis()
        test_2_incremental_indexing()
        test_3_context_pruning()
        test_4_business_rule_discovery()
        test_5_integrated_workflow_analysis()
        test_6_performance_analysis()
