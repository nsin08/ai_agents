# Level 2 Examples — Intermediate Curriculum

These examples are intentionally short. For verified runnable examples (and tests), use:

- `curriculum/presentable/02_intermediate/snippets/README.md`

---

## Example 1 — Orchestrator as a State Machine (conceptual)

```text
states:
  OBSERVING -> PLANNING -> ACTING -> VERIFYING -> DONE
                         └────────> REFINING -> (back to OBSERVING)
  any -> FAILED (if unrecoverable)

rules:
  max_turns = 5
  retries(tool_timeout) = 2 (exponential backoff)
  stop_if: max_cost, max_latency, max_turns
```

---

## Example 2 — Memory Tiers (conceptual)

```text
short_term:  recent messages / facts (bounded, low risk)
long_term:   curated durable facts (policy-gated writes)
rag:         external docs/search results (policy-gated retrieval)

write policy: what is allowed to persist?
retrieval policy: what is allowed into context?
```

---

## Example 3 — Tool Contract (schema + side effects)

```yaml
tool: create_ticket_comment
description: "Add an internal note to an existing ticket."
inputs:
  ticket_id: { type: string, pattern: "^TCKT-[0-9]+$" }
  body: { type: string, max_length: 2000 }
side_effects:
  writes: ["ticketing_system.comment"]
constraints:
  timeout_s: 5
  retries: 2
gating:
  requires_confirmation: true
```

