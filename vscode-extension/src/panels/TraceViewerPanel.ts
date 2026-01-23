/**
 * TraceViewerPanel - Visualizes agent state transitions using VSCode Tree View.
 * Displays orchestrator flow: Observe → Plan → Act → Verify with tool details.
 */

import * as vscode from 'vscode';
import { TraceService } from '../services/TraceService';
import { ExportService } from '../services/ExportService';
import {
  ConversationTrace,
  TraceEntry,
  TraceTreeNode,
  AgentState,
  ToolExecution
} from '../models/Trace';

export class TraceViewerPanel implements vscode.TreeDataProvider<TraceTreeNode> {
  private _onDidChangeTreeData: vscode.EventEmitter<TraceTreeNode | undefined | null | void> = 
    new vscode.EventEmitter<TraceTreeNode | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<TraceTreeNode | undefined | null | void> = 
    this._onDidChangeTreeData.event;

  private traceService: TraceService;
  private exportService: ExportService;
  private treeView: vscode.TreeView<TraceTreeNode>;
  private currentConversationId: string | undefined;

  constructor(
    context: vscode.ExtensionContext,
    traceService: TraceService,
    exportService: ExportService
  ) {
    this.traceService = traceService;
    this.exportService = exportService;

    // Register tree view
    this.treeView = vscode.window.createTreeView('ai-agent.traceViewer', {
      treeDataProvider: this,
      showCollapseAll: true
    });

    context.subscriptions.push(this.treeView);

    // Register commands
    context.subscriptions.push(
      vscode.commands.registerCommand('ai-agent.refreshTraces', () => this.refresh()),
      vscode.commands.registerCommand('ai-agent.exportTraces', () => this.exportTraces()),
      vscode.commands.registerCommand('ai-agent.clearTraces', () => this.clearTraces()),
      vscode.commands.registerCommand('ai-agent.showTraceDetails', (node: TraceTreeNode) => 
        this.showTraceDetails(node)
      )
    );
  }

  /**
   * Set the current conversation to display.
   */
  public setConversation(conversationId: string): void {
    this.currentConversationId = conversationId;
    this.refresh();
  }

  /**
   * Refresh the tree view.
   */
  public refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  /**
   * Get tree item representation.
   */
  getTreeItem(element: TraceTreeNode): vscode.TreeItem {
    const treeItem = new vscode.TreeItem(
      element.label,
      element.children && element.children.length > 0
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None
    );

    treeItem.tooltip = element.tooltip;
    treeItem.contextValue = element.type;

    // Set icons based on type
    switch (element.type) {
      case 'conversation':
        treeItem.iconPath = new vscode.ThemeIcon('comment-discussion');
        break;
      case 'turn':
        treeItem.iconPath = new vscode.ThemeIcon('debug-step-over');
        break;
      case 'state':
        treeItem.iconPath = this.getStateIcon(element.data as TraceEntry);
        break;
      case 'tool':
        treeItem.iconPath = new vscode.ThemeIcon('tools');
        break;
      case 'error':
        treeItem.iconPath = new vscode.ThemeIcon('error');
        break;
    }

    // Add click command for detail view
    if (element.data) {
      treeItem.command = {
        command: 'ai-agent.showTraceDetails',
        title: 'Show Details',
        arguments: [element]
      };
    }

    return treeItem;
  }

  /**
   * Get children for tree node.
   */
  getChildren(element?: TraceTreeNode): vscode.ProviderResult<TraceTreeNode[]> {
    if (!element) {
      // Root level: show all conversations
      return this.getConversationNodes();
    }

    // Return children if available
    return element.children || [];
  }

  /**
   * Get conversation nodes (root level).
   */
  private getConversationNodes(): TraceTreeNode[] {
    const traces = this.currentConversationId
      ? [this.traceService.getTrace(this.currentConversationId)].filter(Boolean) as ConversationTrace[]
      : this.traceService.getAllTraces();

    if (traces.length === 0) {
      return [{
        id: 'empty',
        label: 'No traces available',
        type: 'conversation',
        collapsibleState: 'none'
      }];
    }

    return traces.map(trace => this.buildConversationNode(trace));
  }

  /**
   * Build tree node for a conversation.
   */
  private buildConversationNode(trace: ConversationTrace): TraceTreeNode {
    const turnNodes = this.groupEntriesByTurn(trace.entries);

    return {
      id: trace.conversationId,
      label: `Conversation: ${trace.provider}/${trace.model} (${trace.totalTurns} turns)`,
      type: 'conversation',
      tooltip: `Started: ${trace.startTime.toLocaleString()}\nEnded: ${trace.endTime?.toLocaleString() || 'Active'}`,
      children: turnNodes,
      collapsibleState: 'collapsed'
    };
  }

  /**
   * Group trace entries by turn.
   */
  private groupEntriesByTurn(entries: TraceEntry[]): TraceTreeNode[] {
    const turnMap = new Map<number, TraceEntry[]>();

    entries.forEach(entry => {
      const turnEntries = turnMap.get(entry.turn) || [];
      turnEntries.push(entry);
      turnMap.set(entry.turn, turnEntries);
    });

    const turnNodes: TraceTreeNode[] = [];
    turnMap.forEach((turnEntries, turnNum) => {
      turnNodes.push(this.buildTurnNode(turnNum, turnEntries));
    });

    return turnNodes.sort((a, b) => {
      const aTurn = parseInt(a.id.split('-')[1]);
      const bTurn = parseInt(b.id.split('-')[1]);
      return aTurn - bTurn;
    });
  }

  /**
   * Build tree node for a turn.
   */
  private buildTurnNode(turnNum: number, entries: TraceEntry[]): TraceTreeNode {
    const totalDuration = entries.reduce((sum, e) => sum + e.duration, 0);
    const hasError = entries.some(e => e.error !== undefined);

    const stateNodes = entries.map(entry => this.buildStateNode(entry));

    return {
      id: `turn-${turnNum}`,
      label: `Turn ${turnNum}${hasError ? ' ⚠️' : ''} (${totalDuration.toFixed(0)}ms)`,
      type: 'turn',
      tooltip: `Total duration: ${totalDuration.toFixed(2)}ms\n${entries.length} state transitions`,
      children: stateNodes,
      collapsibleState: 'collapsed'
    };
  }

  /**
   * Build tree node for a state transition.
   */
  private buildStateNode(entry: TraceEntry): TraceTreeNode {
    const children: TraceTreeNode[] = [];

    // Add tool executions if present
    if (entry.toolsUsed && entry.toolsUsed.length > 0) {
      entry.toolsUsed.forEach((tool, idx) => {
        children.push(this.buildToolNode(tool, idx));
      });
    }

    // Add error if present
    if (entry.error) {
      children.push({
        id: `${entry.id}-error`,
        label: `❌ Error: ${entry.error.message}`,
        type: 'error',
        tooltip: `Type: ${entry.error.type}\n${entry.error.stackTrace || 'No stack trace'}`,
        data: entry.error,
        collapsibleState: 'none'
      });
    }

    const stateIcon = this.getStateEmoji(entry.state);
    const errorIndicator = entry.error ? ' ⚠️' : '';

    return {
      id: entry.id,
      label: `${stateIcon} ${entry.state}${errorIndicator} (${entry.duration.toFixed(0)}ms)`,
      type: 'state',
      tooltip: this.buildStateTooltip(entry),
      data: entry,
      children: children.length > 0 ? children : undefined,
      collapsibleState: children.length > 0 ? 'collapsed' : 'none'
    };
  }

  /**
   * Build tree node for a tool execution.
   */
  private buildToolNode(tool: ToolExecution, index: number): TraceTreeNode {
    const statusIcon = tool.status === 'success' ? '✅' : '❌';

    return {
      id: `tool-${index}-${tool.name}`,
      label: `${statusIcon} ${tool.name} (${tool.duration.toFixed(0)}ms)`,
      type: 'tool',
      tooltip: `Status: ${tool.status}\nDuration: ${tool.duration.toFixed(2)}ms\nInput: ${JSON.stringify(tool.input)}\n${tool.error || ''}`,
      data: tool,
      collapsibleState: 'none'
    };
  }

  /**
   * Get icon for agent state.
   */
  private getStateIcon(entry: TraceEntry): vscode.ThemeIcon {
    if (entry.error) {
      return new vscode.ThemeIcon('error', new vscode.ThemeColor('errorForeground'));
    }

    switch (entry.state) {
      case 'Observe':
        return new vscode.ThemeIcon('eye');
      case 'Plan':
        return new vscode.ThemeIcon('lightbulb');
      case 'Act':
        return new vscode.ThemeIcon('play');
      case 'Verify':
        return new vscode.ThemeIcon('check');
      default:
        return new vscode.ThemeIcon('circle-outline');
    }
  }

  /**
   * Get emoji for agent state.
   */
  private getStateEmoji(state: AgentState): string {
    switch (state) {
      case 'Observe': return '👁️';
      case 'Plan': return '💡';
      case 'Act': return '▶️';
      case 'Verify': return '✅';
      default: return '⚪';
    }
  }

  /**
   * Build tooltip text for state node.
   */
  private buildStateTooltip(entry: TraceEntry): string {
    let tooltip = `State: ${entry.state}\n`;
    tooltip += `Timestamp: ${entry.timestamp.toLocaleString()}\n`;
    tooltip += `Duration: ${entry.duration.toFixed(2)}ms\n`;

    if (entry.input) {
      tooltip += `\nInput:\n${this.truncate(entry.input, 200)}`;
    }

    if (entry.output) {
      tooltip += `\n\nOutput:\n${this.truncate(entry.output, 200)}`;
    }

    if (entry.toolsUsed && entry.toolsUsed.length > 0) {
      tooltip += `\n\nTools: ${entry.toolsUsed.map(t => t.name).join(', ')}`;
    }

    return tooltip;
  }

  /**
   * Show detailed view of trace entry.
   */
  private async showTraceDetails(node: TraceTreeNode): Promise<void> {
    if (!node.data) {
      return;
    }

    const doc = await vscode.workspace.openTextDocument({
      content: JSON.stringify(node.data, null, 2),
      language: 'json'
    });

    await vscode.window.showTextDocument(doc, { preview: true });
  }

  /**
   * Export all traces.
   */
  private async exportTraces(): Promise<void> {
    const traces = this.traceService.getAllTraces();
    if (traces.length === 0) {
      vscode.window.showInformationMessage('No traces to export');
      return;
    }

    const choice = await vscode.window.showQuickPick(['JSON', 'CSV'], {
      placeHolder: 'Select export format'
    });

    if (!choice) {
      return;
    }

    const exportData = choice === 'JSON'
      ? this.exportService.exportTracesToJSON(traces)
      : this.exportService.exportTracesToCSV(traces.flatMap(t => t.entries));

    await this.exportService.saveToFile(exportData);
  }

  /**
   * Clear all traces with confirmation.
   */
  private async clearTraces(): Promise<void> {
    const confirm = await vscode.window.showWarningMessage(
      'Are you sure you want to clear all traces? This cannot be undone.',
      { modal: true },
      'Clear All'
    );

    if (confirm === 'Clear All') {
      this.traceService.clearAllTraces();
      this.refresh();
      vscode.window.showInformationMessage('All traces cleared');
    }
  }

  /**
   * Truncate long strings.
   */
  private truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  }
}
