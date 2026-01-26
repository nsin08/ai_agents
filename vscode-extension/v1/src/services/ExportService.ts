/**
 * ExportService - Exports metrics and traces to CSV/JSON formats.
 * Provides file save functionality for external analysis.
 */

import * as vscode from 'vscode';
import { ConversationMetrics, ExportFormat } from '../models/Statistics';
import { ConversationTrace, TraceEntry } from '../models/Trace';

export class ExportService {
  /**
   * Export conversation metrics to CSV format.
   */
  public exportMetricsToCSV(metrics: ConversationMetrics[]): ExportFormat {
    const headers = [
      'Conversation ID',
      'Provider',
      'Model',
      'Start Time',
      'End Time',
      'Message Count',
      'Total Tokens',
      'Prompt Tokens',
      'Completion Tokens',
      'Total Cost (USD)',
      'Avg Response Time (ms)'
    ];

    const rows = metrics.map(m => [
      m.conversationId,
      m.provider,
      m.model,
      m.startTime.toISOString(),
      m.endTime?.toISOString() || 'Active',
      m.messageCount.toString(),
      m.totalTokens.toString(),
      m.promptTokens.toString(),
      m.completionTokens.toString(),
      m.totalCost.toFixed(4),
      m.averageResponseTime.toFixed(2)
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(cell => this.escapeCsvCell(cell)).join(','))
      .join('\n');

    return {
      format: 'csv',
      data: csv,
      filename: `agent-metrics-${this.getTimestamp()}.csv`,
      mimeType: 'text/csv'
    };
  }

  /**
   * Export conversation metrics to JSON format.
   */
  public exportMetricsToJSON(metrics: ConversationMetrics[]): ExportFormat {
    const json = JSON.stringify(metrics, null, 2);

    return {
      format: 'json',
      data: json,
      filename: `agent-metrics-${this.getTimestamp()}.json`,
      mimeType: 'application/json'
    };
  }

  /**
   * Export conversation traces to JSON format.
   */
  public exportTracesToJSON(traces: ConversationTrace[]): ExportFormat {
    const json = JSON.stringify(traces, null, 2);

    return {
      format: 'json',
      data: json,
      filename: `agent-traces-${this.getTimestamp()}.json`,
      mimeType: 'application/json'
    };
  }

  /**
   * Export trace entries to CSV format.
   */
  public exportTracesToCSV(entries: TraceEntry[]): ExportFormat {
    const headers = [
      'Trace ID',
      'Conversation ID',
      'Timestamp',
      'Turn',
      'State',
      'Duration (ms)',
      'Input',
      'Output',
      'Tools Used',
      'Error'
    ];

    const rows = entries.map(e => [
      e.id,
      e.conversationId,
      e.timestamp.toISOString(),
      e.turn.toString(),
      e.state,
      e.duration.toFixed(2),
      this.truncate(e.input || '', 100),
      this.truncate(e.output || '', 100),
      e.toolsUsed?.map(t => t.name).join('; ') || '',
      e.error?.message || ''
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(cell => this.escapeCsvCell(cell)).join(','))
      .join('\n');

    return {
      format: 'csv',
      data: csv,
      filename: `agent-traces-${this.getTimestamp()}.csv`,
      mimeType: 'text/csv'
    };
  }

  /**
   * Save export data to file with user prompt.
   */
  public async saveToFile(exportData: ExportFormat): Promise<boolean> {
    const uri = await vscode.window.showSaveDialog({
      defaultUri: vscode.Uri.file(exportData.filename),
      filters: {
        [exportData.format.toUpperCase()]: [exportData.format]
      }
    });

    if (!uri) {
      return false; // User cancelled
    }

    try {
      const buffer = Buffer.from(exportData.data, 'utf8');
      await vscode.workspace.fs.writeFile(uri, buffer);
      vscode.window.showInformationMessage(`Exported to ${uri.fsPath}`);
      return true;
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to save file: ${error}`);
      return false;
    }
  }

  /**
   * Copy export data to clipboard.
   */
  public async copyToClipboard(exportData: ExportFormat): Promise<boolean> {
    try {
      await vscode.env.clipboard.writeText(exportData.data);
      vscode.window.showInformationMessage(`${exportData.format.toUpperCase()} data copied to clipboard`);
      return true;
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to copy to clipboard: ${error}`);
      return false;
    }
  }

  /**
   * Escape CSV cell value (handle commas, quotes, newlines).
   */
  private escapeCsvCell(value: string): string {
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replace(/"/g, '""')}"`;
    }
    return value;
  }

  /**
   * Truncate long strings for CSV export.
   */
  private truncate(value: string, maxLength: number): string {
    if (value.length <= maxLength) {
      return value;
    }
    return value.substring(0, maxLength - 3) + '...';
  }

  /**
   * Generate timestamp string for filenames.
   */
  private getTimestamp(): string {
    const now = new Date();
    return now.toISOString().replace(/[:.]/g, '-').substring(0, 19);
  }
}
