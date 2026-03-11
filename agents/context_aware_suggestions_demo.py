#!/usr/bin/env python3
"""
Context-Aware Suggestions Demo

Demonstrates the intelligent recommendations system:
- Duplicate validation logic detection
- Unhandled error case identification
- Function consolidation opportunities
- Business rule conflict discovery
"""

import sys
import os

# Add to path
sys.path.insert(0, '/Users/juani/github-projects/documentationmcp/documentationmcp')

from agents.integrated_context_aware_agent import IntegratedContextAwareAgent


def main():
    """Run context-aware suggestions demo."""
    
    print("\n" + "="*80)
    print("🎯 CONTEXT-AWARE SUGGESTIONS DEMO")
    print("="*80)
    print("""
This demo shows how the Context-Aware Suggestions Engine provides smart 
recommendations by analyzing your codebase:
    
1. 🔍 DUPLICATE VALIDATION LOGIC
   "This validation logic duplicates that rule found in payment.py"
   
   The system detects when similar validation checks appear in multiple
   files and suggests extracting shared utility functions.

2. 🚨 UNHANDLED ERROR CASES
   "This error case isn't handled in your main flow"
   
   The system identifies operations (I/O, network, database) that could
   fail but lack error handling.

3. 🔗 FUNCTION CONSOLIDATION
   "These 3 functions could be consolidated"
   
   The system finds functions with similar parameters, complexity, and
   behavior that could be merged into a single utility.

4. ⚖️  BUSINESS RULE CONFLICTS
   "This business rule contradicts this other one"
   
   The system identifies contradictions between business rules in
   different parts of the codebase (e.g., "require approval" vs "auto-approve").

""")
    print("="*80 + "\n")
    
    # Get codebase path
    if len(sys.argv) > 1:
        codebase_path = sys.argv[1]
    else:
        # Default to current directory
        codebase_path = '/Users/juani/github-projects/documentationmcp/documentationmcp'
    
    print(f"📁 Analyzing: {codebase_path}\n")
    
    # Run analysis
    agent = IntegratedContextAwareAgent(codebase_path)
    results = agent.analyze()
    
    # Print comprehensive report
    print("\n")
    agent.print_report()
    
    # Show specific examples
    print("\n" + "="*80)
    print("📌 DETAILED EXAMPLES")
    print("="*80 + "\n")
    
    suggestions = results['suggestions']['suggestions']
    summary = results['suggestions']['summary']
    
    # Example 1: Duplicate validation
    if summary['duplicate_validation_found'] > 0 and suggestions['duplicate_validation']:
        print("Example 1: DUPLICATE VALIDATION LOGIC")
        print("-" * 80)
        dup = suggestions['duplicate_validation'][0]
        print(f"""
Function A: {dup['function_a']} ({dup['file_a']}:{dup['line_a']})
Function B: {dup['function_b']} ({dup['file_b']}:{dup['line_b']})

Similarity: {dup['similarity']:.1%}

Recommendation: {dup['details']['recommendation']}

Action:
  1. Review both validation functions
  2. Extract common logic to a shared utility module
  3. Update both to use the shared utility
  4. Add comprehensive tests to the shared utility
""")
    
    # Example 2: Unhandled errors
    if summary['unhandled_errors_found'] > 0 and suggestions['unhandled_errors']:
        print("\nExample 2: UNHANDLED ERROR CASES")
        print("-" * 80)
        err = suggestions['unhandled_errors'][0]
        print(f"""
Function: {err['function']} ({err['file']}:{err['line']})
Severity: {err['severity'].upper()}

Issue: {err['message']}

Risky Operations:
  • I/O Operations: {err['details']['has_io']}
  • Network Operations: {err['details']['has_network']}
  • Database Operations: {err['details']['has_db']}

Recommendation: {err['details']['recommendation']}

Action:
  1. Add try-except block around risky operations
  2. Handle specific exceptions (don't catch all)
  3. Log or report errors appropriately
  4. Provide fallback behavior
""")
    
    # Example 3: Consolidation
    if len(suggestions['consolidation_opportunities']) > 0 and suggestions['consolidation_opportunities']:
        print("\nExample 3: FUNCTION CONSOLIDATION OPPORTUNITIES")
        print("-" * 80)
        cons = suggestions['consolidation_opportunities'][0]
        print(f"""
Similarity: {cons['similarity']:.1%}

Functions to consolidate:
""")
        for func in cons['functions'][:2]:
            print(f"  • {func['name']} ({func['file']}:{func['line']})")
        
        print(f"""
Recommendation: {cons['details']['recommendation']}

Action:
  1. Compare the function implementations
  2. Identify common and different parts
  3. Create a parametrized shared function
  4. Update callers to use shared function
  5. Add tests for new behavior variations
""")
    
    # Example 4: Rule conflicts
    if summary['rule_conflicts_found'] > 0 and suggestions['rule_conflicts']:
        print("\nExample 4: BUSINESS RULE CONFLICTS")
        print("-" * 80)
        conf = suggestions['rule_conflicts'][0]
        print(f"""
Rule A: {conf['rule_a']['type']} in {conf['rule_a']['function']} 
        ({conf['rule_a']['file']}:{conf['rule_a']['line']})

Rule B: {conf['rule_b']['type']} in {conf['rule_b']['function']}
        ({conf['rule_b']['file']}:{conf['rule_b']['line']})

Conflict Type: {conf['conflict_type'].upper()}
Severity: {conf['severity'].upper()}

Issue: {conf['explanation']}

Recommendation: {conf['details']['recommendation']}

Action:
  1. Review the conflicting rules with stakeholders
  2. Clarify the intended behavior
  3. Update the implementation to match intent
  4. Add tests to prevent regression
  5. Document the expected behavior
""")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80 + "\n")
    
    # Print quick stats
    print(f"""Summary Statistics:
  • Files analyzed: {results['suggestions']['metadata']['total_files_analyzed']}
  • Validations found: {results['suggestions']['metadata']['total_validations']}
  • Error handlers: {results['suggestions']['metadata']['total_handlers']}
  • Functions analyzed: {results['suggestions']['metadata']['total_functions']}
  • Business rules: {results['suggestions']['metadata']['total_rules']}
  
Total Suggestions: {results['suggestions']['summary']['total_suggestions']}
  • Duplicate validation: {results['suggestions']['summary']['duplicate_validation_found']}
  • Unhandled errors: {results['suggestions']['summary']['unhandled_errors_found']}
  • Consolidation opportunities: {results['suggestions']['summary']['consolidation_opportunities']}
  • Rule conflicts: {results['suggestions']['summary']['rule_conflicts_found']}
""")
    
    # Export to JSON if requested
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        agent.export_json(output_path)
    
    return results


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
