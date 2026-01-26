# Error Taxonomy (Stable Failures and Actionable Messages)

## Goal

Provide a small, stable set of error categories so:
- CLI exit codes are consistent
- service HTTP responses are consistent
- artifacts remain comparable across versions/providers

## Core error categories (recommended)

### Configuration errors
- `ConfigInvalid`: schema or validation failure
- `MissingSecret`: required env var missing
- `PluginUnavailable`: selected engine/provider backend not installed

### Policy errors (expected failures)
- `PolicyViolation`: read-only violation, tool not allowlisted, missing scope
- `BudgetExceeded`: max tool calls, max time, max tokens, max cost
- `ApprovalRequired`: action requires approval (if enabled)

### Model errors
- `ModelTimeout`
- `ModelProviderError` (HTTP 4xx/5xx, parsing failure)
- `ModelResponseInvalid` (schema/format mismatch)

### Tool errors
- `ToolNotFound`
- `ToolTimeout`
- `ToolProviderError`
- `ToolResultInvalid`

### Retrieval/storage errors
- `RetrievalError`
- `VectorStoreError`
- `StorageError` (artifact/run/memory stores)

### Evaluation errors
- `EvaluationError` (suite invalid, scorer failure, gate comparison failure)

## Error object fields (recommended)

Every error should capture:
- `type` (one of the categories)
- `message` (actionable)
- `details` (structured, redacted)
- `retryable` (bool)
- `source` (model|tool|retrieval|storage|policy)

## HTTP mapping (service)

Recommended mapping:
- 400: `ConfigInvalid`
- 401/403: auth issues and `PolicyViolation` (scoped)
- 409: conflicts (duplicate run_id, idempotency collisions)
- 412: `PluginUnavailable` / missing capabilities
- 422: validation errors (tool args/model output invalid)
- 429: budget/rate limits
- 500: unexpected internal failures
- 502/503/504: upstream provider failures/timeouts

## CLI mapping (exit codes)

Recommended mapping:
- 2: user/config/policy error (actionable)
- 3: runtime/provider failure
- 4: evaluation gate failure

