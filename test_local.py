#!/usr/bin/env python3
"""
Local test script for CDK Diff Summarizer
Run this to test the functionality locally without GitHub Actions
"""

import os
import json
import sys
from summarize_cdk_diff import read_cdk_diff, generate_prompt, get_ai_summary_with_retry

# Hardcoded credentials for local testing
# WARNING: Only use for local testing, never commit real credentials to git!
TEST_CREDENTIALS = {
    'OPENAI_API_KEY': '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',  # Replace with your actual key
    'GITHUB_TOKEN': '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',     # Replace with your actual token
}

def setup_test_environment():
    """Set up test environment with credentials."""
    print("🔧 Setting up test environment...")
    
    # Set environment variables for testing
    for key, value in TEST_CREDENTIALS.items():
        if value.startswith('sk-your-') or value.startswith('ghp-your-'):
            print(f"⚠️  Please replace the placeholder {key} with your actual credentials")
            print(f"   Current value: {value[:10]}...")
            return False
        os.environ[key] = value
    
    print("✅ Test environment set up successfully")
    return True

def create_test_diff():
    """Create a test CDK diff for local testing."""
    return {
        "stacks": {
            "TestStack": {
                "create": True,
                "resources": {
                    "MyS3Bucket": {
                        "create": True,
                        "type": "AWS::S3::Bucket"
                    },
                    "MyLambdaFunction": {
                        "create": True,
                        "type": "AWS::Lambda::Function"
                    },
                    "MyLambdaRole": {
                        "create": True,
                        "type": "AWS::IAM::Role"
                    },
                    "MyDynamoDBTable": {
                        "create": True,
                        "type": "AWS::DynamoDB::Table"
                    }
                }
            },
            "ExistingStack": {
                "update": True,
                "resources": {
                    "ExistingEC2Instance": {
                        "update": True,
                        "type": "AWS::EC2::Instance"
                    },
                    "OldResource": {
                        "destroy": True,
                        "type": "AWS::S3::Bucket"
                    }
                }
            }
        }
    }

def test_diff_reading():
    """Test reading CDK diff from file."""
    print("🧪 Testing CDK diff reading...")
    
    # Create test file
    test_diff = create_test_diff()
    with open('test-diff.json', 'w') as f:
        json.dump(test_diff, f, indent=2)
    
    # Test reading
    result = read_cdk_diff('test-diff.json')
    assert result == test_diff, "Diff reading failed"
    print("✅ CDK diff reading test passed")
    
    # Cleanup
    os.remove('test-diff.json')

def test_prompt_generation():
    """Test prompt generation."""
    print("🧪 Testing prompt generation...")
    
    test_diff = create_test_diff()
    prompt = generate_prompt(test_diff)
    
    # Check that prompt contains expected elements
    assert "TestStack" in prompt, "Prompt missing TestStack"
    assert "MyS3Bucket" in prompt, "Prompt missing MyS3Bucket"
    assert "AWS::S3::Bucket" in prompt, "Prompt missing resource type"
    assert "will be created" in prompt, "Prompt missing create action"
    assert "will be updated" in prompt, "Prompt missing update action"
    assert "will be destroyed" in prompt, "Prompt missing destroy action"
    
    print("✅ Prompt generation test passed")
    print(f"📝 Generated prompt preview: {prompt[:200]}...")

def test_ai_summary():
    """Test AI summary generation (requires API key)."""
    print("🧪 Testing AI summary generation...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key.startswith('sk-your-'):
        print("⚠️  Skipping AI test - no valid OPENAI_API_KEY found")
        print("   Please update TEST_CREDENTIALS in this file with your actual API key")
        return
    
    test_diff = create_test_diff()
    prompt = generate_prompt(test_diff)
    
    print("🤖 Calling OpenAI API...")
    summary = get_ai_summary_with_retry(prompt, max_tokens=200)
    
    if "Failed" in summary or "Error" in summary:
        print(f"❌ AI summary failed: {summary}")
        return
    
    print("✅ AI summary test passed")
    print(f"📝 Generated summary: {summary}")

def test_error_handling():
    """Test error handling scenarios."""
    print("🧪 Testing error handling...")
    
    # Test missing file
    result = read_cdk_diff('non-existent-file.json')
    assert result == {"stacks": {}}, "Missing file handling failed"
    
    # Test empty file
    with open('empty-diff.json', 'w') as f:
        f.write('')
    
    result = read_cdk_diff('empty-diff.json')
    assert result == {"stacks": {}}, "Empty file handling failed"
    
    # Test invalid JSON
    with open('invalid-diff.json', 'w') as f:
        f.write('invalid json content')
    
    result = read_cdk_diff('invalid-diff.json')
    assert result == {"stacks": {}}, "Invalid JSON handling failed"
    
    # Cleanup
    os.remove('empty-diff.json')
    os.remove('invalid-diff.json')
    
    print("✅ Error handling test passed")

def test_full_workflow():
    """Test the complete workflow from diff to summary."""
    print("🧪 Testing complete workflow...")
    
    # Create test diff
    test_diff = create_test_diff()
    with open('workflow-test-diff.json', 'w') as f:
        json.dump(test_diff, f, indent=2)
    
    try:
        # Read diff
        diff_data = read_cdk_diff('workflow-test-diff.json')
        print("✅ Diff reading: OK")
        
        # Generate prompt
        prompt = generate_prompt(diff_data)
        print("✅ Prompt generation: OK")
        print(f"   Prompt length: {len(prompt)} characters")
        
        # Generate AI summary (if API key available)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and not api_key.startswith('sk-your-'):
            summary = get_ai_summary_with_retry(prompt, max_tokens=300)
            if "Failed" not in summary and "Error" not in summary:
                print("✅ AI summary generation: OK")
                print(f"   Summary length: {len(summary)} characters")
                print(f"   Summary preview: {summary[:100]}...")
            else:
                print("⚠️  AI summary generation: Failed")
        else:
            print("⚠️  AI summary generation: Skipped (no API key)")
        
        print("✅ Complete workflow test passed")
        
    finally:
        # Cleanup
        if os.path.exists('workflow-test-diff.json'):
            os.remove('workflow-test-diff.json')

def main():
    """Run all tests."""
    print("🚀 Starting CDK Diff Summarizer local tests...\n")
    
    # Check if credentials are set up
    if not setup_test_environment():
        print("\n📝 To run tests with real API calls, update TEST_CREDENTIALS in this file:")
        print("   1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
        print("   2. Get your GitHub token from: https://github.com/settings/tokens")
        print("   3. Replace the placeholder values in TEST_CREDENTIALS")
        print("   4. Run this script again\n")
    
    try:
        test_diff_reading()
        print()
        
        test_prompt_generation()
        print()
        
        test_error_handling()
        print()
        
        test_ai_summary()
        print()
        
        test_full_workflow()
        print()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 