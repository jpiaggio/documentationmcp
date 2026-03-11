#!/usr/bin/env python3
import sys

# Test 1: Check tree-sitter version and capabilities
try:
    from tree_sitter import Language, Parser
    print("tree-sitter imported successfully")
except ImportError as e:
    print(f"Failed to import tree-sitter: {e}")
    sys.exit(1)

# Test 2: Check if tree-sitter-python is available
try:
    from tree_sitter_python import language as python_language
    print("tree-sitter-python is available")
    py_lang = python_language()
    print(f"Python language loaded: {py_lang}")
except ImportError:
    print("tree-sitter-python is NOT available")
except Exception as e:
    print(f"Error loading tree-sitter-python: {e}")

# Test 3: Check installed packages
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
tree_packages = [line for line in result.stdout.split('\n') if 'tree' in line.lower()]
print("\nTree-sitter related packages:")
for pkg in tree_packages:
    print(f"  {pkg}")

# Test 4: Try to create a parser with the language
try:
    from tree_sitter_python import language as python_language
    py_lang = python_language()
    parser = Parser()
    parser.set_language(py_lang)
    print("\nParser created successfully with tree-sitter-python language")
except Exception as e:
    print(f"\nError creating parser: {e}")
