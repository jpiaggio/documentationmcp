"""
Integrated Context-Aware Suggestions Agent

Combines context-aware suggestions with ML pattern recognition,
semantic analysis, and business rules extraction to provide
comprehensive code improvement recommendations.
"""

import os
import sys
import json
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from context_aware_suggestions import ContextAwareSuggestionsEngine
from semantic_analyzer import SemanticAnalyzer
from business_rules_extractor import BusinessRulesExtractor


class IntegratedContextAwareAgent:
    """
    Orchestrates comprehensive context-aware analysis:
    1. Extract structural information (code patterns)
    2. Semantic analysis (call graphs, data flow)
    3. Business rules analysis
    4. Context-aware suggestions
    """
    
    def __init__(self, codebase_path: str):
        self.codebase_path = codebase_path
        self.suggestions_engine = ContextAwareSuggestionsEngine(codebase_path)
        self.semantic_analyzer = SemanticAnalyzer('python')
        self.business_extractor = BusinessRulesExtractor()
        self.analysis_results = {}
    
    def analyze(self) -> Dict[str, Any]:
        """Run complete context-aware analysis."""
        print(f"\n{'='*70}")
        print("🚀 INTEGRATED CONTEXT-AWARE SUGGESTIONS AGENT")
        print(f"{'='*70}")
        print(f"\n📁 Codebase: {self.codebase_path}\n")
        
        # Phase 1: Context-aware suggestions
        print("Phase 1: Generating context-aware suggestions...")
        suggestions_results = self.suggestions_engine.analyze_codebase()
        
        # Phase 2: Semantic analysis
        print("\nPhase 2: Running semantic analysis...")
        semantic_results = self._run_semantic_analysis()
        
        # Phase 3: Business rules analysis
        print("\nPhase 3: Extracting business rules...")
        business_results = self._run_business_analysis()
        
        # Phase 4: Cross-reference insights
        print("\nPhase 4: Cross-referencing insights...")
        cross_referenced = self._cross_reference_insights(
            suggestions_results,
            semantic_results,
            business_results
        )
        
        # Compile final results
        self.analysis_results = {
            'metadata': {
                'codebase': self.codebase_path,
                'timestamp': datetime.now().isoformat(),
                'phases_completed': 4
            },
            'suggestions': suggestions_results,
            'semantic_analysis': semantic_results,
            'business_analysis': business_results,
            'cross_referenced_insights': cross_referenced
        }
        
        return self.analysis_results
    
    def _run_semantic_analysis(self) -> Dict[str, Any]:
        """Run semantic analysis on codebase."""
        results = {
            'call_graphs': [],
            'data_flows': [],
            'control_flows': [],
            'total_files': 0
        }
        
        # Discover and analyze files
        for root, dirs, files in os.walk(self.codebase_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source = f.read()
                        
                        # Run semantic analysis
                        analysis = self.semantic_analyzer.analyze(source, file)
                        results['total_files'] += 1
                        
                        # Store aggregated results
                        if analysis.get('call_graph'):
                            results['call_graphs'].extend(analysis['call_graph'].get('edges', []))
                    except:
                        continue
        
        return results
    
    def _run_business_analysis(self) -> Dict[str, Any]:
        """Run business rules and entity extraction."""
        results = {
            'business_processes': [],
            'business_entities': [],
            'business_events': [],
            'integration_points': [],
            'total_files': 0
        }
        
        for root, dirs, files in os.walk(self.codebase_path):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source = f.read()
                        
                        rel_path = os.path.relpath(file_path, self.codebase_path)
                        
                        # Extract business information
                        processes = self.business_extractor.extract_business_processes(source, rel_path)
                        entities = self.business_extractor.extract_business_entities(source, rel_path)
                        
                        if processes:
                            results['business_processes'].extend(processes)
                        if entities:
                            results['business_entities'].extend(entities)
                        
                        results['total_files'] += 1
                    except:
                        continue
        
        return results
    
    def _cross_reference_insights(
        self,
        suggestions: Dict[str, Any],
        semantic: Dict[str, Any],
        business: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cross-reference insights from different analyses."""
        insights = {
            'validation_logic_metrics': self._analyze_validation_coverage(suggestions),
            'error_handling_gaps': self._analyze_error_patterns(suggestions, semantic),
            'function_consolidation_impact': self._calculate_consolidation_impact(suggestions),
            'rule_consistency': self._analyze_rule_consistency(business, suggestions),
            'recommendations': []
        }
        
        # Generate consolidated recommendations
        insights['recommendations'] = self._generate_consolidated_recommendations(
            suggestions,
            semantic,
            business,
            insights
        )
        
        return insights
    
    def _analyze_validation_coverage(self, suggestions: Dict) -> Dict[str, Any]:
        """Analyze validation logic coverage."""
        duplicates = suggestions['suggestions']['duplicate_validation']
        
        return {
            'total_duplicate_sets': len(duplicates),
            'affected_functions': len(set(d['function_a'] for d in duplicates) | set(d['function_b'] for d in duplicates)),
            'consolidation_potential': {
                'functions_to_extract': len(set(d['function_a'] for d in duplicates)),
                'lines_to_save': sum(d.get('details', {}).get('line_a', 0) for d in duplicates),
                'estimated_effort': 'low' if len(duplicates) < 5 else 'medium'
            }
        }
    
    def _analyze_error_patterns(self, suggestions: Dict, semantic: Dict) -> Dict[str, Any]:
        """Analyze error handling patterns."""
        unhandled = suggestions['suggestions']['unhandled_errors']
        
        return {
            'total_unhandled_cases': len(unhandled),
            'high_risk_cases': [u for u in unhandled if u['severity'] == 'high'],
            'operation_types': {
                'io_operations': len([u for u in unhandled if u['details']['has_io']]),
                'network_operations': len([u for u in unhandled if u['details']['has_network']]),
                'database_operations': len([u for u in unhandled if u['details']['has_db']])
            },
            'priority': 'critical' if len([u for u in unhandled if u['severity'] == 'high']) > 0 else 'medium'
        }
    
    def _calculate_consolidation_impact(self, suggestions: Dict) -> Dict[str, Any]:
        """Calculate impact of function consolidation."""
        opportunities = suggestions['suggestions']['consolidation_opportunities']
        
        total_similarity = sum(o['similarity'] for o in opportunities) / len(opportunities) if opportunities else 0
        
        return {
            'total_opportunities': len(opportunities),
            'average_similarity': total_similarity,
            'potential_reduction': {
                'code_duplication': f"{total_similarity:.1%}",
                'maintenance_burden': 'reduced' if len(opportunities) > 2 else 'minimal',
                'test_coverage_improvement': 'significant' if len(opportunities) > 5 else 'moderate'
            }
        }
    
    def _analyze_rule_consistency(self, business: Dict, suggestions: Dict) -> Dict[str, Any]:
        """Analyze business rule consistency."""
        conflicts = suggestions['suggestions']['rule_conflicts']
        total_rules = business.get('business_processes', [])
        
        return {
            'total_business_rules': len(total_rules),
            'rule_conflicts_found': len(conflicts),
            'critical_conflicts': len([c for c in conflicts if c['severity'] == 'critical']),
            'consistency_score': max(0, 1 - (len(conflicts) / max(1, len(total_rules)))),
            'recommended_actions': [c['details']['recommendation'] for c in conflicts[:3]]
        }
    
    def _generate_consolidated_recommendations(
        self,
        suggestions: Dict,
        semantic: Dict,
        business: Dict,
        insights: Dict
    ) -> List[Dict[str, Any]]:
        """Generate consolidated recommendations."""
        recommendations = []
        
        # Recommendation 1: Validation consolidation
        if insights['validation_logic_metrics']['total_duplicate_sets'] > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'code_quality',
                'title': 'Consolidate duplicate validation logic',
                'description': 'Multiple validation rules are duplicated across files. Create shared utility functions.',
                'impact': f"Reduce code duplication by {len(suggestions['suggestions']['duplicate_validation'])} functions",
                'effort': 'medium',
                'timeline': '1-2 days'
            })
        
        # Recommendation 2: Error handling
        if insights['error_handling_gaps']['total_unhandled_cases'] > 0:
            recommendations.append({
                'priority': 'critical' if insights['error_handling_gaps']['priority'] == 'critical' else 'high',
                'category': 'reliability',
                'title': 'Add error handling to critical operations',
                'description': 'Several functions perform risky operations without proper error handling.',
                'impact': f"Improve application resilience and prevent crashes",
                'effort': 'medium',
                'timeline': '2-3 days'
            })
        
        # Recommendation 3: Function consolidation
        if insights['function_consolidation_impact']['total_opportunities'] > 2:
            recommendations.append({
                'priority': 'medium',
                'category': 'maintainability',
                'title': 'Consolidate similar functions',
                'description': f"{insights['function_consolidation_impact']['total_opportunities']} functions have high similarity and could be merged.",
                'impact': 'Reduce maintenance burden and improve testability',
                'effort': 'low' if insights['function_consolidation_impact']['total_opportunities'] < 5 else 'medium',
                'timeline': '1-3 days'
            })
        
        # Recommendation 4: Business rule alignment
        if insights['rule_consistency']['critical_conflicts'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'business_logic',
                'title': 'Resolve contradicting business rules',
                'description': f"{insights['rule_consistency']['critical_conflicts']} critical contradictions found in business rules.",
                'impact': 'Prevent business logic errors and ensure consistency',
                'effort': 'high',
                'timeline': '3-5 days'
            })
        
        return recommendations
    
    def print_report(self):
        """Print comprehensive analysis report."""
        if not self.analysis_results:
            print("No analysis results available. Run analyze() first.")
            return
        
        results = self.analysis_results
        
        print(f"\n{'='*70}")
        print("📊 COMPREHENSIVE ANALYSIS REPORT")
        print(f"{'='*70}\n")
        
        # Executive Summary
        print("📈 EXECUTIVE SUMMARY")
        print("-" * 70)
        
        sugg = results['suggestions']['summary']
        print(f"   • Duplicate validation found:     {sugg['duplicate_validation_found']} instances")
        print(f"   • Unhandled error cases:          {sugg['unhandled_errors_found']} functions")
        print(f"   • Consolidation opportunities:    {sugg['consolidation_opportunities']} functions")
        print(f"   • Business rule conflicts:        {sugg['rule_conflicts_found']} conflicts")
        print(f"   • Total actionable suggestions:   {sugg['total_suggestions']}\n")
        
        # Detailed Suggestions
        self.suggestions_engine.print_summary()
        
        # Cross-referenced insights
        cross_ref = results['cross_referenced_insights']
        
        print("🔍 CROSS-REFERENCED INSIGHTS")
        print("-" * 70)
        
        print(f"\n   Validation Coverage:")
        val_metrics = cross_ref['validation_logic_metrics']
        print(f"   • Duplicate validation sets: {val_metrics['total_duplicate_sets']}")
        print(f"   • Affected functions: {val_metrics['affected_functions']}")
        print(f"   • Consolidation potential: {val_metrics['consolidation_potential']['functions_to_extract']} functions")
        
        print(f"\n   Error Handling Analysis:")
        err_gaps = cross_ref['error_handling_gaps']
        print(f"   • Total unhandled cases: {err_gaps['total_unhandled_cases']}")
        print(f"   • High-risk cases: {len(err_gaps['high_risk_cases'])}")
        print(f"   • Network operations without handlers: {err_gaps['operation_types']['network_operations']}")
        
        print(f"\n   Function Consolidation:")
        consol = cross_ref['function_consolidation_impact']
        print(f"   • Consolidation opportunities: {consol['total_opportunities']}")
        print(f"   • Average similarity: {consol['average_similarity']:.1%}")
        
        print(f"\n   Business Rule Consistency:")
        rules = cross_ref['rule_consistency']
        print(f"   • Total rules: {rules['total_business_rules']}")
        print(f"   • Conflicts found: {rules['rule_conflicts_found']}")
        print(f"   • Consistency score: {rules['consistency_score']:.1%}")
        
        # Recommendations
        if cross_ref['recommendations']:
            print(f"\n\n💡 ACTION PLAN")
            print("-" * 70)
            
            for i, rec in enumerate(cross_ref['recommendations'], 1):
                priority_emoji = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
                print(f"\n   {priority_emoji} {i}. {rec['title']}")
                print(f"      Category: {rec['category']}")
                print(f"      {rec['description']}")
                print(f"      Impact: {rec['impact']}")
                print(f"      Effort: {rec['effort']}")
                print(f"      Timeline: {rec['timeline']}")
        
        print(f"\n{'='*70}\n")
    
    def export_json(self, output_path: str):
        """Export analysis results as JSON."""
        with open(output_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        print(f"✅ Results exported to {output_path}")


def run_integrated_analysis(codebase_path: str) -> Dict[str, Any]:
    """Run integrated context-aware analysis."""
    agent = IntegratedContextAwareAgent(codebase_path)
    results = agent.analyze()
    agent.print_report()
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python integrated_context_aware_agent.py <codebase_path> [output_json]")
        sys.exit(1)
    
    codebase_path = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = run_integrated_analysis(codebase_path)
    
    if output_json:
        agent = IntegratedContextAwareAgent(codebase_path)
        agent.analysis_results = results
        agent.export_json(output_json)
