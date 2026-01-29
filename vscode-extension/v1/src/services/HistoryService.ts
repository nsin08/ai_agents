/**
 * HistoryService - Persists conversation history per workspace and provides indexed search.
 */

import * as vscode from 'vscode';
import { TraceService } from './TraceService';
import {
  AgentMode,
  ConversationHistoryEntry,
  ConversationIndexEntry,
  HistoryIndex,
  HistorySearchFilters,
  WorkspaceContext
} from '../models/History';

export interface HistorySaveOptions {
  agentMode: AgentMode;
  provider?: string;
  model?: string;
  planProvider?: string;
  planModel?: string;
  actProvider?: string;
  actModel?: string;
  workspaceUri?: vscode.Uri;
  metadata?: Record<string, any>;
}

export interface HistorySessionSnapshot {
  id: string;
  createdAt: number;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
    tokens?: {
      prompt: number;
      completion: number;
    };
    responseTime?: number;
  }>;
}

export class HistoryService {
  private readonly context: vscode.ExtensionContext;
  private readonly traceService?: TraceService;
  private readonly encoder = new TextEncoder();
  private readonly decoder = new TextDecoder('utf-8');

  constructor(context: vscode.ExtensionContext, traceService?: TraceService) {
    this.context = context;
    this.traceService = traceService;
  }

  public async saveConversation(session: HistorySessionSnapshot, options: HistorySaveOptions): Promise<void> {
    const root = await this.getHistoryRoot(options.workspaceUri);
    if (!root) {
      console.warn('[HistoryService] No workspace available for history storage.');
      return;
    }

    await this.ensureDirectory(root);

    const workspace = await this.getWorkspaceContext(root);
    const trace = this.traceService?.getTrace(session.id);
    const now = Date.now();

    const entry: ConversationHistoryEntry = {
      id: session.id,
      createdAt: session.createdAt,
      updatedAt: now,
      agentMode: options.agentMode,
      provider: options.provider,
      model: options.model,
      planProvider: options.planProvider,
      planModel: options.planModel,
      actProvider: options.actProvider,
      actModel: options.actModel,
      workspace,
      messages: session.messages,
      trace,
      metadata: options.metadata
    };

    const fileName = `${session.id}.json`;
    const fileUri = vscode.Uri.joinPath(root, fileName);
    const payload = JSON.stringify(entry, null, 2);
    await vscode.workspace.fs.writeFile(fileUri, this.encoder.encode(payload));

    const index = await this.readIndex(root);
    const updatedEntry = this.buildIndexEntry(entry, fileName);
    const existingIndex = index.entries.findIndex((item) => item.id === entry.id);
    if (existingIndex >= 0) {
      index.entries[existingIndex] = updatedEntry;
    } else {
      index.entries.unshift(updatedEntry);
    }

    await this.writeIndex(root, index);
  }

  public async loadConversation(id: string, workspaceUri?: vscode.Uri): Promise<ConversationHistoryEntry | undefined> {
    const root = await this.getHistoryRoot(workspaceUri);
    if (!root) {
      return undefined;
    }

    const fileUri = vscode.Uri.joinPath(root, `${id}.json`);
    const data = await this.readFileIfExists(fileUri);
    if (!data) {
      return undefined;
    }

    return JSON.parse(this.decoder.decode(data)) as ConversationHistoryEntry;
  }

  public async search(filters: HistorySearchFilters, workspaceUri?: vscode.Uri): Promise<ConversationIndexEntry[]> {
    const root = await this.getHistoryRoot(workspaceUri);
    if (!root) {
      return [];
    }

    const index = await this.readIndex(root);
    const normalizedQuery = filters.query?.trim().toLowerCase();

    return index.entries.filter((entry) => {
      if (filters.agentMode && entry.agentMode !== filters.agentMode) {
        return false;
      }
      if (filters.provider && entry.provider !== filters.provider) {
        return false;
      }
      if (filters.model && entry.model !== filters.model) {
        return false;
      }
      if (filters.startDate && entry.createdAt < filters.startDate) {
        return false;
      }
      if (filters.endDate && entry.createdAt > filters.endDate) {
        return false;
      }
      if (normalizedQuery) {
        const content = entry.content.toLowerCase();
        if (!content.includes(normalizedQuery)) {
          return false;
        }
      }
      return true;
    });
  }

  public async listConversations(workspaceUri?: vscode.Uri): Promise<ConversationIndexEntry[]> {
    const root = await this.getHistoryRoot(workspaceUri);
    if (!root) {
      return [];
    }

    const index = await this.readIndex(root);
    return index.entries;
  }

  public async deleteConversation(id: string, workspaceUri?: vscode.Uri): Promise<boolean> {
    const root = await this.getHistoryRoot(workspaceUri);
    if (!root) {
      return false;
    }

    const index = await this.readIndex(root);
    const nextEntries = index.entries.filter((entry) => entry.id !== id);
    if (nextEntries.length === index.entries.length) {
      return false;
    }

    index.entries = nextEntries;
    await this.writeIndex(root, index);

    const fileUri = vscode.Uri.joinPath(root, `${id}.json`);
    await this.deleteFileIfExists(fileUri);
    return true;
  }

  public async clearAll(workspaceUri?: vscode.Uri): Promise<void> {
    const root = await this.getHistoryRoot(workspaceUri);
    if (!root) {
      return;
    }

    const index = await this.readIndex(root);
    for (const entry of index.entries) {
      const fileUri = vscode.Uri.joinPath(root, entry.fileName);
      await this.deleteFileIfExists(fileUri);
    }

    await this.writeIndex(root, { version: 1, updatedAt: Date.now(), entries: [] });
  }

  private buildIndexEntry(entry: ConversationHistoryEntry, fileName: string): ConversationIndexEntry {
    const content = entry.messages.map((message) => message.content).join('\n');
    const preview = this.buildPreview(entry);
    const lastMessageAt = entry.messages.length
      ? entry.messages[entry.messages.length - 1].timestamp
      : entry.updatedAt;

    return {
      id: entry.id,
      createdAt: entry.createdAt,
      updatedAt: entry.updatedAt,
      lastMessageAt,
      agentMode: entry.agentMode,
      provider: entry.provider,
      model: entry.model,
      planProvider: entry.planProvider,
      planModel: entry.planModel,
      actProvider: entry.actProvider,
      actModel: entry.actModel,
      messageCount: entry.messages.length,
      preview,
      content,
      fileName,
      workspace: entry.workspace
    };
  }

  private buildPreview(entry: ConversationHistoryEntry): string {
    const assistantMessage = entry.messages.find((message) => message.role === 'assistant');
    const source = assistantMessage?.content || entry.messages[0]?.content || '';
    const trimmed = source.replace(/\s+/g, ' ').trim();
    if (trimmed.length <= 140) {
      return trimmed;
    }
    return `${trimmed.substring(0, 137)}...`;
  }

  private async readIndex(root: vscode.Uri): Promise<HistoryIndex> {
    const indexUri = vscode.Uri.joinPath(root, 'index.json');
    const data = await this.readFileIfExists(indexUri);
    if (!data) {
      return { version: 1, updatedAt: Date.now(), entries: [] };
    }

    try {
      const parsed = JSON.parse(this.decoder.decode(data)) as HistoryIndex;
      return {
        version: parsed.version || 1,
        updatedAt: parsed.updatedAt || Date.now(),
        entries: parsed.entries || []
      };
    } catch (error) {
      console.warn('[HistoryService] Failed to parse index.json, rebuilding.', error);
      return { version: 1, updatedAt: Date.now(), entries: [] };
    }
  }

  private async writeIndex(root: vscode.Uri, index: HistoryIndex): Promise<void> {
    index.updatedAt = Date.now();
    const indexUri = vscode.Uri.joinPath(root, 'index.json');
    const payload = JSON.stringify(index, null, 2);
    await vscode.workspace.fs.writeFile(indexUri, this.encoder.encode(payload));
  }

  private async ensureDirectory(uri: vscode.Uri): Promise<void> {
    try {
      await vscode.workspace.fs.stat(uri);
    } catch (error) {
      await vscode.workspace.fs.createDirectory(uri);
    }
  }

  private async readFileIfExists(uri: vscode.Uri): Promise<Uint8Array | undefined> {
    try {
      return await vscode.workspace.fs.readFile(uri);
    } catch (error) {
      return undefined;
    }
  }

  private async deleteFileIfExists(uri: vscode.Uri): Promise<void> {
    try {
      await vscode.workspace.fs.delete(uri, { recursive: false, useTrash: true });
    } catch (error) {
      return;
    }
  }

  private async getHistoryRoot(workspaceUri?: vscode.Uri): Promise<vscode.Uri | undefined> {
    if (workspaceUri) {
      return vscode.Uri.joinPath(workspaceUri, '.vscode', 'agent-history');
    }

    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
      const folder = this.pickWorkspaceFolder(workspaceFolders);
      return vscode.Uri.joinPath(folder.uri, '.vscode', 'agent-history');
    }

    if (this.context.globalStorageUri) {
      return vscode.Uri.joinPath(this.context.globalStorageUri, 'agent-history');
    }

    return undefined;
  }

  private pickWorkspaceFolder(workspaceFolders: readonly vscode.WorkspaceFolder[]): vscode.WorkspaceFolder {
    const active = vscode.window.activeTextEditor?.document?.uri;
    if (active) {
      const match = workspaceFolders.find((folder) => active.fsPath.startsWith(folder.uri.fsPath));
      if (match) {
        return match;
      }
    }
    return workspaceFolders[0];
  }

  private async getWorkspaceContext(historyRoot: vscode.Uri): Promise<WorkspaceContext> {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
      const folder = this.pickWorkspaceFolder(workspaceFolders);
      return {
        name: folder.name,
        path: folder.uri.fsPath
      };
    }

    return {
      name: 'global',
      path: historyRoot.fsPath
    };
  }
}
