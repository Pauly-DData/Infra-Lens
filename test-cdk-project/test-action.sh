#!/bin/bash

cd "$(dirname "$0")"

# Test script for CDK Diff Summarizer Action
# This script tests the action with different scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_test_result() {
    echo -e "${CYAN}Test Result: $1${NC}"
}

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY not set. Some tests will fail."
    print_warning "Set it with: export OPENAI_API_KEY='your-api-key'"
else
    print_status "OPENAI_API_KEY found and will be used for testing"
fi

# Function to test a scenario
test_scenario() {
    local scenario_name=$1
    local diff_file=$2
    local expected_result=$3
    local test_description=$4
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    OUTPUT_FILE="output_${scenario_name// /_}.txt"
    ERROR_FILE="error_${scenario_name// /_}.txt"
    
    print_header "🧪 Testing: $scenario_name"
    print_status "Description: $test_description"
    print_status "Using diff file: $diff_file"
    print_status "Expected result: $expected_result"
    
    # Set environment variables for testing
    export CDK_DIFF_FILE="$diff_file"
    export OUTPUT_FORMAT="markdown"
    export LANGUAGE="en"
    export CACHE_ENABLED="false"
    
    # Run the action (without command line arguments)
    if OPENAI_API_KEY="$OPENAI_API_KEY" python3 ../src/main.py > "$OUTPUT_FILE" 2> "$ERROR_FILE"; then
        if [ "$expected_result" = "success" ]; then
            print_success "Scenario '$scenario_name' completed successfully"
            print_test_result "✅ PASSED"
        else
            print_error "Scenario '$scenario_name' succeeded but was expected to fail"
            print_test_result "❌ FAILED (unexpected success)"
        fi
    else
        if [ "$expected_result" = "fail" ]; then
            print_success "Scenario '$scenario_name' failed as expected"
            print_test_result "✅ PASSED (expected failure)"
        else
            print_error "Scenario '$scenario_name' failed unexpectedly"
            print_test_result "❌ FAILED (unexpected failure)"
            return 1
        fi
    fi
    
    # Check if summary was generated
    if [ -s "$OUTPUT_FILE" ] && grep -q "GENERATED SUMMARY:" "$OUTPUT_FILE"; then
        print_status "✅ Summary generated successfully"
    else
        print_warning "⚠️  No summary found in output"
    fi
    
    echo ""
}

# Function to run integration tests
run_integration_tests() {
    print_header "🔗 Running Integration Tests"
    
    # Test different output formats
    print_status "Testing output formats..."
    for format in markdown json html; do
        export OUTPUT_FORMAT="$format"
        export CDK_DIFF_FILE="test-diffs/simple-changes.json"
        if python3 ../src/main.py > "output_format_${format}.txt" 2>/dev/null; then
            print_success "Output format '$format' works"
        else
            print_error "Output format '$format' failed"
        fi
    done
    
    # Test different languages
    print_status "Testing languages..."
    for lang in en nl; do
        export LANGUAGE="$lang"
        export CDK_DIFF_FILE="test-diffs/simple-changes.json"
        if python3 ../src/main.py > "output_lang_${lang}.txt" 2>/dev/null; then
            print_success "Language '$lang' works"
        else
            print_error "Language '$lang' failed"
        fi
    done
}

# Function to run performance tests
run_performance_tests() {
    print_header "⚡ Running Performance Tests"
    
    # Test with large diff file
    print_status "Testing with complex changes..."
    export CDK_DIFF_FILE="test-diffs/complex-changes.json"
    start_time=$(date +%s)
    if python3 ../src/main.py > "output_performance.txt" 2>/dev/null; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        print_success "Complex changes processed in ${duration}s"
    else
        print_error "Performance test failed"
    fi
}

# Main test execution
echo ""
print_header "🧪 Starting CDK Diff Summarizer Action Tests"
echo "=============================================="
echo ""

# Basic functionality tests
print_header "📋 Basic Functionality Tests"

# Test 1: No changes
test_scenario "No Changes" "test-diffs/no-changes.json" "success" "Should handle empty diff gracefully"

# Test 2: Simple changes
test_scenario "Simple Changes" "test-diffs/simple-changes.json" "success" "Should process simple resource changes"

# Test 3: Security changes
test_scenario "Security Changes" "test-diffs/security-changes.json" "success" "Should handle security-related changes"

# Test 4: Complex changes
test_scenario "Complex Changes" "test-diffs/complex-changes.json" "success" "Should process complex multi-stack changes"

# Test 5: Destructive changes
test_scenario "Destructive Changes" "test-diffs/destructive-changes.json" "success" "Should handle destructive operations"

# Error handling tests
print_header "🚨 Error Handling Tests"

# Test 6: Invalid JSON (should fail gracefully)
test_scenario "Invalid JSON" "test-diffs/invalid.json" "fail" "Should handle malformed JSON gracefully"

# Test 7: Non-existent file (should fail gracefully)
test_scenario "Non-existent File" "test-diffs/does-not-exist.json" "fail" "Should handle missing files gracefully"

# Integration tests
run_integration_tests

# Performance tests
run_performance_tests

# Test summary
echo ""
print_header "📊 Test Summary"
echo "=============================================="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo "Success Rate: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    print_header "🎉 All tests completed successfully!"
else
    echo ""
    print_header "⚠️  Some tests failed. Check the output above for details."
fi

echo ""
echo "Next steps:"
echo "1. Review the generated summaries"
echo "2. Test with different output formats (JSON, HTML)"
echo "3. Test with different languages (nl)"
echo "4. Test caching functionality"
echo "5. Test with real CDK projects"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi 