# Chapter 02: Reasoning Architectures (Chain-of-Thought, Tree-of-Thought, Multimodal Reasoning)

This chapter treats reasoning as a system design problem, not a prompt trick.
At pro level, reasoning quality comes from combining:
- candidate generation (multiple possible answers/plans)
- constraints and verification (rules, tests, schemas, citations)
- budgets (latency, cost, and maximum exploration depth)

## Learning objectives (3-5)

By the end of this chapter, you can:
- Differentiate "single-pass reasoning" (CoT-like) from "search + constraints" (ToT-like) and explain when each is appropriate.
- Design a reasoning harness that generates candidates, scores them, and selects the best safe option.
- Build retrieval-aware reasoning (RAG with gating and citation requirements) and explain how it reduces hallucination.
- Describe multimodal reasoning risks and implement evidence-first patterns (structured extraction, provenance, and verification).
- Define an evaluation plan for reasoning upgrades (accuracy, stability, cost per success, and safety metrics).

## 1. Why "reasoning architecture" matters

In typical LLM usage, "reasoning" is an internal behavior: you send a prompt and get an answer.
In agent systems, reasoning is a workflow component that drives actions:
- choose tools
- generate plans
- decide when to ask clarifying questions
- decide when to escalate or stop

That means reasoning must be:
- bounded (to control cost and time)
- verifiable (to reduce confident errors)
- observable (so you can debug and improve it)

Pro rule:
> If a reasoning upgrade cannot be evaluated and gated, it is not an upgrade. It is risk.

## 2. A taxonomy of reasoning modes

Reasoning modes are not "better/worse". They are trade-offs.

### 2.1 Single-pass reasoning (CoT-like)

Pattern:
- Generate a chain of intermediate steps to reach an answer or plan.

Strengths:
- fast and simple
- often improves performance on multi-step tasks vs direct answering

Weaknesses:
- brittle to prompt changes
- can be confidently wrong
- can produce long outputs that are hard to validate

Practical pro usage:
- Use it to generate internal plans and intermediate artifacts.
- Do not treat the chain as a control signal unless you can parse and validate it.
- Keep user-visible answers short, grounded, and checkable.

Research anchor:
- CoT paper summary: `papers/01_chain_of_thought_prompting.md`

### 2.2 Search-based reasoning (ToT-like)

Pattern:
- Generate multiple candidate steps/solutions.
- Score candidates using a heuristic or judge.
- Expand the best candidates (tree search).

Strengths:
- explores alternatives, reducing "first idea wins" failures
- can outperform single-pass reasoning on harder tasks

Weaknesses:
- higher cost and latency
- quality depends on the scoring function
- can still fail if search explores nonsense branches

Pro usage:
- Use ToT-like search only where it has ROI (high-value or high-risk decisions).
- Bound the search (depth, branching, time).
- Prefer deterministic scoring first; use LLM judges second.

Research anchor:
- ToT paper summary: `papers/03_tree_of_thoughts.md`

### 2.3 Acting + observing (ReAct-like)

Pattern:
- Interleave reasoning with tool calls and observations.

Strengths:
- reduces hallucination by using tools
- creates an observable action trace

Weaknesses:
- requires strict tool boundary enforcement
- tool injection and unsafe tool use become primary risks

Research anchor (optional for this chapter):
- `papers/02_react_reasoning_and_acting.md`

### 2.4 Retrieval-aware reasoning (RAG + critique)

Pattern:
- Decide whether to retrieve.
- Use retrieved evidence in generation.
- Critique outputs against evidence (citations, consistency checks).

Strengths:
- better grounding and factuality
- improved user trust when citations are correct

Weaknesses:
- prompt injection via retrieved content
- citation laundering (citations exist but do not support claims)
- over-retrieval cost and latency

Research anchor:
- Self-RAG paper summary: `papers/10_self_rag.md`

### 2.5 Multimodal reasoning (text + vision + structured data)

Pattern:
- Combine text prompts with images/audio/diagrams/tables.
- Use tools to extract structure when possible.

Strengths:
- enables workflows that interact with real artifacts (documents, UI screenshots, charts)

Weaknesses:
- models can hallucinate visual details
- verification is harder
- privacy/compliance risks increase (images can contain sensitive data)

Pro stance:
- Multimodal reasoning is useful only when you enforce evidence requirements and add extraction/verification steps.

### 2.6 Self-consistency and sampling (useful only with scoring)

Many teams discover an obvious trick:
- "If I sample multiple answers, one of them is usually good."

This is true, but it is not a system.

Self-consistency style approaches rely on:
- generating multiple candidate rationales/answers
- selecting the "most consistent" or "highest scoring" answer

Pro guidance:
- Sampling without scoring is just randomness.
- Sampling with scoring can be a powerful upgrade, especially when:
  - tasks have multiple plausible solutions
  - the model is sensitive to prompt phrasing
  - you can define a deterministic constraint (schema, rule check, test)

Common production pattern:
- Generate 3-5 candidates with low temperature.
- Reject any candidate that violates hard constraints.
- Choose the candidate with the strongest evidence (citations, correct tool use, passes checks).

Measure it:
- If sampling increases cost by 3x but increases success by only 1%, it is not worth it.
- If sampling increases stability and reduces unsafe outputs, it can be worth it even if success rate changes little.

### 2.7 Debate, verifier, and critic architectures

"Debate" and "critic" patterns are popular because they mimic how humans reduce errors:
- one agent proposes
- another agent critiques
- a third agent decides

Pro reality:
- If the verifier has the same blind spots as the proposer, you do not get real verification.
- Critics are most valuable when they check against constraints:
  - retrieved evidence
  - tool outputs
  - schemas and policies
  - executable tests

Better framing:
> Verifiers are not "more models". Verifiers are "more constraints".

Practical pro design:
- Use deterministic verifiers first:
  - schema validators
  - business rule engines
  - citation checkers
- Use LLM critics second:
  - to catch style issues, missing caveats, unclear reasoning
  - to explain failures in human-readable terms

If you do use a judge model as a verifier:
- keep it isolated (it should not execute tools)
- keep it conservative (default to "uncertain" when evidence is weak)
- log its decision and inputs (so you can audit it)

### 2.8 Decomposition: plan-then-execute vs plan-and-solve

Many reasoning failures are really decomposition failures:
- the model attempts to solve the whole problem at once
- it misses constraints (cost, tool limits, permissions)
- it produces an answer that is not actionable

Two common patterns:

Plan-then-execute:
- model produces a plan as a structured artifact
- runtime validates the plan and executes steps with tools
- verification is done after each step (or after critical steps)

Plan-and-solve:
- model reasons and produces the final answer directly
- tools are optional and often underused

Pro rule:
> For any workflow that touches tools or external systems, prefer plan-then-execute.

Why:
- you can validate the plan (structure, tool availability, permissions)
- you can attach budgets to steps
- you can insert interrupts and approvals
- you can measure step-level failures and improve them

### 2.9 Reasoning under context limits (windowing, summarization, and "reasoning debt")

Even with larger context windows, every real system hits context limits:
- tool logs grow
- retrieved documents are long
- multi-turn conversations accumulate

When context overflows, reasoning quality collapses in predictable ways:
- the model forgets constraints (budgets, permissions)
- it repeats earlier steps because it cannot see its own trace
- it produces answers that ignore recent tool outputs

Pro pattern: control context explicitly.

Techniques:
- Windowing: keep only the last N turns and a compact summary of older turns.
- Structured state: store key artifacts (plan, tool results, decisions) as structured fields instead of raw text.
- Summarize with intent: summaries should preserve constraints, decisions, and open questions, not just "what was discussed".
- Keep raw traces out of the prompt: store them externally and include pointers + highlights.

This is a key connection between reasoning and architecture:
> The best reasoning model still fails if you feed it unbounded, noisy context.

## 3. The pro pattern: reasoning as "search + constraints + budgets"

You can implement many reasoning modes with one mental model:

1. Generate candidates (answers, plans, tool calls)
2. Score candidates (constraints and metrics)
3. Select the best safe candidate
4. Execute and observe
5. Verify and stop (or iterate)

This is the reasoning harness.

### 3.1 Candidate generation strategies

Candidates can be generated by:
- the same model with different sampling seeds
- different prompts (specialist prompts)
- different models (small vs large model)
- different tools (retrieve more evidence, run a calculator, query a database)

Pro guidance:
- Use sampling only if you have scoring and selection; otherwise you just add randomness.
- Keep the number of candidates small (3-8) and measure ROI.

### 3.2 Constraints (what to score against)

Constraints are how you turn reasoning into engineering.

Deterministic constraints (preferred):
- schema validity (tool call must validate)
- rule checks (business logic, safety policy)
- retrieval grounding (citations required for knowledge claims)
- unit tests / simulations (executable correctness)

Probabilistic constraints (secondary):
- LLM-as-judge scoring (with calibration)
- heuristic confidence estimates

Pro rule:
> Constraints are not optional. Without constraints, "reasoning" is storytelling.

### 3.3 Budgets (how to keep reasoning safe and affordable)

Budgets are constraints on the reasoning process itself:
- max time
- max tokens
- max tool calls
- max search depth
- max branching factor

Budgets prevent the two most common production failures:
- infinite loops / runaway cost
- slow responses that time out user sessions

### 3.4 Budgets as policies (make them explicit and testable)

Budgets are not just constants; they are policies that encode business constraints.

Examples:
- "Customer support agent must respond in under 10 seconds."
- "This workflow is allowed at most 2 tool calls per request."
- "High-stakes workflow must ask for approval before any write."

Make budgets explicit by attaching them to the workflow state:
- `max_steps`
- `max_tool_calls`
- `max_cost_usd`
- `max_latency_ms`

Then you can test budget enforcement:
- simulate long tool calls and ensure timeouts fire
- simulate repeated failures and ensure retries stop
- ensure budget exceed leads to a safe degradation mode (summary + escalation)

### 3.5 Routing among reasoning modes (a pro lever)

Not every input deserves deep reasoning.

Common routing strategies:
- intent-based routing: lookup vs write vs plan
- uncertainty-based routing: simple when confident, deep when uncertain
- risk-based routing: more verification for higher risk

Example:
- If intent is "calculator": use a tool directly with strict schema validation.
- If intent is "policy question": retrieve and cite.
- If intent is "execute change": plan + verify + approval interrupt.

Routing is where you make the system affordable and safe at scale.

## 4. Implementation patterns with code

These code snippets are framework-agnostic. They show the architecture of a reasoning harness.

### 4.1 A minimal candidate selector (ToT-inspired)

```python
from dataclasses import dataclass
from typing import Callable, List, Tuple


@dataclass(frozen=True)
class Candidate:
    text: str
    metadata: dict


ScoreFn = Callable[[Candidate], float]


def select_best(candidates: List[Candidate], score_fn: ScoreFn) -> Tuple[Candidate, List[Tuple[float, Candidate]]]:
    scored = [(score_fn(c), c) for c in candidates]
    scored.sort(reverse=True, key=lambda t: t[0])
    return scored[0][1], scored
```

What makes this "pro":
- the selection is explicit and testable
- the scored list is an artifact you can log and analyze

### 4.2 Scoring with deterministic constraints first

Example scoring strategy:
- reject invalid candidates with a hard zero
- reward candidates with citations
- penalize candidates that exceed token budget

```python
def score_candidate(candidate: Candidate) -> float:
    if candidate.metadata.get("schema_valid") is False:
        return 0.0
    score = 0.5
    if candidate.metadata.get("has_citations"):
        score += 0.3
    score -= min(candidate.metadata.get("token_cost", 0) / 10_000, 0.2)
    return max(0.0, min(1.0, score))
```

This is intentionally simple, but it demonstrates a key idea:
- scoring is where you encode constraints and trade-offs

### 4.3 Separating internal reasoning from final answers

Pro systems treat internal plans as internal artifacts.

Suggested artifact layout:
- `plan`: internal reasoning text, not shown to the user
- `actions`: typed tool calls
- `evidence`: retrieved snippets with provenance
- `final`: concise answer with citations and checks

This separation reduces leakage risk and improves output quality.

### 4.4 Retrieval gating (no/light/deep)

Retrieval should be a decision, not a default.

Example gating rule (conceptual):
- If the question is factual and time-sensitive, retrieve.
- If the question is about the workflow itself, do not retrieve.
- If the question is ambiguous, ask a clarifying question before retrieving deeply.

Implementation sketch:

```python
from enum import Enum

class RetrievalMode(Enum):
    NONE = "none"
    LIGHT = "light"
    DEEP = "deep"

def choose_retrieval_mode(intent: str, uncertainty: float) -> RetrievalMode:
    if intent in {"factual_lookup", "policy_check"}:
        return RetrievalMode.DEEP if uncertainty > 0.6 else RetrievalMode.LIGHT
    return RetrievalMode.NONE
```

Key pro requirement:
- log retrieval mode decisions, because they affect cost, latency, and injection risk

### 4.5 Multimodal evidence-first pattern

If you accept images or complex documents, prefer:
- extraction step (turn unstructured inputs into structured fields)
- verification step (validate fields and relationships)
- generation step (produce final output based on verified fields)

This pattern is more reliable than "ask the model to look at the image and describe it".

### 4.6 Tool-call planning as structured output

If your agent uses tools, the most important reasoning artifact is often a tool call.
A pro pattern is to force tool calls into a structured schema, even if you generate them with an LLM.

Example schema (conceptual):
- tool name
- arguments
- expected result type
- safety tier (read-only vs write)

Implementation sketch:

```python
from dataclasses import dataclass
from typing import Any, Dict, Literal

SafetyTier = Literal["read_only", "write_requires_approval"]


@dataclass
class PlannedToolCall:
    tool: str
    args: Dict[str, Any]
    safety_tier: SafetyTier
    rationale: str
```

Why include rationale at all?
- Not to "trust the model".
- To help debugging and human review (approvals) when something looks wrong.

### 4.7 Citation checking as a deterministic verifier

If your system claims facts, you need a citation discipline.

Pro pattern:
- The agent produces claims and citations in a machine-checkable format.
- A verifier checks that citations exist and reference known sources.

Implementation sketch (toy):

```python
import re
from typing import List

def extract_citations(text: str) -> List[str]:
    # Example format: [doc:SOURCE_ID]
    return re.findall(r\"\\[doc:([A-Za-z0-9_\\-]+)\\]\", text)

def verify_citations(citations: List[str], allowed_sources: List[str]) -> bool:
    return all(c in allowed_sources for c in citations) and len(citations) > 0
```

In real systems, go further:
- citations should point to doc ids and spans
- the verifier should check that the cited span supports the claim (harder but possible)

### 4.8 Judge-based scoring (when deterministic checks are not enough)

Sometimes you cannot define correctness deterministically:
- writing quality
- helpfulness
- completeness for open-ended tasks

If you use judge models:
- constrain the judge with a rubric
- keep judge prompts versioned
- evaluate judge stability (it can drift)
- never let judge scores override safety constraints

Pro move:
- Combine a judge score with a deterministic "floor":
  - if schema invalid -> fail
  - if unsafe policy violated -> fail
  - else use judge score as a tie-breaker

### 4.9 Case study: reasoning harness for a "risky change request"

Scenario:
- A user asks: "Update the production config to enable feature X."

This request mixes:
- reasoning (what changes are needed?)
- tool use (read config, compute diff, apply change)
- safety (writes to production)
- human control (approval)

A pro reasoning harness might look like:

1. Classify intent and risk
   - intent: "change_request"
   - risk: high (write)
2. Generate candidate plans (3-5)
   - each plan is a structured sequence of steps
3. Validate plans deterministically
   - required tools exist
   - steps are ordered correctly (read before write)
   - approval required before any write
4. Select the best plan
   - prefer plans with fewer steps, clear verification, and rollback
5. Execute with checkpoints
   - after each read, store results
   - before write, interrupt for approval
6. Verify
   - check post-change state with a read tool
   - run a domain validator (if available)
7. Respond
   - final answer includes:
     - what changed
     - verification result
     - trace id and rollback instructions

Why this is a reasoning architecture topic:
- The quality comes from constraints and workflow, not from longer chain-of-thought.
- The selection step reduces "first bad plan wins".
- The verification step prevents confident failure.

Evaluation design for this scenario:
- Create a small golden set of change requests with expected diffs.
- Add adversarial cases:
  - prompt injection in retrieved config files
  - missing tools / permission denied
  - ambiguous request (requires clarifying question)
- Measure:
  - unsafe action blocked rate
  - successful change rate
  - rollback correctness

## 5. Research spotlights (2-3 papers)

This chapter requires current research integration. The paper summaries live in `papers/`.

### 5.1 Chain-of-Thought prompting (baseline reasoning)

Paper: `papers/01_chain_of_thought_prompting.md`

What to take into production:
- Use CoT-like reasoning for planning and decomposition.
- Keep the chain internal and bounded.

What not to do:
- Do not treat free-form reasoning text as executable instructions.
- Do not rely on long reasoning as a proxy for correctness.

### 5.2 Tree of Thoughts (reasoning as search)

Paper: `papers/03_tree_of_thoughts.md`

What to take into production:
- Generate multiple candidates.
- Score candidates with constraints.
- Use bounded search only where ROI exists.

What not to do:
- Do not deploy unbounded search in production paths.
- Do not let the same model both generate and judge without calibration.

### 5.3 Self-RAG (adaptive retrieval + critique)

Paper: `papers/10_self_rag.md`

What to take into production:
- Retrieval gating.
- Citation requirements.
- Critique against evidence, not against vibes.

What not to do:
- Do not accept "citations" that do not support claims.
- Do not store retrieved content as trusted memory without provenance.

## 6. Benchmarking reasoning upgrades (what to measure)

Reasoning architectures can regress silently.
You must measure:
- success rate (overall and by intent)
- hallucination / unsupported claim rate
- citation precision (for knowledge tasks)
- tool-call validity (for tool-driven tasks)
- latency and cost per success
- stability across reruns

Reference:
- `benchmark_evaluation_framework.md`

### 6.1 A practical evaluation strategy

Use a layered approach:
1. Deterministic checks: schema validation, rule engines, executable tests.
2. Golden set: fixed scenarios with expected checks.
3. Adversarial set: injection attempts, malformed inputs.
4. Only then use judge models where necessary.

### 6.2 Stability testing (pro requirement)

If your system behaves differently on the same input, you cannot operate it.

Stability test pattern:
- Run the same benchmark case N times (N=5-20).
- Track:
  - success rate variance
  - tool-call variance (different tools chosen)
  - cost variance

Stability is the fastest way to detect "prompt brittleness".

### 6.3 Responsible use of LLM-as-judge (practical safeguards)

LLM-as-judge is useful but dangerous:
- it can be biased toward certain writing styles
- it can be fooled by confident-sounding nonsense
- it can drift when the judge model changes

Practical safeguards:
- Use a rubric with explicit scoring dimensions (accuracy, citations, safety, completeness).
- Use multiple judgments (N=3) and aggregate to reduce variance.
- Maintain a small human-labeled calibration set and measure judge agreement.
- Log judge inputs/outputs for audit and debugging.

Pro rule:
> Judges can help you rank candidates. Judges should not define safety.

### 6.4 Thresholding and escalation (turn uncertainty into behavior)

Reasoning systems need a policy for uncertainty:
- If confidence low, what happens?

Pro patterns:
- Ask a clarifying question (cheapest).
- Retrieve more evidence (next cheapest).
- Escalate to human review (highest cost, highest safety).
- Stop and explain limitations (when action would be risky).

This is where reasoning meets workflow design:
- uncertainty is not just a score; it becomes a routing decision.

### 6.5 Benchmark design patterns (make evaluation match reality)

Pro-level benchmarks fail when they measure the wrong thing.
Common anti-patterns:
- measuring only "answer quality" when the workflow depends on tools
- using a judge model without calibration or stability checks
- excluding adversarial inputs (the system looks great until it is attacked)

Recommended benchmark mix:
- Golden set:
  - your 20-50 highest-value scenarios
  - stable expected checks (schemas, citations, key facts)
- Adversarial set:
  - prompt injection attempts
  - malformed inputs
  - conflicting sources
- Regression set:
  - previously failing cases that you fixed
  - keep them forever to prevent re-breakage
- Canary set (online):
  - a small subset run regularly in production
  - detect drift and dependency failures early

Your goal is not to build a perfect benchmark. Your goal is to build an improvement loop that keeps you honest.

## 7. Hands-on projects (pro level)

### Project 1: Reasoning harness (candidates + scoring + selection)

Objective:
- Implement a bounded candidate generation and scoring system.

Deliverables:
- Candidate schema (what each candidate includes).
- Scoring function with deterministic constraints.
- Trace output showing scored candidates and selection reason.

Evaluation:
- Demonstrate improved success rate on a hard subset.
- Show cost per success trade-off.

### Project 2: Retrieval gating + citation precision

Objective:
- Implement retrieval mode routing and citation requirements.

Deliverables:
- Retrieval gating logic.
- Citation format (doc id + snippet pointer).
- Metrics for citation precision/recall on a small benchmark set.

Evaluation:
- Show reduced unsupported claim rate with acceptable latency.

### Project 3: Multimodal workflow (evidence-first)

Objective:
- Build a workflow that accepts a document artifact (image or PDF) and produces a verified, structured summary.

Deliverables:
- Extraction step producing structured fields.
- Validation step enforcing invariants.
- Final generation step with references to extracted fields.

Evaluation:
- Demonstrate failure behavior when extraction is uncertain (ask user, escalate, or stop).

## 8. Chapter checklist

Before you move on:
- You can describe reasoning as a harness (generate -> score -> select -> verify).
- You have a bounded search strategy for high-risk cases.
- You have retrieval gating and citation requirements for knowledge tasks.
- You have a benchmark plan that measures success, stability, and cost per success.

### 8.1 Common pitfalls (and how pro teams avoid them)

Pitfall: Treating chain-of-thought as truth
- Symptom: long, confident reasoning that is wrong.
- Mitigation: require evidence (citations, tool outputs) and verify against constraints.

Pitfall: Using ToT-like search everywhere
- Symptom: latency and cost blow up, and results still vary.
- Mitigation: route search to only the intents where it has ROI, and cap depth/branching.

Pitfall: Letting scoring be "vibes"
- Symptom: judge scores do not correlate with user outcomes.
- Mitigation: define deterministic floors (schema validity, policy compliance) and calibrate judges against a small human set.

Pitfall: Over-retrieval
- Symptom: retrieval dominates latency and increases injection risk, with little quality improvement.
- Mitigation: implement retrieval gating (none/light/deep) and measure citation precision and retrieval hit rate.

Pitfall: No uncertainty policy
- Symptom: the system takes risky actions when it is unsure.
- Mitigation: define thresholds and behaviors (clarify, retrieve more, escalate, or stop).

Pitfall: Ignoring context limits
- Symptom: the system forgets constraints or repeats work.
- Mitigation: explicit context windowing, structured state, and external trace storage.

Pro exercise (recommended):
- Pick one workflow you care about (support, ops, research, coding).
- Write down the reasoning harness explicitly:
  - candidates: what alternatives will you generate?
  - constraints: what deterministic checks must every candidate pass?
  - budgets: what limits keep the process safe and affordable?
  - escalation: what happens when uncertainty remains?
- Then create a benchmark set of 20 cases and measure:
  - success rate, stability, and cost per success
  - invalid tool call rate (if tools are involved)
  - citation precision (if retrieval is involved)

If you cannot measure those, you do not yet know whether your reasoning architecture is improving the system.

Optional stretch:
- Add an A/B harness that compares a baseline reasoning mode (single-pass) against a candidate mode (search + scoring).
- Log why the selector chose a candidate (which constraints it satisfied, which evidence it used).
- Run the suite weekly and track trend lines. Reasoning improvements are real only when they persist across model updates, prompt refactors, and dependency changes.

Pro-level reasoning is a loop you can measure: generate options, constrain them, verify against evidence, and ship only what survives your evaluation gates.

## References and further reading

Core papers:
- CoT: https://arxiv.org/abs/2201.11903
- ToT: https://arxiv.org/abs/2305.10601
- Self-RAG: https://arxiv.org/abs/2310.11511

Additional (optional):
- ReAct: https://arxiv.org/abs/2210.03629
