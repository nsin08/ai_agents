import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';
import { ConfigService, AgentConfig } from './ConfigService';
import { MetricsService } from './MetricsService';
import { TraceService } from './TraceService';
import { AgentState } from '../models/Trace';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  tokens?: {
    prompt: number;
    completion: number;
  };
  responseTime?: number;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  config: AgentConfig;
  createdAt: number;
}

export class AgentService {
  private configService: ConfigService;
  private metricsService: MetricsService | undefined;
  private traceService: TraceService | undefined;
  private currentSession: ChatSession | undefined;
  private httpClient: AxiosInstance;
  private sessionId: string;
  private currentTurn: number = 0;

  constructor(configService: ConfigService, metricsService?: MetricsService, traceService?: TraceService) {
    this.configService = configService;
    this.metricsService = metricsService;
    this.traceService = traceService;
    this.sessionId = this.generateSessionId();
    this.httpClient = axios.create();
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Start a new conversation session
   */
  public async startSession(): Promise<ChatSession> {
    const config = this.configService.getConfig();

    this.currentSession = {
      id: this.sessionId,
      messages: [],
      config,
      createdAt: Date.now(),
    };

    // Load from storage if exists
    const stored = await this.configService.loadSession(this.sessionId);

    // Initialize metrics and trace collection
    if (this.metricsService) {
      this.metricsService.startConversation(this.sessionId, config.provider, config.model);
    }
    if (this.traceService) {
      this.traceService.startTrace(this.sessionId, config.provider, config.model);
    }
    this.currentTurn = 0;

    if (stored) {
      this.currentSession = stored as ChatSession;
      console.log('Session restored from storage:', this.sessionId);
    }

    return this.currentSession;
  }

  /**
   * Send a message to the AI agent
   */
  public async sendMessage(userMessage: string): Promise<string> {
    if (!this.currentSession) {
      await this.startSession();
    }

    const config = this.configService.getConfig();
    this.currentTurn++;
    const turnStartTime = Date.now();

    // Trace: Observe state
    this.recordTrace('Observe', userMessage, undefined, turnStartTime);

    // Add user message to history
    const userMsg: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: turnStartTime,
    };
    this.currentSession!.messages.push(userMsg);

    try {
      // Trace: Plan state (simulated - would come from actual orchestrator)
      const planStartTime = Date.now();
      this.recordTrace('Plan', userMessage, 'Planning response strategy', planStartTime);

      // Trace: Act state (call backend)
      const actStartTime = Date.now();
      const response = await this.callBackendAPI(userMessage, config);
      const responseTime = Date.now() - actStartTime;

      // Estimate token counts (in real implementation, get from API response)
      const promptTokens = this.estimateTokens(userMessage);
      const completionTokens = this.estimateTokens(response);

      // Trace: Verify state (simulated - would come from actual orchestrator)
      const verifyStartTime = Date.now();
      this.recordTrace('Verify', response, 'Response validated', verifyStartTime);

      // Record metrics for this message
      if (this.metricsService) {
        this.metricsService.recordMessage(
          this.sessionId,
          promptTokens,
          completionTokens,
          responseTime
        );
      }

      // Add assistant response to history with metadata
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response,
        timestamp: Date.now(),
        tokens: {
          prompt: promptTokens,
          completion: completionTokens
        },
        responseTime
      };
      this.currentSession!.messages.push(assistantMsg);

      // Save session
      await this.configService.saveSession(this.sessionId, this.currentSession!);

      return response;
    } catch (error) {
      // Record error in trace
      if (this.traceService) {
        this.traceService.recordStateTransition(
          this.sessionId,
          'Act',
          this.currentTurn,
          Date.now() - turnStartTime,
          userMessage,
          undefined,
          undefined,
          {
            message: error instanceof Error ? error.message : 'Unknown error',
            type: 'AgentError',
            context: { provider: config.provider, model: config.model }
          }
        );
      }

      // Remove failed user message
      this.currentSession!.messages.pop();
      throw error;
    }
  }

  /**
   * Call the backend API (web/backend from PR #73)
   */
  private async callBackendAPI(message: string, config: AgentConfig): Promise<string> {
    const config_timeout = config.timeout * 1000; // Convert to milliseconds

    // If mock provider, return mock response
    if (config.provider === 'mock') {
      return this.getMockResponse(message);
    }

    // Try to call web backend API
    try {
      const response = await this.httpClient.post(
        'http://localhost:8000/api/chat/send',
        {
          message,
          session_id: this.sessionId,
        },
        {
          timeout: config_timeout,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.response || 'No response from agent';
    } catch (error) {
      console.error('Backend API error:', error);
      throw new Error(`Failed to communicate with agent: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Record trace entry for orchestrator state transition.
   */
  private recordTrace(
    state: AgentState,
    input?: string,
    output?: string,
    startTime?: number
  ): void {
    if (!this.traceService) {
      return;
    }

    const duration = startTime ? Date.now() - startTime : 0;

    this.traceService.recordStateTransition(
      this.sessionId,
      state,
      this.currentTurn,
      duration,
      input,
      output
    );
  }

  /**
   * Estimate token count for a text string.
   * Real implementation would use tokenizer or get from API response.
   * Rough estimate: ~4 characters per token for English text.
   */
  private estimateTokens(text: string): number {
    return Math.ceil(text.length / 4);
  }

  /**
   * Get mock response for testing (when provider is 'mock')
   */
  private getMockResponse(message: string): string {
    return `Mock Agent Response: You said "${message}". This is a test response from the mock provider.`;
  }

  /**
   * Get current session
   */
  public getCurrentSession(): ChatSession | undefined {
    return this.currentSession;
  }

  /**
   * Get conversation history
   */
  public getMessages(): ChatMessage[] {
    return this.currentSession?.messages || [];
  }

  /**
   * Reset the current session
   */
  public async resetSession(): Promise<void> {
    // End current session metrics/traces
    if (this.metricsService && this.currentSession) {
      this.metricsService.endConversation(this.sessionId);
    }
    if (this.traceService && this.currentSession) {
      this.traceService.endTrace(this.sessionId);
    }

    this.sessionId = this.generateSessionId();
    this.currentSession = undefined;
    this.currentTurn = 0;
    console.log('Session reset');
  }

  /**
   * Update configuration (called when settings change)
   */
  public updateConfiguration(): void {
    const config = this.configService.getConfig();
    if (this.currentSession) {
      this.currentSession.config = config;
    }
    console.log('Agent configuration updated:', config);
  }
}
