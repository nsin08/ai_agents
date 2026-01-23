/**
 * Statistics and metrics data models for Phase 2.
 * Tracks token usage, response times, costs, and conversation metrics.
 */

export interface ConversationMetrics {
  /** Unique identifier for the conversation/session */
  conversationId: string;
  
  /** LLM provider used (ollama, openai, anthropic, etc.) */
  provider: string;
  
  /** Model name (e.g., llama2, gpt-4, claude-3-opus) */
  model: string;
  
  /** Total tokens consumed (prompt + completion) */
  totalTokens: number;
  
  /** Tokens used in prompts/input */
  promptTokens: number;
  
  /** Tokens generated in completions/output */
  completionTokens: number;
  
  /** Total cost in USD (calculated from token counts and provider rates) */
  totalCost: number;
  
  /** Number of messages in conversation */
  messageCount: number;
  
  /** Average response time in milliseconds */
  averageResponseTime: number;
  
  /** Conversation start timestamp */
  startTime: Date;
  
  /** Conversation end timestamp (undefined if still active) */
  endTime?: Date;
}

export interface MessageMetrics {
  /** Message index in conversation */
  messageIndex: number;
  
  /** Timestamp when message was sent */
  timestamp: Date;
  
  /** Response time in milliseconds */
  responseTime: number;
  
  /** Tokens in this message */
  promptTokens: number;
  
  /** Tokens in response */
  completionTokens: number;
  
  /** Cost for this message */
  cost: number;
  
  /** Tools used in this turn (if any) */
  toolsUsed?: string[];
  
  /** Error if message failed */
  error?: string;
}

export interface ProviderRates {
  /** Provider name */
  provider: string;
  
  /** Model name (or 'default' for all models) */
  model: string;
  
  /** Cost per 1K prompt tokens in USD */
  promptTokenCostPer1K: number;
  
  /** Cost per 1K completion tokens in USD */
  completionTokenCostPer1K: number;
}

/**
 * Default pricing for common providers (as of 2026-01).
 * Update these rates periodically or load from external config.
 */
export const DEFAULT_PROVIDER_RATES: ProviderRates[] = [
  // OpenAI
  { provider: 'openai', model: 'gpt-4', promptTokenCostPer1K: 0.03, completionTokenCostPer1K: 0.06 },
  { provider: 'openai', model: 'gpt-4-turbo', promptTokenCostPer1K: 0.01, completionTokenCostPer1K: 0.03 },
  { provider: 'openai', model: 'gpt-3.5-turbo', promptTokenCostPer1K: 0.0005, completionTokenCostPer1K: 0.0015 },
  
  // Anthropic
  { provider: 'anthropic', model: 'claude-3-opus', promptTokenCostPer1K: 0.015, completionTokenCostPer1K: 0.075 },
  { provider: 'anthropic', model: 'claude-3-sonnet', promptTokenCostPer1K: 0.003, completionTokenCostPer1K: 0.015 },
  { provider: 'anthropic', model: 'claude-3-haiku', promptTokenCostPer1K: 0.00025, completionTokenCostPer1K: 0.00125 },
  
  // Google
  { provider: 'google', model: 'gemini-pro', promptTokenCostPer1K: 0.00025, completionTokenCostPer1K: 0.0005 },
  { provider: 'google', model: 'gemini-ultra', promptTokenCostPer1K: 0.01, completionTokenCostPer1K: 0.03 },
  
  // Ollama (local, free)
  { provider: 'ollama', model: 'default', promptTokenCostPer1K: 0, completionTokenCostPer1K: 0 },
  
  // Mock (testing, free)
  { provider: 'mock', model: 'default', promptTokenCostPer1K: 0, completionTokenCostPer1K: 0 },
  
  // Azure OpenAI (similar to OpenAI)
  { provider: 'azure-openai', model: 'gpt-4', promptTokenCostPer1K: 0.03, completionTokenCostPer1K: 0.06 },
  { provider: 'azure-openai', model: 'gpt-35-turbo', promptTokenCostPer1K: 0.0005, completionTokenCostPer1K: 0.0015 },
];

export interface ExportFormat {
  /** Format type */
  format: 'csv' | 'json';
  
  /** Exported data */
  data: string;
  
  /** Suggested filename */
  filename: string;
  
  /** MIME type for saving */
  mimeType: string;
}

export interface StatisticsSummary {
  /** Total conversations tracked */
  totalConversations: number;
  
  /** Total messages across all conversations */
  totalMessages: number;
  
  /** Total tokens consumed */
  totalTokens: number;
  
  /** Total cost (USD) */
  totalCost: number;
  
  /** Average response time (ms) */
  averageResponseTime: number;
  
  /** Most used provider */
  topProvider: string;
  
  /** Most used model */
  topModel: string;
  
  /** Date range */
  dateRange: {
    from: Date;
    to: Date;
  };
}
