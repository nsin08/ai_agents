# Curriculum + Labs Gap Analysis + Component Maturity Model

**Date:** 2026-01-20  
**Scope:** Full repository scan (`src/`, `labs/`, `curriculum/`, `Agents/`)

## Executive Summary: From Basic Understanding to Professional Design

This repository successfully establishes a **strong educational baseline** (Levels 1-2) for AI Agent development. It teaches key concepts—Orchestration, Memory Tiers, Tool Use, and Safety—through clear Python implementations and hands-on labs.

However, to bridge the gap to **Professional/Production Systems** (Levels 3-4), specific architectural components need maturity upgrades. Professional agents require standardized interfaces (MCP), robust persistence (Postgres/Vector DBs), and rigorous engineering controls (CI Evaluation Gates, OpenTelemetry).

**Key Findings:**
1.  **Educational Core is Solid**: Labs 01-08 cover the fundamental lifecycle of an agent excellently.
2.  **MCP is the Major Integration Gap**: While mentioned in architectural case studies, the *Model Context Protocol* is absent from code and labs. Adding this is critical for modern, interoperable tool servers.
3.  **Persistence needs a Production Path**: The current `sqlite` and `in-memory` defaults are perfect for learning but fail to demonstrate multi-tenant, scalable deployments (Postgres/pgvector).
4.  **Evaluation is Manual**: We lack a "Ship Gate" workflow. Professional engineering requires automated evaluation sets (Golden Datasets) running in CI.

---

## 1. Coverage Map & Maturity Assessment

| Component | Current State | Maturity Level | Professional Gap to Close |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | ✅ Implemented (`src/.../orchestrator`) | **Level 2** (Configurable) | Resumability/Checkpoints for long-running workflows. |
| **Tools** | ✅ Registry exists (`src/.../tools/registry.py`) | **Level 2** (Registry + Validation) | **MCP Support** (Remote tool discovery & standard protocol). |
| **Memory** | ✅ Layers defined (`impl` in Lab 04) | **Level 1** (In-Memory/SQLite) | **Production Stores**: Postgres, Vector DB (Chroma/pgvector) implementation. |
| **Observability**| ✅ Structured Logs (`src/.../observability`) | **Level 2** (JSON Logs + Traces) | **OpenTelemetry**: Standard OTLP exporters for standard APM tools. |
| **Safety** | ✅ Guardrails (`Labs/07`) | **Level 2** (Validators) | **Context-Aware Safety**: dynamic policies based on user tier. |
| **Evaluation** | ⚠️ Partial (`src/agent_labs/evaluation`) | **Level 1** (Basic Scorers) | **CI/CD Gates**: "Golden Set" automation to prevent regression. |
| **Multi-Agent** | ✅ Lab 08 exists | **Level 2** (Router/Swarm) | **Distributed**: Running agents as separate services (Service Mesh). |

---

## 2. Detailed Gap Analysis

### 2.1 Model Context Protocol (MCP) (Critical)
*   **Status**: Referenced only in `Agents/` case study appendices. Absent from `src` and `Labs`.
*   **Why Professional?**: Solves the "N Tools × M Agents" problem. Allows agents to connect to local (filesystem, git) and remote (Slack, GitHub) resources securely and uniformly.
*   **Action**: 
    *   Create `src/agent_labs/mcp/` adapter.
    *   Add Lab to build a simple MCP Tool Server.

### 2.2 Production Persistence Strategy (High)
*   **Status**: `SqliteStorage` and `InMemoryStorage` are the only implemented backends. `ChromaVectorStore` is a placeholder.
*   **Why Professional?**: Real agents need multi-tenant isolation, concurrent writes, and scalable vector search. SQLite cannot handle high-concurrency production loads.
*   **Action**:
    *   Implement `PostgresStorage` (JSONB for documents + relational for logs).
    *   Implement a real Vector DB connector (pgvector or Chroma).

### 2.3 Evaluation as Code (High)
*   **Status**: `runner.py` and `scorers.py` exist but aren't wired into a workflow.
*   **Why Professional?**: You cannot "eye-ball" LLM changes. Every prompt adjustment needs a regression test against a "Certified Golden Set".
*   **Action**:
    *   Create a reusable "Evaluation Task" (e.g., `make evaluate`).
    *   Add a Lab on "Building your Golden Set".

### 2.4 OpenTelemetry (OTel) Integration (Medium)
*   **Status**: Custom JSON logging is implemented. OTel is mentioned in docs.
*   **Why Professional?**: DevOps teams use Datadog/Honeycomb/Jaeger. Agents must emit standard Spans and Metrics to fit into existing enterprise monitoring.
*   **Action**:
    *   Add `OpenTelemetryExporter` to the observability module.

---

## 3. Design Patterns for Professional Components

Professional agent systems require three core design patterns to achieve modularity, testability, and operational flexibility.

### 3.1 Strategy Pattern (Algorithm Selection)
**Purpose**: Encapsulate interchangeable algorithms/behaviors behind a common interface.

**Example Use Cases**:
- **Chunking Strategies**: Fixed-size, semantic-boundary, recursive-split
- **Retrieval Strategies**: Keyword, vector-similarity, hybrid, BM25
- **LLM Response Parsers**: JSON, markdown, structured-output

**Implementation Pattern**:
```python
from abc import ABC, abstractmethod

class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        pass

class FixedSizeChunker(ChunkingStrategy):
    def __init__(self, size: int = 512):
        self.size = size
    
    def chunk(self, text: str) -> List[str]:
        # Implementation
        pass

class SemanticChunker(ChunkingStrategy):
    def chunk(self, text: str) -> List[str]:
        # Split on paragraph/sentence boundaries
        pass

# Usage
class ContextBuilder:
    def __init__(self, strategy: ChunkingStrategy):
        self.strategy = strategy
    
    def build(self, document: str):
        chunks = self.strategy.chunk(document)
        # ...
```

**Current Gap**: Context chunking exists in `src/agent_labs/context/chunking.py` but no Strategy abstraction.

---

### 3.2 Factory Pattern (Object Creation)
**Purpose**: Centralize object construction logic; create instances based on config/environment.

**Example Use Cases**:
- **LLM Provider Factory**: Create MockProvider, OllamaProvider, OpenAIProvider from config
- **Storage Backend Factory**: Create InMemory, SQLite, Postgres, Redis from config
- **Tool Factory**: Instantiate tools with proper credentials/endpoints

**Implementation Pattern**:
```python
from enum import Enum
from typing import Protocol

class StorageBackend(Protocol):
    def store(self, key: str, value: Any) -> None: ...
    def get(self, key: str) -> Optional[Any]: ...

class StorageType(str, Enum):
    MEMORY = "memory"
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    REDIS = "redis"

class StorageFactory:
    @staticmethod
    def create(config: dict) -> StorageBackend:
        storage_type = StorageType(config.get("type", "memory"))
        
        if storage_type == StorageType.MEMORY:
            return InMemoryStorage()
        elif storage_type == StorageType.SQLITE:
            return SqliteStorage(path=config.get("path", "memory.db"))
        elif storage_type == StorageType.POSTGRES:
            return PostgresStorage(
                host=config["host"],
                database=config["database"]
            )
        elif storage_type == StorageType.REDIS:
            return RedisStorage(url=config["redis_url"])
        
        raise ValueError(f"Unknown storage type: {storage_type}")

# Usage
config = {"type": "postgres", "host": "localhost", "database": "agent_db"}
storage = StorageFactory.create(config)
```

**Current Gap**: 
- No `ProviderFactory` for LLM providers
- No `StorageFactory` for memory backends
- Config exists (`src/agent_labs/config.py`) but construction is scattered

---

### 3.3 Registry Pattern (Dynamic Discovery)
**Purpose**: Runtime discovery, registration, and selection of implementations.

**Example Use Cases**:
- **Tool Registry**: Register/discover tools by name/capability *(Already exists! See `src/agent_labs/tools/registry.py`)*
- **Provider Registry**: Select LLM provider by cost/latency/capability
- **Retrieval Strategy Registry**: Choose retrieval mode based on query intent

**Implementation Pattern**:
```python
from typing import Dict, List, Optional, Callable

class ProviderCapability(str, Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, Provider] = {}
        self._capabilities: Dict[str, List[ProviderCapability]] = {}
        self._cost_per_token: Dict[str, float] = {}
    
    def register(
        self, 
        name: str, 
        provider: Provider,
        capabilities: List[ProviderCapability],
        cost_per_1k_tokens: float = 0.0
    ):
        self._providers[name] = provider
        self._capabilities[name] = capabilities
        self._cost_per_token[name] = cost_per_1k_tokens
    
    def get(self, name: str) -> Optional[Provider]:
        return self._providers.get(name)
    
    def find_by_capability(
        self, 
        capability: ProviderCapability,
        max_cost: Optional[float] = None
    ) -> List[str]:
        """Find providers matching capability and cost constraints."""
        matches = []
        for name, caps in self._capabilities.items():
            if capability in caps:
                if max_cost is None or self._cost_per_token[name] <= max_cost:
                    matches.append(name)
        return matches
    
    def select_cheapest(self, capability: ProviderCapability) -> Optional[Provider]:
        """Select the cheapest provider for a capability."""
        candidates = self.find_by_capability(capability)
        if not candidates:
            return None
        
        cheapest = min(candidates, key=lambda n: self._cost_per_token[n])
        return self._providers[cheapest]

# Usage
registry = ProviderRegistry()
registry.register("ollama", OllamaProvider(), [ProviderCapability.CHAT], cost_per_1k_tokens=0.0)
registry.register("gpt-4", OpenAIProvider(), [ProviderCapability.CHAT, ProviderCapability.FUNCTION_CALLING], cost_per_1k_tokens=0.03)

# Select cheapest provider with function calling
provider = registry.select_cheapest(ProviderCapability.FUNCTION_CALLING)
```

**Current State**:
- ✅ **Tool Registry exists** in `src/agent_labs/tools/registry.py`
- ❌ No Provider Registry for LLM routing
- ❌ No Retrieval Strategy Registry

---

### 3.4 Applying Patterns to Each Component

| Component | Strategy Pattern | Factory Pattern | Registry Pattern | Current Level | Target Level |
|-----------|------------------|-----------------|------------------|---------------|--------------|
| **LLM Providers** | N/A (providers are strategies) | ❌ Missing | ❌ Missing | 1 | 3 |
| **Memory Storage** | ✅ Partial (ABCs exist) | ❌ Missing | ❌ Missing | 1 | 2-3 |
| **Context Chunking** | ❌ Missing | ❌ Missing | ⚠️ Optional | 1 | 2 |
| **Retrieval** | ❌ Missing | ❌ Missing | ❌ Missing | 1 | 2-3 |
| **Tools** | ✅ Base class exists | ⚠️ Partial | ✅ **Implemented!** | 2 | 3 |
| **Observability** | ✅ Exporters/Formatters | ⚠️ Partial | ⚠️ Optional | 2 | 2 |

---

## 4. Component Maturity Model (Target State)

We apply this 5-level model to guide the evolution of components.

*   **Level 0 (Hardcoded)**: Logic embedded in `if/else` statements.
*   **Level 1 (Interface)**: Abstract Base Classes (ABCs) defined, one implementation.
*   **Level 2 (Configurable)**: Factories create instances based on config files. *<-- WE ARE HERE*
*   **Level 3 (Registry/Platform)**: Dynamic discovery, conflict resolution, plugin architectures.
*   **Level 4 (Professional/Adaptive)**: Self-healing, routing based on latency/cost telemetry, extensive specialized backends.

---

## 5. Prioritized Action Plan

### Phase 1: The "Professional Data Layer" (Weeks 1-2)
1.  **Vector DB**: Replace `ChromaVectorStore` placeholder with actual implementation (or `pgvector`).
2.  **Postgres**: Add `PostgresStorage` backend to replace SQLite for concurrent workloads.
3.  **Lab Update**: Update Lab 04 (Memory) to include a "Production Setup" exercise using Docker Compose.

### Phase 2: The "Integration Layer" (Weeks 3-4)
4.  **MCP Core**: Implement `McpClient` in `src/agent_labs`.
5.  **MCP Lab**: Create a new mini-lab: "Connecting your Agent to the GitHub MCP Server".

### Phase 3: The "Engineering Discipline" (Weeks 5-6)
6.  **Eval Harness**: script to run 20 fixed inputs and assert semantic similarity > 0.9.
7.  **OTel**: Add `opentelemetry-sdk` dependency and a trace exporter.

---

## 5. Prioritized Action Plan

### Phase 0: Design Patterns Foundation (Week 0)
**Goal**: Establish the architectural patterns before building features.

0. **Add Design Patterns Lab/Module**:
   - Create `labs/09_design_patterns/` or add to existing labs
   - Teach Strategy, Factory, Registry patterns with agent-specific examples
   - Show refactoring from hardcoded → interface → factory → registry
   - Include exercises: "Refactor chunking to use Strategy pattern"

### Phase 1: The "Professional Data Layer" (Weeks 1-2)
1.  **Storage Factory**: Create `StorageFactory` in `src/agent_labs/memory/factory.py`
2.  **Vector DB**: Replace `ChromaVectorStore` placeholder with actual implementation (or `pgvector`).
3.  **Postgres**: Add `PostgresStorage` backend to replace SQLite for concurrent workloads.
4.  **Lab Update**: Update Lab 04 (Memory) to include a "Production Setup" exercise using Docker Compose + factory pattern.

### Phase 2: The "Integration Layer" (Weeks 3-4)
5.  **Provider Factory**: Create `ProviderFactory.create(config)` in `src/agent_labs/llm_providers/factory.py`
6.  **Provider Registry**: Implement `ProviderRegistry` with capability-based selection and cost tracking
7.  **MCP Core**: Implement `McpClient` in `src/agent_labs/mcp/`
8.  **MCP Lab**: Create a new mini-lab: "Connecting your Agent to the GitHub MCP Server"

### Phase 3: The "Engineering Discipline" (Weeks 5-6)
9.  **Eval Harness**: script to run 20 fixed inputs and assert semantic similarity > 0.9
10. **OTel**: Add `opentelemetry-sdk` dependency and a trace exporter
11. **Context Strategy**: Refactor chunking/packing to use Strategy pattern with factory selection

---

## 6. Detailed Implementation Guide: Factory Pattern for LLM Providers

**File**: `src/agent_labs/llm_providers/factory.py` (NEW)

```python
"""
LLM Provider Factory - Centralized provider construction.
"""
from typing import Optional
from .base import Provider
from .mock import MockProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .cloud import CloudProvider
from ..config import LLMProvider, ProviderConfig

class ProviderFactory:
    """Factory for creating LLM providers from configuration."""
    
    @staticmethod
    def create(provider_type: LLMProvider, config: Optional[ProviderConfig] = None) -> Provider:
        """
        Create a provider instance from configuration.
        
        Args:
            provider_type: Type of provider to create
            config: Optional configuration (auto-created if None)
        
        Returns:
            Configured provider instance
        
        Raises:
            ValueError: If provider type is unknown or config is invalid
        
        Example:
            >>> factory = ProviderFactory()
            >>> provider = factory.create(LLMProvider.OLLAMA)
            >>> response = await provider.query("Hello")
        """
        if config is None:
            config = ProviderConfig(provider_type)
        
        if provider_type == LLMProvider.MOCK:
            return MockProvider(responses=config.model or ["Mock response"])
        
        elif provider_type == LLMProvider.OLLAMA:
            if not config.model:
                raise ValueError("Ollama provider requires 'model' in config")
            return OllamaProvider(
                model=config.model,
                base_url=config.base_url or "http://localhost:11434",
                timeout=config.timeout
            )
        
        elif provider_type == LLMProvider.OPENAI:
            if not config.api_key:
                raise ValueError("OpenAI provider requires 'OPENAI_API_KEY' environment variable")
            return OpenAIProvider(
                api_key=config.api_key,
                model=config.model or "gpt-3.5-turbo",
                timeout=config.timeout
            )
        
        elif provider_type in [LLMProvider.ANTHROPIC, LLMProvider.GOOGLE, LLMProvider.AZURE_OPENAI]:
            if not config.api_key:
                raise ValueError(f"{provider_type.value} provider requires API key")
            return CloudProvider(
                provider=provider_type.value,
                api_key=config.api_key,
                model=config.model,
                timeout=config.timeout
            )
        
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def create_from_env() -> Provider:
        """
        Create provider from environment variables.
        
        Uses LLM_PROVIDER env var to determine provider type.
        
        Returns:
            Configured provider instance
        """
        import os
        provider_name = os.getenv("LLM_PROVIDER", "mock")
        provider_type = LLMProvider(provider_name)
        return ProviderFactory.create(provider_type)
```

**Update**: `src/agent_labs/config.py`

Add convenience method:
```python
class ProviderConfig:
    # ... existing code ...
    
    def create_provider(self) -> "Provider":
        """Create provider instance from this config."""
        from .llm_providers.factory import ProviderFactory
        return ProviderFactory.create(self.provider, self)
```

---

## 7. Lab Architecture: Example "Professional" Lab Spec

**New Lab: "Production RAG with MCP & Evaluation"**

*   **Goal**: Build a RAG agent that uses a remote MCP server for content validation and checks itself against a Golden Set.
*   **Stack**:
    *   **Memory**: Postgres (Vector + Relational) via Factory pattern.
    *   **Tools**: MCP Client connecting to a local file server.
    *   **Observability**: Traces exported to a local Jaeger instance.
*   **Flow**:
    1.  User query -> **Auth Gate** (Safety).
    2.  **Router** decides "Consult Knowledge Base".
    3.  **Retriever** (Strategy pattern) queries Postgres Vector Store.
    4.  LLM (via Factory) Synthesizes answer.
    5.  **Eval Loop**: Async check of answer quality against reference.

---

## 8. Curriculum Integration: Teaching Design Patterns

### 8.1 Where Patterns Fit in Learning Progression

**Beginner Level**: Focus on understanding components
- Labs 01-03: Basic concepts, no patterns needed
- Students learn "what" before "how to organize"

**Intermediate Level**: Introduce patterns through refactoring *(RECOMMENDED INSERTION POINT)*
- **Lab 04 (Memory)**: Introduce Strategy pattern for chunking
- **Lab 05 (Context)**: Add Factory pattern for backend selection
- **New Lab 09**: "Refactoring for Production: Design Patterns"

**Advanced Level**: Apply patterns to complex systems
- Multi-agent coordination using Registry pattern
- Dynamic routing with telemetry-driven selection

**Pro Level**: Pattern composition and trade-offs
- When to use Factory vs Registry vs Builder
- Performance implications of abstraction layers

---

### 8.2 Proposed Lab 09: Design Patterns for Agents

**Lab 09: Refactoring for Production: Design Patterns**

**Learning Objectives**:
1. Recognize when hardcoded logic should become a pattern
2. Implement Strategy, Factory, and Registry patterns
3. Refactor existing code to use patterns
4. Understand trade-offs (flexibility vs complexity)

**Lab Structure**:

#### Exercise 1: Strategy Pattern (Chunking)
**Before (Hardcoded)**:
```python
def chunk_text(text: str, method: str = "fixed"):
    if method == "fixed":
        return [text[i:i+512] for i in range(0, len(text), 512)]
    elif method == "sentence":
        return text.split(". ")
    else:
        raise ValueError("Unknown method")
```

**After (Strategy Pattern)**:
```python
class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]: pass

class FixedSizeChunker(ChunkingStrategy):
    def chunk(self, text: str) -> List[str]:
        return [text[i:i+512] for i in range(0, len(text), 512)]

# Usage: strategy = FixedSizeChunker(); chunks = strategy.chunk(text)
```

**Task**: Implement `SemanticChunker` and `RecursiveChunker` strategies.

---

#### Exercise 2: Factory Pattern (Storage Backends)
**Before (Scattered Construction)**:
```python
# In main.py
if os.getenv("STORAGE") == "sqlite":
    storage = SqliteStorage("data.db")
elif os.getenv("STORAGE") == "postgres":
    storage = PostgresStorage(host="localhost")
else:
    storage = InMemoryStorage()

# In test.py
storage = InMemoryStorage()  # Duplicated logic

# In server.py
storage = SqliteStorage("prod.db")  # Duplicated logic
```

**After (Factory Pattern)**:
```python
# storage/factory.py
class StorageFactory:
    @staticmethod
    def create_from_config(config: dict) -> StorageBackend:
        storage_type = config.get("type", "memory")
        if storage_type == "sqlite":
            return SqliteStorage(config["path"])
        elif storage_type == "postgres":
            return PostgresStorage(**config["postgres"])
        return InMemoryStorage()

# Everywhere else
storage = StorageFactory.create_from_config(config)
```

**Task**: Add Redis backend to factory; update tests to use factory.

---

#### Exercise 3: Registry Pattern (Dynamic Tool Selection)
**Scenario**: Agent needs to select best tool based on cost/latency constraints.

**Before (Manual Selection)**:
```python
if budget > 10 and "search" in query:
    tool = WebSearchTool()
elif "calculate" in query:
    tool = CalculatorTool()
else:
    tool = DefaultTool()
```

**After (Registry Pattern)**:
```python
registry = ToolRegistry()
registry.register("web_search", WebSearchTool(), cost=5, capabilities=["search"])
registry.register("calculator", CalculatorTool(), cost=0, capabilities=["math"])

# Smart selection
tool = registry.select_by_cost_and_capability(
    capability="search",
    max_cost=budget
)
```

**Task**: Implement `ToolRegistry.select_by_cost_and_capability()`.

---

#### Exercise 4: Refactoring Challenge
**Given**: A messy agent implementation with hardcoded LLM selection, storage, and chunking.

**Task**: Refactor to use:
1. Factory for LLM provider creation
2. Strategy for chunking method
3. Registry for tool discovery

**Acceptance Criteria**:
- No `if provider == "ollama"` blocks outside factory
- All storage creation goes through `StorageFactory`
- Tests pass with mock implementations

---

### 8.3 Pattern Decision Tree (For Students)

```
┌─────────────────────────────────────────┐
│ Do you have multiple algorithms that    │
│ need to be swapped at runtime?          │
└──────────────┬──────────────────────────┘
               │
         Yes   │   No
               │
        ┌──────▼──────┐
        │   STRATEGY  │
        │   PATTERN   │
        └─────────────┘

┌─────────────────────────────────────────┐
│ Do you have complex object creation     │
│ logic scattered across your codebase?   │
└──────────────┬──────────────────────────┘
               │
         Yes   │   No
               │
        ┌──────▼──────┐
        │   FACTORY   │
        │   PATTERN   │
        └─────────────┘

┌─────────────────────────────────────────┐
│ Do you need runtime discovery and       │
│ selection of implementations?           │
└──────────────┬──────────────────────────┘
               │
         Yes   │   No
               │
        ┌──────▼──────┐
        │  REGISTRY   │
        │   PATTERN   │
        └─────────────┘
```

---

### 8.4 Anti-Patterns to Avoid (Teach Explicitly)

**❌ God Factory**: One factory that creates everything
```python
# BAD
class ComponentFactory:
    def create_provider(self, ...): ...
    def create_storage(self, ...): ...
    def create_tool(self, ...): ...
    # 20 more create methods...
```

**✅ Separate Factories**: One factory per component family
```python
# GOOD
ProviderFactory.create(...)
StorageFactory.create(...)
ToolFactory.create(...)
```

---

**❌ Registry Sprawl**: Registries for everything
```python
# BAD: You don't need a registry for simple config
class TemplateRegistry:
    def register(self, template): ...
# Just use a dict or enum!
```

**✅ Use Registry Only When Needed**: Dynamic discovery, plugin systems, cost-based routing

---

**❌ Over-Abstraction**: Adding patterns before you need them
```python
# BAD: If you only have one implementation
class LoggerStrategy(ABC): pass  # Why?
```

**✅ Rule of Three**: Add abstraction after 3rd duplicate

---

## 9. Cross-Reference: Where Patterns Exist Today

| Pattern | Existing Implementation | Location | Maturity |
|---------|------------------------|----------|----------|
| **Strategy** | Tool base class | `src/agent_labs/tools/base.py` | ✅ Solid |
| **Registry** | Tool registry | `src/agent_labs/tools/registry.py` | ✅ **Excellent** |
| **Factory** | `sqlite_backend()` helper | `src/agent_labs/memory/long_term.py` | ⚠️ Ad-hoc |
| **ABC/Protocol** | StorageBackend, Provider | `src/agent_labs/memory/storage.py`, `llm_providers/base.py` | ✅ Solid |

**Action**: Elevate the ad-hoc `sqlite_backend()` to a proper `StorageFactory` and document pattern usage.

---

## 10. Summary: Gap Closure Roadmap

### Critical Gaps (Must Close for Professional Use)
1. ✅ **MCP Integration**: Protocol + Lab
2. ✅ **Production Storage**: Postgres + pgvector implementations
3. ✅ **Factory Pattern**: Provider + Storage factories
4. ✅ **Evaluation Gates**: CI-integrated golden set runner

### Important Gaps (Should Close for Scalability)
5. ✅ **Provider Registry**: Cost/capability-based routing
6. ✅ **OTel Exporter**: Standard observability
7. ✅ **Strategy Refactor**: Context chunking/packing

### Nice-to-Have (Enhances Flexibility)
8. ✅ **Checkpoint/Resume**: Long-running workflow state
9. ⚠️ **Graph DB**: Optional for relationship-heavy domains
10. ⚠️ **Multi-tenant isolation**: Data-layer scoping

---

**Document Status**: ✅ Complete  
**Next Action**: Prioritize gaps → Create Stories → Implement in phases  
**Framework Integration**: All changes follow space_framework governance (Story → PR → Review → Merge)