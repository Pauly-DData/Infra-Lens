#!/usr/bin/env python3
"""
Local test script for CDK Diff Summarizer
Run this to test the functionality locally without GitHub Actions
"""

import os
import json
import sys
from summarize_cdk_diff import read_cdk_diff, generate_prompt, get_ai_summary_with_retry

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
    if not api_key:
        print("⚠️  Skipping AI test - no OPENAI_API_KEY found")
        print("   Set OPENAI_API_KEY environment variable to test AI functionality")
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

def main():
    """Run all tests."""
    print("🚀 Starting CDK Diff Summarizer local tests...\n")
    
    try:
        test_diff_reading()
        print()
        
        test_prompt_generation()
        print()
        
        test_error_handling()
        print()
        
        test_ai_summary()
        print()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 