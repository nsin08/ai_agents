# Configuration (Profiles, Multi-Model Roles, and Swappable Components)

## Goals

- One config model for library/CLI/service.
- Multi-model roles are first-class.
- Swappable components are selected by keys (registry) + structured config.
- Deterministic vs real mode can be controlled centrally.

## Config sources (recommended precedence)

1. Explicit config object (embedding)
2. Config file path (YAML/JSON)
3. Environment variables
4. Built-in defaults

CLI and service should support all three:
- file path
- env overrides
- inline overrides (optional, later)

## Top-level sections (proposed)

- `app`: app name, environment, optional build metadata
- `mode`: `deterministic` or `real`
- `engine`: execution engine selection (default `local`)
- `models`: per-role model specs + routing policy
- `tools`: allowlists, providers (native + MCP + optional LC provider)
- `retrieval`: gating, embedder, vector store backend
- `memory`: session store, long-term store, run store (optional early)
- `policies`: read-only, budgets, approvals, safety settings
- `observability`: exporters, redaction rules, sampling
- `evaluation`: golden suites, scorecards, gate thresholds
- `artifacts`: where to write artifact bundles (local path, later S3)
- `service`: server settings (host/port/auth) (only used by hosted wrapper)

## Multi-model roles

### Role map

Roles are stable identifiers:
- `router`: low-cost routing/classification
- `planner`: plan generation
- `actor`: tool use and main response generation
- `critic`: verification
- `summarizer`: compression and report formatting
- `embedder`: embeddings for retrieval

### ModelSpec

Each role has a `ModelSpec`:
- provider: `mock` | `ollama` | `openai` (base) | others later
- model: provider-specific name
- base_url: required for ollama; optional for openai if using standard endpoint
- api_key_env: environment variable name (for providers requiring secrets)
- timeout_s: default timeout
- capabilities: optional declared capabilities (tool_calling, json_mode, long_context)

### Routing policy (phase-able)

v1: role -> exact ModelSpec.

Later:
- allow `candidates` per role
- select by routing policy: cost/latency/health/capability tags
- allow fallbacks (cloud -> local) and eval-gated promotions

## Swappable components via registries

All swappable components should be selected by a key:

- Engine:
  - `local` (built-in)
  - `langgraph` (optional, provided by `agent_lg`)
  - future: `temporal`, `prefect`, etc.

- Tool provider:
  - `native` (built-in)
  - `mcp` (built-in provider type)
  - `langchain` (optional, provided by `agent_lc`)

- Vector store:
  - `memory` (built-in deterministic)
  - `chroma_persist` (optional dependency)
  - future: `pgvector`, `qdrant`, etc.

## Deterministic mode contract

In deterministic mode, config must ensure:
- model roles use `mock` provider (or a replay provider)
- tools use mocked providers or replay fixtures
- retrieval uses deterministic embedder and/or deterministic fixtures

The CLI/service can enforce this by validating config at startup/run time.

## Example config files

The reference schemas live in `schemas/`:
- `schemas/agent_core_config.schema.json`
- `schemas/agent_core_config.example.yaml`

