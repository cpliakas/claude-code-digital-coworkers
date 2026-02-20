---
name: lookup-aws-service
description: "Look up AWS service capability cards for service selection decisions. Use to verify service capabilities, compare alternatives, or discover services for a use case."
user-invokable: true
allowed-tools: Read, Glob
argument-hint: "<service name> or category:<category> or usecase:<description>"
---

# AWS Service Lookup

Look up curated capability cards for AWS services. Each card covers when to use a service, when not to, key facts, pricing, common misconceptions, and related services.

## Input

`$ARGUMENTS` = one of:

- **Service name** — e.g. `Storage Gateway`, `DynamoDB`, `S3 Object Lambda`
- **Category query** — `category:storage`, `category:compute`, `category:database`
- **Use-case query** — `usecase:shared file system with AD integration`

If `$ARGUMENTS` is empty, list all available categories and their service counts.

## Process

### 1. Determine Query Type

Parse `$ARGUMENTS`:

- If it starts with `category:`, extract the category name (the part after the prefix, trimmed)
- If it starts with `usecase:`, extract the use-case description (the part after the prefix, trimmed)
- Otherwise, treat the entire argument as a service name to look up

### 2. Find Data Files

Use Glob to find all JSON files in the `data/` directory relative to this skill:

```
plugins/cloud-infra-aws/skills/lookup-aws-service/data/*.json
```

Each file is named by category (e.g. `storage.json`, `compute.json`). Each file contains an array of capability cards.

### 3. Execute the Query

**If no arguments:** Read each JSON file, count the cards, and return a summary table of categories and their service counts.

**If service name lookup:**

1. Read all JSON files
2. Search for matches in this order (stop at the first match level that returns results):
   - Exact match on the `service` field (case-insensitive)
   - Substring match on the `service` field (case-insensitive)
   - Substring match on the `one_liner` field (case-insensitive)
3. Return the full capability card(s) for all matches

**If category query:**

1. Read the JSON file matching the category name (e.g. `storage.json` for `category:storage`)
2. If the file is empty or doesn't exist, report no services in that category
3. Return a summary: service name + one-liner for each card in the category

**If use-case query:**

1. Read all JSON files
2. Search each card's `when_to_use` entries, `one_liner`, and `key_facts` for substring matches (case-insensitive)
3. Return a summary: service name + category + one-liner for each match

## Output

**For service name lookups:** Return the full JSON capability card including all fields (`service`, `category`, `one_liner`, `when_to_use`, `when_not_to_use`, `key_facts`, `pricing_summary`, `common_misconceptions`, `related_services`).

**For category or use-case queries:** Return a table or list with service name, category, and one-liner for each match.

**If no matches:** Report that no capability card was found and list the available services.
