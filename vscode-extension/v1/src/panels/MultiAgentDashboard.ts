/**
 * MultiAgentDashboard - Displays multi-agent coordination status and controls.
 */

import * as vscode from 'vscode';
import { MultiAgentCoordinator } from '../services/MultiAgentCoordinator';
import { MetricsService } from '../services/MetricsService';
import { TraceService } from '../services/TraceService';
import { SpecialistAgent } from '../models/AgentRole';
import { AgentMessage, Subtask } from '../models/AgentMessage';

export class MultiAgentDashboard {
  public static readonly viewType = 'ai-agent.multiAgentDashboard';
  private panel: vscode.WebviewPanel | undefined;
  private extensionUri: vscode.Uri;
  private coordinator: MultiAgentCoordinator;
  private metricsService: MetricsService | undefined;
  private traceService: TraceService | undefined;

  constructor(
    extensionUri: vscode.Uri,
    coordinator: MultiAgentCoordinator,
    metricsService?: MetricsService,
    traceService?: TraceService
  ) {
    this.extensionUri = extensionUri;
    this.coordinator = coordinator;
    this.metricsService = metricsService;
    this.traceService = traceService;
  }

  public async show(): Promise<void> {
    if (this.panel) {
      this.panel.reveal(vscode.ViewColumn.Two);
      return;
    }

    this.panel = vscode.window.createWebviewPanel(
      MultiAgentDashboard.viewType,
      'Multi-Agent Dashboard',
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
      this.coordinator.setCallbacks(undefined);
      this.panel = undefined;
    }, undefined);

    this.coordinator.setCallbacks({
      onStateChange: (state) => this.updateCoordinatorState(state),
      onAgentsUpdate: (agents) => this.updateAgentStatus(agents),
      onQueueUpdate: (queue) => this.updateTaskQueue(queue),
      onProgressUpdate: (progress) => this.updateProgress(progress),
      onLogUpdate: (messages) => this.updateCommunicationLog(messages)
    });

    await this.updateCoordinatorState(this.coordinator.getState());
    await this.updateAgentStatus(this.coordinator.getRegisteredAgents());
  }

  public dispose(): void {
    if (this.panel) {
      this.panel.dispose();
      this.panel = undefined;
    }
  }

  public async updateAgentStatus(agents: SpecialistAgent[]): Promise<void> {
    this.postMessage({
      type: 'updateAgents',
      agents
    });
    await this.updateMetrics(agents);
  }

  public async updateTaskQueue(queue: Subtask[]): Promise<void> {
    this.postMessage({
      type: 'updateQueue',
      queue: queue.map((task) => ({
        description: task.description,
        status: task.status,
        dependencies: task.dependencies
      }))
    });
  }

  public async updateProgress(percentage: number): Promise<void> {
    this.postMessage({
      type: 'updateProgress',
      progress: percentage
    });
  }

  public async updateCommunicationLog(messages: AgentMessage[]): Promise<void> {
    this.postMessage({
      type: 'updateLog',
      log: messages.map((message) => `${message.from} -> ${message.to}: ${message.content}`)
    });
  }

  public async updateCoordinatorState(state: string): Promise<void> {
    this.postMessage({
      type: 'updateState',
      state
    });
  }

  private async updateMetrics(agents: SpecialistAgent[]): Promise<void> {
    if (!this.metricsService) {
      return;
    }

    const metrics = agents.map((agent) => {
      const stats = this.metricsService?.getAgentMetrics(agent.id);
      return {
        id: agent.id,
        role: agent.role,
        totalTokens: stats?.totalTokens ?? 0,
        totalDuration: stats?.totalDuration ?? 0,
        executionCount: stats?.executionCount ?? 0
      };
    });

    this.postMessage({
      type: 'updateMetrics',
      metrics,
      coordinatorOverhead: this.metricsService.getCoordinatorOverhead()
    });
  }

  private async handleMessage(message: any): Promise<void> {
    switch (message.type) {
      case 'submitTask':
        await this.handleSubmitTask();
        break;
      case 'showReasoning':
        if (message.agentId) {
          await vscode.commands.executeCommand('ai-agent.showReasoningPanel', message.agentId);
        }
        break;
      case 'exportLog':
        await vscode.commands.executeCommand('ai-agent.exportCoordinationLog');
        break;
      case 'stopCoordination':
        this.coordinator.cancel();
        vscode.window.showInformationMessage('Coordination cancel requested.');
        break;
    }
  }

  private async handleSubmitTask(): Promise<void> {
    const task = await vscode.window.showInputBox({
      prompt: 'Enter the task for multi-agent coordination'
    });
    if (!task) {
      return;
    }

    try {
      await this.coordinator.orchestrate(task);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      vscode.window.showErrorMessage(`Multi-agent orchestration failed: ${message}`);
    }
  }

  private async getHtmlForWebview(): Promise<string> {
    const uri = vscode.Uri.joinPath(this.extensionUri, 'src', 'views', 'multiAgentDashboard.html');
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
