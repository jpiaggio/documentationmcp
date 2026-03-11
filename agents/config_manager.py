#!/usr/bin/env python3
"""
Configuration Manager for Enterprise Enhancements

Helps users:
1. Create module configurations
2. Manage multiple repositories
3. Set up incremental indexing
4. Monitor performance across projects
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ConfigManager:
    """Manage analysis configurations."""
    
    def __init__(self, config_dir: str = ".cartographer_config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def create_default_config(self, repo_path: str, name: str = None) -> Dict[str, Any]:
        """
        Create default configuration for a repository.
        
        Args:
            repo_path: Path to repository
            name: Project name (optional)
        
        Returns:
            Configuration dictionary
        """
        if name is None:
            name = Path(repo_path).name
        
        # Detect language by looking at file types
        py_files = list(Path(repo_path).glob('**/*.py'))
        java_files = list(Path(repo_path).glob('**/*.java'))
        ts_files = list(Path(repo_path).glob('**/*.ts'))
        
        extensions = []
        if py_files:
            extensions.append('.py')
        if java_files:
            extensions.append('.java')
        if ts_files:
            extensions.append('.ts')
        
        if not extensions:
            extensions = ['.py']  # Default
        
        return {
            'modules': [
                {
                    'path': repo_path,
                    'name': name,
                    'extensions': extensions
                }
            ],
            'parallel_workers': 4,
            'force_reindex': False,
            'extract_business_rules': True,
            'prune_context': True,
            'cache_dir': '.cartographer_cache',
            'created': datetime.now().isoformat(),
            'description': f'Configuration for {name}'
        }
    
    def save_config(self, config: Dict[str, Any], config_name: str) -> str:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            config_name: Name of configuration (without .json)
        
        Returns:
            Path to saved configuration file
        """
        config_path = self.config_dir / f"{config_name}.json"
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved: {config_path}")
        return str(config_path)
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from file.
        
        Args:
            config_name: Name of configuration (without .json)
        
        Returns:
            Configuration dictionary or None if not found
        """
        config_path = self.config_dir / f"{config_name}.json"
        
        if not config_path.exists():
            print(f"❌ Configuration not found: {config_path}")
            return None
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def list_configs(self) -> List[str]:
        """List all available configurations."""
        configs = list(self.config_dir.glob('*.json'))
        return [c.stem for c in configs]
    
    def add_module_to_config(self, config_name: str, module_path: str, 
                            module_name: str = None, extensions: List[str] = None) -> bool:
        """
        Add a module to an existing configuration.
        
        Args:
            config_name: Name of configuration
            module_path: Path to module
            module_name: Display name for module
            extensions: File extensions to scan
        
        Returns:
            True if successful
        """
        config = self.load_config(config_name)
        if config is None:
            return False
        
        if module_name is None:
            module_name = Path(module_path).name
        
        if extensions is None:
            extensions = ['.py']
        
        # Check for duplicates
        for mod in config['modules']:
            if mod['path'] == module_path:
                print(f"⚠️  Module already in config: {module_path}")
                return False
        
        config['modules'].append({
            'path': module_path,
            'name': module_name,
            'extensions': extensions
        })
        
        self.save_config(config, config_name)
        return True
    
    def remove_module_from_config(self, config_name: str, module_path: str) -> bool:
        """
        Remove a module from configuration.
        
        Args:
            config_name: Name of configuration
            module_path: Path to module
        
        Returns:
            True if successful
        """
        config = self.load_config(config_name)
        if config is None:
            return False
        
        original_count = len(config['modules'])
        config['modules'] = [m for m in config['modules'] if m['path'] != module_path]
        
        if len(config['modules']) == original_count:
            print(f"⚠️  Module not found in config: {module_path}")
            return False
        
        self.save_config(config, config_name)
        return True
    
    def print_config(self, config_name: str):
        """Print configuration in human-readable format."""
        config = self.load_config(config_name)
        if config is None:
            return
        
        print(f"\nConfiguration: {config_name}")
        print("="*80)
        
        if 'description' in config:
            print(f"Description: {config['description']}")
        
        print(f"\nModules ({len(config['modules'])} total):")
        for i, mod in enumerate(config['modules'], 1):
            print(f"  {i}. {mod['name']}")
            print(f"     Path: {mod['path']}")
            print(f"     Extensions: {', '.join(mod['extensions'])}")
        
        print(f"\nSettings:")
        print(f"  Parallel workers: {config.get('parallel_workers', 4)}")
        print(f"  Force reindex: {config.get('force_reindex', False)}")
        print(f"  Extract business rules: {config.get('extract_business_rules', True)}")
        print(f"  Prune context: {config.get('prune_context', True)}")
        
        if 'created' in config:
            print(f"\nCreated: {config['created']}")


def setup_interactive_config():
    """Interactive configuration setup wizard."""
    print("\n" + "="*80)
    print("Configuration Setup Wizard")
    print("="*80)
    
    manager = ConfigManager()
    config_name = input("\nEnter configuration name (e.g., 'my-project'): ").strip()
    
    if config_name in manager.list_configs():
        use_existing = input(f"Configuration '{config_name}' already exists. Overwrite? (y/n): ").strip().lower()
        if use_existing != 'y':
            return
    
    modules = []
    
    while True:
        repo_path = input("\nEnter repository path (or 'done' to finish): ").strip()
        
        if repo_path.lower() == 'done':
            if not modules:
                print("❌ At least one module is required")
                continue
            break
        
        if not Path(repo_path).exists():
            print(f"❌ Path does not exist: {repo_path}")
            continue
        
        module_name = input(f"Enter display name for this module (default: {Path(repo_path).name}): ").strip()
        if not module_name:
            module_name = Path(repo_path).name
        
        extensions_input = input("Enter file extensions to scan (default: .py, separate with comma): ").strip()
        if extensions_input:
            extensions = [f".{ext.strip('.')}" for ext in extensions_input.split(',')]
        else:
            extensions = ['.py']
        
        modules.append({
            'path': repo_path,
            'name': module_name,
            'extensions': extensions
        })
        
        print(f"✅ Added: {module_name}")
    
    # Configure settings
    print("\n" + "="*80)
    print("Configure Settings")
    print("="*80)
    
    workers = input("Number of parallel workers (default: 4): ").strip()
    parallel_workers = int(workers) if workers else 4
    
    force_reindex = input("Force full reindex? (y/n, default: n): ").strip().lower() == 'y'
    extract_rules = input("Extract business rules? (y/n, default: y): ").strip().lower() != 'n'
    prune = input("Prune context? (y/n, default: y): ").strip().lower() != 'n'
    
    config = {
        'modules': modules,
        'parallel_workers': parallel_workers,
        'force_reindex': force_reindex,
        'extract_business_rules': extract_rules,
        'prune_context': prune,
        'cache_dir': '.cartographer_cache',
        'created': datetime.now().isoformat(),
        'description': f'Configuration with {len(modules)} module(s)'
    }
    
    # Save configuration
    manager.save_config(config, config_name)
    
    # Print summary
    print("\n" + "="*80)
    print("Configuration Created Successfully!")
    print("="*80)
    manager.print_config(config_name)
    
    print(f"\nTo use this configuration, run:")
    print(f"  python integrated_workflow.py {manager.config_dir / config_name}.json")


if __name__ == '__main__':
    import sys
    
    manager = ConfigManager()
    
    if len(sys.argv) < 2:
        setup_interactive_config()
    elif sys.argv[1] == 'list':
        configs = manager.list_configs()
        if configs:
            print(f"\nAvailable configurations ({len(configs)}):")
            for config in configs:
                manager.print_config(config)
        else:
            print("No configurations found")
    elif sys.argv[1] == 'show' and len(sys.argv) > 2:
        manager.print_config(sys.argv[2])
    elif sys.argv[1] == 'create' and len(sys.argv) > 2:
        # Create from repo path
        repo_path = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        config = manager.create_default_config(repo_path, name)
        config_name = name or Path(repo_path).name
        manager.save_config(config, config_name)
        manager.print_config(config_name)
    else:
        setup_interactive_config()
