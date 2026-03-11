# Context-Aware Suggestions - Quick Reference

## Installation

No additional installation needed - uses existing Python AST library.

```bash
cd /path/to/documentationmcp
python agents/context_aware_suggestions_demo.py /path/to/analyze
```

## 4 Key Suggestions Types

### 1️⃣ Duplicate Validation Logic
```
"This validation logic duplicates that rule found in payment.py"

Detection: Analyzes validation functions (*.py files with validate/check/verify)
Threshold: >70% code similarity
Action: Extract to shared utils/validation.py utility
Impact: Reduce duplication, ensure consistency
Timeline: 1-2 days
```

### 2️⃣ Unhandled Error Cases
```
"This error case isn't handled in your main flow"

Detection: Identifies functions with risky ops (I/O, network, DB) but no try-except
Threshold: High-risk operations without error handlers
Action: Add try-except blocks with specific exception handling
Impact: Improve reliability, prevent crashes
Timeline: 2-3 days
```

### 3️⃣ Function Consolidation
```
"These 3 functions could be consolidated"

Detection: Functions with similar parameters, complexity, and behavior
Threshold: >65% similarity
Action: Merge into single parametrized utility function
Impact: Reduce duplication, improve testability
Timeline: 1-3 days
```

### 4️⃣ Business Rule Conflicts  
```
"This business rule contradicts this other one"

Detection: Contradictory or overlapping business rules across files
Types: contradictory (opposite logic), overlapping (same keywords)
Action: Align rules with stakeholder input, document decision
Impact: Prevent business logic errors, ensure consistency
Timeline: 3-5 days
```

## Usage Patterns

### Basic Analysis
```python
from agents.integrated_context_aware_agent import IntegratedContextAwareAgent

agent = IntegratedContextAwareAgent('/path/to/code')
results = agent.analyze()
agent.print_report()
```

### Export Results
```python
agent.export_json('suggestions.json')
```

### Programmatic Access
```python
duplicates = results['suggestions']['suggestions']['duplicate_validation']
errors = results['suggestions']['suggestions']['unhandled_errors']
consolidations = results['suggestions']['suggestions']['consolidation_opportunities']
conflicts = results['suggestions']['suggestions']['rule_conflicts']
```

## Example Suggestions

### Duplicate Validation Example
```
Function A: validators.py::validate_amount (line 45) 
Function B: payment.py::check_amount (line 78)
Similarity: 85%

Actions:
├─ Create: utils/validation.py (shared validation logic)
├─ Update: validators.py (import shared logic)
├─ Update: payment.py (import shared logic)  
└─ Add: Tests for shared validation
```

### Unhandled Error Example
```
Function: fetch_user_data (users.py:120)
Operations: network_call() without error handling
Severity: HIGH

Actions:
├─ Add: try-except around requests.get()
├─ Handle: RequestException, Timeout, JSONDecodeError
├─ Add: Retry logic with exponential backoff
├─ Add: Logging for debugging
└─ Add: Tests for error cases
```

### Consolidation Example
```
Functions: process_order, handle_order, order_handler
Similarity: 72% (parameters, complexity, calls)

Actions:
├─ Compare: All three implementations
├─ Create: Single process_order() with parameters
├─ Update: All callers to use new function
├─ Add: Tests for all variations
└─ Remove: Duplicate functions
```

### Rule Conflict Example
```
Rule A: payment.py - "requires approval for premium customers"
Rule B: eligibility.py - "premium customers auto-approved"
Conflict: Contradictory (requires vs auto)
Severity: CRITICAL

Actions:
├─ Clarify: With product/business team
├─ Document: Business rule decision
├─ Implement: Consistent logic
├─ Test: Both premium and non-premium flows
└─ Monitor: Payment processing after change
```

## Command Line

```bash
# Analyze codebase
python agents/context_aware_suggestions_demo.py /path/to/code

# Save to JSON
python agents/context_aware_suggestions_demo.py /path/to/code output.json

# Analyze specific directory
python agents/context_aware_suggestions_demo.py /path/to/code/backend
```

## Output Interpretation

```
✅ Files analyzed: 45
Suggestions found: 18
├─ Duplicate validation: 5 (extract 5 shared utilities)
├─ Unhandled errors: 8 (add error handling to 8 functions)
├─ Consolidation opportunities: 3 (merge 6 functions into 3)
└─ Business rule conflicts: 2 (align 2 rule pairs)

Impact Score:
├─ Code quality: +25% (less duplication)
├─ Reliability: +15% (better error handling)
├─ Maintainability: +20% (fewer functions to maintain)
└─ Consistency: +30% (aligned business rules)
```

## Common Scenarios

### 🔴 Payment Processing Code
```
Expected findings:
├─ Duplicate validation (amount, card, etc.)
├─ Unhandled: network calls, database operations
├─ Functions: validate_payment, process_payment, charge_card
└─ Conflicts: approval flows, rate limits
```

### 🔴 User Management
```
Expected findings:
├─ Duplicate validation (email format, password strength)
├─ Unhandled: API calls, database queries
├─ Functions: validate_user, create_user, update_user
└─ Conflicts: permission rules, access control
```

### 🔴 Data Processing
```
Expected findings:
├─ Duplicate validation (format, size, encoding)
├─ Unhandled: file I/O, parsing errors
├─ Functions: validate_data, process_data, transform_data
└─ Conflicts: data retention, cleanup policies
```

## Tips & Tricks

### Filter by Severity
```python
high_priority = [s for s in suggestions if s.get('severity') == 'high']
```

### Group by File
```python
from collections import defaultdict
by_file = defaultdict(list)
for sugg in suggestions:
    by_file[sugg.get('file')].append(sugg)
```

### Calculate Impact Score
```python
critical = len([s for s in suggestions if s['severity'] == 'critical'])
high = len([s for s in suggestions if s['severity'] == 'high'])
impact = (critical * 3) + (high * 1)
```

### Track Improvements
```python
# Before
initial_suggestions = results['summary']['total_suggestions']

# After fixing duplicates
updated_suggestions = len(remaining_issues)

improvement = ((initial_suggestions - updated_suggestions) / initial_suggestions) * 100
print(f"Improvement: {improvement:.1f}%")
```

## FAQ

**Q: How are duplicates detected?**
A: Code similarity analysis using SequenceMatcher (70%+ threshold)

**Q: Will it find all issues?**
A: No - uses pattern-based analysis, AST walking, and heuristics. Manual review needed.

**Q: How long to implement suggestions?**
A: Typically 1-2 weeks for comprehensive improvements

**Q: Can I customize thresholds?**
A: Yes - modify thresholds in engine initialization

**Q: What about false positives?**
A: Review all suggestions with team before implementing

**Q: Does it work on non-Python code?**
A: Currently Python-focused, but framework extensible

**Q: Can I export results?**
A: Yes - JSON export for reports and tracking

---

**Pro Tip:** Start with Critical/High priority items, then schedule medium/low improvements. Review all findings with team before implementing.
