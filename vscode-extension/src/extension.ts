import * as vscode from 'vscode';
import { ChatPanel } from './panels/ChatPanel';
import { ConfigPanel } from './panels/ConfigPanel';
import { StatisticsPanel } from './panels/StatisticsPanel';
import { TraceViewerPanel } from './panels/TraceViewerPanel';
import { AgentService } from './services/AgentService';
import { ConfigService } from './services/ConfigService';
import { MetricsService } from './services/MetricsService';
import { TraceService } from './services/TraceService';
import { ExportService } from './services/ExportService';

let chatPanel: ChatPanel | undefined;
let configPanel: ConfigPanel | undefined;
let statisticsPanel: StatisticsPanel | undefined;
let traceViewerPanel: TraceViewerPanel | undefined;
let agentService: AgentService;
let configService: ConfigService;
let metricsService: MetricsService;
let traceService: TraceService;
let exportService: ExportService;

export function activate(context: vscode.ExtensionContext) {
  console.log('AI Agent Extension activating...');

  // Initialize services
  configService = new ConfigService(context);
  metricsService = new MetricsService(context);
  traceService = new TraceService(context);
  exportService = new ExportService();
  agentService = new AgentService(configService, metricsService, traceService);

  // Initialize UI panels
  statisticsPanel = new StatisticsPanel(context.extensionUri, metricsService, exportService);
  traceViewerPanel = new TraceViewerPanel(context, traceService, exportService);

  // Register command: Start Conversation
  const startConversationCmd = vscode.commands.registerCommand(
    'ai-agent.startConversation',
    async () => {
      console.log('Starting conversation...');
      if (!chatPanel) {
        chatPanel = new ChatPanel(
          context.extensionUri,
          agentService,
          configService,
          () => { chatPanel = undefined; }
        );
      }
      chatPanel.show();
    }
  );

  // Register command: Switch Provider
  const switchProviderCmd = vscode.commands.registerCommand(
    'ai-agent.switchProvider',
    async () => {
      console.log('Switching provider...');
      if (!configPanel) {
        configPanel = new ConfigPanel(
          context.extensionUri,
          configService,
          () => { configPanel = undefined; }
        );
      }
      configPanel.show();
    }
  );

  // Register command: Switch Model
  const switchModelCmd = vscode.commands.registerCommand(
    'ai-agent.switchModel',
    async () => {
      console.log('Switching model...');
      if (!configPanel) {
        configPanel = new ConfigPanel(
          context.extensionUri,
          configService,
          () => { configPanel = undefined; }
        );
      }
      configPanel.show();
    }
  );

  // Register command: Reset Session
  const resetSessionCmd = vscode.commands.registerCommand(
    'ai-agent.resetSession',
    async () => {
      console.log('Resetting session...');
      await agentService.resetSession();
      vscode.window.showInformationMessage('Session reset');
    }
  );

  // Register command: Show Statistics (Phase 2)
  const showStatisticsCmd = vscode.commands.registerCommand(
    'ai-agent.showStatistics',
    () => {
      console.log('Showing statistics...');
      if (statisticsPanel) {
        statisticsPanel.show();
      }
    }
  );

  // Register command: Show Trace Viewer (Phase 2)
  const showTraceViewerCmd = vscode.commands.registerCommand(
    'ai-agent.showTraceViewer',
    () => {
      console.log('Showing trace viewer...');
      if (traceViewerPanel) {
        traceViewerPanel.refresh();
      }
    }
  );

  // Subscribe to configuration changes
  vscode.workspace.onDidChangeConfiguration((event) => {
    if (event.affectsConfiguration('aiAgent')) {
      configService.reload();
      agentService.updateConfiguration();
    }
  });

  context.subscriptions.push(
    startConversationCmd,
    switchProviderCmd,
    switchModelCmd,
    resetSessionCmd,
    showStatisticsCmd,
    showTraceViewerCmd
  );

  console.log('AI Agent Extension activated successfully');
}

export function deactivate() {
  console.log('AI Agent Extension deactivating...');
  if (chatPanel) {
    chatPanel.dispose();
  }
  if (configPanel) {
    configPanel.dispose();
  }
  if (statisticsPanel) {
    statisticsPanel.dispose();
  }
}
