/**
 * StatisticsPanel - Displays token usage, cost, and response time metrics.
 * Supports both single-agent and multi-agent (Plan + Act) modes.
 */

import * as vscode from 'vscode';
import { MetricsService } from '../services/MetricsService';
import { ExportService } from '../services/ExportService';
import { ConfigService } from '../services/ConfigService';
import { AgentConfigurationService } from '../services/AgentConfigurationService';
import { ConversationMetrics, StatisticsSummary } from '../models/Statistics';
import type { AgentConfiguration } from '../models/AgentRole';

export class StatisticsPanel {
  public static readonly viewType = 'ai-agent.statisticsPanel';
  private panel: vscode.WebviewPanel | undefined;
  private metricsService: MetricsService;
  private exportService: ExportService;
  private configService: ConfigService | AgentConfigurationService;
  private extensionUri: vscode.Uri;
  private updateInterval: NodeJS.Timeout | undefined;
  private currentConfig: AgentConfiguration | any;
  private configChangeDisposable: vscode.Disposable | undefined;

  constructor(
    extensionUri: vscode.Uri,
    metricsService: MetricsService,
    exportService: ExportService,
    configService: ConfigService | AgentConfigurationService
  ) {
    this.extensionUri = extensionUri;
    this.metricsService = metricsService;
    this.exportService = exportService;
    this.configService = configService;

    // Load initial configuration
    if (configService instanceof AgentConfigurationService) {
      this.currentConfig = configService.getConfig();
      console.log('[StatisticsPanel] Initial config loaded:', this.currentConfig.mode);
      
      this.configChangeDisposable = configService.onConfigurationChange((newConfig) => {
        console.log('[StatisticsPanel] Config changed from', this.currentConfig.mode, 'to', newConfig.mode);
        this.currentConfig = newConfig;
        if (this.panel) {
          this.refreshData();
        }
      });
    } else {
      this.currentConfig = (configService as ConfigService).getConfig();
    }
  }

  /**
   * Show the statistics panel.
   */
  public show(): void {
    if (this.panel) {
      this.panel.reveal(vscode.ViewColumn.Two);
      return;
    }

    // Create new panel
    this.panel = vscode.window.createWebviewPanel(
      StatisticsPanel.viewType,
      'Agent Statistics',
      vscode.ViewColumn.Two,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [this.extensionUri]
      }
    );

    // Get initial data
    const summary = this.metricsService.getSummary();
    const allMetrics = this.metricsService.getAllMetrics();
    let executionMode = 'legacy';
    let provider = 'unknown';
    let model = 'unknown';
    
    if (this.configService instanceof AgentConfigurationService) {
      const config = this.currentConfig as AgentConfiguration;
      executionMode = config.mode || 'legacy';
      
      if (config.mode === 'single') {
        provider = config.provider || 'unknown';
        model = config.model || 'unknown';
      } else {
        provider = `Plan: ${config.plan?.provider || 'unknown'} | Act: ${config.act?.provider || 'unknown'}`;
        model = `Plan: ${config.plan?.model || 'unknown'} | Act: ${config.act?.model || 'unknown'}`;
      }
    } else {
      provider = (this.currentConfig as any).provider || 'unknown';
      model = (this.currentConfig as any).model || 'unknown';
    }

    this.panel.webview.html = this.getHtmlForWebviewWithData(
      this.panel.webview,
      summary,
      allMetrics,
      executionMode,
      provider,
      model
    );

    // Handle messages from webview
    this.panel.webview.onDidReceiveMessage(
      (message) => this.handleMessage(message),
      undefined
    );

    // Handle panel disposal
    this.panel.onDidDispose(() => {
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
      }
      this.panel = undefined;
    }, undefined);

    // Auto-refresh every 5 seconds
    this.updateInterval = setInterval(() => {
      this.refreshData();
    }, 5000);

    // Initial data load
    this.refreshData();
  }

  /**
   * Dispose the panel.
   */
  public dispose(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    if (this.configChangeDisposable) {
      this.configChangeDisposable.dispose();
    }
    if (this.panel) {
      this.panel.dispose();
      this.panel = undefined;
    }
  }

  /**
   * Refresh statistics data and update webview.
   */
  private refreshData(): void {
    if (!this.panel) {
      return;
    }

    console.log('[StatisticsPanel] refreshData() called');
    
    const summary = this.metricsService.getSummary();
    const allMetrics = this.metricsService.getAllMetrics();
    
    let executionMode = 'legacy';
    let provider = 'unknown';
    let model = 'unknown';
    
    if (this.configService instanceof AgentConfigurationService) {
      const config = this.currentConfig as AgentConfiguration;
      executionMode = config.mode || 'legacy';
      
      console.log('[StatisticsPanel] Current config mode:', config.mode, 'Provider:', config.mode === 'single' ? config.provider : `${config.plan?.provider}/${config.act?.provider}`);
      
      if (config.mode === 'single') {
        provider = config.provider || 'unknown';
        model = config.model || 'unknown';
      } else {
        // Multi-agent: show both Plan and Act
        provider = `Plan: ${config.plan?.provider || 'unknown'} | Act: ${config.act?.provider || 'unknown'}`;
        model = `Plan: ${config.plan?.model || 'unknown'} | Act: ${config.act?.model || 'unknown'}`;
      }
    } else {
      provider = (this.currentConfig as any).provider || 'unknown';
      model = (this.currentConfig as any).model || 'unknown';
    }
    
    console.log('[StatisticsPanel] Display - Mode:', executionMode, 'Provider:', provider, 'Model:', model);
    
    // Instead of relying on webview JavaScript, regenerate entire HTML with fresh data
    this.panel.webview.html = this.getHtmlForWebviewWithData(
      this.panel.webview,
      summary,
      allMetrics,
      executionMode,
      provider,
      model
    );
  }

  /**
   * Handle messages from webview.
   */
  private async handleMessage(message: any): Promise<void> {
    switch (message.type) {
      case 'log':
        console.log(message.message);
        break;
        
      case 'refresh':
        this.refreshData();
        break;

      case 'exportCSV':
        await this.exportToCSV();
        break;

      case 'exportJSON':
        await this.exportToJSON();
        break;

      case 'copyToClipboard':
        await this.copyToClipboard(message.data);
        break;

      case 'clearMetrics':
        await this.clearAllMetrics();
        break;
    }
  }

  /**
   * Export metrics to CSV.
   */
  private async exportToCSV(): Promise<void> {
    const metrics = this.metricsService.getAllMetrics();
    if (metrics.length === 0) {
      vscode.window.showInformationMessage('No metrics to export');
      return;
    }

    const exportData = this.exportService.exportMetricsToCSV(metrics);
    await this.exportService.saveToFile(exportData);
  }

  /**
   * Export metrics to JSON.
   */
  private async exportToJSON(): Promise<void> {
    const metrics = this.metricsService.getAllMetrics();
    if (metrics.length === 0) {
      vscode.window.showInformationMessage('No metrics to export');
      return;
    }

    const exportData = this.exportService.exportMetricsToJSON(metrics);
    await this.exportService.saveToFile(exportData);
  }

  /**
   * Copy data to clipboard.
   */
  private async copyToClipboard(format: 'csv' | 'json'): Promise<void> {
    const metrics = this.metricsService.getAllMetrics();
    if (metrics.length === 0) {
      vscode.window.showInformationMessage('No metrics to copy');
      return;
    }

    const exportData = format === 'csv'
      ? this.exportService.exportMetricsToCSV(metrics)
      : this.exportService.exportMetricsToJSON(metrics);

    await this.exportService.copyToClipboard(exportData);
  }

  /**
   * Clear all metrics with confirmation.
   */
  private async clearAllMetrics(): Promise<void> {
    const confirm = await vscode.window.showWarningMessage(
      'Are you sure you want to clear all metrics? This cannot be undone.',
      { modal: true },
      'Clear All'
    );

    if (confirm === 'Clear All') {
      this.metricsService.clearAllMetrics();
      this.refreshData();
      vscode.window.showInformationMessage('All metrics cleared');
    }
  }

  /**
   * Generate HTML for the webview with data rendered server-side.
   */
  private getHtmlForWebviewWithData(
    webview: vscode.Webview,
    summary: StatisticsSummary,
    metrics: ConversationMetrics[],
    executionMode: string,
    provider: string,
    model: string
  ): string {
    const modeDisplay = executionMode === 'single' ? '👤 Single-Agent' : executionMode === 'multi' ? '🤝 Multi-Agent (Plan + Act)' : '⚙️ Legacy';
    
    // Format provider and model for multi-agent display
    let providerDisplay = provider;
    let modelDisplay = model;
    
    if (provider.includes('|')) {
      // Multi-agent: format as two lines
      const parts = provider.split('|').map(p => p.trim());
      providerDisplay = `<div style="line-height: 1.6;">${parts[0]}<br/>${parts[1]}</div>`;
    }
    
    if (model.includes('|')) {
      // Multi-agent: format as two lines
      const parts = model.split('|').map(m => m.trim());
      modelDisplay = `<div style="line-height: 1.6;">${parts[0]}<br/>${parts[1]}</div>`;
    }
    
    // Build metrics table rows
    const metricsRows = metrics.length === 0 
      ? '<tr><td colspan="8" style="text-align: center; padding: 40px; color: var(--vscode-descriptionForeground);">No conversation metrics available</td></tr>'
      : metrics.map(m => `
        <tr>
          <td><span class="status-badge ${m.endTime ? 'status-ended' : 'status-active'}">${m.endTime ? 'Ended' : 'Active'}</span></td>
          <td>${m.provider}</td>
          <td>${m.model}</td>
          <td>${m.messageCount}</td>
          <td>${m.totalTokens.toLocaleString()}</td>
          <td>$${m.totalCost.toFixed(4)}</td>
          <td>${m.averageResponseTime.toFixed(0)}</td>
          <td>${new Date(m.startTime).toLocaleString()}</td>
        </tr>
      `).join('');

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Statistics</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      margin: 0;
    }
    h1, h2 {
      margin-top: 0;
      border-bottom: 1px solid var(--vscode-panel-border);
      padding-bottom: 10px;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }
    .metric-card {
      background: var(--vscode-editor-background);
      border: 1px solid var(--vscode-panel-border);
      border-radius: 4px;
      padding: 15px;
    }
    .metric-label {
      font-size: 12px;
      color: var(--vscode-descriptionForeground);
      margin-bottom: 5px;
    }
    .metric-value {
      font-size: 24px;
      font-weight: bold;
      color: var(--vscode-textLink-foreground);
    }
    .metric-unit {
      font-size: 14px;
      color: var(--vscode-descriptionForeground);
      margin-left: 5px;
    }
    .button-group {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    button {
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 8px 16px;
      cursor: pointer;
      border-radius: 2px;
      font-size: 13px;
    }
    button:hover {
      background: var(--vscode-button-hoverBackground);
    }
    button.secondary {
      background: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }
    button.secondary:hover {
      background: var(--vscode-button-secondaryHoverBackground);
    }
    button.danger {
      background: var(--vscode-inputValidation-errorBackground);
      color: var(--vscode-inputValidation-errorForeground);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    th, td {
      text-align: left;
      padding: 8px;
      border-bottom: 1px solid var(--vscode-panel-border);
    }
    th {
      background: var(--vscode-editor-background);
      font-weight: 600;
      position: sticky;
      top: 0;
    }
    tr:hover {
      background: var(--vscode-list-hoverBackground);
    }
    .status-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 600;
    }
    .status-active {
      background: var(--vscode-testing-iconPassed);
      color: var(--vscode-editor-background);
    }
    .status-ended {
      background: var(--vscode-descriptionForeground);
      color: var(--vscode-editor-background);
    }
  </style>
</head>
<body>
  <h1>📊 Agent Statistics</h1>

  <div class="button-group">
    <button onclick="vscode.postMessage({type: 'refresh'})">🔄 Refresh</button>
    <button onclick="vscode.postMessage({type: 'exportCSV'})">📄 Export CSV</button>
    <button onclick="vscode.postMessage({type: 'exportJSON'})">📦 Export JSON</button>
    <button class="secondary" onclick="vscode.postMessage({type: 'copyToClipboard', data: 'json'})">📋 Copy JSON</button>
    <button class="danger" onclick="vscode.postMessage({type: 'clearMetrics'})">🗑️ Clear All</button>
  </div>

  <h2>Summary</h2>
  <div class="summary-grid">
    <div class="metric-card">
      <div class="metric-label">Execution Mode</div>
      <div class="metric-value" style="font-size: 16px;">${modeDisplay}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total Conversations</div>
      <div class="metric-value">${summary.totalConversations}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total Messages</div>
      <div class="metric-value">${summary.totalMessages}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total Tokens</div>
      <div class="metric-value">${summary.totalTokens.toLocaleString()}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total Cost</div>
      <div class="metric-value">$${summary.totalCost.toFixed(4)}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Avg Response Time</div>
      <div class="metric-value">${summary.averageResponseTime.toFixed(0)}<span class="metric-unit">ms</span></div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Provider</div>
      <div class="metric-value" style="font-size: 13px;">${providerDisplay}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Model</div>
      <div class="metric-value" style="font-size: 13px;">${modelDisplay}</div>
    </div>
  </div>

  <h2>Conversation History</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th>
        <th>Provider</th>
        <th>Model</th>
        <th>Messages</th>
        <th>Tokens</th>
        <th>Cost</th>
        <th>Avg Time (ms)</th>
        <th>Started</th>
      </tr>
    </thead>
    <tbody>
      ${metricsRows}
    </tbody>
  </table>

  <script>
    const vscode = acquireVsCodeApi();
  </script>
</body>
</html>`;
  }

  /**
   * Generate HTML for the webview (empty template - now replaced by getHtmlForWebviewWithData).
   */
  private getHtmlForWebview(webview: vscode.Webview): string {
    // This is kept for reference but getHtmlForWebviewWithData is now used instead
    const now = new Date();
    return this.getHtmlForWebviewWithData(webview, { 
      totalConversations: 0, 
      totalMessages: 0, 
      totalTokens: 0, 
      totalCost: 0, 
      averageResponseTime: 0,
      topProvider: 'unknown',
      topModel: 'unknown',
      dateRange: { from: now, to: now }
    }, [], 'legacy', 'unknown', 'unknown');
  }
}
