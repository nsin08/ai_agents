import axios, { AxiosInstance } from 'axios';
import { AgentService } from './AgentService';
import { MetricsService } from './MetricsService';
import { TraceService } from './TraceService';
import { ConfigService } from './ConfigService';
import { AgentConfigurationService, ConfigurationWithDebug } from './AgentConfigurationService';
import {
  AgentRole,
  AgentStage,
  SpecialistAgent,
  AgentStatus,
  AgentConfiguration,
  SingleAgentConfig,
  MultiAgentConfig,
  StageConfig
} from '../models/AgentRole';
import {
  CombinedResult,
  CoordinatorState,
  DecomposedTask,
  AgentMessage,
  ReasoningChain,
  Subtask
} from '../models/AgentMessage';
import { TaskResult } from '../models/AgentRole';

export interface CoordinatorConfig {
  maxTurnsPerAgent: number;
  agentTimeoutSeconds: number;
  decompositionTimeoutSeconds: number;
  enableVerifier: boolean;
  fallbackOnTimeout: boolean;
  verbose: boolean;
}

export interface StateTransition {
  from: CoordinatorState;
  to: CoordinatorState;
  timestamp: number;
}

export interface CoordinatorCallbacks {
  onStateChange?: (state: CoordinatorState) => void;
  onAgentsUpdate?: (agents: SpecialistAgent[]) => void;
  onQueueUpdate?: (queue: Subtask[]) => void;
  onProgressUpdate?: (progress: number) => void;
  onLogUpdate?: (messages: AgentMessage[]) => void;
}

const defaultConfig: CoordinatorConfig = {
  maxTurnsPerAgent: 5,
  agentTimeoutSeconds: 30,
  decompositionTimeoutSeconds: 10,
  enableVerifier: false,
  fallbackOnTimeout: true,
  verbose: false
};

export class MultiAgentCoordinator {
  private agentService: AgentService;
  private metricsService: MetricsService | undefined;
  private traceService: TraceService | undefined;
  private configService: ConfigService | AgentConfigurationService;
  private config: CoordinatorConfig;
  private agents: Map<AgentRole, SpecialistAgent> = new Map();
  private state: CoordinatorState = CoordinatorState.IDLE;
  private stateHistory: StateTransition[] = [];
  private currentConversationId: string | undefined;
  private callbacks: CoordinatorCallbacks | undefined;
  private messageLog: AgentMessage[] = [];
  private reasoningByAgent: Map<string, ReasoningChain> = new Map();
  private cancelRequested: boolean = false;
  private multiAgentEnabled: boolean = true;
  private agentConfig: (AgentConfiguration & ConfigurationWithDebug) | undefined;
  private httpClient: AxiosInstance;
  private debugMode: boolean = false;

  constructor(
    agentService: AgentService,
    metricsService: MetricsService | undefined,
    traceService: TraceService | undefined,
    configService: ConfigService | AgentConfigurationService,
    config?: Partial<CoordinatorConfig>
  ) {
    this.agentService = agentService;
    this.metricsService = metricsService;
    this.traceService = traceService;
    this.configService = configService;
    this.config = { ...defaultConfig, ...(config ?? {}) };
    this.httpClient = axios.create();

    // Load agent configuration if using new service
    if (configService instanceof AgentConfigurationService) {
      this.agentConfig = configService.getConfig();
      // Listen for config changes
      configService.onConfigurationChange((newConfig) => {
        this.agentConfig = newConfig;
        // Update debug mode when config changes
        this.debugMode = process.env.DEBUG_MULTI_AGENT === 'true' || 
                         (this.agentConfig?.debugMode ?? false) || 
                         this.config.verbose;
      });
    }

    // Initialize debug mode (checks env var, VS Code setting, or config flag)
    this.debugMode = process.env.DEBUG_MULTI_AGENT === 'true' || 
                     (this.agentConfig?.debugMode ?? false) || 
                     this.config.verbose;
  }

  /**
   * Log debug message if debug mode is enabled
   */
  private debug(message: string): void {
    if (this.debugMode) {
      console.log(message);
    }
  }

  public registerAgent(role: AgentRole, agent: SpecialistAgent): void {
    this.agents.set(role, agent);
  }

  public getRegisteredAgents(): SpecialistAgent[] {
    return Array.from(this.agents.values());
  }

  public getAgent(role: AgentRole): SpecialistAgent | undefined {
    return this.agents.get(role);
  }

  public getState(): CoordinatorState {
    return this.state;
  }

  public getStateHistory(): StateTransition[] {
    return [...this.stateHistory];
  }

  public setCallbacks(callbacks: CoordinatorCallbacks | undefined): void {
    this.callbacks = callbacks;
  }

  public setMultiAgentEnabled(enabled: boolean): void {
    this.multiAgentEnabled = enabled;
  }

  public isMultiAgentEnabled(): boolean {
    return this.multiAgentEnabled;
  }

  public getCurrentConversationId(): string | undefined {
    return this.currentConversationId;
  }

  public getMessageLog(): AgentMessage[] {
    return [...this.messageLog];
  }

  public async orchestrate(_userTask: string): Promise<CombinedResult> {
    const startTime = Date.now();

    this.currentConversationId = `multi-agent-${startTime}`;
    this.cancelRequested = false;

    try {
      // Determine execution mode
      const executionMode = this.getExecutionMode();

      if (executionMode === 'single-agent') {
        return await this.orchestrateSingleAgent(_userTask, startTime);
      } else if (executionMode === 'multi-agent') {
        return await this.orchestrateMultiAgent(_userTask, startTime);
      } else {
        // Fallback for legacy mode
        return await this.orchestrateMultiAgent(_userTask, startTime);
      }
    } catch (error) {
      this.setState(CoordinatorState.ERROR);
      this.recordCoordinatorState(CoordinatorState.ERROR, {
        message: error instanceof Error ? error.message : 'Unknown error'
      });

      if (this.config.fallbackOnTimeout) {
        const fallback = await this.fallbackToSingleAgent(_userTask);
        const totalDuration = Date.now() - startTime;
        this.metricsService?.recordCoordinatorOverhead(totalDuration);
        if (this.currentConversationId) {
          await this.metricsService?.endConversation(this.currentConversationId);
          this.traceService?.endTrace(this.currentConversationId);
        }
        return this.buildFallbackResult(_userTask, fallback, totalDuration);
      }

      throw error;
    }
  }

  /**
   * Determine execution mode: 'single-agent', 'multi-agent', or 'legacy'
   */
  private getExecutionMode(): 'single-agent' | 'multi-agent' | 'legacy' {
    if (!this.agentConfig) {
      return 'legacy';
    }

    return this.agentConfig.mode === 'single' ? 'single-agent' : 'multi-agent';
  }

  /**
   * Execute task in single-agent mode
   */
  private async orchestrateSingleAgent(_userTask: string, startTime: number): Promise<CombinedResult> {
    const config = this.agentConfig as SingleAgentConfig;
    
    this.metricsService?.startConversation(
      this.currentConversationId!,
      config.provider,
      config.model
    );
    this.traceService?.startTrace(
      this.currentConversationId!,
      config.provider,
      config.model,
      'single'
    );

    this.setState(CoordinatorState.DELEGATING);
    this.recordCoordinatorState(CoordinatorState.DELEGATING, { mode: 'single-agent' });

    try {
      // Route task based on keywords to determine stage (Plan or Act)
      const stage = this.routeToStage(_userTask);
      
      this.setState(CoordinatorState.PROCESSING);
      const result = await this.agentService.sendMessage(_userTask);

      const totalDuration = Date.now() - startTime;
      const estimatedTokens = Math.ceil(result.length / 4);

      this.setState(CoordinatorState.COMPLETE);
      this.recordCoordinatorState(CoordinatorState.COMPLETE);
      this.metricsService?.recordCoordinatorOverhead(totalDuration);

      if (this.currentConversationId) {
        await this.metricsService?.endConversation(this.currentConversationId);
        this.traceService?.endTrace(this.currentConversationId);
      }

      return {
        originalTask: _userTask,
        decomposition: {
          id: `decomposition-${Date.now()}`,
          originalTask: _userTask,
          subtasks: [],
          reasoning: {
            steps: [
              {
                action: 'Single-agent execution',
                rationale: `Task routed to ${stage} stage based on content analysis.`,
                chosen: true
              }
            ],
            summary: `Single-agent mode: ${stage} stage.`,
            confidence: 0.8
          },
          estimatedDuration: totalDuration,
          estimatedTokens
        },
        subtaskResults: [],
        finalOutput: result,
        totalDuration,
        totalTokens: estimatedTokens,
        coordinatorOverhead: totalDuration
      };
    } catch (error) {
      this.setState(CoordinatorState.ERROR);
      throw error;
    }
  }

  /**
   * Execute task in multi-agent mode (sequential: Plan → Act)
   */
  private async orchestrateMultiAgent(_userTask: string, startTime: number): Promise<CombinedResult> {
    const config = this.agentConfig as MultiAgentConfig;

    this.debug('[MultiAgentCoordinator] 🤝 MULTI-AGENT ORCHESTRATION STARTED');
    this.debug(`[MultiAgentCoordinator]   Plan Stage: ${config.plan.provider}/${config.plan.model}`);
    this.debug(`[MultiAgentCoordinator]   Act Stage: ${config.act.provider}/${config.act.model}`);
    this.debug(`[MultiAgentCoordinator]   User Task: "${_userTask.substring(0, 100)}..."`);

    this.metricsService?.startConversation(
      this.currentConversationId!,
      config.plan.provider,
      config.plan.model
    );
    this.traceService?.startTrace(
      this.currentConversationId!,
      config.plan.provider,
      config.plan.model,
      'multi',
      config.plan.provider,
      config.plan.model,
      config.act.provider,
      config.act.model
    );

    const stageResults: { stage: 'plan' | 'act'; output: string; tokens: number; duration: number }[] = [];

    try {
      // Stage 1: Plan (Analysis)
      this.setState(CoordinatorState.DECOMPOSING);
      this.recordCoordinatorState(CoordinatorState.DECOMPOSING);

      const planStartTime = Date.now();
      const planResult = await this.executePlanStage(_userTask, config.plan);
      const planDuration = Date.now() - planStartTime;
      const planTokens = Math.ceil(planResult.length / 4);

      this.debug(`[MultiAgentCoordinator] ✓ Plan stage completed in ${planDuration}ms`);

      stageResults.push({
        stage: 'plan',
        output: planResult,
        tokens: planTokens,
        duration: planDuration
      });

      this.callbacks?.onProgressUpdate?.(50);

      // Stage 2: Act (Execution)
      if (this.cancelRequested) {
        throw new Error('Multi-agent coordination cancelled by user.');
      }

      this.setState(CoordinatorState.DELEGATING);
      this.recordCoordinatorState(CoordinatorState.DELEGATING, { stage: 'act' });

      const actStartTime = Date.now();
      const actResult = await this.executeActStage(_userTask, planResult, config.act);
      const actDuration = Date.now() - actStartTime;
      const actTokens = Math.ceil(actResult.length / 4);

      this.debug(`[MultiAgentCoordinator] ✓ Act stage completed in ${actDuration}ms`);
      this.debug(`[MultiAgentCoordinator] 🤝 MULTI-AGENT ORCHESTRATION COMPLETE`);

      stageResults.push({
        stage: 'act',
        output: actResult,
        tokens: actTokens,
        duration: actDuration
      });

      this.callbacks?.onProgressUpdate?.(100);

      const totalDuration = Date.now() - startTime;
      const totalTokens = planTokens + actTokens;

      this.setState(CoordinatorState.COMPLETE);
      this.recordCoordinatorState(CoordinatorState.COMPLETE);
      this.metricsService?.recordCoordinatorOverhead(totalDuration);

      if (this.currentConversationId) {
        await this.metricsService?.endConversation(this.currentConversationId);
        this.traceService?.endTrace(this.currentConversationId);
      }

      return {
        originalTask: _userTask,
        decomposition: {
          id: `decomposition-${Date.now()}`,
          originalTask: _userTask,
          subtasks: stageResults.map((r, idx) => ({
            id: `stage-${r.stage}-${idx}`,
            description: r.stage === 'plan' ? 'Plan: Analyze and decompose task' : 'Act: Execute implementation',
            priority: idx + 1,
            dependencies: idx === 0 ? [] : [`stage-plan-0`],
            assignedAgent: r.stage === 'plan' ? AgentRole.PLANNER : AgentRole.EXECUTOR,
            status: 'completed' as const,
            result: {
              id: `result-${r.stage}`,
              subtaskId: `stage-${r.stage}`,
              content: r.output,
              success: true,
              duration: r.duration,
              tokensUsed: { input: r.tokens, output: r.tokens },
              confidence: 0.8
            }
          })),
          reasoning: {
            steps: [
              {
                action: 'Plan Stage',
                rationale: 'Analyzed task and created execution plan.',
                chosen: true
              },
              {
                action: 'Act Stage',
                rationale: 'Implemented task based on plan.',
                chosen: true
              }
            ],
            summary: `Sequential execution: Plan (${planTokens} tokens) → Act (${actTokens} tokens)`,
            confidence: 0.85
          },
          estimatedDuration: totalDuration,
          estimatedTokens: totalTokens
        },
        subtaskResults: [],
        finalOutput: actResult,
        totalDuration,
        totalTokens,
        coordinatorOverhead: totalDuration
      };
    } catch (error) {
      this.setState(CoordinatorState.ERROR);
      this.recordCoordinatorState(CoordinatorState.ERROR, {
        message: error instanceof Error ? error.message : 'Stage execution failed'
      });

      if (this.config.fallbackOnTimeout) {
        const fallback = await this.fallbackToSingleAgent(_userTask);
        const totalDuration = Date.now() - startTime;
        this.metricsService?.recordCoordinatorOverhead(totalDuration);
        if (this.currentConversationId) {
          await this.metricsService?.endConversation(this.currentConversationId);
          this.traceService?.endTrace(this.currentConversationId);
        }
        return this.buildFallbackResult(_userTask, fallback, totalDuration);
      }

      throw error;
    }
  }

  /**
   * Execute Plan stage (analysis and task decomposition)
   */
  private async executePlanStage(task: string, config: StageConfig): Promise<string> {
    this.debug('[MultiAgentCoordinator] 🧠 PLAN STAGE EXECUTING');
    this.debug(`[MultiAgentCoordinator]   Model: ${config.model}`);
    this.debug(`[MultiAgentCoordinator]   Provider: ${config.provider}`);
    this.debug(`[MultiAgentCoordinator]   Task: "${task.substring(0, 100)}..."`);
    
    const planPrompt = `Analyze and break down the following task into clear, actionable steps:

Task: ${task}

Provide:
1. Task analysis and key requirements
2. Decomposition into subtasks
3. Suggested execution order
4. Any dependencies or considerations`;

    // Call Ollama API directly to avoid circular dependency
    const result = await this.callOllamaAPI(planPrompt, config);

    this.debug(`[MultiAgentCoordinator] ✓ PLAN STAGE COMPLETE (${result.length} chars)`);
    this.debug(`[MultiAgentCoordinator]   Output preview: "${result.substring(0, 150)}..."`);

    return result;
  }

  /**
   * Execute Act stage (implementation based on plan output)
   */
  private async executeActStage(
    originalTask: string,
    planOutput: string,
    config: StageConfig
  ): Promise<string> {
    this.debug('[MultiAgentCoordinator] ⚡ ACT STAGE EXECUTING');
    this.debug(`[MultiAgentCoordinator]   Model: ${config.model}`);
    this.debug(`[MultiAgentCoordinator]   Provider: ${config.provider}`);
    this.debug(`[MultiAgentCoordinator]   Original Task: "${originalTask.substring(0, 100)}..."`);
    this.debug(`[MultiAgentCoordinator]   Using Plan output: "${planOutput.substring(0, 150)}..."`);
    
    const actPrompt = `Based on the following plan, execute the task and provide a detailed implementation:

Original Task: ${originalTask}

Plan/Analysis from previous stage:
${planOutput}

Now provide the actual implementation, solution, or execution based on this plan. Be specific and detailed.`;

    // Call Ollama API directly to avoid circular dependency
    const result = await this.callOllamaAPI(actPrompt, config);

    this.debug(`[MultiAgentCoordinator] ✓ ACT STAGE COMPLETE (${result.length} chars)`);
    this.debug(`[MultiAgentCoordinator]   Output preview: "${result.substring(0, 150)}..."`);

    return result;
  }

  /**
   * Route task to Plan or Act stage based on keywords (for single-agent mode)
   */
  private routeToStage(description: string): 'plan' | 'act' {
    const lowerDesc = description.toLowerCase();

    // Plan keywords: analysis, review, planning, design
    if (lowerDesc.match(/\b(analyz|review|check|identify|examine|inspect|assess|evaluate|plan|design|architect|outline|strategy|investigate)\b/i)) {
      return 'plan';
    }

    // Default to Act (implementation)
    return 'act';
  }

  private setState(newState: CoordinatorState): void {
    if (this.state === newState) {
      return;
    }

    this.stateHistory.push({
      from: this.state,
      to: newState,
      timestamp: Date.now()
    });
    this.state = newState;
    this.callbacks?.onStateChange?.(newState);
  }

  public async fallbackToSingleAgent(_task: string): Promise<string> {
    return this.agentService.sendMessage(_task);
  }

  public cancel(): void {
    this.cancelRequested = true;
  }

  private recordCoordinatorState(state: CoordinatorState, metadata?: Record<string, any>): void {
    if (!this.currentConversationId || !this.traceService) {
      return;
    }
    this.traceService.recordCoordinatorState(this.currentConversationId, state, metadata);
  }

  private recordInterAgentMessage(message: AgentMessage): void {
    if (!this.currentConversationId || !this.traceService) {
      return;
    }
    this.messageLog.push(message);
    this.callbacks?.onLogUpdate?.([...this.messageLog]);
    this.traceService.recordInterAgentMessage(this.currentConversationId, message);
  }

  private recordAgentReasoning(agentId: string, reasoning: ReasoningChain): void {
    if (!this.currentConversationId || !this.traceService) {
      return;
    }
    this.reasoningByAgent.set(agentId, reasoning);
    this.traceService.recordAgentReasoning(this.currentConversationId, agentId, reasoning);
  }

  private recordAgentResponse(role: AgentRole, subtask: Subtask, result: TaskResult): void {
    const message: AgentMessage = {
      id: `msg-${Date.now()}`,
      type: 'task-response',
      from: role,
      to: 'coordinator',
      content: result.content,
      timestamp: Date.now(),
      metadata: {
        taskId: subtask.id,
        confidence: result.confidence
      }
    };
    this.recordInterAgentMessage(message);
  }

  private buildExecutionReasoning(
    role: AgentRole,
    subtask: Subtask,
    result: TaskResult
  ): ReasoningChain {
    return {
      steps: [
        {
          action: `Execute subtask (${role})`,
          rationale: `Handled "${subtask.description}" with ${result.success ? 'success' : 'errors'}.`,
          chosen: true
        }
      ],
      summary: result.success ? 'Execution completed.' : 'Execution failed.',
      confidence: result.success ? 0.7 : 0.3
    };
  }

  private getAgentId(role: AgentRole): string {
    return `${role}-1`;
  }

  private buildExecutionPlan(subtasks: Subtask[]): Subtask[] {
    if (subtasks.length === 0) {
      return [];
    }

    const idToTask = new Map(subtasks.map(task => [task.id, task]));
    const remainingDeps = new Map<string, Set<string>>();
    subtasks.forEach(task => {
      remainingDeps.set(task.id, new Set(task.dependencies));
    });

    const queue = subtasks.filter(task => (remainingDeps.get(task.id)?.size ?? 0) === 0);
    const ordered: Subtask[] = [];

    while (queue.length > 0) {
      const current = queue.shift()!;
      ordered.push(current);

      for (const task of subtasks) {
        const deps = remainingDeps.get(task.id);
        if (!deps || deps.size === 0) {
          continue;
        }
        if (deps.has(current.id)) {
          deps.delete(current.id);
          if (deps.size === 0) {
            queue.push(task);
          }
        }
      }
    }

    if (ordered.length !== subtasks.length) {
      // Fallback: return original order if cyclic dependencies detected.
      return subtasks;
    }

    return ordered;
  }

  private async withTimeout<T>(promise: Promise<T>, timeoutSeconds: number): Promise<T> {
    if (!timeoutSeconds || timeoutSeconds <= 0) {
      return promise;
    }

    let timeoutHandle: NodeJS.Timeout | undefined;
    const timeoutPromise = new Promise<T>((_, reject) => {
      timeoutHandle = setTimeout(() => {
        reject(new Error('Agent execution timed out.'));
      }, timeoutSeconds * 1000);
    });

    try {
      return await Promise.race([promise, timeoutPromise]);
    } finally {
      if (timeoutHandle) {
        clearTimeout(timeoutHandle);
      }
    }
  }

  private buildFallbackResult(
    task: string,
    output: string,
    duration: number,
    decomposition?: DecomposedTask
  ): CombinedResult {
    return {
      originalTask: task,
      decomposition: decomposition ?? {
        id: `decomposition-${Date.now()}`,
        originalTask: task,
        subtasks: [],
        reasoning: {
          steps: [
            {
              action: 'Fallback',
              rationale: 'Multi-agent flow disabled or failed.',
              chosen: true
            }
          ],
          summary: 'Fallback to single-agent execution.',
          confidence: 0.5
        },
        estimatedDuration: duration,
        estimatedTokens: 0
      },
      subtaskResults: [],
      finalOutput: output,
      totalDuration: duration,
      totalTokens: 0,
      coordinatorOverhead: duration
    };
  }

  /**
   * Call Ollama API directly for Plan/Act stages
   */
  private async callOllamaAPI(prompt: string, config: StageConfig): Promise<string> {
    try {
      const response = await this.httpClient.post(
        'http://localhost:11434/api/generate',
        {
          model: config.model,
          prompt: prompt,
          stream: false,
        },
        {
          timeout: config.timeout * 1000
        }
      );

      return response.data.response || 'No response from Ollama';
    } catch (error) {
      console.error('[MultiAgentCoordinator] Ollama API error:', error);
      throw new Error(`Failed to call Ollama API: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}
