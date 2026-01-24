/**
 * StatisticsPanel - Displays token usage, cost, and response time metrics.
 * Provides export functionality for conversation metrics.
 */

import * as vscode from 'vscode';
import { MetricsService } from '../services/MetricsService';
import { ExportService } from '../services/ExportService';
import { ConversationMetrics, StatisticsSummary } from '../models/Statistics';

export class StatisticsPanel {
  public static readonly viewType = 'ai-agent.statisticsPanel';
  private panel: vscode.WebviewPanel | undefined;
  private metricsService: MetricsService;
  private exportService: ExportService;
  private extensionUri: vscode.Uri;
  private updateInterval: NodeJS.Timeout | undefined;

  constructor(
    extensionUri: vscode.Uri,
    metricsService: MetricsService,
    exportService: ExportService
  ) {
    this.extensionUri = extensionUri;
    this.metricsService = metricsService;
    this.exportService = exportService;
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

    this.panel.webview.html = this.getHtmlForWebview(this.panel.webview);

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

    const summary = this.metricsService.getSummary();
    const allMetrics = this.metricsService.getAllMetrics();

    this.panel.webview.postMessage({
      type: 'updateData',
      summary,
      metrics: allMetrics
    });
  }

  /**
   * Handle messages from webview.
   */
  private async handleMessage(message: any): Promise<void> {
    switch (message.type) {
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
   * Generate HTML for the webview.
   */
  private getHtmlForWebview(webview: vscode.Webview): string {
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
    .empty-state {
      text-align: center;
      padding: 40px;
      color: var(--vscode-descriptionForeground);
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
    <button onclick="refresh()">🔄 Refresh</button>
    <button onclick="exportCSV()">📄 Export CSV</button>
    <button onclick="exportJSON()">📦 Export JSON</button>
    <button class="secondary" onclick="copyToClipboard('json')">📋 Copy JSON</button>
    <button class="danger" onclick="clearMetrics()">🗑️ Clear All</button>
  </div>

  <h2>Summary</h2>
  <div class="summary-grid" id="summaryGrid">
    <!-- Populated by JS -->
  </div>

  <h2>Conversation History</h2>
  <div id="metricsTable">
    <!-- Populated by JS -->
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    // Handle messages from extension
    window.addEventListener('message', event => {
      const message = event.data;
      if (message.type === 'updateData') {
        updateSummary(message.summary);
        updateMetricsTable(message.metrics);
      }
    });

    function updateSummary(summary) {
      const grid = document.getElementById('summaryGrid');
      grid.innerHTML = \`
        <div class="metric-card">
          <div class="metric-label">Total Conversations</div>
          <div class="metric-value">\${summary.totalConversations}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total Messages</div>
          <div class="metric-value">\${summary.totalMessages}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total Tokens</div>
          <div class="metric-value">\${summary.totalTokens.toLocaleString()}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total Cost</div>
          <div class="metric-value">$\${summary.totalCost.toFixed(4)}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Avg Response Time</div>
          <div class="metric-value">\${summary.averageResponseTime.toFixed(0)}<span class="metric-unit">ms</span></div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Top Provider</div>
          <div class="metric-value" style="font-size: 18px;">\${summary.topProvider}</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Top Model</div>
          <div class="metric-value" style="font-size: 16px;">\${summary.topModel}</div>
        </div>
      \`;
    }

    function updateMetricsTable(metrics) {
      const container = document.getElementById('metricsTable');
      
      if (metrics.length === 0) {
        container.innerHTML = '<div class="empty-state">No conversation metrics available</div>';
        return;
      }

      container.innerHTML = \`
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
            \${metrics.map(m => \`
              <tr>
                <td><span class="status-badge \${m.endTime ? 'status-ended' : 'status-active'}">\${m.endTime ? 'Ended' : 'Active'}</span></td>
                <td>\${m.provider}</td>
                <td>\${m.model}</td>
                <td>\${m.messageCount}</td>
                <td>\${m.totalTokens.toLocaleString()}</td>
                <td>$\${m.totalCost.toFixed(4)}</td>
                <td>\${m.averageResponseTime.toFixed(0)}</td>
                <td>\${new Date(m.startTime).toLocaleString()}</td>
              </tr>
            \`).join('')}
          </tbody>
        </table>
      \`;
    }

    function refresh() {
      vscode.postMessage({ type: 'refresh' });
    }

    function exportCSV() {
      vscode.postMessage({ type: 'exportCSV' });
    }

    function exportJSON() {
      vscode.postMessage({ type: 'exportJSON' });
    }

    function copyToClipboard(format) {
      vscode.postMessage({ type: 'copyToClipboard', data: format });
    }

    function clearMetrics() {
      vscode.postMessage({ type: 'clearMetrics' });
    }
  </script>
</body>
</html>`;
  }
}
