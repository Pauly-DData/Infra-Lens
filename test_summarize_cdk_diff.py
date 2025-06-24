#!/usr/bin/env python3
"""
Unit tests for CDK Diff Summarizer
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from summarize_cdk_diff import (
    read_cdk_diff,
    generate_prompt,
    get_ai_summary_with_retry,
    post_to_github,
    set_output
)

class TestCDKDiffSummarizer(unittest.TestCase):
    
    def setUp(self):
        self.sample_diff = {
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
                        }
                    }
                }
            }
        }
    
    def test_read_cdk_diff_valid_file(self):
        """Test reading a valid CDK diff JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_diff, f)
            temp_file = f.name
        
        try:
            result = read_cdk_diff(temp_file)
            self.assertEqual(result, self.sample_diff)
        finally:
            os.unlink(temp_file)
    
    def test_read_cdk_diff_missing_file(self):
        """Test reading a non-existent file."""
        result = read_cdk_diff("non_existent_file.json")
        self.assertEqual(result, {"stacks": {}})
    
    def test_read_cdk_diff_empty_file(self):
        """Test reading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            result = read_cdk_diff(temp_file)
            self.assertEqual(result, {"stacks": {}})
        finally:
            os.unlink(temp_file)
    
    def test_read_cdk_diff_invalid_json(self):
        """Test reading a file with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            result = read_cdk_diff(temp_file)
            self.assertEqual(result, {"stacks": {}})
        finally:
            os.unlink(temp_file)
    
    def test_generate_prompt_with_changes(self):
        """Test prompt generation with actual changes."""
        prompt = generate_prompt(self.sample_diff)
        
        self.assertIn("TestStack", prompt)
        self.assertIn("MyS3Bucket", prompt)
        self.assertIn("MyLambdaFunction", prompt)
        self.assertIn("AWS::S3::Bucket", prompt)
        self.assertIn("AWS::Lambda::Function", prompt)
        self.assertIn("will be created", prompt)
    
    def test_generate_prompt_no_changes(self):
        """Test prompt generation with no changes."""
        empty_diff = {"stacks": {}}
        prompt = generate_prompt(empty_diff)
        
        self.assertIn("No infrastructure changes", prompt)
        self.assertIn("CDK diff command failed", prompt)
    
    def test_generate_prompt_mixed_changes(self):
        """Test prompt generation with mixed change types."""
        mixed_diff = {
            "stacks": {
                "Stack1": {
                    "create": True,
                    "resources": {
                        "NewResource": {"create": True, "type": "AWS::S3::Bucket"}
                    }
                },
                "Stack2": {
                    "update": True,
                    "resources": {
                        "UpdatedResource": {"update": True, "type": "AWS::Lambda::Function"}
                    }
                },
                "Stack3": {
                    "destroy": True,
                    "resources": {
                        "OldResource": {"destroy": True, "type": "AWS::EC2::Instance"}
                    }
                }
            }
        }
        
        prompt = generate_prompt(mixed_diff)
        
        self.assertIn("Stack1", prompt)
        self.assertIn("Stack2", prompt)
        self.assertIn("Stack3", prompt)
        self.assertIn("will be created", prompt)
        self.assertIn("will be updated", prompt)
        self.assertIn("will be destroyed", prompt)
    
    @patch('summarize_cdk_diff.openai.OpenAI')
    def test_get_ai_summary_success(self, mock_openai):
        """Test successful AI summary generation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test summary"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = get_ai_summary_with_retry("test prompt")
        
        self.assertEqual(result, "Test summary")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('summarize_cdk_diff.openai.OpenAI')
    def test_get_ai_summary_no_api_key(self, mock_openai):
        """Test AI summary generation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_ai_summary_with_retry("test prompt")
        
        self.assertEqual(result, "OpenAI API key not found in environment variables.")
        mock_openai.assert_not_called()
    
    @patch('summarize_cdk_diff.openai.OpenAI')
    def test_get_ai_summary_rate_limit(self, mock_openai):
        """Test AI summary generation with rate limiting."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit")
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = get_ai_summary_with_retry("test prompt", max_retries=1)
        
        self.assertIn("Failed to generate AI summary", result)
    
    @patch('summarize_cdk_diff.Github')
    def test_post_to_github_issue_only(self, mock_github):
        """Test posting to GitHub as issue only."""
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_repo.create_issue.return_value = mock_issue
        mock_github.return_value.get_repo.return_value = mock_repo
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'test-token'}):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"repository": {"full_name": "test/repo"}}, f)
                temp_file = f.name
            
            try:
                with patch.dict(os.environ, {'GITHUB_EVENT_PATH': temp_file}):
                    result = post_to_github("test summary", "issue")
                
                self.assertEqual(result, 123)
                mock_repo.create_issue.assert_called_once()
            finally:
                os.unlink(temp_file)
    
    def test_post_to_github_no_token(self):
        """Test posting to GitHub without token."""
        with patch.dict(os.environ, {}, clear=True):
            result = post_to_github("test summary")
        
        self.assertIsNone(result)
    
    def test_set_output(self):
        """Test setting GitHub Action output."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            with patch.dict(os.environ, {'GITHUB_OUTPUT': temp_file}):
                set_output('test_key', 'test_value')
            
            with open(temp_file, 'r') as f:
                content = f.read()
            
            self.assertIn('test_key=test_value', content)
        finally:
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main() 