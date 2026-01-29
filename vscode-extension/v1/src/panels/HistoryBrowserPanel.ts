/**
 * HistoryBrowserPanel - Allows users to search, replay, and export conversation history.
 */

import * as vscode from 'vscode';
import { ExportService } from '../services/ExportService';
import { HistoryService } from '../services/HistoryService';
import { HistorySearchFilters } from '../models/History';

export class HistoryBrowserPanel {
  public static readonly viewType = 'ai-agent.historyBrowser';
  private panel: vscode.WebviewPanel | undefined;
  private extensionUri: vscode.Uri;
  private historyService: HistoryService;
  private exportService: ExportService;
  private activeConversationId: string | undefined;

  constructor(
    extensionUri: vscode.Uri,
    historyService: HistoryService,
    exportService: ExportService
  ) {
    this.extensionUri = extensionUri;
    this.historyService = historyService;
    this.exportService = exportService;
  }

  public async show(): Promise<void> {
    if (this.panel) {
      this.panel.reveal(vscode.ViewColumn.Two);
      return;
    }

    this.panel = vscode.window.createWebviewPanel(
      HistoryBrowserPanel.viewType,
      'Conversation History',
      vscode.ViewColumn.Two,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
        localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, 'src', 'views')]
      }
    );

    this.panel.webview.html = await this.getHtmlForWebview();

    this.panel.webview.onDidReceiveMessage(
      (message) => this.handleMessage(message),
      undefined
    );

    this.panel.onDidDispose(() => {
      this.panel = undefined;
    }, undefined);

    await this.refreshList();
  }

  public dispose(): void {
    if (this.panel) {
      this.panel.dispose();
      this.panel = undefined;
    }
  }

  private async handleMessage(message: any): Promise<void> {
    switch (message.type) {
      case 'refresh':
        await this.refreshList();
        break;
      case 'search':
        await this.applySearch(message.filters);
        break;
      case 'openConversation':
        await this.openConversation(message.id);
        break;
      case 'exportConversation':
        await this.exportConversation(message.id, message.format);
        break;
      case 'deleteConversation':
        await this.deleteConversation(message.id);
        break;
    }
  }

  private async refreshList(): Promise<void> {
    const entries = await this.historyService.listConversations();
    this.postMessage({
      type: 'historyList',
      entries,
      activeId: this.activeConversationId
    });
  }

  private async applySearch(filters: any): Promise<void> {
    const searchFilters: HistorySearchFilters = {
      query: filters?.query || undefined,
      agentMode: filters?.agentMode || undefined,
      startDate: filters?.startDate ? new Date(filters.startDate).getTime() : undefined,
      endDate: filters?.endDate ? new Date(filters.endDate).getTime() + 86400000 : undefined
    };

    const entries = await this.historyService.search(searchFilters);
    this.postMessage({
      type: 'historyList',
      entries,
      activeId: this.activeConversationId
    });
  }

  private async openConversation(id: string): Promise<void> {
    const entry = await this.historyService.loadConversation(id);
    if (!entry) {
      this.postMessage({ type: 'error', message: 'Conversation not found.' });
      return;
    }

    this.activeConversationId = id;
    this.postMessage({ type: 'conversationLoaded', entry });
    await this.refreshList();
  }

  private async exportConversation(id: string, format: string): Promise<void> {
    const entry = await this.historyService.loadConversation(id);
    if (!entry) {
      vscode.window.showErrorMessage('Conversation not found for export.');
      return;
    }

    let exportData;
    if (format === 'html') {
      exportData = this.exportService.exportConversationToHTML(entry);
    } else {
      exportData = this.exportService.exportConversationToMarkdown(entry);
    }

    await this.exportService.saveToFile(exportData);
  }

  private async deleteConversation(id: string): Promise<void> {
    const confirm = await vscode.window.showWarningMessage(
      'Delete this conversation history? This cannot be undone.',
      { modal: true },
      'Delete'
    );

    if (confirm !== 'Delete') {
      return;
    }

    const success = await this.historyService.deleteConversation(id);
    if (!success) {
      vscode.window.showWarningMessage('Conversation not found.');
      return;
    }

    if (this.activeConversationId === id) {
      this.activeConversationId = undefined;
      this.postMessage({ type: 'conversationCleared' });
    }

    await this.refreshList();
  }

  private async getHtmlForWebview(): Promise<string> {
    const uri = vscode.Uri.joinPath(this.extensionUri, 'src', 'views', 'historyBrowser.html');
    const data = await vscode.workspace.fs.readFile(uri);
    return new TextDecoder('utf-8').decode(data);
  }

  private postMessage(payload: any): void {
    if (!this.panel) {
      return;
    }
    this.panel.webview.postMessage(payload);
  }
}
