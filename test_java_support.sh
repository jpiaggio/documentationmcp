#!/bin/bash
# Comprehensive test for Cartographer with Python and Java support

echo "=========================================="
echo "Testing Cartographer MCP with Java Support"
echo "=========================================="
echo ""

# Create a test Java file temporarily
cat > TestSample.java << 'EOF'
import java.util.List;
import java.util.ArrayList;

public class TestSample {
    private List<String> items;
    
    public TestSample() {
        this.items = new ArrayList<>();
    }
    
    public void addItem(String item) {
        items.add(item);
    }
    
    public List<String> getAll() {
        return items;
    }
}
EOF

cat > test_sample.py << 'EOF'
def hello_world():
    """Test Python function"""
    return "Hello, World!"

class Calculator:
    """Test Python class"""
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
EOF

echo "Test 1: Scan Python files with test sample"
echo "=========================================="
.venv/bin/python -c "
from agents.cartographer_agent import cartographer_agent

# Test Python files
py_results = [s for s in cartographer_agent('.', file_ext='.py', max_workers=1) if 'test_sample' in s]
print(f'Python test_sample.py statements: {len(py_results)}')
if py_results:
    print('Sample:', py_results[0][:80])
" 2>&1 | grep -v "Initializing\|Python language\|Using tree"

echo ""
echo "Test 2: Scan Java files with test sample"
echo "========================================"
.venv/bin/python -c "
from agents.cartographer_agent import cartographer_agent

# Test Java files
java_results = cartographer_agent('.', file_ext='.java', max_workers=1)
test_java = [s for s in java_results if 'TestSample' in s]
print(f'Java TestSample.java statements: {len(test_java)}')
for stmt in test_java[:3]:
    print(stmt)
" 2>&1 | grep -v "Initializing\|Python language\|Using tree"

echo ""
echo "Test 3: Verify Method detection in Java"
echo "========================================"
.venv/bin/python -c "
from agents.cartographer_agent import cartographer_agent

# Test Java files and look for Method nodes
java_results = cartographer_agent('.', file_ext='.java', max_workers=1)
methods = [s for s in java_results if ':Method' in s and 'TestSample' in s]
classes = [s for s in java_results if ':Class' in s and 'TestSample' in s]
print(f'Java Classes found: {len(classes)}')
print(f'Java Methods found: {len(methods)}')
if methods:
    print('Methods detected:')
    for m in methods:
        print('  -', m[20:80])
" 2>&1 | grep -v "Initializing\|Python language\|Using tree"

echo ""
echo "✅ Java support test completed!"
echo ""

# Cleanup
rm -f TestSample.java test_sample.py

