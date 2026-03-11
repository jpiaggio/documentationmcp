"""
Deep LLM Integration for Code Analysis

Supports multiple LLM providers (Claude, Gemini, etc.) for:
- What code is really doing (semantic intent)
- Complex business logic summarization  
- Human-readable explanations of business rules
- Pattern validation and reasoning
- Business impact analysis
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

# Import from llm_providers (relative or absolute)
try:
    from .llm_providers import LLMProvider, get_llm_provider, LLMProviderFactory
except ImportError:
    from llm_providers import LLMProvider, get_llm_provider, LLMProviderFactory


@dataclass
class CodeInterpretation:
    """LLM's interpretation of what code does."""
    function_name: str
    interpreted_purpose: str  # What it's really doing
    key_operations: List[str]  # Key things it does
    business_value: str  # Why this matters to business
    risks: List[str]  # Potential issues or risks
    dependencies: List[str]  # What it depends on
    complexity_rating: str  # simple, moderate, complex
    confidence: float  # 0.0-1.0


@dataclass
class BusinessRuleExplanation:
    """Human-readable explanation of business rules."""
    rule_name: str
    simple_explanation: str  # Simple language explanation
    business_impact: str  # Why it matters
    exceptions: List[str]  # When it doesn't apply
    related_rules: List[str]  # Connected rules
    examples: List[str]  # Concrete examples
    implementation_notes: str  # How it's implemented


@dataclass
class PatternValidation:
    """Validation of extracted patterns using LLM reasoning."""
    pattern_name: str
    is_valid: bool  # Is this a real pattern?
    confidence: float  # 0.0-1.0
    reasoning: str  # Why this is/isn't valid
    similar_patterns: List[str]  # Related patterns
    counterexamples: List[str]  # Cases where it breaks
    recommendations: List[str]  # How to improve


class LLMCodeAnalyzer:
    """Uses LLM providers (Claude, Gemini, etc.) to understand code at semantic level."""
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, 
                 model: Optional[str] = None):
        """
        Initialize LLM analyzer with flexible provider selection.
        
        Args:
            provider: "claude", "gemini", or None (auto-detect from env vars)
            api_key: API key for provider (optional, defaults to env var)
            model: Model name (optional, uses provider default)
            
        Examples:
            # Auto-detect provider from environment
            analyzer = LLMCodeAnalyzer()
            
            # Explicit Gemini
            analyzer = LLMCodeAnalyzer(provider="gemini")
            
            # Custom Claude model
            analyzer = LLMCodeAnalyzer(provider="claude", model="claude-3-haiku-20240307")
        """
        try:
            self.llm_provider = get_llm_provider(provider=provider, api_key=api_key, model=model)
        except ValueError as e:
            print(f"LLM Provider Error: {e}")
            print("\nAvailable Providers:")
            for name, status in LLMProviderFactory.list_providers().items():
                print(f"  {name.capitalize()}: {status}")
            raise
        
        self.provider_name = self.llm_provider.provider_name
        self.model = model
        self.conversation_history = defaultdict(list)  # Per-context conversation
        self.cache = {}  # Cache for expensive analyses
    
    def interpret_function(self, function_code: str, function_name: str, 
                          context: Optional[str] = None) -> CodeInterpretation:
        """
        Deeply analyze what a function really does (not just metadata).
        
        Asks: "What is this function REALLY doing? What's its true purpose?"
        """
        cache_key = f"interpret_{function_name}_{hash(function_code)}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""Analyze what this function REALLY does (not just syntax, but semantic intent):

FUNCTION NAME: {function_name}

CODE:
```python
{function_code}
```

{f'CONTEXT: {context}' if context else ''}

Respond with JSON including:
1. "interpreted_purpose": One sentence describing what it REALLY does (simple language)
2. "key_operations": List of 3-5 main things it does
3. "business_value": Why this matters to the business
4. "risks": List of potential issues or edge cases
5. "dependencies": What external things it depends on (databases, APIs, etc.)
6. "complexity_rating": "simple", "moderate", or "complex"
7. "confidence": 0.0-1.0 confidence in this analysis

Think deeply about the PURPOSE, not just the MECHANICS."""

        response = self._call_llm(prompt, context="function_analysis")
        
        try:
            result = json.loads(response)
            interpretation = CodeInterpretation(
                function_name=function_name,
                interpreted_purpose=result.get("interpreted_purpose", ""),
                key_operations=result.get("key_operations", []),
                business_value=result.get("business_value", ""),
                risks=result.get("risks", []),
                dependencies=result.get("dependencies", []),
                complexity_rating=result.get("complexity_rating", "moderate"),
                confidence=float(result.get("confidence", 0.7))
            )
            
            self.cache[cache_key] = interpretation
            return interpretation
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return CodeInterpretation(
                function_name=function_name,
                interpreted_purpose=response[:200],
                key_operations=[],
                business_value="",
                risks=[],
                dependencies=[],
                complexity_rating="unknown",
                confidence=0.5
            )
    
    def summarize_complex_logic(self, code_snippet: str, title: str = "Complex Logic") -> Dict[str, Any]:
        """
        Generate a clear summary of complex business logic.
        
        Breaks down: What's happening, Why, and How to fix/improve it.
        """
        prompt = f"""Summarize this complex business logic in SIMPLE, human-readable terms:

TITLE: {title}

CODE:
```
{code_snippet}
```

Provide your response as JSON with:
1. "summary": 2-3 sentence simple explanation
2. "what_happens": Step-by-step breakdown of what happens
3. "why_it_matters": Why this logic is important
4. "potential_issues": Any problems you see
5. "how_to_improve": Suggestions for improvement
6. "human_readable_name": A simple name for this logic

Make it understandable to non-technical stakeholders."""

        response = self._call_llm(prompt, context="complex_logic")
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"summary": response, "what_happens": [], "why_it_matters": ""}
    
    def explain_business_rules(self, code_snippet: str, 
                               rule_name: str = "Business Rule") -> BusinessRuleExplanation:
        """
        Generate human-readable explanation of business rules found in code.
        
        Explains: What the rule is, why it exists, when it applies, examples.
        """
        prompt = f"""Explain this business rule in simple terms:

RULE NAME: {rule_name}

CODE:
```
{code_snippet}
```

Respond with JSON including:
1. "simple_explanation": Explain like you're talking to a business person
2. "business_impact": Why does this rule matter to the business?
3. "exceptions": When doesn't this rule apply?
4. "related_rules": Other rules that work with this one
5. "examples": 2-3 real-world examples of this rule in action
6. "implementation_notes": How is it actually implemented?

Be specific and concrete, not technical."""

        response = self._call_llm(prompt, context="business_rules")
        
        try:
            result = json.loads(response)
            return BusinessRuleExplanation(
                rule_name=rule_name,
                simple_explanation=result.get("simple_explanation", ""),
                business_impact=result.get("business_impact", ""),
                exceptions=result.get("exceptions", []),
                related_rules=result.get("related_rules", []),
                examples=result.get("examples", []),
                implementation_notes=result.get("implementation_notes", "")
            )
        except json.JSONDecodeError:
            return BusinessRuleExplanation(
                rule_name=rule_name,
                simple_explanation=response[:200],
                business_impact="",
                exceptions=[],
                related_rules=[],
                examples=[],
                implementation_notes=""
            )
    
    def validate_patterns(self, pattern_description: str, 
                         code_evidence: List[str],
                         pattern_name: str = "Pattern") -> PatternValidation:
        """
        Use LLM reasoning to validate if extracted patterns are real and valid.
        
        Checks: Is this a real pattern? How confident? What are counterexamples?
        """
        evidence_str = "\n".join([f"- {code}" for code in code_evidence[:5]])  # First 5 examples
        
        prompt = f"""Analyze if this extracted pattern is REAL and VALID:

PATTERN NAME: {pattern_name}

DESCRIPTION:
{pattern_description}

CODE EVIDENCE (examples where pattern occurs):
{evidence_str}

Respond with JSON including:
1. "is_valid": true/false - is this a real, meaningful pattern?
2. "confidence": 0.0-1.0 - how confident are you?
3. "reasoning": Explain your reasoning
4. "similar_patterns": Other patterns this is similar to
5. "counterexamples": Cases where this pattern breaks or doesn't apply
6. "recommendations": How to refine or improve this pattern

Be honest about whether this is a real pattern or just coincidence."""

        response = self._call_llm(prompt, context="pattern_validation")
        
        try:
            result = json.loads(response)
            return PatternValidation(
                pattern_name=pattern_name,
                is_valid=result.get("is_valid", False),
                confidence=float(result.get("confidence", 0.5)),
                reasoning=result.get("reasoning", ""),
                similar_patterns=result.get("similar_patterns", []),
                counterexamples=result.get("counterexamples", []),
                recommendations=result.get("recommendations", [])
            )
        except json.JSONDecodeError:
            return PatternValidation(
                pattern_name=pattern_name,
                is_valid=False,
                confidence=0.3,
                reasoning=response[:200],
                similar_patterns=[],
                counterexamples=[],
                recommendations=[]
            )
    
    def analyze_business_impact(self, code_snippet: str, 
                               metric: str = "unknown") -> Dict[str, Any]:
        """
        Analyze the business impact of code changes.
        
        Questions: Who does this affect? What breaks if it fails? How critical?
        """
        prompt = f"""Analyze the business impact of this code:

METRIC/AREA: {metric}

CODE:
```
{code_snippet}
```

Provide JSON with:
1. "affected_users": Who is affected? (customers, staff, systems)
2. "impact_category": "financial", "operational", "compliance", "user_experience", etc.
3. "failure_impact": What happens if this code fails?
4. "criticality": "critical", "high", "medium", "low"
5. "dependent_systems": What else depends on this?
6. "business_value": Quantify the business value if possible
7. "risk_level": Assessment of risk

Think from business perspective, not technical."""

        response = self._call_llm(prompt, context="business_impact")
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"summary": response}
    
    def ask_followup(self, question: str, context: str = "default") -> str:
        """
        Ask a follow-up question in the context of previous analyses.
        
        Uses conversation history to maintain context across questions.
        """
        return self._call_llm(question, context=context)
    
    def _call_llm(self, user_message: str, context: str = "default", 
                   max_tokens: int = 2000) -> str:
        """Call LLM provider with optional conversation history."""
        
        # Add to conversation history
        self.conversation_history[context].append({
            "role": "user",
            "content": user_message
        })
        
        # Keep history manageable (last 20 messages = 10 turns)
        if len(self.conversation_history[context]) > 20:
            self.conversation_history[context] = self.conversation_history[context][-20:]
        
        # Build system prompt from history
        system_prompt = "You are a helpful AI assistant analyzing code. Provide structured, technical responses."
        
        # Call LLM provider
        response = self.llm_provider.call(
            message=user_message,
            system_prompt=system_prompt,
            json_mode=False,
            max_tokens=max_tokens
        )
        
        assistant_message = response.content
        
        # Add to history
        self.conversation_history[context].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message


class BusinessLogicExplainer:
    """High-level interface for explaining business logic."""
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        self.analyzer = LLMCodeAnalyzer(provider=provider, api_key=api_key)
        self.analyses = []
    
    def analyze_function_group(self, functions: Dict[str, str]) -> List[CodeInterpretation]:
        """
        Analyze a group of related functions.
        
        Input: {"function_name": "code", ...}
        Returns: List of CodeInterpretation objects
        """
        results = []
        for func_name, func_code in functions.items():
            interpretation = self.analyzer.interpret_function(func_code, func_name)
            results.append(interpretation)
            self.analyses.append(interpretation)
        return results
    
    def generate_business_summary(self, code_modules: Dict[str, str]) -> str:
        """
        Generate an executive summary of business logic across modules.
        
        Input: {"module_name": "code", ...}
        Returns: Human-readable summary
        """
        summaries = []
        for module_name, code in code_modules.items():
            summary = self.analyzer.summarize_complex_logic(code, title=module_name)
            summaries.append(f"### {module_name}\n{summary.get('summary', '')}")
        
        # Ask Claude to synthesize into executive summary
        combined = "\n\n".join(summaries)
        prompt = f"""Create an executive summary of these business processes:

{combined}

Provide a 3-5 paragraph summary suitable for business stakeholders."""
        
        return self.analyzer.ask_followup(prompt, context="executive_summary")
    
    def validate_extracted_rules(self, rules: Dict[str, List[str]]) -> Dict[str, PatternValidation]:
        """
        Validate all extracted business rules.
        
        Input: {"rule_name": ["evidence1", "evidence2", ...], ...}
        Returns: {rule_name: PatternValidation}
        """
        results = {}
        for rule_name, evidence in rules.items():
            validation = self.analyzer.validate_patterns(
                pattern_description=f"Business rule: {rule_name}",
                code_evidence=evidence,
                pattern_name=rule_name
            )
            results[rule_name] = validation
        return results
    
    def create_documentation(self, functions: Dict[str, str]) -> str:
        """
        Create human-readable documentation from code.
        
        Input: {"function_name": "code", ...}
        Returns: Markdown documentation
        """
        doc_parts = []
        
        for func_name, func_code in functions.items():
            interpretation = self.analyzer.interpret_function(func_code, func_name)
            
            doc_parts.append(f"""
## {func_name}

**What it does:** {interpretation.interpreted_purpose}

**Key Operations:**
""")
            for op in interpretation.key_operations:
                doc_parts.append(f"- {op}")
            
            doc_parts.append(f"""
**Business Value:** {interpretation.business_value}

**Complexity:** {interpretation.complexity_rating}

**Risk Factors:**
""")
            for risk in interpretation.risks:
                doc_parts.append(f"- {risk}")
            
            if interpretation.dependencies:
                doc_parts.append("\n**Dependencies:**\n")
                for dep in interpretation.dependencies:
                    doc_parts.append(f"- {dep}")
        
        return "\n".join(doc_parts)


class PatternValidator:
    """Validates extracted patterns using LLM reasoning."""
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        self.analyzer = LLMCodeAnalyzer(provider=provider, api_key=api_key)
    
    def validate_all_patterns(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate multiple patterns with reasoning.
        
        Returns statistics on pattern validity.
        """
        validations = {}
        valid_count = 0
        total_count = 0
        
        for pattern_name, pattern_data in patterns.items():
            total_count += 1
            
            validation = self.analyzer.validate_patterns(
                pattern_description=pattern_data.get("description", ""),
                code_evidence=pattern_data.get("evidence", []),
                pattern_name=pattern_name
            )
            
            validations[pattern_name] = validation
            
            if validation.is_valid:
                valid_count += 1
        
        return {
            "total_patterns": total_count,
            "valid_patterns": valid_count,
            "validity_percentage": (valid_count / total_count * 100) if total_count > 0 else 0,
            "validations": validations
        }
    
    def generate_validation_report(self, patterns: Dict[str, Any]) -> str:
        """Generate a report on pattern validation."""
        validations = self.validate_all_patterns(patterns)
        
        report = f"""# Pattern Validation Report

## Summary
- Total Patterns: {validations['total_patterns']}
- Valid Patterns: {validations['valid_patterns']}
- Validity: {validations['validity_percentage']:.1f}%

## Details
"""
        
        for pattern_name, validation in validations['validations'].items():
            status = "✓ VALID" if validation.is_valid else "✗ INVALID"
            report += f"\n### {pattern_name} {status}\n"
            report += f"Confidence: {validation.confidence:.1%}\n"
            report += f"Reasoning: {validation.reasoning}\n"
            
            if validation.recommendations:
                report += "Recommendations:\n"
                for rec in validation.recommendations:
                    report += f"- {rec}\n"
        
        return report
