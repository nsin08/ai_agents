import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';
import { ConfigService, AgentConfig } from './ConfigService';
import { AgentConfigurationService } from './AgentConfigurationService';
import { MetricsService } from './MetricsService';
import { TraceService } from './TraceService';
import { MultiAgentCoordinator } from './MultiAgentCoordinator';
import { AgentState } from '../models/Trace';
import { AgentRole, SpecialistAgent, AgentCapability } from '../models/AgentRole';
import { CombinedResult } from '../models/AgentMessage';
import type { AgentConfiguration, MultiAgentConfig } from '../models/AgentRole';
import { HistoryService } from './HistoryService';

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
  private agentConfigService: AgentConfigurationService | undefined;
  private metricsService: MetricsService | undefined;
  private traceService: TraceService | undefined;
  private coordinator: MultiAgentCoordinator | undefined;
  private historyService: HistoryService | undefined;
  private currentSession: ChatSession | undefined;
  private httpClient: AxiosInstance;
  private sessionId: string;
  private currentTurn: number = 0;
  private activeProvider: string = '';
  private activeModel: string = '';
  private specialistAgents: Map<AgentRole, SpecialistAgent> = new Map();

  constructor(
    configService: ConfigService,
    metricsService?: MetricsService,
    traceService?: TraceService,
    agentConfigService?: AgentConfigurationService,
    historyService?: HistoryService
  ) {
    this.configService = configService;
    this.agentConfigService = agentConfigService;
    this.metricsService = metricsService;
    this.traceService = traceService;
    this.historyService = historyService;
    this.sessionId = this.generateSessionId();
    this.httpClient = axios.create();
    
    // Initialize coordinator if we have all required services
    if (metricsService && traceService && agentConfigService) {
      this.coordinator = new MultiAgentCoordinator(
        this,
        metricsService,
        traceService,
        agentConfigService
      );
    }
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

    // Track active config for change detection
    this.activeProvider = config.provider;
    this.activeModel = config.model;

    this.currentSession = {
      id: this.sessionId,
      messages: [],
      config,
      createdAt: Date.now(),
    };

    // Load from storage if exists (only restore messages, not config)
    const stored = await this.configService.loadSession(this.sessionId);

    // Initialize metrics and trace collection
    if (this.metricsService) {
      // Determine mode from AgentConfigurationService if available, otherwise default to 'single'
      const mode = this.agentConfigService?.getConfig().mode || 'single';
      
      if (mode === 'multi') {
        const multiConfig = this.agentConfigService?.getConfig() as any;
        // For multi-agent, use format "Plan: provider | Act: provider"
        const provider = `Plan: ${multiConfig.plan?.provider || 'unknown'} | Act: ${multiConfig.act?.provider || 'unknown'}`;
        const model = `Plan: ${multiConfig.plan?.model || 'unknown'} | Act: ${multiConfig.act?.model || 'unknown'}`;
        this.metricsService.startConversation(this.sessionId, provider, model);
      } else {
        this.metricsService.startConversation(this.sessionId, config.provider, config.model);
      }
    }
    if (this.traceService) {
      // Determine mode from AgentConfigurationService if available, otherwise default to 'single'
      const mode = this.agentConfigService?.getConfig().mode || 'single';
      
      if (mode === 'multi') {
        const multiConfig = this.agentConfigService?.getConfig() as MultiAgentConfig;
        this.traceService.startTrace(
          this.sessionId,
          multiConfig.plan.provider,
          multiConfig.plan.model,
          'multi',
          multiConfig.plan.provider,
          multiConfig.plan.model,
          multiConfig.act.provider,
          multiConfig.act.model
        );
      } else {
        this.traceService.startTrace(this.sessionId, config.provider, config.model, 'single');
      }
    }
    this.currentTurn = 0;

    if (stored) {
      // Only restore messages, keep new config
      this.currentSession.messages = (stored as ChatSession).messages;
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
    
    // Check if provider/model changed - if so, end current and start new conversation
    if (this.currentSession && 
        (this.activeProvider !== config.provider || 
         this.activeModel !== config.model)) {
      
      // End current conversation
      if (this.metricsService) {
        await this.metricsService.endConversation(this.sessionId);
      }
      if (this.traceService) {
        this.traceService.endTrace(this.sessionId);
      }
      
      // Start new conversation with new config
      this.sessionId = this.generateSessionId();
      this.currentTurn = 0;
      await this.startSession();
    }
    
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
      let response: string;

      // Check if multi-agent mode is enabled
      const isMultiAgent = this.agentConfigService?.getConfig().mode === 'multi';
      
      if (isMultiAgent && this.coordinator) {
        // Use multi-agent coordinator
        const coordinatorResult = await this.coordinator.orchestrate(userMessage);
        response = coordinatorResult.finalOutput || 'No response from coordinator';
      } else {
        // Use direct API call for single-agent mode
        // Trace: Plan state (simulated - would come from actual orchestrator)
        const planStartTime = Date.now();
        this.recordTrace('Plan', userMessage, 'Planning response strategy', planStartTime);

        // Trace: Act state (call backend)
        const actStartTime = Date.now();
        response = await this.callBackendAPI(userMessage, config);
        const responseTime = Date.now() - actStartTime;

        // Trace: Verify state (simulated - would come from actual orchestrator)
        const verifyStartTime = Date.now();
        this.recordTrace('Verify', response, 'Response validated', verifyStartTime);
      }

      // Estimate token counts (in real implementation, get from API response)
      const promptTokens = this.estimateTokens(userMessage);
      const completionTokens = this.estimateTokens(response);
      const responseTime = Date.now() - turnStartTime;

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
      await this.persistHistory();

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

    // Handle Ollama provider directly
    if (config.provider === 'ollama') {
      return this.callOllamaAPI(message, config);
    }

    // Try to call web backend API for other providers
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
   * Call Ollama API directly
   */
  private async callOllamaAPI(message: string, config: AgentConfig): Promise<string> {
    const config_timeout = config.timeout * 1000;

    try {
      const response = await this.httpClient.post(
        `${config.baseUrl}/api/generate`,
        {
          model: config.model,
          prompt: message,
          stream: false,
        },
        {
          timeout: config_timeout,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.response || 'No response from Ollama';
    } catch (error) {
      console.error('Ollama API error:', error);
      throw new Error(`Failed to communicate with Ollama: ${error instanceof Error ? error.message : 'Unknown error'}`);
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

  private async persistHistory(): Promise<void> {
    if (!this.historyService || !this.currentSession) {
      return;
    }

    const mode = this.agentConfigService?.getConfig().mode || 'single';
    if (mode === 'multi') {
      const multiConfig = this.agentConfigService?.getConfig() as MultiAgentConfig;
      await this.historyService.saveConversation(this.currentSession, {
        agentMode: 'multi',
        planProvider: multiConfig?.plan?.provider,
        planModel: multiConfig?.plan?.model,
        actProvider: multiConfig?.act?.provider,
        actModel: multiConfig?.act?.model
      });
      return;
    }

    const config = this.configService.getConfig();
    await this.historyService.saveConversation(this.currentSession, {
      agentMode: 'single',
      provider: config.provider,
      model: config.model
    });
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

  /**
   * Register a specialist agent for multi-agent coordination.
   */
  public registerSpecialistAgent(role: AgentRole, agent: SpecialistAgent): void {
    this.specialistAgents.set(role, agent);
  }

  /**
   * Get all registered specialist agents.
   */
  public getRegisteredAgents(): SpecialistAgent[] {
    return Array.from(this.specialistAgents.values());
  }

  /**
   * Get a registered agent by role.
   */
  public getAgent(role: AgentRole): SpecialistAgent | undefined {
    return this.specialistAgents.get(role);
  }

  /**
   * Get agent capabilities for a role or all capabilities if no role is provided.
   */
  public getAgentCapabilities(role?: AgentRole): AgentCapability[] {
    if (role) {
      return this.specialistAgents.get(role)?.capabilities ?? [];
    }

    const capabilities: AgentCapability[] = [];
    for (const agent of this.specialistAgents.values()) {
      capabilities.push(...agent.capabilities);
    }
    return capabilities;
  }

  /**
   * Orchestrate a task via multi-agent coordination (stub until coordinator is implemented).
   */
  public async orchestrateMultiAgent(_task: string): Promise<CombinedResult> {
    throw new Error('Multi-agent coordinator not implemented yet.');
  }
}
