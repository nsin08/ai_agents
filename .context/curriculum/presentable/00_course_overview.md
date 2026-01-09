# Course Overview: AI Agents (Foundations → Production)

## Audience

- Software engineers building agentic products
- Solution/enterprise architects designing agent platforms
- Product/engineering leaders who need correct mental models + governance

## Prerequisites

- Can read/write basic code (any language)
- Familiar with HTTP APIs, JSON, auth concepts
- Basic understanding of LLMs (prompting, tokens, context window)

## Outcomes (What You’ll Be Able To Do)

By the end of the curriculum, learners can:

- Decide when an agent is appropriate vs deterministic automation
- Design a production agent architecture (orchestrator, tools, memory, safety, observability)
- Implement a control-loop agent with tool contracts and verification
- Build evaluation, safety, and reliability mechanisms (tests, guardrails, HITL)
- Operate agents in production (deployment model, cost control, performance, monitoring)

## Structure (4 Levels, 25 Chapters, 12 Projects)

This pack mirrors the rough draft chapters:

- **Level 1 — Beginner (Foundations & Mental Models):** B1–B6
- **Level 2 — Intermediate (Core Components & Integration):** I1–I7
- **Level 3 — Advanced (Production Patterns & Safety):** A1–A6
- **Level 4 — Pro (Domain Specialization & Scale):** P1–P6

Projects are modular and can be used as labs, take-home assignments, or capstones.

## Suggested Pacing

Use any pacing model; two common ones:

### Option A — 16-week (Deep)

- Weeks 1–3: Level 1 + Projects P01–P02
- Weeks 4–8: Level 2 + Projects P03–P05
- Weeks 9–12: Level 3 + Projects P06–P07 (+ P11 as optional)
- Weeks 13–16: Level 4 + Capstone (pick one: P08/P09/P10/P12)

### Option B — 6-week (Bootcamp)

- Week 1: Level 1 (compressed) + P01
- Week 2–3: Level 2 + P03/P04
- Week 4: Level 3 essentials (A2–A5) + P07
- Week 5–6: Level 4 essentials + capstone (P09 or P12)

## Assessment Approach (Practical + Evidence-Based)

- **Knowledge checks:** short “explain in your own words” prompts per chapter
- **Labs/projects:** graded via checklists (success criteria, tests, demo evidence)
- **Design reviews:** architecture diagrams + risk analysis + tradeoffs (cost/latency/safety)

## Environment & Tooling (Minimal Assumptions)

This repo is documentation-first. Example implementations are presented as pseudocode and reference architectures.

If you want to add runnable labs later, standardize on:
- A single runtime (e.g., Python or TypeScript)
- A single orchestration pattern (graph/state-machine or loop-based controller)
- A single eval harness (golden tests + regression)

## Primary Source Material (In-Repo)

The curriculum content is derived from `Agents/` documents (see `appendix_source_mapping.md`).

For critical production gaps (testing/eval, security, failure modes), the pack also references:
- `../../review/ai_agents_critical_review.md`

## How To Present (Instructor Notes)

- Lead with **system thinking**: agents are distributed systems with LLM reasoning inside a control loop.
- Treat **tool calls as production API calls**: schema validation, authz, auditing, and rollback semantics.
- Treat **memory as data engineering**: write policy, retrieval policy, and privacy boundaries.
- Treat **evaluation as a product feature**: without tests, you do not have “reliability,” only anecdotes.
