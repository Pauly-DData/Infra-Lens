#!/usr/bin/env python3
"""
Main entry point for CDK Diff Summarizer GitHub Action.
This is the new modular version with enhanced features.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from summarizer import run_summarizer


def main():
    """Main function for the GitHub Action."""
    try:
        # Load configuration
        config = Config()
        
        # Run the summarizer
        result = run_summarizer(config)
        
        # Exit with appropriate code
        if result['success']:
            sys.exit(0)
        else:
            print(f"::error::Summarizer failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"::error::Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main() 