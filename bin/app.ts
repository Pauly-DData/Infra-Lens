#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DummyStack } from '../dummy_stack/dummy_stack';

const app = new cdk.App();
new DummyStack(app, 'DummyStack', {
  env: {
    account: '123456789012',
    region: 'us-east-1',
  },
}); 