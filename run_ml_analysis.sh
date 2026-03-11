#!/bin/bash
# ML Pattern Recognition - Execution Guide & Testing Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}ML PATTERN RECOGNITION SUITE${NC}"
echo -e "${BLUE}Execution & Testing Guide${NC}"
echo -e "${BLUE}================================${NC}"

# Check Python version
echo -e "\n${YELLOW}Checking Python environment...${NC}"
PYTHON_BIN="/opt/homebrew/bin/python3.10"

if [ ! -x "$PYTHON_BIN" ]; then
    echo -e "${RED}❌ Python 3.10 not found. Installing...${NC}"
    brew install python@3.10
fi

echo -e "${GREEN}✅ Using Python 3.10: $PYTHON_BIN${NC}"

# Check dependencies
echo -e "\n${YELLOW}Checking ML dependencies...${NC}"
$PYTHON_BIN -c "import sklearn; print('✅ scikit-learn')" 2>/dev/null || {
    echo -e "${RED}Installing ML packages...${NC}"
    $PYTHON_BIN -m pip install scikit-learn numpy scipy --quiet
}
echo -e "${GREEN}✅ All dependencies available${NC}"

# Display options
echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}Available Options:${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}1.${NC} Run Quick Start Demo"
echo "   - Shows all 4 ML capabilities"
echo "   - Demonstrates pattern learning, anomaly detection, categorization, and documentation prediction"
echo ""
echo -e "${GREEN}2.${NC} Run Comprehensive Tests"
echo "   - 20 tests covering all components"
echo "   - Validates all functionality"
echo ""
echo -e "${GREEN}3.${NC} Analyze a Codebase"
echo "   - Run full analysis on a Python project"
echo "   - Generates JSON results and recommendations"
echo ""
echo -e "${GREEN}4.${NC} Run Interactive Demo"
echo "   - Step-by-step demonstration"
echo "   - Shows output for each capability"
echo ""

# Function to run quick demo
run_quick_demo() {
    echo -e "\n${BLUE}Running Quick Start Demo...${NC}\n"
    cd /Users/juani/github-projects/documentationmcp/documentationmcp
    $PYTHON_BIN agents/ml_quick_start.py
}

# Function to run tests
run_tests() {
    echo -e "\n${BLUE}Running Comprehensive Test Suite...${NC}\n"
    cd /Users/juani/github-projects/documentationmcp/documentationmcp
    $PYTHON_BIN test_ml_pattern_recognition.py
}

# Function to analyze codebase
analyze_codebase() {
    echo -e "\n${BLUE}Codebase Analysis${NC}"
    read -p "Enter path to codebase: " CODEBASE_PATH
    read -p "Enter output directory (default: ./ml_results): " OUTPUT_DIR
    OUTPUT_DIR=${OUTPUT_DIR:-./ml_results}
    
    if [ ! -d "$CODEBASE_PATH" ]; then
        echo -e "${RED}❌ Directory not found: $CODEBASE_PATH${NC}"
        return 1
    fi
    
    echo -e "\n${BLUE}Analyzing $CODEBASE_PATH...${NC}\n"
    cd /Users/juani/github-projects/documentationmcp/documentationmcp
    $PYTHON_BIN agents/ml_integrated_agent.py "$CODEBASE_PATH" -o "$OUTPUT_DIR"
    
    echo -e "\n${GREEN}✅ Analysis complete!${NC}"
    echo "Results saved to:"
    echo "  • $OUTPUT_DIR/ml_analysis_results.json"
    echo "  • $OUTPUT_DIR/ml_recommendations.json"
    echo "  • $OUTPUT_DIR/ml_model.json"
}

# Function for interactive demo
interactive_demo() {
    echo -e "\n${BLUE}Interactive ML Pattern Recognition Demo${NC}\n"
    
    cat << 'EOF'
This demo will show you all 4 ML capabilities:

1️⃣  PATTERN LEARNER
   Learns from code patterns and extracts features:
   - Complexity metrics (cyclomatic complexity, nesting)
   - Code quality indicators (error handling, validation, logging)
   - Business relevance (keywords, external calls)
   
2️⃣  ANOMALY DETECTOR  
   Finds unusual code patterns that might be bugs:
   - Uses Isolation Forest algorithm
   - Rates severity (critical, high, medium, low)
   - Explains why code is flagged
   
3️⃣  IMPORTANCE CATEGORIZER
   Ranks code by business value:
   - Critical Path (payment, auth, core business)
   - Hot Path (performance sensitive)
   - Business Logic (rules, validation)
   - Integration (external APIs)
   - Utility (helpers)
   - Infrastructure (logging, config)
   
4️⃣  DOCUMENTATION PREDICTOR
   Suggests what needs documentation:
   - Finds similar documented patterns
   - Recommends documentation style
   - Calculates confidence scores

EOF
    
    read -p "Press Enter to start the demo..." -t 3 || true
    
    run_quick_demo
}

# Function to show usage examples
show_examples() {
    cat << 'EOF'

📚 USAGE EXAMPLES
==================

1. Quick API Usage:
   
   from agents.ml_pattern_recognition import MLPatternRecognitionEngine
   
   engine = MLPatternRecognitionEngine()
   engine.learner.add_pattern(code, 'business_logic', 'file.py', 10, {})
   results = engine.analyze_patterns({})
   engine.print_report()

2. Integrated Analysis:
   
   from agents.ml_integrated_agent import run_integrated_analysis
   
   results = run_integrated_analysis(
       '/path/to/project',
       output_dir='./ml_results',
       file_ext='.py',
       max_workers=8
   )

3. Component-level Usage:
   
   from agents.ml_pattern_recognition import (
       PatternLearner,
       AnomalyDetector,
       ImportanceCategorizer,
       DocumentationPredictor
   )
   
   learner = PatternLearner()
   detector = AnomalyDetector()
   categorizer = ImportanceCategorizer()
   predictor = DocumentationPredictor()

EOF
}

# Main menu
show_menu() {
    echo ""
    read -p "Select an option (1-4): " choice
    
    case $choice in
        1) run_quick_demo ;;
        2) run_tests ;;
        3) analyze_codebase ;;
        4) interactive_demo ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
}

# Run main menu
show_menu

# Show examples
show_examples

echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}Documentation:${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "📖 ML_PATTERN_RECOGNITION.md"
echo "   Complete user guide with API documentation"
echo ""
echo "📖 ML_IMPLEMENTATION_SUMMARY.md"
echo "   Implementation details and architecture"
echo ""
echo "📖 agents/ml_pattern_recognition.py"
echo "   Source code with inline documentation"
echo ""

echo -e "${GREEN}✅ ML Pattern Recognition Suite is ready!${NC}\n"
