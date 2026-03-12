"""
Unified Multi-Language Analyzer for the Cartographer system.

Orchestrates analysis across multiple programming languages:
- Python (via existing integration)
- Java (via existing integration)
- JavaScript/TypeScript (NEW)
- Go (NEW)
- C#/.NET (NEW)

Provides:
- Automatic language detection
- Polyglot codebase analysis
- Cross-language dependency detection
- Unified entity graph construction
- Multi-language business rule extraction
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import language-specific analyzers
try:
    from javascript_typescript_analyzer import JavaScriptTypeScriptAnalyzer, HAS_JS_SUPPORT
except ImportError:
    HAS_JS_SUPPORT = False
    JavaScriptTypeScriptAnalyzer = None

try:
    from go_analyzer import GoAnalyzer, HAS_GO_SUPPORT
except ImportError:
    HAS_GO_SUPPORT = False
    GoAnalyzer = None

try:
    from csharp_analyzer import CSharpAnalyzer, HAS_CSHARP_SUPPORT
except ImportError:
    HAS_CSHARP_SUPPORT = False
    CSharpAnalyzer = None


class MultiLanguageAnalyzer:
    """
    Unified analyzer supporting multiple programming languages.
    
    Automatically detects language based on file extension and routes
    to the appropriate language-specific analyzer.
    """

    # File extension to language mapping
    LANGUAGE_MAP = {
        # Python
        '.py': 'python',
        # Java
        '.java': 'java',
        # JavaScript
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.mjs': 'javascript',
        # TypeScript
        '.ts': 'typescript',
        '.tsx': 'typescript',
        # Go
        '.go': 'go',
        # C#
        '.cs': 'csharp',
    }

    # Language support status
    SUPPORTED_LANGUAGES = {
        'python': True,  # Existing support
        'java': True,     # Existing support
        'javascript': HAS_JS_SUPPORT,
        'typescript': HAS_JS_SUPPORT,
        'go': HAS_GO_SUPPORT,
        'csharp': HAS_CSHARP_SUPPORT,
    }

    def __init__(self):
        """Initialize multi-language analyzer."""
        self.analyzed_files: Dict[str, Dict[str, Any]] = {}
        self.cross_language_dependencies: List[Dict[str, Any]] = []
        self.analyzers = self._init_analyzers()

    def _init_analyzers(self) -> Dict[str, Any]:
        """Initialize language-specific analyzers."""
        analyzers = {}

        # Python and Java are handled separately (existing implementation)
        # but we prepare for future integration

        if HAS_JS_SUPPORT:
            try:
                analyzers['javascript'] = JavaScriptTypeScriptAnalyzer()
                analyzers['typescript'] = analyzers['javascript']  # Same analyzer
            except Exception as e:
                print(f"Warning: Could not initialize JavaScript analyzer: {e}", file=sys.stderr)

        if HAS_GO_SUPPORT:
            try:
                analyzers['go'] = GoAnalyzer()
            except Exception as e:
                print(f"Warning: Could not initialize Go analyzer: {e}", file=sys.stderr)

        if HAS_CSHARP_SUPPORT:
            try:
                analyzers['csharp'] = CSharpAnalyzer()
            except Exception as e:
                print(f"Warning: Could not initialize C# analyzer: {e}", file=sys.stderr)

        return analyzers

    def detect_language(self, filepath: str) -> Optional[str]:
        """
        Detect the programming language from file extension.

        Args:
            filepath: Path to the file

        Returns:
            Language name or None if unknown
        """
        ext = Path(filepath).suffix.lower()
        return self.LANGUAGE_MAP.get(ext)

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported in this installation."""
        return self.SUPPORTED_LANGUAGES.get(language, False)

    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a single file with automatic language detection.

        Args:
            filepath: Path to the file to analyze

        Returns:
            Analysis results with language metadata
        """
        language = self.detect_language(filepath)

        if not language:
            return {
                "filepath": filepath,
                "language": "unknown",
                "error": f"Unknown file type: {Path(filepath).suffix}",
            }

        if not self.is_language_supported(language):
            return {
                "filepath": filepath,
                "language": language,
                "error": f"Language not supported in this installation: {language}",
                "supported_languages": list(self.SUPPORTED_LANGUAGES.keys()),
            }

        try:
            # Route to appropriate analyzer
            if language in ('javascript', 'typescript'):
                analyzer = self.analyzers.get('javascript')
                if analyzer:
                    result = analyzer.analyze_file(filepath)
                else:
                    return {"filepath": filepath, "error": "JavaScript analyzer not available"}

            elif language == 'go':
                analyzer = self.analyzers.get('go')
                if analyzer:
                    result = analyzer.analyze_file(filepath)
                else:
                    return {"filepath": filepath, "error": "Go analyzer not available"}

            elif language == 'csharp':
                analyzer = self.analyzers.get('csharp')
                if analyzer:
                    result = analyzer.analyze_file(filepath)
                else:
                    return {"filepath": filepath, "error": "C# analyzer not available"}

            else:
                return {"filepath": filepath, "error": f"No analyzer for language: {language}"}

            # Store in cache
            self.analyzed_files[filepath] = result
            return result

        except Exception as e:
            return {
                "filepath": filepath,
                "language": language,
                "error": str(e),
            }

    def analyze_directory(self, directory: str, max_workers: int = 4) -> Dict[str, Any]:
        """
        Recursively analyze all code files in a directory.

        Args:
            directory: Root directory to analyze
            max_workers: Number of parallel worker threads

        Returns:
            Comprehensive analysis results across all files
        """
        # Find all source files
        source_files = self._find_source_files(directory)

        results_by_language = defaultdict(list)
        errors = []

        # Analyze files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.analyze_file, filepath): filepath
                for filepath in source_files
            }

            for future in as_completed(futures):
                filepath = futures[future]
                try:
                    result = future.result()
                    language = result.get('language', 'unknown')
                    if 'error' not in result:
                        results_by_language[language].append(result)
                    else:
                        errors.append({
                            'filepath': filepath,
                            'error': result.get('error'),
                        })
                except Exception as e:
                    errors.append({
                        'filepath': filepath,
                        'error': str(e),
                    })

        # Build cross-language dependency graph
        self._build_cross_language_dependencies(results_by_language)

        # Aggregate statistics
        statistics = self._aggregate_statistics(results_by_language)

        return {
            "directory": directory,
            "total_files_analyzed": len(self.analyzed_files),
            "files_by_language": {lang: len(files) for lang, files in results_by_language.items()},
            "results": dict(results_by_language),
            "cross_language_dependencies": self.cross_language_dependencies,
            "errors": errors,
            "statistics": statistics,
        }

    def _find_source_files(self, directory: str) -> List[str]:
        """Find all supported source files in a directory."""
        source_files = []
        supported_extensions = set(self.LANGUAGE_MAP.keys())

        for root, dirs, files in os.walk(directory):
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in (
                '.git', '.svn', 'node_modules', '__pycache__', '.venv',
                '.env', 'dist', 'build', 'target', 'bin', 'obj'
            )]

            for file in files:
                file_path = os.path.join(root, file)
                if Path(file_path).suffix.lower() in supported_extensions:
                    source_files.append(file_path)

        return sorted(source_files)

    def _build_cross_language_dependencies(self, results_by_language: Dict[str, List[Dict]]):
        """
        Analyze cross-language dependencies in polyglot codebases.
        
        Detects when components in one language depend on components
        in another language.
        """
        self.cross_language_dependencies = []

        # Build a map of all exported/public entities
        entity_map: Dict[str, List[str]] = defaultdict(list)  # name -> [language, filepath]

        for language, results in results_by_language.items():
            for result in results:
                entities = result.get('entities', [])
                filepath = result.get('filepath', '')

                for entity in entities:
                    entity_name = entity.get('name', '')
                    if entity_name:
                        entity_map[entity_name].append({
                            'language': language,
                            'filepath': filepath,
                            'entity': entity,
                        })

        # Find cross-language references
        for language, results in results_by_language.items():
            for result in results:
                # Check imports/dependencies
                imports = result.get('imports', [])
                dependencies = result.get('dependencies', [])

                filepath = result.get('filepath', '')

                for imp in imports:
                    source = imp.get('source', '') or imp.get('path', '')
                    for imported_name in imp.get('items', []):
                        if imported_name in entity_map:
                            for entity_ref in entity_map[imported_name]:
                                if entity_ref['language'] != language:
                                    self.cross_language_dependencies.append({
                                        'source': {
                                            'language': language,
                                            'filepath': filepath,
                                        },
                                        'target': {
                                            'language': entity_ref['language'],
                                            'filepath': entity_ref['filepath'],
                                            'entity': imported_name,
                                        },
                                        'type': 'cross_language_import',
                                    })

    def _aggregate_statistics(self, results_by_language: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Aggregate statistics across all analyzed files."""
        stats = {
            'total_lines_of_code': 0,
            'total_classes': 0,
            'total_functions': 0,
            'total_methods': 0,
            'total_interfaces': 0,
            'by_language': {},
        }

        for language, results in results_by_language.items():
            lang_stats = {
                'files': len(results),
                'lines_of_code': 0,
                'classes': 0,
                'functions': 0,
                'methods': 0,
                'interfaces': 0,
                'types': 0,
            }

            for result in results:
                file_stats = result.get('statistics', {})
                lang_stats['lines_of_code'] += file_stats.get('lines_of_code', 0)

                # Aggregate entity counts
                for entity_type in ('classes', 'functions', 'methods', 'interfaces', 'types'):
                    lang_stats[entity_type] += file_stats.get(f'num_{entity_type}', 0)

                # Also count from entities list
                entities = result.get('entities', [])
                for entity in entities:
                    entity_type = entity.get('type', '')
                    if entity_type == 'class':
                        lang_stats['classes'] += 1
                    elif entity_type in ('function', 'method', 'async_function'):
                        if entity_type == 'method':
                            lang_stats['methods'] += 1
                        else:
                            lang_stats['functions'] += 1
                    elif entity_type == 'interface':
                        lang_stats['interfaces'] += 1

            stats['by_language'][language] = lang_stats

            # Update totals
            stats['total_lines_of_code'] += lang_stats['lines_of_code']
            stats['total_classes'] += lang_stats['classes']
            stats['total_functions'] += lang_stats['functions']
            stats['total_methods'] += lang_stats['methods']
            stats['total_interfaces'] += lang_stats['interfaces']

        return stats

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of all analyzed files."""
        return {
            'total_files': len(self.analyzed_files),
            'languages_detected': set(f.get('language') for f in self.analyzed_files.values()),
            'cross_language_dependencies': len(self.cross_language_dependencies),
            'files': list(self.analyzed_files.keys()),
        }

    def export_as_graph(self) -> Dict[str, Any]:
        """
        Export the analysis as a graph structure.

        Useful for visualization and further processing.
        """
        nodes = []
        edges = []
        file_id = 0
        entity_id = 0

        # Create nodes for files
        for filepath, analysis in self.analyzed_files.items():
            nodes.append({
                'id': f'file_{file_id}',
                'type': 'file',
                'name': os.path.basename(filepath),
                'filepath': filepath,
                'language': analysis.get('language', 'unknown'),
            })
            file_id += 1

        # Create nodes for entities
        entity_to_id = {}
        for filepath, analysis in self.analyzed_files.items():
            entities = analysis.get('entities', [])
            for entity in entities:
                entity_key = f"{filepath}:{entity.get('name')}"
                entity_to_id[entity_key] = f'entity_{entity_id}'

                nodes.append({
                    'id': f'entity_{entity_id}',
                    'type': 'entity',
                    'name': entity.get('name'),
                    'entity_type': entity.get('type'),
                    'language': analysis.get('language'),
                    'filepath': filepath,
                })
                entity_id += 1

        # Create edges for dependencies
        for filepath, analysis in self.analyzed_files.items():
            language = analysis.get('language')

            # Import edges
            imports = analysis.get('imports', [])
            for imp in imports:
                source = imp.get('source', '') or imp.get('path', '')
                # Create generic dependency edge
                edges.append({
                    'source': f"file_{list(self.analyzed_files.keys()).index(filepath)}",
                    'target_module': source,
                    'type': 'imports',
                    'language': language,
                })

        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': {
                'num_nodes': len(nodes),
                'num_edges': len(edges),
            },
        }


# Convenience functions
def analyze_codebase(directory: str, max_workers: int = 4) -> Dict[str, Any]:
    """
    Analyze an entire codebase with automatic language detection.

    Args:
        directory: Root directory of the codebase
        max_workers: Number of parallel workers

    Returns:
        Comprehensive analysis results
    """
    analyzer = MultiLanguageAnalyzer()
    return analyzer.analyze_directory(directory, max_workers)


def analyze_file(filepath: str) -> Dict[str, Any]:
    """
    Analyze a single file with automatic language detection.

    Args:
        filepath: Path to the file

    Returns:
        Analysis results
    """
    analyzer = MultiLanguageAnalyzer()
    return analyzer.analyze_file(filepath)


def get_supported_languages() -> Dict[str, bool]:
    """Get the list of supported languages and their availability."""
    return MultiLanguageAnalyzer.SUPPORTED_LANGUAGES.copy()


def get_language_extensions() -> Dict[str, str]:
    """Get mapping of file extensions to languages."""
    return MultiLanguageAnalyzer.LANGUAGE_MAP.copy()
