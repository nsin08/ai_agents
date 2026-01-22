import * as vscode from 'vscode';
import { ChatPanel } from './panels/ChatPanel';
import { ConfigPanel } from './panels/ConfigPanel';
import { AgentService } from './services/AgentService';
import { ConfigService } from './services/ConfigService';

let chatPanel: ChatPanel | undefined;
let configPanel: ConfigPanel | undefined;
let agentService: AgentService;
let configService: ConfigService;

export function activate(context: vscode.ExtensionContext) {
  console.log('AI Agent Extension activating...');

  // Initialize services
  configService = new ConfigService(context);
  agentService = new AgentService(configService);

  // Register command: Start Conversation
  const startConversationCmd = vscode.commands.registerCommand(
    'ai-agent.startConversation',
    async () => {
      console.log('Starting conversation...');
      if (!chatPanel) {
        chatPanel = new ChatPanel(context.extensionUri, agentService, configService);
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
        configPanel = new ConfigPanel(context.extensionUri, configService);
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
        configPanel = new ConfigPanel(context.extensionUri, configService);
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
    resetSessionCmd
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
}
