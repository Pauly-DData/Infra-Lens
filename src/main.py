#!/usr/bin/env python3
"""
Main entry point for CDK Diff Summarizer GitHub Action.
This is the new modular version with enhanced features.
"""

import sys
import os
from pathlib import Path
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from summarizer import run_summarizer


def main():
    """Main function for the GitHub Action."""
    try:
        print("::debug::Starting main function")
        
        # Load configuration
        config = Config()
        print("::debug::Config loaded")
        
        # Run the summarizer
        result = run_summarizer(config)
        print(f"::debug::Summarizer result: {result}")
        
        # Exit with appropriate code
        if result['success']:
            print("::debug::Success case - printing summary")
            # Print the summary to stdout for testing
            print("\n" + "="*50)
            print("GENERATED SUMMARY:")
            print("="*50)
            summary = result.get('summary', 'No summary generated')
            print(f"Summary length: {len(summary)}")
            print(summary)
            print("="*50 + "\n")
            
            # Set outputs for GitHub Actions
            _set_outputs(result)
            
            sys.exit(0)
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"::error::Summarizer failed: {error_msg}")
            _set_error_outputs(error_msg)
            sys.exit(1)
            
    except ValueError as e:
        # Configuration errors
        print(f"::error::Configuration error: {str(e)}")
        _set_error_outputs(f"Configuration error: {str(e)}")
        sys.exit(1)
        
    except FileNotFoundError as e:
        # File not found errors
        print(f"::error::File not found: {str(e)}")
        _set_error_outputs(f"File not found: {str(e)}")
        sys.exit(1)
        
    except Exception as e:
        # Unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        print(f"::error::{error_msg}")
        print(f"::debug::Traceback: {traceback.format_exc()}")
        _set_error_outputs(error_msg)
        sys.exit(1)


def _set_outputs(result):
    """Set GitHub Action outputs."""
    try:
        # Set summary output
        if 'summary' in result:
            print(f"::set-output name=summary::{result['summary']}")
        
        # Set risk score output
        if 'metadata' in result and 'risk_score' in result['metadata']:
            print(f"::set-output name=risk-score::{result['metadata']['risk_score']}")
        
        # Set cost impact output
        if 'metadata' in result and 'cost_impact' in result['metadata']:
            print(f"::set-output name=cost-impact::{result['metadata']['cost_impact']}")
        
        # Set success output
        print(f"::set-output name=success::{result.get('success', False)}")
        
    except Exception as e:
        print(f"::warning::Failed to set outputs: {str(e)}")


def _set_error_outputs(error_message):
    """Set error outputs for GitHub Actions."""
    try:
        print(f"::set-output name=success::false")
        print(f"::set-output name=error::{error_message}")
    except Exception as e:
        print(f"::warning::Failed to set error outputs: {str(e)}")


if __name__ == '__main__':
    main() 