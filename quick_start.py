#!/usr/bin/env python3
"""
Quick Start Helper - Sets up enterprise enhancements in minutes

Usage:
  1. python3 quick_start.py                 # Interactive setup
  2. python3 quick_start.py /path/to/repo  # Auto-setup with defaults
"""

import sys
import os
from pathlib import Path

# Add agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from config_manager import ConfigManager
from integrated_workflow import create_workflow_from_file, AnalysisConfig
from performance_dashboard import PerformanceDashboard


def print_banner():
    """Print welcome banner."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  Enterprise Enhancements - Quick Start Guide".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")


def quick_setup(repo_path: str = None):
    """Quick setup for a repository."""
    print_banner()
    
    print("\n📋 STEP 1: Create Configuration")
    print("-" * 80)
    
    manager = ConfigManager()
    
    if repo_path is None:
        repo_path = input("Enter repository path: ").strip()
    
    if not Path(repo_path).exists():
        print(f"❌ Path does not exist: {repo_path}")
        sys.exit(1)
    
    project_name = Path(repo_path).name
    config = manager.create_default_config(repo_path, project_name)
    
    print(f"✅ Configuration created for: {project_name}")
    print(f"   Path: {repo_path}")
    print(f"   Extensions: {', '.join(config['modules'][0]['extensions'])}")
    
    print("\n📋 STEP 2: Save Configuration")
    print("-" * 80)
    
    config_path = manager.save_config(config, project_name)
    
    print("\n📋 STEP 3: Run First Analysis")
    print("-" * 80)
    
    run_analysis = input("Run analysis now? (y/n): ").strip().lower()
    
    if run_analysis != 'y':
        print(f"\n✅ Setup complete!")
        print(f"\nTo run analysis later, use:")
        print(f"  python3 agents/integrated_workflow.py {config_path}")
        print(f"\nOr programmatically:")
        print(f"  from agents.integrated_workflow import create_workflow_from_file")
        print(f"  workflow = create_workflow_from_file('{config_path}')")
        print(f"  result = workflow.analyze()")
        return
    
    # Run analysis
    print(f"\n🔄 Starting analysis of {project_name}...")
    print("-" * 80)
    
    try:
        workflow = create_workflow_from_file(config_path)
        result = workflow.analyze()
        
        if result['status'] == 'success' and result.get('metrics'):
            metrics = result['metrics']
            
            print("\n" + "="*80)
            print("✅ ANALYSIS COMPLETE")
            print("="*80)
            
            print(f"\n📊 Results:")
            print(f"   Files analyzed: {metrics['total_files_processed']}")
            print(f"   Business rules: {metrics['total_statements']}")
            print(f"   Execution time: {metrics['execution_time']:.2f}s")
            
            print(f"\n💰 Cost Savings:")
            print(f"   Cost without optimization:  ${metrics['cost_before']:.2f}")
            print(f"   Cost with optimization:     ${metrics['cost_after']:.2f}")
            print(f"   Savings (this run):         ${metrics['cost_before'] - metrics['cost_after']:.2f}")
            print(f"   Monthly projection:         ${(metrics['cost_before'] - metrics['cost_after']) * 30:.2f}")
            print(f"   Annual projection:          ${(metrics['cost_before'] - metrics['cost_after']) * 365:.2f}")
            
            print(f"\n🔄 Incremental Indexing:")
            print(f"   API calls saved:    {metrics['api_calls_saved']:,}")
            print(f"   Token reduction:    {metrics['token_reduction']*100:.0f}%")
            
            print(f"\n📁 Caching & Future Runs:")
            print(f"   Cache location: .cartographer_cache/{project_name}/")
            print(f"   Next run: Only changed files will be analyzed (~90% faster)")
            
        else:
            print(f"\n⚠️  Status: {result.get('status', 'unknown')}")
            if 'message' in result:
                print(f"   {result['message']}")
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Show next steps
    print("\n" + "="*80)
    print("✨ NEXT STEPS")
    print("="*80)
    
    print(f"""
1. 📊 View performance metrics:
   python3 agents/performance_dashboard.py

2. 🔄 Run analysis again (will use cache):
   python3 agents/integrated_workflow.py {config_path}

3. ➕ Add more modules:
   python3 agents/config_manager.py

4. 📖 Read the full guide:
   cat MIGRATION_GUIDE.md

5. 🤖 Integrate with Copilot:
   cat MCP_TOOL_SCHEMA.json

Your configuration is saved. You can run analysis anytime with:
  python3 agents/integrated_workflow.py {config_path}
    """)


def interactive_mode():
    """Interactive setup wizard."""
    print_banner()
    
    print("\n🎯 Welcome to Enterprise Enhancements!")
    print("""
This quick start will help you:
1. Create a configuration for your project
2. Run your first analysis
3. Show you the cost savings
4. Set up automatic monitoring

Let's get started!
    """)
    
    print("\n📋 STEP 1: Project Information")
    print("-" * 80)
    
    project_name = input("Enter project name: ").strip()
    repo_path = input("Enter repository path: ").strip()
    
    if not Path(repo_path).exists():
        print(f"❌ Path does not exist: {repo_path}")
        sys.exit(1)
    
    manager = ConfigManager()
    config = manager.create_default_config(repo_path, project_name)
    
    print(f"\n✅ Found {len(config['modules'][0]['extensions'])} file extension(s)")
    
    # Customize settings
    print("\n📋 STEP 2: Customize Settings")
    print("-" * 80)
    
    workers = input("Number of parallel workers (default: 4): ").strip()
    if workers:
        config['parallel_workers'] = int(workers)
    
    prune = input("Enable context pruning? (y/n, default: y): ").strip().lower() != 'n'
    config['prune_context'] = prune
    
    # Save
    print("\n📋 STEP 3: Save Configuration")
    print("-" * 80)
    
    config_path = manager.save_config(config, project_name)
    manager.print_config(project_name)
    
    # Run analysis
    print("\n📋 STEP 4: First Analysis")
    print("-" * 80)
    
    run_now = input("Run analysis now? (y/n): ").strip().lower()
    
    if run_now == 'y':
        print(f"\n🔄 Analyzing {project_name}...")
        workflow = create_workflow_from_file(config_path)
        result = workflow.analyze()
        
        if result['status'] == 'success' and result.get('metrics'):
            metrics = result['metrics']
            print(f"\n✅ Complete! Analyzed {metrics['total_files_processed']} files")
            print(f"💰 Saved: ${metrics['cost_before'] - metrics['cost_after']:.2f} (this run)")
            print(f"📈 Monthly: ${(metrics['cost_before'] - metrics['cost_after']) * 30:.2f}")
    
    print(f"""
✨ Setup Complete!

Your configuration is ready at: {config_path}

Next time, run:
  python3 agents/integrated_workflow.py {config_path}

(It will be 90% faster due to caching!)
    """)


def show_help():
    """Show help message."""
    print("""
Usage:
  python3 quick_start.py [repo_path]

Examples:
  # Interactive setup
  python3 quick_start.py
  
  # Auto-setup with defaults
  python3 quick_start.py /path/to/repo
  
  # View dashboard
  python3 agents/performance_dashboard.py
  
  # List configurations
  python3 agents/config_manager.py list
    """)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_help()
        else:
            # Auto-setup with provided path
            quick_setup(sys.argv[1])
    else:
        # Interactive mode
        interactive_mode()
