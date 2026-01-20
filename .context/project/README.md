# Project Context: AI Agents

## Purpose

Comprehensive AI agent learning platform with knowledge base, curriculum, and hands-on labs. This project applies the `space_framework` governance model for enforcement-first SDLC.

## Key Links

- **Repository:** https://github.com/nsin08/ai_agents
- **Framework:** https://github.com/nsin08/space_framework
- **Main Contacts:** @nsin08 (CODEOWNER, Tech Lead, PM)

## Architecture Decision Records (ADR)

This section links to key architectural decisions. Create ADRs in `.context/project/adr/` following the format:

- `YYYYMMDD-{title}.md`

Example: `.context/project/adr/20260120-llm-provider-abstraction.md`

| Decision | Date | Status | Link |
|----------|------|--------|------|
| LLM Provider Abstraction | 2026-01-15 | Accepted | [ADR-001](./adr/20260115-llm-provider-abstraction.md) |

## Key Technologies

- **Language:** Python 3.11+
- **Agent Framework:** LangChain, LangGraph
- **Testing:** pytest, pytest-asyncio
- **Governance:** space_framework (GitHub Actions enforced)

## File Organization (Rule 11)

### Committed (tracked in git)

- `.context/project/` — Architecture, ADRs, design docs, meeting notes
- `.context/sprint/` — Sprint plans, retros, shared materials

### Git-Ignored (per .gitignore)

- `.context/temp/` — Agent scratch work, drafts, logs
- `.context/issues/` — Issue-specific workspaces
- `.context/reports/` — Generated reports, analysis

## Quick Start

See [README.md](../../README.md) for clone, install, and run instructions.

## Governance

This project enforces `space_framework` rules via GitHub Actions:

- **State Machine:** Idea → Approved → Ready → In Progress → In Review → Done → Released
- **Artifact Linking:** Every PR links to a Story; every Story links to an Epic
- **Approval Gate:** Only @nsin08 (CODEOWNER) can merge PRs
- **Evidence-Based:** PRs require evidence mapping (tests, screenshots, metrics)

For governance details, see:
- Framework rules: https://github.com/nsin08/space_framework/tree/main/20-rules
- Framework roles: https://github.com/nsin08/space_framework/tree/main/10-roles

---

**Last Updated:** 2026-01-20
