---
name: cf-lint
description: >
  Validate a CloudFormation template against best practices and common
  errors. Use before deploying stacks or during PR review of CF changes.
user-invocable: true
context: fork
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[path to CloudFormation template]"
---

# CloudFormation Lint

Validate a CloudFormation template against best practices.

## Input
`$ARGUMENTS` = path to a CloudFormation YAML template.

## Process

### 1. Read the Template
Parse the template and identify all sections (Parameters, Resources, Outputs, etc.).

### 2. Structural Checks
- [ ] Has Description
- [ ] Has AWSTemplateFormatVersion
- [ ] Parameters have AllowedValues or AllowedPattern constraints
- [ ] Outputs exist for values other stacks might need
- [ ] No hardcoded values that should be parameters (account IDs, AMI IDs, ARNs)

### 3. Security Checks
- [ ] No secrets in Parameters default values or resource properties
- [ ] Security groups don't allow 0.0.0.0/0 on non-HTTP ports
- [ ] IAM policies follow least privilege (no Action: "*" or Resource: "*")
- [ ] Encryption enabled on storage resources (S3, EBS, RDS)
- [ ] CloudTrail or logging enabled where applicable

### 4. Reliability Checks
- [ ] Stateful resources have DeletionPolicy: Retain
- [ ] Multi-AZ enabled for databases and critical services
- [ ] Auto-scaling configured where appropriate

### 5. Best Practice Checks
- [ ] All resources tagged (Environment, Project, ManagedBy)
- [ ] Uses !Ref and !GetAtt over hardcoded values
- [ ] No circular dependencies
- [ ] Stack outputs exported for cross-stack references where needed

### 6. Run cfn-lint (if available)
`cfn-lint $ARGUMENTS` — report any findings.

## Output
For each finding:
- **Category**: Structure / Security / Reliability / Best Practice
- **Severity**: Error / Warning / Info
- **Location**: Resource logical ID or line reference
- **Issue**: What's wrong
- **Fix**: How to fix it
