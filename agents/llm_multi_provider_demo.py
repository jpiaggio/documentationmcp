"""
Multi-Provider LLM Demo

Shows how to use the unified LLM system with multiple providers:
- Claude (Anthropic)
- Gemini (Google)

Demonstrates:
1. Provider selection and auto-detection
2. Switching between providers
3. Using the same interface with different LLMs
4. Getting recommendations for available providers
"""

try:
    from .llm_providers import LLMProviderFactory, get_llm_provider
    from .llm_code_analyzer import LLMCodeAnalyzer
    from .unified_analyzer import UnifiedCodeAnalyzer, InteractiveLLMAnalysis
except ImportError:
    from llm_providers import LLMProviderFactory, get_llm_provider
    from llm_code_analyzer import LLMCodeAnalyzer
    from unified_analyzer import UnifiedCodeAnalyzer, InteractiveLLMAnalysis


def demo_provider_info():
    """Show available providers and their status."""
    print("\n" + "="*60)
    print("DEMO 1: Provider Information")
    print("="*60)
    
    providers = LLMProviderFactory.list_providers()
    print("\nAvailable LLM Providers:")
    for name, status in providers.items():
        print(f"  {name.upper():10} {status}")
    
    print("\nSetup Instructions:")
    print("  Claude:  export ANTHROPIC_API_KEY='sk-ant-...'")
    print("  Gemini:  export GOOGLE_API_KEY='...'")


def demo_auto_detection():
    """Auto-detect and use default provider."""
    print("\n" + "="*60)
    print("DEMO 2: Auto-Detection (Simplified)")
    print("="*60 + "\n")
    
    print("Auto-detecting available LLM provider...")
    
    try:
        # This will auto-detect Claude or Gemini based on env vars
        analyzer = LLMCodeAnalyzer()
        print(f"✓ Successfully initialized with {analyzer.provider_name.upper()}")
        print(f"  Model: {analyzer.llm_provider.model}")
    except ValueError as e:
        print(f"✗ No LLM provider configured")
        print(f"  Error: {e}")


def demo_explicit_provider():
    """Explicitly choose a provider."""
    print("\n" + "="*60)
    print("DEMO 3: Explicit Provider Selection")
    print("="*60 + "\n")
    
    providers_to_try = ["claude", "gemini"]
    
    for provider_name in providers_to_try:
        print(f"\nTrying {provider_name.upper()}...")
        try:
            analyzer = LLMCodeAnalyzer(provider=provider_name)
            print(f"  ✓ {provider_name.upper()} is available")
            print(f"    Model: {analyzer.llm_provider.model}")
        except ValueError as e:
            print(f"  ✗ {provider_name.upper()} not available")
            print(f"    ({e})")


def demo_unified_analyzer_multi_provider():
    """Show unified analyzer working with different providers."""
    print("\n" + "="*60)
    print("DEMO 4: Unified Analyzer (Multi-Provider)")
    print("="*60 + "\n")
    
    sample_code = '''
def calculate_discount(customer_type, total_amount):
    """Calculate discount based on customer type and amount."""
    if customer_type == "VIP":
        if total_amount > 1000:
            return 0.20  # 20% discount
        elif total_amount > 500:
            return 0.15  # 15% discount
        else:
            return 0.10  # 10% discount
    elif customer_type == "REGULAR":
        if total_amount > 500:
            return 0.05  # 5% discount
    return 0.0  # No discount
'''
    
    print("Sample Code:")
    print(sample_code)
    print("\nAnalyzing with available provider...")
    
    try:
        analyzer = UnifiedCodeAnalyzer()
        if analyzer.provider_name:
            print(f"✓ Using provider: {analyzer.provider_name.upper()}")
            
            # Show what we would analyze (without actually calling API)
            print("\nExample Analysis (simulated):")
            print("""
FUNCTION: calculate_discount
INTERPRETATION: Provides progressive discounts for VIP customers and bulk purchases
BUSINESS VALUE: Incentivizes larger purchases and rewards loyal customers
COMPLEXITY: Moderate
RISKS:
  - Hard-coded discount tiers (not flexible)
  - No consideration for item type or margin
  - VIP customers lose bulk discount if below 1000
            """)
        else:
            print("✗ No provider available - skipping analysis example")
            print("\nTo enable this demo, set ANTHROPIC_API_KEY or GOOGLE_API_KEY")
    except Exception as e:
        print(f"✗ Could not initialize analyzer")
        print(f"  {e}")


def demo_interactive_session():
    """Show interactive analysis session."""
    print("\n" + "="*60)
    print("DEMO 5: Interactive Q&A Session")
    print("="*60 + "\n")
    
    code = '''
def process_payment(customer_id, amount, card_token):
    """Process a payment for a customer."""
    # Validate amount
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    # Charge the card
    charge_result = stripe.charge(card_token, amount)
    
    if not charge_result.success:
        return {"status": "failed", "error": charge_result.error}
    
    # Record in database
    payment = Payment(
        customer_id=customer_id,
        amount=amount,
        stripe_id=charge_result.id,
        status="completed"
    )
    payment.save()
    
    # Send receipt email
    send_receipt_email(customer_id, amount)
    
    return {"status": "success", "payment_id": payment.id}
'''
    
    print("Code to analyze:")
    print(code)
    print("\nStarting interactive session...\n")
    
    try:
        session = InteractiveLLMAnalysis(code, "payment_processor.py")
        if session.unified_analyzer.provider_name:
            print(f"✓ Session started with {session.unified_analyzer.provider_name.upper()}")
            
            print("\nAvailable commands:")
            print("  session.ask('Your question?')       - Ask about the code")
            print("  session.get_summary()               - What does it do?")
            print("  session.get_risks()                 - What could go wrong?")
            print("  session.get_improvements()          - How to improve?")
            print("  session.find_dependencies()         - What systems does it need?")
            print("  session.analyze_flow('payment')     - Trace entity flow")
            
            print("\n(Note: Actual API calls would be made with configured API key)")
        else:
            print("✗ No provider available for interactive session")
            print("\nTo enable this demo, set ANTHROPIC_API_KEY or GOOGLE_API_KEY")
    except ValueError as e:
        print(f"✗ Could not start session")
        print(f"  {e}")


def demo_provider_switching():
    """Show switching between providers."""
    print("\n" + "="*60)
    print("DEMO 6: Provider Switching")
    print("="*60 + "\n")
    
    print("Creating analyzers with different providers...\n")
    
    configs = [
        {"provider": "claude", "desc": "Claude (Anthropic)"},
        {"provider": "gemini", "desc": "Gemini (Google)"},
        {"provider": None, "desc": "Auto-detect"},
    ]
    
    for config in configs:
        provider = config["provider"]
        desc = config["desc"]
        
        print(f"Attempting: {desc}")
        try:
            if provider is None:
                analyzer = LLMCodeAnalyzer()
            else:
                analyzer = LLMCodeAnalyzer(provider=provider)
            
            print(f"  ✓ SUCCESS using {analyzer.provider_name.upper()}")
        except ValueError as e:
            print(f"  ✗ FAILED - {str(e)[:60]}...")
        print()


def demo_feature_compatibility():
    """Show feature compatibility across providers."""
    print("\n" + "="*60)
    print("DEMO 7: Feature Compatibility")
    print("="*60 + "\n")
    
    features = [
        ("Semantic Understanding", "interpret_function()"),
        ("Business Logic Summary", "summarize_complex_logic()"),
        ("Business Rule Explanation", "explain_business_rules()"),
        ("Pattern Validation", "validate_patterns()"),
        ("Business Impact Analysis", "analyze_business_impact()"),
        ("Interactive Q&A", "ask_followup()"),
    ]
    
    print("Features available across all providers:\n")
    
    for feature, method in features:
        print(f"✓ {feature:30} ({method})")
    
    print("\nAll features work with both Claude and Gemini!")
    print("\nProvider-specific models:")
    print("  Claude: claude-3-5-sonnet, claude-3-haiku, claude-3-opus")
    print("  Gemini: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash")


def main():
    """Run all demonstrations."""
    print("""
╔════════════════════════════════════════════════════════════════╗
║            Multi-Provider LLM Integration Demo                 ║
║                                                                ║
║  Demonstrates using Claude and Gemini with the same interface  ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Run demonstrations
    demo_provider_info()
    demo_auto_detection()
    demo_explicit_provider()
    demo_unified_analyzer_multi_provider()
    demo_interactive_session()
    demo_provider_switching()
    demo_feature_compatibility()
    
    print("\n" + "="*60)
    print("Setup for Real Usage")
    print("="*60)
    print("""
To use with Claude:
  1. Get API key from https://console.anthropic.com
  2. export ANTHROPIC_API_KEY='sk-ant-...'
  3. pip install anthropic
  
To use with Gemini:
  1. Get API key from https://aistudio.google.com/apikey
  2. export GOOGLE_API_KEY='...'
  3. pip install google-generativeai

Then run:
  analyzer = LLMCodeAnalyzer()  # Auto-detect
  # or
  analyzer = LLMCodeAnalyzer(provider="gemini")  # Explicit
    """)


if __name__ == "__main__":
    main()
