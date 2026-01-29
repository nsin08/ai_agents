# Artifacts and Run State (Reproducibility Contract)

## Why artifacts matter

Standardization requires that any run can be:
- reproduced (in deterministic mode)
- inspected (what happened and why)
- compared (baseline vs candidate)
- audited (tool calls and policy blocks)

This requires a stable artifact bundle format.

## RunArtifact bundle (v1)

A run produces a directory (or object-store prefix) containing:

```text
run/
  run.json                 # main index (metadata, result, pointers)
  config.snapshot.json     # fully-resolved config (redacted secrets)
  events.jsonl             # append-only event log (redacted)
  evidence.json            # evidence manifest (if retrieval used)
  tool_calls.json          # tool call summaries (audit-safe)
  eval/
    scorecard.json         # optional
    gate.json              # optional
```

## `run.json` (index)

Contains:
- identifiers: `run_id`, `request_id` (optional), tenant/user context (optional)
- timestamps: start/end
- status and error summary
- config hash and config snapshot pointer
- versions:
  - `ai_agents` version
  - git commit (if available)
  - provider versions (best effort)
- pointers to other files in the bundle
- final `RunResult` summary

## Secrets and redaction

Rules:
- secrets must never be written to artifacts (API keys, tokens)
- tool arguments/results must be redacted based on ToolContract data handling rules
- prompts and raw model outputs should not be stored by default
  - if needed, store separately under explicit "debug mode" and with warnings

## Artifact store interface

Provide an `ArtifactStore` interface with backends:
- local filesystem (v1)
- object store (future)

Both CLI and service must use the same artifact store abstraction so:
- local runs and hosted runs generate identical artifact bundles

## Run state store (checkpointing)

Separate from artifacts:
- `RunStore` stores checkpointable `RunState` objects (engine internal)
- artifacts are for inspection/replay, not necessarily for resuming

LangGraph engine can map checkpoints to RunStore.
LocalEngine may add RunStore support later.

