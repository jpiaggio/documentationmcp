"""
Incremental Indexing System for Multi-Module Processing

Implements smart file tracking to avoid re-processing unchanged files.
This dramatically reduces API costs and processing time for large repos.
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


class IncrementalIndexer:
    """
    Tracks which files have changed and only processes new/modified files.
    
    Uses git history to efficiently determine what needs re-indexing:
    - First run: Indexes all files
    - Subsequent runs: Only indexes changed files since last run
    - Supports multiple commits/branches
    """
    
    def __init__(self, repo_root: str, cache_dir: str = ".cartographer_cache"):
        """
        Initialize the incremental indexer.
        
        Args:
            repo_root: Path to repository root
            cache_dir: Directory to store indexing metadata
        """
        self.repo_root = repo_root
        self.cache_dir = os.path.join(repo_root, cache_dir)
        self.metadata_file = os.path.join(self.cache_dir, "index_metadata.json")
        self.file_hashes_file = os.path.join(self.cache_dir, "file_hashes.json")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.metadata = self._load_metadata()
        self.file_hashes = self._load_file_hashes()
    
    def _load_metadata(self) -> Dict:
        """Load indexing metadata from cache."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
        return {
            'last_indexed': None,
            'last_commit': None,
            'total_files_processed': 0,
            'indexed_extensions': []
        }
    
    def _load_file_hashes(self) -> Dict[str, str]:
        """Load file hashes from cache."""
        if os.path.exists(self.file_hashes_file):
            try:
                with open(self.file_hashes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load file hashes: {e}")
        return {}
    
    def _save_metadata(self):
        """Save indexing metadata to cache."""
        self.metadata['last_indexed'] = datetime.now().isoformat()
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def _save_file_hashes(self):
        """Save file hashes to cache."""
        try:
            with open(self.file_hashes_file, 'w') as f:
                json.dump(self.file_hashes, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save file hashes: {e}")
    
    def _compute_file_hash(self, filepath: str) -> str:
        """Compute MD5 hash of file contents."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _get_git_changed_files(self, since_commit: str = None) -> Set[str]:
        """
        Get list of changed files from git history.
        
        Args:
            since_commit: Get files changed since this commit. If None, uses last indexed commit.
        
        Returns:
            Set of relative paths to changed files
        """
        try:
            if since_commit is None:
                since_commit = self.metadata.get('last_commit')
            
            if since_commit is None:
                # First run: return all files
                return set()
            
            # Get files changed between commits
            result = subprocess.run(
                ['git', 'diff', '--name-only', f"{since_commit}..HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return set(result.stdout.strip().split('\n')) - {''}
            return set()
        except Exception as e:
            print(f"Warning: Could not get git changed files: {e}")
            return set()
    
    def _get_current_commit(self) -> str:
        """Get current HEAD commit hash."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"Warning: Could not get current commit: {e}")
        return None
    
    def get_files_to_process(
        self,
        file_extensions: List[str] = None,
        force_reindex: bool = False
    ) -> Tuple[List[str], Dict[str, str]]:
        """
        Get list of files that need processing.
        
        Args:
            file_extensions: List of extensions to scan ('.py', '.java', etc.)
            force_reindex: If True, ignore cache and process all files
        
        Returns:
            Tuple of (list of file paths, metadata dict with statistics)
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        if force_reindex:
            return self._get_all_files(file_extensions), {
                'mode': 'full_reindex',
                'reason': 'Force reindex requested'
            }
        
        # Check if we can use git history
        current_commit = self._get_current_commit()
        is_git_repo = current_commit is not None
        
        if not is_git_repo or self.metadata.get('last_commit') is None:
            # First run or not a git repo: process all files
            all_files = self._get_all_files(file_extensions)
            self.metadata['last_commit'] = current_commit
            self.metadata['indexed_extensions'] = file_extensions
            self._save_metadata()
            
            return all_files, {
                'mode': 'full_index_initial',
                'reason': 'First run or not a git repository',
                'total_files': len(all_files)
            }
        
        # Get changed files from git
        changed_files = self._get_git_changed_files()
        
        if not changed_files:
            # Nothing changed
            return [], {
                'mode': 'no_changes',
                'reason': 'No files changed since last index',
                'last_indexed': self.metadata.get('last_indexed'),
                'last_commit': self.metadata.get('last_commit')
            }
        
        # Filter changed files by extension
        relevant_changes = [
            os.path.join(self.repo_root, f) for f in changed_files
            if any(f.endswith(ext) for ext in file_extensions)
        ]
        
        # Also check for changed files using hash comparison (for non-git repos)
        files_missing_hash = self._get_files_missing_hash(
            self._get_all_files(file_extensions),
            relevant_changes
        )
        
        all_files_to_process = list(set(relevant_changes + files_missing_hash))
        
        self.metadata['last_commit'] = current_commit
        self._save_metadata()
        
        return all_files_to_process, {
            'mode': 'incremental_index',
            'reason': f'Processing changed files',
            'total_changed': len(relevant_changes),
            'new_files': len(files_missing_hash),
            'total_files_to_process': len(all_files_to_process)
        }
    
    def _get_all_files(self, extensions: List[str]) -> List[str]:
        """Get all files matching extensions in repo."""
        files = []
        for root, _, filenames in os.walk(self.repo_root):
            # Skip cache directory itself
            if self.cache_dir in root:
                continue
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
        return files
    
    def _get_files_missing_hash(self, all_files: List[str], excluded_files: List[str] = None) -> List[str]:
        """Get files that don't have a hash in cache (new files)."""
        if excluded_files is None:
            excluded_files = []
        
        excluded_set = set(excluded_files)
        missing_hash = []
        
        for filepath in all_files:
            if filepath not in excluded_set:
                relative_path = os.path.relpath(filepath, self.repo_root)
                if relative_path not in self.file_hashes:
                    missing_hash.append(filepath)
        
        return missing_hash
    
    def mark_files_processed(self, files: List[str]):
        """
        Update hashes for processed files.
        
        Args:
            files: List of file paths that were processed
        """
        for filepath in files:
            relative_path = os.path.relpath(filepath, self.repo_root)
            file_hash = self._compute_file_hash(filepath)
            if file_hash:
                self.file_hashes[relative_path] = file_hash
        
        self._save_file_hashes()
    
    def get_stats(self) -> Dict:
        """Get indexing statistics."""
        return {
            'cache_directory': self.cache_dir,
            'cached_files': len(self.file_hashes),
            'last_indexed': self.metadata.get('last_indexed'),
            'last_commit': self.metadata.get('last_commit'),
            'total_files_processed': self.metadata.get('total_files_processed', 0),
            'indexed_extensions': self.metadata.get('indexed_extensions', [])
        }
    
    def clear_cache(self):
        """Clear the indexing cache (forces full reindex on next run)."""
        try:
            import shutil
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)
            self.metadata = {}
            self.file_hashes = {}
            print(f"Cache cleared: {self.cache_dir}")
        except Exception as e:
            print(f"Warning: Could not clear cache: {e}")
