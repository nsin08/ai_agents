# Level 1 Slides — Foundations & Mental Models (B1–B6)

Use this as a slide outline. Each “Slide” section is intended to become 1 slide.

---

## Slide — Title

AI Agents: Foundations & Mental Models (Level 1)

---

## Slide — What You’ll Learn

- What agents are (precise definition)
- What agents are good for (and not good for)
- The baseline architecture (6 pillars)
- Current ecosystem patterns and framework choices

---

## Slide — B1: Why AI Agents Now?

- Chatbots answer; agents execute
- Why “assistants” plateau in real workflows
- Enablers: better models + tool standardization + retrieval/memory + business pull
- Outcome: operational collaborators that can do multi-step work

---

## Slide — Activity: Workflow Backlog

- List 10 workflows requiring human orchestration
- Mark: info-only vs single action vs multi-step
- Pick one workflow for the course projects

---

## Slide — B2: What Is an AI Agent?

- Agent = LLM reasoning inside a control loop
- Observe → Plan → Act → Verify → Refine
- Key components: orchestrator, tools, memory, safety, observability
- Autonomy is a spectrum; gates are part of design

---

## Slide — B3: What Problems Do Agents Solve?

- Multi-step workflows across systems
- Grounded decisions using real-time data (tools + retrieval)
- Reliability through verification, retries, and fallbacks
- “When NOT to use agents” is a feature, not a footnote

---

## Slide — B4: Architecture (6 Pillars)

- UI ↔ Orchestrator ↔ LLM
- Tools: the only path to external state
- Memory: what you retrieve and what you persist
- Safety + Observability: required for production

---

## Slide — B5: Evolution & Trends

- From single prompt → tool use → memory → routing → multi-agent + platforms
- Why multi-LLM designs win (cost/latency/accuracy)
- New risks introduced by more capability (safety, eval, ops)

---

## Slide — B6: Frameworks Landscape

- Loop controller vs graph/state-machine orchestration
- Frameworks help with runtime and patterns; they don’t replace architecture
- Choose based on constraints (auditability, branching, reliability, safety)

---

## Slide — Level 1 Projects

- P01: FAQ bot with RAG (grounding + evaluation basics)
- P02: Intent router (multi-model routing and policy)

---

## Slide — Wrap-Up: Level 1 Outcomes

- You can define an agent precisely
- You can decide when to use (or avoid) agents
- You can sketch a safe architecture and pick a framework direction
