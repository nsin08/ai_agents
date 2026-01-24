// TypeScript types for Provider functionality

export enum ProviderType {
  MOCK = "mock",
  OLLAMA = "ollama",
  OPENAI = "openai",
  ANTHROPIC = "anthropic",
  GOOGLE = "google",
  AZURE_OPENAI = "azure-openai",
}

export type ProviderStatus = "available" | "coming_soon" | "deprecated";

export interface ProviderInfo {
  id: string;
  name: string;
  requires_api_key: boolean;
  supported_models: string[];
  api_key_env_var: string | null;
  status: ProviderStatus;
}

export interface ValidateKeyRequest {
  provider: ProviderType;
  api_key: string;
  model?: string;
}

export interface ValidateKeyResponse {
  valid: boolean;
  message: string;
  models_available: string[] | null;
}

export interface ChatRequest {
  message: string;
  provider: string;
  model: string;
  api_key?: string;
  config?: Record<string, any>;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  metadata: Record<string, any>;
}

export interface ProviderConfig {
  provider: ProviderType;
  model: string;
  api_key?: string;
}
