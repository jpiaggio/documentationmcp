# Multi-Provider Quick Start

**Status:** ✅ Ready to Use | **Providers:** Claude + Gemini

---

## 60-Second Setup

### Choose Your Provider

**Option A: Use Gemini (recommended for cost)**
```bash
export GOOGLE_API_KEY="your-gemini-api-key"
pip install google-generativeai
```

**Option B: Use Claude (recommended for quality)**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key"
# anthropic already installed
```

**Option C: Use Both (system decides)**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
```

### Run Demo
```bash
python3 agents/llm_multi_provider_demo.py
```

### Use It
```python
from agents.llm_code_analyzer import LLMCodeAnalyzer

# Auto-detect provider
analyzer = LLMCodeAnalyzer()

# Or explicit
analyzer = LLMCodeAnalyzer(provider="gemini")
analyzer = LLMCodeAnalyzer(provider="claude")

# Same interface, either way
result = analyzer.interpret_function(code, "func_name")
```

---

## Get API Keys

**Gemini (1 minute):**
1. Go to https://aistudio.google.com/apikey
2. Click "Get API Key"
3. Copy key
4. `export GOOGLE_API_KEY="..."`

**Claude (2 minutes):**
1. Go to https://console.anthropic.com
2. Create account
3. Click "API Keys"
4. Create key (starts with `sk-ant-`)
5. `export ANTHROPIC_API_KEY="sk-ant-..."`

---

## Features Work With Both

✓ `interpret_function()` - Semantic understanding  
✓ `summarize_complex_logic()` - Business logic explanation  
✓ `explain_business_rules()` - Rule explanation  
✓ `validate_patterns()` - Pattern validation  
✓ `analyze_business_impact()` - Business impact  
✓ `ask_followup()` - Interactive Q&A  

---

## Provider Selection

### Auto-Detect (Recommended)
```python
analyzer = LLMCodeAnalyzer()
# Uses Claude if available, else Gemini
```

### Explicit
```python
analyzer = LLMCodeAnalyzer(provider="gemini")
analyzer = LLMCodeAnalyzer(provider="claude")
```

### With Custom Model
```python
analyzer = LLMCodeAnalyzer(
    provider="gemini",
    model="gemini-1.5-pro"
)

analyzer = LLMCodeAnalyzer(
    provider="claude",
    model="claude-3-haiku-20240307"
)
```

---

## Cost Estimates

| Provider | Model | Per Analysis | 1000 Analyses |
|----------|-------|-------------|---------------|
| Claude | Sonnet | $0.02-0.03 | $20-30 |
| Claude | Haiku | $0.005-0.01 | $5-10 |
| Gemini | Flash | $0.01-0.02 | $10-20 |
| Gemini | Pro | $0.03-0.05 | $30-50 |

---

## Quick Examples

### Example 1: Switch Providers
```python
# Try Claude, fall back to Gemini
try:
    analyzer = LLMCodeAnalyzer(provider="claude")
except:
    analyzer = LLMCodeAnalyzer(provider="gemini")

result = analyzer.interpret_function(code, "func")
```

### Example 2: Use Gemini for Batch Processing
```python
analyzer = LLMCodeAnalyzer(provider="gemini")

for file in files:
    code = read(file)
    analysis = analyzer.interpret_function(code, "func")
    # Lower cost than Claude
```

### Example 3: Auto-Detect with Fallback
```python
from llm_providers import LLMProviderFactory

try:
    analyzer = LLMCodeAnalyzer()  # Auto-detect
except ValueError:
    print("No provider configured!")
    print(LLMProviderFactory.list_providers())
```

---

## Unified Analyzer

```python
from agents.unified_analyzer import UnifiedCodeAnalyzer, InteractiveLLMAnalysis

# Auto-detect provider
analyzer = UnifiedCodeAnalyzer()

# Deep analysis combining all approaches
analysis = analyzer.analyze_code_deeply(code, "file.py")
report = analyzer.generate_comprehensive_report(analysis)

# Interactive Q&A
session = InteractiveLLMAnalysis(code, "file.py", provider="gemini")
session.ask("What could break?")
session.get_summary()
session.get_improvements()
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No LLM API key found" | Set ANTHROPIC_API_KEY or GOOGLE_API_KEY |
| "anthropic not installed" | `pip install anthropic` |
| "google-generativeai not installed" | `pip install google-generativeai` |
| "GOOGLE_API_KEY not set" | Use `provider="claude"` or set env var |
| "API rate limited" | Try other provider (usually separate quotas) |

---

## Files

**New:**
- `agents/llm_providers.py` - Provider abstraction (400+ lines)
- `agents/llm_multi_provider_demo.py` - Demonstration (350+ lines)
- `GEMINI_INTEGRATION.md` - Complete documentation (600+ lines)

**Updated:**
- `agents/llm_code_analyzer.py` - Now supports multiple providers
- `agents/unified_analyzer.py` - Now supports multiple providers

**Backward Compatible:**
✅ All existing code still works unchanged!

---

## Models Available

**Claude:**
- `claude-3-5-sonnet-20241022` ⭐ Default (best quality/speed)
- `claude-3-opus-20240229` (most capable)
- `claude-3-haiku-20240307` (fastest/cheapest)

**Gemini:**
- `gemini-2.0-flash` ⭐ Default (fastest/best)
- `gemini-1.5-pro` (most capable)
- `gemini-1.5-flash` (faster/cheaper)

---

## Next Steps

1. Get API key (Claude or Gemini)
2. Set environment variable
3. Install library if needed
4. Use `LLMCodeAnalyzer()`

That's it! Same interface, works with both.

---

## Full Documentation

See [GEMINI_INTEGRATION.md](GEMINI_INTEGRATION.md) for:
- Architecture details
- Migration guide
- Comprehensive examples
- Provider comparison
- Performance benchmarks
- Troubleshooting

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Providers:** Claude (Anthropic) + Gemini (Google)
