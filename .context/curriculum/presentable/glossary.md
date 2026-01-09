# Glossary (AI Agents)

## Core Terms

- **Agent:** An LLM-based reasoning component inside a control loop that can take actions via tools, maintain state/memory, and verify outcomes.
- **Orchestrator / Controller:** The non-LLM control plane that enforces the loop, validates tool calls, applies policy, and manages retries/timeouts.
- **Tool:** A callable capability (API, function, workflow) with a strict schema, permissions, and defined side effects.
- **Control loop:** Observe → Plan → Act → Verify → Refine (iterative execution with feedback).
- **Autonomy spectrum:** Range from fully user-driven (assistant) to fully autonomous (agent) with varying human gates.

## Grounding & Memory

- **RAG (Retrieval-Augmented Generation):** Bringing external documents/data into the model context at runtime to reduce hallucinations and improve specificity.
- **Short-term memory:** Session context (recent messages, current task state).
- **Long-term memory:** Persisted user/tenant/task knowledge, subject to write policy and privacy constraints.
- **Context engineering:** Designing what information enters the context window (selection, compression, ordering, and formatting).

## Safety & Reliability

- **Guardrails:** Policies and enforcement mechanisms that constrain actions/outputs (permissions, content filters, confirmation gates).
- **HITL (Human-in-the-loop):** Required human review/approval at defined points (especially for irreversible or high-risk actions).
- **Golden tests:** A curated set of stable test cases used to catch regressions in agent behavior.
- **Adversarial tests:** Tests designed to break the system (prompt injection, tool misuse, data exfiltration).

## Operations

- **Observability:** Logs, metrics, traces, and dashboards that make agent behavior debuggable and measurable in production.
- **Cost attribution:** Tracking cost per request/task and attributing to user/tenant/workflow.
- **Routing:** Using different models or strategies (small/large LLMs) based on task complexity, cost, latency, and risk.

