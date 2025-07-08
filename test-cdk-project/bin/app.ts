#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SimpleStack } from '../lib/simple-stack';
import { SecurityStack } from '../lib/security-stack';

const app = new cdk.App();

// Create stacks
new SimpleStack(app, 'SimpleStack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});

new SecurityStack(app, 'SecurityStack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
}); 