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

**Solution Outline:**
- Use `AgentState` and `can_transition()` for transitions.
- Track `turn_count` in `AgentContext`.
- Add a log line per transition.

### Project 1.2: Verification Gate

**Goal:** Add a rule-based verifier that checks output format.

**Deliverables:**
- Verifier function
- Failure feedback message
- Example run showing retry

**Solution Outline:**
- Return `VerificationResult` with `is_complete=False` on format mismatch.
- Pass verifier into `Agent` constructor.

### Project 1.3: Retry Policy

**Goal:** Add retry logic to `_act` with backoff.

**Deliverables:**
- Retry counter
- Backoff strategy
- Failure path after max retries

**Solution Outline:**
- Wrap `_act` in try/except and retry on transient errors.
- Use exponential backoff and cap retries.

---

## Chapter 2: Advanced Memory (Projects 4-6)

### Project 2.1: Memory Tier Diagram

**Goal:** Design and document short/long/RAG tiers.

**Deliverables:**
- ASCII diagram
- Write policy
- Retrieval policy

**Solution Outline:**
- Use a three-column diagram with tier rules.
- Add a short policy table (allowed/blocked).

### Project 2.2: Memory Consolidation Job

**Goal:** Summarize short-term memory into long-term memory.

**Deliverables:**
- Consolidation function
- Summary format
- Example before/after

**Solution Outline:**
- Use `ContextSummarizer` or mock summarizer.
- Store summary in long-term tier with metadata.

### Project 2.3: Memory Confidence Decay

**Goal:** Decay long-term facts over time.

**Deliverables:**
- Decay rule
- Revalidation trigger
- Example simulation

**Solution Outline:**
- Add `confidence` to metadata.
- Reduce confidence each day and revalidate below threshold.

---

## Chapter 3: Context Engineering (Projects 7-9)

### Project 3.1: Prompt Template Library

**Goal:** Create 3 reusable prompt templates.

**Deliverables:**
- Template definitions
- Variable validation
- Example renders

**Solution Outline:**
- Use `PromptTemplate` with explicit variables.
- Validate missing variables and fail fast.

### Project 3.2: Token Budget Packer

**Goal:** Pack context to a fixed token budget.

**Deliverables:**
- Budget parameters
- Prioritization rules
- Overflow strategy

**Solution Outline:**
- Use `TokenCounter` to estimate tokens.
- Drop low-priority items first.

### Project 3.3: Chunking Comparison

**Goal:** Compare fixed vs sliding chunks on the same document.

**Deliverables:**
- Chunk counts
- Example output
- Recommendation

**Solution Outline:**
- Use `chunk_fixed` and `chunk_sliding`.
- Compare number of chunks and overlap.

---

## Chapter 4: Observability (Projects 10-12)

### Project 4.1: Structured Logging Baseline

**Goal:** Log each OPRV phase with consistent fields.

**Deliverables:**
- Log schema
- Example logs
- Field list

**Solution Outline:**
- Use `StructuredLogger` with `run_id`.
- Emit log per phase with latency.

### Project 4.2: Tracing Spans

**Goal:** Trace each phase and capture durations.

**Deliverables:**
- Span names
- Timing output
- Example trace

**Solution Outline:**
- Wrap each phase in `Tracer.span()`.
- Export span data to console.

### Project 4.3: Metrics Thresholds

**Goal:** Define alerts for latency and errors.

**Deliverables:**
- Threshold values
- Alert rules
- Example evaluation

**Solution Outline:**
- Use `MetricsCollector.snapshot()` and compare to thresholds.

---

## Chapter 5: Multi-Turn Conversations (Projects 13-15)

### Project 5.1: Slot Filling Agent

**Goal:** Collect required slots for a booking flow.

**Deliverables:**
- Slot list
- Repair prompts
- Completion rule

**Solution Outline:**
- Track slots in memory metadata.
- Ask targeted questions when missing.

### Project 5.2: Conversation Summaries

**Goal:** Summarize long history into a short memory item.

**Deliverables:**
- Summary function
- Example summary
- Token reduction estimate

**Solution Outline:**
- Keep last N turns; summarize older turns.
- Store summary in short-term memory.

### Project 5.3: Conflict Resolution

**Goal:** Handle conflicting user statements gracefully.

**Deliverables:**
- Conflict detection rule
- Clarification prompt
- Resolution policy

**Solution Outline:**
- Detect conflicting values in slot metadata.
- Ask user to confirm the latest value.

---

## Chapter 6: Integration Patterns (Projects 16-18)

### Project 6.1: Tool Contract Definition

**Goal:** Define a tool contract with schema and constraints.

**Deliverables:**
- Input schema
- Output schema
- Constraints and side effects

**Solution Outline:**
- Use `ToolContract` with JSON schema.
- Add constraints like timeout and retries.

### Project 6.2: Tool Registry Validation

**Goal:** Validate inputs before tool execution.

**Deliverables:**
- Validation errors
- Example failing input
- Example passing input

**Solution Outline:**
- Register tools in `ToolRegistry`.
- Call `execute()` with invalid input to test validation.

### Project 6.3: Circuit Breaker Policy

**Goal:** Define a circuit breaker for failing tools.

**Deliverables:**
- Failure thresholds
- Cooldown period
- Recovery behavior

**Solution Outline:**
- Track failure count per tool.
- Open breaker after threshold; retry after cooldown.

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Uses clear headings and short paragraphs
- [ ] Each project includes a solution outline
- [ ] Links to labs or core modules are accurate
- [ ] Language is accessible and consistent
- [ ] Examples are ASCII only

