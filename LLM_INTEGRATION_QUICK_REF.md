# LLM Integration Quick Reference

**TL;DR**: You can now ask your code questions in plain English and get intelligent answers.

---

## 30-Second Setup

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 2. Install client (if needed)
pip install anthropic

# 3. Try it
python3 -c "
from agents.unified_analyzer import UnifiedCodeAnalyzer
code = open('agents/semantic_analyzer.py').read()
analyzer = UnifiedCodeAnalyzer()
print(analyzer.ask_question_about_code(code, 'What does this code do?'))
"
```

---

## One-Minute Examples

### Ask a Question About Code
```python
from agents.unified_analyzer import InteractiveLLMAnalysis

session = InteractiveLLMAnalysis(source_code, "payment_service.py")

# Ask anything
session.ask("What happens if payment fails?")
session.ask("Are there security issues?")
session.ask("How does this scale?")
```

### Understand a Function
```python
from agents.llm_code_analyzer import LLMCodeAnalyzer

analyzer = LLMCodeAnalyzer()
func = """
def calculate_shipping(order_weight, delivery_zone):
    base_cost = 5.99
    weight_factor = order_weight * 0.50
    zone_multiplier = 1.0 + (delivery_zone * 0.10)
    return (base_cost + weight_factor) * zone_multiplier
"""

interpretation = analyzer.interpret_function(func, "calculate_shipping")
print(interpretation.interpreted_purpose)
print(f"Risks: {interpretation.risks}")
```

### Explain Complex Logic
```python
complex_code = """
# Complex discount logic...
"""

summary = analyzer.summarize_complex_logic(complex_code)
print(summary['summary'])       # Simple explanation
print(summary['what_happens'])  # Step-by-step
print(summary['potential_issues'])  # What could break
```

### Validate Extracted Patterns
```python
validation = analyzer.validate_patterns(
    "Always check payment before shipping",
    ["check_payment() in line 42", "require_payment() in line 156"]
)
print(f"Real pattern? {validation.is_valid}")
print(f"Confidence: {validation.confidence}")
print(f"Reasoning: {validation.reasoning}")
```

### Analyze Business Impact
```python
impact = analyzer.analyze_business_impact(refund_code, "refunds")
print(f"Criticality: {impact['criticality']}")
print(f"Affected: {impact['affected_users']}")
print(f"If it fails: {impact['failure_impact']}")
```

### Get Full Analysis
```python
from agents.unified_analyzer import UnifiedCodeAnalyzer

analyzer = UnifiedCodeAnalyzer()
analysis = analyzer.analyze_code_deeply(source_code, "filename.py")
report = analyzer.generate_comprehensive_report(analysis)
print(report)  # Complete markdown report
```

---

## Common Patterns

### "What Does This Do?" 
```python
interpretation = analyzer.interpret_function(code, name)
print(interpretation.interpreted_purpose)
```

### "Is This Important?"
```python
impact = analyzer.analyze_business_impact(code)
print(f"{impact['criticality']} - {impact['affected_users']}")
```

### "What Could Break?"
```python
interpretation = analyzer.interpret_function(code, name)
for risk in interpretation.risks:
    print(f"  ⚠️  {risk}")
```

### "Explain This to a Non-Coder"
```python
summary = analyzer.summarize_complex_logic(code)
print(summary['summary'])
```

### "Is This Pattern Real?"
```python
validation = analyzer.validate_patterns(pattern_desc, evidence)
if validation.is_valid:
    print(f"✓ Real pattern ({validation.confidence}% sure)")
else:
    print(f"✗ Not a real pattern")
```

---

## Entry Points

### For Analyzing Single Function
```python
analyzer = LLMCodeAnalyzer()
interpretation = analyzer.interpret_function(code, "func_name")
```

### For Interactive Q&A
```python
session = InteractiveLLMAnalysis(code, "file.py")
answer = session.ask("Your question?")
```

### For Comprehensive Analysis
```python
analyzer = UnifiedCodeAnalyzer()
analysis = analyzer.analyze_code_deeply(code, "file.py")
report = analyzer.generate_comprehensive_report(analysis)
```

### For Business Documentation
```python
docs = analyzer.create_business_documentation(code, "file.py")
```

### For Pattern Validation
```python
validator = PatternValidator()
result = validator.validate_all_patterns(patterns_dict)
```

---

## What You Get

| Method | Returns | Use For |
|--------|---------|---------|
| `interpret_function()` | CodeInterpretation | Understand what function does |
| `summarize_complex_logic()` | Dict | Explain logic simply |
| `explain_business_rules()` | BusinessRuleExplanation | Document business rules |
| `validate_patterns()` | PatternValidation | Verify patterns are real |
| `analyze_business_impact()` | Dict | Understand criticality |
| `ask_followup()` | String | Follow-up questions |
| `analyze_code_deeply()` | Dict | Complete analysis |
| `ask()` (interactive) | String | Any question about code |

---

## Files

- **`agents/llm_code_analyzer.py`** - Core LLM functionality
- **`agents/unified_analyzer.py`** - Integration layer
- **`agents/llm_demo.py`** - Examples and demonstrations

Run demo:
```bash
python3 agents/llm_demo.py
```

---

## Cost Estimate

- Per function: ~$0.02
- Per complex analysis: ~$0.10
- 1000 function analyses: ~$20

*Costs approximate based on Claude pricing*

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "ANTHROPIC_API_KEY not found" | `export ANTHROPIC_API_KEY="sk-..."` |
| "Module anthropic not found" | `pip install anthropic` |
| Slow responses | Normal (1-3 sec), check Internet |
| Expensive analyses | Use caching, only analyze critical code |

---

## Classes & Methods

### LLMCodeAnalyzer
```python
analyzer.interpret_function(code, name, context = None)
analyzer.summarize_complex_logic(code, title = "")
analyzer.explain_business_rules(code, rule_name = "")
analyzer.validate_patterns(description, evidence, name = "")
analyzer.analyze_business_impact(code, metric = "")
analyzer.ask_followup(question, context = "default")
```

### UnifiedCodeAnalyzer  
```python
analyzer.analyze_code_deeply(code, filename)
analyzer.generate_comprehensive_report(analysis)
analyzer.create_business_documentation(code, filename)
analyzer.ask_question_about_code(code, question)
```

### InteractiveLLMAnalysis
```python
session.ask(question)
session.get_summary()
session.get_risks()
session.get_improvements()
session.find_dependencies()
session.analyze_flow(entity_name)
```

---

## Real Examples

### Example 1: Review PR
```python
analyzer = LLMCodeAnalyzer()
interpretation = analyzer.interpret_function(pr_code, "new_feature")
impact = analyzer.analyze_business_impact(pr_code)

# Discuss: Does this match intent? Is impact acceptable?
```

### Example 2: Understand Legacy Code
```python
session = InteractiveLLMAnalysis(legacy_code, "old_feature.py")
session.ask("What does this code do?")
session.ask("Why does it do it this way?")
session.ask("What are the risks?")
```

### Example 3: Validate Pattern
```python
# After automatic extraction
validation = analyzer.validate_patterns(
    "Always authenticate first",
    ["auth() at line 42", "auth() at line 156", ...]
)
if validation.is_valid:
    print("✓ This is a real pattern")
```

---

## Integration With Existing System

Works with:
- ✅ semantic_analyzer.py
- ✅ business_rules_extractor.py
- ✅ smart_entity_graph.py
- ✅ All existing analyzers

UnifiedCodeAnalyzer combines all of them.

---

## Next Steps

1. **Set up:** `export ANTHROPIC_API_KEY="..."`
2. **Try demo:** `python3 agents/llm_demo.py`
3. **Use it:** See examples above
4. **Integrate:** Use in your workflows

---

**Status:** ✅ Ready | **Files:** 3 new modules | **Documentation:** See [LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)
