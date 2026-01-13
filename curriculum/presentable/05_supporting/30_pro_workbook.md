# Pro Workbook: Research Projects and Implementations

**Level**: Pro
**Total Projects**: 4
**Estimated Time**: 12-18 hours
**Prerequisites**: Advanced curriculum

---

## Project 1: Evaluation Framework Prototype

**Goal:** Build a small evaluation harness for prompts and tools.

**Deliverables:**
- Evaluation metrics (accuracy, cost, latency)
- Dataset of 20 prompts
- Report with findings

**Solution (Example Steps):**
1. Define a prompt evaluation schema (prompt, expected answer, rubric) and store 20 prompts in a simple JSON file.
2. Run all prompts with `MockProvider` to capture baseline accuracy, latency, and cost (cost = 0 for mock).
3. Run the same prompts with a real LLM provider (Ollama or a cloud adapter) and capture the same metrics.
4. Write a report table with deltas and a short recommendation section.

---

## Project 2: Multi-Agent Coordination Study

**Goal:** Compare single-agent vs multi-agent performance on a complex task.

**Deliverables:**
- Task decomposition plan
- Coordination protocol
- Outcome comparison table

**Solution (Example Steps):**
1. Define three roles (planner, executor, verifier) and a coordination protocol (order of turns, handoff format).
2. Implement a coordinator that passes the task output from planner -> executor -> verifier.
3. Run the same task with a single agent and with the multi-agent protocol; measure quality and latency.
4. Summarize differences in a comparison table and a short narrative.

---

## Project 3: Safety Benchmark

**Goal:** Create a small benchmark for unsafe prompts.

**Deliverables:**
- 25 test prompts
- Safety outcomes table
- Mitigation recommendations

**Solution (Example Steps):**
1. Create 25 prompts across categories (prompt injection, data leakage, policy bypass).
2. Define pass/fail criteria for each prompt and document expected safe behavior.
3. Run prompts against your agent setup and record outcomes in a table.
4. Add mitigation recommendations for each failed case.

---

## Project 4: Cost Engineering Experiment

**Goal:** Reduce cost per request by 30 percent.

**Deliverables:**
- Routing policy
- Cost breakdown
- Before/after chart

**Solution (Example Steps):**
1. Establish baseline cost per request using a fixed dataset and provider settings.
2. Add a routing policy (cheap model for low complexity, expensive model for high risk).
3. Cache high-confidence responses and reuse them for repeated queries.
4. Compare before/after cost and latency and document trade-offs.

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] 4 research projects included
- [ ] Each includes deliverables and solution outline
- [ ] ASCII only

