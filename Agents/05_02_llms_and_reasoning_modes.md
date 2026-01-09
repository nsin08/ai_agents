[Previous](05_01_orchestrator_agent_controller.md) | [Next](05_03_tools_and_apis_agent.md)

# LLMs and Reasoning Modes  

## Table of Contents

- [**5.2 LLMs in Agent Systems — Roles, Modes, and Architecture**](#52-llms-in-agent-systems-roles-modes-and-architecture)
- [**1. The Role of LLMs in an Agent Architecture**](#1-the-role-of-llms-in-an-agent-architecture)
- [**2. Single‑LLM vs Multi‑LLM Architectures**](#2-singlellm-vs-multillm-architectures)
  - [**2.1 Single‑LLM Setup**](#21-singlellm-setup)
  - [**2.2 Multi‑LLM Architecture**](#22-multillm-architecture)
    - [**A. Router Model**](#a-router-model)
    - [**B. Planner Model**](#b-planner-model)
    - [**C. Executor / Tool‑Former Model**](#c-executor-toolformer-model)
    - [**D. Critic / Verifier Model**](#d-critic-verifier-model)
    - [**E. Communicator / Finalizer Model**](#e-communicator-finalizer-model)
  - [**2.3 Why Multi‑LLM Is Superior in Real Deployments**](#23-why-multillm-is-superior-in-real-deployments)
- [**3. Reasoning Modes in Agents**](#3-reasoning-modes-in-agents)
- [**3.1 Standard (Shallow) Reasoning**](#31-standard-shallow-reasoning)
- [**3.2 Deep / Extended Reasoning**](#32-deep-extended-reasoning)
- [**3.3 Reflective / Self‑Critique Reasoning**](#33-reflective-selfcritique-reasoning)
- [**3.4 Tool‑Aware Reasoning (Toolformer Style)**](#34-toolaware-reasoning-toolformer-style)
- [**3.5 Retrieval-Augmented Reasoning**](#35-retrieval-augmented-reasoning)
- [**4. Prompting Strategies for Agent LLMs**](#4-prompting-strategies-for-agent-llms)
  - [**4.1 System Prompts**](#41-system-prompts)
  - [**4.2 Structured Output Prompts**](#42-structured-output-prompts)
  - [**4.3 Few-Shot Examples**](#43-few-shot-examples)
  - [**4.4 Reflection Templates**](#44-reflection-templates)
- [**5. Model Selection Considerations**](#5-model-selection-considerations)
  - [**Accuracy Requirements**](#accuracy-requirements)
  - [**Cost vs Reliability**](#cost-vs-reliability)
  - [**Tool Compatibility**](#tool-compatibility)
  - [**Latency Requirements**](#latency-requirements)
  - [**Security**](#security)
- [**6. Example Multi‑LLM Architecture Flow**](#6-example-multillm-architecture-flow)

## **5.2 LLMs in Agent Systems — Roles, Modes, and Architecture**

LLMs act as the **reasoning layer** of an agentic system. They provide the semantic understanding, planning capability, and adaptive decision‑making that deterministic code alone cannot achieve. However, in a production agent, LLMs are *not the entire system* — they are carefully orchestrated components that work within a structured pipeline of tools, memory, policies, and observability.

This document provides a deep dive into how LLMs are used inside agents, how to design single‑LLM vs multi‑LLM architectures, and how different reasoning modes affect performance, cost, and reliability.

---

## **1. The Role of LLMs in an Agent Architecture**

LLMs provide the “intelligence” used for:

- **Understanding user intent**  
- **Generating structured plans**  
- **Selecting tools and creating tool arguments**  
- **Interpreting tool outputs**  
- **Summarizing and communicating**  
- **Performing reflection or critique**  
- **Adapting when failures or anomalies occur**

Engineers should view LLMs as **reasoning modules**, not execution engines.  
Execution belongs to the **tools** and **orchestrator**.

---

## **2. Single‑LLM vs Multi‑LLM Architectures**

### **2.1 Single‑LLM Setup**
The simplest architecture uses one model for all tasks:

- intent detection  
- planning  
- tool selection  
- refinement  
- final messaging  

**Pros**
- Simple to build  
- Lower engineering overhead  
- Easier debugging  
- Good for prototypes or low-volume agents  

**Cons**
- Not cost-efficient  
- Not specialized (same model handles trivial + complex tasks)  
- Increased latency  
- Harder to optimize performance at scale  
- No separation of concerns  
- Risk of overloading one model with conflicting prompts  

Single-LLM systems work for:
- small agents  
- constrained domains  
- early-stage development  
- low traffic volumes  

---

### **2.2 Multi‑LLM Architecture**
Production agents often use multiple LLMs, each with a specific responsibility. Example roles:

#### **A. Router Model**
- Classifies the user request  
- Determines which model to call  
- Performs lightweight intent detection  
- Routes simple tasks → small model  
- Routes complex tasks → large model  

#### **B. Planner Model**
- Produces structured plans  
- Breaks tasks into steps  
- Chooses appropriate tools  
- Enforces reasoning consistency  
- Typically high-quality model with good planning ability  

#### **C. Executor / Tool‑Former Model**
- Writes tool arguments  
- Parses tool responses  
- Generates intermediate explanations  
- Useful when tool invocation schemas are strict  

#### **D. Critic / Verifier Model**
- Evaluates:  
  - correctness  
  - completeness  
  - hallucination risks  
  - adherence to constraints  
- Required for workflows where accuracy matters (finance, HR, operations)  

#### **E. Communicator / Finalizer Model**
- Produces user-friendly replies  
- Reformats complex information  
- May be smaller/cheaper for cost efficiency  

---

### **2.3 Why Multi‑LLM Is Superior in Real Deployments**
Multi‑LLM design enables:

- Lower cost (cheap model handles easy tasks)  
- Faster responses  
- Higher reliability (critic model catches errors)  
- Separation of concerns (planning ≠ communication)  
- Swapping models without breaking architecture  
- Ability to fine-tune specific components  

This structure is similar to how real human teams operate:
- planners  
- executors  
- reviewers  
- communicators  

---

## **3. Reasoning Modes in Agents**

Agents use different reasoning levels depending on complexity, cost, and urgency.

---

## **3.1 Standard (Shallow) Reasoning**
- Fast  
- Low cost  
- Good for simple routing or FAQ-like tasks  
- Avoids unnecessary chain-of-thought  

Use cases:
- “What is the refund policy?”  
- “Show me my last 5 orders.”  
- “Update my phone number.”  

---

## **3.2 Deep / Extended Reasoning**
- Longer thinking time  
- More deliberate planning  
- Structured multi-step reasoning  
- Can generate multi-layer plans, edge-case detection, fallback analysis  

Use cases:
- diagnosing production incidents  
- analyzing logs or documents  
- generating step-by-step workflows  
- complex tool orchestration  

---

## **3.3 Reflective / Self‑Critique Reasoning**
The model:
- generates an answer  
- evaluates its own errors  
- revises output before returning  

This mirrors human "double-checking".

Used in:
- code generation  
- compliance workflows  
- engineering or research agents  

---

## **3.4 Tool‑Aware Reasoning (Toolformer Style)**
The LLM thinks like:
- “Which tool can solve this?”  
- “What arguments should I pass?”  
- “How do I integrate results?”  

Tool-forming reasoning is the backbone of modern agents.

---

## **3.5 Retrieval-Augmented Reasoning**
When context exceeds model window:

- LLM formulates retrieval queries  
- Orchestrator fetches relevant content  
- LLM reasons over retrieved chunks  

Critical for:
- policy analysis  
- legal/compliance  
- technical manuals  
- engineering workflows  

---

## **4. Prompting Strategies for Agent LLMs**

### **4.1 System Prompts**
Provide:
- allowed tools  
- role definition  
- planning rules  
- safety constraints  

### **4.2 Structured Output Prompts**
LLMs must output:
- JSON  
- YAML  
- decision graphs  
- tool calls in strict schema  

Unstructured text ≠ safe agent behavior.

### **4.3 Few-Shot Examples**
Demonstrate:
- planning patterns  
- error recovery  
- schema requirements  

### **4.4 Reflection Templates**
Give models patterns like:
- “Check your assumptions.”  
- “Verify all returned values follow schema.”  
- “Re-evaluate whether the goal is met.”  

---

## **5. Model Selection Considerations**

When choosing LLMs for agents, consider:

### **Accuracy Requirements**
- Support agents → moderate accuracy  
- Finance/HR → high accuracy  
- Engineering → strong reasoning  

### **Cost vs Reliability**
- Multi-LLM routing helps optimize  
- Large models used sparingly  

### **Tool Compatibility**
Some models are better at:
- structured output  
- JSON reasoning  
- iterative refinement  
- code generation  

### **Latency Requirements**
- Real-time chat needs low-latency small models  
- Background workflows can afford slower deep reasoning  

### **Security**
- Ensure model does not leak sensitive info  
- System prompts and guardrails must constrain access  

---

## **6. Example Multi‑LLM Architecture Flow**

```text
User → Router LLM →  
    If "simple": Small LLM → direct answer  
    If "complex":  
       Planner LLM → structured plan  
       Executor LLM → tool calls  
       Critic LLM → validate results  
       Communicator LLM → final answer

[Previous](05_01_orchestrator_agent_controller.md) | [Next](05_03_tools_and_apis_agent.md)
