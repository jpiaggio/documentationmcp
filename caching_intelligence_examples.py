"""
Caching Intelligence Examples
Practical demonstrations of all caching intelligence features
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.cache_intelligence import (
    GitHistoryAnalyzer,
    DependencyGraphBuilder, 
    ChangePrioritizer,
    SmartCachePredictor,
    CacheIntelligenceManager
)
from agents.smart_cartographer import SmartCartographerAgent


def example_1_git_analysis():
    """
    Example 1: Analyze git history to find file patterns
    
    Use case: Understand which files change together
    """
    print("=" * 60)
    print("Example 1: Git History Analysis")
    print("=" * 60)
    
    repo = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    analyzer = GitHistoryAnalyzer(repo)
    
    print("\n1. Finding hot modules (frequently changed files)...")
    hotspots = analyzer.find_hot_modules(days=30, top_n=5)
    for filepath, count in hotspots:
        print(f"   {os.path.basename(filepath)}: {count} changes in last 30 days")
    
    print("\n2. Finding files that change together...")
    if hotspots:
        test_file = hotspots[0][0]
        print(f"   Analyzing: {os.path.basename(test_file)}")
        cochanges = analyzer.find_cochanged_files(test_file, max_commits=50, min_count=1)
        if cochanges:
            for filepath, count in list(cochanges.items())[:5]:
                print(f"   - {os.path.basename(filepath)}: changed together {count} times")
        else:
            print("   (No cochanges found - maybe new file or no git history)")
    
    print("\n3. Change frequency distribution (all Python files)...")
    frequency = analyzer.analyze_change_frequency(['.py'], days=30)
    if frequency:
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        for filepath, count in sorted_freq:
            print(f"   {os.path.basename(filepath)}: {count} changes")
    else:
        print("   (No recent changes found)")


def example_2_dependency_graph():
    """
    Example 2: Build and analyze dependency graphs
    
    Use case: Find which files depend on each other
    """
    print("\n" + "=" * 60)
    print("Example 2: Dependency Graph Analysis")
    print("=" * 60)
    
    repo = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    builder = DependencyGraphBuilder(repo)
    
    # Get some Python files
    all_files = []
    for root, _, files in os.walk(os.path.join(repo, 'agents')):
        for f in files:
            if f.endswith('.py') and not f.startswith('_'):
                all_files.append(os.path.join(root, f))
    
    if not all_files:
        print("No Python files found to analyze")
        return
    
    print(f"\n1. Analyzing {len(all_files)} files for dependencies...")
    
    # Show imports for first file
    test_file = all_files[0]
    imports = builder.extract_imports(test_file, 'python')
    print(f"\n2. Imports in {os.path.basename(test_file)}:")
    for imp in sorted(imports)[:5]:
        print(f"   - {imp}")
    
    # Find files that depend on this one
    print(f"\n3. Building dependency graph...")
    dependents = builder.find_dependent_files(test_file, all_files, 'python')
    if dependents:
        print(f"   Files that depend on {os.path.basename(test_file)}:")
        for f in list(dependents)[:5]:
            print(f"   - {os.path.basename(f)}")
    else:
        print(f"   No files depend on {os.path.basename(test_file)}")
    
    # Find related files
    print(f"\n4. Finding all related files (depth=2)...")
    related = builder.find_related_files(test_file, all_files, 'python', depth=2)
    print(f"   Found {len(related)} related files")
    if related:
        print("   Examples:")
        for f in list(related)[:5]:
            print(f"   - {os.path.basename(f)}")


def example_3_change_prioritization():
    """
    Example 3: Prioritize files by change frequency and impact
    
    Use case: Focus analysis on most important files
    """
    print("\n" + "=" * 60)
    print("Example 3: Change Prioritization")
    print("=" * 60)
    
    repo = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    analyzer = GitHistoryAnalyzer(repo)
    builder = DependencyGraphBuilder(repo)
    
    # Get test files
    all_files = []
    for root, _, files in os.walk(os.path.join(repo, 'agents')):
        for f in files:
            if f.endswith('.py'):
                all_files.append(os.path.join(root, f))
    
    if not all_files:
        print("No Python files found")
        return
    
    # Build dependency graph
    dependency_graph = builder.build_dependency_graph(all_files, 'python')
    
    # Get frequency data
    frequency = analyzer.analyze_change_frequency(['.py'], days=30)
    
    # Prioritize
    prioritizer = ChangePrioritizer(analyzer, dependency_graph)
    prioritized = prioritizer.prioritize_files(all_files[:20], frequency)
    
    print(f"\n1. Top 5 priority files (by change frequency + impact):")
    for filepath, score in prioritized[:5]:
        basename = os.path.basename(filepath)
        dependents = sum(
            1 for deps in dependency_graph.values() 
            if filepath in deps
        )
        print(f"   {basename}: score={score:.1f}, dependents={dependents}")
    
    if len(prioritized) > 5:
        print(f"\n2. Lower priority files:")
        for filepath, score in prioritized[-5:]:
            basename = os.path.basename(filepath)
            print(f"   {basename}: score={score:.1f}")


def example_4_smart_predictor():
    """
    Example 4: Use smart cache predictor to anticipate analysis needs
    
    Use case: Predict what needs re-analysis when files change
    """
    print("\n" + "=" * 60)
    print("Example 4: Smart Cache Prediction")
    print("=" * 60)
    
    repo = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    try:
        predictor = SmartCachePredictor(repo)
        
        # Get files
        all_files = []
        for root, _, files in os.walk(os.path.join(repo, 'agents')):
            for f in files:
                if f.endswith('.py'):
                    all_files.append(os.path.join(root, f))
        
        if not all_files:
            print("No Python files found")
            return
        
        print(f"\n1. Initializing intelligence system...")
        print(f"   Analyzing {len(all_files)} files...")
        result = predictor.analyze_patterns(all_files[:50])  # Limit for demo
        
        print(f"   Found {result['cochange_patterns_found']} cochange patterns")
        print(f"   Found {result['frequently_changed_files']} frequently changed files")
        print(f"   Total dependencies: {result['total_dependencies']}")
        
        # Simulate file changes
        if len(all_files) >= 2:
            changed = all_files[:2]
            print(f"\n2. Predicting impact of changes to {len(changed)} files:")
            for f in changed:
                print(f"   - {os.path.basename(f)}")
            
            plan = predictor.get_analysis_plan(changed, all_files, 'python')
            
            print(f"\n3. Analysis prediction results:")
            print(f"   Total files to analyze: {plan['total_files_to_analyze']}")
            print(f"   Files to prefetch: {plan['total_prefetch']}")
            
            print(f"\n4. Predicted impacts by category:")
            breakdown = plan['analysis_priority_breakdown']
            for category, files in breakdown.items():
                count = len(files)
                if count > 0:
                    print(f"   {category}: {count} files")
                    for filepath, score in files[:2]:
                        print(f"     - {os.path.basename(filepath)}: {score:.1f}")
    
    except Exception as e:
        print(f"Note: Smart predictor needs git history: {e}")


def example_5_smart_cartographer():
    """
    Example 5: Use SmartCartographerAgent for analysis
    
    Use case: Run intelligent analysis with caching
    """
    print("\n" + "=" * 60)
    print("Example 5: Smart Cartographer Agent")
    print("=" * 60)
    
    repo = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    try:
        agent = SmartCartographerAgent(repo)
        
        print(f"\n1. Getting analysis report...")
        report = agent.get_analysis_report()
        
        print(f"\n2. Incremental indexing status:")
        inc = report['incremental_indexing']
        print(f"   Cache directory: {inc['cache_directory']}")
        print(f"   Cached files: {inc['cached_files']}")
        print(f"   Last indexed: {inc['last_indexed']}")
        
        print(f"\n3. Cache intelligence status:")
        ci = report['cache_intelligence']
        print(f"   Initialized: {ci['initialized']}")
        print(f"   Cochange patterns: {ci['cochange_patterns']}")
        print(f"   Known dependencies: {ci['known_dependencies']}")
        
        # Get files to analyze
        print(f"\n4. Getting files to analyze (with intelligence)...")
        files, metadata = agent.get_files_to_analyze(
            file_extensions=['.py'],
            use_intelligence=True
        )
        
        print(f"   Files to analyze: {len(files)}")
        print(f"   Intelligence used: {metadata['intelligence_used']}")
        
        if metadata['intelligence_used'] and 'predicted_analyses' in metadata:
            pred = metadata['predicted_analyses']
            if 'top_priorities' in pred and pred['top_priorities']:
                print(f"\n5. Top priority files:")
                for item in pred['top_priorities'][:3]:
                    print(f"   {item['file']}: {item['reason']}")
    
    except Exception as e:
        print(f"Note: SmartCartographerAgent demo: {e}")
        import traceback
        traceback.print_exc()


def example_6_workflow():
    """
    Example 6: Complete workflow - initialize, analyze, report
    
    Use case: Real-world analysis pipeline
    """
    print("\n" + "=" * 60)
    print("Example 6: Complete Workflow")
    print("=" * 60)
    
    repo = "/Users/juani/github-projects/documentationmcp/documentationmcp"
    
    try:
        manager = CacheIntelligenceManager(repo)
        
        # Get all Python files
        all_files = []
        for root, _, files in os.walk(os.path.join(repo, 'agents')):
            for f in files:
                if f.endswith('.py'):
                    all_files.append(os.path.join(root, f))
        
        if not all_files:
            print("No files found")
            return
        
        print(f"\n1. Step 1: Initialize intelligence system")
        print(f"   Analyzing {len(all_files)} files...")
        result = manager.initialize_intelligence(all_files)
        print(f"   Initialized: {result}")
        
        print(f"\n2. Step 2: Simulate some files changing")
        changed = all_files[:1] if all_files else []
        if changed:
            print(f"   Changed file: {os.path.basename(changed[0])}")
            
            print(f"\n3. Step 3: Get smart analysis plan")
            plan = manager.get_smart_analysis_plan(changed, all_files, 'python')
            print(f"   Files to analyze: {plan['total_files_to_analyze']}")
            print(f"   Prefetch candidates: {plan['total_prefetch']}")
        
        print(f"\n4. Step 4: Get system status")
        status = manager.get_status()
        print(f"   Status: {status}")
    
    except Exception as e:
        print(f"Workflow demo: {e}")


def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("CACHING INTELLIGENCE EXAMPLES")
    print("=" * 60)
    
    examples = [
        example_1_git_analysis,
        example_2_dependency_graph,
        example_3_change_prioritization,
        example_4_smart_predictor,
        example_5_smart_cartographer,
        example_6_workflow,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n⚠️  Example {i} error: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            '1': example_1_git_analysis,
            '2': example_2_dependency_graph,
            '3': example_3_change_prioritization,
            '4': example_4_smart_predictor,
            '5': example_5_smart_cartographer,
            '6': example_6_workflow,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Available: 1, 2, 3, 4, 5, 6")
    else:
        run_all_examples()
