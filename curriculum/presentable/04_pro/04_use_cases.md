# Level 4 Use Cases: Pro (What Experts Build With These Patterns)

This file maps Pro curriculum concepts to real-world use cases and recommended patterns.

Each use case includes:
- What it is
- Why it is hard
- Recommended architecture patterns
- Evaluation and safety notes

## Use case 1: Production change assistant (write with approvals)

What it is:
- An agent that proposes and executes controlled changes (feature flags, configs, rollouts).

Why it is hard:
- Writes are high risk.
- Tool failures and retries can cause duplicate changes.
- Auditability is mandatory.

Recommended patterns:
- Graph workflow with interrupts: `chapter_01_advanced_frameworks.md`
- Tool safety runtime: allowlists, idempotency, approvals: `chapter_04_research_frontiers.md`
- Reasoning harness for plan selection: `chapter_02_reasoning_architectures.md`

Evaluation:
- Executable verification: read-after-write checks
- Regression suite for change scenarios

## Use case 2: RAG research assistant (grounded answers with citations)

What it is:
- A knowledge assistant that retrieves from curated corpora and must cite evidence.

Why it is hard:
- Prompt injection via retrieved docs.
- Citation laundering.
- Over-retrieval cost and latency.

Recommended patterns:
- Retrieval gating + citation verification: `chapter_02_reasoning_architectures.md`
- Provenance-first memory: `chapter_03_agentic_design_patterns.md`
- Grounding evaluation: `benchmark_evaluation_framework.md`

Evaluation:
- Citation precision/recall metrics
- Adversarial injection set

## Use case 3: Architecture review copilot (multi-agent, artifact contracts)

What it is:
- A system that reviews designs and produces structured risk analyses.

Why it is hard:
- Hard-to-define correctness (open-ended).
- Needs traceability and evidence.
- Benefits from specialization (security, reliability, cost).

Recommended patterns:
- Manager-worker-verifier: `chapter_03_agentic_design_patterns.md`
- SOPs and artifact contracts: `papers/07_metagpt.md`
- Adoption discipline and benchmarking: `chapter_04_research_frontiers.md`

Evaluation:
- Rubric-based scoring + deterministic checks (required sections, citations format)
- Human spot-checking for calibration

## Use case 4: Incident triage agent (read-only, high throughput)

What it is:
- An agent that reads logs/metrics and proposes likely root causes and next actions.

Why it is hard:
- Unstructured and noisy inputs.
- High variance and high uncertainty.
- Time pressure and high cost of false confidence.

Recommended patterns:
- Bounded loops + uncertainty routing: `chapter_02_reasoning_architectures.md`
- Tool composition pipelines with retries/fallbacks: `chapter_03_agentic_design_patterns.md`
- Observability-first traces: `chapter_01_advanced_frameworks.md`

Evaluation:
- Golden set of incident scenarios
- Stability tests (rerun the same scenario)

## Use case 5: Evaluation platform (agent system CI gate)

What it is:
- A platform that runs benchmarks, produces scorecards, and gates changes.

Why it is hard:
- Requires reproducibility and good metrics.
- Needs stable datasets and versioning.
- Must avoid overfitting and benchmark theater.

Recommended patterns:
- Evaluation as control plane: `chapter_04_research_frontiers.md`
- Benchmark framework: `benchmark_evaluation_framework.md`
- Research synthesis for prioritization: `research_paper_analysis.md`

Evaluation:
- CI smoke suite + nightly/weekly full suite
- Drift detection and alerts

## Use case selection guide (quick)

If the workflow:
- Writes to systems: start with approval interrupts + idempotency + verification.
- Answers knowledge questions: start with retrieval gating + citations + grounding eval.
- Is open-ended: start with artifact contracts + rubrics + human calibration.
- Must scale: start with routing + cost controls + stable traces.

Pro rule:
> Pick the simplest architecture that meets safety and evaluation requirements, then iterate with evidence.

