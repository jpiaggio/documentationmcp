"""
Enhanced Cartographer Agent with Caching Intelligence

Integrates intelligent caching to dramatically improve performance:
- Pre-fetches related files based on import patterns
- Prioritizes frequently-changed files
- Learns from git history which files change together
- Predicts which modules need re-analysis
"""

import os
import sys
import json
import concurrent.futures
from functools import partial
from typing import List, Dict, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from cartographer_agent import process_module, parse_code, extract_functions_and_classes, extract_imports
from cache_intelligence import CacheIntelligenceManager
from incremental_indexer import IncrementalIndexer


class SmartCartographerAgent:
    """
    Enhanced cartographer agent with intelligent caching.
    
    Features:
    1. Analyzes git history to find file co-change patterns
    2. Pre-fetches related files based on import dependencies
    3. Prioritizes frequently-changed modules
    4. Predicts which files need re-analysis
    """
    
    def __init__(self, repo_root: str, cache_dir: str = ".cartographer_cache"):
        self.repo_root = repo_root
        self.cache_dir = cache_dir
        self.incremental_indexer = IncrementalIndexer(repo_root, cache_dir)
        self.cache_manager = CacheIntelligenceManager(repo_root, cache_dir)
    
    def get_files_to_analyze(self, file_extensions: List[str] = None, force_reindex: bool = False, use_intelligence: bool = True) -> Tuple[List[str], Dict]:
        """
        Get the list of files to analyze using intelligent caching.
        
        Args:
            file_extensions: Extensions to analyze ('.py', '.java', etc.)
            force_reindex: If True, ignore cache and analyze all files
            use_intelligence: If True, use predictive caching based on git history
        
        Returns:
            Tuple of (files_to_analyze, analysis_metadata)
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        # Get files from incremental indexer
        files_to_analyze, incremental_stats = self.incremental_indexer.get_files_to_process(
            file_extensions=file_extensions,
            force_reindex=force_reindex
        )
        
        if not use_intelligence or incremental_stats['mode'] == 'full_reindex':
            # Return directly from incremental indexer
            return files_to_analyze, {
                'incremental_stats': incremental_stats,
                'intelligence_used': False
            }
        
        # Get all files for intelligence analysis
        all_files = self.incremental_indexer._get_all_files(file_extensions)
        
        # Use cache intelligence to predict related files
        # This helps pre-fetch files that might be affected by the changes
        metadata = {
            'incremental_stats': incremental_stats,
            'intelligence_used': True,
            'predicted_analyses': {}
        }
        
        if files_to_analyze and incremental_stats['mode'] in ['incremental_index', 'partial_index']:
            # Get smart analysis plan
            language = 'java' if '.java' in file_extensions else 'python'
            analysis_plan = self.cache_manager.get_smart_analysis_plan(
                files_to_analyze,
                all_files,
                language
            )
            
            # Extract prioritized files from the analysis plan
            predicted = analysis_plan.get('predicted_analyses', [])
            
            # Convert from (filepath, score, categories) to files we should analyze
            # Keep direct changes + high-priority dependent files
            additional_files = []
            for filepath, score, categories in predicted:
                if filepath not in files_to_analyze:
                    # Include if it's in direct_changes category or score is high
                    if 'direct_changes' in categories or score > 5.0:
                        additional_files.append(filepath)
            
            # Add related files for pre-fetching (but don't queue for analysis yet)
            prefetch_files = analysis_plan.get('prefetch_candidates', [])
            
            files_to_analyze = list(set(files_to_analyze + additional_files))
            
            metadata['predicted_analyses'] = {
                'total_predicted': len(predicted),
                'added_to_queue': len(additional_files),
                'prefetch_candidates': len(prefetch_files),
                'top_priorities': [
                    {'file': os.path.basename(f), 'score': s, 'reason': ', '.join(c)}
                    for f, s, c in predicted[:5]
                ]
            }
        
        return files_to_analyze, metadata
    
    def analyze_with_intelligence(self, repo_root: str, file_extensions: List[str] = None, 
                                 max_workers: int = 8, use_business_rules: bool = True,
                                 use_intelligence: bool = True, force_reindex: bool = False) -> Dict:
        """
        Analyze repository with intelligent caching.
        
        Args:
            repo_root: Path to repository root
            file_extensions: Extensions to scan for
            max_workers: Number of parallel workers
            use_business_rules: Extract business insights or technical analysis
            use_intelligence: Use predictive caching based on git history
            force_reindex: Force re-analysis of all files
        
        Returns:
            Dictionary with analysis results and metrics
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        # Convert single extension string to list
        if isinstance(file_extensions, str):
            file_extensions = [file_extensions]
        
        # Initialize intelligence on first run
        cache_status = self.cache_manager.get_status()
        if not cache_status['initialized'] and not force_reindex:
            print("Initializing cache intelligence system...", file=sys.stderr)
            all_files = self.incremental_indexer._get_all_files(file_extensions)
            language = 'java' if '.java' in file_extensions else 'python'
            self.cache_manager.initialize_intelligence(all_files, file_extensions, language)
        
        # Get files to analyze
        files_to_analyze, analysis_metadata = self.get_files_to_analyze(
            file_extensions=file_extensions,
            force_reindex=force_reindex,
            use_intelligence=use_intelligence
        )
        
        print(f"Analysis Plan:", file=sys.stderr)
        print(f"  Files to analyze: {len(files_to_analyze)}", file=sys.stderr)
        if analysis_metadata.get('intelligence_used'):
            print(f"  Predicted impacts: {analysis_metadata['predicted_analyses'].get('total_predicted', 'N/A')}", file=sys.stderr)
            if analysis_metadata['predicted_analyses'].get('top_priorities'):
                print(f"  Top priorities:", file=sys.stderr)
                for item in analysis_metadata['predicted_analyses']['top_priorities'][:3]:
                    print(f"    - {item['file']}: {item['reason']}", file=sys.stderr)
        
        # Analyze files
        cypher_queries = []
        language = 'java' if '.java' in file_extensions else 'python'
        
        if files_to_analyze:
            print(f"Analyzing {len(files_to_analyze)} files with {max_workers} workers...", file=sys.stderr)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                tasks = [
                    partial(process_module, path, language, use_business_rules) 
                    for path in files_to_analyze
                ]
                results = list(executor.map(lambda task: task(), tasks))
                for cypher_list in results:
                    cypher_queries.extend(cypher_list)
            
            # Mark files as processed
            self.incremental_indexer.mark_files_processed(files_to_analyze)
        
        return {
            'cypher_queries': cypher_queries,
            'statistics': {
                'files_analyzed': len(files_to_analyze),
                'queries_generated': len(cypher_queries),
                'cache_status': cache_status,
                'analysis_metadata': analysis_metadata
            }
        }
    
    def get_analysis_report(self) -> Dict:
        """Get a detailed report on current cache intelligence status."""
        stats = self.incremental_indexer.get_stats()
        cache_status = self.cache_manager.get_status()
        
        return {
            'incremental_indexing': stats,
            'cache_intelligence': cache_status,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    
    def prefetch_dependencies(self, changed_files: List[str], all_files: List[str], 
                            language: str = 'python', prefetch_depth: int = 2) -> List[str]:
        """
        Pre-fetch files that should be loaded into memory due to dependencies.
        
        Args:
            changed_files: Files that changed
            all_files: All source files
            language: 'python' or 'java'
            prefetch_depth: How deep to traverse relationships
        
        Returns:
            List of files to prefetch
        """
        prefetch = self.cache_manager.predictor.prefetch_related_files(
            changed_files, all_files, language, prefetch_depth
        )
        return list(prefetch)


def smart_cartographer_agent(repo_root: str, file_extensions: str = '.py', max_workers: int = 8,
                            use_business_rules: bool = True, use_intelligence: bool = True) -> List[str]:
    """
    Enhanced cartographer agent with intelligent caching.
    
    Args:
        repo_root: Path to repository root
        file_extensions: Extensions to scan for ('.py', '.java', '.py,.java')
        max_workers: Number of parallel workers
        use_business_rules: Extract business insights or technical analysis
        use_intelligence: Use cache intelligence
    
    Returns:
        List of Cypher queries
    """
    # Handle multiple extensions
    if ',' in file_extensions:
        extensions = [ext.strip() for ext in file_extensions.split(',')]
    else:
        extensions = [file_extensions]
    
    agent = SmartCartographerAgent(repo_root)
    result = agent.analyze_with_intelligence(
        repo_root,
        file_extensions=extensions,
        max_workers=max_workers,
        use_business_rules=use_business_rules,
        use_intelligence=use_intelligence
    )
    
    return result['cypher_queries']


# Main execution
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python smart_cartographer.py <repo_path> [options]", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  --no-intelligence    Disable cache intelligence", file=sys.stderr)
        print("  --force-reindex      Force full re-analysis", file=sys.stderr)
        print("  --technical          Use technical analysis instead of business rules", file=sys.stderr)
        print("  --report             Show analysis report instead of running analysis", file=sys.stderr)
        sys.exit(1)
    
    repo_path = sys.argv[1]
    use_intelligence = '--no-intelligence' not in sys.argv
    force_reindex = '--force-reindex' in sys.argv
    use_business = '--technical' not in sys.argv
    show_report = '--report' in sys.argv
    
    print(f"Smart Cartographer Agent", file=sys.stderr)
    print(f"Repo: {repo_path}", file=sys.stderr)
    print(f"Cache Intelligence: {'Enabled' if use_intelligence else 'Disabled'}", file=sys.stderr)
    
    try:
        agent = SmartCartographerAgent(repo_path)
        
        if show_report:
            report = agent.get_analysis_report()
            print(json.dumps(report, indent=2))
        else:
            result = agent.analyze_with_intelligence(
                repo_path,
                file_extensions=['.py'],
                use_business_rules=use_business,
                use_intelligence=use_intelligence,
                force_reindex=force_reindex
            )
            
            queries = result['cypher_queries']
            stats = result['statistics']
            
            print(f"Generated {len(queries)} insights", file=sys.stderr)
            print(json.dumps(stats, indent=2), file=sys.stderr)
            
            # Output Cypher queries
            for query in queries:
                print(query)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
