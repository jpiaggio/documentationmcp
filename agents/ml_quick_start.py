"""
ML Pattern Recognition Quick Start

This script demonstrates the ML Pattern Recognition feature:
- Training on extracted patterns
- Detecting anomalies in code
- Categorizing code by business importance
- Predicting missing documentation
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ml_pattern_recognition import (
    MLPatternRecognitionEngine,
    PatternLearner,
    CodePattern,
    AnomalyDetector,
    ImportanceCategorizer,
    DocumentationPredictor
)


def demo_pattern_learner():
    """Demonstrate pattern learning capabilities."""
    print("\n" + "="*70)
    print("1️⃣  PATTERN LEARNER DEMO")
    print("="*70)
    
    learner = PatternLearner()
    
    # Example patterns to learn
    patterns_data = [
        {
            'code': '''
def validate_payment(amount, currency):
    if amount <= 0:
        raise ValueError("Invalid amount")
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported currency")
    return True
''',
            'type': 'business_logic',
            'file': 'payment_service.py',
            'line': 10,
            'metadata': {'name': 'validate_payment', 'documented': True}
        },
        {
            'code': '''
def process_order(order_id):
    try:
        order = db.get_order(order_id)
        log.info(f"Processing order {order_id}")
        return order.finalize()
    except Exception as e:
        log.error(f"Failed to process order: {e}")
        return None
''',
            'type': 'business_logic',
            'file': 'order_service.py',
            'line': 45,
            'metadata': {'name': 'process_order', 'documented': True}
        }
    ]
    
    print("\n📚 Adding patterns to learner...")
    for pattern_data in patterns_data:
        pattern = learner.add_pattern(
            pattern_data['code'],
            pattern_data['type'],
            pattern_data['file'],
            pattern_data['line'],
            pattern_data['metadata']
        )
        print(f"  ✓ Added: {pattern.name} ({pattern.pattern_type})")
        print(f"    Complexity: {pattern.code_features['cyclomatic_complexity']}")
        print(f"    Has documentation: {pattern.documented}")
    
    print(f"\n📊 Learner Status:")
    print(f"  Total patterns: {len(learner.patterns)}")
    print(f"  Pattern types: {set(p.pattern_type for p in learner.patterns.values())}")


def demo_anomaly_detector():
    """Demonstrate anomaly detection capabilities."""
    print("\n" + "="*70)
    print("2️⃣  ANOMALY DETECTOR DEMO")
    print("="*70)
    
    learner = PatternLearner()
    detector = AnomalyDetector(sensitivity=0.7)
    
    # Create patterns - some normal, some anomalous
    patterns_data = [
        # Normal patterns
        ('GET /api/users', 'integration', 'api.py', 10, {'name': 'get_users'}),
        ('POST /api/orders', 'integration', 'api.py', 20, {'name': 'create_order'}),
        ('def validate(x): return x > 0', 'validation', 'utils.py', 30, {'name': 'validate'}),
        
        # Anomalous pattern - complex without comments or error handling
        ('''
def process_data(data):
    for item in data:
        for sub in item:
            for x in sub:
                if x > 10:
                    y = x * 2
                    z = calculate(y)
                    if z < 100:
                        log_result(z)
                    else:
                        retry_with_backup(z)
''', 'business_logic', 'processor.py', 50, {'name': 'process_data'})
    ]
    
    print("\n🔍 Creating patterns for anomaly detection...")
    for code, ptype, file, line, meta in patterns_data:
        pattern = learner.add_pattern(code, ptype, file, line, meta)
        print(f"  ✓ {pattern.name}")
    
    print(f"\n🚨 Detecting anomalies...")
    anomalies = detector.detect_anomalies(learner.patterns)
    
    if anomalies:
        print(f"\n⚠️  Found {len(anomalies)} anomalies:")
        for anomaly in anomalies[:5]:
            print(f"\n  Pattern: {anomaly['pattern_name']}")
            print(f"  Severity: {anomaly['severity']}")
            print(f"  Score: {anomaly['anomaly_score']:.2f}")
            print(f"  Reason: {anomaly['reason']}")
    else:
        print("\n✅ No significant anomalies detected")


def demo_importance_categorizer():
    """Demonstrate code categorization by importance."""
    print("\n" + "="*70)
    print("3️⃣  IMPORTANCE CATEGORIZER DEMO")
    print("="*70)
    
    learner = PatternLearner()
    categorizer = ImportanceCategorizer()
    
    # Create various patterns
    patterns_data = [
        ('Payment processing', 'business_logic', 'payments.py', 10, {'name': 'process_payment'}),
        ('Query optimization', 'utility', 'database.py', 50, {'name': 'optimize_query'}),
        ('Cache management', 'hot_path', 'cache.py', 100, {'name': 'manage_cache'}),
        ('External API call', 'integration', 'api_client.py', 200, {'name': 'call_external_api'}),
        ('Logging setup', 'infrastructure', 'logger.py', 300, {'name': 'setup_logging'}),
    ]
    
    print("\n📊 Creating patterns for categorization...")
    for code, ptype, file, line, meta in patterns_data:
        pattern = learner.add_pattern(code, ptype, file, line, meta)
        print(f"  ✓ {pattern.name} ({ptype})")
    
    print(f"\n🎯 Categorizing by business importance...")
    categories = categorizer.categorize(learner.patterns)
    
    for category, items in categories.items():
        if items:
            print(f"\n  {category.upper()} ({len(items)} patterns)")
            for item in items:
                print(f"    • {item['name']} (score: {item['importance_score']:.2f})")
    
    print(f"\n📝 Documentation Priority:")
    priority = categorizer.get_documentation_priority()
    for item in priority[:5]:
        print(f"  {item['category']:15s}: {item['name']}")


def demo_documentation_predictor():
    """Demonstrate documentation prediction."""
    print("\n" + "="*70)
    print("4️⃣  DOCUMENTATION PREDICTOR DEMO")
    print("="*70)
    
    try:
        learner = PatternLearner()
        predictor = DocumentationPredictor()
        
        # Create patterns - some with docs, some without
        patterns_data = [
            ('''
def validate_email(email):
    """Validates email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
''', 'validation', 'validators.py', 10, {'name': 'validate_email', 'documented': True}),
            
            ('''
def validate_phone(phone):
    pattern = r'^\\+?1?\\d{9,15}$'
    return bool(re.match(pattern, phone))
''', 'validation', 'validators.py', 50, {'name': 'validate_phone', 'documented': False}),
        ]
        
        print("\n📝 Creating patterns...")
        for code, ptype, file, line, meta in patterns_data:
            pattern = learner.add_pattern(code, ptype, file, line, meta)
            doc_status = "✓ documented" if meta['documented'] else "✗ undocumented"
            print(f"  {pattern.name} ({doc_status})")
        
        print(f"\n🤖 Predicting missing documentation...")
        predictions = predictor.predict_missing_docs(learner.patterns)
        
        if predictions:
            print(f"\n✓ {len(predictions)} patterns need documentation")
            for pred in predictions[:3]:
                print(f"\n  Pattern: {pred['pattern_name']}")
                print(f"  Type: {pred['pattern_type']}")
                if pred['similar_documented_patterns']:
                    print(f"  Similar documented patterns:")
                    for similar in pred['similar_documented_patterns'][:2]:
                        print(f"    • {similar['pattern']} (similarity: {similar['similarity']:.2f})")
                print(f"  Suggested doc style: {pred['suggested_doc_style']}")
        else:
            print("\n✅ All patterns are documented!")
    
    except Exception as e:
        print(f"\n⚠️  Note: {e}")
        print("   Documentation prediction requires scikit-learn")


def demo_complete_engine():
    """Demonstrate the complete ML Pattern Recognition Engine."""
    print("\n" + "="*70)
    print("🤖 COMPLETE ML PATTERN RECOGNITION ENGINE DEMO")
    print("="*70)
    
    engine = MLPatternRecognitionEngine()
    
    # Simulate some analysis
    analysis_data = {
        'files_analyzed': 42,
        'total_lines': 15000,
        'patterns_found': {}
    }
    
    # Add example patterns
    learner = engine.learner
    patterns_data = [
        ('Payment validation', 'business_logic', 'payments.py', 10, {'name': 'validate_payment'}),
        ('Order processing', 'business_logic', 'orders.py', 50, {'name': 'process_order'}),
        ('User authentication', 'business_logic', 'auth.py', 100, {'name': 'authenticate'}),
        ('Database query', 'hot_path', 'db.py', 200, {'name': 'query_users'}),
        ('Cache lookup', 'utility', 'cache.py', 250, {'name': 'get_from_cache'}),
    ]
    
    print("\n📚 Building pattern dataset...")
    for code, ptype, file, line, meta in patterns_data:
        pattern = learner.add_pattern(code, ptype, file, line, meta)
        print(f"  ✓ {pattern.name}")
    
    print(f"\n🤖 Running complete analysis...")
    results = engine.analyze_patterns(analysis_data)
    
    # Print report
    engine.print_report()
    
    print(f"\n📊 Analysis Summary:")
    print(f"  Total patterns: {results['summary']['total_patterns']}")
    print(f"  Anomalies: {results['anomalies']['count']}")
    print(f"  Clusters: {results['model']['clusters']}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 ML PATTERN RECOGNITION - QUICK START DEMO")
    print("="*70)
    
    try:
        # Run all demos
        demo_pattern_learner()
        demo_anomaly_detector()
        demo_importance_categorizer()
        demo_documentation_predictor()
        demo_complete_engine()
        
        print("\n" + "="*70)
        print("✅ All demos completed successfully!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Run: python agents/ml_integrated_agent.py /path/to/codebase")
        print("  2. Review results in ml_analysis_results.json")
        print("  3. Check recommendations in ml_recommendations.json")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
