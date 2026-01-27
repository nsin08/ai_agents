/**
 * ReasoningPanel - Displays agent reasoning chains.
 * Supports both single-agent and multi-agent (Plan + Act stages) modes.
 */

import * as vscode from 'vscode';
import { MultiAgentCoordinator } from '../services/MultiAgentCoordinator';
import { AgentConfigurationService } from '../services/AgentConfigurationService';
import { ReasoningChain } from '../models/AgentMessage';
import type { AgentConfiguration } from '../models/AgentRole';

export class ReasoningPanel {
  public static readonly viewType = 'ai-agent.reasoningPanel';
  private panel: vscode.WebviewPanel | undefined;
  private extensionUri: vscode.Uri;
  private coordinator: MultiAgentCoordinator;
  private configService: AgentConfigurationService | undefined;
  private currentMode: 'single' | 'multi' | 'legacy' = 'legacy';

  constructor(
    extensionUri: vscode.Uri,
    coordinator: MultiAgentCoordinator,
    configService?: AgentConfigurationService
  ) {
    this.extensionUri = extensionUri;
    this.coordinator = coordinator;
    this.configService = configService;

    if (configService) {
      const config = configService.getConfig() as AgentConfiguration;
      this.currentMode = config.mode === 'single' ? 'single' : config.mode === 'multi' ? 'multi' : 'legacy';
      
      configService.onConfigurationChange((newConfig) => {
        this.currentMode = newConfig.mode === 'single' ? 'single' : newConfig.mode === 'multi' ? 'multi' : 'legacy';
      });
    }
  }

  public async showReasoning(agentId: string): Promise<void> {
    if (!this.panel) {
      this.panel = vscode.window.createWebviewPanel(
        ReasoningPanel.viewType,
        'Agent Reasoning',
        vscode.ViewColumn.Two,
        {
          enableScripts: true,
          retainContextWhenHidden: true,
          localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, 'src', 'views')]
        }
      );

      this.panel.webview.html = await this.getHtmlForWebview();

      this.panel.onDidDispose(() => {
        this.panel = undefined;
      }, undefined);
    } else {
      this.panel.reveal(vscode.ViewColumn.Two);
    }
  }

  public updateReasoning(agentId: string, reasoning: ReasoningChain): void {
    if (!this.panel) {
      return;
    }
    this.panel.webview.postMessage({
      type: 'updateReasoning',
      agentId,
      reasoning,
      mode: this.currentMode
    });
  }

  public dispose(): void {
    if (this.panel) {
      this.panel.dispose();
      this.panel = undefined;
    }
  }

  private async getHtmlForWebview(): Promise<string> {
    const uri = vscode.Uri.joinPath(this.extensionUri, 'src', 'views', 'reasoningPanel.html');
    const data = await vscode.workspace.fs.readFile(uri);
    return new TextDecoder('utf-8').decode(data);
  }
}
