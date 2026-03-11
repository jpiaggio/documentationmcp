# Deep LLM Integration Guide

**Status:** ✅ Production Ready  
**Version:** 2.0  
**Date:** March 2026

---

## Overview

This guide explains how to use **Deep LLM Integration** to understand code at the semantic level using Gemini and Claude. Instead of just extracting facts about code, the LLM asks:

- **"What is this function REALLY doing?"** (not just what the syntax says)
- **"Why does the business need this?"** (business impact, not mechanics)
- **"What could go wrong?"** (risk assessment)
- **"How should this be explained to non-technical people?"** (requirement gathering, stakeholder communication)

---

## What's New: Deep Semantic Analysis

### Before: Syntactic Analysis Only
```python
# Extract syntax facts
- Function name: process_order
- Parameters: order (Dict)
- Return type: Boolean
- If conditions: 3
- Raise statements: 2
```

### After: Syntactic + Semantic Analysis
```python
# Syntactic facts (same as before)
- Function name: process_order
- Parameters: order (Dict)

# NEW: Semantic understanding (from LLM)
- TRUE PURPOSE: "Validates order, charges customer, reserves inventory"
- BUSINESS VALUE: "Ensures only valid, paid orders proceed to fulfillment"
- RISKS: ["Payment processor timeout", "Inventory race condition"]
- EMBEDDED RULES: ["Amount must be > $0", "Customer must be verified"]
```

---

## Key Features

### 1. Semantic Function Analysis ✨
Understand what a function REALLY does at the business level.

```python
from agents.llm_rule_inference import LLMRuleInferenceEngine

engine = LLMRuleInferenceEngine(provider="gemini")  # or "claude"

analysis = engine.analyze_function_semantics(
    source_code=function_code,
    function_name="charge_customer",
    ask_specifically="What does this do from the payment system's perspective?"
)

print(analysis.true_purpose)  # "Charges customer's payment method and logs transaction"
print(analysis.business_value)  # "Enables revenue generation for orders"
print(analysis.key_risks)  # ["Payment processor down", "Fraud detection block"]
print(analysis.embedded_rules)  # ["Amount must be > 0", "Customer must have valid card"]
```

**What it analyzes:**
- True purpose (semantic intent, not mechanics)
- Business value and impact
- User perspective and experience
- Implementation strategy
- Complexity assessment
- Key risks and edge cases
- Data flow patterns
- External dependencies
- Embedded business rules
- Decision points and branching

---

### 2. Human-Readable Rule Explanation 📖
Convert extracted rules into language that non-technical people understand.

```python
# Before: Raw extracted rules
rules = [
    {"field": "age", "operator": ">=", "value": 18},
    {"precondition": "authenticate", "postcondition": "process_payment"}
]

# After: Human-readable explanations
explanations = engine.explain_rules_humanly(
    rules,
    domain_context="E-commerce order processing"
)

for explanation in explanations:
    print(f"Rule: {explanation.simple_explanation}")
    # "Customers must be at least 18 years old"
    
    print(f"Why: {explanation.business_context}")
    # "We're required to collect age verification for legal compliance"
    
    print(f"When: {explanation.when_it_applies}")
    # "When a customer creates an account"
    
    print(f"Examples: {explanation.positive_examples}")
    # ["Customer age 25", "Customer age 18", "Customer age 65"]
    
    print(f"Violations: {explanation.negative_examples}")
    # ["Customer age 17", "Customer age 12"]
    
    print(f"Impact: {explanation.implications}")
    # ["Account creation blocked", "Error message displayed"]
```

---

### 3. Business Logic Summarization 📊
Generate high-level summaries of complex code.

```python
# This is 50 lines of complex order processing code...
code = read_order_processor()

summary = engine.summarize_business_logic(
    code,
    file_context="Order management system",
    complexity_level="complex"
)

# Get business-level summary
print(summary["business_summary"])
# "Validates orders, charges customers, and initiates shipment"

# Understand the workflow
print(summary["main_workflow"])
# ["Validate items exist", "Check inventory", "Calculate total", 
#  "Process payment", "Reserve inventory", "Trigger fulfillment"]

# Identify business rules
print(summary["business_rules"])
# ["Orders must have at least 1 item", "Total must be > $0",
#  "Inventory must be available", "Payment must succeed"]

# Understand data transformations
print(summary["data_transformations"])
# ["Calculates tax based on location", "Applies discount codes",
#  "Charges total to payment method"]

# See external integrations
print(summary["external_integrations"])
# ["Integrates with payment processor", "Queries inventory database",
#  "Publishes to fulfillment system"]

# Understand business value
print(summary["business_value"])
# "Converts orders to revenue while ensuring accuracy and compliance"
```

---

### 4. Pattern Validation with LLM Reasoning ✅
Validate extracted patterns using LLM intelligence.

```python
pattern = {
    "name": "retry_with_backoff",
    "description": "Retry failed operations with exponential backoff",
    "examples": ["payment_retry", "api_call_retry"]
}

validation = engine.validate_pattern(
    pattern,
    codebase_context="Production e-commerce platform"
)

print(f"Is valid: {validation.is_valid}")
# True

print(f"Confidence: {validation.confidence}")
# 0.92

print(f"Feedback: {validation.validation_reasoning}")
# "This pattern is well-established and properly implemented"

print(f"Consistency: {validation.consistency}")
# 0.88 (how consistently applied across codebase)

print(f"Improvements: {validation.design_improvements}")
# ["Use jitter in backoff to avoid thundering herd",
#  "Add circuit breaker for complete outages"]

print(f"Related patterns: {validation.similar_patterns}")
# ["circuit_breaker_pattern", "bulkhead_isolation"]
```

---

## Installation & Setup

### Step 1: Install Dependencies

```bash
# For Gemini support
pip install google-generativeai

# For Claude support  
pip install anthropic

# Or both
pip install google-generativeai anthropic
```

### Step 2: Set API Keys

```bash
# Gemini (Google)
export GOOGLE_API_KEY="your-gemini-api-key"

# Claude (Anthropic)
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"

# Or use a .env file
echo "GOOGLE_API_KEY=your-key" >> .env
echo "ANTHROPIC_API_KEY=your-key" >> .env
```

### Step 3: Verify Setup

```bash
python agents/llm_rule_inference.py  # Demo script with test
```

---

## Usage Examples

### Example 1: Understanding a Complex Function

```python
from agents.llm_rule_inference import LLMRuleInferenceEngine

# Initialize (auto-detects provider from env vars)
engine = LLMRuleInferenceEngine()

# Your function code
function_code = '''
def finalize_payment(payment_id: str) -> dict:
    payment = get_payment_record(payment_id)
    
    if payment.status != 'pending':
        raise ValueError("Can only finalize pending payments")
    
    # Attempt authorization
    for attempt in range(3):
        try:
            result = authorize_with_processor(payment.token)
            payment.status = 'authorized'
            payment.authenticated_at = now()
            save_payment(payment)
            
            # Notify downstream systems
            emit_event('payment.authorized', payment_id)
            return result
            
        except RetryableError as e:
            if attempt < 2:
                sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                payment.status = 'failed'
                emit_event('payment.failed', payment_id)
                raise PaymentFailedError(str(e))
        except FraudError as e:
            notify_fraud_prevention_team(payment_id)
            payment.fraud_detected = True
            raise
'''

# Analyze semantically
analysis = engine.analyze_function_semantics(
    function_code,
    "finalize_payment",
    context="Payment processing pipeline for e-commerce",
    ask_specifically="What could cause this payment to fail from customer perspective?"
)

# Results
print(f"What it really does: {analysis.true_purpose}")
# "Charges customer's payment method with fraud detection and automatic retry"

print(f"Why it matters: {analysis.business_value}")
# "Authorizes payments ensuring revenue collection while blocking fraud"

print(f"Risks: {', '.join(analysis.key_risks)}")
# "Processor timeout, Fraud blocking valid card, Race condition on retry"

print(f"Rules embedded: {', '.join(analysis.embedded_rules)}")
# "Payment status must be pending, Must authenticate with processor, ..."

print(f"Complexity: {analysis.complexity}")
# "complex"
```

---

### Example 2: Making Rules Understandable

```python
from smartrule_inference import SmartRuleInference
from llm_rule_inference import LLMRuleInferenceEngine

# Extract rules syntactically
rule_engine = SmartRuleInference()
extracted = rule_engine.infer_all_rules(code, "payment.py")

# Explain rules humanly
llm_engine = LLMRuleInferenceEngine()
explanations = llm_engine.explain_rules_humanly(
    extracted["validation_rules"] + extracted["constraint_rules"],
    domain_context="Financial transaction system"
)

# Stakeholder-friendly output
for rule in explanations:
    print(f"\n📋 {rule.rule_type.upper()}: {rule.simple_explanation}")
    print(f"👥 {rule.business_context}")
    print(f"⏰ {rule.when_it_applies}")
    print(f"✓ Valid: {', '.join(rule.positive_examples)}")
    print(f"✗ Invalid: {', '.join(rule.negative_examples)}")
    print(f"⚠️ Impact: {', '.join(rule.implications)}")
```

---

### Example 3: Analyzing Full Codebase

```python
from agents.deep_llm_integration_demo import DeepLLMAnalyzer

analyzer = DeepLLMAnalyzer()

# Analyze codebase
results = analyzer.analyze_codebase_deeply(
    root_path="/path/to/codebase",
    file_limit=10,  # Cost control
    function_limit=3
)

# Results contain:
# - Syntactic rules (validation, temporal, permission)
# - Semantic analyses (purpose, value, risks)
# - Business summaries (workflows, entities, rules)
# - Human-readable explanations (for stakeholders)

print(f"Files analyzed: {results['files_analyzed']}")
for file_analysis in results['file_analyses']:
    file_path = file_analysis["file"]
    analysis = file_analysis["analysis"]
    
    print(f"\n📄 {file_path}")
    
    # Show business summary
    if analysis["semantic_analysis"].get("business_summary"):
        summary = analysis["semantic_analysis"]["business_summary"]
        print(f"  Business purpose: {summary['business_summary']}")
    
    # Show extracted rules
    rules = analysis["syntactic_analysis"]
    total_rules = sum([
        len(rules.get("validation_rules", [])),
        len(rules.get("constraint_rules", [])),
        len(rules.get("temporal_dependencies", []))
    ])
    print(f"  Business rules found: {total_rules}")
```

---

## Architecture

```
┌─────────────────────────────┐
│  Your Python Code           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  LLMRuleInferenceEngine             │
│  ┌─────────────────────────────┐   │
│  │ Semantic Analysis Layer     │   │
│  │ • What is it really doing? │   │
│  │ • Business value/impact    │   │
│  │ • Risks & dependencies     │   │
│  └─────────┬───────────────────┘   │
│            │                       │
│  ┌─────────▼───────────────────┐   │
│  │ Rule Explanation Layer      │   │
│  │ • Human-readable rules      │   │
│  │ • Business context          │   │
│  │ • Examples & implications   │   │
│  └─────────┬───────────────────┘   │
│            │                       │
│  ┌─────────▼───────────────────┐   │
│  │ Pattern Validation Layer    │   │
│  │ • Pattern recognition       │   │
│  │ • Design improvements       │   │
│  │ • Consistency checking      │   │
│  └─────────┬───────────────────┘   │
└────────────┼──────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ LLM Provider │
      │ (Gemini/Clau)│
      └──────────────┘
```

---

## Cost Optimization

LLM API calls have costs. Use these strategies:

### 1. Limit Analysis Scope
```python
# Analyze only top N files
analyzer.analyze_codebase_deeply(
    root_path="/large/codebase",
    file_limit=5,  # Not all files
    function_limit=2  # Not all functions
)

# Analyze only key files
key_files = ["models.py", "services.py", "utils.py"]
for file in key_files:
    engine.analyze_function_semantics(code, name)
```

### 2. Use Caching
```python
# Engine caches results automatically
analysis1 = engine.analyze_function_semantics(code, "func1")
analysis2 = engine.analyze_function_semantics(code, "func1")  # Cached, no API call
```

### 3. Batch Analysis
```python
# Process multiple items together
explanations = engine.explain_rules_humanly(rules)  # All rules at once
# vs calling for each rule individually
```

### 4. Use Cheaper Models
```python
# Gemini Flash is faster/cheaper than Gemini Pro
engine = LLMRuleInferenceEngine(
    provider="gemini",
    model="gemini-1.5-flash"  # Faster, cheaper
)

# Claude 3.5 Haiku is cheaper than Sonnet
engine = LLMRuleInferenceEngine(
    provider="claude",
    model="claude-3-5-haiku-20241022"  # Cheaper
)
```

---

## Comparison: Syntactic vs Semantic Analysis

| Aspect | Syntactic (AST) | Semantic (LLM) |
|--------|-----------------|----------------|
| **What it finds** | Variables, comparisons, calls | Purpose, intent, impact |
| **Example** | `if x < 10:` | "Validates amount is less than limit" |
| **Cost** | Free | API cost |
| **Speed** | Instant | 1-3 seconds |
| **Accuracy** | Deterministic | Probabilistic |
| **Use case** | Finding patterns | Understanding meaning |
| **Human readable** | No (code-like) | Yes (business language) |

---

## Integration with Existing Systems

### With Cartographer Agent
```python
from agents.cartographer_agent import cartographer_agent
from agents.llm_rule_inference import LLMRuleInferenceEngine

# Get code structure from Cartographer
cypher_statements = cartographer_agent("/path/to/code")

# Enhance with deep LLM analysis
engine = LLMRuleInferenceEngine()
for file_code in extracted_files:
    analysis = engine.analyze_with_extracted_rules(file_code, "file.py")
    # Save to Neo4j with semantic insights
```

### With Neo4j
```python
# Store semantic analysis results in graph
def_node = {
    "name": "process_order",
    "true_purpose": analysis.true_purpose,
    "business_value": analysis.business_value,
    "complexity": analysis.complexity,
    "risks": analysis.key_risks
}

# Create relationships
"process_order -[HAS_RISK]-> timeout"
"process_order -[EMBEDDED_RULE]-> validation_rule"
```

### With Caching Intelligence
```python
# Cache semantic analyses
engine = LLMRuleInferenceEngine()
analysis = engine.analyze_function_semantics(code, "func")

# Cache key: hash(code) + function_name
# Results cached for 24 hours by default
```

---

## Troubleshooting

### "No LLM provider configured"
```bash
# Set environment variable
export GOOGLE_API_KEY="..."
# OR
export ANTHROPIC_API_KEY="..."

# Verify
python -c "from agents.llm_rule_inference import LLMRuleInferenceEngine; \
           engine = LLMRuleInferenceEngine(); print(engine.provider_name)"
```

### "JSON decode error"
The LLM response wasn't valid JSON. Try:
1. Use simpler code examples (shorter < 500 lines)
2. Try different provider
3. Increase max_tokens
4. Check API key is valid

### "Request timeout"
LLM API took too long:
1. Reduce code size
2. Use faster model (e.g., flash models)
3. Increase timeout parameter
4. Check network connection

### "Rate limit exceeded"
Hit API quota:
1. Wait and retry
2. Use file_limit and function_limit
3. Consider cheaper models
4. Batch requests

---

## Best Practices

### 1. Use Domain Context
```python
# Bad: No context
analysis = engine.analyze_function_semantics(code, "process")

# Good: Include domain context
analysis = engine.analyze_function_semantics(
    code, "process",
    context="E-commerce order fulfillment system"
)
```

### 2. Ask Specific Questions
```python
# Bad: Generic
analysis = engine.analyze_function_semantics(code, "charge")

# Good: Specific question
analysis = engine.analyze_function_semantics(
    code, "charge",
    ask_specifically="What happens if the payment processor is down?"
)
```

### 3. Validate with Multiple Providers
```python
# Compare results
for provider in ["gemini", "claude"]:
    engine = LLMRuleInferenceEngine(provider=provider)
    analysis = engine.analyze_function_semantics(code, func)
    # Compare interpretations
    print(f"{provider}: {analysis.true_purpose}")
```

### 4. Document Findings
```python
# Save analysis results
import json

results = engine.analyze_with_extracted_rules(code, file)
with open("analysis.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

# Review later without re-running
```

---

## Examples Gallery

See `agents/deep_llm_integration_demo.py` for working examples:

```bash
# Run all demos
python agents/deep_llm_integration_demo.py

# Analyze specific codebase
python agents/deep_llm_integration_demo.py /path/to/code
```

---

## Next Steps

1. **Run the demo**: `python agents/llm_rule_inference.py`
2. **Try on your code**: `python agents/deep_llm_integration_demo.py /your/code`
3. **Integrate with Neo4j**: Store semantic insights in graph
4. **Build workflows**: Combine with Cartographer for full analysis
5. **Share findings**: Use human-readable rules with stakeholders

---

## Summary

**Deep LLM Integration** adds semantic understanding to rule inference:

✅ **What functions REALLY do** (semantic intent)  
✅ **Why businesses need them** (business value)  
✅ **What could go wrong** (risk analysis)  
✅ **Explanations non-technical people understand** (stakeholder-friendly)  
✅ **Pattern validation & improvement suggestions** (quality assurance)  

Use Gemini or Claude to understand your codebase at the business level, not just the technical level.
