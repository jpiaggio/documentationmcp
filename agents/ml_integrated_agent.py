"""
Integrated ML Pattern Recognition Agent

Combines cartographer_agent, semantic_analyzer, and ml_pattern_recognition
to provide complete codebase analysis with machine learning insights.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from cartographer_agent import cartographer_agent
from ml_pattern_recognition import (
    MLPatternRecognitionEngine, 
    CodePattern,
    PatternLearner
)


class IntegratedPatternAnalysisAgent:
    """
    Orchestrates complete analysis pipeline:
    1. Extract code structure (cartographer)
    2. Analyze semantics (semantic_analyzer)
    3. Apply ML pattern recognition
    4. Generate insights and recommendations
    """
    
    def __init__(self, codebase_path: str, model_cache_path: Optional[str] = None):
        self.codebase_path = codebase_path
        self.model_cache_path = model_cache_path or os.path.join(
            os.path.expanduser('~'), 
            '.documentationmcp', 
            'ml_models'
        )
        self.ml_engine = MLPatternRecognitionEngine(model_cache_path)
        self.extraction_results = {}
        self.analysis_results = {}
        self.recommendations = []
    
    def analyze(self, file_ext: str = '.py', max_workers: int = 8) -> Dict[str, Any]:
        """
        Run complete analysis pipeline.
        """
        print(f"\n🚀 Starting Integrated Pattern Analysis on {self.codebase_path}")
        print(f"   File extension: {file_ext}")
        print(f"   Max workers: {max_workers}")
        
        # Step 1: Extract code structure
        print(f"\n📖 Step 1: Extracting code structure...")
        self._extract_code_structure(file_ext, max_workers)
        
        # Step 2: Identify patterns from extraction
        print(f"\n🔍 Step 2: Identifying patterns...")
        self._identify_patterns()
        
        # Step 3: Apply ML analysis
        print(f"\n🤖 Step 3: Applying ML pattern recognition...")
        self.ml_engine.analyze_patterns(self.extraction_results)
        
        # Step 4: Generate recommendations
        print(f"\n💡 Step 4: Generating insights and recommendations...")
        self._generate_recommendations()
        
        # Compile final results
        self.analysis_results = {
            'metadata': {
                'codebase': self.codebase_path,
                'file_extension': file_ext,
                'timestamp': datetime.now().isoformat(),
                'extraction_count': len(self.extraction_results)
            },
            'extraction': self.extraction_results,
            'ml_analysis': self.ml_engine.analysis_results,
            'recommendations': self.recommendations
        }
        
        return self.analysis_results
    
    def _extract_code_structure(self, file_ext: str, max_workers: int):
        """Extract code structure using cartographer_agent."""
        try:
            cypher_statements = cartographer_agent(
                self.codebase_path,
                file_ext=file_ext,
                max_workers=max_workers
            )
            
            # Parse and organize results
            self.extraction_results = {
                'total_statements': len(cypher_statements),
                'file_extension': file_ext,
                'results': cypher_statements[:100],  # Store first 100 for analysis
                'full_count': len(cypher_statements)
            }
            
            print(f"  ✅ Extracted {len(cypher_statements)} code elements")
            
        except Exception as e:
            print(f"  ❌ Extraction failed: {e}")
            self.extraction_results = {'error': str(e)}
    
    def _identify_patterns(self):
        """Identify patterns from extraction results."""
        patterns_found = {
            'modules': 0,
            'classes': 0,
            'functions': 0,
            'calls': 0,
            'definitions': 0
        }
        
        # Count pattern types from extraction
        if 'results' in self.extraction_results:
            for statement in self.extraction_results['results']:
                if ':Module' in statement:
                    patterns_found['modules'] += 1
                elif ':Class' in statement:
                    patterns_found['classes'] += 1
                elif ':Function' in statement or ':Method' in statement:
                    patterns_found['functions'] += 1
                elif 'CALLS' in statement:
                    patterns_found['calls'] += 1
        
        print(f"  📊 Pattern Summary:")
        for ptype, count in patterns_found.items():
            if count > 0:
                print(f"     {ptype}: {count}")
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on analysis."""
        if not self.ml_engine.analysis_results:
            return
        
        ml_results = self.ml_engine.analysis_results
        recommendations = []
        
        # Recommendation 1: Address anomalies
        if ml_results['anomalies']['details']:
            anomalies = ml_results['anomalies']['details']
            critical_anomalies = [a for a in anomalies if a['severity'] in ['critical', 'high']]
            
            if critical_anomalies:
                recommendations.append({
                    'priority': 'critical',
                    'category': 'Code Quality',
                    'title': 'Address Critical Code Anomalies',
                    'description': f'Found {len(critical_anomalies)} patterns with unusual or risky code structures',
                    'items': critical_anomalies[:5],
                    'action': 'Review flagged patterns for potential bugs or security issues',
                    'impact': 'high'
                })
        
        # Recommendation 2: Document critical path
        cat = ml_results['categorization']
        if cat['critical_path'] > 0:
            critical_items = cat['details'].get('critical_path', [])[:3]
            undocumented_critical = [item for item in critical_items if not item['documented']]
            
            if undocumented_critical:
                recommendations.append({
                    'priority': 'high',
                    'category': 'Documentation',
                    'title': 'Document Critical Path Code',
                    'description': f'Found {len(undocumented_critical)} critical business logic patterns without documentation',
                    'items': undocumented_critical,
                    'action': 'Add comprehensive documentation to critical path functions',
                    'impact': 'high'
                })
        
        # Recommendation 3: Improve hot path performance
        if cat['hot_path'] > 3:
            hot_items = cat['details'].get('hot_path', [])[:3]
            recommendations.append({
                'priority': 'high',
                'category': 'Performance',
                'title': 'Optimize Hot Path Code',
                'description': f'Identified {cat["hot_path"]} performance-sensitive code sections',
                'items': hot_items,
                'action': 'Add caching, optimize algorithms, and profile performance',
                'impact': 'medium'
            })
        
        # Recommendation 4: Improve test coverage for business logic
        business_items = cat['details'].get('business_logic', [])
        if business_items:
            untested = [item for item in business_items if not item.get('has_tests', True)][:3]
            if untested:
                recommendations.append({
                    'priority': 'high',
                    'category': 'Testing',
                    'title': 'Increase Business Logic Test Coverage',
                    'description': 'Business logic patterns need comprehensive test coverage',
                    'items': untested,
                    'action': 'Write unit and integration tests for business rules',
                    'impact': 'high'
                })
        
        # Recommendation 5: ML-predicted documentation
        docs = ml_results['documentation']
        if docs['priority_items']:
            priority_items = docs['priority_items'][:3]
            recommendations.append({
                'priority': 'medium',
                'category': 'Documentation',
                'title': 'Document Based on ML Predictions',
                'description': f'ML analysis suggests {len(docs["priority_items"])} patterns need documentation',
                'items': priority_items,
                'action': 'Use similar patterns as documentation templates',
                'impact': 'medium'
            })
        
        # Recommendation 6: Pattern clustering insights
        if ml_results['model']['clusters'] > 0:
            recommendations.append({
                'priority': 'low',
                'category': 'Code Organization',
                'title': 'Review Pattern Clusters',
                'description': f'Discovered {ml_results["model"]["clusters"]} pattern clusters in codebase',
                'action': 'Analyze clusters to identify opportunities for code reuse and consolidation',
                'impact': 'medium'
            })
        
        self.recommendations = recommendations
    
    def print_full_report(self):
        """Print comprehensive analysis report."""
        print("\n" + "="*80)
        print("🔬 INTEGRATED PATTERN ANALYSIS REPORT")
        print("="*80)
        
        if not self.analysis_results:
            print("❌ No analysis results. Run analyze() first.")
            return
        
        # Metadata
        meta = self.analysis_results['metadata']
        print(f"\n📋 METADATA")
        print(f"  Codebase: {meta['codebase']}")
        print(f"  Timestamp: {meta['timestamp']}")
        
        # ML Analysis
        ml = self.ml_engine.analysis_results
        if ml:
            print(f"\n🤖 ML ANALYSIS SUMMARY")
            print(f"  Total Patterns: {ml['summary']['total_patterns']}")
            print(f"  Anomalies Found: {ml['anomalies']['count']}")
            print(f"  Documentation Gaps: {ml['summary']['documentation_gaps']}")
            
            # Categorization breakdown
            cat = ml['categorization']
            print(f"\n  Pattern Categories:")
            print(f"    • Critical Path:  {cat['critical_path']}")
            print(f"    • Hot Path:       {cat['hot_path']}")
            print(f"    • Business Logic: {cat['business_logic']}")
            print(f"    • Integration:    {cat['integration']}")
            print(f"    • Utility:        {cat['utility']}")
            print(f"    • Infrastructure: {cat['infrastructure']}")
        
        # Recommendations
        if self.recommendations:
            print(f"\n💡 KEY RECOMMENDATIONS ({len(self.recommendations)} total)")
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sorted_recs = sorted(self.recommendations, 
                               key=lambda x: priority_order.get(x['priority'], 999))
            
            for i, rec in enumerate(sorted_recs[:6], 1):
                priority_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec['priority'], '⚪')
                
                print(f"\n  {i}. {priority_emoji} {rec['title']}")
                print(f"     Category: {rec['category']}")
                print(f"     Impact: {rec['impact'].upper()}")
                print(f"     Action: {rec['action']}")
                
                if rec.get('items'):
                    print(f"     Items ({len(rec['items'])}):")
                    for item in rec['items'][:2]:
                        name = item.get('name') or item.get('pattern_name', 'unnamed')
                        print(f"       • {name}")
        
        # Anomalies detail
        if ml['anomalies']['details']:
            print(f"\n⚠️  TOP ANOMALIES")
            for i, anomaly in enumerate(ml['anomalies']['details'][:3], 1):
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(anomaly['severity'], '⚪')
                
                print(f"  {i}. {severity_emoji} {anomaly['pattern_name']} ({anomaly['severity']})")
                print(f"     File: {anomaly['file']}:{anomaly['line']}")
                print(f"     Score: {anomaly['anomaly_score']:.2f}/1.0")
                print(f"     Reason: {anomaly['reason']}")
        
        print("\n" + "="*80)
    
    def save_report(self, output_dir: str):
        """Save analysis results to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save full results
        results_file = os.path.join(output_dir, 'ml_analysis_results.json')
        with open(results_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        print(f"💾 Results saved to {results_file}")
        
        # Save recommendations
        if self.recommendations:
            recs_file = os.path.join(output_dir, 'ml_recommendations.json')
            with open(recs_file, 'w') as f:
                json.dump(self.recommendations, f, indent=2, default=str)
            print(f"💾 Recommendations saved to {recs_file}")
        
        # Save model
        if self.ml_engine.learner.patterns:
            model_file = os.path.join(output_dir, 'ml_model.json')
            self.ml_engine.save_model(model_file)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of analysis results."""
        if not self.analysis_results:
            return {'status': 'No analysis run yet'}
        
        return {
            'codebase': self.analysis_results['metadata']['codebase'],
            'total_patterns': self.ml_engine.analysis_results['summary']['total_patterns'],
            'anomalies': self.ml_engine.analysis_results['anomalies']['count'],
            'recommendations': len(self.recommendations),
            'documentation_gaps': self.ml_engine.analysis_results['summary']['documentation_gaps'],
            'critical_items': len(self.ml_engine.analysis_results['categorization']['critical_path']),
            'timestamp': self.analysis_results['metadata']['timestamp']
        }


def run_integrated_analysis(codebase_path: str, output_dir: Optional[str] = None,
                           file_ext: str = '.py', max_workers: int = 8) -> Dict:
    """
    Convenience function to run complete analysis.
    
    Args:
        codebase_path: Path to codebase to analyze
        output_dir: Directory to save results (optional)
        file_ext: File extension to analyze (default: .py)
        max_workers: Number of parallel workers (default: 8)
    
    Returns:
        Analysis results dictionary
    """
    agent = IntegratedPatternAnalysisAgent(codebase_path)
    results = agent.analyze(file_ext=file_ext, max_workers=max_workers)
    
    agent.print_full_report()
    
    if output_dir:
        agent.save_report(output_dir)
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Integrated ML Pattern Recognition Analysis'
    )
    parser.add_argument('codebase_path', help='Path to codebase to analyze')
    parser.add_argument('--output', '-o', help='Output directory for results')
    parser.add_argument('--ext', '-e', default='.py', help='File extension to analyze')
    parser.add_argument('--workers', '-w', type=int, default=8, help='Number of parallel workers')
    
    args = parser.parse_args()
    
    # Run analysis
    results = run_integrated_analysis(
        args.codebase_path,
        output_dir=args.output,
        file_ext=args.ext,
        max_workers=args.workers
    )
    
    print(f"\n✅ Analysis complete!")
