"""
Main summarizer module for CDK Diff Summarizer.
Orchestrates all components to generate summaries.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

from config import Config
from templates import TemplateManager
from ai_service import AIService
from github_service import GitHubService, OutputFormatter
from cache import DiffCache


class CDKDiffSummarizer:
    """Main class for CDK Diff Summarizer."""
    
    def __init__(self, config: Config):
        self.config = config
        self.template_manager = TemplateManager(config)
        self.ai_service = AIService(config)
        self.github_service = GitHubService(config)
        self.cache = DiffCache(config.cache) if config.cache.enabled else None
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration."""
        if not self.config.ai.api_key:
            raise ValueError("AI API key is required")
        
        if not os.path.exists(self.config.cdk_diff_file):
            print(f"::warning::CDK diff file not found: {self.config.cdk_diff_file}")
    
    def run(self) -> Dict[str, Any]:
        """Run the summarizer and return results."""
        try:
            print("::notice::CDK Diff Summarizer starting...")
            print(f"::notice::Working directory: {os.getcwd()}")
            print(f"::notice::CDK diff file: {self.config.cdk_diff_file}")
            
            # Read CDK diff data
            diff_data = self._read_cdk_diff()
            
            if not diff_data or not self._has_changes(diff_data):
                print("::notice::No changes detected in CDK diff")
                return self._handle_no_changes()
            
            # Generate summary
            summary_result = self._generate_summary(diff_data)
            
            # Format output
            formatted_summary = self._format_output(summary_result['summary'])
            
            # Post to GitHub if configured
            issue_number = None
            if self.config.github:
                issue_number = self._post_to_github(formatted_summary)
            
            # Set outputs
            self._set_outputs(summary_result, issue_number)
            
            print("::notice::CDK Diff Summarizer completed successfully!")
            
            return {
                'success': True,
                'summary': formatted_summary,
                'issue_number': issue_number,
                'metadata': summary_result['metadata']
            }
            
        except Exception as e:
            print(f"::error::An error occurred: {str(e)}")
            self._set_error_outputs(str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def _read_cdk_diff(self) -> Dict[str, Any]:
        """Read and parse CDK diff file."""
        diff_file = Path(self.config.cdk_diff_file)
        
        if not diff_file.exists():
            print(f"::warning::CDK diff file not found: {diff_file}")
            return {"stacks": {}}
        
        try:
            with open(diff_file, 'r') as f:
                content = f.read().strip()
                
            if not content:
                print(f"::warning::CDK diff file is empty: {diff_file}")
                return {"stacks": {}}
            
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"::error::Failed to parse CDK diff file: {str(e)}")
            return {"stacks": {}}
        except Exception as e:
            print(f"::error::Failed to read CDK diff file: {str(e)}")
            return {"stacks": {}}
    
    def _has_changes(self, diff_data: Dict[str, Any]) -> bool:
        """Check if there are any changes in the diff data."""
        stacks = diff_data.get('stacks', {})
        
        for stack_data in stacks.values():
            # Check stack-level changes
            if any(stack_data.get(action) for action in ['create', 'update', 'destroy']):
                return True
            
            # Check resource-level changes
            resources = stack_data.get('resources', {})
            for resource_data in resources.values():
                if any(resource_data.get(action) for action in ['create', 'update', 'destroy', 'replace']):
                    return True
        
        return False
    
    def _handle_no_changes(self) -> Dict[str, Any]:
        """Handle case when no changes are detected."""
        no_changes_message = """## No Infrastructure Changes Detected

No changes were found in the CDK diff. This could mean:

- The infrastructure is already up to date
- No changes were made to the CDK code
- The CDK diff command failed to execute properly

**Next Steps:**
1. Verify that changes were actually made to your CDK code
2. Check the CDK diff command execution in the logs
3. Ensure your CDK stack is properly configured

---
*Generated by CDK Diff Summarizer*"""
        
        # Set outputs
        self._set_outputs({
            'summary': no_changes_message,
            'metadata': {
                'generator': 'CDK Diff Summarizer',
                'version': '1.0.0',
                'model': 'none',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'repository': os.getenv('GITHUB_REPOSITORY', 'Unknown')
            }
        }, None)
        
        return {
            'success': True,
            'summary': no_changes_message,
            'issue_number': None,
            'metadata': {
                'generator': 'CDK Diff Summarizer',
                'version': '1.0.0',
                'model': 'none',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'repository': os.getenv('GITHUB_REPOSITORY', 'Unknown')
            }
        }
    
    def _generate_summary(self, diff_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary from diff data."""
        # Check cache first
        if self.cache:
            diff_hash = self.cache.create_diff_hash(diff_data)
            cached_summary = self.cache.get_diff_summary(diff_hash)
            if cached_summary:
                print("::notice::Using cached summary")
                return {
                    'summary': cached_summary,
                    'metadata': self._create_metadata('cached')
                }
        
        # Generate template summary
        template_summary = self.template_manager.render_summary(diff_data)
        
        # Generate AI summary
        ai_summary = self.ai_service.generate_summary(diff_data, template_summary)
        
        # Combine summaries
        final_summary = self._combine_summaries(template_summary, ai_summary)
        
        # Cache the result
        if self.cache:
            diff_hash = self.cache.create_diff_hash(diff_data)
            self.cache.set_diff_summary(diff_hash, final_summary)
        
        return {
            'summary': final_summary,
            'metadata': self._create_metadata(self.config.ai.model)
        }
    
    def _combine_summaries(self, template_summary: str, ai_summary: str) -> str:
        """Combine template and AI summaries."""
        # For now, use AI summary as primary, but this could be enhanced
        # to intelligently combine both summaries
        return ai_summary
    
    def _format_output(self, summary: str) -> str:
        """Format output based on configuration."""
        metadata = self._create_metadata(self.config.ai.model)
        
        return OutputFormatter.format_output(
            summary, 
            self.config.output_format, 
            metadata
        )
    
    def _post_to_github(self, summary: str) -> Optional[int]:
        """Post summary to GitHub."""
        if not self.config.github:
            return None
        
        return self.github_service.post_summary(summary, self.config.output_format)
    
    def _create_metadata(self, model: str) -> Dict[str, str]:
        """Create metadata for the summary."""
        return {
            'generator': 'CDK Diff Summarizer',
            'version': '1.0.0',
            'model': model,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'repository': os.getenv('GITHUB_REPOSITORY', 'Unknown'),
            'commit_sha': os.getenv('GITHUB_SHA', 'Unknown'),
            'workflow_run_id': os.getenv('GITHUB_RUN_ID', 'Unknown')
        }
    
    def _set_outputs(self, summary_result: Dict[str, Any], issue_number: Optional[int]):
        """Set GitHub Action outputs."""
        if self.github_service:
            self.github_service.set_output('summary', summary_result['summary'])
            self.github_service.set_output('success', 'true')
            
            if issue_number:
                self.github_service.set_output('issue-number', str(issue_number))
            
            # Add metadata output
            metadata = summary_result.get('metadata', {})
            self.github_service.set_output('metadata', json.dumps(metadata))
    
    def _set_error_outputs(self, error_message: str):
        """Set error outputs."""
        if self.github_service:
            self.github_service.set_output('success', 'false')
            self.github_service.set_output('error', error_message)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if self.cache:
            return self.cache.cache_manager.get_stats()
        return {}
    
    def clear_cache(self):
        """Clear cache."""
        if self.cache:
            self.cache.cache_manager.clear()


def create_summarizer(config: Config) -> CDKDiffSummarizer:
    """Factory function to create a summarizer instance."""
    return CDKDiffSummarizer(config)


def run_summarizer(config: Config) -> Dict[str, Any]:
    """Convenience function to run the summarizer."""
    summarizer = create_summarizer(config)
    return summarizer.run() 