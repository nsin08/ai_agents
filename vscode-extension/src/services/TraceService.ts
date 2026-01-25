/**
 * TraceService - Captures and manages agent orchestrator traces.
 * Records state transitions, tool executions, and debugging context.
 */

import * as vscode from 'vscode';
import {
  TraceEntry,
  AgentState,
  ToolExecution,
  TraceError,
  ConversationTrace,
  TraceFilter,
  TraceSummary
} from '../models/Trace';

export class TraceService {
  private static readonly STORAGE_KEY = 'agentTraces';
  private static readonly MAX_TRACES_PER_CONVERSATION = 1000; // Limit memory usage
  
  private context: vscode.ExtensionContext;
  private activeTraces: Map<string, ConversationTrace>;
  private traceCounter: number;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.activeTraces = new Map();
    this.traceCounter = 0;
  }

  /**
   * Start tracing a new conversation.
   */
  public startTrace(conversationId: string, provider: string, model: string): void {
    const trace: ConversationTrace = {
      conversationId,
      entries: [],
      startTime: new Date(),
      totalTurns: 0,
      provider,
      model
    };
    this.activeTraces.set(conversationId, trace);
  }

  /**
   * Record a state transition in the agent orchestrator.
   */
  public recordStateTransition(
    conversationId: string,
    state: AgentState,
    turn: number,
    duration: number,
    input?: string,
    output?: string,
    toolsUsed?: ToolExecution[],
    error?: TraceError,
    metadata?: Record<string, any>
  ): void {
    let trace = this.activeTraces.get(conversationId);
    if (!trace) {
      console.warn(`No active trace found for conversation: ${conversationId}, auto-restarting trace`);
      // Auto-restart trace if it was cleared
      this.startTrace(conversationId, 'unknown', 'unknown');
      trace = this.activeTraces.get(conversationId)!;
    }

    const entry: TraceEntry = {
      id: `${conversationId}-${this.traceCounter++}`,
      timestamp: new Date(),
      state,
      turn,
      conversationId,
      input,
      output,
      toolsUsed,
      duration,
      error,
      metadata
    };

    trace.entries.push(entry);
    trace.totalTurns = Math.max(trace.totalTurns, turn);

    // Limit memory usage
    if (trace.entries.length > TraceService.MAX_TRACES_PER_CONVERSATION) {
      trace.entries.shift(); // Remove oldest entry
    }

    this.saveTraces();
  }

  /**
   * Record a tool execution during Act state.
   */
  public recordToolExecution(
    conversationId: string,
    toolName: string,
    input: Record<string, any>,
    output: any,
    duration: number,
    status: 'success' | 'failure',
    error?: string
  ): void {
    const trace = this.activeTraces.get(conversationId);
    if (!trace || trace.entries.length === 0) {
      return;
    }

    // Find the most recent Act state entry
    const actEntry = [...trace.entries].reverse().find(e => e.state === 'Act');
    if (actEntry) {
      const toolExecution: ToolExecution = {
        name: toolName,
        input,
        output,
        duration,
        status,
        error
      };

      if (!actEntry.toolsUsed) {
        actEntry.toolsUsed = [];
      }
      actEntry.toolsUsed.push(toolExecution);
      this.saveTraces();
    }
  }

  /**
   * End tracing for a conversation.
   */
  public endTrace(conversationId: string): void {
    const trace = this.activeTraces.get(conversationId);
    if (trace) {
      trace.endTime = new Date();
      this.saveTraces();
      this.activeTraces.delete(conversationId);
    }
  }

  /**
   * Get trace for a specific conversation.
   */
  public getTrace(conversationId: string): ConversationTrace | undefined {
    // Check active first
    const active = this.activeTraces.get(conversationId);
    if (active) {
      return active;
    }

    // Check stored
    const stored = this.context.globalState.get<ConversationTrace[]>(TraceService.STORAGE_KEY, []);
    return stored.find(t => t.conversationId === conversationId);
  }

  /**
   * Get all traces (active + historical).
   */
  public getAllTraces(): ConversationTrace[] {
    const stored = this.context.globalState.get<ConversationTrace[]>(TraceService.STORAGE_KEY, []);
    const active = Array.from(this.activeTraces.values());
    return [...stored, ...active];
  }

  /**
   * Filter traces by criteria.
   */
  public filterTraces(filter: TraceFilter): TraceEntry[] {
    const allTraces = this.getAllTraces();
    let entries: TraceEntry[] = [];

    // Collect entries from matching conversations
    for (const trace of allTraces) {
      if (filter.conversationId && trace.conversationId !== filter.conversationId) {
        continue;
      }
      entries.push(...trace.entries);
    }

    // Apply filters
    if (filter.state) {
      entries = entries.filter(e => e.state === filter.state);
    }

    if (filter.turnRange) {
      entries = entries.filter(e => 
        e.turn >= filter.turnRange!.from && e.turn <= filter.turnRange!.to
      );
    }

    if (filter.timeRange) {
      entries = entries.filter(e => 
        e.timestamp >= filter.timeRange!.from && e.timestamp <= filter.timeRange!.to
      );
    }

    if (filter.errorsOnly) {
      entries = entries.filter(e => e.error !== undefined);
    }

    if (filter.toolsOnly) {
      entries = entries.filter(e => e.toolsUsed && e.toolsUsed.length > 0);
    }

    return entries;
  }

  /**
   * Generate summary statistics for traces.
   */
  public getSummary(): TraceSummary {
    const allTraces = this.getAllTraces();
    const allEntries = allTraces.flatMap(t => t.entries);

    if (allEntries.length === 0) {
      return {
        totalTraces: 0,
        totalTurns: 0,
        averageTurnDuration: 0,
        mostCommonState: 'Observe',
        totalErrors: 0,
        totalToolExecutions: 0,
        successRate: 100
      };
    }

    const totalTraces = allTraces.length;
    const totalTurns = allTraces.reduce((sum, t) => sum + t.totalTurns, 0);
    const averageTurnDuration = allEntries.reduce((sum, e) => sum + e.duration, 0) / allEntries.length;

    // Count states (excluding Observe)
    const stateCounts = new Map<AgentState, number>();
    allEntries.filter(e => e.state !== 'Observe').forEach(e => {
      stateCounts.set(e.state, (stateCounts.get(e.state) || 0) + 1);
    });
    const mostCommonState = Array.from(stateCounts.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'Plan';

    const totalErrors = allEntries.filter(e => e.error !== undefined).length;
    const totalToolExecutions = allEntries
      .filter(e => e.toolsUsed)
      .reduce((sum, e) => sum + (e.toolsUsed?.length || 0), 0);

    const successRate = ((allEntries.length - totalErrors) / allEntries.length) * 100;

    return {
      totalTraces,
      totalTurns,
      averageTurnDuration,
      mostCommonState,
      totalErrors,
      totalToolExecutions,
      successRate
    };
  }

  /**
   * Clear all stored traces (for testing or reset).
   */
  public clearAllTraces(): void {
    this.activeTraces.clear();
    this.context.globalState.update(TraceService.STORAGE_KEY, []);
    this.traceCounter = 0;
  }

  /**
   * Persist traces to storage.
   */
  private async saveTraces(): Promise<void> {
    const stored = this.context.globalState.get<ConversationTrace[]>(TraceService.STORAGE_KEY, []);
    const completed = Array.from(this.activeTraces.values()).filter(t => t.endTime);
    const updated = [...stored, ...completed];
    
    // Limit total stored traces to prevent storage overflow
    const MAX_STORED_TRACES = 50;
    if (updated.length > MAX_STORED_TRACES) {
      updated.splice(0, updated.length - MAX_STORED_TRACES);
    }
    
    await this.context.globalState.update(TraceService.STORAGE_KEY, updated);
  }
}
