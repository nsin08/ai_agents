# Chapter 06: Integration Patterns

[Prev](chapter_05_multi_turn_conversations.md) | [Up](README.md) | [Next: Level 3 Workbook](../03_advanced/02_workbook.md)

---

## Learning Objectives

After completing this chapter, you will be able to:

1. **Connect Agents to External APIs** — Build tool wrappers for REST, GraphQL, and gRPC services
2. **Handle Authentication** — Implement OAuth, API keys, and token refresh patterns
3. **Design Webhook Handlers** — Build event-driven agents that respond to external triggers
4. **Implement Retry and Circuit Breakers** — Build resilient integrations that handle failures
5. **Build Composable Tool Architectures** — Create reusable tool libraries with consistent contracts

---

## Introduction

An agent is only as useful as its tools. While simple calculators and string utilities are great for learning, production agents need to integrate with external systems: databases, APIs, message queues, and cloud services.

This chapter teaches integration patterns that make agents production-ready: authentication, retry logic, circuit breakers, and event-driven architectures.

**Key Insight:** Integration code is where most agent failures occur. Robust error handling and retry logic are not optional—they're essential.

## Hands-on (Lane A)

- Lab 09: MCP tool servers (offline foundations): `../../../labs/09/README.md`
- Related code: `../../../src/agent_labs/mcp/` and `../../../src/agent_labs/tools/`

---

## 1. Tool Architecture Overview

### 1.1 The Tool Abstraction

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TOOL ARCHITECTURE LAYERS                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Agent Orchestrator                        │ │
│  │                 (decides which tools to call)                  │ │
│  └───────────────────────────┬────────────────────────────────────┘ │
│                              │                                      │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Tool Registry                             │ │
│  │           (manages tools, validates inputs, executes)          │ │
│  └───────────────────────────┬────────────────────────────────────┘ │
│                              │                                      │
│         ┌────────────────────┼────────────────────┐                 │
│         ▼                    ▼                    ▼                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐             │
│  │   Tool A     │   │   Tool B     │   │   Tool C     │             │
│  │ (Calculator) │   │ (Weather)    │   │ (Database)   │             │
│  └──────────────┘   └──────────────┘   └──────────────┘             │
│         │                    │                    │                 │
│         ▼                    ▼                    ▼                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐             │
│  │   Internal   │   │   REST API   │   │  PostgreSQL  │             │
│  │   Logic      │   │   (HTTP)     │   │   (Async)    │             │
│  └──────────────┘   └──────────────┘   └──────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Components

From the codebase's tool architecture:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime

class ExecutionStatus(Enum):
    """Status of tool execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    NOT_FOUND = "not_found"

@dataclass
class ToolResult:
    """Result from tool execution."""
    status: ExecutionStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    retries: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS

class Tool(ABC):
    """Abstract base class for all tools."""

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the schema describing this tool."""
        pass
```

---

## 2. Building API Tool Wrappers

### 2.1 REST API Tool Pattern

```python
import aiohttp
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class ToolContract:
    """Contract defining a tool's interface."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
    tags: list = field(default_factory=list)

class WeatherTool(Tool):
    """Weather API tool wrapper."""

    def __init__(self, api_key: str, base_url: str = "https://api.weather.com"):
        self.name = "weather"
        self.api_key = api_key
        self.base_url = base_url
        self.contract = ToolContract(
            name=self.name,
            description="Get current weather for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "conditions": {"type": "string"},
                    "humidity": {"type": "number"}
                }
            },
            tags=["weather", "api", "external"]
        )

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()

    async def execute(self, **kwargs) -> ToolResult:
        """Fetch weather data from API."""
        import time
        start = time.perf_counter()
        
        location = kwargs.get("location")
        units = kwargs.get("units", "celsius")
        
        if not location:
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                error="Missing required parameter: location",
                latency_ms=(time.perf_counter() - start) * 1000
            )

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/current"
                params = {
                    "q": location,
                    "units": units,
                    "appid": self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ToolResult(
                            status=ExecutionStatus.SUCCESS,
                            output={
                                "temperature": data["main"]["temp"],
                                "conditions": data["weather"][0]["description"],
                                "humidity": data["main"]["humidity"]
                            },
                            metadata={"location": location, "units": units},
                            latency_ms=(time.perf_counter() - start) * 1000
                        )
                    else:
                        return ToolResult(
                            status=ExecutionStatus.FAILURE,
                            error=f"API returned status {response.status}",
                            latency_ms=(time.perf_counter() - start) * 1000
                        )

        except aiohttp.ClientError as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=f"Network error: {str(e)}",
                latency_ms=(time.perf_counter() - start) * 1000
            )
```

### 2.2 Database Tool Pattern

```python
import asyncpg
from typing import List, Dict, Any

class DatabaseTool(Tool):
    """PostgreSQL database query tool."""

    def __init__(self, connection_string: str):
        self.name = "database"
        self.connection_string = connection_string
        self._pool: Optional[asyncpg.Pool] = None
        self.contract = ToolContract(
            name=self.name,
            description="Execute read-only database queries",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "params": {
                        "type": "array",
                        "description": "Query parameters",
                        "items": {"type": ["string", "number", "boolean"]}
                    }
                },
                "required": ["query"]
            },
            tags=["database", "sql", "read"]
        )

    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=5
            )
        return self._pool

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()

    async def execute(self, **kwargs) -> ToolResult:
        """Execute database query."""
        import time
        start = time.perf_counter()
        
        query = kwargs.get("query", "")
        params = kwargs.get("params", [])
        
        # Security: Only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return ToolResult(
                status=ExecutionStatus.INVALID_INPUT,
                error="Only SELECT queries are allowed",
                latency_ms=(time.perf_counter() - start) * 1000
            )

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                result = [dict(row) for row in rows]
                
                return ToolResult(
                    status=ExecutionStatus.SUCCESS,
                    output=result,
                    metadata={
                        "row_count": len(result),
                        "query": query[:100]  # Truncate for logging
                    },
                    latency_ms=(time.perf_counter() - start) * 1000
                )

        except asyncpg.PostgresError as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=f"Database error: {str(e)}",
                latency_ms=(time.perf_counter() - start) * 1000
            )

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
```

---

## 3. Authentication Patterns

### 3.1 API Key Authentication

```python
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class AuthConfig:
    """Authentication configuration."""
    method: str  # "api_key", "bearer", "oauth2"
    credentials: Dict[str, str]
    header_name: str = "Authorization"

class AuthenticatedTool(Tool):
    """Base class for tools requiring authentication."""

    def __init__(self, auth_config: AuthConfig):
        self.auth_config = auth_config

    def _get_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers."""
        method = self.auth_config.method
        creds = self.auth_config.credentials
        
        if method == "api_key":
            return {
                self.auth_config.header_name: creds.get("api_key", "")
            }
        elif method == "bearer":
            return {
                self.auth_config.header_name: f"Bearer {creds.get('token', '')}"
            }
        elif method == "basic":
            import base64
            credentials = f"{creds.get('username', '')}:{creds.get('password', '')}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {
                self.auth_config.header_name: f"Basic {encoded}"
            }
        
        return {}
```

### 3.2 OAuth2 with Token Refresh

```python
import time
from dataclasses import dataclass
from typing import Optional
import aiohttp

@dataclass
class OAuth2Token:
    """OAuth2 token container."""
    access_token: str
    refresh_token: Optional[str]
    expires_at: float  # Unix timestamp

class OAuth2AuthProvider:
    """OAuth2 authentication with automatic token refresh."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        refresh_buffer: int = 300,  # Refresh 5 min before expiry
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.refresh_buffer = refresh_buffer
        self._token: Optional[OAuth2Token] = None

    def _is_token_expired(self) -> bool:
        """Check if token needs refresh."""
        if not self._token:
            return True
        return time.time() > (self._token.expires_at - self.refresh_buffer)

    async def _refresh_token(self) -> None:
        """Refresh the access token."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "grant_type": "refresh_token",
                "refresh_token": self._token.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            async with session.post(self.token_url, data=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self._token = OAuth2Token(
                        access_token=data["access_token"],
                        refresh_token=data.get("refresh_token", self._token.refresh_token),
                        expires_at=time.time() + data.get("expires_in", 3600),
                    )
                else:
                    raise Exception(f"Token refresh failed: {response.status}")

    async def get_access_token(self) -> str:
        """Get valid access token, refreshing if needed."""
        if self._is_token_expired():
            await self._refresh_token()
        return self._token.access_token

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        token = await self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

class OAuth2Tool(Tool):
    """Tool with OAuth2 authentication."""

    def __init__(self, auth_provider: OAuth2AuthProvider):
        self.auth_provider = auth_provider

    async def _make_authenticated_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """Make request with automatic token refresh."""
        headers = await self.auth_provider.get_auth_headers()
        headers.update(kwargs.pop("headers", {}))
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, **kwargs
            ) as response:
                return response
```

---

## 4. Retry and Circuit Breaker Patterns

### 4.1 Exponential Backoff Retry

```python
import asyncio
import random
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar("T")

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt number."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay

def with_retry(config: RetryConfig):
    """Decorator for adding retry logic to async functions."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        delay = config.get_delay(attempt)
                        await asyncio.sleep(delay)
                    else:
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator

# Usage
retry_config = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    retryable_exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
)

class RetryableWeatherTool(WeatherTool):
    """Weather tool with retry logic."""

    @with_retry(retry_config)
    async def execute(self, **kwargs) -> ToolResult:
        return await super().execute(**kwargs)
```

### 4.2 Circuit Breaker Pattern

```python
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5      # Failures before opening
    recovery_timeout: float = 30.0  # Seconds before half-open
    success_threshold: int = 2      # Successes to close from half-open

class CircuitBreaker:
    """Circuit breaker for protecting external calls."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None

    def _should_attempt(self) -> bool:
        """Check if request should be attempted."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        
        # HALF_OPEN - allow limited requests
        return True

    def record_success(self) -> None:
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker."""
        if not self._should_attempt():
            raise CircuitOpenError(f"Circuit '{self.name}' is open")
        
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise

class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

class CircuitProtectedTool(Tool):
    """Tool with circuit breaker protection."""

    def __init__(self, tool: Tool, breaker_config: CircuitBreakerConfig):
        self.inner_tool = tool
        self.name = tool.name
        self.breaker = CircuitBreaker(tool.name, breaker_config)

    def get_schema(self) -> Dict[str, Any]:
        return self.inner_tool.get_schema()

    async def execute(self, **kwargs) -> ToolResult:
        """Execute with circuit breaker protection."""
        try:
            return await self.breaker.call(
                self.inner_tool.execute, **kwargs
            )
        except CircuitOpenError:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=f"Circuit breaker open for tool '{self.name}'",
                metadata={"circuit_state": self.breaker.state.value}
            )
```

---

## 5. Event-Driven Agent Patterns

### 5.1 Webhook Handler

```python
from dataclasses import dataclass
from typing import Dict, Any, Callable, Awaitable
from enum import Enum

class WebhookEventType(str, Enum):
    MESSAGE_RECEIVED = "message.received"
    TASK_COMPLETED = "task.completed"
    PAYMENT_PROCESSED = "payment.processed"
    USER_SIGNUP = "user.signup"

@dataclass
class WebhookEvent:
    """Incoming webhook event."""
    event_type: WebhookEventType
    payload: Dict[str, Any]
    timestamp: float
    signature: Optional[str] = None

class WebhookHandler:
    """Handles incoming webhooks and routes to agent."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self._handlers: Dict[WebhookEventType, Callable] = {}

    def register_handler(
        self,
        event_type: WebhookEventType,
        handler: Callable[[WebhookEvent], Awaitable[None]]
    ) -> None:
        """Register handler for event type."""
        self._handlers[event_type] = handler

    def verify_signature(self, event: WebhookEvent) -> bool:
        """Verify webhook signature."""
        import hmac
        import hashlib
        import json
        
        if not event.signature:
            return False
        
        payload_bytes = json.dumps(event.payload).encode()
        expected = hmac.new(
            self.secret_key.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(event.signature, expected)

    async def handle_event(self, event: WebhookEvent) -> Dict[str, Any]:
        """Process incoming webhook event."""
        # Verify signature
        if not self.verify_signature(event):
            return {"status": "error", "message": "Invalid signature"}
        
        # Find handler
        handler = self._handlers.get(event.event_type)
        if not handler:
            return {"status": "ignored", "message": f"No handler for {event.event_type}"}
        
        # Execute handler
        try:
            await handler(event)
            return {"status": "processed", "event_type": event.event_type.value}
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

### 5.2 Event-Driven Agent

```python
import asyncio
from typing import Dict, Any, List

class EventDrivenAgent:
    """Agent that responds to external events."""

    def __init__(self, webhook_handler: WebhookHandler):
        self.webhook_handler = webhook_handler
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
        # Register webhook handlers
        self.webhook_handler.register_handler(
            WebhookEventType.MESSAGE_RECEIVED,
            self._handle_message
        )
        self.webhook_handler.register_handler(
            WebhookEventType.TASK_COMPLETED,
            self._handle_task_completed
        )

    async def _handle_message(self, event: WebhookEvent) -> None:
        """Handle incoming message event."""
        message = event.payload.get("message", "")
        user_id = event.payload.get("user_id")
        
        # Queue for processing
        await self.event_queue.put({
            "type": "message",
            "content": message,
            "user_id": user_id,
        })

    async def _handle_task_completed(self, event: WebhookEvent) -> None:
        """Handle task completion event."""
        task_id = event.payload.get("task_id")
        result = event.payload.get("result")
        
        await self.event_queue.put({
            "type": "task_result",
            "task_id": task_id,
            "result": result,
        })

    async def process_events(self) -> None:
        """Main event processing loop."""
        self._running = True
        
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                await self._process_event(event)
                
            except asyncio.TimeoutError:
                continue

    async def _process_event(self, event: Dict[str, Any]) -> None:
        """Process a single event."""
        event_type = event.get("type")
        
        if event_type == "message":
            response = await self._generate_response(event["content"])
            await self._send_response(event["user_id"], response)
        
        elif event_type == "task_result":
            await self._handle_task_result(
                event["task_id"],
                event["result"]
            )

    async def _generate_response(self, message: str) -> str:
        """Generate response to message."""
        # Agent processing logic here
        return f"Processed: {message}"

    async def _send_response(self, user_id: str, response: str) -> None:
        """Send response to user."""
        # Send via appropriate channel
        pass

    async def _handle_task_result(self, task_id: str, result: Any) -> None:
        """Handle completed task result."""
        pass

    def stop(self) -> None:
        """Stop the event processing loop."""
        self._running = False
```

---

## 6. Tool Registry Pattern

### 6.1 Centralized Tool Management

```python
from typing import Dict, List, Optional
import time

class ToolRegistry:
    """Registry for managing and executing tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool in the registry."""
        if not hasattr(tool, "name"):
            raise AttributeError("Tool must have a 'name' attribute")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """Unregister a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """Get a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_all_schemas(self) -> Dict[str, Dict]:
        """Get schemas for all registered tools."""
        return {name: tool.get_schema() for name, tool in self._tools.items()}

    async def execute(
        self,
        name: str,
        validate_input: bool = True,
        **kwargs
    ) -> ToolResult:
        """Execute a tool by name."""
        start_time = time.perf_counter()
        
        tool = self.get(name)
        
        if tool is None:
            return ToolResult(
                status=ExecutionStatus.NOT_FOUND,
                error=f"Tool '{name}' not found. Available: {self.list_tools()}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )

        try:
            result = await tool.execute(**kwargs)
            return result
            
        except Exception as e:
            return ToolResult(
                status=ExecutionStatus.FAILURE,
                error=f"Error executing tool '{name}': {str(e)}",
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
```

### 6.2 Tool Discovery and Documentation

```python
class ToolDocumentation:
    """Generate documentation for registered tools."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def generate_markdown(self) -> str:
        """Generate Markdown documentation for all tools."""
        lines = ["# Available Tools\n"]
        
        for name in sorted(self.registry.list_tools()):
            tool = self.registry.get(name)
            schema = tool.get_schema()
            
            lines.append(f"## {name}\n")
            lines.append(f"{schema.get('description', 'No description')}\n")
            
            # Parameters
            params = schema.get("parameters", {}).get("properties", {})
            required = schema.get("parameters", {}).get("required", [])
            
            if params:
                lines.append("### Parameters\n")
                lines.append("| Name | Type | Required | Description |")
                lines.append("|------|------|----------|-------------|")
                
                for param_name, param_info in params.items():
                    param_type = param_info.get("type", "any")
                    is_required = "Yes" if param_name in required else "No"
                    desc = param_info.get("description", "")
                    lines.append(f"| {param_name} | {param_type} | {is_required} | {desc} |")
                
                lines.append("")
        
        return "\n".join(lines)

    def generate_openapi(self) -> Dict[str, Any]:
        """Generate OpenAPI spec for tools."""
        paths = {}
        
        for name in self.registry.list_tools():
            tool = self.registry.get(name)
            schema = tool.get_schema()
            
            paths[f"/tools/{name}"] = {
                "post": {
                    "summary": schema.get("description", ""),
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": schema.get("parameters", {})
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Successful execution"}
                    }
                }
            }
        
        return {
            "openapi": "3.0.0",
            "info": {"title": "Agent Tools API", "version": "1.0.0"},
            "paths": paths
        }
```

### 6.3 Standardized Tool Servers (MCP)

As tool ecosystems grow, integrations become painful:

- You end up re-implementing the same wrapper patterns for every system.
- Tool discovery is ad-hoc ("what tools exist in this deployment?").
- Remote tools blur security boundaries (auth, audit, tenant isolation).

**Model Context Protocol (MCP)** is a standard that helps solve this by treating tools as **discoverable capabilities** exposed by a tool server.

At a high level:

- **MCP server**: publishes tools (name, description, input schema) and executes them.
- **MCP client**: lists available tools and invokes them with structured arguments.
- **Tool schema**: defines contracts similar to what we already do with `ToolContract`.

#### Mapping MCP to this repo's tool system

You can treat an MCP tool as a normal tool in your `ToolRegistry`:

1. Discover tools via MCP (`list_tools()`).
2. Convert tool schema to `ToolContract` (name/description/input schema).
3. Wrap each MCP tool behind a local `Tool` implementation.
4. Execute via `ToolRegistry.execute(...)` so you get validation, errors, and consistent results.

#### Error taxonomy + observability

For production-capable integrations, standardize these:

- **Timeouts**: MCP call exceeds deadline -> `ExecutionStatus.TIMEOUT`
- **Invalid input**: MCP server rejects args -> `ExecutionStatus.INVALID_INPUT`
- **Not found**: tool name missing -> `ExecutionStatus.NOT_FOUND`
- **Connection**: server unreachable -> `ExecutionStatus.FAILURE` (with clear error message)

Always emit correlation fields around remote tool calls:

- `request_id` / `run_id`
- `tool_name`
- `tool_call_id`
- `tenant_id` (if multi-tenant)

These are critical for debugging and audit.

---

## 7. Integration Testing

### 7.1 Mock Tool for Testing

```python
class MockTool(Tool):
    """Mock tool for testing without external dependencies."""

    def __init__(
        self,
        name: str,
        responses: List[ToolResult] = None,
        delay_ms: float = 0,
    ):
        self.name = name
        self.responses = responses or []
        self.delay_ms = delay_ms
        self.call_count = 0
        self.call_history: List[Dict] = []
        self.contract = ToolContract(
            name=name,
            description=f"Mock tool: {name}",
            input_schema={"type": "object", "properties": {}},
        )

    def get_schema(self) -> Dict[str, Any]:
        return self.contract.to_dict()

    async def execute(self, **kwargs) -> ToolResult:
        """Execute mock tool."""
        self.call_history.append(kwargs)
        self.call_count += 1
        
        if self.delay_ms > 0:
            await asyncio.sleep(self.delay_ms / 1000)
        
        if self.responses:
            return self.responses[(self.call_count - 1) % len(self.responses)]
        
        return ToolResult(
            status=ExecutionStatus.SUCCESS,
            output={"mock": True, "call_count": self.call_count},
        )

# Usage in tests
async def test_agent_uses_weather_tool():
    """Test that agent calls weather tool correctly."""
    mock_weather = MockTool(
        name="weather",
        responses=[
            ToolResult(
                status=ExecutionStatus.SUCCESS,
                output={"temperature": 22, "conditions": "sunny"}
            )
        ]
    )
    
    registry = ToolRegistry()
    registry.register(mock_weather)
    
    # Run agent with mock tool
    # ... agent code ...
    
    assert mock_weather.call_count == 1
    assert mock_weather.call_history[0]["location"] == "Seattle"
```

### 7.2 Integration Test Pattern

```python
import pytest

class TestWeatherToolIntegration:
    """Integration tests for weather tool."""

    @pytest.fixture
    def weather_tool(self):
        """Create weather tool with test API key."""
        return WeatherTool(
            api_key="test_api_key",
            base_url="https://api.test.weather.com"
        )

    @pytest.mark.asyncio
    async def test_successful_weather_fetch(self, weather_tool, httpx_mock):
        """Test successful weather API call."""
        httpx_mock.add_response(
            json={
                "main": {"temp": 22.5, "humidity": 65},
                "weather": [{"description": "clear sky"}]
            }
        )
        
        result = await weather_tool.execute(location="Seattle")
        
        assert result.success
        assert result.output["temperature"] == 22.5
        assert result.output["conditions"] == "clear sky"

    @pytest.mark.asyncio
    async def test_api_error_handling(self, weather_tool, httpx_mock):
        """Test handling of API errors."""
        httpx_mock.add_response(status_code=500)
        
        result = await weather_tool.execute(location="Seattle")
        
        assert not result.success
        assert result.status == ExecutionStatus.FAILURE
        assert "500" in result.error
```

---

## Summary

### Key Takeaways

1. **Tool abstractions** provide consistent interfaces for diverse backends (APIs, databases, services).

2. **Authentication patterns** (API keys, OAuth2) must handle token refresh and secure credential storage.

3. **Retry with exponential backoff** handles transient failures; circuit breakers prevent cascade failures.

4. **Event-driven patterns** enable agents to respond to webhooks and external triggers.

5. **Tool registries** centralize management, validation, and documentation.

6. **Mock tools** enable testing without external dependencies.

### What's Next

This concludes the Intermediate curriculum. You now have the skills to build production-capable agents. Continue to the **Advanced curriculum** to learn multi-agent orchestration, human-in-the-loop patterns, and enterprise deployment.

---

## References

- **Tool Module:** [src/agent_labs/tools/](../../../src/agent_labs/tools/)
- **Tool Registry:** [src/agent_labs/tools/registry.py](../../../src/agent_labs/tools/registry.py)
- **Tool Contracts:** [src/agent_labs/tools/contract.py](../../../src/agent_labs/tools/contract.py)
- **aiohttp docs:** [aiohttp.readthedocs.io](https://docs.aiohttp.org/)
- **Circuit Breaker Pattern:** [martinfowler.com/bliki/CircuitBreaker.html](https://martinfowler.com/bliki/CircuitBreaker.html)

---

## Exercises

Complete these exercises in the workbook to reinforce your learning:

1. **API Tool Wrapper:** Create a tool that wraps a public API (e.g., GitHub, OpenWeatherMap) with proper authentication and error handling.

2. **Retry Logic:** Implement exponential backoff retry for an API tool. Test with a mock that fails on first 2 attempts.

3. **Circuit Breaker:** Implement a circuit breaker that opens after 3 failures and recovers after 30 seconds.

4. **Webhook Handler:** Build a webhook endpoint that triggers agent processing for incoming events.

5. **Tool Documentation:** Generate Markdown documentation for a registry with 5+ tools.

---

[Prev](chapter_05_multi_turn_conversations.md) | [Up](README.md) | [Next: Level 3 Workbook](../03_advanced/02_workbook.md)
