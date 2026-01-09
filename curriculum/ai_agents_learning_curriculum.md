# AI Agents Learning Curriculum

**Purpose:** Structured learning path from foundational concepts to production-grade implementations  
**Source Material:** AI Agents Reference Hub (34 documents)  
**Framework:** space_framework SDLC Governance  
**Last Updated:** 2026-01-09

---

## Curriculum Overview

| Level | Focus Area | Chapters | Hands-On Projects | Duration (Est.) |
|-------|------------|----------|-------------------|-----------------|
| **Beginner** | Foundations & Mental Models | 6 | 2 | 2-3 weeks |
| **Intermediate** | Core Components & Integration | 7 | 3 | 4-5 weeks |
| **Advanced** | Production Patterns & Safety | 6 | 3 | 4-5 weeks |
| **Pro** | Domain Specialization & Scale | 6 | 4 | 6-8 weeks |

**Total:** 25 Chapters, 12 Projects

---

# 🟢 LEVEL 1: BEGINNER (Foundations)

**Goal:** Understand what agents are, why they matter, and core mental models.  
**Prerequisites:** Basic programming, familiarity with APIs, conceptual understanding of LLMs.

---

## Chapter B1: Why AI Agents Now?

**Learning Objectives:**
- Explain the limitations of traditional chatbots
- Describe the 4 enabling factors for agentic AI
- Articulate the value proposition for engineering, business, and end users

**Source Material:**
- [01_introduction_motivation.md](../../Agents/01_introduction_motivation.md)

**Key Concepts:**
1. Reactive vs. Proactive AI systems
2. The "Action + Intelligence" gap
3. LLM maturity + tool standardization + memory advances + organizational need
4. Agents as "operational collaborators" not "informative assistants"

**Exercises:**
- [ ] List 5 workflows in your organization that require human orchestration today
- [ ] Classify each as: information-only, single action, or multi-step workflow
- [ ] Identify which could benefit from agentic automation

---

## Chapter B2: What Is an AI Agent? (Core Definition)

**Learning Objectives:**
- Define an AI Agent using precise technical language
- Distinguish agents from chatbots, automation scripts, and simple API wrappers
- Describe the Observe → Plan → Act → Verify → Refine loop

**Source Material:**
- [02_what_is_an_ai_agent.md](../../Agents/02_what_is_an_ai_agent.md)

**Key Concepts:**
1. Agent = LLM inside a control loop
2. Components: Reasoning (LLM), Action (Tools), Memory, Safety, Observability
3. The control loop pattern
4. Autonomy spectrum (fully autonomous → human-in-the-loop)

**Mental Model:**
```
Agent ≠ Better Prompt
Agent = Distributed System with LLM as reasoning component
```

**Exercises:**
- [ ] Draw the control loop for a simple task: "Book a flight"
- [ ] Identify: What observes? What plans? What acts? What verifies?

---

## Chapter B3: What Problems Do Agents Solve?

**Learning Objectives:**
- Enumerate categories of problems agents address
- Understand agent limitations and anti-patterns
- Recognize when NOT to use agents

**Source Material:**
- [03_what_problems_do_agents_solve.md](../../Agents/03_what_problems_do_agents_solve.md)

**Key Concepts:**
1. Multi-step workflow execution
2. Enterprise system integration
3. Real-time data grounding (anti-hallucination)
4. Decision automation with verification
5. Self-healing and retry logic
6. 24/7 autonomous operation

**When NOT to Use Agents:**
- Deterministic logic (if X then Y)
- Latency <100ms required
- Zero error tolerance
- Cost <$0.001/request required
- Fixed workflow with no adaptation

**Exercises:**
- [ ] Take one of your identified workflows from B1
- [ ] List what systems it needs to access
- [ ] Identify potential failure modes
- [ ] Determine if agent approach is appropriate (justify)

---

## Chapter B4: High-Level Architecture (The 6 Pillars)

**Learning Objectives:**
- Draw the 6-pillar agent architecture from memory
- Explain the role of each pillar
- Understand information flow between pillars

**Source Material:**
- [04_high_level_architecture.md](../../Agents/04_high_level_architecture.md)

**The 6 Pillars:**
```
┌─────────────────────────────────────┐
│     1. User Interface               │
└────────────────┬────────────────────┘
                 │
         ┌───────v────────┐
         │  2. Agent      │
         │  Orchestrator  │
         └───────┬────────┘
        ┌────────┼────────┬──────────┐
        │        │        │          │
    ┌───v──┐  ┌─v──┐  ┌─v───┐  ┌──v─────┐
    │3. LLM│  │4.  │  │5.   │  │6.      │
    │Layer │  │Tool│  │Mem- │  │Policies│
    └──────┘  │API │  │ory  │  │Guards  │
              └────┘  └─────┘  └────────┘
                 │
         ┌───────v────────┐
         │ Observability  │
         └────────────────┘
```

**Exercises:**
- [ ] Whiteboard the 6-pillar architecture
- [ ] For each pillar, list 3 responsibilities
- [ ] Trace a request: "Where is my order?" through all pillars

---

## Chapter B5: Evolution of Agent Systems (History & Context)

**Learning Objectives:**
- Trace the 5-phase evolution of LLM applications
- Understand current "best practice" baseline
- Identify where the industry is heading

**Source Material:**
- [09_00_current_trends_and_patterns.md](../../Agents/09_00_current_trends_and_patterns.md)

**5-Phase Evolution:**
1. **Prompted chat** (2022) — Single prompt → response
2. **RAG** (2023) — LLM + knowledge grounding
3. **Tool calling** (2023-24) — LLM selects tools + arguments
4. **Orchestrated agents** (2024) — LLM inside control loop
5. **Agent networks** (2025+) — Multi-agent collaboration

**Exercises:**
- [ ] Classify 3 AI products you use by phase (1-5)
- [ ] Identify what separates Phase 3 (tool calling) from Phase 4 (orchestrated)

---

## Chapter B6: Frameworks Landscape Overview

**Learning Objectives:**
- Understand major agent frameworks (LangChain, LangGraph, etc.)
- Know when to use frameworks vs. custom orchestration
- Recognize framework tradeoffs

**Source Material:**
- [05_01_1_langchain.md](../../Agents/05_01_1_langchain.md)
- [05_01_3_langraph.md](../../Agents/05_01_3_langraph.md)
- [09_01_agent_frameworks_and_multi_agent_systems.md](../../Agents/09_01_agent_frameworks_and_multi_agent_systems.md)

**Framework Decision:**

| Framework | Best For | Limitations |
|-----------|----------|-------------|
| LangChain | Rapid prototyping, RAG-heavy | Hard to debug, abstractions leak |
| LangGraph | Graph workflows, retries | Learning curve, Python-only |
| Custom | Full control, production scale | High engineering cost |

**Rule of thumb:** Start with framework (speed), migrate to custom (control) at scale.

**Exercises:**
- [ ] Install LangChain/LangGraph in a sandbox
- [ ] Build "Hello World" agent that calls one tool
- [ ] Identify 3 things the framework abstracts away

---

## 🧪 BEGINNER PROJECT 1: FAQ Bot with RAG

**Objective:** Build a simple Q&A agent that retrieves answers from a knowledge base.

**Scope:**
- Single LLM (no multi-model)
- One tool: vector search
- No write actions
- Basic observability (print logs)

**Deliverables:**
- Working prototype
- Documentation of architecture decisions
- 10-question test set with expected answers

**Governance (space_framework):**
- Create as Epic with 3-4 Stories
- Each Story has clear acceptance criteria
- PR links to Story

> **💡 See:** [Project P1 Idea Template](#project-p1-idea-template-faq-bot-with-rag) below

---

## 🧪 BEGINNER PROJECT 2: Intent Classification Router

**Objective:** Build a routing layer that classifies user intent and directs to appropriate handler.

**Scope:**
- Small model for classification
- 5 intent categories (e.g., order_status, refund, billing, technical, other)
- Structured JSON output
- Evaluation harness with labeled examples

**Deliverables:**
- Router module with clear interface
- Test set (50+ labeled examples)
- Accuracy report

**Governance:**
- Epic → 3 Stories (router, test harness, evaluation)

> **💡 See:** [Project P2 Idea Template](#project-p2-idea-template-intent-router) below

---

# 🟡 LEVEL 2: INTERMEDIATE (Core Components)

**Goal:** Deep understanding of each agent component and how they integrate.  
**Prerequisites:** Completed Beginner level, familiarity with Python, basic API development.

---

## Chapter I1: The Orchestrator (Control Loop Deep Dive)

**Learning Objectives:**
- Implement the Observe → Plan → Act → Verify → Refine loop
- Handle state management across turns
- Implement error recovery and retry logic
- Enforce loop bounds (max steps, timeout, cost budget)

**Source Material:**
- [05_01_orchestrator_agent_controller.md](../../Agents/05_01_orchestrator_agent_controller.md)
- [05_00_core_components.md](../../Agents/05_00_core_components.md)

**Key Implementation Pattern:**
```python
def orchestrate(request, context):
    state = initialize(request)
    
    while not state.done and state.steps < MAX_STEPS:
        observations = gather_context(state)
        plan = llm.plan(observations)
        validate(plan)
        
        for action in plan.actions:
            if not policies.allow(action):
                return error("Blocked by policy")
            result = execute_tool(action)
            state.add_result(result)
        
        if state.has_errors():
            state = recover(state)
        else:
            state.mark_progress()
    
    return finalize(state)
```

**Exercises:**
- [ ] Implement a minimal orchestrator (no framework)
- [ ] Add step counting and timeout enforcement
- [ ] Add error recovery with exponential backoff

---

## Chapter I2: LLM Selection & Multi-Model Routing

**Learning Objectives:**
- Understand single vs. multi-LLM architectures
- Implement model routing based on task complexity
- Configure reasoning modes (standard vs. extended)
- Calculate cost tradeoffs

**Source Material:**
- [05_02_llms_and_reasoning_modes.md](../../Agents/05_02_llms_and_reasoning_modes.md)

**Multi-LLM Pattern:**
```
User Request
     │
     ├─→ Router LLM (small, fast, cheap)
     │   └─→ Classify: easy/medium/hard
     │
     ├─→ Easy → Executor LLM (mid-tier)
     ├─→ Medium → Planner LLM (strong) → Executor
     └─→ Hard → Planner (extended reasoning) → Executor → Critic
```

**Cost Model:**
- Router: ~$0.0001/call
- Executor: ~$0.005/call
- Planner: ~$0.01/call
- Extended reasoning: ~$0.05/call

**Exercises:**
- [ ] Implement a complexity classifier
- [ ] Route requests to appropriate model tier
- [ ] Track cost per request

---

## Chapter I3: Tools & API Integration

**Learning Objectives:**
- Design tool contracts (schema, permissions, side effects)
- Implement tool validation and execution
- Handle tool errors gracefully
- Build a tool registry

**Source Material:**
- [05_03_tools_and_apis_agent.md](../../Agents/05_03_tools_and_apis_agent.md)
- [09_02_tool_use_computer_control_autonomous_workflows.md](../../Agents/09_02_tool_use_computer_control_autonomous_workflows.md)

**Tool Contract Pattern:**
```json
{
  "name": "get_order_status",
  "description": "Retrieve order details from Order Service",
  "input_schema": {
    "type": "object",
    "properties": {
      "order_id": {"type": "string"}
    },
    "required": ["order_id"]
  },
  "output_schema": {...},
  "permissions": ["orders_read"],
  "side_effects": "none",
  "rate_limit": "100/min"
}
```

**Exercises:**
- [ ] Design contracts for 5 tools (3 read, 2 write)
- [ ] Implement tool registry with validation
- [ ] Add permission checking before execution

---

## Chapter I4: Memory Systems (Short-Term, Long-Term, RAG)

**Learning Objectives:**
- Implement session memory (conversation context)
- Design safe long-term memory policies
- Integrate RAG for knowledge grounding
- Choose between RAG vs. long context

**Source Material:**
- [05_04_0_memory_and_rag.md](../../Agents/05_04_0_memory_and_rag.md)
- [05_04_1_context_engineering.md](../../Agents/05_04_1_context_engineering.md)
- [05_04_2_memory_write_policy.md](../../Agents/05_04_2_memory_write_policy.md)
- [05_04_3_memory_retrieval_policy.md](../../Agents/05_04_3_memory_retrieval_policy.md)

**Memory Types:**
1. **Short-term:** Conversation history, task state (session-bound)
2. **Long-term:** User preferences, past interactions (persistent, requires safe write policy)
3. **Knowledge (RAG):** Organizational docs, policies (retrieved on demand)

**RAG vs Long Context Decision:**

| Use RAG When | Use Long Context When |
|--------------|----------------------|
| Large persistent knowledge base | Task input is large but temporary |
| Content changes frequently | Sequential reasoning over whole text |
| Citations matter | Must reason end-to-end |
| Low token cost at scale | One large input |

**Exercises:**
- [ ] Implement session memory with sliding window
- [ ] Build RAG retrieval with metadata filtering
- [ ] Define write policy: when to persist to long-term memory

---

## Chapter I5: Context Engineering

**Learning Objectives:**
- Structure prompts for agent tasks
- Manage context window efficiently
- Implement context pruning strategies
- Balance precision vs. context size

**Source Material:**
- [05_04_1_context_engineering.md](../../Agents/05_04_1_context_engineering.md)

**Context Composition:**
```
[System Prompt: Role, constraints, output format]
[Retrieved Knowledge: Top-K RAG results]
[Conversation History: Last N turns]
[Current Task State: Steps completed, pending]
[Available Tools: Schemas for current context]
[User Message: Current request]
```

**Pruning Strategies:**
- Summarize old conversation turns
- Filter RAG by relevance threshold
- Omit tool schemas not relevant to task
- Compress tool results to essential fields

**Exercises:**
- [ ] Calculate token budget for each context section
- [ ] Implement summarization for conversation history
- [ ] Add relevance-based RAG filtering

---

## Chapter I6: Policies & Guardrails

**Learning Objectives:**
- Implement safety tiers (0-3)
- Build permission systems (RBAC/ABAC)
- Add confirmation gates for write actions
- Enforce cost and step budgets

**Source Material:**
- [05_05_policies_and_guardrails.md](../../Agents/05_05_policies_and_guardrails.md)

**Safety Tiers:**
- **Tier 0 (Informational):** Read-only Q&A → minimal guardrails
- **Tier 1 (Operational Read):** Query systems → allow reads, block writes
- **Tier 2 (Limited Write):** Update non-critical → confirmation gate
- **Tier 3 (High-Stakes):** Finance, HR, security → human approval mandatory

**Exercises:**
- [ ] Implement RBAC for tool access
- [ ] Add confirmation gate for write tools
- [ ] Enforce max cost per request

---

## Chapter I7: Observability (Logging, Metrics, Tracing)

**Learning Objectives:**
- Implement structured logging
- Add distributed tracing (OpenTelemetry)
- Track costs and latency
- Build debugging dashboards

**Source Material:**
- [05_06_observability_logging_metrics_tracing.md](../../Agents/05_06_observability_logging_metrics_tracing.md)

**Observability Stack:**
```
Structured Logging → Trace ID, step, action, result, latency, cost
Distributed Tracing → Request → Plan → Tool calls → Verify → Response
Metrics → Success rate, latency P50/P95/P99, cost/request, error rate
Alerts → Cost spike, error rate threshold, latency degradation
```

**Exercises:**
- [ ] Add structured JSON logging
- [ ] Implement request-level cost tracking
- [ ] Create simple metrics dashboard

---

## 🧪 INTERMEDIATE PROJECT 3: Customer Support Agent (Read-Only)

**Objective:** Build a support agent that answers questions using tools (no write actions).

**Scope:**
- Multi-LLM (router + executor)
- 3 tools: order_lookup, policy_search, faq_search
- Session memory
- RAG for policies
- Structured logging

**Deliverables:**
- Working agent with 3 tools
- 50-case evaluation set
- Latency and cost tracking

**Governance:**
- Epic with 5-6 Stories
- Safety tier: Tier 1 (read-only)

> **💡 See:** [Project P3 Idea Template](#project-p3-idea-template-support-agent-read-only) below

---

## 🧪 INTERMEDIATE PROJECT 4: Multi-Tool Orchestrator

**Objective:** Build an orchestrator that chains multiple tools to complete a task.

**Scope:**
- 5 tools with dependencies (tool B needs output from tool A)
- Error handling and retry
- Step budget enforcement
- Parallel execution where possible

**Deliverables:**
- Orchestrator with dependency resolution
- Error recovery patterns implemented
- Performance benchmarks

**Governance:**
- Epic with 4 Stories

> **💡 See:** [Project P4 Idea Template](#project-p4-idea-template-multi-tool-orchestrator) below

---

## 🧪 INTERMEDIATE PROJECT 5: RAG Pipeline with Evaluation

**Objective:** Build a production-quality RAG pipeline with evaluation harness.

**Scope:**
- Document ingestion (chunking, embedding)
- Metadata filtering + reranking
- Golden test set (50+ questions)
- Evaluation metrics (recall, precision, answer quality)

**Deliverables:**
- RAG pipeline with reranking
- Evaluation framework
- Baseline metrics report

**Governance:**
- Epic with 4 Stories

> **💡 See:** [Project P5 Idea Template](#project-p5-idea-template-rag-with-evaluation) below

---

# 🟠 LEVEL 3: ADVANCED (Production Patterns)

**Goal:** Build production-ready agents with safety, testing, and operational excellence.  
**Prerequisites:** Completed Intermediate level, experience with production systems.

---

## Chapter A1: Design Decision Trees

**Learning Objectives:**
- Apply decision frameworks for architecture choices
- Balance latency, cost, and accuracy tradeoffs
- Make context-appropriate decisions (not dogmatic)

**Source Material:**
- [06_design_decision_tree.md](../../Agents/06_design_decision_tree.md)
- [07_design_decision_tree.md](../../Agents/07_design_decision_tree.md)

**Key Decisions:**
1. Single LLM vs. Multi-LLM
2. RAG vs. Long Context
3. Autonomous vs. Gated Execution
4. Tool vs. Internal Code
5. Long-Term Memory Policy
6. Latency vs. Cost vs. Accuracy tradeoffs

**Exercises:**
- [ ] For a given use case, walk through all 6 decisions
- [ ] Justify each choice with specific constraints
- [ ] Identify what would change the decision

---

## Chapter A2: Failure Modes & Recovery Patterns

**Learning Objectives:**
- Catalog common agent failure modes
- Implement recovery strategies
- Handle partial completion
- Build checkpoint/resume capability

**Key Failure Modes:**
1. **Tool cascade failures** — Tool A fails → dependent tools B, C cannot proceed
2. **Context window overflow** — Memory + plan + tools exceed max tokens
3. **LLM non-determinism** — Same prompt yields different plans
4. **Partial success** — Agent completes 3/5 steps, then fails
5. **Infinite retry loops** — Agent retries same failing tool endlessly

**Recovery Patterns:**
- Tool timeout → Fallback tool or cached result
- LLM hallucination → Verification catches it → Retry with constraints
- Context overflow → Summarize + prune
- Partial completion → Checkpoint state → Resume later

**Exercises:**
- [ ] Implement graceful degradation for tool failure
- [ ] Add context pruning when approaching token limit
- [ ] Build checkpoint/resume for long workflows

---

## Chapter A3: Testing & Evaluation Framework

**Learning Objectives:**
- Build unit tests for agent components
- Create integration test harnesses
- Implement regression testing
- Design adversarial tests

**Testing Layers:**
```
Unit Tests
├─ Mock LLM responses
├─ Mock tool outputs
└─ Verify orchestrator logic

Integration Tests
├─ Golden test sets (input → expected output)
├─ End-to-end workflow validation
└─ Multi-turn conversation tests

Regression Tests
├─ Version model + tools
├─ Detect behavior drift
└─ Baseline comparison

Adversarial Tests
├─ Prompt injection attempts
├─ Tool misuse patterns
└─ Boundary violations
```

**Evaluation Metrics:**
- Task success rate
- Tool call accuracy
- Hallucination rate
- Cost per task
- Latency (P50, P95, P99)

**Exercises:**
- [ ] Build golden test set (50+ cases)
- [ ] Implement mock-based unit testing
- [ ] Create adversarial test suite

---

## Chapter A4: Security & Compliance

**Learning Objectives:**
- Defend against prompt injection
- Prevent data exfiltration
- Implement audit logging
- Address GDPR/HIPAA requirements

**Security Checklist:**
```
✅ Input Security
- [ ] Sanitize user inputs (block injection patterns)
- [ ] Validate all tool arguments
- [ ] Rate limit per user/tenant

✅ Output Security
- [ ] Redact PII in responses
- [ ] Filter sensitive data
- [ ] Never log raw LLM outputs with user data

✅ Tool Security
- [ ] Allowlist tools (no dynamic loading)
- [ ] Secrets via secure vault
- [ ] Audit all tool calls

✅ Memory Security
- [ ] Encrypt long-term memory at rest
- [ ] Partition memory by tenant
- [ ] Implement right-to-delete (GDPR)
```

**Exercises:**
- [ ] Implement input sanitization
- [ ] Add PII redaction to responses
- [ ] Build audit log with tenant isolation

---

## Chapter A5: Human-in-the-Loop Patterns

**Learning Objectives:**
- Design approval workflows
- Implement async approval handling
- Build escalation triggers
- Create handoff protocols

**Patterns:**
1. **Synchronous approval** — Agent waits for user confirmation
2. **Asynchronous approval** — Agent submits plan, user approves later, agent resumes
3. **Smart escalation** — Agent detects low confidence → escalates proactively
4. **Handoff context** — Agent provides full trace to human

**Exercises:**
- [ ] Implement confirmation gate with timeout
- [ ] Build async approval queue
- [ ] Create escalation rules based on confidence score

---

## Chapter A6: Scalability & Performance

**Learning Objectives:**
- Design for horizontal scalability
- Implement caching strategies
- Optimize latency
- Handle high concurrency

**Source Material:**
- [08_scalability_and_performance.md](../../Agents/08_scalability_and_performance.md)

**Optimization Techniques:**
- **Streaming:** Return partial results while agent works
- **Parallel tools:** Independent tools run concurrently
- **Prompt caching:** Cache static system prompts
- **Result caching:** Cache stable reads with TTL
- **Async pattern:** Fire slow tools, continue with fast, merge

**Exercises:**
- [ ] Implement response streaming
- [ ] Add parallel tool execution
- [ ] Build result caching with TTL

---

## 🧪 ADVANCED PROJECT 6: Support Agent with Write Actions

**Objective:** Extend Project 3 to include write actions with safety gates.

**Scope:**
- Add write tools: initiate_refund, update_address, create_ticket
- Confirmation gates for all writes
- Audit logging
- Human escalation path

**Deliverables:**
- Agent with read + write tools
- Safety gate implementation
- Audit log system
- Escalation workflow

**Governance:**
- Epic with 6 Stories
- Safety tier: Tier 2 (limited write with confirmation)

> **💡 See:** [Project P6 Idea Template](#project-p6-idea-template-support-agent-with-writes) below

---

## 🧪 ADVANCED PROJECT 7: Testing & Evaluation Harness

**Objective:** Build a comprehensive testing framework for agents.

**Scope:**
- Unit test framework with mocks
- Golden test set (100+ cases)
- Regression testing pipeline
- Adversarial test suite
- Metrics dashboard

**Deliverables:**
- Testing framework
- Golden test dataset
- CI/CD integration
- Metrics dashboard

**Governance:**
- Epic with 5 Stories

> **💡 See:** [Project P7 Idea Template](#project-p7-idea-template-testing-harness) below

---

## 🧪 ADVANCED PROJECT 8: Multi-Tenant Agent Platform

**Objective:** Build agent infrastructure that supports multiple tenants securely.

**Scope:**
- Tenant isolation (data, memory, logs)
- Per-tenant rate limiting and cost caps
- Tenant-specific configurations
- Audit separation

**Deliverables:**
- Multi-tenant architecture
- Isolation verification tests
- Admin dashboard per tenant

**Governance:**
- Epic with 5 Stories
- Security review required

> **💡 See:** [Project P8 Idea Template](#project-p8-idea-template-multi-tenant-platform) below

---

# 🔴 LEVEL 4: PRO (Domain Specialization)

**Goal:** Build domain-specific production agents with full operational maturity.  
**Prerequisites:** Completed Advanced level, domain expertise in target area.

---

## Chapter P1: Case Study Deep Dive — Customer Support

**Learning Objectives:**
- Analyze production support agent architecture
- Understand domain-specific constraints
- Apply patterns to real deployment

**Source Material:**
- [09_04_case_study_customer_support_agent.md](../../Agents/09_04_case_study_customer_support_agent.md)
- [12_01_customer_support_agent_architecture.md](../../Agents/12_01_customer_support_agent_architecture.md)

**Key Patterns:**
- Multi-source data (structured + unstructured)
- Policy grounding via RAG
- Autonomy tiers by action type
- PII handling and compliance

---

## Chapter P2: Case Study Deep Dive — Coding Agent

**Learning Objectives:**
- Understand code generation agent architecture
- Handle code execution safely
- Integrate with development tools (git, CI/CD)

**Source Material:**
- [12_04_coding_agent_architecture.md](../../Agents/12_04_coding_agent_architecture.md)

**Key Patterns:**
- Code interpreter sandboxing
- Test execution and verification
- Version control integration
- Multi-file context handling

---

## Chapter P3: Case Study Deep Dive — Medical Agent

**Learning Objectives:**
- Design for high-stakes domains
- Implement mandatory human approval
- Address regulatory compliance (HIPAA)
- Build audit trails

**Source Material:**
- [12_05_medical_agent_architecture.md](../../Agents/12_05_medical_agent_architecture.md)

**Key Patterns:**
- Safety tier 3 (mandatory human approval)
- No autonomous treatment decisions
- Comprehensive audit logging
- Data residency requirements

---

## Chapter P4: Case Study Deep Dive — DevOps Troubleshooting

**Learning Objectives:**
- Build diagnostic agents
- Integrate with monitoring systems
- Implement safe remediation
- Handle on-call workflows

**Source Material:**
- [12_06_ops_troubleshooting_agent_architecture.md](../../Agents/12_06_ops_troubleshooting_agent_architecture.md)

**Key Patterns:**
- Log and metrics retrieval tools
- Read-only diagnostics by default
- Remediation with approval gates
- Runbook integration

---

## Chapter P5: Deployment Models & Operations

**Learning Objectives:**
- Choose between self-managed vs. agent-as-a-service
- Implement versioning and rollback
- Design blue-green/canary deployments
- Build operational runbooks

**Source Material:**
- [11_self_managed_vs_agent_as_a_service.md](../../Agents/11_self_managed_vs_agent_as_a_service.md)

**Deployment Decision:**

| Self-Managed | Agent-as-a-Service |
|--------------|-------------------|
| Full control | Turn-key solution |
| Data sovereignty | Vendor manages ops |
| Custom integrations | Faster deployment |
| Higher ops burden | Less customization |

**Trend:** Hybrid — self-managed orchestrator + vendor LLMs/tools

---

## Chapter P6: Future Directions & Emerging Patterns

**Learning Objectives:**
- Understand emerging trends
- Evaluate new patterns and frameworks
- Plan for future capabilities

**Source Material:**
- [10_conclusion_future_directions.md](../../Agents/10_conclusion_future_directions.md)
- [09_01_agent_frameworks_and_multi_agent_systems.md](../../Agents/09_01_agent_frameworks_and_multi_agent_systems.md)
- [09_03_retrieval_tools_planning_modern_stack.md](../../Agents/09_03_retrieval_tools_planning_modern_stack.md)

**Emerging Patterns:**
- Self-improving agents
- Agent marketplaces
- Cross-platform agents
- Federated agents
- Agentic workflows in IDEs

---

## 🧪 PRO PROJECT 9: Domain-Specific Production Agent

**Objective:** Build a production-ready agent for a specific domain (choose one):
- Customer Support
- Travel Booking
- Code Assistant
- DevOps Troubleshooting

**Scope:**
- Full 6-pillar architecture
- Multi-LLM routing
- 10+ tools (read + write)
- Safety tiers appropriate to domain
- Comprehensive observability
- Evaluation pipeline
- Deployment strategy

**Deliverables:**
- Production-ready agent
- Documentation (architecture, runbooks)
- Evaluation results
- Deployment manifests

**Governance:**
- Multiple Epics, each with Stories
- Full Definition of Done compliance
- CODEOWNER approval required

> **💡 See:** [Project P9 Idea Template](#project-p9-idea-template-domain-production-agent) below

---

## 🧪 PRO PROJECT 10: Agent Evaluation Platform

**Objective:** Build a platform for continuous agent evaluation and monitoring.

**Scope:**
- Golden test management
- Automated regression testing
- A/B testing infrastructure
- Drift detection
- Evaluation dashboards

**Deliverables:**
- Evaluation platform
- Integration with agent deployments
- Dashboard with key metrics
- Alerting for regressions

**Governance:**
- Epic with 6 Stories

> **💡 See:** [Project P10 Idea Template](#project-p10-idea-template-evaluation-platform) below

---

## 🧪 PRO PROJECT 11: Cost Engineering & Optimization

**Objective:** Build cost tracking, attribution, and optimization for agents.

**Scope:**
- Per-request cost tracking (model + tools)
- Cost attribution by tenant/user
- Optimization patterns (caching, routing)
- Budget enforcement
- Cost dashboards and alerts

**Deliverables:**
- Cost tracking system
- Attribution reports
- Optimization recommendations
- Budget controls

**Governance:**
- Epic with 4 Stories

> **💡 See:** [Project P11 Idea Template](#project-p11-idea-template-cost-engineering) below

---

## 🧪 PRO PROJECT 12: Multi-Agent System

**Objective:** Build a system where multiple specialized agents collaborate.

**Scope:**
- 3+ specialized agents (e.g., researcher, planner, executor)
- Agent-to-agent communication protocol
- Coordinator/supervisor pattern
- Shared state management
- Failure handling across agents

**Deliverables:**
- Multi-agent system
- Communication protocol
- Coordinator implementation
- End-to-end workflow demo

**Governance:**
- Multiple Epics
- Architecture review required

> **💡 See:** [Project P12 Idea Template](#project-p12-idea-template-multi-agent-system) below

---

# 📋 PROJECT IDEA TEMPLATES

All projects follow the space_framework Idea template format for governance integration.

---

## Project P1 Idea Template: FAQ Bot with RAG

```markdown
# Idea: FAQ Bot with RAG Grounding

## Business Need
Build a simple Q&A agent that answers user questions using a knowledge base,
demonstrating core RAG patterns and basic agent architecture.

## Success Criteria
- [ ] Agent correctly answers 80%+ of test questions
- [ ] Answers are grounded in retrieved documents (citations provided)
- [ ] Latency <3 seconds per response
- [ ] Basic logging captures all requests and responses

## Scope
### In Scope
- Single LLM architecture
- Vector store for document embeddings
- One tool: knowledge_search
- Session memory (no persistence)
- Structured logging

### Out of Scope
- Write actions
- Multi-LLM routing
- Long-term memory
- Production deployment

## Stakeholders
- Role: Client — Defines FAQ content domain
- Role: Architect — Reviews design decisions
- Role: Implementer — Builds the agent

## Constraints
- Safety Tier: 0 (informational only)
- Budget: Prototype level (~$10 LLM costs)
- Timeline: 1 week

## Proposed Approach
1. Ingest FAQ documents into vector store
2. Implement basic retrieval with top-K
3. Build simple orchestrator with single LLM
4. Add structured logging
5. Create 10-question test set
6. Evaluate and document

## Exit Criteria for Idea → Approved
- [ ] FAQ content identified
- [ ] Vector store solution selected
- [ ] LLM provider selected
- [ ] Success criteria accepted by stakeholders
```

---

## Project P2 Idea Template: Intent Router

```markdown
# Idea: Intent Classification Router

## Business Need
Build a routing layer that classifies user intent to enable efficient request handling
and demonstrate multi-model routing patterns.

## Success Criteria
- [ ] Router achieves 90%+ accuracy on labeled test set
- [ ] Classification latency <500ms
- [ ] Structured JSON output for downstream processing
- [ ] 50+ labeled examples in evaluation set

## Scope
### In Scope
- Small classification model
- 5 intent categories
- Structured output schema
- Evaluation harness
- Accuracy reporting

### Out of Scope
- Downstream handlers (just classification)
- Write actions
- Memory
- Production deployment

## Stakeholders
- Role: Architect — Defines intent taxonomy
- Role: Implementer — Builds classifier

## Constraints
- Safety Tier: 0
- Budget: Prototype level
- Timeline: 1 week

## Proposed Approach
1. Define 5 intent categories with examples
2. Create labeled dataset (50+ examples)
3. Implement classification with structured output
4. Build evaluation harness
5. Tune for accuracy
6. Document results

## Exit Criteria for Idea → Approved
- [ ] Intent taxonomy defined
- [ ] Example dataset created
- [ ] Model approach selected
```

---

## Project P3 Idea Template: Support Agent (Read-Only)

```markdown
# Idea: Customer Support Agent (Read-Only)

## Business Need
Build a support agent that answers customer questions using real system data
while maintaining strict read-only safety constraints.

## Success Criteria
- [ ] Agent resolves 70%+ of test tickets correctly
- [ ] All answers grounded in tool outputs or RAG
- [ ] Zero write actions executed
- [ ] Cost <$0.10 per resolved ticket
- [ ] Latency <5 seconds

## Scope
### In Scope
- Multi-LLM (router + executor)
- 3 tools: order_lookup, policy_search, faq_search
- Session memory
- RAG for policies
- Structured logging with cost tracking
- 50-case evaluation set

### Out of Scope
- Write actions (refunds, updates)
- Human escalation workflows
- Production deployment

## Stakeholders
- Role: Client — Defines support scenarios
- Role: Architect — Reviews tool contracts
- Role: Implementer — Builds agent
- Role: Reviewer — Validates safety constraints

## Constraints
- Safety Tier: 1 (read-only)
- Budget: ~$50 for evaluation
- Timeline: 3 weeks

## Proposed Approach
1. Design tool contracts for 3 tools
2. Implement multi-LLM routing
3. Build RAG for policy documents
4. Develop orchestrator with session memory
5. Add observability (logs, costs)
6. Create 50-case evaluation set
7. Evaluate and iterate

## Exit Criteria for Idea → Approved
- [ ] Tool contracts reviewed
- [ ] Policy documents identified
- [ ] Test scenarios defined
- [ ] Safety tier confirmed (Tier 1)
```

---

## Project P4 Idea Template: Multi-Tool Orchestrator

```markdown
# Idea: Multi-Tool Orchestrator with Dependencies

## Business Need
Build an orchestrator that can chain multiple tools with dependencies,
demonstrating complex workflow execution patterns.

## Success Criteria
- [ ] Successfully chains 5 tools with dependencies
- [ ] Handles tool failures gracefully
- [ ] Respects step budget (max 10 steps)
- [ ] Parallel execution where possible
- [ ] Performance benchmarks documented

## Scope
### In Scope
- 5 tools with defined dependencies
- Dependency resolution logic
- Error handling and retry
- Step budget enforcement
- Parallel execution engine
- Performance benchmarking

### Out of Scope
- Real external systems (mock tools)
- Production deployment
- Multi-tenant

## Constraints
- Budget: Prototype level
- Timeline: 2 weeks

## Proposed Approach
1. Design 5 tools with clear dependencies
2. Build dependency graph resolver
3. Implement parallel execution engine
4. Add retry logic with exponential backoff
5. Enforce step budget
6. Benchmark performance

## Exit Criteria for Idea → Approved
- [ ] Tool dependencies mapped
- [ ] Failure scenarios defined
- [ ] Performance targets set
```

---

## Project P5 Idea Template: RAG with Evaluation

```markdown
# Idea: Production RAG Pipeline with Evaluation

## Business Need
Build a RAG pipeline with metadata filtering, reranking, and comprehensive
evaluation to ensure retrieval quality meets production standards.

## Success Criteria
- [ ] Recall >90% on golden test set
- [ ] Precision >80% at top-5
- [ ] Reranking improves precision by 10%+
- [ ] Evaluation framework runs automatically
- [ ] Baseline metrics documented

## Scope
### In Scope
- Document ingestion with chunking
- Embedding generation
- Metadata filtering
- Reranking (cross-encoder)
- 50+ question golden test set
- Evaluation metrics pipeline

### Out of Scope
- Agent integration
- Production deployment
- Real-time updates

## Constraints
- Budget: ~$20 for embeddings and evaluation
- Timeline: 2 weeks

## Proposed Approach
1. Design chunking strategy
2. Ingest documents with metadata
3. Implement retrieval with filtering
4. Add reranking step
5. Create golden test set
6. Build evaluation pipeline
7. Document baseline metrics

## Exit Criteria for Idea → Approved
- [ ] Document corpus identified
- [ ] Metadata schema defined
- [ ] Golden questions drafted
```

---

## Project P6 Idea Template: Support Agent with Writes

```markdown
# Idea: Customer Support Agent with Write Actions

## Business Need
Extend support agent to perform bounded write actions (refunds, updates)
with safety gates and audit logging.

## Success Criteria
- [ ] All write actions require confirmation gate
- [ ] Audit log captures all actions
- [ ] Human escalation path functional
- [ ] Zero unauthorized writes in testing
- [ ] Resolution rate improves 20% vs read-only

## Scope
### In Scope
- Add 3 write tools: initiate_refund, update_address, create_ticket
- Confirmation gates for all writes
- Audit logging system
- Human escalation workflow
- Extended evaluation set (75+ cases)

### Out of Scope
- Production deployment
- Multi-tenant

## Constraints
- Safety Tier: 2 (limited write with confirmation)
- Budget: ~$100 for evaluation
- Timeline: 3 weeks

## Proposed Approach
1. Design write tool contracts with side effects
2. Implement confirmation gate pattern
3. Build audit logging
4. Add escalation triggers and workflow
5. Extend evaluation set
6. Security review

## Exit Criteria for Idea → Approved
- [ ] Write tool contracts reviewed
- [ ] Confirmation UX designed
- [ ] Audit log schema defined
- [ ] Security requirements documented
```

---

## Project P7 Idea Template: Testing Harness

```markdown
# Idea: Agent Testing & Evaluation Harness

## Business Need
Build a comprehensive testing framework to ensure agent reliability,
catch regressions, and detect adversarial inputs.

## Success Criteria
- [ ] Unit test coverage >80% on orchestrator
- [ ] Golden test set with 100+ cases
- [ ] CI/CD integration with regression checks
- [ ] Adversarial test suite with 20+ attacks
- [ ] Metrics dashboard operational

## Scope
### In Scope
- Unit test framework with LLM/tool mocks
- Golden test dataset management
- Regression testing pipeline
- Adversarial test suite
- Metrics collection and dashboard
- CI/CD integration

### Out of Scope
- Production agent (uses existing)
- Real-time monitoring

## Constraints
- Timeline: 3 weeks

## Proposed Approach
1. Design mock framework for LLM and tools
2. Build unit test suite
3. Create golden test dataset
4. Implement regression detection
5. Develop adversarial tests
6. Build metrics dashboard
7. Integrate with CI/CD

## Exit Criteria for Idea → Approved
- [ ] Mock strategy defined
- [ ] Golden test categories identified
- [ ] Adversarial attack types listed
```

---

## Project P8 Idea Template: Multi-Tenant Platform

```markdown
# Idea: Multi-Tenant Agent Platform

## Business Need
Build agent infrastructure that securely serves multiple tenants with
data isolation, resource quotas, and per-tenant configuration.

## Success Criteria
- [ ] Complete data isolation between tenants
- [ ] Per-tenant rate limiting functional
- [ ] Per-tenant cost tracking
- [ ] Audit logs separated by tenant
- [ ] Security review passed

## Scope
### In Scope
- Tenant isolation architecture
- Memory partitioning
- Rate limiting and cost caps
- Tenant-specific configurations
- Audit separation
- Security testing

### Out of Scope
- Self-service tenant onboarding
- Billing integration

## Constraints
- Security: Must pass isolation verification
- Timeline: 4 weeks

## Proposed Approach
1. Design tenant isolation architecture
2. Implement memory partitioning
3. Add rate limiting per tenant
4. Build cost tracking with attribution
5. Separate audit logs
6. Create isolation test suite
7. Security review

## Exit Criteria for Idea → Approved
- [ ] Isolation requirements documented
- [ ] Threat model reviewed
- [ ] Security reviewer assigned
```

---

## Project P9 Idea Template: Domain Production Agent

```markdown
# Idea: Production [DOMAIN] Agent

## Business Need
Build a production-ready agent for [DOMAIN] with full 6-pillar architecture,
comprehensive safety, and operational excellence.

## Success Criteria
- [ ] Production deployment achieved
- [ ] SLA: 99.5% uptime
- [ ] Resolution rate: 80%+
- [ ] Cost per task: <$X.XX
- [ ] Security review passed
- [ ] Runbooks documented

## Scope
### In Scope
- Full 6-pillar architecture
- Multi-LLM routing
- 10+ tools (read + write)
- Domain-appropriate safety tier
- Comprehensive observability
- Evaluation pipeline
- Production deployment
- Operational documentation

### Out of Scope
- [Define based on domain]

## Stakeholders
- Role: Client — Defines domain requirements
- Role: Architect — Reviews architecture
- Role: Implementer — Builds agent
- Role: Reviewer — Code and security review
- Role: DevOps — Deployment and monitoring
- Role: CODEOWNER — Final approval

## Constraints
- Safety Tier: [Appropriate for domain]
- Budget: Production level
- Timeline: 6-8 weeks

## Proposed Approach
[Domain-specific implementation plan]

## Exit Criteria for Idea → Approved
- [ ] Domain requirements documented
- [ ] Architecture reviewed
- [ ] Safety tier confirmed
- [ ] Security requirements documented
- [ ] Deployment target identified
```

---

## Project P10 Idea Template: Evaluation Platform

```markdown
# Idea: Agent Evaluation Platform

## Business Need
Build a platform for continuous agent evaluation, regression detection,
and quality monitoring to maintain production reliability.

## Success Criteria
- [ ] Automated evaluation runs on schedule
- [ ] Regression detection <1 hour after deploy
- [ ] A/B testing infrastructure functional
- [ ] Drift detection alerts operational
- [ ] Dashboard with key metrics

## Scope
### In Scope
- Golden test management system
- Automated regression testing
- A/B testing infrastructure
- Drift detection pipeline
- Evaluation dashboards
- Alert integration

### Out of Scope
- Agent development (uses existing agents)
- Self-service test creation

## Constraints
- Timeline: 4 weeks

## Proposed Approach
1. Design evaluation data model
2. Build golden test management
3. Implement automated runners
4. Add A/B testing framework
5. Develop drift detection
6. Create dashboards
7. Configure alerts

## Exit Criteria for Idea → Approved
- [ ] Evaluation metrics defined
- [ ] Test infrastructure selected
- [ ] Alert thresholds defined
```

---

## Project P11 Idea Template: Cost Engineering

```markdown
# Idea: Agent Cost Engineering & Optimization

## Business Need
Build comprehensive cost tracking, attribution, and optimization
to ensure economic sustainability of agent operations.

## Success Criteria
- [ ] Per-request cost tracking accurate to $0.001
- [ ] Attribution by tenant/user functional
- [ ] 20%+ cost reduction through optimization
- [ ] Budget enforcement prevents overruns
- [ ] Cost dashboards operational

## Scope
### In Scope
- Per-request cost tracking (model + tools)
- Cost attribution by tenant/user
- Caching optimization (RAG, prompts)
- Routing optimization
- Budget enforcement
- Cost dashboards and alerts

### Out of Scope
- Billing integration
- Self-service budget management

## Constraints
- Timeline: 3 weeks

## Proposed Approach
1. Instrument cost tracking
2. Build attribution system
3. Implement caching optimizations
4. Add routing optimization
5. Create budget controls
6. Build dashboards

## Exit Criteria for Idea → Approved
- [ ] Cost tracking points identified
- [ ] Attribution requirements defined
- [ ] Optimization targets set
```

---

## Project P12 Idea Template: Multi-Agent System

```markdown
# Idea: Multi-Agent Collaborative System

## Business Need
Build a system where multiple specialized agents collaborate on complex
tasks, demonstrating agent network patterns.

## Success Criteria
- [ ] 3+ specialized agents working together
- [ ] Communication protocol defined and working
- [ ] Coordinator manages workflow
- [ ] Failure handled across agents
- [ ] End-to-end workflow demo successful

## Scope
### In Scope
- 3+ specialized agents (researcher, planner, executor)
- Agent-to-agent communication protocol
- Coordinator/supervisor implementation
- Shared state management
- Cross-agent failure handling
- End-to-end demo workflow

### Out of Scope
- Production deployment
- Self-organizing agents

## Stakeholders
- Role: Architect — Multi-agent design
- Role: Implementer — Agent development
- Role: Reviewer — Integration review

## Constraints
- Complexity: High (architecture review required)
- Timeline: 6 weeks

## Proposed Approach
1. Design agent specializations
2. Define communication protocol
3. Build coordinator logic
4. Implement shared state
5. Add failure handling
6. Create demo workflow
7. End-to-end testing

## Exit Criteria for Idea → Approved
- [ ] Agent roles defined
- [ ] Communication protocol designed
- [ ] Workflow documented
- [ ] Architecture review completed
```

---

# 📚 APPENDIX: Source Document Mapping

| Chapter | Source Documents |
|---------|-----------------|
| B1 | 01_introduction_motivation.md |
| B2 | 02_what_is_an_ai_agent.md |
| B3 | 03_what_problems_do_agents_solve.md |
| B4 | 04_high_level_architecture.md |
| B5 | 09_00_current_trends_and_patterns.md |
| B6 | 05_01_1_langchain.md, 05_01_3_langraph.md, 09_01_agent_frameworks_and_multi_agent_systems.md |
| I1 | 05_01_orchestrator_agent_controller.md, 05_00_core_components.md |
| I2 | 05_02_llms_and_reasoning_modes.md |
| I3 | 05_03_tools_and_apis_agent.md, 09_02_tool_use_computer_control_autonomous_workflows.md |
| I4 | 05_04_0_memory_and_rag.md, 05_04_1_context_engineering.md, 05_04_2_memory_write_policy.md, 05_04_3_memory_retrieval_policy.md |
| I5 | 05_04_1_context_engineering.md |
| I6 | 05_05_policies_and_guardrails.md |
| I7 | 05_06_observability_logging_metrics_tracing.md |
| A1 | 06_design_decision_tree.md, 07_design_decision_tree.md |
| A2 | (Gap: Failure modes under-documented - based on critical review) |
| A3 | (Gap: Testing framework under-documented - based on critical review) |
| A4 | (Gap: Security under-documented - based on critical review) |
| A5 | (Gap: HITL under-documented - based on critical review) |
| A6 | 08_scalability_and_performance.md |
| P1 | 09_04_case_study_customer_support_agent.md, 12_01_customer_support_agent_architecture.md |
| P2 | 12_04_coding_agent_architecture.md |
| P3 | 12_05_medical_agent_architecture.md |
| P4 | 12_06_ops_troubleshooting_agent_architecture.md |
| P5 | 11_self_managed_vs_agent_as_a_service.md |
| P6 | 10_conclusion_future_directions.md, 09_01-09_03 |

---

**Curriculum Version:** 1.0  
**Created:** 2026-01-09  
**Framework:** space_framework SDLC Governance  
**Author:** Technical Architect / Curriculum Designer
