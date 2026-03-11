# Context-Aware Suggestions Guide

## Overview

The Context-Aware Suggestions Engine provides intelligent recommendations for code improvement by analyzing your codebase and identifying:

1. **Duplicate Validation Logic** - "This validation logic duplicates that rule found in payment.py"
2. **Unhandled Error Cases** - "This error case isn't handled in your main flow"
3. **Consolidation Opportunities** - "These 3 functions could be consolidated"
4. **Business Rule Conflicts** - "This business rule contradicts this other one"

## Quick Start

### Basic Usage

```bash
# Run context-aware suggestions on your codebase
cd /path/to/documentationmcp
python agents/context_aware_suggestions_demo.py /path/to/your/codebase

# Export results to JSON
python agents/context_aware_suggestions_demo.py /path/to/your/codebase output.json
```

### Programmatic Usage

```python
from agents.integrated_context_aware_agent import IntegratedContextAwareAgent

# Create agent
agent = IntegratedContextAwareAgent('/path/to/your/codebase')

# Run analysis
results = agent.analyze()

# Print comprehensive report
agent.print_report()

# Export as JSON
agent.export_json('results.json')
```

## Feature Details

### 1. Duplicate Validation Logic Detection

**What it detects:**
- Validation functions with similar logic across files
- Similar error checking patterns
- Overlapping constraint validation

**Example output:**
```
This validation logic duplicates that rule found in payment.py
  File A: validators.py::validate_amount (line 45)
  File B: payment.py::check_payment_amount (line 78)
  Similarity: 85%
```

**Why it matters:**
- Reduces code duplication
- Ensures consistent validation across the codebase
- Makes maintenance easier

**How to use:**
1. Review both validation functions
2. Identify the common logic
3. Extract to a shared utility module
4. Update both functions to use the shared utility
5. Add comprehensive tests

**Example refactoring:**

```python
# Before: Duplicated validation

# validators.py
def validate_amount(amount):
    if not isinstance(amount, (int, float)):
        raise ValueError("Amount must be numeric")
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if amount > 1000000:
        raise ValueError("Amount exceeds limit")
    return True

# payment.py
def check_payment_amount(amt):
    if not isinstance(amt, (int, float)):
        raise ValueError("Payment amount must be numeric")
    if amt <= 0:
        raise ValueError("Payment must be positive")
    if amt > 1000000:
        raise ValueError("Exceeds maximum payment")
    return True

# After: Consolidated validation

# utils/validation.py
def validate_amount(amount, allow_zero=False):
    """Validate amount field with consistent rules."""
    if not isinstance(amount, (int, float)):
        raise ValueError("Amount must be numeric")
    if amount < (0 if allow_zero else 1):
        raise ValueError("Amount must be positive" if not allow_zero else "Amount cannot be negative")
    if amount > 1000000:
        raise ValueError("Amount exceeds maximum limit")
    return True

# validators.py & payment.py
from utils.validation import validate_amount

def validate_payment_amount(amount):
    return validate_amount(amount, allow_zero=False)
```

### 2. Unhandled Error Cases

**What it detects:**
- Functions performing risky operations (I/O, network, database) without error handling
- Network calls without retry logic
- File operations without exception handling
- Database queries without transaction handling

**Example output:**
```
This error case isn't handled in your main flow
  Function: fetch_user_data (users.py:120)
  Severity: HIGH
  Risky operations:
    • Network operations: true
    • I/O operations: true
```

**Why it matters:**
- Prevents application crashes
- Improves reliability and user experience
- Makes debugging easier

**How to use:**
1. Identify the risky operations in the function
2. Determine what error conditions can occur
3. Add appropriate error handling
4. Log errors for troubleshooting
5. Provide fallback behavior

**Example refactoring:**

```python
# Before: No error handling

def fetch_user_data(user_id):
    """Fetch user data from API."""
    response = requests.get(f"https://api.example.com/users/{user_id}")
    data = response.json()
    return data

# After: Comprehensive error handling

import logging
import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)

def fetch_user_data(user_id, retries=3):
    """Fetch user data from API with error handling."""
    for attempt in range(retries):
        try:
            response = requests.get(
                f"https://api.example.com/users/{user_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except Timeout:
            if attempt < retries - 1:
                logger.warning(f"Timeout fetching user {user_id}, retrying...")
                continue
            logger.error(f"Failed to fetch user {user_id} after {retries} attempts")
            raise
        
        except RequestException as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise
        
        except ValueError as e:
            logger.error(f"Invalid JSON response for user {user_id}: {e}")
            raise
    
    # Fallback
    return None
```

### 3. Function Consolidation Opportunities

**What it detects:**
- Functions with similar:
  - Parameter counts and types
  - Complexity levels
  - Internal function calls
  - Control flow structure

**Example output:**
```
These 3 functions could be consolidated
  Similarity: 72%
  Functions:
    • process_order (orders.py:142)
    • handle_order (main.py:89)
    • order_handler (api.py:250)
```

**Why it matters:**
- Reduces code duplication
- Improves maintainability
- Simplifies testing
- Reduces bug surface area

**How to use:**
1. Compare the similar functions
2. Identify common and different aspects
3. Create a parametrized function
4. Update all callers
5. Add tests for variations

**Example refactoring:**

```python
# Before: Duplicated functions

def process_order(order):
    validate_order(order)
    calculate_total(order)
    save_order(order)
    send_confirmation(order)
    return order

def handle_order(order_data):
    if validate_order_data(order_data):
        total = calculate_order_total(order_data)
        persist_order(order_data, total)
        notify_customer(order_data)
        return True
    return False

def order_handler(order_dict):
    if not order_dict:
        return None
    check_order_validity(order_dict)
    amount = compute_total(order_dict)
    db_save(order_dict)
    push_notification(order_dict)
    return order_dict

# After: Consolidated function

def process_order(
    order_data,
    validate_fn=None,
    calculate_fn=None,
    save_fn=None,
    notify_fn=None,
    raise_on_invalid=False
):
    """
    Process an order with customizable validation and notification.
    
    Args:
        order_data: Order to process
        validate_fn: Custom validation function (default: validate_order)
        calculate_fn: Custom calculation function (default: calculate_total)
        save_fn: Custom save function (default: save_order)
        notify_fn: Custom notification function (default: send_confirmation)
        raise_on_invalid: Whether to raise on validation failure
    
    Returns:
        Processed order or None if invalid (unless raise_on_invalid=True)
    """
    if not order_data:
        if raise_on_invalid:
            raise ValueError("Order data is required")
        return None
    
    # Validation
    validate_func = validate_fn or validate_order
    if not validate_func(order_data):
        if raise_on_invalid:
            raise ValueError("Order validation failed")
        return None
    
    # Calculation
    calc_func = calculate_fn or calculate_total
    order_data['total'] = calc_func(order_data)
    
    # Storage
    save_func = save_fn or save_order
    save_func(order_data)
    
    # Notification
    notify_func = notify_fn or send_confirmation
    notify_func(order_data)
    
    return order_data
```

### 4. Business Rule Conflicts

**What it detects:**
- Contradictory rules (e.g., "requires approval" vs "auto-approve")
- Overlapping conditions with different outcomes
- Inconsistent business logic across modules
- Rule precedence issues

**Example output:**
```
This business rule contradicts this other one
  Rule A: payment rule in validate_payment (payment.py:45)
  Rule B: eligibility rule in check_eligibility (eligibility.py:120)
  Conflict: Requires approval but other rule auto-approves
  Severity: CRITICAL
```

**Why it matters:**
- Prevents business logic errors
- Ensures consistent user experience
- Reduces customer confusion
- Prevents compliance issues

**How to use:**
1. Understand both conflicting rules
2. Clarify the intended behavior with stakeholders
3. Update implementation to match intent
4. Document the business rule
5. Add tests to prevent regression

**Example refactoring:**

```python
# Before: Conflicting rules

# payment.py
def process_payment(amount, customer_type):
    if customer_type == 'premium':
        # Premium customers need approval
        if not get_approval():
            raise Exception("Payment requires approval")
    return charge_customer(amount)

# eligibility.py
def check_eligibility(customer_type):
    if customer_type == 'premium':
        # Premium customers auto-approved
        return True
    return validate_standard_customer()

# After: Consistent rules with documented precedence

"""
Business Rules Documentation:

RULE: Payment Processing for Premium Customers
- Premium customers MUST undergo approval process
- No auto-approval for premium payments
- Approval must be done by authorized personnel
- Escalate if amount exceeds threshold

RULE: Account Eligibility
- Premium customers are eligible for services
- Eligibility != Payment Approval
- These are separate concerns
"""

# payment.py
def process_payment(amount, customer_id):
    """
    Process payment with appropriate approval based on customer type.
    
    Raises:
        PaymentApprovalRequired: If payment requires approval
        PaymentFailed: If payment cannot be processed
    """
    customer = get_customer(customer_id)
    
    if customer.type == 'premium':
        # Premium customers require explicit approval
        approval = get_payment_approval(customer_id, amount)
        if not approval:
            raise PaymentApprovalRequired(
                f"Premium customer {customer_id} requires approval for ${amount}"
            )
    
    return charge_customer(customer_id, amount)

# eligibility.py
def check_eligibility(customer_id):
    """
    Check if customer is eligible for services (not the same as payment approval).
    
    Note: Eligibility is separate from payment approval.
    Eligible customers still need approval for individual transactions.
    """
    customer = get_customer(customer_id)
    
    if customer.type == 'premium':
        return True  # Premium customers are eligible
    
    return customer.status == 'active' and not customer.is_suspended()

# billing.py - New unified billing module
class PaymentProcessor:
    """Handles payment processing with consistent business rules."""
    
    def process_with_approval(self, customer_id, amount):
        """Process payment, requiring approval for premium customers."""
        # Check eligibility
        if not check_eligibility(customer_id):
            raise IneligibleCustomer(f"Customer {customer_id} is not eligible")
        
        # Process with approval rules
        return process_payment(amount, customer_id)
```

## Configuration

### Customizing Analysis

```python
from agents.context_aware_suggestions import ContextAwareSuggestionsEngine

# Create engine with custom settings
engine = ContextAwareSuggestionsEngine(
    codebase_path='/path/to/code',
)

# Customize detection thresholds
engine.validation_similarity_threshold = 0.75  # 75% similarity required
engine.error_severity_threshold = 'high'  # Only report high-severity errors
engine.consolidation_similarity_threshold = 0.70  # 70% similarity for consolidation

# Run analysis
results = engine.analyze_codebase()
```

## Understanding Results

### Result Structure

```json
{
  "metadata": {
    "codebase": "/path/to/code",
    "total_files_analyzed": 45,
    "total_validations": 23,
    "total_handlers": 18,
    "total_functions": 156,
    "total_rules": 34
  },
  "suggestions": {
    "duplicate_validation": [...],
    "unhandled_errors": [...],
    "consolidation_opportunities": [...],
    "rule_conflicts": [...]
  },
  "summary": {
    "duplicate_validation_found": 5,
    "unhandled_errors_found": 8,
    "consolidation_opportunities": 3,
    "rule_conflicts_found": 2,
    "total_suggestions": 18
  }
}
```

### Interpreting Severity Levels

- **CRITICAL** (🔴): Requires immediate attention, may cause production issues
- **HIGH** (🔴): Important issues that should be addressed soon
- **MEDIUM** (🟡): Improvements that enhance code quality
- **LOW** (🟢): Minor changes for optimization
- **INFO** (ℹ️): Informational, for awareness

## Best Practices

### 1. Prioritize by Impact

1. **Critical issues first** - Business rule conflicts, unhandled network errors
2. **High-priority fixes** - Unhandled I/O, validation duplicates
3. **Improvements** - Consolidation opportunities
4. **Optimizations** - Code cleanup and refactoring

### 2. Review with Team

- Present findings to relevant team members
- Discuss implications with business stakeholders for rule conflicts
- Get consensus before refactoring

### 3. Add Tests

- Add tests before refactoring
- Ensure tests pass after consolidation
- Add tests for error handling paths

### 4. Document Changes

- Document why consolidation was done
- Explain business rule decisions
- Keep audit trail of changes

### 5. Gradual Rollout

- Fix critical issues immediately
- Schedule other improvements
- Monitor impact after changes

## Examples

### Analyzing Your Own Codebase

```bash
# Analyze project with verbose output
python agents/context_aware_suggestions_demo.py /path/to/project

# Save results for review
python agents/context_aware_suggestions_demo.py /path/to/project results.json

# Analyze specific subdirectory
python agents/context_aware_suggestions_demo.py /path/to/project/backend
```

### Checking Specific Suggestion Types

```python
from agents.context_aware_suggestions import ContextAwareSuggestionsEngine
import json

engine = ContextAwareSuggestionsEngine('/path/to/code')
results = engine.analyze_codebase()

# Look at duplicate validations
duplicates = results['suggestions']['duplicate_validation']
for dup in duplicates:
    print(f"Duplicate found: {dup['function_a']} and {dup['function_b']}")
    print(f"Similarity: {dup['similarity']:.1%}")

# Look at error handling gaps
errors = results['suggestions']['unhandled_errors']
critical_errors = [e for e in errors if e['details']['has_network']]
print(f"Network operations without error handling: {len(critical_errors)}")

# Look at consolidation opportunities
consolidations = results['suggestions']['consolidation_opportunities']
high_similarity = [c for c in consolidations if c['similarity'] > 0.8]
print(f"High-similarity functions: {len(high_similarity)}")
```

## Troubleshooting

### No suggestions found

- Codebase might be too small or not have the patterns being analyzed
- Check that Python files are in standard format
- Ensure __pycache__ and .venv are not interfering

### Too many suggestions

- Consider filtering by severity
- Adjust similarity thresholds
- Focus on critical issues first

### Performance issues on large codebases

- Analyze specific directories instead of entire codebase
- Increase file extension filter to specific paths
- Run analysis during off-peak hours

## Related Tools

- **Semantic Analyzer** - Deep semantic analysis of code structure
- **Business Rules Extractor** - Extract business logic from code
- **ML Pattern Recognition** - Use machine learning for pattern detection
- **Cartographer Agent** - Create detailed code dependency graphs

see the following files for more details:
- [Semantic Analysis Guide](../SEMANTIC_ANALYSIS_GUIDE.md)
- [Business Rule Extraction](../SMART_RULE_INFERENCE.md)
- [ML Pattern Recognition](../ML_PATTERN_RECOGNITION.md)

## API Reference

### ContextAwareSuggestionsEngine

```python
class ContextAwareSuggestionsEngine:
    def __init__(self, codebase_path: str)
    def analyze_codebase(self, file_list: Optional[List[str]] = None) -> Dict[str, Any]
    def print_summary(self)
```

### IntegratedContextAwareAgent

```python
class IntegratedContextAwareAgent:
    def __init__(self, codebase_path: str)
    def analyze(self) -> Dict[str, Any]
    def print_report(self)
    def export_json(self, output_path: str)
```

## Contributing

To extend the context-aware suggestions system:

1. **Add new detection types** in `ContextAwareSuggestionsEngine`
2. **Extend analysis** in `IntegratedContextAwareAgent`
3. **Create new recommendation generators** in cross-reference methods
4. **Add tests** to verify new detections

---

**Last Updated:** March 2026  
**Version:** 1.0  
**Maintainer:** Documentation MCP Team
