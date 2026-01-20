# Intermediate Workbook: Projects and Solutions

**Level**: Intermediate
**Total Projects**: 18 (3 per chapter)
**Estimated Time**: 15-20 hours
**Prerequisites**: Beginner curriculum + Labs 00-02

---

## How to Use This Workbook

1. Build the project from the problem statement.
2. Compare your approach with the solution outline.
3. Extend the solution with your own domain constraints.

---

## Chapter 1: Orchestrator Patterns (Projects 1-3)

### Project 1.1: Minimal State Machine Orchestrator

**Goal:** Implement a strict OPRV loop with explicit state transitions.

**Deliverables:**
- State transition table
- Logs for each transition
- Max turns enforcement

**Solution (Example Steps):**
1. Create a transition table using `AgentState` and enforce it with `can_transition()`.
2. Track `turn_count` in `AgentContext` and include it in state change logs.
3. Emit a log line for each transition and verify max turns behavior with a short run.

### Project 1.2: Verification Gate

**Goal:** Add a rule-based verifier that checks output format.

**Deliverables:**
- Verifier function
- Failure feedback message
- Example run showing retry

**Solution (Example Steps):**
1. Write a verifier that checks output format (regex or prefix match).
2. Return `VerificationResult` with `is_complete=False` and feedback on mismatch.
3. Pass the verifier into `Agent` and show a run that retries until the format passes.

### Project 1.3: Retry Policy

**Goal:** Add retry logic to `_act` with backoff.

**Deliverables:**
- Retry counter
- Backoff strategy
- Failure path after max retries

**Solution (Example Steps):**
1. Wrap `_act` in a retry loop that catches transient errors.
2. Apply exponential backoff (for example 0.5s, 1s, 2s) and cap retries.
3. Log the failure path when retries are exhausted.

---

## Chapter 2: Advanced Memory (Projects 4-6)

### Project 2.1: Memory Tier Diagram

**Goal:** Design and document short/long/RAG tiers.

**Deliverables:**
- ASCII diagram
- Write policy
- Retrieval policy

**Solution (Example Steps):**
1. Draw an ASCII diagram with short-term, long-term, and RAG tiers plus responsibilities.
2. Add a write policy and retrieval policy table for each tier.
3. Validate the diagram with a short example scenario.

### Project 2.2: Memory Consolidation Job

**Goal:** Summarize short-term memory into long-term memory.

**Deliverables:**
- Consolidation function
- Summary format
- Example before/after

**Solution (Example Steps):**
1. Pull the last N items from short-term memory and summarize them.
2. Store the summary in long-term memory with metadata (source, timestamp).
3. Show a before/after list to confirm consolidation.

### Project 2.3: Memory Confidence Decay

**Goal:** Decay long-term facts over time.

**Deliverables:**
- Decay rule
- Revalidation trigger
- Example simulation

**Solution (Example Steps):**
1. Add a `confidence` field to long-term memory metadata.
2. Apply a decay step (for example multiply by 0.9 per day).
3. Trigger revalidation when confidence drops below a threshold and log it.

---

## Chapter 3: Context Engineering (Projects 7-9)

### Project 3.1: Prompt Template Library

**Goal:** Create 3 reusable prompt templates.

**Deliverables:**
- Template definitions
- Variable validation
- Example renders

**Solution (Example Steps):**
1. Define three prompt templates with named variables and defaults.
2. Validate missing variables and raise a clear error before rendering.
3. Render each template once and include one failing example.

### Project 3.2: Token Budget Packer

**Goal:** Pack context to a fixed token budget.

**Deliverables:**
- Budget parameters
- Prioritization rules
- Overflow strategy

**Solution (Example Steps):**
1. Estimate tokens per context item with a simple counter function.
2. Sort items by priority and pack until the budget is reached.
3. Drop low-priority items and record the overflow reason.

### Project 3.3: Chunking Comparison

**Goal:** Compare fixed vs sliding chunks on the same document.

**Deliverables:**
- Chunk counts
- Example output
- Recommendation

**Solution (Example Steps):**
1. Apply `chunk_fixed` and `chunk_sliding` to the same document.
2. Compare chunk counts and overlap ratios.
3. Recommend which strategy fits QA vs summary workloads.

---

## Chapter 4: Observability (Projects 10-12)

### Project 4.1: Structured Logging Baseline

**Goal:** Log each OPRV phase with consistent fields.

**Deliverables:**
- Log schema
- Example logs
- Field list

**Solution (Example Steps):**
1. Define a log schema (run_id, phase, latency_ms, status).
2. Emit a log record per OPRV phase.
3. Provide a short example log output for a run.

### Project 4.2: Tracing Spans

**Goal:** Trace each phase and capture durations.

**Deliverables:**
- Span names
- Timing output
- Example trace

**Solution (Example Steps):**
1. Wrap each phase in a `Tracer.span()` context.
2. Capture start/end times and durations per span.
3. Print a trace summary for a sample run.

### Project 4.3: Metrics Thresholds

**Goal:** Define alerts for latency and errors.

**Deliverables:**
- Threshold values
- Alert rules
- Example evaluation

**Solution (Example Steps):**
1. Define thresholds for latency and error rate.
2. Take a `MetricsCollector.snapshot()` and evaluate thresholds.
3. Emit an alert message when thresholds are exceeded.

---

## Chapter 5: Multi-Turn Conversations (Projects 13-15)

### Project 5.1: Slot Filling Agent

**Goal:** Collect required slots for a booking flow.

**Deliverables:**
- Slot list
- Repair prompts
- Completion rule

**Solution (Example Steps):**
1. Define required slots and a storage structure for values and status.
2. Ask targeted questions for missing slots and store answers in metadata.
3. End the flow when all slots are filled and print a summary.

### Project 5.2: Conversation Summaries

**Goal:** Summarize long history into a short memory item.

**Deliverables:**
- Summary function
- Example summary
- Token reduction estimate

**Solution (Example Steps):**
1. Keep the last N turns in short-term memory and summarize older turns.
2. Store the summary as a `MemoryItem` and include it in the prompt.
3. Report the token reduction estimate.

### Project 5.3: Conflict Resolution

**Goal:** Handle conflicting user statements gracefully.

**Deliverables:**
- Conflict detection rule
- Clarification prompt
- Resolution policy

**Solution (Example Steps):**
1. Detect conflicting slot values by comparing stored history.
2. Ask a clarification question and record the chosen value.
3. Update memory and continue the flow.

---

## Chapter 6: Integration Patterns (Projects 16-18)

### Project 6.1: Tool Contract Definition

**Goal:** Define a tool contract with schema and constraints.

**Deliverables:**
- Input schema
- Output schema
- Constraints and side effects

**Solution (Example Steps):**
1. Define input and output JSON schema using `ToolContract`.
2. Document constraints such as timeout, retries, and side effects.
3. Provide an example tool call with valid input.

### Project 6.2: Tool Registry Validation

**Goal:** Validate inputs before tool execution.

**Deliverables:**
- Validation errors
- Example failing input
- Example passing input

**Solution (Example Steps):**
1. Register tools in `ToolRegistry` with validators enabled.
2. Call `execute()` with invalid input and capture the validation error.
3. Call `execute()` with valid input and capture the success result.

### Project 6.3: Circuit Breaker Policy

**Goal:** Define a circuit breaker for failing tools.

**Deliverables:**
- Failure thresholds
- Cooldown period
- Recovery behavior

**Solution (Example Steps):**
1. Track failures per tool and define open/closed breaker states.
2. Open the breaker after the failure threshold and block calls during cooldown.
3. Allow recovery after cooldown and log state changes.

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Uses clear headings and short paragraphs
- [ ] Each project includes a solution outline
- [ ] Links to labs or core modules are accurate
- [ ] Language is accessible and consistent
- [ ] Examples are ASCII only

