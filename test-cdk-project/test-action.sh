#!/bin/bash

# Test script for CDK Diff Summarizer Action
# This script tests the action with different scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY not set. Some tests will fail."
    print_warning "Set it with: export OPENAI_API_KEY='your-api-key'"
fi

# Function to test a scenario
test_scenario() {
    local scenario_name=$1
    local diff_file=$2
    local expected_result=$3
    
    print_status "Testing scenario: $scenario_name"
    print_status "Using diff file: $diff_file"
    
    # Set environment variables for testing
    export CDK_DIFF_FILE="$diff_file"
    export OUTPUT_FORMAT="markdown"
    export LANGUAGE="en"
    export CACHE_ENABLED="false"
    
    # Run the action
    if python3 ../src/main.py; then
        print_success "Scenario '$scenario_name' completed successfully"
    else
        if [ "$expected_result" = "fail" ]; then
            print_success "Scenario '$scenario_name' failed as expected"
        else
            print_error "Scenario '$scenario_name' failed unexpectedly"
            return 1
        fi
    fi
    
    echo ""
}

# Main test execution
echo "🧪 Starting CDK Diff Summarizer Action Tests"
echo "=============================================="
echo ""

# Test 1: No changes
test_scenario "No Changes" "test-diffs/no-changes.json" "success"

# Test 2: Simple changes
test_scenario "Simple Changes" "test-diffs/simple-changes.json" "success"

# Test 3: Security changes
test_scenario "Security Changes" "test-diffs/security-changes.json" "success"

# Test 4: Complex changes
test_scenario "Complex Changes" "test-diffs/complex-changes.json" "success"

# Test 5: Destructive changes
test_scenario "Destructive Changes" "test-diffs/destructive-changes.json" "success"

# Test 6: Invalid JSON (should fail gracefully)
test_scenario "Invalid JSON" "test-diffs/invalid.json" "fail"

# Test 7: Non-existent file (should fail gracefully)
test_scenario "Non-existent File" "test-diffs/does-not-exist.json" "fail"

echo ""
echo "🎉 All tests completed!"
echo ""
echo "Test Summary:"
echo "- 6 scenarios tested"
echo "- Check output above for results"
echo ""
echo "Next steps:"
echo "1. Review the generated summaries"
echo "2. Test with different output formats (JSON, HTML)"
echo "3. Test with different languages (nl)"
echo "4. Test caching functionality" 