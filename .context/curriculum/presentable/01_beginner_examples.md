# Level 1 Examples — Foundations & Mental Models

These examples are intentionally lightweight and framework-agnostic.

## Example 1: Chatbot vs Agent (Control Loop)

**Chatbot (informational):**

```text
user_question -> LLM -> answer
```

**Agent (operational):**

```text
task -> observe -> plan -> act (tools) -> verify -> refine -> result
```

## Example 2: Minimal Agent Controller Skeleton (Pseudocode)

```pseudo
state = { goal, constraints, context }

while not done and steps < MAX_STEPS:
  observations = gather_context(state) + retrieve_docs(state)
  proposal = llm_plan(observations)

  for action in proposal.actions:
    assert policy_allows(action)
    tool_result = tools.execute(action)
    state = update_state(state, tool_result)

  done = verify_goal(state)

return build_user_response(state)
```

## Example 3: 6-Pillar Architecture (ASCII Sketch)

```text
User/UI
  |
  v
Orchestrator/Controller  <--- policy gates, retries, timeouts
  |         |
  |         v
  |      Observability (logs/metrics/traces)
  |
  +--> LLM(s)  <--- reasoning, planning, summarization
  |
  +--> Tools/Integrations  <--- external APIs & side effects
  |
  +--> Memory/Knowledge  <--- RAG + short/long-term state
```

## Example 4: Autonomy Spectrum (Simple Gate Model)

```text
Read-only mode: tool calls only read data → low risk → higher autonomy
Write mode: tool calls mutate state → higher risk → confirmations required
Irreversible actions: higher risk → multi-step approval (HITL)
```

## Example 5: “When NOT to Use Agents” Heuristic

```text
If the workflow is deterministic + stable + cheap:
  build a normal service/workflow engine
Else if it is variable + tool-heavy + needs judgment:
  consider an agent with verification and policy gates
```

