"""
LLM Provider Abstraction Layer

Supports multiple LLM providers (Claude, Gemini, etc.)
Switch providers easily by setting environment variables or parameters.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def call(self, message: str, system_prompt: Optional[str] = None, 
             json_mode: bool = False, max_tokens: int = 2000) -> LLMResponse:
        """
        Call the LLM with a message.
        
        Args:
            message: The user message/prompt
            system_prompt: Optional system prompt
            json_mode: Request JSON output
            max_tokens: Maximum tokens in response
            
        Returns:
            LLMResponse with standardized content
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Check if API credentials are available and valid"""
        pass


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key: Optional[str] = None, 
                 model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Claude provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.provider_name = "claude"
        
        # Lazy import
        self.client = None

    def _get_client(self):
        """Lazy load Anthropic client"""
        if self.client is None:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic library not installed. "
                    "Install with: pip install anthropic"
                )
        return self.client

    def validate_credentials(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key)

    def call(self, message: str, system_prompt: Optional[str] = None,
             json_mode: bool = False, max_tokens: int = 2000) -> LLMResponse:
        """Call Claude API"""
        if not self.validate_credentials():
            raise ValueError("ANTHROPIC_API_KEY not set")

        client = self._get_client()

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[{"role": "user", "content": message}],
            )

            content = response.content[0].text
            
            # Try to parse JSON if json_mode requested
            if json_mode:
                try:
                    parsed = json.loads(content)
                    content = json.dumps(parsed)
                except json.JSONDecodeError:
                    # Return as-is if not valid JSON
                    pass

            return LLMResponse(
                content=content,
                provider="claude",
                model=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            )

        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")


class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""

    def __init__(self, api_key: Optional[str] = None,
                 model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Gemini model to use
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.provider_name = "gemini"
        
        # Lazy import
        self.client = None

    def _get_client(self):
        """Lazy load Gemini client"""
        if self.client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
            except ImportError:
                raise ImportError(
                    "google-generativeai library not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self.client

    def validate_credentials(self) -> bool:
        """Check if API key is set"""
        return bool(self.api_key)

    def call(self, message: str, system_prompt: Optional[str] = None,
             json_mode: bool = False, max_tokens: int = 2000) -> LLMResponse:
        """Call Gemini API"""
        if not self.validate_credentials():
            raise ValueError("GOOGLE_API_KEY not set")

        genai = self._get_client()

        try:
            # Build the prompt with system message if provided
            full_message = message
            if system_prompt:
                full_message = f"{system_prompt}\n\n{message}"

            # Create model with generation config
            model = genai.GenerativeModel(
                self.model,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": max_tokens,
                }
            )

            response = model.generate_content(full_message)
            content = response.text

            # Try to parse JSON if json_mode requested
            if json_mode:
                try:
                    parsed = json.loads(content)
                    content = json.dumps(parsed)
                except json.JSONDecodeError:
                    # Return as-is if not valid JSON
                    pass

            # Estimate tokens (Gemini doesn't always return token counts)
            estimated_tokens = len(full_message.split()) + len(content.split())

            return LLMResponse(
                content=content,
                provider="gemini",
                model=self.model,
                tokens_used=estimated_tokens,
            )

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")


class LLMProviderFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create(provider: Optional[str] = None,
               api_key: Optional[str] = None,
               model: Optional[str] = None) -> LLMProvider:
        """
        Create an LLM provider.
        
        Args:
            provider: "claude", "gemini", or None (auto-detect)
            api_key: API key (optional, defaults to env var)
            model: Model name (optional, uses default if not specified)
            
        Returns:
            LLMProvider instance
            
        Examples:
            # Auto-detect from environment
            provider = LLMProviderFactory.create()
            
            # Explicit provider
            provider = LLMProviderFactory.create("gemini")
            
            # With custom key
            provider = LLMProviderFactory.create("claude", api_key="sk-...")
        """
        
        # Auto-detect if not specified
        if provider is None:
            claude_key = os.getenv("ANTHROPIC_API_KEY")
            gemini_key = os.getenv("GOOGLE_API_KEY")
            
            if claude_key and not gemini_key:
                provider = "claude"
            elif gemini_key and not claude_key:
                provider = "gemini"
            elif claude_key and gemini_key:
                # Prefer Claude if both available
                provider = "claude"
            else:
                raise ValueError(
                    "No LLM API key found. Set ANTHROPIC_API_KEY or GOOGLE_API_KEY"
                )

        provider = provider.lower()

        if provider == "claude":
            return ClaudeProvider(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
        elif provider == "gemini":
            return GeminiProvider(api_key=api_key, model=model or "gemini-2.0-flash")
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def list_providers() -> Dict[str, str]:
        """List available providers and their status"""
        providers = {}
        
        # Check Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            providers["claude"] = "✓ Available"
        else:
            providers["claude"] = "✗ ANTHROPIC_API_KEY not set"
        
        # Check Gemini
        if os.getenv("GOOGLE_API_KEY"):
            providers["gemini"] = "✓ Available"
        else:
            providers["gemini"] = "✗ GOOGLE_API_KEY not set"
        
        return providers


# Convenience function
def get_llm_provider(provider: Optional[str] = None,
                     api_key: Optional[str] = None,
                     model: Optional[str] = None) -> LLMProvider:
    """
    Get an LLM provider instance.
    
    Args:
        provider: "claude", "gemini", or None (auto-detect)
        api_key: API key (optional)
        model: Model name (optional)
        
    Returns:
        LLMProvider instance
        
    Examples:
        # Auto-detect
        provider = get_llm_provider()
        
        # Explicit
        provider = get_llm_provider("gemini")
        
        # With custom settings
        provider = get_llm_provider("claude", model="claude-3-haiku-20240307")
    """
    return LLMProviderFactory.create(provider=provider, api_key=api_key, model=model)


if __name__ == "__main__":
    # Show available providers
    print("Available LLM Providers:")
    print("-" * 40)
    
    providers = LLMProviderFactory.list_providers()
    for name, status in providers.items():
        print(f"  {name.capitalize():10} {status}")
    
    print("\nUsage:")
    print("  provider = get_llm_provider()  # Auto-detect")
    print("  provider = get_llm_provider('gemini')  # Explicit")
    
    # Try to create default provider
    try:
        provider = get_llm_provider()
        print(f"\n✓ Default provider: {provider.provider_name}")
        
        # Test it
        response = provider.call("What is 2 + 2?")
        print(f"Response: {response.content[:100]}...")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
