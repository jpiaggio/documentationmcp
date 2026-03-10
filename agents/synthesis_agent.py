from typing import Dict, Any, List

class SynthesisAgent:
    """
    SynthesisAgent generates a layered natural language narrative for a Product Manager
    from a subgraph of code context and business rules.
    """

    def __init__(self, llm):
        """
        llm: An LLM interface with a .generate(prompt: str) -> str method.
        """
        self.llm = llm

    def synthesize(self, subgraph: Dict[str, Any], business_rules: List[str]) -> Dict[str, str]:
        """
        subgraph: Dict with nodes and edges representing the code context.
        business_rules: List of business rule strings.
        Returns a dict with keys: 'executive_summary', 'why', 'user_journey'.
        """
        # Layer 1: Executive Summary
        exec_summary_prompt = self._build_exec_summary_prompt(subgraph, business_rules)
        executive_summary = self.llm.generate(exec_summary_prompt)

        # Layer 2: Why (Business Logic Rationale)
        why_prompt = self._build_why_prompt(subgraph, business_rules)
        why = self.llm.generate(why_prompt)

        # Layer 3: User Journey
        journey_prompt = self._build_user_journey_prompt(subgraph)
        user_journey = self.llm.generate(journey_prompt)

        return {
            "executive_summary": executive_summary.strip(),
            "why": why.strip(),
            "user_journey": user_journey.strip()
        }

    def _build_exec_summary_prompt(self, subgraph, business_rules):
        return (
            "You are an expert technical writer. "
            "Given the following code modules and business rules, write a concise executive summary "
            "for a Product Manager, focusing on what this system or feature does.\n\n"
            f"Modules: {', '.join(node['name'] for node in subgraph.get('nodes', []))}\n"
            f"Business Rules: {'; '.join(business_rules)}\n"
            "Executive Summary:"
        )

    def _build_why_prompt(self, subgraph, business_rules):
        return (
            "You are a business analyst. "
            "Given the following business rules and code modules, explain the rationale behind the business logic. "
            "Why were these rules implemented? What business goals do they serve?\n\n"
            f"Business Rules: {'; '.join(business_rules)}\n"
            f"Modules: {', '.join(node['name'] for node in subgraph.get('nodes', []))}\n"
            "Rationale:"
        )

    def _build_user_journey_prompt(self, subgraph):
        # Assume edges are in the form {'source': 'ModuleA', 'target': 'ModuleB', 'type': 'CALLS'}
        journey_steps = []
        for edge in subgraph.get('edges', []):
            journey_steps.append(f"{edge['source']} → {edge['target']} ({edge['type']})")
        journey_str = " → ".join(journey_steps) if journey_steps else "N/A"
        return (
            "You are a UX writer. "
            "Describe the user journey through the following modules, step by step, "
            "explaining how a user interacts with the system from start to finish.\n\n"
            f"Module Flow: {journey_str}\n"
            "User Journey:"
        )

# Example usage:
# llm = YourLLMWrapper()
# agent = SynthesisAgent(llm)
# narrative = agent.synthesize(subgraph, business_rules)
