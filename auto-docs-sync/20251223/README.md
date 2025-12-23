# Real Estate Intelligence

This repository is the **Real Estate Intelligence execution surface** within the Infinity X One Systems ecosystem.

It contains:
- Domain-specific agents and workflows
- Cloud Run–deployable services
- Persistent memory services
- Validation and workflow artifacts
- Industry-facing orchestration logic

This repo is designed to **execute**, not to define global cognition or platform-wide policy.

---

## Architecture Overview

The system is organized around a clear separation of concerns:

- **Services**: Executable Cloud Run services (memory, gateway, crawler, agents)
- **Agents**: Domain operators that perform reasoning and execution
- **Memory**: Persistent, Cloud Run–hosted memory service
- **Workflows & Templates**: First-class operational artifacts
- **Validation**: Platform and contract validation utilities

All components in this repo are deployable and operational.

---

## Vision Cortex (Cognitive Submodule)

The `vision-cortex/` directory is included as a **Git submodule**.

**Vision Cortex is the shared cognitive engine** used for advanced reasoning and decision support across Infinity X One Systems.

### Important Rules

- `vision-cortex/` is **read-only** in this repository
- Do **NOT** modify Vision Cortex code here
- All Vision Cortex changes must be made in its own repository
- This repo may *call* Vision Cortex, but does not own it

Think of this relationship as:

> Real Estate Intelligence = execution body  
> Vision Cortex = shared brain  

---

## Memory Authority

This repository includes a Cloud Run–deployable **memory service**.

- Memory is externalized from agents
- Agents must read memory **before** reasoning
- Agents must write memory **after** execution
- Memory persistence is handled via service endpoints, not local state

This ensures determinism, auditability, and replayability.

---

## Git & Repo Conventions

- Generated artifacts (scans, inspections) are ignored
- Workflows, templates, validators, and logs are intentional and tracked
- Backup snapshots are explicitly excluded from version control
- Submodules are pinned and treated as dependencies

---

## Status

This repository is:
- Cloud Run ready
- Memory-enabled
- Agent-operational
- Cognition-integrated (via Vision Cortex)

It represents a **production execution surface**, not an experiment.

---
