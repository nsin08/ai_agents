import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as vscode from 'vscode';
import { HistoryService } from '../../src/services/HistoryService';

const createWorkspaceFolder = (root: string) => ({
  uri: { fsPath: root },
  name: path.basename(root)
});

describe('HistoryService', () => {
  let tempDir: string;
  let historyService: HistoryService;

  beforeEach(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'history-service-'));

    (vscode.workspace as any).workspaceFolders = [createWorkspaceFolder(tempDir)];
    (vscode.workspace as any).fs = {
      readFile: jest.fn((uri: any) => fs.promises.readFile(uri.fsPath)),
      writeFile: jest.fn((uri: any, data: Uint8Array) => fs.promises.writeFile(uri.fsPath, data)),
      stat: jest.fn((uri: any) => fs.promises.stat(uri.fsPath)),
      createDirectory: jest.fn((uri: any) => fs.promises.mkdir(uri.fsPath, { recursive: true })),
      delete: jest.fn((uri: any) => fs.promises.rm(uri.fsPath, { force: true }))
    };

    historyService = new HistoryService({} as any);
  });

  afterEach(() => {
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  it('saves and loads conversation history', async () => {
    const session = {
      id: 'session-1',
      createdAt: Date.now(),
      messages: [
        { role: 'user' as const, content: 'Hello', timestamp: Date.now() },
        { role: 'assistant' as const, content: 'Hi there', timestamp: Date.now() }
      ]
    };

    await historyService.saveConversation(session, {
      agentMode: 'single',
      provider: 'mock',
      model: 'llama2'
    });

    const loaded = await historyService.loadConversation('session-1');
    expect(loaded).toBeDefined();
    expect(loaded?.messages.length).toBe(2);
    expect(loaded?.provider).toBe('mock');

    const list = await historyService.listConversations();
    expect(list.length).toBe(1);
    expect(list[0].id).toBe('session-1');
  });

  it('searches by keyword, date, and mode', async () => {
    const now = Date.now();
    const sessionA = {
      id: 'session-a',
      createdAt: now - 1000,
      messages: [
        { role: 'user' as const, content: 'Build a dashboard', timestamp: now - 1000 }
      ]
    };
    const sessionB = {
      id: 'session-b',
      createdAt: now + 1000,
      messages: [
        { role: 'user' as const, content: 'Write tests', timestamp: now + 1000 }
      ]
    };

    await historyService.saveConversation(sessionA, { agentMode: 'single' });
    await historyService.saveConversation(sessionB, { agentMode: 'multi' });

    const keywordResults = await historyService.search({ query: 'dashboard' });
    expect(keywordResults.map(r => r.id)).toEqual(['session-a']);

    const dateResults = await historyService.search({ startDate: now, endDate: now + 2000 });
    expect(dateResults.map(r => r.id)).toEqual(['session-b']);

    const modeResults = await historyService.search({ agentMode: 'multi' });
    expect(modeResults.map(r => r.id)).toEqual(['session-b']);
  });

  it('deletes conversations and clears history', async () => {
    const session = {
      id: 'session-delete',
      createdAt: Date.now(),
      messages: [
        { role: 'user' as const, content: 'Remove me', timestamp: Date.now() }
      ]
    };

    await historyService.saveConversation(session, { agentMode: 'single' });
    const deleted = await historyService.deleteConversation('session-delete');
    expect(deleted).toBe(true);

    const listAfterDelete = await historyService.listConversations();
    expect(listAfterDelete.length).toBe(0);

    await historyService.saveConversation(session, { agentMode: 'single' });
    await historyService.clearAll();
    const listAfterClear = await historyService.listConversations();
    expect(listAfterClear.length).toBe(0);
  });
});
