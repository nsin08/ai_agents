# Model Layer (Multi-Role, Swappable Providers)

## Goals

- Support multiple model roles in a single run.
- Swap providers without changing application code.
- Keep base install minimal while supporting OpenAI now.
- Enable deterministic tests via mock/replay providers.

## Roles (first-class)

Recommended stable roles:
- `router`: classify and decide retrieval/tooling posture
- `planner`: create a plan / next actions
- `actor`: execute (propose tool calls, produce final answer)
- `critic`: verify and catch failures
- `summarizer`: compress long outputs and produce structured reports
- `embedder`: embeddings for retrieval (separate interface)

Roles are not "hardcoded behavior"; they are a way to bind config, budgets, and policies to a model usage.

## Interfaces

### Chat model interface: ModelClient

Responsibilities:
- accept messages (system/user/tool)
- return structured output (text and/or tool call requests)
- emit model events with metrics (tokens, latency, cost best-effort)

### Embedder interface: Embedder

Keep embeddings separate from chat to avoid conflating capabilities.

## Providers (base install)

### `mock` (deterministic)

Used for:
- unit tests
- deterministic evaluation gates

Recommended behavior:
- deterministic response selection based on:
  - prompt hash
  - role
  - optional seed

### `ollama` (local dev)

Used for:
- local-first development
- realistic behavior without cloud keys

Implementation:
- HTTP requests to local Ollama server
- configurable base URL per role

### `openai` (cloud, base install)

Used for:
- cloud-backed production inference (initial provider)

Implementation constraint:
- implement OpenAI calls via `httpx` (no OpenAI SDK dependency).

Notes:
- keep API surface behind `ModelClient`
- support standard auth via env var (e.g., `OPENAI_API_KEY`)

## Providers (planned later)

- `anthropic` (Claude)
- `azure_openai` (Azure OpenAI)
- others as needed

These should be added behind the same interface and (optionally) behind extras if dependency footprint grows.

## Multi-model routing (phase-able)

v1:
- Each role maps to exactly one provider/model.

v2+:
- roles define candidate sets
- a `RoutingPolicy` selects a candidate based on:
  - budgets (cost/time)
  - capabilities (tool calling, long context)
  - health signals (timeouts/errors)
  - rollout gates (candidate must pass goldens)

## Cost and token accounting

Design goal:
- every model call emits:
  - request/response token counts (best effort)
  - latency
  - estimated cost (if pricing known)

This enables:
- budget enforcement
- cost attribution per run/tenant/user

Do not block v1 on perfect accounting; emit what is available and keep the schema stable.

