"""
Advanced Caching Intelligence System

Implements intelligent file caching strategies based on:
1. Git history analysis - learn which files change together
2. Import patterns - pre-fetch related files
3. Change frequency - prioritize frequently-changed files
4. Module relationships - predict re-analysis needs
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import hashlib


class GitHistoryAnalyzer:
    """Analyzes git history to understand file change patterns."""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self._verify_git_repo()
    
    def _verify_git_repo(self):
        """Verify this is a git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_root,
                capture_output=True,
                timeout=5,
                check=True
            )
        except Exception as e:
            raise RuntimeError(f"{self.repo_root} is not a git repository: {e}")
    
    def get_file_commit_history(self, filepath: str, max_commits: int = 100) -> List[str]:
        """
        Get commit hashes that modified a specific file.
        
        Args:
            filepath: Path to file
            max_commits: Maximum number of commits to retrieve
        
        Returns:
            List of commit hashes in reverse chronological order
        """
        try:
            result = subprocess.run(
                ['git', 'log', '--follow', '--pretty=format:%H', '-n', str(max_commits), filepath],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return [c for c in result.stdout.strip().split('\n') if c]
            return []
        except Exception as e:
            print(f"Warning: Could not get commit history for {filepath}: {e}")
            return []
    
    def get_files_in_commit(self, commit_hash: str) -> Set[str]:
        """Get all files modified in a specific commit."""
        try:
            result = subprocess.run(
                ['git', 'show', '--name-only', '--pretty=format:', commit_hash],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return set(f for f in result.stdout.strip().split('\n') if f)
            return set()
        except Exception as e:
            print(f"Warning: Could not get files in commit {commit_hash}: {e}")
            return set()
    
    def find_cochanged_files(self, filepath: str, max_commits: int = 100, min_count: int = 2) -> Dict[str, int]:
        """
        Find files that frequently change together with the given file.
        
        Args:
            filepath: Reference file path
            max_commits: Number of commits to analyze
            min_count: Minimum co-change count to include
        
        Returns:
            Dictionary mapping file paths to co-change counts
        """
        commits = self.get_file_commit_history(filepath, max_commits)
        cochange_counts = Counter()
        
        for commit in commits:
            files_in_commit = self.get_files_in_commit(commit)
            files_in_commit.discard(filepath)  # Don't count the file with itself
            cochange_counts.update(files_in_commit)
        
        return {f: count for f, count in cochange_counts.items() if count >= min_count}
    
    def analyze_change_frequency(self, file_extensions: List[str] = None, days: int = 30) -> Dict[str, int]:
        """
        Analyze how frequently files change in the last N days.
        
        Args:
            file_extensions: Filter to specific extensions ('.py', '.java', etc.)
            days: Number of days to analyze
        
        Returns:
            Dictionary mapping file paths to change counts
        """
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            if file_extensions:
                # Build git format for multiple extensions
                pathspec = [f"'*.{ext.lstrip('.')}'" for ext in file_extensions]
                pathspec_str = ' -- ' + ' '.join(pathspec) if pathspec else ''
            else:
                pathspec_str = ''
            
            result = subprocess.run(
                f"git log --since='{since_date}' --name-only --pretty=format: {pathspec_str}",
                shell=True,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                frequency = Counter(f for f in result.stdout.strip().split('\n') if f)
                return dict(frequency)
            return {}
        except Exception as e:
            print(f"Warning: Could not analyze change frequency: {e}")
            return {}
    
    def find_hot_modules(self, file_extensions: List[str] = None, days: int = 30, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Find the most frequently-changed modules.
        
        Args:
            file_extensions: Filter to specific extensions
            days: Number of days to analyze
            top_n: Return top N modules
        
        Returns:
            List of (filepath, change_count) tuples sorted by frequency
        """
        frequency = self.analyze_change_frequency(file_extensions, days)
        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:top_n]


class DependencyGraphBuilder:
    """Builds dependency graphs from import patterns."""
    
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.import_cache = {}
    
    def extract_imports(self, filepath: str, language: str = 'python') -> Set[str]:
        """
        Extract imports from a source file.
        
        Args:
            filepath: Path to source file
            language: 'python' or 'java'
        
        Returns:
            Set of imported module/package names
        """
        if filepath in self.import_cache:
            return self.import_cache[filepath]
        
        imports = set()
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return imports
        
        if language == 'python':
            imports = self._extract_python_imports(content, filepath)
        elif language == 'java':
            imports = self._extract_java_imports(content, filepath)
        
        self.import_cache[filepath] = imports
        return imports
    
    def _extract_python_imports(self, content: str, filepath: str) -> Set[str]:
        """Extract Python imports."""
        imports = set()
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Handle 'import X' or 'from X import Y'
                if line.startswith('from '):
                    parts = line.split()
                    if len(parts) >= 2:
                        module = parts[1].split('.')[0]
                        imports.add(module)
                elif line.startswith('import '):
                    parts = line.split()
                    for part in parts[1:]:
                        if part and not part.startswith('#'):
                            module = part.split('.')[0].rstrip(',')
                            if module:
                                imports.add(module)
        
        return imports
    
    def _extract_java_imports(self, content: str, filepath: str) -> Set[str]:
        """Extract Java imports."""
        imports = set()
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import '):
                # Handle 'import package.Class;'
                import_stmt = line.replace('import ', '').rstrip(';')
                package = import_stmt.rsplit('.', 1)[0] if '.' in import_stmt else import_stmt
                imports.add(package)
        
        return imports
    
    def build_dependency_graph(self, files: List[str], language: str = 'python') -> Dict[str, Set[str]]:
        """
        Build a dependency graph for given files.
        
        Args:
            files: List of file paths
            language: 'python' or 'java'
        
        Returns:
            Dictionary mapping file paths to their dependencies
        """
        graph = {}
        for filepath in files:
            graph[filepath] = self.extract_imports(filepath, language)
        return graph
    
    def find_dependent_files(self, filepath: str, all_files: List[str], language: str = 'python') -> Set[str]:
        """
        Find all files that depend on the given file.
        
        Args:
            filepath: Target file path
            all_files: List of all files to search
            language: 'python' or 'java'
        
        Returns:
            Set of file paths that import the target file
        """
        target_module = self._get_module_name(filepath, language)
        dependents = set()
        
        for file in all_files:
            if file == filepath:
                continue
            imports = self.extract_imports(file, language)
            if target_module in imports:
                dependents.add(file)
        
        return dependents
    
    def find_related_files(self, filepath: str, all_files: List[str], language: str = 'python', depth: int = 2) -> Set[str]:
        """
        Find all files related to the given file (imports and dependents, recursively).
        
        Args:
            filepath: Target file path
            all_files: List of all files to search
            language: 'python' or 'java'
            depth: Recursion depth for finding related files
        
        Returns:
            Set of related file paths
        """
        related = set()
        to_process = {filepath}
        processed = set()
        
        for _ in range(depth):
            new_files = set()
            
            for file in to_process:
                if file in processed:
                    continue
                processed.add(file)
                
                # Find files this one imports
                imports = self.extract_imports(file, language)
                for other_file in all_files:
                    other_module = self._get_module_name(other_file, language)
                    if other_module in imports:
                        related.add(other_file)
                        new_files.add(other_file)
                
                # Find files that depend on this one
                dependents = self.find_dependent_files(file, all_files, language)
                related.update(dependents)
                new_files.update(dependents)
            
            to_process = new_files
            if not new_files:
                break
        
        return related
    
    def _get_module_name(self, filepath: str, language: str = 'python') -> str:
        """Extract module name from file path."""
        basename = os.path.basename(filepath)
        if language == 'python':
            return basename.replace('.py', '')
        elif language == 'java':
            return basename.replace('.java', '')
        return basename


class ChangePrioritizer:
    """Prioritizes files based on change frequency and impact."""
    
    def __init__(self, git_analyzer: GitHistoryAnalyzer, dependency_graph: Dict[str, Set[str]]):
        self.git_analyzer = git_analyzer
        self.dependency_graph = dependency_graph
    
    def calculate_change_score(self, filepath: str, frequency_data: Dict[str, int], days: int = 30) -> float:
        """
        Calculate priority score for a file based on change frequency.
        
        Score = base_frequency + (1.0 if changed_in_last_N_days else 0.0)
        
        Args:
            filepath: File path
            frequency_data: Dictionary from analyze_change_frequency
            days: Days to consider as "recent"
        
        Returns:
            Priority score (higher = more important)
        """
        frequency = frequency_data.get(filepath, 0)
        cochanges = len(self.dependency_graph.get(filepath, set()))
        
        # Frequency has more weight than dependency count
        score = frequency * 2.0 + cochanges * 0.5
        return score
    
    def calculate_impact_score(self, filepath: str, num_dependents: int) -> float:
        """
        Calculate impact score based on how many files depend on this one.
        
        Args:
            filepath: File path
            num_dependents: Number of files that depend on this file
        
        Returns:
            Impact score (higher = more impact if changed)
        """
        return min(num_dependents * 1.5, 10.0)  # Cap at 10.0
    
    def prioritize_files(self, files: List[str], frequency_data: Dict[str, int]) -> List[Tuple[str, float]]:
        """
        Prioritize files for re-analysis based on change history.
        
        Args:
            files: List of file paths
            frequency_data: Dictionary from analyze_change_frequency
        
        Returns:
            List of (filepath, priority_score) tuples sorted by priority
        """
        prioritized = []
        
        for filepath in files:
            change_score = self.calculate_change_score(filepath, frequency_data)
            num_dependents = sum(1 for deps in self.dependency_graph.values() if filepath in deps)
            impact_score = self.calculate_impact_score(filepath, num_dependents)
            
            total_score = change_score + impact_score
            prioritized.append((filepath, total_score))
        
        return sorted(prioritized, key=lambda x: x[1], reverse=True)


class SmartCachePredictor:
    """Predicts which files need analysis based on multiple signals."""
    
    def __init__(self, repo_root: str, cache_dir: str = ".cartographer_cache"):
        self.repo_root = repo_root
        self.cache_dir = os.path.join(repo_root, cache_dir)
        self.intelligence_file = os.path.join(self.cache_dir, "cache_intelligence.json")
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.git_analyzer = GitHistoryAnalyzer(repo_root)
        self.dependency_builder = DependencyGraphBuilder(repo_root)
        self.intelligence_data = self._load_intelligence_data()
    
    def _load_intelligence_data(self) -> Dict:
        """Load previously saved intelligence data."""
        if os.path.exists(self.intelligence_file):
            try:
                with open(self.intelligence_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load intelligence data: {e}")
        
        return {
            'cochange_patterns': {},
            'frequency_data': {},
            'dependency_graph': {},
            'last_analyzed': None
        }
    
    def _save_intelligence_data(self):
        """Save intelligence data for future use."""
        try:
            with open(self.intelligence_file, 'w') as f:
                json.dump(self.intelligence_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save intelligence data: {e}")
    
    def analyze_patterns(self, files: List[str], file_extensions: List[str] = None, language: str = 'python') -> Dict:
        """
        Analyze all patterns and store intelligence data.
        
        Args:
            files: List of file paths to analyze
            file_extensions: Extensions to analyze for change frequency
            language: 'python' or 'java'
        
        Returns:
            Dictionary with analysis results
        """
        print(f"Analyzing change patterns for {len(files)} files...")
        
        # Build dependency graph
        dependency_graph = self.dependency_builder.build_dependency_graph(files, language)
        
        # Analyze change frequency
        frequency_data = self.git_analyzer.analyze_change_frequency(file_extensions, days=30)
        
        # Find co-change patterns
        cochange_patterns = {}
        for filepath in files[:10]:  # Analyze top 10 files for performance
            cochanges = self.git_analyzer.find_cochanged_files(filepath, max_commits=50, min_count=1)
            if cochanges:
                cochange_patterns[filepath] = cochanges
        
        # Store in cache
        self.intelligence_data['cochange_patterns'] = cochange_patterns
        self.intelligence_data['frequency_data'] = frequency_data
        self.intelligence_data['dependency_graph'] = {
            k: list(v) for k, v in dependency_graph.items()
        }
        self.intelligence_data['last_analyzed'] = datetime.now().isoformat()
        
        self._save_intelligence_data()
        
        return {
            'files_analyzed': len(files),
            'cochange_patterns_found': len(cochange_patterns),
            'frequently_changed_files': len(frequency_data),
            'total_dependencies': sum(len(deps) for deps in dependency_graph.values())
        }
    
    def predict_needed_analyses(self, changed_files: List[str], all_files: List[str], language: str = 'python') -> Dict[str, List[Tuple[str, float]]]:
        """
        Predict which files need analysis based on changed files.
        
        Args:
            changed_files: Files that were recently changed
            all_files: All source files in the repo
            language: 'python' or 'java'
        
        Returns:
            Dictionary with different categories of predicted changes
        """
        predictions = {
            'direct_changes': [],
            'dependent_files': [],
            'cochange_files': [],
            'hotspot_files': []
        }
        
        # 1. Direct changes - files that changed
        frequency_data = self.intelligence_data.get('frequency_data', {})
        prioritizer = ChangePrioritizer(
            self.git_analyzer,
            self.intelligence_data.get('dependency_graph', {})
        )
        
        direct_scores = prioritizer.prioritize_files(changed_files, frequency_data)
        predictions['direct_changes'] = direct_scores
        
        # 2. Find dependent files
        dependent_set = set()
        for changed_file in changed_files:
            dependents = self.dependency_builder.find_dependent_files(changed_file, all_files, language)
            dependent_set.update(dependents)
        
        dependent_scores = prioritizer.prioritize_files(list(dependent_set), frequency_data)
        predictions['dependent_files'] = dependent_scores
        
        # 3. Find co-change files
        cochange_set = set()
        cochange_patterns = self.intelligence_data.get('cochange_patterns', {})
        for changed_file in changed_files:
            if changed_file in cochange_patterns:
                cochange_set.update(cochange_patterns[changed_file].keys())
        
        cochange_scores = prioritizer.prioritize_files(list(cochange_set), frequency_data)
        predictions['cochange_files'] = cochange_scores
        
        # 4. Find hotspot files (frequently changed)
        trend = self.git_analyzer.find_hot_modules(days=7, top_n=10)
        hotspot_files = [f for f, _ in trend if f in all_files]
        hotspot_scores = prioritizer.prioritize_files(hotspot_files, frequency_data)
        predictions['hotspot_files'] = hotspot_scores
        
        return predictions
    
    def prefetch_related_files(self, changed_files: List[str], all_files: List[str], language: str = 'python', depth: int = 2) -> Set[str]:
        """
        Pre-fetch files that should be analyzed together with changed files.
        
        Args:
            changed_files: Files that were changed
            all_files: All source files
            language: 'python' or 'java'
            depth: Relationship depth to traverse
        
        Returns:
            Set of file paths to pre-fetch
        """
        prefetch = set()
        
        for changed_file in changed_files:
            # Get related files
            related = self.dependency_builder.find_related_files(changed_file, all_files, language, depth)
            prefetch.update(related)
            
            # Get co-changed files
            cochanges = self.git_analyzer.find_cochanged_files(changed_file, max_commits=50, min_count=2)
            for cochange_file in cochanges.keys():
                full_path = os.path.join(self.repo_root, cochange_file)
                if os.path.exists(full_path):
                    prefetch.add(full_path)
        
        return prefetch
    
    def get_analysis_plan(self, changed_files: List[str], all_files: List[str], language: str = 'python') -> Dict:
        """
        Generate a complete analysis plan based on changed files.
        
        Args:
            changed_files: Files that changed
            all_files: All files in repo
            language: 'python' or 'java'
        
        Returns:
            Dictionary with analysis plan and prioritization
        """
        predictions = self.predict_needed_analyses(changed_files, all_files, language)
        prefetch = self.prefetch_related_files(changed_files, all_files, language)
        
        # Combine all predictions into a single prioritized list
        all_predicted = set()
        for category in predictions.values():
            all_predicted.update(f for f, _ in category)
        
        # Remove duplicates and create final priority list
        unique_predictions = {}
        for category, files in predictions.items():
            for filepath, score in files:
                if filepath not in unique_predictions:
                    unique_predictions[filepath] = {'scores': {}, 'categories': []}
                unique_predictions[filepath]['scores'][category] = score
                unique_predictions[filepath]['categories'].append(category)
        
        # Calculate combined score
        final_list = []
        for filepath, data in unique_predictions.items():
            combined_score = sum(data['scores'].values())
            final_list.append((filepath, combined_score, data['categories']))
        
        final_list.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'changed_files': changed_files,
            'predicted_analyses': final_list,
            'prefetch_candidates': list(prefetch),
            'total_files_to_analyze': len(final_list),
            'total_prefetch': len(prefetch),
            'analysis_priority_breakdown': predictions
        }


class CacheIntelligenceManager:
    """High-level manager for intelligent caching."""
    
    def __init__(self, repo_root: str, cache_dir: str = ".cartographer_cache"):
        self.repo_root = repo_root
        self.cache_dir = cache_dir
        self.predictor = SmartCachePredictor(repo_root, cache_dir)
    
    def initialize_intelligence(self, files: List[str], file_extensions: List[str] = None, language: str = 'python') -> Dict:
        """
        Initialize intelligence system by analyzing existing patterns.
        
        Args:
            files: Files to analyze
            file_extensions: Extensions to consider
            language: 'python' or 'java'
        
        Returns:
            Initialization results
        """
        return self.predictor.analyze_patterns(files, file_extensions, language)
    
    def get_smart_analysis_plan(self, changed_files: List[str], all_files: List[str], language: str = 'python') -> Dict:
        """
        Get a smart analysis plan based on changes.
        
        Args:
            changed_files: Recently changed files
            all_files: All files in repo
            language: 'python' or 'java'
        
        Returns:
            Analysis plan with priorities
        """
        return self.predictor.get_analysis_plan(changed_files, all_files, language)
    
    def get_status(self) -> Dict:
        """Get status of intelligence system."""
        intelligence_data = self.predictor.intelligence_data
        
        return {
            'initialized': intelligence_data.get('last_analyzed') is not None,
            'last_analyzed': intelligence_data.get('last_analyzed'),
            'cochange_patterns': len(intelligence_data.get('cochange_patterns', {})),
            'frequency_data_points': len(intelligence_data.get('frequency_data', {})),
            'known_dependencies': len(intelligence_data.get('dependency_graph', {}))
        }


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cache_intelligence.py <repo_path> [command]")
        print("Commands:")
        print("  initialize                    Initialize intelligence system")
        print("  analyze <file> <all_files>   Analyze impact of file changes")
        print("  hotspots                     Find hot modules")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else 'initialize'
    
    try:
        manager = CacheIntelligenceManager(repo_path)
        
        if command == 'initialize':
            # Find all Python files
            all_files = []
            for root, _, files in os.walk(repo_path):
                for f in files:
                    if f.endswith('.py'):
                        all_files.append(os.path.join(root, f))
            
            print(f"Initializing intelligence for {len(all_files)} files...")
            result = manager.initialize_intelligence(all_files[:100])  # Limit for demo
            print(json.dumps(result, indent=2))
        
        elif command == 'analyze':
            # Demo: analyze what needs re-analysis
            all_files = []
            for root, _, files in os.walk(repo_path):
                for f in files:
                    if f.endswith('.py'):
                        all_files.append(os.path.join(root, f))
            
            # Simulate some changed files
            changed = all_files[:3] if len(all_files) > 3 else all_files
            print(f"Analyzing impact of {len(changed)} changed files...")
            
            plan = manager.get_smart_analysis_plan(changed, all_files)
            print(f"\nAnalysis Plan Summary:")
            print(f"  Files to analyze: {plan['total_files_to_analyze']}")
            print(f"  Files to prefetch: {plan['total_prefetch']}")
            print(f"\nTop priority files:")
            for filepath, score, categories in plan['predicted_analyses'][:5]:
                print(f"  {os.path.basename(filepath)}: {score:.1f} ({', '.join(categories)})")
        
        elif command == 'hotspots':
            git_analyzer = GitHistoryAnalyzer(repo_path)
            hotspots = git_analyzer.find_hot_modules(days=30, top_n=10)
            print(f"Hot modules (last 30 days):")
            for filepath, count in hotspots:
                print(f"  {filepath}: {count} changes")
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
