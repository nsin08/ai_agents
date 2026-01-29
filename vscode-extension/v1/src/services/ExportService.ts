/**
 * ExportService - Exports metrics and traces to CSV/JSON formats.
 * Provides file save functionality for external analysis.
 */

import * as vscode from 'vscode';
import { ConversationMetrics, ExportFormat } from '../models/Statistics';
import { ConversationTrace, TraceEntry } from '../models/Trace';
import { ConversationHistoryEntry } from '../models/History';

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
   * Export conversation history to Markdown format.
   */
  public exportConversationToMarkdown(entry: ConversationHistoryEntry): ExportFormat {
    const header = [
      `# Conversation ${entry.id}`,
      '',
      `- Created: ${new Date(entry.createdAt).toLocaleString()}`,
      `- Updated: ${new Date(entry.updatedAt).toLocaleString()}`,
      `- Mode: ${entry.agentMode}`,
      `- Provider: ${entry.provider || 'n/a'}`,
      `- Model: ${entry.model || 'n/a'}`,
      entry.planProvider ? `- Plan Provider: ${entry.planProvider}` : undefined,
      entry.planModel ? `- Plan Model: ${entry.planModel}` : undefined,
      entry.actProvider ? `- Act Provider: ${entry.actProvider}` : undefined,
      entry.actModel ? `- Act Model: ${entry.actModel}` : undefined,
      '',
      '---',
      ''
    ].filter(Boolean);

    const messages = entry.messages.map((message) => {
      const timestamp = new Date(message.timestamp).toLocaleString();
      return [
        `## ${message.role.toUpperCase()} (${timestamp})`,
        '',
        message.content,
        ''
      ].join('\n');
    });

    const content = [...header, ...messages].join('\n');
    return {
      format: 'md',
      data: content,
      filename: `agent-conversation-${entry.id}.md`,
      mimeType: 'text/markdown'
    };
  }

  /**
   * Export conversation history to HTML format.
   */
  public exportConversationToHTML(entry: ConversationHistoryEntry): ExportFormat {
    const escapeHtml = (value: string): string =>
      value.replace(/[&<>"']/g, (char) => {
        const map: Record<string, string> = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#039;'
        };
        return map[char];
      });

    const messages = entry.messages.map((message) => {
      const timestamp = new Date(message.timestamp).toLocaleString();
      return `
        <div class="message ${message.role}">
          <div class="message-header">
            <span>${message.role.toUpperCase()}</span>
            <span>${escapeHtml(timestamp)}</span>
          </div>
          <pre class="message-body">${escapeHtml(message.content)}</pre>
        </div>
      `;
    }).join('\n');

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Conversation ${entry.id}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 24px;
      background: #f7f7f9;
      color: #1a1a1a;
    }
    h1 {
      margin-top: 0;
    }
    .meta {
      margin-bottom: 24px;
      font-size: 14px;
      color: #444;
    }
    .meta div {
      margin-bottom: 4px;
    }
    .message {
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    .message.user {
      border-left: 4px solid #0066cc;
    }
    .message.assistant {
      border-left: 4px solid #2e7d32;
    }
    .message-header {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #666;
      margin-bottom: 8px;
    }
    .message-body {
      white-space: pre-wrap;
      font-family: \"Courier New\", monospace;
      font-size: 13px;
      margin: 0;
    }
  </style>
</head>
<body>
  <h1>Conversation ${escapeHtml(entry.id)}</h1>
  <div class="meta">
    <div><strong>Created:</strong> ${escapeHtml(new Date(entry.createdAt).toLocaleString())}</div>
    <div><strong>Updated:</strong> ${escapeHtml(new Date(entry.updatedAt).toLocaleString())}</div>
    <div><strong>Mode:</strong> ${escapeHtml(String(entry.agentMode))}</div>
    <div><strong>Provider:</strong> ${escapeHtml(entry.provider || 'n/a')}</div>
    <div><strong>Model:</strong> ${escapeHtml(entry.model || 'n/a')}</div>
  </div>
  ${messages}
</body>
</html>`;

    return {
      format: 'html',
      data: html,
      filename: `agent-conversation-${entry.id}.html`,
      mimeType: 'text/html'
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
