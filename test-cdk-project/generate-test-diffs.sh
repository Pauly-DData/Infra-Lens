#!/bin/bash

# Test CDK Diff Generator for CDK Diff Summarizer
# This script generates different CDK diff scenarios for testing

set -e

echo "🚀 Generating CDK diff test scenarios..."

# Create test directory
mkdir -p test-diffs

# Scenario 1: No changes (empty diff)
echo "📝 Generating Scenario 1: No changes..."
echo '{"stacks": {}}' > test-diffs/no-changes.json
echo "✅ Generated: test-diffs/no-changes.json"

# Scenario 2: Simple changes (add resources)
echo "📝 Generating Scenario 2: Simple changes..."
cat > test-diffs/simple-changes.json << 'EOF'
{
  "stacks": {
    "SimpleStack": {
      "create": true,
      "resources": {
        "SimpleStack/TestBucket": {
          "type": "AWS::S3::Bucket",
          "create": true
        },
        "SimpleStack/TestFunction": {
          "type": "AWS::Lambda::Function",
          "create": true
        }
      }
    }
  }
}
EOF
echo "✅ Generated: test-diffs/simple-changes.json"

# Scenario 3: Security changes (high risk)
echo "📝 Generating Scenario 3: Security changes..."
cat > test-diffs/security-changes.json << 'EOF'
{
  "stacks": {
    "SecurityStack": {
      "create": true,
      "resources": {
        "SecurityStack/TestKey": {
          "type": "AWS::KMS::Key",
          "create": true
        },
        "SecurityStack/TestRole": {
          "type": "AWS::IAM::Role",
          "create": true
        },
        "SecurityStack/TestPolicy": {
          "type": "AWS::IAM::Policy",
          "create": true
        },
        "SecurityStack/TestSecret": {
          "type": "AWS::SecretsManager::Secret",
          "create": true
        },
        "SecurityStack/TestVpc": {
          "type": "AWS::EC2::VPC",
          "create": true
        },
        "SecurityStack/TestSecurityGroup": {
          "type": "AWS::EC2::SecurityGroup",
          "create": true
        }
      }
    }
  }
}
EOF
echo "✅ Generated: test-diffs/security-changes.json"

# Scenario 4: Complex changes (multiple stacks, many resources)
echo "📝 Generating Scenario 4: Complex changes..."
cat > test-diffs/complex-changes.json << 'EOF'
{
  "stacks": {
    "SimpleStack": {
      "update": true,
      "resources": {
        "SimpleStack/TestBucket": {
          "type": "AWS::S3::Bucket",
          "update": true
        },
        "SimpleStack/TestFunction": {
          "type": "AWS::Lambda::Function",
          "replace": true
        },
        "SimpleStack/NewResource": {
          "type": "AWS::DynamoDB::Table",
          "create": true
        }
      }
    },
    "SecurityStack": {
      "create": true,
      "resources": {
        "SecurityStack/TestKey": {
          "type": "AWS::KMS::Key",
          "create": true
        },
        "SecurityStack/TestRole": {
          "type": "AWS::IAM::Role",
          "create": true
        }
      }
    },
    "DatabaseStack": {
      "create": true,
      "resources": {
        "DatabaseStack/TestDatabase": {
          "type": "AWS::RDS::DBInstance",
          "create": true
        },
        "DatabaseStack/TestSubnetGroup": {
          "type": "AWS::RDS::DBSubnetGroup",
          "create": true
        }
      }
    }
  }
}
EOF
echo "✅ Generated: test-diffs/complex-changes.json"

# Scenario 5: Destructive changes (deletions)
echo "📝 Generating Scenario 5: Destructive changes..."
cat > test-diffs/destructive-changes.json << 'EOF'
{
  "stacks": {
    "OldStack": {
      "destroy": true,
      "resources": {
        "OldStack/OldBucket": {
          "type": "AWS::S3::Bucket",
          "destroy": true
        },
        "OldStack/OldFunction": {
          "type": "AWS::Lambda::Function",
          "destroy": true
        }
      }
    },
    "NewStack": {
      "create": true,
      "resources": {
        "NewStack/NewBucket": {
          "type": "AWS::S3::Bucket",
          "create": true
        }
      }
    }
  }
}
EOF
echo "✅ Generated: test-diffs/destructive-changes.json"

# Scenario 6: Invalid JSON (for error testing)
echo "📝 Generating Scenario 6: Invalid JSON..."
cat > test-diffs/invalid.json << 'EOF'
{
  "stacks": {
    "TestStack": {
      "create": true,
      "resources": {
        "TestStack/TestResource": {
          "type": "AWS::S3::Bucket",
          "create": true
        }
      }
    }
  }
  // Missing closing brace - invalid JSON
EOF
echo "✅ Generated: test-diffs/invalid.json"

echo ""
echo "🎉 All test scenarios generated!"
echo ""
echo "Available test files:"
ls -la test-diffs/
echo ""
echo "Next steps:"
echo "1. Test with: python ../src/main.py"
echo "2. Set OPENAI_API_KEY environment variable"
echo "3. Use different diff files: --cdk-diff-file test-diffs/[scenario].json" 