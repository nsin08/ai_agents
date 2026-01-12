# Chapter 03: Agentic Design Patterns (Planning, Tool Composition, Collaboration Frameworks)

This chapter is about repeatable engineering patterns that make agent systems reliable at scale.
You are not learning "tips". You are learning designs that survive:
- tool failures
- model upgrades
- prompt refactors
- new domains and new teams

At pro level, design patterns are the difference between a clever demo and an operable system.

## Learning objectives (3-5)

By the end of this chapter, you can:
- Implement planning patterns (plan-then-execute, bounded refinement, clarifying questions) with explicit artifacts and stop conditions.
- Design tool composition pipelines with contracts, validation, authorization, error handling, and traceability.
- Decide when multi-agent collaboration is warranted and implement role boundaries with artifact contracts and a verifier stage.
- Build a feedback loop that turns failures into improvements (reflections -> constraints -> tests) without creating uncontrolled "agent learning".
- Define evaluation signals for design patterns (tool-call validity, recovery rate, traceability, and cost per success).

## 1. What is a design pattern in agent systems?

In traditional software, a design pattern is a reusable solution to a recurring problem.
In agent systems, the recurring problems are different:
- non-deterministic reasoning (variance)
- actions with side effects (tools)
- untrusted inputs (prompt injection, data exfil)
- long context and memory (drift, contamination)
- hard-to-define correctness (open-ended tasks)

Agentic design patterns are reusable workflow designs that tame these problems.

Pro rule:
> Patterns are not just code structure. Patterns are constraints: what must happen, what must not happen, and what evidence proves it.

## 2. Planning patterns

Planning is the bridge between "goal" and "actions".
A plan is valuable only if:
- it is executable (maps to tools and steps)
- it is constrained (budgets and permissions)
- it is verifiable (you can check progress)

### 2.1 Pattern: plan-then-execute (with a structured plan artifact)

Problem:
- When the model tries to solve everything in one shot, it forgets constraints and produces brittle outputs.

Solution:
- Require a structured plan artifact, validate it, then execute step-by-step.

Example plan schema (conceptual):

```python
from dataclasses import dataclass
from typing import List, Literal, Optional

ActionType = Literal["tool", "ask_user", "think", "verify"]

@dataclass
class PlanStep:
    id: str
    type: ActionType
    description: str
    tool: Optional[str] = None
    depends_on: List[str] = None
    risk: Literal["low", "medium", "high"] = "low"
```

Pro requirements:
- Validate that tool steps reference known tools.
- Enforce that high-risk steps require approvals.
- Ensure each step has a verification method (a check, a tool, or a measurable condition).

### 2.2 Pattern: bounded refinement loop

Problem:
- Agents can loop forever, retrying the same mistake.

Solution:
- Add an explicit refine loop with budgets:
  - max turns
  - max tool calls
  - max cost
  - stop conditions (done/failed/escalate)

Design guidance:
- Refinement must add new information or constraints, not repeat the same prompt.
- Use structured feedback: "what failed", "what to change", "what to verify next".

### 2.3 Pattern: clarifying questions before acting

Problem:
- Ambiguous inputs cause unsafe or incorrect actions.

Solution:
- Add a decision node that asks clarifying questions when:
  - required parameters are missing
  - the intent is unclear
  - the action risk is high

Pro move:
- Treat clarifying questions as a cost-saving strategy, not a UX annoyance.
- Ask the smallest question that resolves the ambiguity.

### 2.4 Pattern: verify-as-you-go planning

Problem:
- Plans drift as execution proceeds; early assumptions become false.

Solution:
- After each significant step, update the plan and verify:
  - "Did we learn something that changes the next step?"
  - "Is the next step still allowed?"

This pattern turns planning into a controlled feedback loop.

### 2.5 Pattern: hierarchical planning (objectives -> tasks -> steps)

Problem:
- Complex goals overwhelm the model and lead to shallow plans ("do everything") or chaotic tool usage.

Solution:
- Use hierarchical planning:
  - Objectives: the business goal, success criteria, and constraints.
  - Tasks: 3-7 major units of work that move the objective forward.
  - Steps: concrete actions mapped to tools, questions, or verifiers.

Practical design:
- Keep each layer small and bounded.
- Force explicit dependencies (what must be true before a step can run?).
- Attach budgets at the task level (max tool calls, max time).

Why it works:
- It reduces cognitive load for the model.
- It gives you better traceability ("which task failed?").
- It makes it easier to insert verification and approvals at the right granularity.

### 2.6 Pattern: plan validation (tool availability, permissions, and budgets)

Plans are untrusted inputs.
Treat a plan like any external request:
- validate it
- reject it if invalid

Plan validation checklist:
- Tool existence: every tool referenced is registered.
- Schema readiness: required parameters are present (or marked as "ask_user").
- Permission readiness: any high-risk step is flagged for approval.
- Budget readiness: plan fits within budget limits (steps, tool calls, time).
- Verification readiness: each step has a check or success signal.

Pro tip:
> If you cannot validate a plan, do not execute it. Ask for clarification or degrade to a safe mode.

### 2.7 Pattern: cost-aware planning (latency and cost as first-class constraints)

At pro level, cost is not an afterthought.
Planning should consider:
- number of tool calls
- expected tool latency
- expected token usage

Simple technique:
- add an "estimate" pass that scores the plan for cost and risk.

```python
def estimate_plan_cost(steps: list[PlanStep]) -> dict:
    tool_calls = sum(1 for s in steps if s.type == "tool")
    high_risk = sum(1 for s in steps if s.risk == "high")
    return {"tool_calls": tool_calls, "high_risk_steps": high_risk}
```

Then you can enforce policies like:
- "If tool_calls > 5, ask user to narrow scope."
- "If any high_risk_steps exist, require approval."

### 2.8 Pattern: plan provenance and auditability

Plans drive actions, so they must be auditable.

Minimum provenance fields to record with a plan:
- goal and inputs
- model and prompt version used to generate the plan
- tool registry version (tool schemas can change)
- approval decisions (who approved what)
- verification outcomes (what proved success)

This is not bureaucracy. It is how you debug incidents and prove compliance.

## 3. Tool composition patterns

Tools are how agents touch reality.
Tool composition is one of the highest-leverage areas in agent engineering.

### 3.1 Pattern: tool contracts (schemas + validation + authorization)

Problem:
- Tool failures and unsafe calls are the most common production incidents for agents.

Solution:
- Define tool contracts with:
  - name and description
  - input schema (validate before execution)
  - output schema (validate when possible)
  - safety tier / permissions

In this repo, see:
- `src/agent_labs/tools/contract.py`
- `src/agent_labs/tools/validators.py`
- `src/agent_labs/tools/registry.py`

Pro rule:
> A tool without a contract is a sharp object. Wrap it or do not ship it.

### 3.2 Pattern: discover -> validate -> execute -> validate -> record

This is the canonical pipeline for tool execution.

```text
Agent -> discover tools -> validate inputs -> authorize -> execute -> validate outputs -> record trace
```

Design notes:
- Discovery: reduce ambiguity by keeping tool names unique and descriptions short.
- Validation: fail fast with actionable errors.
- Authorization: enforce least privilege.
- Execution: timeouts, retries, and idempotency keys for writes.
- Recording: every call produces a trace event (success and failure).

### 3.3 Pattern: small tools beat mega-tools

Problem:
- A single mega-tool with many options becomes hard for the model to call correctly.

Solution:
- Prefer small tools with narrow schemas and clear outputs.

Why:
- easier schema validation
- clearer errors
- easier evaluation (tool-call validity is measurable)
- easier permissions (least privilege)

### 3.4 Pattern: tool chaining with explicit intermediate artifacts

Tool chains are common:
- retrieve docs -> extract fields -> validate -> write result

Pro pattern:
- Store intermediate artifacts explicitly (structured objects), not as raw text.
- Validate between steps.

Example artifact progression:
- `raw_docs` (list of doc ids)
- `extracted_fields` (structured)
- `validated_record` (passes invariants)
- `write_result` (status + id)

### 3.5 Pattern: error handling as workflow, not try/except

Tool failures are expected. Your workflow must define what happens.

Common error handling patterns:
- Retry with backoff (bounded)
- Fallback tool (secondary provider)
- Degradation mode (summary-only)
- Escalation (human review)

Pro rule:
> Every tool must have a failure story: how to detect, how to recover, and how to communicate to the user.

### 3.6 Pattern: idempotency, compensation, and safe writes

If your tools can write (create tickets, change configs, send emails), you must design for:
- duplicate execution (retries, resumes, user double-clicks)
- partial failure (step 3 succeeded, step 4 failed)
- rollback (undo when possible)

Pro requirements for write tools:
- Idempotency keys:
  - the same request id should not apply the same write twice
- Previews:
  - generate a diff or "what will change" preview before execution
- Approvals:
  - high-risk writes require explicit approval
- Post-write verification:
  - read back the system state and confirm the change

Compensation patterns:
- If an action is reversible, define the inverse tool (undo, revert, cancel).
- If it is not reversible, define an escalation workflow (human follow-up).

Design tip:
> Treat every write as a transaction with a trace, not as a side effect hidden in a tool call.

### 3.7 Pattern: tool selection routing (reduce ambiguity)

Tool selection errors often come from ambiguity:
- too many overlapping tools
- vague tool descriptions
- inconsistent naming

Pro strategies:
- Keep tool sets per workflow small (5-15 is a common sweet spot).
- Group tools by capability and expose only what the workflow needs.
- Add a "router" stage that selects tools deterministically when possible (rules first, model second).

Example router rules:
- If input matches a strict pattern (math), use calculator tool directly.
- If intent is lookup, use retrieval tool.
- If intent is write, require a plan + approval.

### 3.8 Pattern: deterministic tests via tool mocking and trace replay

Tool-driven workflows are hard to test if every test hits real services.
Pro teams use mocks and recorded traces.

Approach:
- Unit tests:
  - validate tool schemas and validators
- Integration tests:
  - run tool registry against a local stub server (or a deterministic fake)
- Workflow tests:
  - replay recorded tool outputs to test control flow deterministically

Benefits:
- fast tests in CI
- reproducible failures
- safe testing of write workflows (dry-run + mocked tools)

### 3.9 Pattern: data minimization at tool boundaries

Tools create data flows. Data flows create risk.

Pro rule:
- Only send the minimum necessary data to each tool.

Practical techniques:
- Redact secrets and PII before tool calls.
- Hash or truncate large payloads.
- Log only metadata by default, store full payloads in a restricted store.

### 3.10 Example: a custom tool with a contract (aligned to this repo)

Below is a minimal example of how a tool is shaped in `src/agent_labs/tools/`.
The point is not the business logic; the point is the contract and predictable behavior.

```python
from agent_labs.tools.base import Tool
from agent_labs.tools.contract import ToolContract, ToolResult, ExecutionStatus


class UppercaseTool(Tool):
    name = "uppercase"

    def __init__(self) -> None:
        self.contract = ToolContract(
            name=self.name,
            description="Uppercase a string (deterministic example tool).",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            output_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            tags=["example"],
        )

    async def execute(self, **kwargs) -> ToolResult:
        text = kwargs["text"]
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={"text": text.upper()},
            metadata={"tool_name": self.name},
        )

    def get_schema(self):
        return self.contract.to_dict()
```

Pro notes:
- The tool is deterministic (easy to test).
- The tool validates inputs via the registry (schema).
- The output schema is defined (optional, but valuable for verification).
- Errors should be actionable (the registry already returns structured validation errors).

Then register and execute it via `ToolRegistry`:

```python
from agent_labs.tools.registry import ToolRegistry

registry = ToolRegistry()
registry.register(UppercaseTool())
result = await registry.execute("uppercase", text="hello")
assert result.success
assert result.output == {"text": "HELLO"}
```

## 4. Collaboration patterns (multi-agent frameworks)

Multi-agent systems can raise ceilings:
- specialization (different prompts/tools/skills)
- separation of privileges (a "writer" agent vs a "reader" agent)
- parallelism (multiple research steps)

They also multiply failure modes:
- coordination overhead
- shared context bloat
- contradictory outputs
- blame ambiguity ("which agent caused the failure?")

### 4.1 When to use multi-agent systems

Use multi-agent patterns when:
- tasks require distinct roles with different constraints (planner vs executor vs verifier)
- you need separation of privileges (only one agent can write)
- you can gain parallelism (research in parallel, then merge)

Avoid multi-agent systems when:
- a single agent with tools can solve it reliably
- you do not have strong traces and evals yet
- latency and cost budgets are tight

### 4.2 Pattern: manager-worker-verifier

This is a pro default for collaboration:
- Manager: decomposes and assigns tasks
- Workers: produce candidate outputs (plans, drafts, analyses)
- Verifier: checks against constraints (schemas, evidence, policies)

Why it works:
- reduces "cascading hallucinations" by inserting verification
- creates clear responsibility boundaries
- produces artifacts that can be logged and replayed

### 4.3 Pattern: artifact contracts between agents

The best way to stabilize multi-agent systems is to define artifact contracts:
- required sections for a plan
- schema for a tool call
- rubric for a review

This is what turns "agents chatting" into a workflow.

### 4.4 Pattern: SOPs (standard operating procedures) for collaboration

In complex workflows, you need repeated structure:
- requirements -> design -> implementation -> verification -> release

SOPs encode this structure so the system does not "forget" steps.

This is also how you make multi-agent systems teachable:
- learners can see the pipeline and replicate it

### 4.5 Pattern: structured communication protocols (messages are contracts)

Free-form chat between agents is unstable.
Pro teams treat agent-to-agent messages as contracts:
- required fields
- limited length
- explicit assumptions
- explicit open questions

Example "worker output" contract (conceptual):
- summary (3-5 bullets)
- proposed plan (structured steps)
- risks and unknowns
- evidence (links to retrieved docs or tool outputs)

Why this matters:
- makes the verifier stage more reliable
- reduces context bloat (short, structured messages)
- improves traceability (you can audit what each agent contributed)

### 4.6 Pattern: blackboard / shared state (when message passing is not enough)

In some multi-agent systems, agents need a shared workspace:
- a shared task list
- shared evidence store
- shared intermediate artifacts

This is often called a blackboard pattern.

Pro risks:
- shared state becomes a dumping ground
- conflicts and race conditions appear (two agents overwrite the same field)

Mitigations:
- define ownership rules (only one role can write a field)
- define merge rules (append-only logs, not overwrite)
- store provenance (who wrote what, when, and why)

### 4.7 Pattern: conflict resolution and consensus

Multi-agent systems produce disagreements:
- different plans
- different interpretations of requirements
- conflicting tool recommendations

Pro approach:
- do not "average" outputs
- resolve conflicts via constraints:
  - which plan is valid (tools exist, permissions, budgets)?
  - which plan has stronger evidence?
  - which plan passes verification checks?

If both plans are plausible:
- ask a clarifying question
- or escalate to human review

### 4.8 Specialized domains (why patterns must be tailored)

The same pattern looks different in different domains:

Code agents:
- tools: repo search, edit, run tests
- verification: unit tests and linters
- risk: writes to codebase

Data agents:
- tools: query warehouses, run notebooks
- verification: schema checks, query explain plans, sampling
- risk: leaking sensitive data

Ops agents:
- tools: read logs, change configs, restart services
- verification: health checks and rollout safety
- risk: outages

Pro strategy:
- keep the core patterns (contracts, verification, traces)
- tailor tools, permissions, and verifiers per domain

### 4.9 Case study: multi-agent "design review" workflow

Scenario:
- You want an agentic system that reviews a proposed architecture change.

This is a good multi-agent candidate because it benefits from role separation:
- Researcher: gathers relevant context (docs, prior decisions, constraints).
- Architect: proposes options and trade-offs.
- Reviewer: critiques the plan against constraints and risk posture.
- Verifier: checks that outputs meet a required structure and include evidence.

Workflow shape:
1. Manager collects requirements and defines success criteria (what counts as a good review?).
2. Researcher retrieves relevant sources and summarizes them with provenance.
3. Architect produces 2-3 candidate designs, each with explicit trade-offs and risks.
4. Reviewer critiques each candidate and flags missing considerations.
5. Verifier enforces artifact contracts:
   - required sections present
   - citations included for factual claims
   - high-risk recommendations include approvals/rollback notes
6. Manager produces the final consolidated recommendation and a trace id.

Pro safeguards:
- Do not allow any agent to execute write tools in this workflow.
- Keep messages short and structured; store raw evidence separately.
- Log every role output as an artifact so you can replay and audit the review later.

Evaluation:
- Use a rubric with deterministic checks (presence of risks, presence of rollback, citations format).
- Add a small golden set of known architecture scenarios and compare outputs over time.

## 5. Research spotlights (2-3 papers)

These papers influence modern design patterns for agent systems.

### 5.1 Reflexion (feedback loops)

Paper: `papers/05_reflexion.md`

Key takeaway for pattern design:
- Convert failures into structured feedback and reuse it.
- Do not let "reflection text" grow without constraints.

Pro adoption guidance:
- Store reflection with provenance (input, trace, model version, outcome).
- Translate reflection into constraints (tests, policies, prompt changes).

### 5.2 MetaGPT (role-based collaboration + SOPs)

Paper: `papers/07_metagpt.md`

Key takeaway:
- Multi-agent systems become reliable when roles and SOPs are explicit.

Pro adoption guidance:
- Define role boundaries and permissions.
- Require intermediate artifacts and verifier stages.

### 5.3 Generative Agents (memory + planning + reflection)

Paper: `papers/06_generative_agents.md`

Key takeaway:
- Long-horizon coherence depends on memory architecture and retrieval design.

Pro adoption guidance:
- Treat memory as an index with provenance, not as a chat transcript.
- Use summaries and importance scoring to avoid context collapse.

## 6. Evaluation and benchmarking for design patterns

Design patterns are only valuable if they improve measurable outcomes.
At pro level, you must evaluate:
- tool-call validity and recovery behavior
- traceability (can you explain the decisions?)
- success rate on realistic workflows
- cost per success and latency
- safety metrics (unsafe action blocked, injection resilience)

Reference:
- `benchmark_evaluation_framework.md`

### 6.1 Pattern-level metrics (examples)

Planning patterns:
- plan validity rate (steps reference real tools and required params)
- clarifying question rate (should exist, but not be excessive)
- refinement loop convergence rate (success improves after feedback)

Tool patterns:
- invalid input rate (schema violations)
- tool not found rate
- retry success rate
- output validation pass rate

Collaboration patterns:
- verifier catch rate (how often verifier blocks an invalid output)
- coordination overhead (extra turns/tool calls)
- stability across reruns (variance)

### 6.2 A practical eval workflow for pattern changes

1. Add a small golden set (20-50 cases).
2. Add a regression set (all previously failing cases).
3. Add adversarial cases (injection, malformed inputs).
4. Run the suite on every PR for the affected workflow.
5. Track weekly trend lines.

### 6.3 Observability as evaluation (traces, dashboards, and alerts)

At pro level, evaluation is not only offline benchmarks.
Evaluation also includes online signals:
- tool failure rate spikes
- latency increases
- unsafe blocks increase (may indicate attack attempts or policy regressions)
- escalation rate increases (the system cannot complete tasks)

Design patterns should improve these signals over time.

Minimum observability artifacts:
- trace id per run
- state transitions / node transitions
- tool call logs (name, args hash, latency, status)
- model routing decisions (provider/model/template)

Dashboards to consider:
- success rate by intent
- invalid tool call rate
- retry and fallback frequency
- cost per success

### 6.4 Cost engineering for patterns (measure overhead explicitly)

Patterns add structure, and structure can add cost.
Pro teams measure overhead:
- additional tool calls for verification
- additional tokens for planning and critique
- latency added by multi-agent coordination

You do not need perfect cost models. You need directional truth:
- Does this pattern increase cost by 2x for a 1% success gain?
- Or does it increase cost by 10% for a 20% reduction in unsafe actions?

Make cost a first-class acceptance criterion for pattern adoption.

## 7. Hands-on projects (pro level)

### Project 1: Tool composition pipeline (contracts + tracing)

Objective:
- Build a tool pipeline that is safe and debuggable.

Deliverables:
- 3-5 tools with contracts and validation.
- A registry and executor that logs tool calls and errors.
- A demo query that triggers multiple tool calls and produces a final answer.

Evaluation:
- Contract tests for tools.
- Metrics showing invalid-call rate and recovery behavior.

### Project 2: Manager-worker-verifier collaboration workflow

Objective:
- Implement a role-based collaboration pipeline for a complex task (design review, research synthesis, incident triage).

Deliverables:
- Role definitions with boundaries.
- Artifact contracts for each role output.
- Verifier stage that enforces constraints.
- Trace logs that show each role contribution.

Evaluation:
- Show a failure case that the verifier blocks.
- Measure overhead vs quality improvement.

### Project 3: Structured reflection loop (failure -> constraint -> improvement)

Objective:
- Turn repeated failures into measurable improvements.

Deliverables:
- A reflection schema (failure category, root cause, next constraint).
- A mechanism that converts reflections into a test or a policy rule.
- A before/after benchmark showing reduced repeat failures.

Evaluation:
- Demonstrate at least one "fixed forever" regression case.

## 8. Chapter checklist

Before you move on:
- Your plans are structured artifacts that can be validated.
- Tool execution follows a strict pipeline with contracts and traces.
- Multi-agent collaboration (if used) has role boundaries and verifier stages.
- You have metrics that prove patterns improve outcomes, not just complexity.

### 8.1 Common anti-patterns (what to avoid)

- "One mega-tool for everything"
  - Symptom: the model calls it wrong; debugging becomes impossible.
  - Fix: smaller tools with contracts and clear errors.
- "Multi-agent because it sounds cool"
  - Symptom: higher cost, lower reliability, no one can explain failures.
  - Fix: start with a single workflow; add roles only when constraints demand it.
- "Retry until it works"
  - Symptom: runaway cost and repeated failures.
  - Fix: bounded retries + new information + structured feedback.
- "Memory as a dump"
  - Symptom: drift and contamination; the system becomes more wrong over time.
  - Fix: provenance-first memory with trust levels and expiration.
- "No verifier stage"
  - Symptom: confident, unsafe, or invalid actions make it to execution.
  - Fix: deterministic checks first, then judges if needed.

If you adopt only one idea from this chapter, adopt this:
- Patterns are constraints plus evidence. If you cannot test it and observe it, it is not a production pattern.

### 8.2 Pro exercise: pattern mapping (turn patterns into a backlog)

Pick one workflow you care about and map it to patterns in this chapter:

1. Planning
   - Do you have a structured plan artifact?
   - Do you validate plans before execution?
   - Do you have a bounded refinement loop?
2. Tools
   - Do all tools have contracts and schema validation?
   - Do write tools have idempotency keys and approvals?
   - Do you log tool calls as trace events?
3. Collaboration (optional)
   - If multi-agent, do roles have boundaries and artifact contracts?
   - Is there a verifier stage that can block bad outputs?
4. Evaluation
   - Can you measure tool-call validity and recovery rate?
   - Do you have a regression set of previously failing cases?

Turn the gaps into a backlog:
- 2-3 quick wins (low effort, high safety)
- 1-2 investments (evaluation suite, trace tooling)
- 1 experiment (multi-agent, reflection loop) with clear success metrics

The goal is not to adopt every pattern. The goal is to adopt the smallest set that makes your system reliable and explainable.

Pro systems evolve by tightening constraints and strengthening evidence loops, not by adding more clever prompts. Measure improvements, then simplify ruthlessly.

## References and further reading

Core papers:
- Reflexion: https://arxiv.org/abs/2303.11366
- MetaGPT: https://arxiv.org/abs/2308.00352
- Generative Agents: https://arxiv.org/abs/2304.03442

Additional (optional):
- Toolformer: https://arxiv.org/abs/2302.04761
