// Config types for agent configuration
export interface AgentConfig {
  max_turns: number;
  temperature: number;
  timeout_seconds: number;
  system_prompt: string | null;
  enable_debug: boolean;
}

export interface ConfigResponse {
  success: boolean;
  config: AgentConfig;
  message: string | null;
}

export interface PresetConfig {
  name: string;
  description: string;
  config: AgentConfig;
}

export interface DebugMetadata {
  tokens_used: number | null;
  tokens_input: number | null;
  tokens_output: number | null;
  latency_ms: number;
  provider: string;
  model: string;
  max_turns: number;
  current_turn: number;
  temperature: number;
  agent_state: string | null;
  reasoning: string | null;
  tool_calls: string[] | null;
  errors: string[] | null;
  backend: string;
}
