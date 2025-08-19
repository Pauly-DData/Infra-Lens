# Infra-Lens

My general goal is to make complex things as simple as possible — so here we go.

According to Claude.ai (and myself), this project can be summarized as:

A professional, modular GitHub Action that automatically summarizes infrastructure changes using AI, making infrastructure changes easier to understand for both technical and non-technical stakeholders.

Sometimes, you just want simple words and short sentences to explain what’s happening during CDK deploys — with a little help from our AI friends.

This project grew out of my journey learning AWS, IaC, and CloudFormation — and the realization that certain changes (like updates to deprecated APIs) can unexpectedly break your cloud stack. It’s designed as an add-on to your workflow, helping anyone — even with limited time or technical background — quickly understand infrastructure changes to your cloud.

<!--

[![Build and Test](https://github.com/CloudLabOne/Infra-Lens/workflows/Build%20and%20Test/badge.svg)](https://github.com/CloudLabOne/Infra-Lens/actions/workflows/build.yml)
[![Release](https://github.com/CloudLabOne/Infra-Lens/workflows/Release/badge.svg)](https://github.com/CloudLabOne/Infra-Lens/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

-->

## Features

- **AI-Powered Summaries**: Uses OpenAI's GPT models to generate intelligent, human-readable summaries of CDK diffs
- **Multi-Language Support**: Templates available in English and Dutch (easily extensible)
- **Rich Output Formats**: Markdown, JSON, and HTML output formats
- **Flexible Output**: Post summaries as PR comments, create issues, or both
- **Customizable Templates**: Jinja2-based template system with custom filters
- **Smart Caching**: File-based caching to reduce API calls and improve performance
- **Modular Architecture**: Clean, maintainable codebase with separate concerns
- **Risk Assessment**: Automatic risk level calculation based on resource types

- **Security Focus**: Special attention to security-related resource changes
- **Flexible Configuration**: Extensive configuration options via environment variables
- **Rate Limiting**: Built-in exponential backoff for API reliability
- **Error Handling**: Graceful handling of missing diffs and API errors

## Quick Start

### 1. Add the Action to Your Workflow

```yaml
name: Infra-Lens Summary

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:

jobs:
  summarize-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Your CDK setup steps here...
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install CDK
        run: npm install -g aws-cdk
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
      
      # Generate CDK diff
      - name: Generate CDK Diff
        run: npx cdk diff --json > cdk-diff.json
      
      # Use Infra-Lens
      - name: Summarize Infrastructure Changes
        uses: Pauly-DData/cdk-diff-summarizer@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          cdk-diff-file: 'cdk-diff.json'
          output-format: 'markdown'
          language: 'en'
          model: 'gpt-4'
          max-tokens: '500'
          fail-on-destructive: 'false'
          post-comment: 'true'
          create-issue: 'false'
```

### 2. Set Up Required Secrets

In your repository settings, add this secret:

- `OPENAI_API_KEY`: Your OpenAI API key for generating AI summaries

## Inputs

| Input | Description | Required | Default | Type |
|-------|-------------|----------|---------|------|
| `openai-api-key` | OpenAI API key for generating AI summaries | ✅ Yes | - | string |
| `cdk-diff-file` | Path to the CDK diff JSON file | ❌ No | `cdk-diff.json` | string |
| `output-format` | Output format for the summary | ❌ No | `markdown` | choice |
| `language` | Language for the summary | ❌ No | `en` | choice |
| `model` | OpenAI model to use for summarization | ❌ No | `gpt-4` | string |
| `max-tokens` | Maximum tokens for the summary | ❌ No | `500` | string |
| `fail-on-destructive` | Fail the workflow if destructive changes are detected | ❌ No | `false` | boolean |
| `post-comment` | Post summary as PR comment | ❌ No | `true` | boolean |
| `create-issue` | Create GitHub issue if no PR is found | ❌ No | `false` | boolean |

### Output Format Options
- `markdown` - Standard markdown format (default)
- `json` - JSON format with metadata
- `html` - HTML format with styling

### Language Options
- `en` - English (default)
- `nl` - Dutch

## Outputs

| Output | Description |
|--------|-------------|
| `summary` | The generated AI summary |
| `risk-score` | Risk assessment score (0-100) |

| `success` | Whether the action completed successfully |

## Output Formats

### `markdown` (Default)
Standard markdown format with structured sections:
- Executive Summary
- Resource Changes Table
- Security & Permissions

- Risk Assessment
- Deployment Notes

### `json`
JSON format with metadata and structured data:
```json
{
  "summary": "Markdown summary content",
  "metadata": {
    "generator": "CDK Diff Summarizer",
    "model": "gpt-4",
    "timestamp": "2024-01-01 12:00:00 UTC"
  },
  "risk_score": 75,
  
}
```

### `html`
HTML format with styling and formatting:
- Responsive design
- Professional styling
- Metadata included
- Easy to embed in web applications

## Example Output

The action generates summaries like this:

```markdown
## Infrastructure Changes Summary

### New Resources Being Created
- **S3 Bucket (MyBucket)**: A new storage bucket for application data
- **Lambda Function (MyFunction)**: Serverless function for processing data
- **IAM Roles & Policies**: Security permissions for the Lambda function

### Business Impact

- **Security**: Enhanced with proper IAM roles
- **Scalability**: Serverless architecture allows automatic scaling

### Potential Risks
- **Data Storage**: Ensure proper backup and retention policies
- **Permissions**: Review IAM policies for least privilege access
```

## Advanced Usage

### Custom Model and Token Limits

```yaml
- name: Summarize CDK Diff
  uses: Pauly-DData/cdk-diff-summarizer@v1
  with:
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    model: 'gpt-3.5-turbo'
    max-tokens: '1000'
    output-format: 'json'
    language: 'nl'
```

### Using with Different Output Formats

```yaml
- name: Summarize CDK Diff (JSON)
  uses: Pauly-DData/cdk-diff-summarizer@v1
  with:
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    output-format: 'json'
    post-comment: false

- name: Summarize CDK Diff (HTML)
  uses: Pauly-DData/cdk-diff-summarizer@v1
  with:
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    output-format: 'html'
    create-issue: true
```

### Using with Existing Diff Files

```yaml
- name: Summarize CDK Diff
  uses: Pauly-DData/cdk-diff-summarizer@v1
  with:
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    cdk-diff-file: 'my-custom-diff.json'
    fail-on-destructive: true
```

### Multi-language Support

```yaml
- name: Summarize CDK Diff (Dutch)
  uses: Pauly-DData/cdk-diff-summarizer@v1
  with:
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    language: 'nl'
    post-comment: true
```

## Error Handling

The action handles various error scenarios gracefully:

- **Missing CDK diff file**: Creates a helpful message
- **Empty diff**: Indicates no changes detected
- **API rate limiting**: Automatic retry with exponential backoff
- **Quota exceeded**: Clear error message with next steps
- **Network issues**: Retry logic with detailed logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/CloudLabOne/Infra-Lens/issues).

## 📦 GitHub Marketplace

This action is available on the [GitHub Marketplace](https://github.com/marketplace/actions/cdk-diff-summarizer) for easy installation and discovery.

### Installation

1. Go to the [GitHub Marketplace](https://github.com/marketplace/actions/cdk-diff-summarizer)
2. Click "Use latest version"
3. Copy the generated workflow code
4. Add your `OPENAI_API_KEY` secret to your repository

### Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI's GPT models
- 📊 **Risk Assessment**: Identifies potential security and operational risks

- 📝 **Multiple Output Formats**: Markdown, JSON, and HTML
- 🌍 **Multi-Language Support**: English and Dutch
- 🔒 **Security Focus**: Highlights IAM and security implications 
<!-- last updated: 2025-07-29 -->
