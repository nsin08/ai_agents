import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';
import { ConfigService, AgentConfig } from './ConfigService';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  config: AgentConfig;
  createdAt: number;
}

export class AgentService {
  private configService: ConfigService;
  private currentSession: ChatSession | undefined;
  private httpClient: AxiosInstance;
  private sessionId: string;

  constructor(configService: ConfigService) {
    this.configService = configService;
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
    if (stored) {
      this.currentSession = stored as ChatSession;
      console.log('Session restored from storage:', this.sessionId);
    }

    return this.currentSession;
  }

  /**
   * Send a message to the agent
   */
  public async sendMessage(userMessage: string): Promise<string> {
    if (!this.currentSession) {
      throw new Error('No active session. Call startSession first.');
    }

    const config = this.configService.getConfig();

    // Add user message to history
    const userMsg: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: Date.now(),
    };
    this.currentSession.messages.push(userMsg);

    try {
      // Call backend API
      const response = await this.callBackendAPI(userMessage, config);

      // Add assistant response to history
      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response,
        timestamp: Date.now(),
      };
      this.currentSession.messages.push(assistantMsg);

      // Save session
      await this.configService.saveSession(this.sessionId, this.currentSession);

      return response;
    } catch (error) {
      // Remove failed user message
      this.currentSession.messages.pop();
      throw error;
    }
  }

  /**
   * Call the backend API (web/backend from PR #73)
   */
  private async callBackendAPI(message: string, config: AgentConfig): Promise<string> {
    const config_timeout = config.timeout * 1000; // Convert to milliseconds

    try {
      // For MVP, use mock provider or local backend
      if (config.provider === 'mock') {
        return this.getMockResponse(message);
      }

      // Try to call web backend API
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
    this.sessionId = this.generateSessionId();
    this.currentSession = undefined;
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
