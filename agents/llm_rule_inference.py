"""
LLM-Enhanced Rule Inference Engine

Combines AST-based rule extraction with LLM semantic analysis to:
1. Generate summaries of complex business logic
2. Ask "What is this function REALLY doing?" (deep semantic intent)
3. Generate human-readable explanations of business rules
4. Validate and refine extracted patterns using LLM reasoning

Works with:
- Claude (Anthropic) 
- Gemini (Google)
- Any LLM provider via the unified interface

This is the "semantic layer" on top of syntactic rule inference.
"""

import json
import ast
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

try:
    from .llm_providers import LLMProvider, get_llm_provider, LLMProviderFactory
    from .smart_rule_inference import SmartRuleInference, ValidationRule, TemporalDependency
except ImportError:
    from llm_providers import LLMProvider, get_llm_provider, LLMProviderFactory
    from smart_rule_inference import SmartRuleInference, ValidationRule, TemporalDependency


@dataclass
class SemanticFunctionAnalysis:
    """Deep semantic understanding of what a function does."""
    function_name: str
    source_code: str
    
    # Semantic understanding
    true_purpose: str  # What it REALLY does (not just mechanics)
    business_value: str  # Why it matters to the business
    user_perspective: str  # What end-user experiences
    implementation_strategy: str  # How it achieves its purpose
    
    # Complexity and risks
    complexity: str  # simple, moderate, complex, architectural
    key_risks: List[str]  # What can go wrong
    data_flow: List[str]  # How data moves through the function
    external_dependencies: List[str]  # APIs, databases, services
    
    # Business rules embedded in code
    embedded_rules: List[str]  # Business rules found in this function
    decision_points: List[str]  # Key decision logic
    
    # Confidence and reasoning
    confidence: float  # 0.0-1.0
    reasoning: str  # Why this interpretation
    similar_patterns: List[str]  # Similar functions it relates to


@dataclass
class HumanReadableRule:
    """Business rule explained in human-readable language."""
    rule_id: str
    rule_type: str  # "validation", "temporal", "permission", "state_machine"
    
    # Simple explanation
    simple_explanation: str  # What the rule means in plain English
    business_context: str  # Why this rule exists
    when_it_applies: str  # When you need to follow this rule
    
    # Examples and implications
    positive_examples: List[str]  # Cases where rule is satisfied
    negative_examples: List[str]  # Cases where rule is violated
    implications: List[str]  # What happens if rule is violated
    
    # Related rules
    related_rules: List[str]  # Connected rules
    exceptions: List[str]  # When rule doesn't apply
    
    # Implementation notes
    implementation_location: str  # Where in code this is enforced
    how_verified: str  # How is this rule validated
    
    # LLM assessment
    clarity: float  # 0.0-1.0 how clear is the rule
    business_criticality: str  # "critical", "important", "nice_to_have"
    reasoning: str  # Why LLM made this assessment


@dataclass  
class ValidatedPattern:
    """Pattern validation results from LLM reasoning."""
    pattern_name: str
    pattern_description: str
    
    # Validation results
    is_valid: bool  # Is this a real, meaningful pattern?
    confidence: float  # 0.0-1.0
    validation_reasoning: str  # Why valid or invalid
    
    # Pattern properties
    consistency: float  # How consistent is this pattern in codebase
    relevance: float  # How relevant to business domain
    
    # Improvements
    suggested_name: str  # Better naming for this pattern
    refactoring_suggestions: List[str]  # How to improve implementation
    design_improvements: List[str]  # Architectural improvements
    
    # Related patterns
    similar_patterns: List[str]  # Related patterns
    conflicts: List[str]  # Patterns that conflict with this
    compatibility: Dict[str, float]  # How well this works with other patterns


class LLMRuleInferenceEngine:
    """
    Enhanced rule inference that combines syntax analysis with semantic understanding.
    
    Usage:
        engine = LLMRuleInferenceEngine(provider="gemini")  # or "claude"
        
        # Analyze a function deeply
        analysis = engine.analyze_function_semantics(code, func_name)
        print(analysis.true_purpose)
        print(analysis.business_value)
        
        # Get human-readable rules
        readable_rules = engine.explain_rules(extracted_rules)
        
        # Validate patterns
        validation = engine.validate_pattern(pattern_data)
    """
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None,
                 model: Optional[str] = None):
        """
        Initialize LLM Rule Inference Engine.
        
        Args:
            provider: "claude", "gemini", or None (auto-detect)
            api_key: API key for provider
            model: Model name (uses provider defaults if None)
        """
        # Get LLM provider
        try:
            self.llm_provider = get_llm_provider(provider=provider, api_key=api_key, model=model)
            self.provider_name = self.llm_provider.provider_name
        except ValueError as e:
            print(f"LLM Provider Error: {e}")
            raise
        
        # Initialize traditional rule inference
        self.rule_inference = SmartRuleInference()
        
        # Cache for expensive operations
        self.cache = {}
        self.conversation_history = defaultdict(list)
    
    def analyze_function_semantics(self, source_code: str, function_name: str,
                                   context: Optional[str] = None,
                                   ask_specifically: Optional[str] = None) -> SemanticFunctionAnalysis:
        """
        Deeply analyze what a function REALLY does (semantic intent, not mechanics).
        
        Asks specific questions like:
        - "What is this function really doing?"
        - "Why does the business need this?"
        - "What could go wrong?"
        - "How is data flowing through this?"
        
        Args:
            source_code: The function code to analyze
            function_name: Name of the function
            context: Optional context (module purpose, business domain, etc.)
            ask_specifically: Optional specific question to ask
            
        Returns:
            SemanticFunctionAnalysis with deep understanding
        """
        cache_key = f"semantic_{function_name}_{hash(source_code)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # System prompt for semantic analysis
        system_prompt = """You are an expert code analyst and business logic interpreter.
Your job is to understand code at the SEMANTIC level - what it REALLY does and why it matters.

When analyzing code:
1. Look beyond syntax to understand PURPOSE
2. Identify what business problem it solves
3. Find embedded business rules and constraints
4. Assess risk and complexity from a business perspective
5. Explain in terms a non-technical person could understand

Always respond with valid JSON."""
        
        # Build the analysis prompt
        prompt = f"""Perform deep semantic analysis of this function. Ask yourself:
"What is this function REALLY doing? Not the mechanics, but the PURPOSE."

FUNCTION: {function_name}

CODE:
```python
{source_code}
```

{f'CONTEXT: {context}' if context else ''}

{f'SPECIFIC QUESTION: {ask_specifically}' if ask_specifically else ''}

Respond with JSON including:

1. "true_purpose": One sentence what this REALLY does (business language, not code language)
2. "business_value": Why the business needs this (impact and value)
3. "user_perspective": What the user/customer experiences as a result
4. "implementation_strategy": How it achieves its purpose (high-level approach)
5. "complexity": "simple", "moderate", "complex", or "architectural"
6. "key_risks": Array of 3-5 things that could go wrong
7. "data_flow": Array of how data moves: ["input receives X", "transforms to Y", "outputs Z"]
8. "external_dependencies": Array of external systems it depends on
9. "embedded_rules": Array of business rules you can identify in the code
10. "decision_points": Array of key conditional logic or branching
11. "confidence": 0.0-1.0 confidence in this analysis
12. "reasoning": Brief explanation of your interpretation
13. "similar_patterns": Array of similar functions this relates to (guess if needed)

Focus on MEANING and BUSINESS IMPACT, not syntax."""

        try:
            response = self.llm_provider.call(prompt, system_prompt=system_prompt, 
                                             json_mode=True, max_tokens=3000)
            result = json.loads(response.content)
            
            analysis = SemanticFunctionAnalysis(
                function_name=function_name,
                source_code=source_code,
                true_purpose=result.get("true_purpose", ""),
                business_value=result.get("business_value", ""),
                user_perspective=result.get("user_perspective", ""),
                implementation_strategy=result.get("implementation_strategy", ""),
                complexity=result.get("complexity", "moderate"),
                key_risks=result.get("key_risks", []),
                data_flow=result.get("data_flow", []),
                external_dependencies=result.get("external_dependencies", []),
                embedded_rules=result.get("embedded_rules", []),
                decision_points=result.get("decision_points", []),
                confidence=float(result.get("confidence", 0.7)),
                reasoning=result.get("reasoning", ""),
                similar_patterns=result.get("similar_patterns", [])
            )
            
            self.cache[cache_key] = analysis
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            # Return a minimal analysis on error
            return SemanticFunctionAnalysis(
                function_name=function_name,
                source_code=source_code,
                true_purpose="Unable to analyze",
                business_value="",
                user_perspective="",
                implementation_strategy="",
                complexity="unknown",
                key_risks=[],
                data_flow=[],
                external_dependencies=[],
                embedded_rules=[],
                decision_points=[],
                confidence=0.0,
                reasoning=f"LLM analysis failed: {str(e)}",
                similar_patterns=[]
            )
    
    def explain_rules_humanly(self, rules: List[Dict[str, Any]], 
                             domain_context: Optional[str] = None) -> List[HumanReadableRule]:
        """
        Convert extracted rules into human-readable business language.
        
        Takes raw extracted rules and generates explanations that:
        - Are understandable by non-technical people
        - Explain business impact and context
        - Provide examples and counterexamples
        - Connect related rules
        
        Args:
            rules: List of extracted rules (from SmartRuleInference)
            domain_context: Optional business domain context
            
        Returns:
            List of HumanReadableRule with clear explanations
        """
        if not rules:
            return []
        
        rules_json = json.dumps(rules, indent=2)[:3000]  # Limit size
        
        system_prompt = """You are a business analyst who specializes in explaining technical rules
in clear, non-technical language. Your job is to make business rules understandable to everyone.

Always respond with valid JSON array."""
        
        prompt = f"""Explain these business rules in clear, human-readable language.
For EACH rule, explain:
1. What it means in simple terms
2. Why the business has this rule
3. When someone needs to follow it
4. Examples of valid and invalid cases
5. What happens if the rule is broken
6. Related rules (if any)
7. Any exceptions

EXTRACTED RULES:
{rules_json}

{f'BUSINESS DOMAIN: {domain_context}' if domain_context else ''}

Respond with JSON array where each item has:
{{
  "rule_id": "unique_id",
  "rule_type": "validation|temporal|permission|state_machine|constraint",
  "simple_explanation": "Plain English explanation",
  "business_context": "Why this rule exists",
  "when_it_applies": "When to follow this rule",
  "positive_examples": ["Valid case 1", "Valid case 2"],
  "negative_examples": ["Invalid case 1", "Invalid case 2"],
  "implications": ["What happens if broken"],
  "related_rules": ["Rule A", "Rule B"],
  "exceptions": ["When rule doesn't apply"],
  "implementation_location": "Where in code this is enforced",
  "how_verified": "How is this validated",
  "clarity": 0.7,
  "business_criticality": "critical|important|nice_to_have",
  "reasoning": "Why this assessment"
}}"""
        
        try:
            response = self.llm_provider.call(prompt, system_prompt=system_prompt,
                                             json_mode=True, max_tokens=4000)
            results = json.loads(response.content)
            
            # Convert to HumanReadableRule objects
            explanations = []
            if isinstance(results, list):
                for result in results:
                    rule = HumanReadableRule(
                        rule_id=result.get("rule_id", f"rule_{len(explanations)}"),
                        rule_type=result.get("rule_type", "constraint"),
                        simple_explanation=result.get("simple_explanation", ""),
                        business_context=result.get("business_context", ""),
                        when_it_applies=result.get("when_it_applies", ""),
                        positive_examples=result.get("positive_examples", []),
                        negative_examples=result.get("negative_examples", []),
                        implications=result.get("implications", []),
                        related_rules=result.get("related_rules", []),
                        exceptions=result.get("exceptions", []),
                        implementation_location=result.get("implementation_location", ""),
                        how_verified=result.get("how_verified", ""),
                        clarity=float(result.get("clarity", 0.5)),
                        business_criticality=result.get("business_criticality", "important"),
                        reasoning=result.get("reasoning", "")
                    )
                    explanations.append(rule)
            
            return explanations
            
        except Exception as e:
            print(f"Failed to explain rules: {e}")
            return []
    
    def summarize_business_logic(self, source_code: str, file_context: Optional[str] = None,
                                complexity_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a summary of complex business logic.
        
        Produces a high-level summary that explains:
        - What the code does at a business level
        - Main workflows and processes
        - Key business entities
        - Critical decision logic
        - Data transformations
        
        Args:
            source_code: Code to summarize
            file_context: Optional context about the file/module
            complexity_level: "simple", "moderate", or "complex" hint
            
        Returns:
            Dict with business logic summary
        """
        cache_key = f"summary_{hash(source_code)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        system_prompt = """You are a business analyst reading code.
Your job is to summarize the business logic in this code for business stakeholders.

Explain:
1. High-level workflow or process
2. Main entities involved
3. Key decisions being made
4. Business rules being enforced
5. Data transformations
6. Integration points with external systems
7. Business impact and value

Use non-technical language. Assume the audience doesn't know how to code.

Always respond with valid JSON."""
        
        code_excerpt = source_code[:2000] if len(source_code) > 2000 else source_code
        
        prompt = f"""Write a business-level summary of this code.
Explain what it does and why it matters from a BUSINESS perspective.

CODE:
```python
{code_excerpt}
```

{f'FILE CONTEXT: {file_context}' if file_context else ''}

Respond with JSON:
{{
  "business_summary": "1-2 sentence summary of what the code does",
  "main_workflow": ["step 1", "step 2", ...],
  "key_entities": ["entity 1", "entity 2", ...],
  "critical_decisions": ["if this then that", ...],
  "business_rules": ["rule 1", "rule 2", ...],
  "data_transformations": ["transforms X into Y", ...],
  "external_integrations": ["integrates with X", ...],
  "business_value": "What value does this create for the business?",
  "risks": ["potential risk 1", "potential risk 2", ...],
  "complexity_assessment": "simple|moderate|complex|architectural"
}}"""
        
        try:
            response = self.llm_provider.call(prompt, system_prompt=system_prompt,
                                             json_mode=True, max_tokens=2500)
            result = json.loads(response.content)
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Failed to summarize business logic: {e}")
            return {"error": str(e)}
    
    def validate_pattern(self, pattern: Dict[str, Any], 
                        codebase_context: Optional[str] = None) -> ValidatedPattern:
        """
        Validate an extracted pattern using LLM reasoning.
        
        Checks:
        - Is this a real, meaningful pattern?
        - How consistently is it applied?
        - Does it make sense for the business domain?
        - Can it be improved?
        - Does it conflict with other patterns?
        
        Args:
            pattern: Pattern dictionary with description and examples
            codebase_context: Optional context about the codebase
            
        Returns:
            ValidatedPattern with validation results and recommendations
        """
        pattern_name = pattern.get("name", "unknown")
        cache_key = f"validate_{pattern_name}_{hash(json.dumps(pattern))}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        system_prompt = """You are a software architecture expert.
Your job is to validate extracted patterns and provide design recommendations.

When validating a pattern:
1. Is it a real, consistent pattern or noise?
2. How well does it fit the business domain?
3. Can the naming be improved?
4. Are there design issues or conflicts?
5. How could it be better implemented?

Always respond with valid JSON."""
        
        pattern_str = json.dumps(pattern, indent=2)[:2000]
        
        prompt = f"""Validate this extracted pattern:

PATTERN:
{pattern_str}

{f'CODEBASE CONTEXT: {codebase_context}' if codebase_context else ''}

Respond with JSON:
{{
  "is_valid": true/false,
  "confidence": 0.85,
  "validation_reasoning": "Why this is/isn't valid",
  "consistency": 0.8,
  "relevance": 0.9,
  "suggested_name": "Better name for this pattern",
  "refactoring_suggestions": ["How to improve implementation"],
  "design_improvements": ["Architectural improvements"],
  "similar_patterns": ["Similar patterns in codebase"],
  "conflicts": ["Patterns that conflict with this"],
  "compatibility": {{"pattern_a": 0.9, "pattern_b": 0.5}}
}}"""
        
        try:
            response = self.llm_provider.call(prompt, system_prompt=system_prompt,
                                             json_mode=True, max_tokens=2000)
            result = json.loads(response.content)
            
            validation = ValidatedPattern(
                pattern_name=pattern_name,
                pattern_description=pattern.get("description", ""),
                is_valid=result.get("is_valid", False),
                confidence=float(result.get("confidence", 0.5)),
                validation_reasoning=result.get("validation_reasoning", ""),
                consistency=float(result.get("consistency", 0.5)),
                relevance=float(result.get("relevance", 0.5)),
                suggested_name=result.get("suggested_name", pattern_name),
                refactoring_suggestions=result.get("refactoring_suggestions", []),
                design_improvements=result.get("design_improvements", []),
                similar_patterns=result.get("similar_patterns", []),
                conflicts=result.get("conflicts", []),
                compatibility=result.get("compatibility", {})
            )
            
            self.cache[cache_key] = validation
            return validation
            
        except Exception as e:
            print(f"Failed to validate pattern: {e}")
            raise
    
    def analyze_with_extracted_rules(self, source_code: str, filename: str,
                                    enrich_with_llm: bool = True) -> Dict[str, Any]:
        """
        Combine syntactic rule extraction with semantic LLM analysis.
        
        Process:
        1. Extract rules using AST (SmartRuleInference)
        2. Analyze functions semantically (LLM)
        3. Generate human-readable explanations (LLM)
        4. Validate patterns (LLM)
        
        Args:
            source_code: Code to analyze
            filename: File path/name
            enrich_with_llm: If True, enhance with LLM analysis (slower but better)
            
        Returns:
            Comprehensive analysis dict with both syntactic and semantic insights
        """
        # Step 1: Extract rules syntactically
        extracted = self.rule_inference.infer_all_rules(source_code, filename)
        
        if not enrich_with_llm:
            return extracted
        
        # Step 2: Extract functions for semantic analysis
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return extracted
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_code = ast.unparse(node)
                functions.append({
                    "name": node.name,
                    "code": func_code,
                    "line": node.lineno
                })
        
        # Step 3: Analyze first few functions semantically (limit for API costs)
        semantic_analyses = []
        for func in functions[:3]:  # Limit to 3 functions for cost
            try:
                analysis = self.analyze_function_semantics(func["code"], func["name"])
                semantic_analyses.append(asdict(analysis))
            except Exception as e:
                print(f"Failed to analyze {func['name']}: {e}")
        
        # Step 4: Explain rules in human language
        human_readable = []
        if extracted.get("validation_rules") or extracted.get("constraint_rules"):
            rules_to_explain = (
                extracted.get("validation_rules", [])[:5] +
                extracted.get("constraint_rules", [])[:5]
            )
            human_readable = [asdict(r) for r in self.explain_rules_humanly(rules_to_explain)]
        
        # Step 5: Summarize business logic
        business_summary = self.summarize_business_logic(source_code, f"File: {filename}")
        
        # Combine all results
        return {
            "filename": filename,
            "syntactic_analysis": {
                "validation_rules": extracted.get("validation_rules", []),
                "temporal_dependencies": extracted.get("temporal_dependencies", []),
                "permission_rules": extracted.get("permission_rules", []),
                "constraint_rules": extracted.get("constraint_rules", []),
                "statistics": extracted.get("statistics", {})
            },
            "semantic_analysis": {
                "function_analyses": semantic_analyses,
                "business_summary": business_summary
            },
            "human_readable_rules": human_readable,
            "analysis_metadata": {
                "provider": self.provider_name,
                "functions_analyzed": len(semantic_analyses),
                "rules_explained": len(human_readable)
            }
        }


def demonstrate_llm_rule_inference():
    """Demonstrate the LLM-enhanced rule inference system."""
    
    print("\n" + "="*70)
    print("LLM-ENHANCED RULE INFERENCE ENGINE DEMO")
    print("="*70)
    
    # Sample business logic code
    sample_code = '''
def process_order(order):
    """Process a customer order."""
    # Validation rules embedded in code
    if order.amount <= 0 or order.amount > 999999.99:
        raise ValueError("Invalid order amount")
    
    if order.customer_age < 18:
        raise ValueError("Customer must be 18+")
    
    # Temporal dependencies
    customer = authenticate_customer(order.customer_id)  # Must happen first
    validate_inventory(order)  # Must happen before payment
    process_payment(order)  # Must happen after validation
    
    # State transitions
    order.status = 'pending'
    update_database(order)
    order.status = 'processing'
    send_confirmation(order)  # Must happen last
    order.status = 'completed'
    
    return order
'''
    
    try:
        # Initialize engine
        print("\n1. Initializing LLM Rule Inference Engine...")
        engine = LLMRuleInferenceEngine()
        print(f"   ✓ Using {engine.provider_name}")
        
        # Semantic analysis
        print("\n2. Analyzing function semantics...")
        analysis = engine.analyze_function_semantics(
            sample_code,
            "process_order",
            ask_specifically="What is the TRUE purpose of this function from a business perspective?"
        )
        print(f"   Purpose: {analysis.true_purpose}")
        print(f"   Business Value: {analysis.business_value}")
        print(f"   Complexity: {analysis.complexity}")
        print(f"   Key Risks: {', '.join(analysis.key_risks[:2])}")
        
        # Combined analysis
        print("\n3. Running combined syntactic + semantic analysis...")
        full_analysis = engine.analyze_with_extracted_rules(sample_code, "example.py", 
                                                            enrich_with_llm=True)
        
        print(f"\n   Extracted Rules:")
        print(f"   - Validation rules: {len(full_analysis['syntactic_analysis']['validation_rules'])}")
        print(f"   - Temporal dependencies: {len(full_analysis['syntactic_analysis']['temporal_dependencies'])}")
        print(f"   - Functions analyzed: {full_analysis['analysis_metadata']['functions_analyzed']}")
        
        if full_analysis.get('semantic_analysis', {}).get('business_summary'):
            summary = full_analysis['semantic_analysis']['business_summary']
            print(f"\n   Business Summary: {summary.get('business_summary', 'N/A')}")
        
        print("\n✅ LLM Rule Inference successful!")
        
    except ValueError as e:
        print(f"❌ LLM Setup Error: {e}")
        print("\nTo use this feature:")
        print("  Gemini:  export GOOGLE_API_KEY='your-key-here'")
        print("  Claude:  export ANTHROPIC_API_KEY='your-key-here'")


if __name__ == "__main__":
    demonstrate_llm_rule_inference()
