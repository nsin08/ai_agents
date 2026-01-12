# Intermediate Level Curriculum

## Overview

The Intermediate curriculum builds on the Beginner foundation to teach **production-capable agent development**. You'll learn orchestration patterns, advanced memory systems, observability, and integration patterns that enable real-world deployments.

**Target Audience:** Developers who have completed the Beginner curriculum and want to build production-ready agents.

**Prerequisites:**
- Completed Beginner curriculum (Labs 00-02)
- Familiarity with Python async/await patterns
- Basic understanding of agent architecture (LLM, tools, memory)

**Duration:** 15-20 hours (reading + exercises)

---

## Learning Objectives

After completing this curriculum, you will be able to:

1. **Implement agent orchestration loops** with state machines, ReAct patterns, and error recovery
2. **Design advanced memory systems** with multi-tier storage and retrieval strategies
3. **Apply context engineering** techniques for token management and prompt optimization
4. **Instrument agents with observability** using structured logging, metrics, and tracing
5. **Build multi-turn conversational agents** with state management and repair strategies
6. **Integrate agents with external systems** using resilient API patterns

---

## Chapters

| # | Chapter | Description | Key Concepts |
|---|---------|-------------|--------------|
| 1 | [Orchestrator Patterns](chapter_01_orchestrator_patterns.md) | Agent loops, ReAct, state machines | OPRV loop, CoT, failure handling |
| 2 | [Advanced Memory](chapter_02_advanced_memory.md) | Multi-tier memory architecture | Short/long-term, RAG, retrieval |
| 3 | [Context Engineering](chapter_03_context_engineering.md) | Prompt and context optimization | Templates, token budgeting, overflow |
| 4 | [Observability & Monitoring](chapter_04_observability.md) | Debugging and monitoring agents | Logging, traces, metrics |
| 5 | [Multi-Turn Conversations](chapter_05_multi_turn_conversations.md) | Stateful conversation design | Slots, history, repair |
| 6 | [Integration Patterns](chapter_06_integration_patterns.md) | External system integration | APIs, auth, retry, events |

---

## Chapter Summaries

### Chapter 1: Orchestrator Patterns

Learn the core agent loop—Observe, Plan, Act, Verify, Refine (OPRV)—and how to implement it with state machines. Covers ReAct pattern, chain-of-thought reasoning, and robust error handling.

**Labs:** 03 (Orchestrator)

### Chapter 2: Advanced Memory

Deep dive into memory architecture with three tiers: short-term (recent context), long-term (persistent facts), and RAG (external knowledge). Learn FIFO pruning, retrieval strategies, and memory persistence.

**Labs:** 04 (Memory)

### Chapter 3: Context Engineering

Master prompt templates, token budgeting, and context overflow prevention. Learn chunking strategies and few-shot learning patterns that maximize LLM effectiveness.

**Labs:** 05 (Context)

### Chapter 4: Observability & Monitoring

Implement structured JSON logging, execution traces, and metrics collection. Learn to debug agent behavior, identify bottlenecks, and export telemetry for analysis.

**Labs:** 06 (Observability)

### Chapter 5: Multi-Turn Conversations

Design agents that maintain coherent conversations across many turns. Learn slot filling, history management strategies (sliding window, summarization), and conversation repair patterns.

**Labs:** 04, 05

### Chapter 6: Integration Patterns

Connect agents to external APIs with proper authentication, retry logic, and circuit breakers. Build event-driven agents that respond to webhooks and manage tool registries.

**Labs:** 03, source/tools

---

## Lab Mapping

| Chapter | Primary Lab | Supporting Labs |
|---------|-------------|-----------------|
| Chapter 1 | Lab 03 | Lab 02 |
| Chapter 2 | Lab 04 | Lab 02 |
| Chapter 3 | Lab 05 | Lab 04 |
| Chapter 4 | Lab 06 | Lab 03 |
| Chapter 5 | Lab 04 | Lab 05 |
| Chapter 6 | Lab 03 | Lab 06 |

---

## Recommended Learning Path

### Week 1: Core Patterns
1. **Day 1-2:** Chapter 1 (Orchestrator) + Lab 03 exercises
2. **Day 3-4:** Chapter 2 (Memory) + Lab 04 exercises
3. **Day 5:** Chapter 3 (Context) + Lab 05 exercises

### Week 2: Production Skills
1. **Day 1-2:** Chapter 4 (Observability) + Lab 06 exercises
2. **Day 3-4:** Chapter 5 (Multi-Turn) + combined lab exercises
3. **Day 5:** Chapter 6 (Integration) + tool development

### Week 3: Integration Project
- Build a complete agent that combines all intermediate patterns
- Implement observability and test error handling
- Document and review with peers

---

## Assessment

After completing the curriculum:

1. **Knowledge Check:** Answer concept questions at the end of each chapter
2. **Practical Exercises:** Complete lab exercises (minimum 3 per chapter)
3. **Integration Project:** Build an agent that demonstrates:
   - State machine orchestration
   - Multi-tier memory with retrieval
   - Structured observability
   - At least 2 external tool integrations

---

## What's Next?

After completing the Intermediate curriculum, continue to:

- **[Advanced Curriculum](../03_advanced/README.md):** Multi-agent systems, human-in-the-loop, enterprise deployment
- **[Projects](../projects/README.md):** End-to-end agent implementations

---

## Quick Links

- [Beginner Curriculum](../01_beginner/README.md) — Prerequisites
- [Labs Directory](../../../labs/) — Hands-on exercises
- [Source Code](../../../src/agent_labs/) — Reference implementations
- [Main Curriculum Overview](../../ai_agents_learning_curriculum.md)
