"""
Cross-Language Dependency Detector

Analyzes dependencies and interactions between components written in different
programming languages within the same codebase.

Features:
- Detect inter-language calls and imports
- Map API boundaries between languages
- Identify polyglot architectural patterns
- Validate dependency direction and coupling
- Generate cross-language dependency graphs
"""

import os
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import defaultdict
import re
from dataclasses import dataclass


@dataclass
class CrossLanguageDependency:
    """Represents a dependency between components in different languages."""
    source_language: str
    source_file: str
    source_entity: str
    target_language: str
    target_file: str
    target_entity: str
    dependency_type: str  # import, call, reference, config, etc
    confidence: float  # 0.0-1.0
    evidence: List[str] = None  # Supporting evidence from code

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []


class CrossLanguageDependencyDetector:
    """
    Detects and analyzes dependencies between different languages
    in a polyglot codebase.
    """

    # Common inter-language patterns
    PATTERNS = {
        'javascript_to_python': [
            r'pythonbridge',
            r'python\s+server',
            r'node.*spawn.*python',
            r'subprocess',
        ],
        'go_to_csharp': [
            r'\.net',
            r'c#\s+service',
            r'csharp.*interface',
        ],
        'typescript_to_java': [
            r'jvm\s+class',
            r'java\s+interface',
            r'jvm.*service',
        ],
        'csharp_to_go': [
            r'grpc',
            r'go.*service',
            r'protobuf',
        ],
    }

    def __init__(self):
        """Initialize the detector."""
        self.dependencies: List[CrossLanguageDependency] = []
        self.language_boundaries: Dict[str, Set[str]] = defaultdict(set)
        self.api_mappings: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def analyze_multi_language_codebase(self, analysis_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Analyze cross-language dependencies from multi-language analysis results.

        Args:
            analysis_results: Results from MultiLanguageAnalyzer, keyed by language

        Returns:
            Dictionary containing cross-language dependency information
        """
        self.dependencies = []
        self.language_boundaries = defaultdict(set)

        # Build entity indices for all languages
        entity_index = self._build_entity_index(analysis_results)

        # Find cross-language imports
        self._detect_cross_language_imports(analysis_results, entity_index)

        # Detect common inter-language patterns
        self._detect_architectural_patterns(analysis_results)

        # Analyze API boundaries
        self._analyze_api_boundaries(analysis_results)

        # Generate polyglot structure report
        polyglot_structure = self._analyze_polyglot_structure(analysis_results)

        return {
            "cross_language_dependencies": [self._dep_to_dict(d) for d in self.dependencies],
            "dependency_count": len(self.dependencies),
            "language_boundaries": dict(self.language_boundaries),
            "api_mappings": dict(self.api_mappings),
            "polyglot_structure": polyglot_structure,
            "statistics": self._calculate_statistics(),
        }

    def _build_entity_index(self, analysis_results: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Build an index of all entities by language and name for quick lookup.

        Returns:
            Dictionary mapping entity names to their definitions across languages
        """
        entity_index: Dict[str, List[Dict]] = defaultdict(list)

        for language, results in analysis_results.items():
            for result in results:
                filepath = result.get('filepath', '')
                entities = result.get('entities', [])

                for entity in entities:
                    entity_name = entity.get('name', '')
                    if entity_name:
                        # Store entity with context
                        entity_index[entity_name].append({
                            'language': language,
                            'filepath': filepath,
                            'entity': entity,
                            'full_name': f"{language}:{filepath}:{entity_name}",
                        })

        return entity_index

    def _detect_cross_language_imports(
        self,
        analysis_results: Dict[str, List[Dict]],
        entity_index: Dict[str, List[Dict]]
    ):
        """Detect direct imports/dependencies between different languages."""

        for language, results in analysis_results.items():
            for result in results:
                filepath = result.get('filepath', '')
                imports = result.get('imports', [])
                dependencies = result.get('dependencies', [])

                # Check imports
                for imp in imports:
                    source = imp.get('source', '') or imp.get('path', '') or imp.get('namespace', '')
                    imported_items = imp.get('items', [])

                    for item in imported_items:
                        if item in entity_index:
                            # Check if it's from a different language
                            for target_info in entity_index[item]:
                                target_lang = target_info['language']

                                if target_lang != language:
                                    dep = CrossLanguageDependency(
                                        source_language=language,
                                        source_file=filepath,
                                        source_entity=item,
                                        target_language=target_lang,
                                        target_file=target_info['filepath'],
                                        target_entity=item,
                                        dependency_type='import',
                                        confidence=0.9,
                                        evidence=[f"Import statement: {source}"],
                                    )
                                    self.dependencies.append(dep)
                                    self.language_boundaries[language].add(target_lang)

    def _detect_architectural_patterns(self, analysis_results: Dict[str, List[Dict]]):
        """
        Detect common architectural patterns for inter-language communication.
        
        Patterns:
        - API gateways
        - Message queues
        - RPC/gRPC services
        - Database mediation
        - File-based communication
        """
        patterns_found: Dict[str, List[str]] = defaultdict(list)

        for language, results in analysis_results.items():
            for result in results:
                filepath = result.get('filepath', '')
                entities = result.get('entities', [])

                # Check entity names and types for patterns
                for entity in entities:
                    entity_name = entity.get('name', '').lower()
                    entity_type = entity.get('type', '').lower()

                    # API/Gateway patterns
                    if any(x in entity_name for x in ['api', 'gateway', 'service', 'server', 'client']):
                        if 'class' in entity_type or 'interface' in entity_type:
                            patterns_found['api_gateway'].append({
                                'language': language,
                                'file': filepath,
                                'entity': entity.get('name'),
                            })

                    # RPC/Messaging patterns
                    if any(x in entity_name for x in ['rpc', 'grpc', 'message', 'queue', 'broker']):
                        patterns_found['rpc_messaging'].append({
                            'language': language,
                            'file': filepath,
                            'entity': entity.get('name'),
                        })

                    # Database/Storage patterns
                    if any(x in entity_name for x in ['db', 'database', 'repository', 'persistence', 'store']):
                        patterns_found['data_layer'].append({
                            'language': language,
                            'file': filepath,
                            'entity': entity.get('name'),
                        })

        self.api_mappings['architectural_patterns'] = patterns_found

    def _analyze_api_boundaries(self, analysis_results: Dict[str, List[Dict]]):
        """
        Analyze API boundaries and public interfaces between languages.
        """
        # Collect exported/public entities per language
        public_apis: Dict[str, List[Dict]] = defaultdict(list)

        for language, results in analysis_results.items():
            for result in results:
                filepath = result.get('filepath', '')
                entities = result.get('entities', [])
                exports = result.get('exports', [])

                # Add exported items
                for export in exports:
                    exported_name = export.get('name', '')
                    if exported_name:
                        public_apis[language].append({
                            'name': exported_name,
                            'filepath': filepath,
                            'type': export.get('type', 'default'),
                        })

                # Add public/exported entities (by naming convention)
                for entity in entities:
                    access_modifier = entity.get('access_modifier', '')
                    if access_modifier in ('public', 'exported'):
                        public_apis[language].append({
                            'name': entity.get('name', ''),
                            'filepath': filepath,
                            'type': entity.get('type', 'unknown'),
                        })

        self.api_mappings['public_apis_by_language'] = dict(public_apis)

    def _analyze_polyglot_structure(self, analysis_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Analyze the overall polyglot architecture structure.
        """
        structure = {
            'languages_present': list(analysis_results.keys()),
            'files_by_language': {},
            'entities_by_language': {},
            'coupling_matrix': {},
        }

        # Count files and entities
        for language, results in analysis_results.items():
            file_count = len(results)
            entity_count = sum(len(r.get('entities', [])) for r in results)

            structure['files_by_language'][language] = file_count
            structure['entities_by_language'][language] = entity_count

        # Build coupling matrix
        coupling_matrix = defaultdict(lambda: defaultdict(int))
        for dep in self.dependencies:
            coupling_matrix[dep.source_language][dep.target_language] += 1

        structure['coupling_matrix'] = {
            lang: dict(targets)
            for lang, targets in coupling_matrix.items()
        }

        return structure

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about cross-language dependencies."""
        if not self.dependencies:
            return {
                'total_dependencies': 0,
                'by_type': {},
                'language_pairs': {},
            }

        stats = {
            'total_dependencies': len(self.dependencies),
            'by_type': defaultdict(int),
            'language_pairs': defaultdict(int),
            'average_confidence': sum(d.confidence for d in self.dependencies) / len(self.dependencies),
        }

        for dep in self.dependencies:
            stats['by_type'][dep.dependency_type] += 1
            pair = f"{dep.source_language}->{dep.target_language}"
            stats['language_pairs'][pair] += 1

        return {
            'total_dependencies': stats['total_dependencies'],
            'by_type': dict(stats['by_type']),
            'language_pairs': dict(stats['language_pairs']),
            'average_confidence': stats['average_confidence'],
        }

    def get_polyglot_recommendations(self) -> Dict[str, Any]:
        """
        Generate recommendations for polyglot architecture improvements.
        """
        recommendations = {
            'coupling_analysis': [],
            'architecture_suggestions': [],
            'language_boundary_issues': [],
        }

        if not self.dependencies:
            recommendations['coupling_analysis'].append("No cross-language dependencies detected.")
            return recommendations

        # Analyze coupling
        for dep in self.dependencies:
            if dep.confidence < 0.5:
                recommendations['language_boundary_issues'].append({
                    'issue': f'Low confidence cross-language dependency detected',
                    'source': f"{dep.source_language}:{dep.source_file}",
                    'target': f"{dep.target_language}:{dep.target_file}",
                    'confidence': dep.confidence,
                    'suggestion': 'Review and clarify this dependency; consider adding documentation',
                })

        # Suggest API gateways for heavily coupled components
        if len(self.dependencies) > 5:
            recommendations['architecture_suggestions'].append({
                'suggestion': 'Consider implementing an API gateway pattern',
                'reason': 'Multiple cross-language dependencies detected',
                'benefit': 'Centralizes inter-language communication and improves maintainability',
            })

        # Suggest message queue for decoupling
        if any(d.dependency_type == 'async' for d in self.dependencies):
            recommendations['architecture_suggestions'].append({
                'suggestion': 'Consider implementing event-driven communication',
                'reason': 'Async dependencies detected between languages',
                'benefit': 'Improves system decoupling and scalability',
            })

        return recommendations

    def _dep_to_dict(self, dep: CrossLanguageDependency) -> Dict[str, Any]:
        """Convert dependency to dictionary."""
        return {
            'source_language': dep.source_language,
            'source_file': dep.source_file,
            'source_entity': dep.source_entity,
            'target_language': dep.target_language,
            'target_file': dep.target_file,
            'target_entity': dep.target_entity,
            'dependency_type': dep.dependency_type,
            'confidence': dep.confidence,
            'evidence': dep.evidence,
        }


# Convenience function
def detect_cross_language_dependencies(analysis_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """
    Detect cross-language dependencies from multi-language analysis results.

    Args:
        analysis_results: Results from MultiLanguageAnalyzer

    Returns:
        Cross-language dependency analysis
    """
    detector = CrossLanguageDependencyDetector()
    return detector.analyze_multi_language_codebase(analysis_results)
