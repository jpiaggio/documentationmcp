"""
Machine Learning-Based Pattern Recognition Engine

Train on extracted patterns to improve future accuracy:
- Learn business patterns from codebase over time
- Detect anomalies in code (unusual business logic that might indicate bugs)
- Categorize code by business importance (hot path vs utility)
- Predict missing documentation based on similar patterns
"""

import json
import pickle
import os
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


@dataclass
class CodePattern:
    """Represents a discovered code pattern."""
    pattern_id: str
    pattern_type: str  # 'business_logic', 'utility', 'integration', 'validation', etc.
    name: str
    file_path: str
    line_number: int
    code_features: Dict[str, Any]  # Feature vector for ML
    frequency: int = 1  # How often this pattern appears
    confidence: float = 0.0  # ML confidence score
    importance_score: float = 0.0  # Business importance (0-1)
    anomaly_score: float = 0.0  # Anomaly probability (0-1)
    documented: bool = False
    related_patterns: List[str] = None  # IDs of similar patterns


@dataclass
class PatternCluster:
    """Represents a cluster of similar patterns."""
    cluster_id: int
    pattern_type: str
    members: List[str]  # Pattern IDs
    centroid_features: Dict[str, float]
    importance_level: str  # 'critical', 'high', 'medium', 'low'
    documentation_gap: float  # Percentage of undocumented patterns


class PatternLearner:
    """Learns patterns from code analysis results to improve future accuracy."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.patterns: Dict[str, CodePattern] = {}
        self.clusters: Dict[int, PatternCluster] = {}
        self.pattern_history: List[Dict] = []
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.vectorizer = TfidfVectorizer(max_features=50, ngram_range=(1, 2))
        self.kmeans = None
        self.feature_importance = {}
        self.learned_thresholds = {
            'anomaly': 0.7,
            'importance_high': 0.7,
            'importance_medium': 0.4,
        }
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def extract_code_features(self, code_snippet: str, metadata: Dict) -> Dict[str, Any]:
        """Extract features from code for ML training."""
        features = {
            # Code complexity
            'lines_of_code': len(code_snippet.split('\n')),
            'cyclomatic_complexity': self._calculate_complexity(code_snippet),
            'nesting_depth': self._calculate_nesting(code_snippet),
            
            # Pattern indicators
            'has_error_handling': 'try' in code_snippet or 'except' in code_snippet,
            'has_validation': any(kw in code_snippet.lower() for kw in 
                                 ['validate', 'check', 'verify', 'assert']),
            'has_logging': 'log' in code_snippet.lower(),
            'has_comments': '#' in code_snippet or '"""' in code_snippet,
            
            # Business indicators
            'has_business_keywords': len([kw for kw in 
                ['user', 'order', 'payment', 'transaction', 'customer'] 
                if kw in code_snippet.lower()]),
            'has_external_calls': len([kw for kw in 
                ['http', 'api', 'request', 'webhook', 'kafka'] 
                if kw in code_snippet.lower()]),
            
            # Code quality
            'has_type_hints': ':' in code_snippet and '->' in code_snippet,
            'has_docstring': '"""' in code_snippet or "'''" in code_snippet,
            'code_text': code_snippet,  # For text vectorization
            
            # Metadata
            'metadata': metadata
        }
        return features
    
    def _calculate_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity."""
        complexity = 1
        keywords = ['if', 'elif', 'else', 'for', 'while', 'except', 'and', 'or']
        for keyword in keywords:
            complexity += code.lower().count(f' {keyword} ')
        return complexity
    
    def _calculate_nesting(self, code: str) -> int:
        """Calculate nesting depth."""
        max_depth = 0
        current_depth = 0
        for line in code.split('\n'):
            spaces = len(line) - len(line.lstrip())
            depth = spaces // 4  # Assuming 4-space indentation
            max_depth = max(max_depth, depth)
        return max_depth
    
    def add_pattern(self, code_snippet: str, pattern_type: str, 
                    file_path: str, line_number: int, metadata: Dict) -> CodePattern:
        """Add a discovered pattern to the learning model."""
        pattern_id = f"{file_path}:{line_number}:{pattern_type}"
        
        # Extract features
        features = self.extract_code_features(code_snippet, metadata)
        
        # Create pattern object
        pattern = CodePattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            name=metadata.get('name', 'unnamed'),
            file_path=file_path,
            line_number=line_number,
            code_features=features,
            documented=metadata.get('documented', False)
        )
        
        # Check if we've seen similar patterns
        pattern.frequency = self._get_pattern_frequency(pattern_type, features)
        
        self.patterns[pattern_id] = pattern
        self.pattern_history.append({
            'timestamp': datetime.now().isoformat(),
            'pattern_id': pattern_id,
            'action': 'added'
        })
        
        return pattern
    
    def _get_pattern_frequency(self, pattern_type: str, features: Dict) -> int:
        """Get how many similar patterns exist."""
        count = 1
        for existing_pattern in self.patterns.values():
            if existing_pattern.pattern_type == pattern_type:
                # Simple similarity: comparing feature keys
                if set(existing_pattern.code_features.keys()) == set(features.keys()):
                    count += 1
        return count
    
    def train(self, min_patterns: int = 10) -> bool:
        """Train ML models on collected patterns."""
        if len(self.patterns) < min_patterns:
            print(f"⚠️  Not enough patterns to train ({len(self.patterns)}/{min_patterns})")
            return False
        
        print(f"📚 Training on {len(self.patterns)} patterns...")
        
        try:
            # Prepare training data
            pattern_ids = list(self.patterns.keys())
            code_texts = []
            feature_vectors = []
            
            for pid in pattern_ids:
                pattern = self.patterns[pid]
                code_texts.append(pattern.code_features.get('code_text', ''))
                
                # Build feature vector
                features = [
                    pattern.code_features.get('lines_of_code', 0),
                    pattern.code_features.get('cyclomatic_complexity', 0),
                    pattern.code_features.get('nesting_depth', 0),
                    int(pattern.code_features.get('has_error_handling', False)),
                    int(pattern.code_features.get('has_validation', False)),
                    int(pattern.code_features.get('has_logging', False)),
                    int(pattern.code_features.get('has_comments', False)),
                    pattern.code_features.get('has_business_keywords', 0),
                    pattern.code_features.get('has_external_calls', 0),
                    int(pattern.code_features.get('has_type_hints', False)),
                    int(pattern.code_features.get('has_docstring', False)),
                ]
                feature_vectors.append(features)
            
            # Scale features
            feature_vectors = np.array(feature_vectors)
            feature_vectors_scaled = self.scaler.fit_transform(feature_vectors)
            
            # Vectorize code text
            code_vectors = self.vectorizer.fit_transform(code_texts).toarray()
            
            # Combine features and text vectors
            combined_vectors = np.hstack([feature_vectors_scaled, code_vectors])
            
            # Train clustering model
            n_clusters = min(5, max(2, len(pattern_ids) // 10))
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = self.kmeans.fit_predict(combined_vectors)
            
            # Create clusters
            for cluster_id in range(n_clusters):
                member_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                member_ids = [pattern_ids[i] for i in member_indices]
                
                # Determine cluster importance
                member_patterns = [self.patterns[pid] for pid in member_ids]
                avg_importance = np.mean([p.frequency for p in member_patterns])
                
                if avg_importance > 3:
                    importance = 'critical'
                elif avg_importance > 2:
                    importance = 'high'
                elif avg_importance > 1:
                    importance = 'medium'
                else:
                    importance = 'low'
                
                cluster = PatternCluster(
                    cluster_id=cluster_id,
                    pattern_type=member_patterns[0].pattern_type if member_patterns else 'unknown',
                    members=member_ids,
                    centroid_features=self.kmeans.cluster_centers_[cluster_id].tolist() if self.kmeans else [],
                    importance_level=importance,
                    documentation_gap=self._calculate_doc_gap(member_ids)
                )
                self.clusters[cluster_id] = cluster
            
            print(f"✅ Training complete! Created {len(self.clusters)} clusters")
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
    
    def _calculate_doc_gap(self, pattern_ids: List[str]) -> float:
        """Calculate percentage of undocumented patterns in a group."""
        if not pattern_ids:
            return 0.0
        documented = sum(1 for pid in pattern_ids if self.patterns[pid].documented)
        return 1.0 - (documented / len(pattern_ids))
    
    def save_model(self, path: str):
        """Serialize the trained model."""
        model_data = {
            'patterns': {k: asdict(v) for k, v in self.patterns.items()},
            'clusters': {k: asdict(v) for k, v in self.clusters.items()},
            'scaler_params': {
                'mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else [],
                'scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else []
            },
            'learned_thresholds': self.learned_thresholds
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2, default=str)
        print(f"💾 Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a trained model."""
        try:
            with open(path, 'r') as f:
                model_data = json.load(f)
            
            # Restore patterns
            for pid, pdata in model_data.get('patterns', {}).items():
                pattern = CodePattern(**pdata)
                self.patterns[pid] = pattern
            
            print(f"✅ Loaded {len(self.patterns)} patterns from model")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")


class AnomalyDetector:
    """Detects anomalies in code that might indicate bugs or unusual patterns."""
    
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity  # 0-1, higher = more sensitive
        self.detector = None if not HAS_SKLEARN else IsolationForest(contamination=0.1)
        self.anomalies: List[Dict] = []
    
    def detect_anomalies(self, patterns: Dict[str, CodePattern]) -> List[Dict]:
        """Detect unusual patterns that might be bugs."""
        if not HAS_SKLEARN or not patterns:
            return []
        
        print(f"🔍 Analyzing {len(patterns)} patterns for anomalies...")
        
        try:
            # Build feature matrix
            feature_matrix = self._build_anomaly_features(patterns)
            
            # Detect anomalies
            anomaly_labels = self.detector.fit_predict(feature_matrix)
            anomaly_scores = self.detector.score_samples(feature_matrix)
            
            # Collect results
            pattern_list = list(patterns.values())
            for i, (pattern, score) in enumerate(zip(pattern_list, anomaly_scores)):
                # Normalize score to 0-1 range
                normalized_score = 1.0 / (1.0 + np.exp(score))  # Sigmoid normalization
                
                if normalized_score > (1.0 - self.sensitivity):
                    anomaly_info = {
                        'pattern_id': pattern.pattern_id,
                        'pattern_name': pattern.name,
                        'file': pattern.file_path,
                        'line': pattern.line_number,
                        'anomaly_score': float(normalized_score),
                        'pattern_type': pattern.pattern_type,
                        'reason': self._explain_anomaly(pattern, normalized_score),
                        'severity': self._get_severity(normalized_score)
                    }
                    self.anomalies.append(anomaly_info)
                    pattern.anomaly_score = normalized_score
            
            self.anomalies.sort(key=lambda x: x['anomaly_score'], reverse=True)
            print(f"⚠️  Found {len(self.anomalies)} anomalies")
            return self.anomalies
            
        except Exception as e:
            print(f"❌ Anomaly detection failed: {e}")
            return []
    
    def _build_anomaly_features(self, patterns: Dict[str, CodePattern]) -> np.ndarray:
        """Build feature matrix for anomaly detection."""
        features = []
        for pattern in patterns.values():
            feature_vec = [
                pattern.code_features.get('lines_of_code', 0),
                pattern.code_features.get('cyclomatic_complexity', 0),
                pattern.code_features.get('nesting_depth', 0),
                pattern.frequency,
                int(not pattern.code_features.get('has_comments', False)),  # Flag missing comments
                int(not pattern.code_features.get('has_error_handling', False)),  # Flag missing error handling
                int(not pattern.code_features.get('has_validation', False)),  # Flag missing validation
            ]
            features.append(feature_vec)
        
        return np.array(features)
    
    def _explain_anomaly(self, pattern: CodePattern, score: float) -> str:
        """Generate human-readable explanation for anomaly."""
        reasons = []
        
        if pattern.code_features.get('cyclomatic_complexity', 0) > 10:
            reasons.append("High cyclomatic complexity")
        
        if pattern.code_features.get('nesting_depth', 0) > 4:
            reasons.append("Deep nesting")
        
        if not pattern.code_features.get('has_error_handling', False):
            reasons.append("Missing error handling")
        
        if not pattern.code_features.get('has_validation', False) and pattern.pattern_type == 'business_logic':
            reasons.append("Business logic without validation")
        
        if pattern.code_features.get('has_business_keywords', 0) > 0 and not pattern.code_features.get('has_comments', False):
            reasons.append("Business logic without comments")
        
        if not reasons:
            reasons.append("Unusual pattern structure")
        
        return "; ".join(reasons)
    
    def _get_severity(self, score: float) -> str:
        """Classify anomaly severity."""
        if score > 0.9:
            return "critical"
        elif score > 0.8:
            return "high"
        elif score > 0.7:
            return "medium"
        else:
            return "low"


class ImportanceCategorizer:
    """Categorizes code by business importance (hot path vs utility)."""
    
    def __init__(self):
        self.categories = {
            'critical_path': [],      # User-facing, high frequency
            'hot_path': [],            # Performance sensitive
            'business_logic': [],      # Core business rules
            'integration': [],         # External integrations
            'utility': [],             # Helper functions
            'infrastructure': []       # Logging, monitoring, etc.
        }
    
    def categorize(self, patterns: Dict[str, CodePattern]) -> Dict[str, List[Dict]]:
        """Categorize patterns by business importance."""
        print(f"📊 Categorizing {len(patterns)} patterns by importance...")
        
        # Reset categories
        for key in self.categories:
            self.categories[key] = []
        
        for pattern in patterns.values():
            importance_score = self._calculate_importance(pattern)
            pattern.importance_score = importance_score
            
            category = self._assign_category(pattern, importance_score)
            
            pattern_info = {
                'id': pattern.pattern_id,
                'name': pattern.name,
                'file': pattern.file_path,
                'line': pattern.line_number,
                'importance_score': importance_score,
                'type': pattern.pattern_type,
                'documented': pattern.documented
            }
            
            self.categories[category].append(pattern_info)
        
        # Print summary
        for category, items in self.categories.items():
            if items:
                print(f"  {category}: {len(items)} patterns")
        
        return self.categories
    
    def _calculate_importance(self, pattern: CodePattern) -> float:
        """Calculate importance score (0-1)."""
        score = 0.0
        
        # Business relevance
        if pattern.code_features.get('has_business_keywords', 0) > 0:
            score += 0.3 + (pattern.code_features.get('has_business_keywords', 0) * 0.05)
        
        # External integrations
        if pattern.code_features.get('has_external_calls', 0) > 0:
            score += 0.2
        
        # Error handling
        if pattern.code_features.get('has_error_handling', False):
            score += 0.15
        
        # Validation
        if pattern.code_features.get('has_validation', False):
            score += 0.15
        
        # Frequency (how often the pattern is used)
        score += min(pattern.frequency * 0.05, 0.15)
        
        return min(score, 1.0)
    
    def _assign_category(self, pattern: CodePattern, score: float) -> str:
        """Assign pattern to a category."""
        # Check for specific keywords
        code_text = pattern.code_features.get('code_text', '').lower()
        
        # Critical path detection
        critical_keywords = ['payment', 'transaction', 'order', 'checkout', 'authenticate', 'authorize']
        if any(kw in code_text for kw in critical_keywords):
            return 'critical_path'
        
        # Hot path detection (performance sensitive)
        hot_keywords = ['cache', 'query', 'loop', 'iteration', 'batch', 'index']
        if any(kw in code_text for kw in hot_keywords) and pattern.code_features.get('cyclomatic_complexity', 0) > 3:
            return 'hot_path'
        
        # Business logic
        business_keywords = ['rule', 'validate', 'check', 'verify', 'workflow', 'process']
        if any(kw in code_text for kw in business_keywords):
            return 'business_logic'
        
        # Integration
        if pattern.code_features.get('has_external_calls', 0) > 0:
            return 'integration'
        
        # Infrastructure
        infra_keywords = ['log', 'metric', 'monitor', 'trace', 'debug', 'config']
        if any(kw in code_text for kw in infra_keywords):
            return 'infrastructure'
        
        # Default to utility
        return 'utility'
    
    def get_documentation_priority(self) -> List[Dict]:
        """Return patterns that need documentation, prioritized by importance."""
        undocumented = []
        
        # Prioritize: critical_path > hot_path > business_logic > integration > utility
        priority_order = ['critical_path', 'hot_path', 'business_logic', 'integration', 'utility', 'infrastructure']
        
        for category in priority_order:
            for pattern in self.categories[category]:
                if not pattern['documented']:
                    undocumented.append({
                        **pattern,
                        'category': category,
                        'documentation_priority': priority_order.index(category)
                    })
        
        return undocumented


class DocumentationPredictor:
    """Predicts missing documentation based on similar patterns."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 3)) if HAS_SKLEARN else None
        self.predictions: List[Dict] = []
    
    def predict_missing_docs(self, patterns: Dict[str, CodePattern]) -> List[Dict]:
        """Predict which patterns need documentation."""
        print(f"📝 Predicting missing documentation for {len(patterns)} patterns...")
        
        if not HAS_SKLEARN or not patterns:
            return []
        
        try:
            # Build vectors for code patterns
            code_texts = [p.code_features.get('code_text', '') for p in patterns.values()]
            pattern_ids = list(patterns.keys())
            
            # Vectorize
            vectors = self.vectorizer.fit_transform(code_texts)
            
            # Calculate similarity matrix
            similarity = cosine_similarity(vectors)
            
            # For each undocumented pattern, find similar documented patterns
            predictions = []
            for i, (pid, pattern) in enumerate(zip(pattern_ids, patterns.values())):
                if pattern.documented:
                    continue
                
                # Find similar patterns
                similarities = similarity[i]
                similar_indices = np.argsort(similarities)[::-1][1:6]  # Top 5 similar
                
                similar_docs = []
                for idx in similar_indices:
                    similar_pattern = list(patterns.values())[idx]
                    if similar_pattern.documented:
                        similar_docs.append({
                            'pattern': similar_pattern.name,
                            'similarity': float(similarities[idx]),
                            'file': similar_pattern.file_path,
                            'line': similar_pattern.line_number
                        })
                
                if similar_docs:
                    prediction = {
                        'pattern_id': pid,
                        'pattern_name': pattern.name,
                        'file': pattern.file_path,
                        'line': pattern.line_number,
                        'pattern_type': pattern.pattern_type,
                        'similar_documented_patterns': similar_docs,
                        'prediction_confidence': float(similar_docs[0]['similarity']) if similar_docs else 0.0,
                        'suggested_doc_style': self._suggest_doc_style(similar_docs[0] if similar_docs else None)
                    }
                    predictions.append(prediction)
            
            self.predictions = predictions
            print(f"📊 Predictions complete: {len(predictions)} patterns need documentation")
            return predictions
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return []
    
    def _suggest_doc_style(self, similar_doc: Optional[Dict]) -> str:
        """Suggest documentation style based on similar patterns."""
        if not similar_doc:
            return "detailed"
        
        similarity = similar_doc.get('similarity', 0)
        if similarity > 0.9:
            return "same_as_similar"
        elif similarity > 0.7:
            return "similar_with_variations"
        else:
            return "custom"


class MLPatternRecognitionEngine:
    """Main engine coordinating all ML pattern recognition components."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.learner = PatternLearner(model_path)
        self.anomaly_detector = AnomalyDetector(sensitivity=0.75)
        self.categorizer = ImportanceCategorizer()
        self.doc_predictor = DocumentationPredictor()
        self.analysis_results = {}
    
    def analyze_patterns(self, extracted_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive pattern analysis."""
        print("\n🤖 Starting ML Pattern Recognition Analysis...")
        
        # Extract patterns from analysis results
        self._extract_patterns_from_analysis(extracted_analysis)
        
        # Train on patterns if we have enough
        if len(self.learner.patterns) >= 5:
            self.learner.train()
        
        # Run analysis components
        anomalies = self.anomaly_detector.detect_anomalies(self.learner.patterns)
        categories = self.categorizer.categorize(self.learner.patterns)
        doc_predictions = self.doc_predictor.predict_missing_docs(self.learner.patterns)
        doc_priority = self.categorizer.get_documentation_priority()
        
        # Compile results
        self.analysis_results = {
            'summary': {
                'total_patterns': len(self.learner.patterns),
                'patterns_by_type': self._count_by_type(),
                'anomalies_found': len(anomalies),
                'documentation_gaps': len([p for p in self.learner.patterns.values() if not p.documented]),
                'timestamp': datetime.now().isoformat()
            },
            'anomalies': {
                'count': len(anomalies),
                'details': anomalies[:10]  # Top 10 anomalies
            },
            'categorization': {
                'critical_path': len(categories['critical_path']),
                'hot_path': len(categories['hot_path']),
                'business_logic': len(categories['business_logic']),
                'integration': len(categories['integration']),
                'utility': len(categories['utility']),
                'infrastructure': len(categories['infrastructure']),
                'details': categories
            },
            'documentation': {
                'prediction_count': len(doc_predictions),
                'priority_items': doc_priority[:15],  # Top 15 by priority
                'predictions': doc_predictions[:20]  # Top 20 predictions
            },
            'model': {
                'clusters': len(self.learner.clusters),
                'cluster_details': [asdict(c) for c in self.learner.clusters.values()]
            }
        }
        
        return self.analysis_results
    
    def _extract_patterns_from_analysis(self, analysis: Dict[str, Any]):
        """Extract patterns from code analysis results."""
        # This would integrate with cartographer_agent and semantic_analyzer results
        # For now, we show the structure
        print(f"🔍 Extracting patterns from analysis data...")
        # Implementation depends on the format of extracted_analysis
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count patterns by type."""
        counts = defaultdict(int)
        for pattern in self.learner.patterns.values():
            counts[pattern.pattern_type] += 1
        return dict(counts)
    
    def print_report(self):
        """Print a comprehensive analysis report."""
        if not self.analysis_results:
            print("❌ No analysis results available. Run analyze_patterns() first.")
            return
        
        print("\n" + "="*70)
        print("🤖 ML PATTERN RECOGNITION ANALYSIS REPORT")
        print("="*70)
        
        # Summary
        summary = self.analysis_results['summary']
        print(f"\n📊 SUMMARY")
        print(f"  Total Patterns Found:         {summary['total_patterns']}")
        print(f"  Anomalies Detected:           {self.analysis_results['anomalies']['count']}")
        print(f"  Documentation Gaps:           {summary['documentation_gaps']}")
        print(f"  Cluster Count:                {self.analysis_results['model']['clusters']}")
        
        # Pattern types
        print(f"\n📈 PATTERNS BY TYPE")
        for ptype, count in summary['patterns_by_type'].items():
            print(f"  {ptype:20s}: {count:3d}")
        
        # Anomalies
        if self.analysis_results['anomalies']['details']:
            print(f"\n⚠️  TOP ANOMALIES")
            for i, anomaly in enumerate(self.analysis_results['anomalies']['details'][:5], 1):
                print(f"  {i}. {anomaly['pattern_name']} ({anomaly['severity']})")
                print(f"     Score: {anomaly['anomaly_score']:.2f}")
                print(f"     Reason: {anomaly['reason']}")
        
        # Categorization
        cat = self.analysis_results['categorization']
        print(f"\n🎯 CATEGORIZATION")
        print(f"  Critical Path:    {cat['critical_path']:3d}")
        print(f"  Hot Path:         {cat['hot_path']:3d}")
        print(f"  Business Logic:   {cat['business_logic']:3d}")
        print(f"  Integration:      {cat['integration']:3d}")
        print(f"  Utility:          {cat['utility']:3d}")
        print(f"  Infrastructure:   {cat['infrastructure']:3d}")
        
        # Documentation priority
        docs = self.analysis_results['documentation']
        if docs['priority_items']:
            print(f"\n📝 DOCUMENTATION PRIORITY (Top 5)")
            for i, item in enumerate(docs['priority_items'][:5], 1):
                category = item.get('category', 'unknown')
                print(f"  {i}. {item['name']} ({category})")
                print(f"     File: {item['file']}:{item['line']}")
        
        print("\n" + "="*70)
    
    def save_results(self, output_path: str):
        """Save analysis results to file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        print(f"💾 Results saved to {output_path}")
    
    def save_model(self, model_path: str):
        """Save trained models."""
        self.learner.save_model(model_path)


if __name__ == '__main__':
    # Example usage
    print("ML Pattern Recognition Engine")
    print("This module should be integrated with cartographer_agent and semantic_analyzer")
    
    if HAS_SKLEARN:
        print("✅ scikit-learn is available")
    else:
        print("⚠️  scikit-learn not installed. Install with: pip install scikit-learn")
