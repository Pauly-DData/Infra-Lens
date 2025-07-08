"""
AI service for CDK Diff Summarizer.
Handles OpenAI API calls, caching, and error handling.
"""

import os
import json
import time
import random
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
import openai
from config import Config, AIConfig


class AIService:
    """Handles AI API calls and caching."""
    
    def __init__(self, config: Config):
        self.config = config
        self.ai_config = config.ai
        self.cache_config = config.cache
        self.client = self._setup_client()
        self.cache = self._setup_cache()
    
    def _setup_client(self) -> openai.OpenAI:
        """Setup OpenAI client with configuration."""
        kwargs = {
            'api_key': self.ai_config.api_key,
            'timeout': self.ai_config.timeout
        }
        
        if self.ai_config.base_url:
            kwargs['base_url'] = self.ai_config.base_url
        
        return openai.OpenAI(**kwargs)
    
    def _setup_cache(self) -> Optional['CacheManager']:
        """Setup cache manager if caching is enabled."""
        if not self.cache_config.enabled:
            return None
        
        try:
            from .cache import CacheManager
            return CacheManager(self.cache_config)
        except ImportError:
            print("Warning: Caching disabled - cache module not available")
            return None
    
    def generate_summary(self, diff_data: Dict[str, Any], template_summary: str = None) -> str:
        """Generate AI summary from CDK diff data."""
        # Create cache key
        cache_key = self._create_cache_key(diff_data)
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                print("::notice::Using cached AI summary")
                return cached_result
        
        # Generate prompt
        prompt = self._generate_prompt(diff_data, template_summary)
        
        # Get AI response with retry logic
        summary = self._get_ai_response_with_retry(prompt)
        
        # Cache the result
        if self.cache and summary:
            self.cache.set(cache_key, summary)
        
        return summary
    
    def _create_cache_key(self, diff_data: Dict[str, Any]) -> str:
        """Create cache key from diff data."""
        # Create a hash of the diff data
        diff_str = json.dumps(diff_data, sort_keys=True)
        config_str = json.dumps(self.config.to_dict(), sort_keys=True)
        
        combined = f"{diff_str}:{config_str}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _generate_prompt(self, diff_data: Dict[str, Any], template_summary: str = None) -> str:
        """Generate prompt for AI based on diff data and optional template."""
        changes = self._extract_changes_for_prompt(diff_data)
        
        if not changes:
            return self._get_no_changes_prompt()
        
        # Base prompt
        prompt = f"""You are an expert AWS infrastructure architect. Analyze the following CDK diff and create a professional summary.

**CDK Changes Detected:**
{chr(10).join(changes)}

**Please provide a structured summary with:**

1. **Executive Summary** (2-3 sentences)
   - High-level overview of changes
   - Business impact

2. **Resource Changes Table**
   | Action | Resource Type | Resource Name | Stack |
   |--------|---------------|---------------|-------|
   [Fill this table with the changes]

3. **Security & Permissions**
   - IAM role changes
   - Policy modifications
   - Security implications

4. **Cost Impact**
   - New resources (estimated costs)
   - Removed resources (cost savings)
   - Updated resources (cost changes)

5. **Risk Assessment**
   - Potential risks
   - Mitigation strategies

6. **Deployment Notes**
   - Dependencies
   - Order of deployment
   - Rollback considerations

**Format the response in clean markdown with proper tables and sections.**
**Keep it professional and business-focused.**
**Use emojis sparingly and only where appropriate.**"""
        
        # Add template summary if provided
        if template_summary:
            prompt += f"""

**Template Summary (for reference):**
{template_summary}

**Please enhance the template summary with additional insights and analysis.**"""
        
        return prompt
    
    def _extract_changes_for_prompt(self, diff_data: Dict[str, Any]) -> List[str]:
        """Extract changes from diff data for prompt generation."""
        changes = []
        
        stacks_data = diff_data.get('stacks', {})
        
        for stack_name, stack_data in stacks_data.items():
            if stack_data.get('create'):
                changes.append(f"Stack '{stack_name}' will be created")
            if stack_data.get('update'):
                changes.append(f"Stack '{stack_name}' will be updated")
            if stack_data.get('destroy'):
                changes.append(f"Stack '{stack_name}' will be destroyed")
            
            # Process resource changes
            resources_data = stack_data.get('resources', {})
            for resource_id, resource_data in resources_data.items():
                resource_type = resource_data.get('type', 'Unknown')
                if resource_data.get('create'):
                    changes.append(f"Resource '{resource_id}' ({resource_type}) will be created in stack '{stack_name}'")
                if resource_data.get('update'):
                    changes.append(f"Resource '{resource_id}' ({resource_type}) will be updated in stack '{stack_name}'")
                if resource_data.get('destroy'):
                    changes.append(f"Resource '{resource_id}' ({resource_type}) will be destroyed in stack '{stack_name}'")
                if resource_data.get('replace'):
                    changes.append(f"Resource '{resource_id}' ({resource_type}) will be replaced in stack '{stack_name}'")
        
        return changes
    
    def _get_no_changes_prompt(self) -> str:
        """Get prompt for when no changes are detected."""
        return """No infrastructure changes were detected in the CDK diff. 

This could be because:
1. The CDK diff command failed to execute properly
2. There are no changes to deploy
3. The infrastructure is already up to date

Please provide a brief summary explaining this situation and suggest next steps for the user."""
    
    def _get_ai_response_with_retry(self, prompt: str) -> str:
        """Get AI response with exponential backoff retry logic."""
        for attempt in range(self.ai_config.max_retries):
            try:
                print(f"::notice::Attempting OpenAI API call (attempt {attempt + 1}/{self.ai_config.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.ai_config.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert AWS infrastructure architect who can explain complex infrastructure changes in simple terms."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=self.ai_config.temperature,
                    max_tokens=self.ai_config.max_tokens
                )
                
                return response.choices[0].message.content
                
            except openai.RateLimitError as e:
                if attempt < self.ai_config.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"::warning::Rate limit hit. Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"::error::Rate limit exceeded after {self.ai_config.max_retries} attempts")
                    return "Rate limit exceeded. Please try again later."
                    
            except openai.APIError as e:
                error_message = str(e)
                if "insufficient_quota" in error_message or "quota" in error_message.lower():
                    print(f"::error::OpenAI quota exceeded: {error_message}")
                    return "OpenAI API quota exceeded. Please check your billing and usage limits."
                
                if attempt < self.ai_config.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"::warning::API error: {error_message}. Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"::error::API error after {self.ai_config.max_retries} attempts: {error_message}")
                    return f"API error: {error_message}"
                    
            except Exception as e:
                print(f"::error::Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.ai_config.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"::warning::Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    return f"Failed to generate AI summary after {self.ai_config.max_retries} attempts: {str(e)}"
        
        return "Failed to generate AI summary after all retry attempts."
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is working."""
        try:
            # Make a simple test call
            response = self.client.chat.completions.create(
                model=self.ai_config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"::error::API key validation failed: {str(e)}")
            return False


class CacheManager:
    """Simple file-based cache manager."""
    
    def __init__(self, cache_config):
        self.cache_dir = Path(cache_config.cache_dir)
        self.ttl_seconds = cache_config.ttl_hours * 3600
        self.max_size_bytes = cache_config.max_cache_size_mb * 1024 * 1024
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(exist_ok=True)
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check TTL
            if time.time() - data['timestamp'] > self.ttl_seconds:
                cache_file.unlink()
                return None
            
            return data['value']
            
        except Exception as e:
            print(f"Warning: Failed to read cache for key {key}: {e}")
            return None
    
    def set(self, key: str, value: str):
        """Set value in cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            data = {
                'value': value,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            # Clean up old cache files if needed
            self._cleanup_cache()
            
        except Exception as e:
            print(f"Warning: Failed to write cache for key {key}: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache files and enforce size limits."""
        try:
            # Get all cache files with their timestamps
            cache_files = []
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    cache_files.append((cache_file, data['timestamp']))
                except:
                    # Remove corrupted cache files
                    cache_file.unlink()
            
            # Remove expired files
            current_time = time.time()
            for cache_file, timestamp in cache_files:
                if current_time - timestamp > self.ttl_seconds:
                    cache_file.unlink()
                    cache_files = [(f, t) for f, t in cache_files if f != cache_file]
            
            # Check total size and remove oldest files if needed
            total_size = sum(f.stat().st_size for f, _ in cache_files)
            if total_size > self.max_size_bytes:
                # Sort by timestamp (oldest first)
                cache_files.sort(key=lambda x: x[1])
                
                # Remove oldest files until under size limit
                for cache_file, _ in cache_files:
                    cache_file.unlink()
                    total_size -= cache_file.stat().st_size
                    if total_size <= self.max_size_bytes:
                        break
                        
        except Exception as e:
            print(f"Warning: Cache cleanup failed: {e}") 