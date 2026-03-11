#!/bin/bash
# Test script for the cartographer MCP system

echo "Testing Cartographer MCP System"
echo "==============================="
echo ""

# Test 1: Run cartographer agent
echo "Test 1: Running cartographer agent..."
/opt/homebrew/bin/python3.10 agents/cartographer_agent.py /Users/juani/github-projects/documentationmcp/documentationmcp 2>&1 | head -20
echo ""

# Test 2: Test cartographer query tool
echo "Test 2: Testing cartographer query tool..."
echo "Stats:"
/opt/homebrew/bin/python3.10 cartographer_query.py /Users/juani/github-projects/documentationmcp/documentationmcp stats 2>&1
echo ""

echo "List modules:"
/opt/homebrew/bin/python3.10 cartographer_query.py /Users/juani/github-projects/documentationmcp/documentationmcp list-modules 2>&1 | head -15
echo ""

echo "✅ Basic tests completed!"
