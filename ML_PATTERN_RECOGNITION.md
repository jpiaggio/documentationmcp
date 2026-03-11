# Machine Learning-Based Pattern Recognition

## Overview

The ML-Based Pattern Recognition feature uses machine learning techniques to automatically learn from your codebase and provide intelligent insights:

### Key Capabilities

1. **Pattern Learning** - Train models on extracted code patterns to improve analysis accuracy over time
2. **Anomaly Detection** - Identify unusual code patterns that might indicate bugs or security issues  
3. **Importance Categorization** - Automatically categorize code by business importance (critical path, hot path, utilities, etc.)
4. **Documentation Prediction** - Predict which patterns need documentation and suggest what style to use based on similar code

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Integrated Pattern Analysis Agent               │
├─────────────────────────────────────────────────────────┤
│  • Cartographer Agent (Code Structure Extraction)       │
│  • Semantic Analyzer (Code Understanding)               │
│  • ML Pattern Recognition Engine                        │
│    - Pattern Learner                                    │
│    - Anomaly Detector                                   │
│    - Importance Categorizer                             │
│    - Documentation Predictor                            │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. PatternLearner

Learns and trains on extracted code patterns.

**Features:**
- Extracts code features (complexity, keywords, documentation, etc.)
- Trains clustering models (K-Means) on patterns
- Calculates pattern frequency and similarity
- Saves/loads trained models for persistence

**Usage:**
```python
from ml_pattern_recognition import PatternLearner

learner = PatternLearner()

# Add patterns from code analysis
pattern = learner.add_pattern(
    code_snippet,
    pattern_type='business_logic',
    file_path='example.py',
    line_number=10,
    metadata={'name': 'validate_payment', 'documented': True}
)

# Train on collected patterns
learner.train(min_patterns=10)

# Save model for future use
learner.save_model('ml_model.json')
```

**Extracted Features:**
- `lines_of_code` - Code length
- `cyclomatic_complexity` - Decision complexity
- `nesting_depth` - Control flow nesting
- `has_error_handling` - Try/except blocks
- `has_validation` - Validation logic
- `has_logging` - Logging calls
- `has_comments` - Comment presence
- `has_business_keywords` - Domain language
- `has_external_calls` - External integrations
- `has_type_hints` - Type annotations
- `has_docstring` - Documentation presence

### 2. AnomalyDetector

Detects unusual code patterns that might indicate bugs.

**Detection Methods:**
- Isolation Forest algorithm for outlier detection
- Analyzes complexity, validation, error handling
- Flags undocumented code with many external calls
- Detects unusual nesting patterns

**Severity Levels:**
- `critical` (score > 0.9) - Requires immediate review
- `high` (score > 0.8) - Should be reviewed
- `medium` (score > 0.7) - Consider reviewing
- `low` (score > 0.6) - Monitor

**Usage:**
```python
from ml_pattern_recognition import AnomalyDetector

detector = AnomalyDetector(sensitivity=0.75)

# Detect anomalies in patterns
anomalies = detector.detect_anomalies(patterns_dict)

for anomaly in anomalies:
    print(f"{anomaly['pattern_name']}: {anomaly['reason']}")
    print(f"Score: {anomaly['anomaly_score']}")
```

### 3. ImportanceCategorizer

Categorizes code by business importance.

**Categories:**

| Category | Importance | Description |
|----------|-----------|-------------|
| `critical_path` | ⭐⭐⭐⭐⭐ | Customer-facing, must work correctly |
| `hot_path` | ⭐⭐⭐⭐ | Performance-sensitive code |
| `business_logic` | ⭐⭐⭐ | Core business rules and workflows |
| `integration` | ⭐⭐⭐ | External API/service calls |
| `utility` | ⭐⭐ | Helper functions, general utilities |
| `infrastructure` | ⭐⭐ | Logging, monitoring, configuration |

**Importance Score Factors:**
- Business keyword frequency (+30%)
- External integration calls (+20%)
- Error handling presence (+15%)
- Validation logic (+15%)
- Pattern frequency usage (+5%)

**Usage:**
```python
from ml_pattern_recognition import ImportanceCategorizer

categorizer = ImportanceCategorizer()

# Categorize patterns
categories = categorizer.categorize(patterns_dict)

# Get documentation priority
priority_items = categorizer.get_documentation_priority()
for item in priority_items:
    print(f"{item['category']}: {item['name']}")
```

### 4. DocumentationPredictor

Predicts which patterns need documentation and suggests style.

**Prediction Strategy:**
- Finds similar patterns using TF-IDF vectorization
- Calculates cosine similarity between code
- Suggests documentation style based on similarity to documented patterns

**Doc Style Suggestions:**
- `same_as_similar` (similarity > 0.9) - Use exact same format
- `similar_with_variations` (similarity > 0.7) - Adapt from similar pattern
- `custom` (similarity ≤ 0.7) - Custom documentation needed

**Usage:**
```python
from ml_pattern_recognition import DocumentationPredictor

predictor = DocumentationPredictor()

# Predict missing documentation
predictions = predictor.predict_missing_docs(patterns_dict)

for pred in predictions:
    print(f"Pattern: {pred['pattern_name']}")
    print(f"Similar: {pred['similar_documented_patterns'][0]['pattern']}")
    print(f"Style: {pred['suggested_doc_style']}")
```

## Complete Analysis Pipeline

### Using the Integrated Agent

The easiest way to run complete analysis:

```python
from agents.ml_integrated_agent import run_integrated_analysis

# Run analysis
results = run_integrated_analysis(
    codebase_path='/path/to/project',
    output_dir='./ml_results',
    file_ext='.py',
    max_workers=8
)

# Results include:
# - Extraction results (code structure)
# - ML analysis (patterns, anomalies, categories)
# - Recommendations (actionable insights)
```

### Step-by-Step Analysis

```python
from agents.ml_integrated_agent import IntegratedPatternAnalysisAgent

# Create agent
agent = IntegratedPatternAnalysisAgent(codebase_path)

# Run full analysis
results = agent.analyze(file_ext='.py', max_workers=8)

# Print comprehensive report
agent.print_full_report()

# Save results
agent.save_report('output_directory')

# Get summary
summary = agent.get_summary()
```

## Example Analysis Output

### Anomaly Detection Results
```json
{
  "anomalies": [
    {
      "pattern_name": "process_payment",
      "severity": "high",
      "anomaly_score": 0.82,
      "reason": "Missing error handling; Business logic without comments",
      "file": "payments.py",
      "line": 45
    }
  ]
}
```

### Categorization Results
```json
{
  "categorization": {
    "critical_path": 5,
    "hot_path": 12,
    "business_logic": 45,
    "integration": 8,
    "utility": 120,
    "infrastructure": 30
  }
}
```

### Documentation Predictions
```json
{
  "predictions": [
    {
      "pattern_name": "validate_order",
      "pattern_type": "business_logic",
      "documented": false,
      "similar_documented_patterns": [
        {
          "pattern": "validate_payment",
          "similarity": 0.87,
          "file": "validators.py"
        }
      ],
      "suggested_doc_style": "similar_with_variations"
    }
  ]
}
```

## Machine Learning Models

### K-Means Clustering

Groups similar patterns into clusters:
- Automatically determines number of clusters (based on pattern count)
- Creates pattern clusters for code organization insights
- Identifies patterns that could be consolidated

**Cluster Information:**
- Cluster ID and member patterns
- Importance level (critical, high, medium, low)
- Documentation gap percentage

Example:
```
Cluster 0 (critical): 12 members, 25% gaps
  - validate_payment
  - process_order
  - authenticate_user

Cluster 1 (high): 8 members, 50% gaps
  - validate_email
  - format_phone
  - parse_date
```

### Isolation Forest (Anomaly Detection)

Detects outlier patterns using ensemble method:
- Builds isolation trees to separate anomalies
- Handles high-dimensional feature spaces
- Adapts sensitivity threshold (0-1)

**Anomaly Score Interpretation:**
- Score = 1.0: Definite anomaly
- Score > 0.8: Likely anomaly
- Score 0.6-0.8: Possible anomaly
- Score < 0.6: Normal pattern

## Configuration & Tuning

### Sensitivity Levels

```python
# More sensitive - catches more anomalies
detector = AnomalyDetector(sensitivity=0.9)

# Default
detector = AnomalyDetector(sensitivity=0.75)

# Less sensitive - fewer false positives
detector = AnomalyDetector(sensitivity=0.5)
```

### Learned Thresholds

The PatternLearner automatically learns thresholds during training:

```python
learner.learned_thresholds = {
    'anomaly': 0.7,              # Anomaly score threshold
    'importance_high': 0.7,       # Importance score for "high"
    'importance_medium': 0.4,     # Importance score for "medium"
}
```

### Model Persistence

Save trained models for reuse across analyses:

```python
# Save model
learner.save_model('my_model.json')

# Load model in future runs
learner = PatternLearner('my_model.json')
```

## Integration with Existing Tools

### With Cartographer Agent
```python
from agents.cartographer_agent import cartographer_agent
from ml_pattern_recognition import PatternLearner

# Extract code structure
cypher_statements = cartographer_agent(codebase_path)

# Create patterns from extraction
learner = PatternLearner()
for statement in cypher_statements:
    # Parse statement and add as pattern
    ...
```

### With Semantic Analyzer
```python
from agents.semantic_analyzer import SemanticAnalyzer
from ml_pattern_recognition import PatternLearner

# Perform semantic analysis
analyzer = SemanticAnalyzer()
for file in files:
    analysis = analyzer.analyze(file)
    
    # Extract patterns
    learner.add_pattern(...)
```

## Requirements & Dependencies

### Required Packages
```bash
pip install scikit-learn numpy scipy
```

### Optional for Enhanced Features
```bash
pip install pandas matplotlib seaborn  # For advanced analytics
pip install tree-sitter tree-sitter-python  # For code parsing
```

## Best Practices

### 1. Train on Sufficient Data
- Minimum 5-10 patterns for basic clustering
- 50+ patterns recommended for reliable models
- 100+ patterns for production use

### 2. Regular Model Updates
```python
# Periodically retrain as codebase grows
if len(learner.patterns) % 50 == 0:
    learner.train()
    learner.save_model('model.json')
```

### 3. Review Anomalies Carefully
- High severity anomalies need immediate review
- Some anomalies are intentional (performance optimizations)
- Use as guidance, not absolute rules

### 4. Prioritize Documentation
- Focus on critical path first
- Then hot path and business logic
- Follow predicted doc styles for consistency

### 5. Monitor Pattern Trends
```python
# Track pattern frequencies over time
for pattern in learner.patterns:
    print(f"{pattern.name}: frequency {pattern.frequency}")
```

## Troubleshooting

### scikit-learn Not Available
```
⚠️  scikit-learn not installed
Solution: pip install scikit-learn
```

If scikit-learn is unavailable:
- Basic pattern learning still works (frequency tracking)
- Anomaly detection disabled
- Clustering/vectorization disabled
- Documentation prediction disabled

### Insufficient Patterns
```
⚠️  Not enough patterns to train (3/10)
Add more patterns to the learner before calling train()
```

### Memory Issues with Large Codebases
```python
# Process in batches
for batch in chunks(patterns, 100):
    learner.train(batch)
```

## Examples

### Example 1: Analyze a Python Project

```bash
# Run from command line
python agents/ml_integrated_agent.py /path/to/project --output results/ --ext .py

# Run programmatically
from agents.ml_integrated_agent import run_integrated_analysis

results = run_integrated_analysis('/path/to/project', output_dir='./results')
```

### Example 2: Custom Pattern Analysis

```python
from ml_pattern_recognition import MLPatternRecognitionEngine

engine = MLPatternRecognitionEngine()

# Add custom patterns
for code_snippet in my_patterns:
    engine.learner.add_pattern(
        code_snippet,
        'custom_type',
        'file.py',
        line_no,
        metadata
    )

# Analyze
results = engine.analyze_patterns({})
engine.print_report()
engine.save_results('analysis.json')
```

### Example 3: Anomaly Review Workflow

```python
from ml_pattern_recognition import AnomalyDetector

detector = AnomalyDetector(sensitivity=0.8)
anomalies = detector.detect_anomalies(patterns)

# Group by severity
critical = [a for a in anomalies if a['severity'] == 'critical']
high = [a for a in anomalies if a['severity'] == 'high']

print(f"Review {len(critical)} critical issues first")
print(f"Then address {len(high)} high priority issues")
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Add pattern | O(1) | O(f) where f = features |
| Train | O(n*f*log n) | O(n) |
| Detect anomalies | O(n) | O(n) |
| Categorize | O(n) | O(1) |
| Predict docs | O(n²) | O(n) |

Where `n` = number of patterns, `f` = number of features

## See Also

- [Semantic Analysis Guide](SEMANTIC_ANALYSIS_GUIDE.md)
- [Business Journey Analysis](BUSINESS_JOURNEY_README.md)
- [Quick Reference](QUICK_REFERENCE.md)
