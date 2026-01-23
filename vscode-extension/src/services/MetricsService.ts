/**
 * MetricsService - Collects and manages conversation metrics.
 * Tracks token usage, response times, costs, and provides aggregation.
 */

import * as vscode from 'vscode';
import {
  ConversationMetrics,
  MessageMetrics,
  ProviderRates,
  DEFAULT_PROVIDER_RATES,
  StatisticsSummary
} from '../models/Statistics';

export class MetricsService {
  private static readonly STORAGE_KEY = 'agentMetrics';
  private context: vscode.ExtensionContext;
  private activeConversations: Map<string, ConversationMetrics>;
  private providerRates: Map<string, ProviderRates>;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.activeConversations = new Map();
    this.providerRates = new Map();
    this.loadProviderRates();
  }

  /**
   * Load provider pricing rates.
   */
  private loadProviderRates(): void {
    for (const rate of DEFAULT_PROVIDER_RATES) {
      const key = `${rate.provider}:${rate.model}`;
      this.providerRates.set(key, rate);
    }
  }

  /**
   * Start tracking a new conversation.
   */
  public startConversation(conversationId: string, provider: string, model: string): void {
    const metrics: ConversationMetrics = {
      conversationId,
      provider,
      model,
      totalTokens: 0,
      promptTokens: 0,
      completionTokens: 0,
      totalCost: 0,
      messageCount: 0,
      averageResponseTime: 0,
      startTime: new Date()
    };
    this.activeConversations.set(conversationId, metrics);
  }

  /**
   * Record metrics for a single message exchange.
   */
  public recordMessage(
    conversationId: string,
    promptTokens: number,
    completionTokens: number,
    responseTime: number,
    toolsUsed?: string[],
    error?: string
  ): void {
    const metrics = this.activeConversations.get(conversationId);
    if (!metrics) {
      console.warn(`No active conversation found for ID: ${conversationId}`);
      return;
    }

    // Update token counts
    metrics.promptTokens += promptTokens;
    metrics.completionTokens += completionTokens;
    metrics.totalTokens = metrics.promptTokens + metrics.completionTokens;

    // Update message count
    metrics.messageCount += 1;

    // Update average response time (incremental average)
    const prevTotal = metrics.averageResponseTime * (metrics.messageCount - 1);
    metrics.averageResponseTime = (prevTotal + responseTime) / metrics.messageCount;

    // Calculate cost
    const messageCost = this.calculateCost(
      metrics.provider,
      metrics.model,
      promptTokens,
      completionTokens
    );
    metrics.totalCost += messageCost;

    // Update storage
    this.saveMetrics();
  }

  /**
   * End a conversation and persist final metrics.
   */
  public endConversation(conversationId: string): void {
    const metrics = this.activeConversations.get(conversationId);
    if (metrics) {
      metrics.endTime = new Date();
      this.activeConversations.delete(conversationId);
      this.saveMetrics();
    }
  }

  /**
   * Calculate cost for a message based on token usage and provider rates.
   */
  private calculateCost(
    provider: string,
    model: string,
    promptTokens: number,
    completionTokens: number
  ): number {
    // Try exact match first
    let rateKey = `${provider}:${model}`;
    let rates = this.providerRates.get(rateKey);

    // Fallback to provider default
    if (!rates) {
      rateKey = `${provider}:default`;
      rates = this.providerRates.get(rateKey);
    }

    // No rates found, assume free
    if (!rates) {
      return 0;
    }

    const promptCost = (promptTokens / 1000) * rates.promptTokenCostPer1K;
    const completionCost = (completionTokens / 1000) * rates.completionTokenCostPer1K;

    return promptCost + completionCost;
  }

  /**
   * Get metrics for a specific conversation.
   */
  public getConversationMetrics(conversationId: string): ConversationMetrics | undefined {
    return this.activeConversations.get(conversationId);
  }

  /**
   * Get all stored metrics (active + historical).
   */
  public getAllMetrics(): ConversationMetrics[] {
    const stored = this.context.globalState.get<ConversationMetrics[]>(MetricsService.STORAGE_KEY, []);
    const active = Array.from(this.activeConversations.values());
    return [...stored, ...active];
  }

  /**
   * Generate summary statistics across all conversations.
   */
  public getSummary(): StatisticsSummary {
    const allMetrics = this.getAllMetrics();

    if (allMetrics.length === 0) {
      return {
        totalConversations: 0,
        totalMessages: 0,
        totalTokens: 0,
        totalCost: 0,
        averageResponseTime: 0,
        topProvider: 'N/A',
        topModel: 'N/A',
        dateRange: {
          from: new Date(),
          to: new Date()
        }
      };
    }

    const totalConversations = allMetrics.length;
    const totalMessages = allMetrics.reduce((sum, m) => sum + m.messageCount, 0);
    const totalTokens = allMetrics.reduce((sum, m) => sum + m.totalTokens, 0);
    const totalCost = allMetrics.reduce((sum, m) => sum + m.totalCost, 0);
    const averageResponseTime = allMetrics.reduce((sum, m) => sum + m.averageResponseTime, 0) / totalConversations;

    // Find most used provider/model
    const providerCounts = new Map<string, number>();
    const modelCounts = new Map<string, number>();
    allMetrics.forEach(m => {
      providerCounts.set(m.provider, (providerCounts.get(m.provider) || 0) + 1);
      modelCounts.set(m.model, (modelCounts.get(m.model) || 0) + 1);
    });

    const topProvider = Array.from(providerCounts.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';
    const topModel = Array.from(modelCounts.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

    // Date range
    const dates = allMetrics.map(m => m.startTime.getTime());
    const from = new Date(Math.min(...dates));
    const to = new Date(Math.max(...dates));

    return {
      totalConversations,
      totalMessages,
      totalTokens,
      totalCost,
      averageResponseTime,
      topProvider,
      topModel,
      dateRange: { from, to }
    };
  }

  /**
   * Clear all stored metrics (for testing or reset).
   */
  public clearAllMetrics(): void {
    this.activeConversations.clear();
    this.context.globalState.update(MetricsService.STORAGE_KEY, []);
  }

  /**
   * Persist metrics to storage.
   */
  private async saveMetrics(): Promise<void> {
    const stored = this.context.globalState.get<ConversationMetrics[]>(MetricsService.STORAGE_KEY, []);
    const completed = Array.from(this.activeConversations.values()).filter(m => m.endTime);
    const updated = [...stored, ...completed];
    await this.context.globalState.update(MetricsService.STORAGE_KEY, updated);
  }
}
