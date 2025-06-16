# AI-Powered CDK Diff Summarizer

This GitHub Action automatically generates human-readable summaries of AWS CDK infrastructure changes using AI. It analyzes the output of `cdk diff` and provides both technical and business-impact focused summaries.

## Features

- Automatically runs on pull requests
- Generates AI-powered summaries of infrastructure changes
- Posts summaries both in GitHub Actions logs and as PR comments
- Focuses on business impact and potential risks
- Supports all CDK resource types

## Setup

1. Add the following secrets to your GitHub repository:
   - `OPENAI_API_KEY`: Your OpenAI API key

2. The workflow will automatically:
   - Run on pull requests
   - Generate CDK diffs
   - Create AI summaries
   - Post results to the PR

## Requirements

- Node.js 18+
- Python 3.9+
- AWS CDK CLI
- OpenAI API key

## Local Development

1. Install dependencies:
```bash
npm install
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. Run the script locally:
```bash
npx cdk diff --json > cdk-diff.json
python summarize_and_comment.py 