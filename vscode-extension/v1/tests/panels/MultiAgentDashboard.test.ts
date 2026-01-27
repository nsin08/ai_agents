import * as vscode from 'vscode';
import { MultiAgentDashboard } from '../../src/panels/MultiAgentDashboard';
import { AgentRole, AgentStatus, SpecialistAgent } from '../../src/models/AgentRole';
import { CoordinatorCallbacks } from '../../src/services/MultiAgentCoordinator';

jest.mock('vscode', () => ({
  window: {
    createWebviewPanel: jest.fn(),
    showInputBox: jest.fn(),
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn()
  },
  workspace: {
    fs: {
      readFile: jest.fn()
    }
  },
  commands: {
    executeCommand: jest.fn()
  },
  Uri: {
    joinPath: jest.fn((...parts: any[]) => ({ path: parts.map(p => p.path ?? p).join('/') }))
  },
  ViewColumn: {
    Two: 2
  }
}));

describe('MultiAgentDashboard', () => {
  let mockPanel: any;
  let messageHandler: Function | undefined;
  let callbacks: CoordinatorCallbacks | undefined;

  const buildAgent = (role: AgentRole): SpecialistAgent => ({
    id: `${role}-1`,
    role,
    status: AgentStatus.IDLE,
    config: {} as any,
    capabilities: []
  });

  const coordinator = {
    setCallbacks: jest.fn((cb?: CoordinatorCallbacks) => {
      callbacks = cb;
    }),
    getState: jest.fn(() => 'idle'),
    getRegisteredAgents: jest.fn(() => [buildAgent(AgentRole.PLANNER), buildAgent(AgentRole.EXECUTOR)]),
    orchestrate: jest.fn(async () => undefined),
    cancel: jest.fn()
  } as any;

  beforeEach(() => {
    jest.clearAllMocks();
    callbacks = undefined;
    messageHandler = undefined;

    mockPanel = {
      webview: {
        html: '',
        postMessage: jest.fn(),
        onDidReceiveMessage: jest.fn((handler: Function) => {
          messageHandler = handler;
          return { dispose: jest.fn() };
        })
      },
      reveal: jest.fn(),
      dispose: jest.fn(),
      onDidDispose: jest.fn((handler: Function) => {
        return { dispose: jest.fn() };
      })
    };

    (vscode.window.createWebviewPanel as jest.Mock).mockReturnValue(mockPanel);
    (vscode.workspace.fs.readFile as jest.Mock).mockResolvedValue(Buffer.from('<html></html>'));
  });

  it('shows dashboard and posts initial state and agents', async () => {
    const dashboard = new MultiAgentDashboard(
      { path: '/mock/extension' } as vscode.Uri,
      coordinator,
      undefined,
      undefined
    );

    await dashboard.show();

    expect(vscode.window.createWebviewPanel).toHaveBeenCalled();
    expect(coordinator.setCallbacks).toHaveBeenCalled();
    expect(mockPanel.webview.postMessage).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'updateState' })
    );
    expect(mockPanel.webview.postMessage).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'updateAgents' })
    );
  });

  it('handles submitTask message and invokes coordinator', async () => {
    (vscode.window.showInputBox as jest.Mock).mockResolvedValue('Test task');

    const dashboard = new MultiAgentDashboard(
      { path: '/mock/extension' } as vscode.Uri,
      coordinator,
      undefined,
      undefined
    );

    await dashboard.show();
    await messageHandler?.({ type: 'submitTask' });

    expect(coordinator.orchestrate).toHaveBeenCalledWith('Test task');
  });

  it('handles showReasoning message and invokes command', async () => {
    const dashboard = new MultiAgentDashboard(
      { path: '/mock/extension' } as vscode.Uri,
      coordinator,
      undefined,
      undefined
    );

    await dashboard.show();
    await messageHandler?.({ type: 'showReasoning', agentId: 'planner-1' });

    expect(vscode.commands.executeCommand).toHaveBeenCalledWith(
      'ai-agent.showReasoningPanel',
      'planner-1'
    );
  });

  it('handles stopCoordination message and cancels coordinator', async () => {
    const dashboard = new MultiAgentDashboard(
      { path: '/mock/extension' } as vscode.Uri,
      coordinator,
      undefined,
      undefined
    );

    await dashboard.show();
    await messageHandler?.({ type: 'stopCoordination' });

    expect(coordinator.cancel).toHaveBeenCalled();
  });

  it('renders queue updates with dependencies', async () => {
    const dashboard = new MultiAgentDashboard(
      { path: '/mock/extension' } as vscode.Uri,
      coordinator,
      undefined,
      undefined
    );

    await dashboard.show();
    callbacks?.onQueueUpdate?.([
      { description: 'Task A', status: 'pending', dependencies: [] },
      { description: 'Task B', status: 'in-progress', dependencies: ['subtask-1'] }
    ] as any);

    expect(mockPanel.webview.postMessage).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'updateQueue' })
    );
  });
});
