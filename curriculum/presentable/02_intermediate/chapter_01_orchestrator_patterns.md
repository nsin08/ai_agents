# Chapter 01: Orchestrator Patterns

[Prev: Level 1 Workbook](../01_beginner/02_workbook.md) | [Up](README.md) | [Next](chapter_02_advanced_memory.md)

---

## Learning Objectives

After completing this chapter, you will be able to:

1. **Understand the Agent Loop** — Trace the complete Observe → Plan → Act → Verify → Refine cycle and explain when each phase executes
2. **Implement State Transitions** — Build valid state machine transitions using the `AgentState` enum and `can_transition()` guard
3. **Apply ReAct Patterns** — Combine Reasoning and Acting in iterative loops with LLM-driven decisions
4. **Design Chain-of-Thought Flows** — Structure prompts that elicit step-by-step reasoning before action
5. **Handle Failure Modes** — Implement graceful degradation, max-turn limits, and verification-driven retries

---

## Introduction

The orchestrator is the "heartbeat" of every AI agent. It coordinates perception, reasoning, action, and reflection in a structured loop. Unlike simple chatbots that respond once per turn, an agent may iterate multiple times—refining its approach until the goal is achieved or resources are exhausted.

This chapter explores the orchestration patterns implemented in `src/agent_labs/orchestrator/` and demonstrated in Lab 3. You'll learn how to trace execution, tune loop parameters, and extend the orchestrator for custom domains.

**Key Insight:** The orchestrator doesn't just call the LLM—it *controls when* the LLM is called, *what context* it receives, and *whether to continue* based on verification results.

---

## 1. The Agent Loop: Observe → Plan → Act → Verify → Refine

### 1.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AGENT ORCHESTRATOR                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│   │ OBSERVE  │───▶│   PLAN   │───▶│   ACT    │───▶│  VERIFY  │     │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│        ▲                                               │            │
│        │                                               │            │
│        │         ┌──────────┐                          │            │
│        └─────────│  REFINE  │◀─────────────────────────┘            │
│                  └──────────┘        (if incomplete)                │
│                                                                      │
│   Exit conditions:                                                   │
│   • Goal achieved (verification passes)                              │
│   • Max turns reached                                                │
│   • Unrecoverable error                                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

Each phase has a specific responsibility:

| Phase | Responsibility | Output |
|-------|---------------|--------|
| **Observe** | Gather current state, goal, and context | Observation dict |
| **Plan** | Decide next action using LLM reasoning | Action plan |
| **Act** | Execute the plan (tools, API calls, etc.) | Execution result |
| **Verify** | Check if result achieves the goal | VerificationResult |
| **Refine** | Adjust approach for next iteration | Updated context |

### 1.2 State Machine Implementation

The orchestrator uses a finite state machine to enforce valid transitions. This prevents bugs where code accidentally skips phases or enters invalid states.

```python
# From src/agent_labs/orchestrator/states.py
from enum import Enum
from typing import Dict, Set

class AgentState(Enum):
    """Agent execution states in the orchestration loop."""
    OBSERVING = "observing"
    PLANNING = "planning"
    ACTING = "acting"
    VERIFYING = "verifying"
    REFINING = "refining"
    DONE = "done"
    FAILED = "failed"

# Valid transitions (adjacency list)
_TRANSITIONS: Dict[AgentState, Set[AgentState]] = {
    AgentState.OBSERVING: {AgentState.PLANNING},
    AgentState.PLANNING: {AgentState.ACTING},
    AgentState.ACTING: {AgentState.VERIFYING},
    AgentState.VERIFYING: {AgentState.DONE, AgentState.REFINING},
    AgentState.REFINING: {AgentState.OBSERVING},
    AgentState.DONE: set(),     # Terminal state
    AgentState.FAILED: set(),   # Terminal state
}

def can_transition(current: AgentState, target: AgentState) -> bool:
    """Check if the state transition is valid."""
    if target == AgentState.FAILED:
        return True  # Can always fail from any state
    return target in _TRANSITIONS.get(current, set())
```

**Key Design Decision:** The `FAILED` state is reachable from any other state—this handles unexpected errors gracefully without requiring explicit transitions from each state.

### 1.3 Transition Validation Pattern

Always validate transitions before changing state. This prevents silent bugs and enables observability:

```python
def _transition_state(self, context: AgentContext, new_state: AgentState) -> None:
    """Transition to a new state with validation and logging."""
    old_state = context.current_state

    if not can_transition(old_state, new_state):
        raise StateTransitionError(old_state.value, new_state.value)

    logger.info("State transition: %s -> %s", old_state.value, new_state.value)
    context.current_state = new_state

    # Observability hook for external monitoring
    if self.on_state_change:
        self.on_state_change(old_state, new_state)
```

**Best Practice:** Hook into `on_state_change` for metrics, tracing, and debugging. This is how you'll instrument production agents.

---

## 1.4 Loop Parameters That Actually Matter

The loop is simple, but the parameters are where most reliability decisions live. A few defaults can make an agent fragile:

- `max_turns`: Prevents infinite loops. For tasks that depend on external tools, set a conservative upper bound (e.g., 3-5) and require explicit approval to raise it.
- `max_cost` or `token_budget`: If you do not cap tokens, you cannot predict cost. Use a hard budget to fail fast.
- `timeouts`: Tool timeouts should be shorter than your overall request budget. It is better to retry a tool quickly than to wait for a single long call.
- `verification_thresholds`: If your verifier returns a confidence score, define what is "good enough" and what requires refinement.

**Rule of thumb:** Start with stricter limits, then relax them only when you have metrics that show success rates are suffering. This creates a safe baseline and avoids cost surprises.

---

## 1.5 Verification Strategies (Not Optional)

Verification is where you decide whether the system should stop or continue. If you do not have verification, you do not have a controllable agent.

There are three common strategies:

1. **LLM self-verification**: Ask the model to judge completion. This is fast but can be biased.
2. **Rule-based verification**: Validate output format, JSON schemas, or deterministic checks.
3. **Hybrid**: Run rules first, then use an LLM to judge soft criteria.

Example (rule-based verifier):

```python
from agent_labs.orchestrator import AgentContext, VerificationResult

def verify_json(context: AgentContext, result: str) -> VerificationResult:
    if result.strip().startswith("{") and result.strip().endswith("}"):
        return VerificationResult(is_complete=True, reason="Valid JSON")
    return VerificationResult(is_complete=False, reason="Output is not JSON", feedback="Return valid JSON")
```

**Best Practice:** Always record the reason in the `VerificationResult`. This is what you use to diagnose "why did it keep looping?"

---

## 2. ReAct Pattern: Reasoning + Acting

### 2.1 What is ReAct?

ReAct (Reasoning + Acting) is a prompting pattern where the LLM alternates between:
1. **Thought** — Explicit reasoning about what to do
2. **Action** — Selecting and executing a tool
3. **Observation** — Processing the result

This creates a traceable chain of reasoning that helps debug agent behavior.

### 2.2 ReAct Implementation

Here's how to structure ReAct-style prompts in the planning phase:

```python
# Example: ReAct-style planning prompt
async def _plan_react(self, context: AgentContext) -> str:
    """Plan using ReAct pattern with explicit reasoning."""
    
    history_str = context.format_history(n=5)
    available_tools = self._get_tool_descriptions()
    
    prompt = f"""You are an AI agent solving a task step by step.

Goal: {context.goal}

Available tools:
{available_tools}

Recent history:
{history_str}

Think step by step:
1. What do I know so far?
2. What do I still need to find out?
3. Which tool should I use next?

Format your response as:
Thought: <your reasoning>
Action: <tool_name>
Action Input: <input for the tool>
"""
    
    response = await self.provider.generate(prompt)
    return self._parse_react_response(response.text)

def _parse_react_response(self, text: str) -> dict:
    """Parse ReAct-formatted response into structured action."""
    lines = text.strip().split('\n')
    result = {"thought": "", "action": "", "action_input": ""}
    
    for line in lines:
        if line.startswith("Thought:"):
            result["thought"] = line[8:].strip()
        elif line.startswith("Action:"):
            result["action"] = line[7:].strip()
        elif line.startswith("Action Input:"):
            result["action_input"] = line[13:].strip()
    
    return result
```

### 2.3 ReAct Execution Trace

Here's what a ReAct trace looks like in practice:

```
Turn 1:
  Thought: I need to find the weather in Seattle. I have a weather_lookup tool available.
  Action: weather_lookup
  Action Input: {"city": "Seattle"}
  
  Observation: Weather in Seattle: 20C and clear.
  
  Thought: I have the weather information. The goal is achieved.
  Action: respond
  Action Input: "The weather in Seattle is 20°C and clear."

Result: "The weather in Seattle is 20°C and clear."
Turns used: 1
```

**Why ReAct Works:** By forcing explicit reasoning before each action, the LLM is less likely to hallucinate or skip steps. The trace also makes debugging much easier—you can see *why* the agent chose each action.

---

## 3. Chain-of-Thought Patterns

### 3.1 Prompting for Step-by-Step Reasoning

Chain-of-Thought (CoT) prompting encourages the LLM to "show its work" before providing an answer. This is especially useful for complex reasoning tasks.

```python
# Example: Chain-of-Thought planning
async def _plan_with_cot(self, context: AgentContext) -> str:
    """Plan using Chain-of-Thought reasoning."""
    
    prompt = f"""Goal: {context.goal}

Let's solve this step by step:

Step 1: Identify what we're trying to accomplish.
Step 2: Break down the problem into smaller parts.
Step 3: For each part, determine the best approach.
Step 4: Combine the results into a final plan.

Now apply this to the goal above:
"""
    
    response = await self.provider.generate(prompt)
    return response.text
```

### 3.2 Multi-Step Math Example

From Lab 3, here's how CoT handles a multi-step calculation:

```python
# Query: "What's 15% of $234.50 plus $12 shipping?"

# Without CoT - LLM might jump to wrong answer
# With CoT - LLM reasons through each step:

"""
Step 1: Calculate 15% of $234.50
  - 15% = 0.15
  - 0.15 × 234.50 = 35.175
  - Rounded: $35.18

Step 2: Add shipping cost
  - Subtotal: $35.18
  - Shipping: $12.00
  - Total: $35.18 + $12.00 = $47.18

Final Answer: $47.18
"""
```

### 3.3 When to Use CoT vs. ReAct

| Pattern | Best For | Overhead |
|---------|----------|----------|
| **Chain-of-Thought** | Complex reasoning, math, logic puzzles | Low (single prompt) |
| **ReAct** | Multi-step tasks with tool use | Medium (multiple turns) |
| **Combined** | Complex tasks requiring both reasoning and tools | High (maximum control) |

---

## 4. Verification and Exit Conditions

### 4.1 The Verification Phase

Verification is crucial—it determines whether to continue iterating or declare the goal complete. The default verifier uses the LLM itself:

```python
async def _default_verify(self, context: AgentContext, result: str) -> VerificationResult:
    """Default verifier using LLM to determine completion."""
    prompt = (
        f"Goal: {context.goal}\n\n"
        f"Result: {result}\n\n"
        "Does this result achieve the goal? Answer with:\n"
        "- \"YES\" if the goal is fully achieved\n"
        "- \"NO\" if more work is needed\n"
        "- Include a brief reason\n\n"
        "Format: YES/NO | reason"
    )

    response = await self.provider.generate(prompt, max_tokens=100)
    answer = response.text.strip()
    
    is_complete = answer.upper().startswith("YES")
    reason = answer.split("|", 1)[1].strip() if "|" in answer else answer
    
    return VerificationResult(
        is_complete=is_complete,
        confidence=1.0 if is_complete else 0.0,
        reason=reason,
        feedback="" if is_complete else "Continue working towards goal",
    )
```

### 4.2 Custom Verification Strategies

For domain-specific agents, inject a custom verifier:

```python
def math_verifier(context: AgentContext, result: str) -> VerificationResult:
    """Custom verifier for math problems - checks for numeric result."""
    import re
    
    # Look for numeric answer in result
    numbers = re.findall(r'\d+\.?\d*', result)
    
    if numbers:
        return VerificationResult(
            is_complete=True,
            confidence=0.9,
            reason=f"Found numeric result: {numbers[-1]}",
            feedback="",
        )
    
    return VerificationResult(
        is_complete=False,
        confidence=0.2,
        reason="No numeric result found",
        feedback="Please provide a numeric answer",
    )

# Usage
agent = Agent(
    provider=provider,
    verifier=math_verifier,
)
```

### 4.3 Exit Conditions Matrix

| Condition | State Transition | Response |
|-----------|-----------------|----------|
| Verification passes | VERIFYING → DONE | Return result |
| Verification fails, turns remaining | VERIFYING → REFINING → OBSERVING | Continue loop |
| Max turns reached | → FAILED | Return last result with warning |
| Unrecoverable error | → FAILED | Raise exception or return error |
| Confidence threshold met | → DONE | Return result (early exit) |

---

## 5. Handling Failure Modes

### 5.1 Exception Hierarchy

The orchestrator defines specific exceptions for different failure modes:

```python
# From src/agent_labs/orchestrator/exceptions.py

class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    pass

class MaxTurnsExceededError(OrchestratorError):
    """Raised when max_turns is exceeded or invalid."""
    pass

class StateTransitionError(OrchestratorError):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, from_state: str, to_state: str):
        super().__init__(f"Invalid transition: {from_state} -> {to_state}")

class PlanningError(OrchestratorError):
    """Raised when planning fails (LLM error, etc.)."""
    pass

class ActionExecutionError(OrchestratorError):
    """Raised when action execution fails (tool error, etc.)."""
    pass

class VerificationError(OrchestratorError):
    """Raised when verification fails unexpectedly."""
    pass
```

### 5.2 Graceful Degradation Pattern

Always handle failures gracefully and provide useful feedback:

```python
async def run_with_fallback(self, goal: str) -> str:
    """Run agent with graceful degradation."""
    try:
        result = await self.run(goal, max_turns=5)
        return result
    
    except MaxTurnsExceededError:
        logger.warning("Max turns reached for goal: %s", goal)
        return "I wasn't able to fully complete this task. Here's what I found so far..."
    
    except PlanningError as e:
        logger.error("Planning failed: %s", e)
        return "I had trouble figuring out how to approach this. Could you rephrase your request?"
    
    except ActionExecutionError as e:
        logger.error("Action failed: %s", e)
        return "I encountered an error while executing. Let me try a different approach."
    
    except Exception as e:
        logger.exception("Unexpected error in agent loop")
        return "Something unexpected happened. Please try again."
```

### 5.3 Retry with Backoff

For transient failures (network issues, rate limits), implement exponential backoff:

```python
import asyncio

async def _act_with_retry(self, context: AgentContext, plan: str, max_retries: int = 3) -> str:
    """Execute action with exponential backoff retry."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await self._act(context, plan)
        except ActionExecutionError as e:
            last_error = e
            wait_time = (2 ** attempt) + (0.1 * attempt)  # 1s, 2.1s, 4.2s
            logger.warning("Action failed (attempt %d/%d), retrying in %.1fs",
                          attempt + 1, max_retries, wait_time)
            await asyncio.sleep(wait_time)
    
    raise last_error
```

---

## 6. Tuning the Orchestrator

### 6.1 Key Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `max_turns` | 5 | Maximum iterations before giving up |
| `confidence_threshold` | 0.95 | Minimum confidence for early exit |
| `history_depth` | 5 | Number of turns to include in context |

### 6.2 Parameter Trade-offs

**max_turns:**
- **Too low:** Agent gives up before completing complex tasks
- **Too high:** Wastes tokens and time on impossible tasks
- **Recommendation:** Start with 5, increase for multi-step workflows

**confidence_threshold:**
- **Too low:** Agent exits prematurely with incomplete answers
- **Too high:** Agent never exits via confidence, always uses max_turns
- **Recommendation:** 0.7-0.9 for most tasks, higher for critical operations

### 6.3 Profiling Example

From Lab 3, compare different parameter settings:

```
| Setting              | Weather Query | Math Query | Missing Tool |
|---------------------|---------------|------------|--------------|
| max_turns=1         | ✓ 1 turn      | ✓ 1 turn   | ✗ Incomplete |
| max_turns=5         | ✓ 1 turn      | ✓ 1 turn   | ✓ 1 turn     |
| conf_threshold=0.5  | ✓ Early exit  | ✓ Early    | ✗ No improve |
| conf_threshold=0.99 | ✓ 1 turn      | ✓ 1 turn   | ✓ 1 turn     |
```

---

## 7. Code Example: Complete Orchestrator

Here's a minimal but complete orchestrator implementation:

```python
"""
Minimal orchestrator demonstrating the complete agent loop.
Run: python -c "import asyncio; asyncio.run(main())"
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional, Callable

class State(Enum):
    OBSERVE = "observe"
    PLAN = "plan"
    ACT = "act"
    VERIFY = "verify"
    REFINE = "refine"
    DONE = "done"

@dataclass
class Context:
    goal: str
    turn: int = 0
    history: List[Tuple[str, str]] = field(default_factory=list)
    state: State = State.OBSERVE

class SimpleOrchestrator:
    def __init__(self, llm_fn: Callable[[str], str], max_turns: int = 5):
        self.llm = llm_fn
        self.max_turns = max_turns
    
    async def run(self, goal: str) -> str:
        ctx = Context(goal=goal)
        result = ""
        
        for turn in range(1, self.max_turns + 1):
            ctx.turn = turn
            
            # Observe
            ctx.state = State.OBSERVE
            observation = f"Turn {turn}: Goal is '{goal}'"
            ctx.history.append(("observe", observation))
            
            # Plan
            ctx.state = State.PLAN
            prompt = f"Goal: {goal}\nHistory: {ctx.history[-3:]}\nWhat action should I take?"
            plan = self.llm(prompt)
            ctx.history.append(("plan", plan))
            
            # Act
            ctx.state = State.ACT
            result = f"Executed: {plan}"
            ctx.history.append(("act", result))
            
            # Verify
            ctx.state = State.VERIFY
            verify_prompt = f"Goal: {goal}\nResult: {result}\nIs goal achieved? YES/NO"
            verification = self.llm(verify_prompt)
            
            if "YES" in verification.upper():
                ctx.state = State.DONE
                return result
            
            # Refine
            ctx.state = State.REFINE
            ctx.history.append(("refine", "Continuing to next turn..."))
        
        return result  # Max turns reached

# Example usage
async def main():
    def mock_llm(prompt: str) -> str:
        if "action" in prompt.lower():
            return "Look up weather for Seattle"
        if "achieved" in prompt.lower():
            return "YES | Weather retrieved successfully"
    return "Processing..."
    
    orchestrator = SimpleOrchestrator(mock_llm, max_turns=3)
    result = await orchestrator.run("Get the weather in Seattle")
    print(f"Final result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Implementation Guide (using core modules)

Use these repo assets to make the chapter actionable:

- Orchestrator loop: `src/agent_labs/orchestrator/agent.py`
- States + transitions: `src/agent_labs/orchestrator/states.py`
- Context + history: `src/agent_labs/orchestrator/context.py`
- Lab: `labs/03/README.md`
- Runnable snippet: `curriculum/presentable/02_intermediate/snippets/ch01_orchestrator_state_transitions.py`

Suggested sequence:

1. Read the chapter, then skim `agent.py` to see how observe/plan/act/verify/refine are structured.
2. Run Lab 03 and instrument state transitions with timestamps.
3. Run the snippet and inspect the printed valid transitions to confirm your mental model.

**Deliverable:** a one-page controller spec (states, transitions, stop conditions, retry rules).

---

## Common Pitfalls and How to Avoid Them

1. **Skipping verification:** This creates runaway loops and inconsistent behavior. Always verify completion.
2. **Unbounded retries:** A retry policy without limits will burn budget and time. Always cap retries and total turns.
3. **Silent state changes:** If you do not log transitions, you cannot debug production incidents.
4. **Tool calls without validation:** If tool inputs are unvalidated, the agent will fail in unpredictable ways.
5. **No failure path:** You must explicitly design what happens when a step is not recoverable.

---

## Summary

### Key Takeaways

1. **The agent loop (Observe → Plan → Act → Verify → Refine) is the foundation of agent behavior.** Each phase has a specific responsibility, and the state machine enforces valid transitions.

2. **ReAct combines reasoning and acting** for traceable, debuggable agent behavior. Use it when you need to understand *why* an agent made each decision.

3. **Chain-of-Thought prompting improves complex reasoning** by encouraging the LLM to show its work before providing answers.

4. **Verification determines loop continuation.** Custom verifiers enable domain-specific success criteria.

5. **Graceful failure handling is essential.** Use typed exceptions, retry with backoff, and always provide useful feedback.

6. **Parameters like `max_turns` and `confidence_threshold` significantly affect behavior.** Profile different settings for your specific use case.

### What's Next

In Chapter 02, you'll learn about **Advanced Memory Systems**—how agents remember facts across turns, distinguish episodic from semantic memory, and implement retrieval strategies.

---

## References

- **Lab 3:** [labs/03/README.md](../../../labs/03/README.md) — Orchestrator Patterns hands-on exercises
- **Source Code:** [src/agent_labs/orchestrator/](../../../src/agent_labs/orchestrator/) — Core implementation
- **State Machine:** [src/agent_labs/orchestrator/states.py](../../../src/agent_labs/orchestrator/states.py) — State definitions and transitions
- **ReAct Paper:** [Yao et al., 2022](https://arxiv.org/abs/2210.03629) — ReAct: Synergizing Reasoning and Acting
- **Chain-of-Thought:** [Wei et al., 2022](https://arxiv.org/abs/2201.11903) — Chain-of-Thought Prompting

---

## Exercises

Complete these exercises in the workbook to reinforce your learning:

1. **Trace a Multi-Turn Execution:** Run Lab 3's orchestrator with a complex query and annotate each state transition with timestamps.

2. **Implement Custom Verification:** Create a verifier for a specific domain (e.g., code compilation, JSON validation) and test it with the orchestrator.

3. **Compare ReAct vs. CoT:** Implement both patterns for the same task and compare token usage, accuracy, and debugging ease.

4. **Tune Parameters:** Experiment with `max_turns` from 1-10 and `confidence_threshold` from 0.5-0.99. Document the trade-offs.

5. **Add Retry Logic:** Extend the `_act` method with exponential backoff retry and test with simulated transient failures.

---

[Prev: Level 1 Workbook](../01_beginner/02_workbook.md) | [Up](README.md) | [Next](chapter_02_advanced_memory.md)
