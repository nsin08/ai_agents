# Complete Glossary

**Scope**: All levels (100+ terms)

---

## Foundations

**Related Chapters**: [Beginner Chapter 1: Environment Setup](../01_beginner/chapter_01_environment_setup.md), [Beginner Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md), [Beginner Chapter 3: RAG Fundamentals](../01_beginner/chapter_03_rag_fundamentals.md)

- **Agent**: An autonomous system that observes, plans, acts, and verifies toward a goal.
- **LLM**: Large language model used for reasoning and generation.
- **Prompt**: Input text that guides model behavior.
- **System prompt**: High-priority instructions that set global behavior.
- **User prompt**: User-provided request or question.
- **Tool**: Callable capability an agent can execute.
- **Tool registry**: Catalog of tools with schemas and execution logic.
- **Tool contract**: Schema describing tool inputs, outputs, and constraints.
- **Memory**: Stored information used to influence responses.
- **Short-term memory**: Recent context kept in a bounded window.
- **Long-term memory**: Durable facts stored across sessions.
- **RAG**: Retrieval-augmented generation from external sources.
- **Embedding**: Vector representation of text for similarity search.
- **Vector store**: Database for embeddings and similarity queries.
- **Chunking**: Splitting documents into smaller pieces for retrieval.
- **Context window**: Maximum input length the model can process.
- **Token**: Unit of text used for model input/output accounting.
- **Token budget**: Allowed total tokens for prompt and response.
- **Temperature**: Sampling parameter controlling randomness.
- **Top-p**: Sampling parameter for nucleus sampling.
- **Max tokens**: Upper bound on model output length.
- **Latency**: Time taken to produce a response.
- **Cost**: Compute or API usage cost per request.
- **Rate limit**: Maximum requests allowed over time.

## Orchestration

**Related Chapters**: [Beginner Chapter 2: Your First Agent](../01_beginner/chapter_02_your_first_agent.md), [Intermediate Chapter 1: Orchestrator Patterns](../02_intermediate/chapter_01_orchestrator_patterns.md)

- **Orchestrator**: Controller that manages the agent loop.
- **OPRV**: Observe, Plan, Act, Verify, Refine loop.
- **State machine**: Controlled transitions between agent phases.
- **Plan**: Proposed next action to reach a goal.
- **Act**: Executing the planned action.
- **Verify**: Checking whether the goal is achieved.
- **Refine**: Adjusting approach after failed verification.
- **ReAct**: Reasoning and acting pattern with explicit steps.
- **Chain-of-thought**: Step-by-step reasoning output.
- **Stop condition**: Rule that ends the loop.
- **Retry**: Re-attempting a failed action.
- **Backoff**: Increasing delay between retries.
- **Timeout**: Maximum time allowed for a step.
- **Circuit breaker**: Stops calls to a failing service.

## Context Engineering

**Related Chapters**: [Intermediate Chapter 3: Context Engineering](../02_intermediate/chapter_03_context_engineering.md)

- **Context packing**: Selecting and ordering context items for a prompt.
- **Overflow strategy**: Policy for handling excessive context.
- **Summarization**: Compressing content into shorter form.
- **Template**: Reusable prompt pattern with variables.
- **Template validation**: Ensuring prompt variables are provided.
- **Context windowing**: Sliding window over conversation history.

## Memory

**Related Chapters**: [Beginner Chapter 5: Memory and Context](../01_beginner/chapter_05_memory_and_context.md), [Intermediate Chapter 2: Advanced Memory](../02_intermediate/chapter_02_advanced_memory.md)

- **Write policy**: Rules controlling what can be stored.
- **Retrieval policy**: Rules controlling what can be retrieved.
- **Memory consolidation**: Summarizing short-term into long-term.
- **Confidence score**: Estimated reliability of a memory item.
- **Decay**: Reducing confidence over time.

## Observability

**Related Chapters**: [Intermediate Chapter 4: Observability](../02_intermediate/chapter_04_observability.md), [Advanced Chapter 5: Monitoring and Alerting](../03_advanced/chapter_05_monitoring_alerting.md)

- **Structured logging**: Logs emitted as key/value records.
- **Tracing**: Time-ordered spans showing execution flow.
- **Span**: Timed segment representing a step.
- **Metrics**: Numeric measurements of system behavior.
- **Counter**: Metric that increments on events.
- **Histogram**: Metric capturing value distributions.
- **Alert**: Notification triggered by a threshold.
- **SLO**: Service level objective.
- **SLA**: Service level agreement.
- **Error budget**: Allowed failure rate over time.
- **Runbook**: Step-by-step incident response guide.
- **Dashboard**: Visualization of metrics and logs.
- **Correlation ID**: Identifier to link related events.

## Safety and Governance

**Related Chapters**: [Advanced Chapter 1: Safety Guardrails](../03_advanced/chapter_01_safety_guardrails.md), [Advanced Chapter 6: Security Best Practices](../03_advanced/chapter_06_security_best_practices.md)

- **Guardrail**: Constraint that prevents unsafe behavior.
- **Prompt injection**: Input intended to override system instructions.
- **Red team**: Adversarial testing for safety.
- **PII**: Personally identifiable information.
- **Data boundary**: Rules for data access and retention.
- **RBAC**: Role-based access control.
- **Allowlist**: Explicitly permitted actions or inputs.
- **Denylist**: Explicitly blocked actions or inputs.
- **Content filter**: Rules to block unsafe outputs.
- **Human-in-the-loop**: Human approval required for actions.

## Evaluation

**Related Chapters**: [Pro Chapter 4: Research Frontiers](../04_pro/chapter_04_research_frontiers.md)

- **Benchmark**: Standardized test set for evaluation.
- **Test suite**: Collection of automated tests.
- **Unit test**: Small test of a single component.
- **Integration test**: Test of components working together.
- **Mock**: Deterministic replacement for external dependencies.
- **Baseline**: Reference performance for comparison.
- **A/B test**: Controlled comparison between variants.
- **Evaluation harness**: Tooling to run standardized evaluations.
- **Scoring**: Method to compute evaluation metrics.
- **Human rating**: Manual assessment by reviewers.
- **Coverage**: Degree to which tests exercise behavior.

## Architecture and Deployment

**Related Chapters**: [Advanced Chapter 2: Multi-Agent Systems](../03_advanced/chapter_02_multi_agent_systems.md), [Advanced Chapter 3: Production Deployment](../03_advanced/chapter_03_production_deployment.md), [Advanced Chapter 4: Scaling Strategies](../03_advanced/chapter_04_scaling_strategies.md)

- **Planner**: Component that decides next steps.
- **Executor**: Component that performs actions.
- **Critic**: Component that evaluates outputs.
- **Router**: Selects tools or models based on context.
- **Multi-agent system**: Multiple specialized agents working together.
- **Coordinator**: Manages collaboration between agents.
- **Message bus**: Asynchronous event transport.
- **Event-driven**: Design where events trigger actions.
- **Webhook**: HTTP callback triggered by events.
- **Canary**: Small rollout to detect issues early.
- **Rollback**: Reverting to a previous version.
- **Scaling**: Handling increased load by adding resources.
- **Load shedding**: Dropping work under overload.
- **Caching**: Storing results to speed up future requests.
- **Async I/O**: Non-blocking operations for concurrency.

## Research

**Related Chapters**: [Pro Chapter 4: Research Frontiers](../04_pro/chapter_04_research_frontiers.md)

- **RLHF**: Reinforcement learning from human feedback.
- **RLAIF**: Reinforcement learning from AI feedback.
- **Prompt tuning**: Optimizing prompts without changing model weights.
- **Fine-tuning**: Training model weights on domain data.
- **Toolformer**: Model that learns to call tools.
- **Reflexion**: Self-reflective prompting for improvement.
- **Tree-of-thoughts**: Branching reasoning search.
- **MetaGPT**: Multi-agent framework for software tasks.
- **AgentBench**: Benchmark for agent capabilities.
- **SWE-bench**: Benchmark for software engineering tasks.

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Includes 100+ terms (current: 108)
- [ ] Terms are grouped by category
- [ ] ASCII only
