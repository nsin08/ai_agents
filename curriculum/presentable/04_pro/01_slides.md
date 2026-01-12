# Level 4 Slides: Pro Curriculum (Research, Frameworks, and Frontiers)

Use this as a slide outline. Each "Slide" section is intended to become 1 slide.

This deck aligns to the Pro chapters in `04_pro/`:

- `chapter_01_advanced_frameworks.md`
- `chapter_02_reasoning_architectures.md`
- `chapter_03_agentic_design_patterns.md`
- `chapter_04_research_frontiers.md`

---

## Slide 01: Title

AI Agents - Pro Level (Level 4): Frameworks, Reasoning Architectures, and Research Frontiers

---

## Slide 02: Audience and Goal

- Audience: expert developers, staff+ engineers, architects, researchers
- Goal: build cutting-edge agent systems with strong evaluation discipline
- Focus: patterns, trade-offs, and research-driven engineering

---

## Slide 03: Pro Level Map (4 Chapters)

1. Advanced frameworks (LangGraph/state machines)
2. Reasoning architectures (CoT/ToT/search, multimodal)
3. Agentic design patterns (planning, tool composition, collaboration)
4. Research frontiers (what is emerging and what to adopt)

---

## Slide 04: What Changes at Pro Level

- You stop "demoing" and start "measuring"
- You treat prompts, policies, and models as versioned artifacts
- You assume adversarial inputs and dependency failures
- You optimize for: correctness + safety + cost per success

---

## Slide 05: Framework Deep Dive (Why LangGraph Exists)

- Agents need explicit control flow: loops, branching, interrupts
- State machines make behavior testable and auditable
- Graphs help scale multi-step workflows without prompt bloat

---

## Slide 06: State Machine Mental Model (Visualization)

```text
   [START]
      |
   (plan)
      |
  +---+---+
  |       |
(tool)  (ask_user)
  |       |
 (verify) |
  +---+---+
      |
   [DONE]
```

---

## Slide 07: Graph Patterns You Actually Use

- Linear pipelines: retrieve -> reason -> verify -> respond
- Loops: plan -> execute -> check -> iterate (bounded)
- Interrupts: approval gates, human review, missing input
- Branching: safe vs risky path, small vs large model routing

---

## Slide 08: Framework Choice Trade-off

- Framework helps with control flow and structure
- Framework does not replace tool contracts, guardrails, or evals
- "Framework-first" is not a strategy; "workflow-first" is

---

## Slide 09: Reasoning Architectures (Why You Need More Than One)

- CoT-like: fast reasoning, but brittle and non-deterministic
- Search-based (ToT-like): explore alternatives, higher cost
- Verification-based: check outputs with deterministic tests
- Multimodal: text + vision + structured data

---

## Slide 10: Reasoning = Search + Constraints

Pro-level reasoning is not "more tokens". It is:

- generate candidates (plans, answers, tool calls)
- score candidates (rules, tests, metrics, constraints)
- select and execute the best safe candidate

---

## Slide 11: Tree of Thoughts (Visualization)

```text
Goal
  |
  +-- Plan A -- score 0.6
  |      |
  |      +-- A1 -- score 0.7
  |      +-- A2 -- score 0.2
  |
  +-- Plan B -- score 0.8  <-- choose
         |
         +-- B1 -- score 0.9  <-- execute
```

---

## Slide 12: Multimodal Reasoning (What to Watch)

- Models can "see" but still need tool constraints and verification
- Grounding: use structured extraction where possible
- Risk: hallucinated visual claims -> require evidence and confidence labeling

---

## Slide 13: Agentic Design Patterns (The Real Engineering Work)

- Planning patterns: plan-then-execute, plan-and-solve, reflect-and-revise
- Tool composition: small tools + contracts beat one mega-tool
- Collaboration: router/manager/verifier roles with boundaries

---

## Slide 14: Tool Composition Pipeline (Visualization)

```text
Intent -> tool discovery -> schema validate -> authorize -> execute -> validate -> log/audit
```

---

## Slide 15: Collaboration Patterns (Multi-Agent vs Single Agent)

- Multi-agent is for ceilings: context, skills, permissions, throughput
- It multiplies failure modes; traceability is mandatory
- A verifier stage is the best ROI pattern

---

## Slide 16: Evaluation Is a Feature

- Without evals, you do not have a production system
- Golden sets + adversarial sets + regression dashboards
- Online monitoring + offline evals + synthetic canaries

---

## Slide 17: Benchmarks to Know (Examples)

- MT-Bench / chat eval sets (LLM-as-judge, with constraints)
- AgentBench (agent tasks)
- ToolBench (tool use)
- SWE-bench (real codebase tasks)
- RAG evaluation (citation rate + answer correctness)

---

## Slide 18: Research Frontiers (What Is Emerging)

- Longer context + better retrieval pipelines
- Self-improving agents (reflection, memory with provenance)
- Safer tool runtimes (sandboxing, policy-as-code)
- Better evaluation infrastructure (continuous evals in CI/CD)

---

## Slide 19: Adopt vs Monitor (Decision Framework)

- Adopt when:
  - it improves outcomes on your eval set
  - safety posture remains enforceable
  - cost per success is acceptable
- Monitor when:
  - benefit is unclear
  - verification is weak
  - operational complexity is high

---

## Slide 20: Hands-On Projects (Pro Level)

- Build a LangGraph-style state machine workflow (with interrupts and approvals)
- Implement a reasoning harness (candidates + scoring + selection)
- Build an evaluation pipeline (baseline vs candidate, canaries, gates)

---

## Slide 21: Reading List (Curated Papers)

See:

- `papers/`
- `research_paper_analysis.md`
- `future_trends_analysis.md`

---

## Slide 22: Final Takeaway

- Pro level = engineering discipline: contracts, measurement, reproducibility
- Frameworks are multipliers only when safety and evals are in place
- Your competitive advantage is the loop: build -> measure -> learn -> ship safely

