"""
Deep LLM Integration Demo

Shows how to use the LLM Rule Inference Engine for:
1. Real codebase analysis (using the Cartographer agent)
2. Business rule summarization
3. Semantic function understanding
4. Pattern validation

This demo integrates with:
- Cartographer (code parsing and extraction)
- Smart Rule Inference (syntactic analysis)
- LLM Providers (Claude/Gemini)
- Neo4j (storing findings)

Usage:
    python deep_llm_integration_demo.py [path_to_codebase]
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our LLM-enhanced inference engine
try:
    from .llm_rule_inference import LLMRuleInferenceEngine, SemanticFunctionAnalysis
    from .cartographer_agent import cartographer_agent, extract_python_entities
except ImportError:
    from llm_rule_inference import LLMRuleInferenceEngine, SemanticFunctionAnalysis
    try:
        from cartographer_agent import cartographer_agent, extract_python_entities
    except ImportError:
        cartographer_agent = None
        extract_python_entities = None


class DeepLLMAnalyzer:
    """High-level interface for deep semantic analysis of codebases."""
    
    def __init__(self, provider: str = "auto"):
        """
        Initialize analyzer.
        
        Args:
            provider: "claude", "gemini", or "auto" (default)
        """
        self.engine = LLMRuleInferenceEngine(provider=None if provider == "auto" else provider)
        self.results = {
            "summaries": [],
            "semantic_analyses": [],
            "rule_explanations": [],
            "pattern_validations": []
        }
    
    def analyze_codebase_deeply(self, root_path: str, file_limit: int = 5,
                               function_limit: int = 3) -> Dict[str, Any]:
        """
        Perform deep analysis on Python files in a codebase.
        
        Args:
            root_path: Path to codebase directory
            file_limit: Max files to analyze (for cost control)
            function_limit: Max functions per file to analyze semantically
            
        Returns:
            Comprehensive analysis results
        """
        
        print(f"\n{'='*70}")
        print(f"DEEP LLM CODEBASE ANALYSIS")
        print(f"{'='*70}")
        print(f"📁 Target: {root_path}")
        print(f"📊 Configuration: {file_limit} files, {function_limit} functions each")
        print(f"🤖 Provider: {self.engine.provider_name.upper()}")
        print(f"{'='*70}\n")
        
        # Find Python files
        python_files = list(Path(root_path).rglob("*.py"))
        python_files = python_files[:file_limit]  # Limit for cost
        
        if not python_files:
            print("❌ No Python files found!")
            return {"error": "No Python files found", "files": []}
        
        print(f"📄 Found {len(python_files)} Python files")
        print(f"🔍 Analyzing {len(python_files)} files...\n")
        
        all_results = {
            "codebase_path": root_path,
            "files_analyzed": len(python_files),
            "file_analyses": []
        }
        
        for idx, file_path in enumerate(python_files, 1):
            print(f"\n[{idx}/{len(python_files)}] {file_path.name}")
            print("-" * 50)
            
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                if len(source_code) < 100:  # Skip very small files
                    print("  ⊘ File too small, skipping")
                    continue
                
                # Run full analysis
                print("  📊 Running comprehensive analysis...")
                analysis = self.engine.analyze_with_extracted_rules(
                    source_code,
                    str(file_path),
                    enrich_with_llm=True
                )
                
                # Print summary
                syntactic = analysis["syntactic_analysis"]
                rule_count = sum([
                    len(syntactic.get('validation_rules', [])),
                    len(syntactic.get('constraint_rules', [])),
                    len(syntactic.get('temporal_dependencies', []))
                ])
                print(f"  ✓ Rules extracted: {rule_count} total")
                
                semantic = analysis["semantic_analysis"]
                if semantic.get("function_analyses"):
                    func_count = len(semantic['function_analyses'])
                    print(f"  ✓ Functions analyzed: {func_count}")
                    for func_analysis in semantic["function_analyses"][:1]:  # Show first
                        func_name = func_analysis['function_name']
                        func_purpose = func_analysis['true_purpose'][:60]
                        print(f"     • {func_name}: {func_purpose}...")
                
                if semantic.get("business_summary"):
                    business_summary = semantic["business_summary"]
                    summary_text = business_summary.get("business_summary", "")
                    if summary_text:
                        summary_preview = summary_text[:70]
                        print(f"  ✓ Summary: {summary_preview}...")
                
                all_results["file_analyses"].append({
                    "file": str(file_path),
                    "analysis": analysis
                })
                
                # Rate limiting to avoid API quota issues
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)[:100]}")
        
        print(f"\n{'='*70}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*70}")
        print(f"📊 Files analyzed: {len(all_results['file_analyses'])}")
        
        return all_results
    
    def demo_semantic_analysis(self):
        """Demonstrate semantic function analysis."""
        
        print(f"\n{'='*60}")
        print(f"SEMANTIC FUNCTION ANALYSIS DEMO")
        print(f"{'='*60}\n")
        
        # Sample functions
        functions = [
            {
                "name": "validate_user_registration",
                "code": '''
def validate_user_registration(user_data: dict) -> bool:
    """Validate user registration data."""
    if not user_data.get("email") or "@" not in user_data["email"]:
        raise ValueError("Invalid email format")
    
    if len(user_data.get("password", "")) < 12:
        raise ValueError("Password must be at least 12 characters")
    
    if user_data.get("age", 0) < 18:
        raise ValueError("Must be 18 or older")
    
    if user_data.get("country") not in ["US", "CA", "MX"]:
        raise ValueError("Service not available in your region")
    
    return True
'''
            },
            {
                "name": "process_payment_retry",
                "code": '''
def process_payment_retry(payment_id: str, max_retries: int = 3):
    """Retry failed payment with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = call_payment_processor(payment_id)
            if response.status == "success":
                log_success(payment_id)
                return response
        except TemporaryError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                sleep(wait_time)
                continue
            else:
                notify_payment_failed(payment_id)
                raise PaymentFailedError(f"Failed after {max_retries} attempts")
        except PermanentError as e:
            notify_support_team(payment_id)
            raise
'''
            }
        ]
        
        for func in functions:
            print(f"📌 Function: {func['name']}")
            print("-" * 60)
            
            try:
                # Analyze semantically
                analysis = self.engine.analyze_function_semantics(
                    func["code"],
                    func["name"],
                    ask_specifically=f"What is {func['name']} really trying to accomplish?"
                )
                
                # Print results
                print(f"✓ Purpose: {analysis.true_purpose}")
                print(f"✓ Business Value: {analysis.business_value}")
                print(f"✓ Complexity: {analysis.complexity}")
                print(f"✓ Confidence: {analysis.confidence:.0%}")
                
                if analysis.key_risks:
                    print(f"✓ Risks: {', '.join(analysis.key_risks[:2])}")
                
                if analysis.embedded_rules:
                    print(f"✓ Embedded Rules:")
                    for rule in analysis.embedded_rules[:2]:
                        print(f"  • {rule}")
                
                print()
                
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
                print()
    
    def demo_rule_explanation(self):
        """Demonstrate human-readable rule explanation."""
        
        print(f"\n{'='*60}")
        print(f"HUMAN-READABLE RULE EXPLANATION DEMO")
        print(f"{'='*60}\n")
        
        # Sample extracted rules
        sample_rules = [
            {
                "field_name": "order.amount",
                "operation": ">=",
                "value": 1.0,
                "description": "Order amount must be at least $1.00"
            },
            {
                "field_name": "user.age",
                "operation": ">=",
                "value": 18,
                "description": "User must be at least 18 years old"
            },
            {
                "precondition": "authenticate_user",
                "postcondition": "process_payment",
                "dependency_type": "sequential",
                "description": "User must be authenticated before payment"
            }
        ]
        
        print("Converting extracted rules to human-readable format...\n")
        
        try:
            explanations = self.engine.explain_rules_humanly(
                sample_rules,
                domain_context="E-commerce order processing system"
            )
            
            for explanation in explanations:
                print(f"📋 Rule: {explanation.rule_id}")
                print(f"   Type: {explanation.rule_type}")
                print(f"   📝 {explanation.simple_explanation}")
                print(f"   🎯 Context: {explanation.business_context}")
                print(f"   📍 When: {explanation.when_it_applies}")
                
                if explanation.positive_examples:
                    print(f"   ✓ Valid: {explanation.positive_examples[0]}")
                if explanation.negative_examples:
                    print(f"   ✗ Invalid: {explanation.negative_examples[0]}")
                
                print(f"   ⚠️ Criticality: {explanation.business_criticality}")
                print()
                
        except Exception as e:
            print(f"❌ Explanation failed: {e}")
    
    def demo_business_logic_summary(self):
        """Demonstrate business logic summarization."""
        
        print(f"\n{'='*60}")
        print(f"BUSINESS LOGIC SUMMARIZATION DEMO")
        print(f"{'='*60}\n")
        
        # Sample complex business logic
        sample_code = '''
class OrderProcessor:
    """Main order processing engine."""
    
    def process_order(self, order_id: str, user: User) -> Order:
        # Step 1: Validate
        order = self.get_order(order_id)
        self.validate_order_items(order)
        self.check_inventory(order)
        
        # Step 2: Calculate pricing
        subtotal = sum(item.price * item.quantity for item in order.items)
        tax = subtotal * self.get_tax_rate(order.shipping_address)
        discount = self.apply_promotional_codes(order)
        total = subtotal + tax - discount
        
        # Step 3: Process payment
        if not self.charge_payment_method(user, total):
            order.set_status("payment_failed")
            self.notify_user_payment_failed(user, order)
            raise PaymentFailedError()
        
        # Step 4: Update state
        order.set_status("paid")
        self.reserve_inventory(order)
        order.set_status("ready_to_ship")
        
        # Step 5: Notify and integrate
        self.send_order_confirmation(user, order)
        self.notify_fulfillment_center(order)
        self.record_analytics(order)
        
        return order
'''
        
        print("Summarizing complex business logic...\n")
        
        try:
            summary = self.engine.summarize_business_logic(
                sample_code,
                file_context="Order management system",
                complexity_level="complex"
            )
            
            print(f"📊 Business Summary:")
            print(f"   {summary.get('business_summary', 'N/A')}\n")
            
            if summary.get("main_workflow"):
                print(f"🔄 Main Workflow:")
                for i, step in enumerate(summary["main_workflow"][:5], 1):
                    print(f"   {i}. {step}")
                print()
            
            if summary.get("business_rules"):
                print(f"📋 Business Rules:")
                for rule in summary["business_rules"][:3]:
                    print(f"   • {rule}")
                print()
            
            if summary.get("business_value"):
                print(f"💰 Business Value:")
                print(f"   {summary['business_value']}\n")
            
        except Exception as e:
            print(f"❌ Summarization failed: {e}")
    
    def demo_pattern_validation(self):
        """Demonstrate pattern validation."""
        
        print(f"\n{'='*60}")
        print(f"PATTERN VALIDATION DEMO")
        print(f"{'='*60}\n")
        
        # Sample patterns
        patterns = [
            {
                "name": "retry_with_exponential_backoff",
                "description": "Retry failed operations with exponential backoff delay",
                "examples": ["payment retry", "api call retry", "database query retry"]
            },
            {
                "name": "state_machine_validation",
                "description": "Validate state transitions are allowed",
                "examples": ["order states", "payment states", "user workflow states"]
            }
        ]
        
        for pattern in patterns:
            print(f"🔍 Validating pattern: {pattern['name']}")
            print("-" * 60)
            
            try:
                validation = self.engine.validate_pattern(
                    pattern,
                    codebase_context="Production e-commerce platform"
                )
                
                print(f"✓ Valid: {validation.is_valid} (confidence: {validation.confidence:.0%})")
                print(f"✓ Consistency: {validation.consistency:.0%}")
                print(f"✓ Relevance: {validation.relevance:.0%}")
                print(f"✓ Reasoning: {validation.validation_reasoning[:100]}...")
                
                if validation.suggested_name and validation.suggested_name != pattern['name']:
                    print(f"✓ Better name: {validation.suggested_name}")
                
                if validation.design_improvements:
                    print(f"✓ Improvements:")
                    for improvement in validation.design_improvements[:2]:
                        print(f"  • {improvement}")
                
                print()
                
            except Exception as e:
                print(f"❌ Validation failed: {e}\n")


def main():
    """Run deep LLM integration demos."""
    
    print(f"\n{'='*70}")
    print("DEEP LLM INTEGRATION FOR RULE INFERENCE & CODE ANALYSIS")
    print("="*70)
    
    # Initialize analyzer
    try:
        analyzer = DeepLLMAnalyzer()
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Setup Required:")
        print("   Gemini:  export GOOGLE_API_KEY='your-api-key'")
        print("   Claude:  export ANTHROPIC_API_KEY='your-api-key'")
        print("   pip install google-generativeai  # For Gemini")
        print("   pip install anthropic            # For Claude")
        return
    
    # Run demos
    try:
        analyzer.demo_semantic_analysis()
        analyzer.demo_rule_explanation()
        analyzer.demo_business_logic_summary()
        analyzer.demo_pattern_validation()
        
        # Optional: Analyze actual codebase if path provided
        if len(sys.argv) > 1:
            codebase_path = sys.argv[1]
            if os.path.isdir(codebase_path):
                print(f"\n📁 Analyzing codebase: {codebase_path}")
                results = analyzer.analyze_codebase_deeply(codebase_path, 
                                                          file_limit=3,
                                                          function_limit=2)
                # Save results
                output_file = "deep_llm_analysis_results.json"
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"✓ Results saved to: {output_file}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
