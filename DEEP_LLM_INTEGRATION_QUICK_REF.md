# Deep LLM Integration - Quick Reference

## Setup (30 seconds)

```bash
# 1. Install
pip install google-generativeai anthropic

# 2. Set API key
export GOOGLE_API_KEY="your-key"  # For Gemini
# OR
export ANTHROPIC_API_KEY="your-key"  # For Claude

# 3. Test
python agents/llm_rule_inference.py
```

## Core API

### Semantic Function Analysis
```python
from agents.llm_rule_inference import LLMRuleInferenceEngine

engine = LLMRuleInferenceEngine()

# Analyze what a function REALLY does
analysis = engine.analyze_function_semantics(code, "my_function")

analysis.true_purpose  # What it really does
analysis.business_value  # Why business needs it
analysis.key_risks  # What can go wrong
analysis.embedded_rules  # Business rules in code
analysis.complexity  # simple, moderate, complex
analysis.data_flow  # How data moves
analysis.confidence  # 0.0-1.0
```

### Human-Readable Rules
```python
# Convert technical rules to plain English
explanations = engine.explain_rules_humanly(rules)

for rule in explanations:
    rule.simple_explanation  # Plain English
    rule.business_context  # Why the rule exists
    rule.positive_examples  # Valid cases
    rule.negative_examples  # Invalid cases
    rule.implications  # What happens if violated
    rule.business_criticality  # critical/important/nice_to_have
```

### Business Logic Summary
```python
# High-level summary of complex code
summary = engine.summarize_business_logic(code)

summary["business_summary"]  # 1-2 sentence summary
summary["main_workflow"]  # Steps involved
summary["key_entities"]  # Main objects
summary["business_rules"]  # Rules being enforced
summary["data_transformations"]  # Conversions
summary["external_integrations"]  # External systems
summary["business_value"]  # Why it matters
summary["risks"]  # Potential issues
```

### Pattern Validation
```python
# Validate patterns found in code
validation = engine.validate_pattern(pattern)

validation.is_valid  # Is this a real pattern?
validation.confidence  # 0.0-1.0
validation.consistency  # How consistently applied
validation.relevance  # Relevance to domain
validation.suggested_name  # Better name
validation.design_improvements  # How to improve
validation.similar_patterns  # Related patterns
```

### Full Analysis (All-in-One)
```python
# Combine syntactic + semantic analysis
result = engine.analyze_with_extracted_rules(code, "file.py")

result["syntactic_analysis"]  # Validation, temporal, permission rules
result["semantic_analysis"]  # Function analyses, business summary
result["human_readable_rules"]  # Plain English explanations
```

## Common Patterns

### Question 1: "What does this do?"
```python
analysis = engine.analyze_function_semantics(code, "func_name")
print(analysis.true_purpose)
print(analysis.business_value)
```

### Question 2: "What could go wrong?"
```python
analysis = engine.analyze_function_semantics(code, "func_name")
for risk in analysis.key_risks:
    print(f"⚠️ {risk}")
```

### Question 3: "What rules are hidden in this code?"
```python
analysis = engine.analyze_function_semantics(code, "func_name")
for rule in analysis.embedded_rules:
    print(f"📋 {rule}")
```

### Question 4: "How do I explain this rule to non-technical people?"
```python
explanations = engine.explain_rules_humanly(extracted_rules)
for rule in explanations:
    print(f"Rule: {rule.simple_explanation}")
    print(f"Why: {rule.business_context}")
```

### Question 5: "Summarize this complex module"
```python
summary = engine.summarize_business_logic(code)
print(summary["business_summary"])
for workflow_step in summary["main_workflow"]:
    print(f"  • {workflow_step}")
```

### Question 6: "Is this a valid pattern?"
```python
validation = engine.validate_pattern(pattern)
print(f"Valid: {validation.is_valid}")
print(f"Confidence: {validation.confidence:.0%}")
print(f"Suggested improvements: {validation.design_improvements}")
```

## Cost Control

### Analyze only key files (30% cost)
```python
analyzer = DeepLLMAnalyzer()
results = analyzer.analyze_codebase_deeply(
    "/path/to/code",
    file_limit=3,      # Not 100 files
    function_limit=2   # Not 50 functions
)
```

### Use cheaper models
```python
# Gemini Flash is 2x faster, 50% cheaper
engine = LLMRuleInferenceEngine(model="gemini-1.5-flash")

# Claude Haiku is cheapest
engine = LLMRuleInferenceEngine(
    provider="claude",
    model="claude-3-5-haiku-20241022"
)
```

### Cache results (100% savings on repeat)
```python
# Cache is automatic
analysis1 = engine.analyze_function_semantics(code, "func")
analysis2 = engine.analyze_function_semantics(code, "func")  # From cache
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No LLM provider" | Set `GOOGLE_API_KEY` or `ANTHROPIC_API_KEY` |
| JSON decode error | Reduce code size or try different provider |
| Rate limit | Use `file_limit` or wait before retrying |
| Timeout | Use faster model (flash, haiku) |
| Wrong interpretation | Add `context` or `ask_specifically` |

## Examples

### Example 1: Payment Processing
```python
code = '''
def charge_customer(customer_id, amount):
    if amount <= 0:
        raise ValueError("Invalid amount")
    customer = get_customer(customer_id)
    response = payment_processor.charge(customer.card, amount)
    if response.status == "success":
        log_transaction(customer_id, amount, "success")
    else:
        log_transaction(customer_id, amount, "failed")
    return response.success
'''

analysis = engine.analyze_function_semantics(
    code, "charge_customer",
    ask_specifically="What validation happens here?"
)

print(analysis.true_purpose)
# Output: "Charges customer's payment method and logs the result"

print(analysis.key_risks)
# Output: ["Payment processor timeout", "Network failure", 
#          "Concurrent charge attempts"]

print(analysis.embedded_rules)
# Output: ["Amount must be > 0", "Must have valid customer record"]
```

### Example 2: Order Workflow
```python
code = '''
def process_order(order_id):
    order = get_order(order_id)
    user = authenticate_user(order.user_id)
    validate_items(order)
    total = calculate_price(order)
    charge_payment(user, total)
    reserve_inventory(order)
    send_confirmation(user)
'''

summary = engine.summarize_business_logic(code)
print(summary["business_summary"])
# "Validates order, charges customer, and initiates fulfillment"

print(summary["main_workflow"])
# ["Authenticate user", "Validate items", "Calculate price",
#  "Charge payment", "Reserve inventory", "Send confirmation"]
```

## Providers

| Provider | Model | Cost | Speed | Quality |
|----------|-------|------|-------|---------|
| Gemini Flash | gemini-1.5-flash | $ | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| Gemini Pro | gemini-2.0-flash | $$ | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| Claude Haiku | claude-3-5-haiku | $ | ⚡⚡ | ⭐⭐⭐⭐ |
| Claude Sonnet | claude-3-5-sonnet | $$$ | ⚡ | ⭐⭐⭐⭐⭐ |

**Recommendation:** Start with Haiku/Flash, upgrade to Pro/Sonnet if needed.

## See Also

- [Deep LLM Integration Guide](DEEP_LLM_INTEGRATION_GUIDE.md) - Complete guide
- [agents/llm_rule_inference.py](agents/llm_rule_inference.py) - Implementation
- [agents/deep_llm_integration_demo.py](agents/deep_llm_integration_demo.py) - Runnable demos
- [SMART_RULE_INFERENCE.md](SMART_RULE_INFERENCE.md) - Syntactic analysis only
- [GEMINI_INTEGRATION.md](GEMINI_INTEGRATION.md) - Multi-provider setup

## Get Started

```bash
# 1. Install
pip install google-generativeai anthropic

# 2. Set API key
export GOOGLE_API_KEY="your-key"

# 3. Run demo
python agents/llm_rule_inference.py

# 4. Analyze your code
python agents/deep_llm_integration_demo.py /path/to/code
```

Done! 🚀
