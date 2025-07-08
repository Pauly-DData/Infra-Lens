# CDK Diff Summarizer

A professional GitHub Action that automatically summarizes AWS CDK diffs using AI, making infrastructure changes easier to understand for both technical and non-technical stakeholders. Understand and explain what is happening during cdk deploys.

[![Build and Test](https://github.com/Pauly-DData/cdk-diff-summarizer/workflows/Build%20and%20Test/badge.svg)](https://github.com/Pauly-DData/cdk-diff-summarizer/actions/workflows/build.yml)
[![Release](https://github.com/Pauly-DData/cdk-diff-summarizer/workflows/Release/badge.svg)](https://github.com/Pauly-DData/cdk-diff-summarizer/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🤖 **AI-Powered Summaries**: Uses OpenAI to generate human-readable summaries of CDK diffs
- 🔄 **Flexible Output**: Post summaries as PR comments, create issues, or both
- ⚡ **Rate Limiting**: Built-in exponential backoff for API reliability
- 🛡️ **Error Handling**: Graceful handling of missing diffs and API errors
- 📊 **Rich Output**: Detailed resource type information and change categorization

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

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `openai-api-key` | OpenAI API key for generating summaries | ✅ Yes | - |
| `aws-region` | AWS region for CDK operations | ✅ Yes | `us-east-1` |
| `cdk-diff-file` | Path to the CDK diff JSON file | ❌ No | `cdk-diff.json` |
| `output-format` | Output format: `issue`, `comment`, or `both` | ❌ No | `both` |
| `model` | OpenAI model to use for summarization | ❌ No | `gpt-4` |
| `max-tokens` | Maximum tokens for the summary | ❌ No | `500` |

## Outputs

| Output | Description |
|--------|-------------|
| `summary` | The generated AI summary |
| `issue-number` | Issue number if created |
| `success` | Whether the action completed successfully |

## Output Formats

### `comment` (PR Comments)
Posts the summary as a comment on the pull request.

### `issue` (GitHub Issues)
Creates a new issue with the summary.

### `both` (Default)
Posts to PR if available, otherwise creates an issue.

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
    aws-region: ${{ secrets.AWS_REGION }}
    model: 'gpt-3.5-turbo'
    max-tokens: '1000'
    output-format: 'issue'
```

### Using with Existing Diff Files

```yaml
- name: Summarize CDK Diff
  uses: Pauly-DData/cdk-diff-summarizer@v1
  with:
    openai-api-key: ${{ secrets.OPENAI_API_KEY }}
    aws-region: ${{ secrets.AWS_REGION }}
    cdk-diff-file: 'my-custom-diff.json'
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
