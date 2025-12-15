# Documentation Style Guide

**Version**: 2.0.0
**Audience**: Documentation writers, content creators
**Status**: Active

---

## 📋 Overview

This guide ensures **consistency, clarity, and professionalism** across all (System Name) documentation.

Alignment with:

- ✅ OpenAI documentation standards
- ✅ Anthropic Claude guides
- ✅ Google Cloud documentation
- ✅ Microsoft Azure documentation

---

## 🎯 Core Principles

### 1. Clarity Over Cleverness

- Use simple, direct language
- Avoid jargon without explanation
- Prefer active voice
- Keep sentences under 20 words

### 2. Consistency Is Key

- Same terminology throughout
- Same formatting for similar content
- Consistent structure across tiers
- Unified code style

### 3. Completeness

- Answer the "why" not just the "how"
- Include prerequisites and next steps
- Provide troubleshooting section
- Link to related topics

### 4. Actionable Content

- Every guide should have clear steps
- Include expected outcomes
- Provide copy-paste ready code
- Show real-world examples

---

## ✍️ Writing Standards

### Formatting

#### Headings

```markdown
# H1: Page Title (Only One Per Document)

## H2: Major Sections

### H3: Subsections

#### H4: Sub-subsections
```

**Rules**:

- Only ONE H1 per document
- Use H2 for major sections
- Keep heading hierarchy logical
- Start with a gerund (verb) for guides: "Getting Started", "Creating Resources"

#### Emphasis

```markdown
**Bold** - For emphasis and key terms
_Italic_ - For variables, file names, and concepts
`Code` - For code snippets, commands, and technical terms
```

#### Lists

```markdown
Unordered lists for groups of items:

- Item 1
- Item 2
- Item 3

Numbered lists for sequential steps:

1. First step
2. Second step
3. Third step

Task lists for checklists:

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3
```

### Writing Voice

#### Use Active Voice

✅ **Good**: "You create a resource by calling the API"
❌ **Bad**: "A resource is created by calling the API"

#### Use Second Person

✅ **Good**: "You configure the webhook..."
❌ **Bad**: "One configures the webhook..."

#### Be Direct

✅ **Good**: "The API returns a 400 error when validation fails"
❌ **Bad**: "It should be noted that error responses may include validation errors"

#### Use Concrete Language

✅ **Good**: "Duplicate the row for each additional environment"
❌ **Bad**: "Consider duplicating the row as needed for scalability"

### Paragraph Structure

- **Opening**: Context or problem
- **Middle**: Explanation or solution
- **Closing**: Result or next step

**Maximum length**: 3-4 sentences per paragraph

### Code Examples

#### General Rules

- Always copy-paste ready
- Include comments explaining logic
- Show both request and response
- Provide multiple languages when applicable
- Include error handling

#### Format

```markdown
\`\`\`(language)
// Language-specific comments
// Explaining the code

const example = "code";
\`\`\`
```

#### Supported Languages

- `javascript`
- `python`
- `bash`
- `curl`
- `json`
- `yaml`
- `sql`
- `html`
- `css`

### Tables

```markdown
| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| Row 1    | Data     | Value    |
| Row 2    | Data     | Value    |
```

**Rules**:

- Use for structured data (parameters, comparisons, matrices)
- Keep columns concise
- Align data to the left
- Maximum 4-5 columns (use multiple tables if needed)

---

## 🏗️ Document Structure

### All Documents

```markdown
# Document Title

**Metadata** (status, audience, time, difficulty)

---

## Overview

Brief description of what this document covers

## Prerequisites

What readers need to know before starting

## Main Content

(Varies by document type)

## Next Steps

Where to go after this document

## Related Topics

Links to related documentation
```

### Overview Documents

```
# Concept Name

## Overview
## Key Components
## When to Use
## Example
## Related Topics
```

### Guide Documents

```
# How to (Action)

## Overview
## Prerequisites
## Step-by-Step Instructions
## Verification
## Troubleshooting
## Next Steps
```

### API Documents

```
# Endpoint Name

## Overview
## Request
## Response
## Examples
## Rate Limiting
## Best Practices
## Related Endpoints
```

### Example Documents

```
# Example: (Scenario)

## Overview
## Complete Code
## Explanation
## Running the Example
## Modifying for Your Use Case
```

---

## 📝 Placeholder Convention

All variable content uses this format:

### Placeholder Syntax

```
(Placeholder Type)
```

### Standard Placeholders

| Placeholder         | Example             | Usage                 |
| ------------------- | ------------------- | --------------------- |
| (System Name)       | "Foundation API"    | Product name          |
| (Organization Name) | "Acme Corp"         | Company name          |
| (Industry)          | "Finance"           | Industry vertical     |
| (Job Title)         | "Software Engineer" | User role             |
| (Region)            | "us-east-1"         | Geographic region     |
| (Version)           | "2.0.1"             | Software version      |
| (Environment)       | "Production"        | Deployment stage      |
| (Color)             | "#FF5733"           | Brand color           |
| (Team Name)         | "Platform Team"     | Organizational unit   |
| (Country)           | "United States"     | Geographic location   |
| (Language)          | "Python"            | Programming language  |
| (Tool/Service)      | "PostgreSQL"        | External tool/service |
| (API Key)           | "sk*live*..."       | Secret/credential     |
| (Domain)            | "api.example.com"   | Domain name           |
| (Port)              | "3000"              | Port number           |
| (Database)          | "MySQL"             | Database system       |

### Usage Examples

```markdown
# Welcome to (System Name)

(System Name) is a platform for (Industry) professionals at (Organization Name).

Get started by installing (System Name) using your preferred package manager:

\`\`\`bash
npm install (system-name-npm-package)
\`\`\`

Configuration:

- API Key: Enter your (API Key) from your (Organization Name) dashboard
- Region: Set to (Region) for optimal performance
- Environment: Currently set to (Environment)
```

### Before Publication

1. Identify ALL placeholders in the document
2. List them at the top of the document
3. When customizing, search and replace all instances
4. Verify no placeholders remain

---

## 🔗 Cross-References

### Internal Links

```markdown
[Link text](./relative/path/to/file.md)
[Link text](./relative/path/to/file.md#heading)
```

### External Links

```markdown
[Link text](https://external-domain.com/path)
```

### Section References

Capitalize section names in links:

```markdown
[Getting Started](#getting-started)
[Best Practices](#best-practices)
```

### Tier Cross-References

```markdown
[See Production Tier](../production/README.md)
[View Advanced Guide](../scaffold/guides/guide-advanced-01.md)
```

---

## 🎨 Visual Elements

### Admonitions (Notes, Warnings, Tips)

#### Note

```markdown
> **Note**: This is important context
```

#### Warning

```markdown
> **⚠️ Warning**: This could cause problems if done incorrectly
```

#### Tip

```markdown
> **💡 Tip**: This will make your life easier
```

#### Example

```markdown
> **📝 Example**: Here's a practical demonstration
```

### Diagrams

Use ASCII diagrams or reference external diagram tools:

```markdown
\`\`\`
┌──────────────┐
│ System │
└──────────────┘
```

For complex diagrams, reference Lucidchart, Draw.io, or ASCII art.

### Icons

Use sparingly and consistently:

- 🔧 Setup/Configuration
- 🚀 Deployment
- 📖 Documentation
- 🧪 Testing
- 🔐 Security
- 📊 Monitoring
- 💰 Cost
- ⚠️ Warning
- ✅ Success
- ❌ Error

---

## 📊 Tone & Voice

### Formal vs. Casual

**Use Formal For**:

- Technical specifications
- Security documentation
- Compliance guides
- Enterprise content

**Use Conversational For**:

- Getting started guides
- Tutorial introductions
- Example explanations
- Tips and tricks

### Audience Awareness

#### Writing for Beginners

- Explain every concept
- Use simple examples
- Include lots of detail
- Provide context

#### Writing for Advanced Users

- Assume knowledge
- Provide quick references
- Include performance details
- Focus on efficiency

### Avoiding Common Mistakes

❌ **Too technical**: "Instantiate a new protocol handler and invoke the asynchronous dispatch mechanism"
✅ **Better**: "Create a new handler and call the async dispatch function"

❌ **Too casual**: "Just like, totally do this thing, y'know?"
✅ **Better**: "Complete this step before proceeding"

❌ **Vague**: "Do some stuff to configure it"
✅ **Better**: "Configure three settings: X, Y, and Z"

---

## ✔️ Checklist for Writers

Before submitting documentation:

### Content

- [ ] Matches the appropriate tier (MVP/Scaffold/Production/Enterprise)
- [ ] Follows the document structure template
- [ ] Includes clear overview/introduction
- [ ] Has step-by-step instructions (if applicable)
- [ ] Includes working code examples
- [ ] Has troubleshooting section (if applicable)
- [ ] Ends with next steps

### Style

- [ ] Uses active voice throughout
- [ ] Sentences under 20 words
- [ ] Clear, jargon-free language
- [ ] Consistent formatting
- [ ] Proper heading hierarchy
- [ ] No grammar errors

### Technical Accuracy

- [ ] Code examples are tested and working
- [ ] API responses are current
- [ ] Commands are accurate
- [ ] URLs are correct
- [ ] Version numbers are current

### Completeness

- [ ] All placeholders identified
- [ ] Cross-references accurate
- [ ] Images/diagrams included if helpful
- [ ] Related topics linked
- [ ] FAQ section for common questions
- [ ] Metadata complete (difficulty, time, etc.)

### Consistency

- [ ] Terminology matches glossary
- [ ] Formatting matches other docs
- [ ] Placeholder usage consistent
- [ ] Code style matches standards
- [ ] Links follow naming convention

---

## 🔤 Terminology & Glossary

### Official Terms

- (System Name): Always capitalize
- API: Not "api" or "Api"
- JSON: Not "json"
- REST: Not "rest"
- SDK: Not "sdk"

### Consistent Language

| Concept   | Term        | Don't Use                 |
| --------- | ----------- | ------------------------- |
| Create    | "create"    | "make", "generate", "add" |
| Delete    | "delete"    | "remove", "destroy"       |
| Update    | "update"    | "modify", "change"        |
| View      | "view"      | "see", "look at"          |
| Configure | "configure" | "set up", "setup"         |

---

## 🔄 Review Process

### For Writers

1. Self-review using the checklist
2. Peer review with colleague
3. Technical review with SME
4. Approval from documentation lead

### For Reviewers

1. Check for clarity and completeness
2. Verify technical accuracy
3. Ensure consistent style
4. Test code examples
5. Validate cross-references

---

## 📦 File Organization

### Naming Convention

```
[section]-[topic]-[number].md

Examples:
- overview-core-concepts-01.md
- guide-getting-started-01.md
- api-resources-01.md
- example-basic-workflow-01.md
- best-practices-performance-01.md
- ops-monitoring-setup-01.md
```

### Directory Structure

```
tier/
├── README.md
├── overview/
│   └── overview-*.md
├── guides/
│   └── guide-*.md
├── api-reference/
│   └── api-*.md
├── examples/
│   └── example-*.md
├── best-practices/ (Production+)
│   └── best-practices-*.md
└── operations/ (Production+)
    └── ops-*.md
```

---

## 🔄 Maintenance

### Update Frequency

- **Weekly**: Check for support questions indicating doc gaps
- **Monthly**: Update examples with new features
- **Quarterly**: Full audit of accuracy
- **Annually**: Strategic review

### Version Control

- Use git for all documentation
- Create branches for major changes
- Document reasons for significant updates
- Maintain version history at top of each file

---

## 📚 Additional Resources

### References

- [Google Developer Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://docs.microsoft.com/en-us/style-guide/welcome/)
- [Apple Style Guide](https://help.apple.com/applestyleguide/)

### Tools

- **Spelling**: Grammarly, built-in spell check
- **Markdown**: VS Code, Markdown preview
- **Diagrams**: Lucidchart, Draw.io, Mermaid

---

## ❓ Frequently Asked Questions

**Q: How many headings should a document have?**
A: 3-6 H2 sections for optimal readability

**Q: When should I use code blocks vs. inline code?**
A: Use code blocks for anything more than one line

**Q: How long should examples be?**
A: Long enough to be useful, short enough to understand (typically 10-30 lines)

**Q: Should I explain every parameter?**
A: Yes, in a table or list format

**Q: When do I capitalize (System Name)?**
A: Always, as it's a proper noun/product name

---

## 📝 Template

Use this when starting a new document:

```markdown
# Document Title

**Tier**: MVP | Scaffold | Production | Enterprise
**Status**: Draft | Review | Published
**Audience**: (Target audience)
**Time to Complete**: (X minutes)
**Difficulty**: Beginner | Intermediate | Advanced

---

## Overview

(1-2 sentence description)

## Prerequisites

(Required knowledge or access)

## Main Content

(Content varies by document type - use appropriate structure)

## Next Steps

(Where to go next)

## Related Topics

- [Related 1](link)
- [Related 2](link)
```

---

## 📞 Questions?

Contact the documentation lead: docs@(organization).com

---

© **(Year)** - **(Organization Name)**. All rights reserved.
