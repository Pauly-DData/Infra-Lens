# CDK Diff Summarizer - Test Setup

This directory contains a complete test setup for the CDK Diff Summarizer action.

## 🏗️ Project Structure

```
test-cdk-project/
├── lib/
│   ├── simple-stack.ts      # Simple stack with S3 and Lambda
│   └── security-stack.ts    # Security-focused stack with IAM, KMS, etc.
├── bin/
│   └── app.ts              # Main CDK app
├── test-diffs/             # Generated test scenarios
├── generate-test-diffs.sh  # Script to generate test scenarios
├── test-action.sh          # Script to test the action
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Generate Test Scenarios

```bash
./generate-test-diffs.sh
```

This creates 6 different test scenarios:
- `no-changes.json` - Empty diff (no changes)
- `simple-changes.json` - Basic resource additions
- `security-changes.json` - High-risk security resources
- `complex-changes.json` - Multiple stacks and resources
- `destructive-changes.json` - Resource deletions
- `invalid.json` - Invalid JSON for error testing

### 2. Set Up OpenAI API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Run Tests

```bash
./test-action.sh
```

## 🧪 Test Scenarios

### Scenario 1: No Changes
- **File**: `test-diffs/no-changes.json`
- **Purpose**: Test handling of empty diffs
- **Expected**: Should show "no changes detected" message

### Scenario 2: Simple Changes
- **File**: `test-diffs/simple-changes.json`
- **Purpose**: Test basic resource additions
- **Resources**: S3 Bucket, Lambda Function
- **Expected**: Low risk, minimal cost impact

### Scenario 3: Security Changes
- **File**: `test-diffs/security-changes.json`
- **Purpose**: Test high-risk security resources
- **Resources**: KMS Key, IAM Role, Secrets Manager, VPC, Security Group
- **Expected**: High risk, security warnings

### Scenario 4: Complex Changes
- **File**: `test-diffs/complex-changes.json`
- **Purpose**: Test multiple stacks and resource types
- **Resources**: Multiple stacks, various resource types
- **Expected**: Medium risk, moderate cost impact

### Scenario 5: Destructive Changes
- **File**: `test-diffs/destructive-changes.json`
- **Purpose**: Test resource deletions
- **Resources**: Old resources being destroyed, new ones created
- **Expected**: Cost savings warnings

### Scenario 6: Invalid JSON
- **File**: `test-diffs/invalid.json`
- **Purpose**: Test error handling
- **Expected**: Graceful error handling

## 🔧 Manual Testing

### Test with Specific Scenario

```bash
# Set environment variables
export CDK_DIFF_FILE="test-diffs/security-changes.json"
export OUTPUT_FORMAT="markdown"
export LANGUAGE="en"

# Run the action
python3 ../src/main.py
```

### Test Different Output Formats

```bash
# Markdown output
export OUTPUT_FORMAT="markdown"
python3 ../src/main.py

# JSON output
export OUTPUT_FORMAT="json"
python3 ../src/main.py

# HTML output
export OUTPUT_FORMAT="html"
python3 ../src/main.py
```

### Test Different Languages

```bash
# English
export LANGUAGE="en"
python3 ../src/main.py

# Dutch
export LANGUAGE="nl"
python3 ../src/main.py
```

### Test Caching

```bash
# Enable caching
export CACHE_ENABLED="true"
python3 ../src/main.py

# Disable caching
export CACHE_ENABLED="false"
python3 ../src/main.py
```

## 📊 Expected Results

### Risk Levels
- **Low Risk**: Simple resources (S3, Lambda)
- **Medium Risk**: Database resources (RDS, DynamoDB)
- **High Risk**: Security resources (IAM, KMS, Secrets Manager)

### Cost Impact
- **Minimal**: < 10 changes
- **Moderate**: 10-20 changes
- **Significant**: > 20 changes

### Security Warnings
- IAM role changes
- KMS key modifications
- Secrets Manager updates
- Security group changes

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you're in the correct directory
2. **API Key Error**: Set the `OPENAI_API_KEY` environment variable
3. **Import Errors**: Ensure all dependencies are installed in the parent directory

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL="DEBUG"
python3 ../src/main.py
```

## 📝 Next Steps

After testing locally:

1. **Review Output Quality**: Check if summaries are accurate and helpful
2. **Test Performance**: Monitor API response times and caching effectiveness
3. **Validate Error Handling**: Ensure graceful handling of edge cases
4. **Test in GitHub Actions**: Deploy to a test repository for full workflow testing 