"""Configuration models for agent_core."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    name: str = "agent_core_app"
    environment: str = "local"


class EngineConfig(BaseModel):
    key: str = "local"
    config: Dict[str, Any] = Field(default_factory=dict)


class ModelSpec(BaseModel):
    provider: str
    model: str
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    timeout_s: Optional[float] = None
    capabilities: Optional[List[str]] = None


class ModelsConfig(BaseModel):
    roles: Dict[str, ModelSpec] = Field(default_factory=dict)


class ToolsConfig(BaseModel):
    allowlist: List[str] = Field(default_factory=list)
    providers: Dict[str, Any] = Field(default_factory=dict)


class BackendConfig(BaseModel):
    backend: str
    config: Dict[str, Any] = Field(default_factory=dict)


class RetrievalConfig(BaseModel):
    gating: str = "none"
    vectorstore: BackendConfig = Field(default_factory=lambda: BackendConfig(backend="memory"))


class MemoryConfig(BaseModel):
    session_store: BackendConfig = Field(default_factory=lambda: BackendConfig(backend="memory"))
    long_term_store: BackendConfig = Field(default_factory=lambda: BackendConfig(backend="disabled"))
    run_store: BackendConfig = Field(default_factory=lambda: BackendConfig(backend="memory"))


class BudgetsConfig(BaseModel):
    max_tool_calls: int = 0
    max_run_seconds: int = 0
    max_total_tokens: int = 0


class PoliciesConfig(BaseModel):
    read_only: bool = True
    budgets: BudgetsConfig = Field(default_factory=BudgetsConfig)


class RedactConfig(BaseModel):
    pii: bool = True
    secrets: bool = True


class ObservabilityConfig(BaseModel):
    exporter: str = "stdout_json"
    redact: RedactConfig = Field(default_factory=RedactConfig)


class GateConfig(BaseModel):
    min_average_score: float = 0.0
    max_regression: float = 0.0


class EvaluationConfig(BaseModel):
    enabled: bool = False
    gate: GateConfig = Field(default_factory=GateConfig)


class ArtifactsConfig(BaseModel):
    store: BackendConfig = Field(default_factory=lambda: BackendConfig(backend="filesystem"))


class AuthConfig(BaseModel):
    mode: str = "none"


class ServiceConfig(BaseModel):
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8080
    auth: AuthConfig = Field(default_factory=AuthConfig)


class AgentCoreConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    mode: str = "real"
    engine: EngineConfig = Field(default_factory=EngineConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    policies: PoliciesConfig = Field(default_factory=PoliciesConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    artifacts: ArtifactsConfig = Field(default_factory=ArtifactsConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)

    def validate_deterministic(self) -> None:
        if self.mode != "deterministic":
            return
        for role, spec in self.models.roles.items():
            if spec.provider not in {"mock"}:
                raise ValueError(
                    f"Deterministic mode requires mock providers. "
                    f"Role '{role}' uses provider '{spec.provider}'."
                )
        if "fixture" not in self.tools.providers:
            raise ValueError(
                "Deterministic mode requires fixture tool provider configuration. "
                "Set tools.providers.fixture in config."
            )
        fixture_config = self.tools.providers.get("fixture", {})
        fixture_path = ""
        if isinstance(fixture_config, dict):
            fixture_path = str(fixture_config.get("path") or "").strip()
        if not fixture_path:
            raise ValueError(
                "Deterministic mode requires fixture tool provider path. "
                "Set tools.providers.fixture.path in config."
            )
