# Level 4 Examples: Pro (Frameworks, Reasoning, Patterns, Frontiers)

This file provides concrete, end-to-end examples that tie together the four Pro chapters.

Notes:
- These examples are intentionally framework-agnostic.
- Traces are illustrative unless explicitly labeled as captured output.

## Example 1: Graph workflow with an approval interrupt (high-risk write)

Scenario:
- User: "Enable feature flag X in production for tenant T."

Target behavior:
- Read current config
- Propose a diff
- Require approval before applying
- Apply change (idempotent)
- Verify post-change state

Workflow shape (ASCII):

```text
START
  -> classify_intent
  -> read_config
  -> propose_change
  -> approval_interrupt
  -> apply_change
  -> verify_change
  -> DONE
```

Key design points:
- The approval interrupt must be enforced by the runtime, not by prompting.
- The write tool must be idempotent (safe to retry/resume).
- Verification must be executable (read back and compare).

Illustrative trace (high level):

```text
node=classify_intent -> intent=write, risk=high
node=read_config -> tool=config_read, status=success
node=propose_change -> produced diff=...
node=approval_interrupt -> status=pending_approval
node=apply_change -> tool=config_write, status=success
node=verify_change -> tool=config_read, status=success, verified=true
node=DONE
```

Links:
- Framework concepts: `chapter_01_advanced_frameworks.md`
- Tool safety runtime: `chapter_04_research_frontiers.md`

## Example 2: Reasoning harness (candidates + scoring + selection)

Scenario:
- User: "Draft a safe rollout plan for service S, given these constraints."

Pro approach:
- Generate 3 candidate plans
- Score candidates with constraints
- Select the best safe plan
- Produce a final answer with explicit assumptions

Candidate schema (conceptual):
- plan steps (structured)
- risk assessment
- verification steps
- rollback plan

Illustrative scoring rubric:
- Reject if missing rollback plan (hard fail)
- Reward if verification steps are executable
- Penalize if number of steps exceeds budget

Links:
- Reasoning architecture: `chapter_02_reasoning_architectures.md`
- ToT paper: `papers/03_tree_of_thoughts.md`

## Example 3: Tool composition pipeline (discover -> validate -> execute -> record)

Scenario:
- User: "Summarize the latest incident report and open a follow-up ticket."

Tools:
- `incident_fetch` (read)
- `summarize` (read)
- `ticket_create` (write, requires approval)

Pro pipeline:
1. Discover available tools (tool registry schemas)
2. Validate inputs against schemas
3. Authorize write tool (policy + approval)
4. Execute tools with timeouts and retries
5. Record each tool call as a trace event

What to verify:
- Tool call arguments validate
- Ticket creation is blocked without approval
- Trace includes tool names, statuses, and latencies

Links:
- Tool patterns: `chapter_03_agentic_design_patterns.md`
- Evaluation: `benchmark_evaluation_framework.md`

## Example 4: Multi-agent design review (manager-worker-verifier)

Scenario:
- "Review this proposed architecture and identify risks and missing pieces."

Roles:
- Manager: decomposes the review request
- Worker A: security review
- Worker B: reliability review
- Worker C: cost review
- Verifier: checks artifact contract and evidence requirements

Artifact contract (example):
- summary (5 bullets)
- risks (security, reliability, cost)
- missing requirements
- recommended next steps
- evidence links (doc ids or references)

Links:
- Collaboration patterns: `chapter_03_agentic_design_patterns.md`
- Frontier adoption discipline: `chapter_04_research_frontiers.md`

## Example 5: Benchmark scorecard (what "evidence" looks like)

A pro team can answer:
- "Did this change improve the system?"

Example scorecard (illustrative):

| Suite | Success | Invalid Tool Calls | Citation Precision | P95 Latency | Cost / Success |
|------|---------:|-------------------:|-------------------:|------------:|---------------:|
| golden (50) | 0.86 -> 0.90 | 0.07 -> 0.03 | 0.72 -> 0.80 | 4.2s -> 4.6s | $0.12 -> $0.14 |
| adversarial (20) | 0.55 -> 0.60 | 0.12 -> 0.05 | 0.60 -> 0.70 | 5.1s -> 5.4s | $0.18 -> $0.20 |

Interpretation:
- Success improved, invalid tool calls decreased, citation precision improved.
- Latency and cost increased slightly; acceptable if within budget.

Links:
- Benchmark framework: `benchmark_evaluation_framework.md`
- Paper context: `research_paper_analysis.md`

