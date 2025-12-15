# Documentation Template Library

This directory contains **reusable templates** for creating consistent documentation across all tiers.

## 📚 Available Templates

### Overview Templates

- [template-overview-concepts.md](#template-overview-concepts) - Concept documentation
- [template-overview-architecture.md](#template-overview-architecture) - Architecture diagrams
- [template-overview-lifecycle.md](#template-overview-lifecycle) - Lifecycle documentation

### Guide Templates

- [template-guide-getting-started.md](#template-guide-getting-started) - Getting started guides
- [template-guide-howto.md](#template-guide-howto) - How-to guides
- [template-guide-integration.md](#template-guide-integration) - Integration guides
- [template-guide-troubleshooting.md](#template-guide-troubleshooting) - Troubleshooting guides

### API Templates

- [template-api-endpoint.md](#template-api-endpoint) - Individual endpoint documentation
- [template-api-reference.md](#template-api-reference) - Complete API reference

### Example Templates

- [template-example-basic.md](#template-example-basic) - Basic examples
- [template-example-advanced.md](#template-example-advanced) - Advanced patterns

### Best Practices Templates

- [template-best-practices-performance.md](#template-best-practices-performance) - Performance
- [template-best-practices-security.md](#template-best-practices-security) - Security
- [template-best-practices-cost.md](#template-best-practices-cost) - Cost optimization

---

## Template: Overview - Core Concepts

**File**: `template-overview-concepts.md`
**Use in**: MVP, Scaffold, Production, Enterprise

```markdown
# (Concept Name)

**Definition**: (Single sentence definition)
**Tier**: (MVP, Scaffold, Production, Enterprise)
**Related Concepts**: (List other concepts)

## Overview

(2-3 paragraph explanation of the concept)

## Key Components

1. **(Component 1)**: (Brief description)
2. **(Component 2)**: (Brief description)
3. **(Component 3)**: (Brief description)

## When to Use

- Use case 1: (Description)
- Use case 2: (Description)
- Use case 3: (Description)

## Example

\`\`\`(Language)
// Example code
\`\`\`

## Best Practices

- [ ] Best practice 1
- [ ] Best practice 2
- [ ] Best practice 3

## Common Mistakes

- ❌ Mistake 1: (Description)
- ❌ Mistake 2: (Description)

## Related Topics

- [Related 1](link)
- [Related 2](link)
```

---

## Template: Guide - How-To

**File**: `template-guide-howto.md`
**Use in**: MVP, Scaffold, Production, Enterprise

```markdown
# How to (Complete Task)

**Difficulty**: Beginner | Intermediate | Advanced
**Time Required**: (X minutes)
**Prerequisites**: (List requirements)

## Overview

(1-2 sentence summary of what you'll accomplish)

## Prerequisites Check

Before starting, verify you have:

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Access to (Resource)

## Step-by-Step Instructions

### Step 1: (First Action)

(Description of what to do)

\`\`\`
// Code example
\`\`\`

Expected result: (What you should see)

### Step 2: (Second Action)

(Description)

\`\`\`
// Code example
\`\`\`

Expected result: (What you should see)

### Step 3: (Subsequent Action)

(Continue as needed)

## Verification

How to verify success:

\`\`\`
// Verification command
\`\`\`

Expected output: (What success looks like)

## Troubleshooting

### Issue: (Common Problem)

**Error Message**: (If applicable)
**Solution**: (Step-by-step fix)

### Issue: (Another Problem)

**Error Message**: (If applicable)
**Solution**: (Step-by-step fix)

## Next Steps

- [ ] Do next action
- [ ] Continue with (Next guide)

## Related Guides

- [Related 1](link)
- [Related 2](link)
```

---

## Template: API - Endpoint

**File**: `template-api-endpoint.md`
**Use in**: Scaffold, Production, Enterprise

```markdown
# (Endpoint Name)

## Overview

**Endpoint**: `(METHOD) /(path)`
**Authentication**: (Type)
**Rate Limit**: (Requests/minute)
**Availability**: (Tier) tier and above

(1-2 paragraph description)

## Request

### URL

\`\`\`
(METHOD) https://api.(domain)/(path)
\`\`\`

### Headers

\`\`\`
Authorization: Bearer (token)
Content-Type: application/json
\`\`\`

### Parameters

| Name   | Type    | Required | Description   |
| ------ | ------- | -------- | ------------- |
| param1 | string  | Yes      | (Description) |
| param2 | integer | No       | (Description) |

### Body

\`\`\`json
{
"field1": "value1",
"field2": "value2"
}
\`\`\`

## Response

### Success (200 OK)

\`\`\`json
{
"id": "resource-id",
"status": "success",
"data": {
"field1": "value1"
}
}
\`\`\`

### Error Responses

#### 400 Bad Request

\`\`\`json
{
"error": "invalid_request",
"message": "Parameter 'X' is required"
}
\`\`\`

#### 401 Unauthorized

\`\`\`json
{
"error": "authentication_failed",
"message": "Invalid or expired token"
}
\`\`\`

## Examples

### Example 1: (Common Use Case)

**Request**:
\`\`\`curl
curl -X (METHOD) https://api.(domain)/(path) \\
-H "Authorization: Bearer YOUR_TOKEN" \\
-H "Content-Type: application/json" \\
-d '{"field": "value"}'
\`\`\`

**Response**:
\`\`\`json
{
"success": true,
"data": {
"id": "123"
}
}
\`\`\`

## Rate Limiting

- **Limit**: (X) requests per minute
- **Reset**: Every minute
- **Headers**:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Best Practices

- Use pagination for large result sets
- Cache responses when appropriate
- Implement exponential backoff for retries

## Related Endpoints

- [Related 1](link)
- [Related 2](link)
```

---

## Template: Example - Basic

**File**: `template-example-basic.md`
**Use in**: MVP, Scaffold

```markdown
# Example: (Scenario)

**Difficulty**: Beginner
**Time**: (X minutes)
**Source Code**: [GitHub](link)

## Overview

(Description of what the example demonstrates)

## Complete Code

\`\`\`(Language)
// Complete working example
// Copy-paste ready

(Full code)
\`\`\`

## Explanation

### Section 1: (Part Description)

\`\`\`(Language)
(Relevant code snippet)
\`\`\`

(Explanation of what this does)

### Section 2: (Next Part)

(Continue as needed)

## Running the Example

\`\`\`bash

# Commands to run the example

\`\`\`

## Expected Output

\`\`\`
(What the output should look like)
\`\`\`

## Modifying for Your Use Case

To adapt this example:

1. Change X to your value
2. Update Y for your system
3. Configure Z as needed

## Related Examples

- [Example 1](link)
- [Example 2](link)
```

---

## Template: Best Practices

**File**: `template-best-practices.md`
**Use in**: Production, Enterprise

```markdown
# Best Practices: (Topic)

**Tier**: Production and above
**Importance**: Critical | High | Medium

## Overview

(Description of the practice area)

## Key Principles

### Principle 1: (Name)

(Explanation)

**Implementation**:
\`\`\`(Language)
// Good example
(Code showing best practice)
\`\`\`

**Avoid**:
\`\`\`(Language)
// Bad example
(Code to avoid)
\`\`\`

### Principle 2: (Name)

(Continue with more principles)

## Checklist

- [ ] Practice 1 implemented
- [ ] Practice 2 implemented
- [ ] Practice 3 implemented

## Metrics to Monitor

| Metric   | Target | Tool   |
| -------- | ------ | ------ |
| Metric 1 | X      | (Tool) |
| Metric 2 | Y      | (Tool) |

## Common Issues

**Issue**: (Problem)
**Solution**: (How to fix)
**Prevention**: (How to avoid)

## Further Reading

- [Link 1](link)
- [Link 2](link)
```

---

## Using These Templates

### Step 1: Copy the Template

Choose the appropriate template for your content type.

### Step 2: Replace Placeholders

Replace all **(Placeholder)** text with your actual content:

- **(Concept Name)** → Your concept
- **(Language)** → JavaScript, Python, Go, etc.
- **(Method)** → GET, POST, PUT, DELETE, etc.

### Step 3: Add Real Examples

Replace example code with actual, working code from your system.

### Step 4: Review and Polish

- Check for consistency
- Verify all links work
- Test code examples
- Proofread carefully

### Step 5: Submit

Add to appropriate directory in the tier structure.

---

## Template Customization

These templates are **starting points**. Customize them:

- Add sections specific to your use case
- Include industry-specific terminology
- Add relevant diagrams
- Include region-specific information

---

## Version History

| Version | Date       | Changes                  |
| ------- | ---------- | ------------------------ |
| 1.0.0   | 2025-12-07 | Initial template library |

---

© 2025 - **(Organization Name)**. All rights reserved.
