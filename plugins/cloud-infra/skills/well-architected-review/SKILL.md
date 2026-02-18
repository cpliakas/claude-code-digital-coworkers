---
name: well-architected-review
description: >
  Run a Well-Architected Framework review against proposed infrastructure
  changes. Use when designing new infrastructure or reviewing significant
  architectural changes.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[description of infrastructure change or path to CF templates]"
---

# Well-Architected Review

Evaluate infrastructure changes against AWS Well-Architected Framework pillars.

## Input
`$ARGUMENTS` = description of the proposed change, or path to CF templates.

## Process

### 1. Understand the Change
Read templates or description. Identify what's being added, modified, or removed.

### 2. Evaluate Each Pillar

**Operational Excellence**
- [ ] Can this be deployed via IaC (no manual steps)?
- [ ] Are there runbooks for failure scenarios?
- [ ] Is monitoring/alerting configured?
- [ ] Can changes be rolled back?

**Security**
- [ ] Least privilege IAM?
- [ ] Encryption at rest and in transit?
- [ ] Network isolation (VPC, security groups, NACLs)?
- [ ] No public access to internal resources?

**Reliability**
- [ ] Multi-AZ for critical components?
- [ ] Auto-scaling for variable load?
- [ ] Backup and restore tested?
- [ ] Fault isolation between components?

**Performance Efficiency**
- [ ] Right-sized for the workload?
- [ ] Caching where beneficial?
- [ ] Async processing where appropriate?

**Cost Optimization**
- [ ] Using managed services where possible?
- [ ] Right pricing model (on-demand vs reserved vs spot)?
- [ ] Cost allocation tags applied?
- [ ] Any idle or over-provisioned resources?

**Sustainability**
- [ ] Managed services preferred over self-hosted?
- [ ] Resource utilization reasonable?

### 3. Risk Assessment
For each pillar, rate: Strong / Adequate / Needs Improvement / At Risk

## Output
Summary table of pillar ratings, specific findings, and recommended actions prioritized by risk.
