import * as vscode from 'vscode';
import { ChatPanel } from './panels/ChatPanel';
import { ConfigPanel } from './panels/ConfigPanel';
import { StatisticsPanel } from './panels/StatisticsPanel';
import { TraceViewerPanel } from './panels/TraceViewerPanel';
import { CodeSuggestionPanel } from './panels/CodeSuggestionPanel';
import { AgentService } from './services/AgentService';
import { ConfigService } from './services/ConfigService';
import { MetricsService } from './services/MetricsService';
import { TraceService } from './services/TraceService';
import { ExportService } from './services/ExportService';
import { CodeContextService } from './services/CodeContextService';
import { CodeInsertionService } from './services/CodeInsertionService';

let chatPanel: ChatPanel | undefined;
let configPanel: ConfigPanel | undefined;
let statisticsPanel: StatisticsPanel | undefined;
let traceViewerPanel: TraceViewerPanel | undefined;
let agentService: AgentService;
let configService: ConfigService;
let metricsService: MetricsService;
let traceService: TraceService;
let exportService: ExportService;
let codeContextService: CodeContextService;
let codeInsertionService: CodeInsertionService;

export function activate(context: vscode.ExtensionContext) {
  console.log('AI Agent Extension activating...');

  // Initialize services
  configService = new ConfigService(context);
  metricsService = new MetricsService(context);
  traceService = new TraceService(context);
  exportService = new ExportService();
  agentService = new AgentService(configService, metricsService, traceService);
  codeContextService = new CodeContextService();
  codeInsertionService = new CodeInsertionService();

  // Initialize UI panels
  statisticsPanel = new StatisticsPanel(context.extensionUri, metricsService, exportService, configService);
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

  // Register command: Send Selection to Agent (Phase 3)
  const sendSelectionCmd = vscode.commands.registerCommand(
    'ai-agent.sendSelection',
    async () => {
      console.log('Sending selection to agent...');
      const codeContext = await codeContextService.extractSelectedCode();
      if (!codeContext) {
        return;
      }

      // Format context for agent
      const formattedContext = codeContextService.formatContextForAgent(codeContext);

      // Show warning if sensitive data detected
      if (codeContext.containsSensitiveData && codeContext.sensitiveDataWarnings) {
        const proceed = await vscode.window.showWarningMessage(
          `Warning: Sensitive data detected (${codeContext.sensitiveDataWarnings.join(', ')}). Continue?`,
          'Yes', 'No'
        );
        if (proceed !== 'Yes') {
          return;
        }
      }

      // Start conversation with code context
      if (!chatPanel) {
        chatPanel = new ChatPanel(
          context.extensionUri,
          agentService,
          configService,
          () => { chatPanel = undefined; }
        );
      }
      chatPanel.show();
      chatPanel.sendMessage(formattedContext);
      vscode.window.showInformationMessage('Code selection sent to agent');
    }
  );

  // Register command: Send File to Agent (Phase 3)
  const sendFileCmd = vscode.commands.registerCommand(
    'ai-agent.sendFile',
    async () => {
      console.log('Sending file to agent...');
      const codeContext = await codeContextService.extractFileContent();
      if (!codeContext) {
        return;
      }

      // Format context for agent
      const formattedContext = codeContextService.formatContextForAgent(codeContext);

      // Show warning if sensitive data detected
      if (codeContext.containsSensitiveData && codeContext.sensitiveDataWarnings) {
        const proceed = await vscode.window.showWarningMessage(
          `Warning: Sensitive data detected (${codeContext.sensitiveDataWarnings.join(', ')}). Continue?`,
          'Yes', 'No'
        );
        if (proceed !== 'Yes') {
          return;
        }
      }

      // Start conversation with code context
      if (!chatPanel) {
        chatPanel = new ChatPanel(
          context.extensionUri,
          agentService,
          configService,
          () => { chatPanel = undefined; }
        );
      }
      chatPanel.show();
      chatPanel.sendMessage(formattedContext);
      vscode.window.showInformationMessage('File content sent to agent');
    }
  );

  // Register command: Show Code Suggestions (Phase 3)
  const showCodeSuggestionsCmd = vscode.commands.registerCommand(
    'ai-agent.showCodeSuggestions',
    async (agentResponse?: string) => {
      console.log('Showing code suggestions...');
      
      // If no response provided, get from chat history or prompt user
      if (!agentResponse) {
        agentResponse = await vscode.window.showInputBox({
          prompt: 'Paste agent response with code blocks',
          placeHolder: '```typescript\\nconst x = 1;\\n```'
        });
        
        if (!agentResponse) {
          return;
        }
      }

      CodeSuggestionPanel.createOrShow(
        context.extensionUri,
        codeInsertionService,
        codeContextService,
        agentResponse
      );
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
    showTraceViewerCmd,
    sendSelectionCmd,
    sendFileCmd,
    showCodeSuggestionsCmd
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
