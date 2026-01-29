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

    (vscode.window.createWebviewPanel as jest.Mock).mockReturnValue(mockPanel);
    (vscode.workspace.fs.readFile as jest.Mock).mockResolvedValue(Buffer.from('<html></html>'));
  });

  it('loads reasoning and posts update to webview', async () => {
    const panel = new ReasoningPanel({ path: '/mock/extension' } as vscode.Uri, {} as any);

    await panel.showReasoning('planner-1');
    panel.updateReasoning('planner-1', {
      steps: [{ action: 'Test', rationale: 'Because', chosen: true }],
      summary: 'Summary',
      confidence: 0.5
    } as ReasoningChain);

    expect(vscode.window.createWebviewPanel).toHaveBeenCalled();
    expect(mockPanel.webview.postMessage).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'updateReasoning', agentId: 'planner-1' })
    );
  });
});
