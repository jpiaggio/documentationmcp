"""
Unified LLM-Enhanced Analysis Pipeline

Integrates LLM code analysis with existing:
- Semantic analysis (call graphs, data flows)
- Business rules extraction
- Entity graph analysis
- Pattern recognition

Creates a comprehensive understanding combining:
- Structural analysis (what's there)
- Semantic analysis (what it does)
- Business analysis (why it matters)
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_code_analyzer import (
    LLMCodeAnalyzer, BusinessLogicExplainer, PatternValidator,
    CodeInterpretation, BusinessRuleExplanation, PatternValidation
)

# Import with fallback for different import styles
try:
    from .llm_providers import LLMProviderFactory, get_llm_provider
except ImportError:
    from llm_providers import LLMProviderFactory, get_llm_provider

from semantic_analyzer import SemanticAnalyzer
from business_rules_extractor import BusinessRulesExtractor


@dataclass
class EnhancedCodeAnalysis:
    """Complete analysis combining structural and semantic understanding."""
    filename: str
    function_name: str
    
    # Structural analysis
    call_graph: Dict[str, Any]
    data_flows: List[Tuple[str, str]]
    
    # LLM semantic analysis
    interpretation: CodeInterpretation
    business_impact: Dict[str, Any]
    
    # Business rules
    business_rules: List[Dict[str, Any]]
    
    # Combined insights
    risk_assessment: str
    improvement_suggestions: List[str]


class UnifiedCodeAnalyzer:
    """
    Unified analyzer combining structural and LLM-based semantic analysis.
    
    This bridges:
    - Semantic analyzer (AST-based structure)
    - Business rules extractor (business logic)
    - LLM code analyzer (semantic intent)
    - Entity graph (relationships)
    """
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, 
                 model: Optional[str] = None):
        """
        Initialize unified analyzer with flexible provider selection.
        
        Args:
            provider: "claude", "gemini", or None (auto-detect)
            api_key: API key (optional, defaults to env var)
            model: Model name (optional, uses provider default)
            
        Examples:
            # Auto-detect provider
            analyzer = UnifiedCodeAnalyzer()
            
            # Use Gemini
            analyzer = UnifiedCodeAnalyzer(provider="gemini")
            
            # Use Claude with custom model
            analyzer = UnifiedCodeAnalyzer(provider="claude", 
                                          model="claude-3-haiku-20240307")
        """
        self.semantic_analyzer = SemanticAnalyzer()
        self.business_extractor = BusinessRulesExtractor()
        
        try:
            self.llm_analyzer = LLMCodeAnalyzer(provider=provider, api_key=api_key, model=model)
            self.provider_name = self.llm_analyzer.provider_name
        except ValueError as e:
            print(f"Warning: LLM analyzer initialization failed: {e}")
            print("\nAvailable Providers:")
            for name, status in LLMProviderFactory.list_providers().items():
                print(f"  {name.capitalize()}: {status}")
            self.llm_analyzer = None
            self.provider_name = None
        
        self.enhanced_analyses = []
    
    def analyze_code_deeply(self, source_code: str, filename: str) -> Dict[str, Any]:
        """
        Perform deep analysis combining all approaches.
        
        Requires at least one LLM provider (Claude or Gemini) to be configured.
        
        Returns: Complete analysis with structure, semantics, and business insights.
        """
        if not self.llm_analyzer:
            providers = LLMProviderFactory.list_providers()
            msg = "LLM analyzer not initialized. Configure an LLM provider:\n"
            for name, status in providers.items():
                msg += f"  - {name.upper()}: {status}\n"
            msg += "\nSet ANTHROPIC_API_KEY (for Claude) or GOOGLE_API_KEY (for Gemini)"
            raise ValueError(msg)
        
        # Step 1: Structural analysis
        print(f"📊 Analyzing structure of {filename}...")
        semantic_results = self.semantic_analyzer.analyze(source_code, filename)
        
        # Step 2: Business rules extraction
        print(f"🎯 Extracting business logic...")
        business_processes = self.business_extractor.extract_business_processes(source_code, filename)
        business_rules = self.business_extractor.extract_business_rules(source_code, filename)
        
        # Step 3: LLM semantic analysis for each function
        print(f"🤖 Analyzing semantic intent with LLM...")
        function_interpretations = {}
        
        functions_info = semantic_results['call_graph'].get('functions', {})
        for func_name in list(functions_info.keys())[:5]:  # Analyze first 5 functions
            try:
                # Extract function code
                func_code = self._extract_function_code(source_code, func_name)
                if func_code:
                    interpretation = self.llm_analyzer.interpret_function(func_code, func_name)
                    function_interpretations[func_name] = interpretation
                    print(f"   ✓ {func_name}: {interpretation.interpreted_purpose[:60]}...")
            except Exception as e:
                print(f"   ⚠️  Error analyzing {func_name}: {e}")
        
        # Step 4: Analyze business impact
        print(f"💼 Analyzing business impact...")
        business_impacts = {}
        for func_name in list(function_interpretations.keys())[:3]:
            try:
                func_code = self._extract_function_code(source_code, func_name)
                impact = self.llm_analyzer.analyze_business_impact(func_code, metric=func_name)
                business_impacts[func_name] = impact
            except Exception as e:
                print(f"   ⚠️  Could not analyze impact for {func_name}: {e}")
        
        # Step 5: Validate extracted patterns
        print(f"✅ Validating extracted patterns...")
        pattern_data = self._prepare_patterns_for_validation(
            business_processes, business_rules
        )
        
        validation_results = {}
        if hasattr(self.llm_analyzer, 'validate_patterns'):
            for pattern_name, evidence in list(pattern_data.items())[:3]:
                try:
                    validation = self.llm_analyzer.validate_patterns(
                        pattern_description=f"Pattern: {pattern_name}",
                        code_evidence=evidence,
                        pattern_name=pattern_name
                    )
                    validation_results[pattern_name] = validation
                    status = "✓" if validation.is_valid else "✗"
                    print(f"   {status} {pattern_name} (confidence: {validation.confidence:.1%})")
                except Exception as e:
                    print(f"   ⚠️  Could not validate {pattern_name}: {e}")
        
        return {
            'filename': filename,
            'semantic_analysis': semantic_results,
            'business_processes': business_processes,
            'business_rules': business_rules,
            'function_interpretations': function_interpretations,
            'business_impacts': business_impacts,
            'pattern_validations': validation_results
        }
    
    def generate_comprehensive_report(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a comprehensive report from unified analysis.
        
        Format: Executive summary + detailed analysis + recommendations.
        """
        report = f"""# Code Analysis Report: {analysis['filename']}

## Executive Summary

### What This Code Does
This module performs the following key functions:
"""
        
        # Add function interpretations
        for func_name, interpretation in analysis['function_interpretations'].items():
            report += f"\n**{func_name}**: {interpretation.interpreted_purpose}\n"
        
        # Add business processes
        report += f"\n## Business Processes\n"
        for process in analysis['business_processes'][:5]:
            report += f"- {process.get('name', 'Unknown')}: {process.get('context', '...')}\n"
        
        # Add business impacts
        report += f"\n## Business Impact Analysis\n"
        for func_name, impact in analysis['business_impacts'].items():
            report += f"\n### {func_name}\n"
            if isinstance(impact, dict):
                report += f"- Criticality: {impact.get('criticality', 'Unknown')}\n"
                report += f"- Affected Users: {impact.get('affected_users', 'Unknown')}\n"
                report += f"- Risk Level: {impact.get('risk_level', 'Unknown')}\n"
        
        # Add pattern validations
        report += f"\n## Pattern Validation Results\n"
        total_patterns = len(analysis['pattern_validations'])
        valid_patterns = sum(1 for v in analysis['pattern_validations'].values() if v.is_valid)
        
        report += f"- Total Patterns: {total_patterns}\n"
        report += f"- Valid Patterns: {valid_patterns}\n"
        report += f"- Validity Rate: {(valid_patterns/total_patterns*100) if total_patterns > 0 else 0:.1f}%\n"
        
        for pattern_name, validation in analysis['pattern_validations'].items():
            status = "✓" if validation.is_valid else "✗"
            report += f"\n{status} **{pattern_name}**\n"
            report += f"   Confidence: {validation.confidence:.1%}\n"
            if validation.recommendations:
                report += f"   Recommendations: {', '.join(validation.recommendations[:2])}\n"
        
        # Add recommendations
        report += f"\n## Recommendations\n"
        all_recommendations = set()
        for validation in analysis['pattern_validations'].values():
            all_recommendations.update(validation.recommendations)
        
        for i, rec in enumerate(list(all_recommendations)[:5], 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def create_business_documentation(self, source_code: str, filename: str) -> str:
        """
        Create business-focused documentation from code.
        
        explains what code does in business terms, not technical terms.
        """
        if not self.llm_analyzer:
            raise ValueError("LLM analyzer not initialized")
        
        explainer = BusinessLogicExplainer(api_key=self.llm_analyzer.api_key)
        
        # Extract functions
        functions = self._extract_all_functions(source_code)
        
        # Generate documentation
        documentation = f"""# Business Logic Documentation: {filename}

## Overview
This document explains what this code does in business terms.

"""
        
        # Add function explanations
        interpretations = explainer.analyze_function_group(functions)
        
        for interpretation in interpretations:
            documentation += f"""
## {interpretation.function_name}

**What It Does**: {interpretation.interpreted_purpose}

**Key Activities**:
"""
            for op in interpretation.key_operations:
                documentation += f"- {op}\n"
            
            documentation += f"""
**Why It Matters**: {interpretation.business_value}

**Complexity**: {interpretation.complexity_rating}

**Important Considerations**:
"""
            for risk in interpretation.risks:
                documentation += f"- ⚠️ {risk}\n"
        
        return documentation
    
    def ask_question_about_code(self, source_code: str, question: str) -> str:
        """
        Ask LLM a question about code.
        
        Examples:
        - "What happens if payment fails?"
        - "How are user permissions validated?"
        - "What's the most critical function here?"
        """
        if not self.llm_analyzer:
            raise ValueError("LLM analyzer not initialized")
        
        # Add source code context
        full_prompt = f"""Given this code:

```python
{source_code[:3000]}
```

Question: {question}

Provide a clear, actionable answer."""
        
        return self.llm_analyzer.ask_followup(full_prompt, context="code_qa")
    
    # Helper methods
    
    def _extract_function_code(self, source_code: str, function_name: str) -> Optional[str]:
        """Extract specific function code from source."""
        import ast
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == function_name:
                        start = node.col_offset
                        end = node.end_col_offset or len(source_code)
                        lines = source_code.split('\n')
                        start_line = node.lineno - 1
                        end_line = node.end_lineno or len(lines)
                        return '\n'.join(lines[start_line:end_line])
        except:
            pass
        return None
    
    def _extract_all_functions(self, source_code: str) -> Dict[str, str]:
        """Extract all function definitions."""
        import ast
        functions = {}
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines = source_code.split('\n')
                    start = node.lineno - 1
                    end = node.end_lineno or len(lines)
                    functions[node.name] = '\n'.join(lines[start:end])
        except:
            pass
        return functions
    
    def _prepare_patterns_for_validation(self, 
                                        processes: List[Dict],
                                        rules: List[Dict]) -> Dict[str, List[str]]:
        """Prepare extracted patterns for validation."""
        pattern_data = {}
        
        for process in processes[:3]:
            name = process.get('name', 'Unknown')
            context = process.get('context', '')
            pattern_data[name] = [context] if context else []
        
        for rule in rules[:3]:
            name = rule.get('name', 'Unknown')
            context = rule.get('context', '')
            if name not in pattern_data:
                pattern_data[name] = []
            if context:
                pattern_data[name].append(context)
        
        return pattern_data


class InteractiveLLMAnalysis:
    """Interactive session for asking questions about code."""
    
    def __init__(self, source_code: str, filename: str, provider: Optional[str] = None,
                 api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize interactive analysis session.
        
        Args:
            source_code: Code to analyze
            filename: Name of file for context
            provider: "claude", "gemini", or None (auto-detect)
            api_key: API key (optional, defaults to env var)
            model: Model name (optional)
        """
        self.source_code = source_code
        self.filename = filename
        self.unified_analyzer = UnifiedCodeAnalyzer(provider=provider, api_key=api_key, model=model)
        self.conversation_context = "code_analysis"
    
    def ask(self, question: str) -> str:
        """Ask a question about the code."""
        return self.unified_analyzer.ask_question_about_code(
            self.source_code, question
        )
    
    def get_summary(self) -> str:
        """Get a summary of what the code does."""
        return self.ask("What does this code do overall? Provide a 2-3 sentence summary for a business stakeholder.")
    
    def get_risks(self) -> str:
        """Get potential risks and issues."""
        return self.ask("What are the potential risks and issues with this code? What could go wrong?")
    
    def get_improvements(self) -> str:
        """Get improvement suggestions."""
        return self.ask("How could this code be improved? What's missing or could be done better?")
    
    def analyze_flow(self, entity: str) -> str:
        """Analyze how an entity flows through the code."""
        return self.ask(f"How does {entity} flow through this code? Trace its path and transformations.")
    
    def find_dependencies(self) -> str:
        """Find external dependencies."""
        return self.ask("What external systems, databases, and APIs does this code depend on?")
