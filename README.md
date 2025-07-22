# CDK Diff Summarizer

My general goal is to make complext things as simple as possible so here we go. According to claude.ai and me this project can be summarized as:

A professional, modular GitHub Action that automatically summarizes AWS CDK diffs using AI, making infrastructure changes easier to understand for both technical and non-technical stakeholders. Sometimes you just want easy words and short sentences, understand and explain what is happening during cdk deploys with some help of our friends of AI. Born out of the idea learning aws and its implications when there are changes and being suprised that some changes (e.g. updates) can impact your cloud stack later on. Probalbvy has to do with my knowledge gap so here we are.

<!--

[![Build and Test](https://github.com/Pauly-DData/cdk-diff-summarizer/workflows/Build%20and%20Test/badge.svg)](https://github.com/Pauly-DData/cdk-diff-summarizer/actions/workflows/build.yml)
[![Release](https://github.com/Pauly-DData/cdk-diff-summarizer/workflows/Release/badge.svg)](https://github.com/Pauly-DData/cdk-diff-summarizer/actions/workflows/release.yml)
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
- **Cost Impact Analysis**: Estimated cost impact assessment
- **Security Focus**: Special attention to security-related resource changes
- **Flexible Configuration**: Extensive configuration options via environment variables
- **Rate Limiting**: Built-in exponential backoff for API reliability
- **Error Handling**: Graceful handling of missing diffs and API errors

## Quick Start

### 1. Add the Action to Your Workflow

```yaml
name: CDK Diff Summary

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
      
      # Use the CDK Diff Summarizer
      - name: Summarize CDK Diff
        uses: Pauly-DData/cdk-diff-summarizer@v1
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
          output-format: 'both'
```

### 2. Set Up Required Secrets

In your repository settings, add these secrets:

- `OPENAI_API_KEY`: Your OpenAI API key
- `AWS_ACCESS_KEY_ID`: AWS access key for CDK operations
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for CDK operations
- `AWS_REGION`: AWS region (e.g., `us-east-1`)

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
| `cost-impact` | Estimated cost impact level |
| `success` | Whether the action completed successfully |

## Output Formats

### `markdown` (Default)
Standard markdown format with structured sections:
- Executive Summary
- Resource Changes Table
- Security & Permissions
- Cost Impact
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
  "cost_impact": "moderate"
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
- **Cost**: Minimal - only pay for actual usage
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

If you encounter any issues or have questions, please [open an issue](https://github.com/Pauly-DData/cdk-diff-summarizer/issues). 
