import * as vscode from 'vscode';
import { ReasoningPanel } from '../../src/panels/ReasoningPanel';
import { ReasoningChain } from '../../src/models/AgentMessage';

jest.mock('vscode', () => ({
  window: {
    createWebviewPanel: jest.fn(),
    showErrorMessage: jest.fn()
  },
  workspace: {
    fs: {
      readFile: jest.fn()
    }
  },
  Uri: {
    joinPath: jest.fn((...parts: any[]) => ({ path: parts.map(p => p.path ?? p).join('/') }))
  },
  ViewColumn: {
    Two: 2
  }
}));

describe('ReasoningPanel', () => {
  let mockPanel: any;
  let mockCoordinator: any;

  beforeEach(() => {
    jest.clearAllMocks();

    mockPanel = {
      webview: {
        html: '',
        postMessage: jest.fn()
      },
      reveal: jest.fn(),
      onDidDispose: jest.fn((handler: Function) => {
        return { dispose: jest.fn() };
      })
    };

    mockCoordinator = {
      requestReasoning: jest.fn(async () => ({
        steps: [{ action: 'Test', rationale: 'Because', chosen: true }],
        summary: 'Summary',
        confidence: 0.5
      } as ReasoningChain))
    };

    (vscode.window.createWebviewPanel as jest.Mock).mockReturnValue(mockPanel);
    (vscode.workspace.fs.readFile as jest.Mock).mockResolvedValue(Buffer.from('<html></html>'));
  });

  it('loads reasoning and posts update to webview', async () => {
    const panel = new ReasoningPanel({ path: '/mock/extension' } as vscode.Uri, mockCoordinator);

    await panel.showReasoning('planner-1');

    expect(vscode.window.createWebviewPanel).toHaveBeenCalled();
    expect(mockCoordinator.requestReasoning).toHaveBeenCalledWith('planner-1');
    expect(mockPanel.webview.postMessage).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'updateReasoning', agentId: 'planner-1' })
    );
  });
});
