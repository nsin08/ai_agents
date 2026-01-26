import * as vscode from 'vscode';
import { AgentService, ChatMessage } from '../services/AgentService';
import { ConfigService } from '../services/ConfigService';

export class ChatPanel {
  public static readonly viewType = 'ai-agent.chatPanel';
  private panel: vscode.WebviewPanel;
  private agentService: AgentService;
  private configService: ConfigService;
  private extensionUri: vscode.Uri;
  private onDisposeCallback?: () => void;

  constructor(
    extensionUri: vscode.Uri,
    agentService: AgentService,
    configService: ConfigService,
    onDispose?: () => void
  ) {
    this.extensionUri = extensionUri;
    this.agentService = agentService;
    this.configService = configService;
    this.onDisposeCallback = onDispose;

    // Create webview panel
    this.panel = vscode.window.createWebviewPanel(
      ChatPanel.viewType,
      'AI Agent Chat',
      vscode.ViewColumn.One,
      this.getWebviewOptions(extensionUri)
    );

    this.panel.webview.html = this.getHtmlForWebview(this.panel.webview);

    // Handle messages from webview
    this.panel.webview.onDidReceiveMessage(
      (message) => this.handleMessage(message),
      undefined
    );

    // Handle panel disposal
    this.panel.onDidDispose(() => {
      this.dispose();
      if (this.onDisposeCallback) {
        this.onDisposeCallback();
      }
    }, undefined);

    // Handle panel becoming visible - refresh config
    this.panel.onDidChangeViewState(() => {
      if (this.panel.visible) {
        this.refreshConfig();
      }
    }, undefined);

    // Initialize session
    this.initializeSession();
  }

  /**
   * Show the panel
   */
  public show(): void {
    this.panel.reveal(vscode.ViewColumn.One);
  }

  /**
   * Dispose the panel
   */
  public dispose(): void {
    this.panel.dispose();
  }

  /**
   * Initialize chat session
   */
  private async initializeSession(): Promise<void> {
    try {
      const session = await this.agentService.startSession();
      this.panel.webview.postMessage({
        type: 'sessionStarted',
        sessionId: session.id,
        config: session.config,
      });
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to start session: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Handle messages from webview
   */
  private async handleMessage(message: unknown): Promise<void> {
    const msg = message as { command: string; content?: string };

    switch (msg.command) {
      case 'sendMessage':
        await this.handleSendMessage(msg.content || '');
        break;
      case 'resetSession':
        await this.handleResetSession();
        break;
      case 'getConfig':
        this.handleGetConfig();
        break;
    }
  }

  /**
   * Handle send message command
   */
  private async handleSendMessage(userMessage: string): Promise<void> {
    if (!userMessage.trim()) {
      return;
    }

    try {
      // Send user message to webview immediately
      this.panel.webview.postMessage({
        type: 'messageReceived',
        message: {
          role: 'user',
          content: userMessage,
          timestamp: Date.now(),
        },
      });

      // Get response from agent
      const response = await this.agentService.sendMessage(userMessage);

      // Send assistant response to webview
      this.panel.webview.postMessage({
        type: 'messageReceived',
        message: {
          role: 'assistant',
          content: response,
          timestamp: Date.now(),
        },
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      this.panel.webview.postMessage({
        type: 'error',
        message: `Failed to get response: ${errorMsg}`,
      });

      vscode.window.showErrorMessage(`Agent error: ${errorMsg}`);
    }
  }

  /**
   * Handle reset session command
   */
  private async handleResetSession(): Promise<void> {
    // Show confirmation dialog in VSCode (not in webview)
    const response = await vscode.window.showWarningMessage(
      'Are you sure you want to reset the conversation? This will clear all messages.',
      { modal: true },
      'Yes',
      'No'
    );

    if (response !== 'Yes') {
      return;
    }

    try {
      await this.agentService.resetSession();
      await this.initializeSession();
      this.panel.webview.postMessage({
        type: 'sessionReset',
      });
      vscode.window.showInformationMessage('Conversation reset successfully');
    } catch (error) {
      vscode.window.showErrorMessage(
        `Failed to reset session: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  }

  /**
   * Public method to send a message (used by external commands)
   */
  public async sendMessage(message: string): Promise<void> {
    await this.handleSendMessage(message);
  }

  /**
   * Handle get config command
   */
  private handleGetConfig(): void {
    const config = this.configService.getConfig();
    this.panel.webview.postMessage({
      type: 'configData',
      config,
    });
  }

  /**
   * Refresh config in webview (called when panel becomes visible or config changes)
   */
  public refreshConfig(): void {
    const config = this.configService.getConfig();
    this.panel.webview.postMessage({
      type: 'configUpdated',
      config,
    });
  }

  /**
   * Get webview options
   */
  private getWebviewOptions(extensionUri: vscode.Uri): vscode.WebviewPanelOptions & vscode.WebviewOptions {
    return {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'webview')],
    };
  }

  /**
   * Get HTML for webview
   */
  private getHtmlForWebview(webview: vscode.Webview): string {
    return '<!DOCTYPE html>' +
'<html lang="en">' +
'<head>' +
'    <meta charset="UTF-8">' +
'    <meta name="viewport" content="width=device-width, initial-scale=1.0">' +
'    <title>AI Agent Chat</title>' +
'    <style>' +
'        * { margin: 0; padding: 0; box-sizing: border-box; }' +
'        body {' +
'            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;' +
'            background-color: var(--vscode-editor-background);' +
'            color: var(--vscode-editor-foreground);' +
'            height: 100vh;' +
'            display: flex;' +
'            flex-direction: column;' +
'        }' +
'        .container { display: flex; flex-direction: column; height: 100%; padding: 16px; }' +
'        .messages { flex: 1; overflow-y: auto; margin-bottom: 16px; border: 1px solid var(--vscode-input-border); border-radius: 4px; padding: 12px; }' +
'        .message { margin-bottom: 12px; padding: 8px; border-radius: 4px; max-width: 85%; }' +
'        .message.user { background-color: var(--vscode-button-background); color: var(--vscode-button-foreground); margin-left: auto; margin-right: 0; }' +
'        .message.assistant { background-color: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }' +
'        .timestamp { font-size: 0.75em; opacity: 0.7; margin-top: 4px; }' +
'        .input-area { display: flex; gap: 8px; }' +
'        input[type="text"] { flex: 1; padding: 8px 12px; border: 1px solid var(--vscode-input-border); border-radius: 4px; background-color: var(--vscode-input-background); color: var(--vscode-input-foreground); font-family: inherit; }' +
'        input[type="text"]:focus { outline: none; border-color: var(--vscode-focusBorder); }' +
'        button { padding: 8px 16px; background-color: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; font-family: inherit; }' +
'        button:hover { background-color: var(--vscode-button-hoverBackground); }' +
'        .reset-btn { padding: 4px 12px; font-size: 0.85em; }' +
'        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--vscode-input-border); }' +
'        .header h2 { font-size: 1em; margin: 0; }' +
'        .config-info { font-size: 0.75em; opacity: 0.8; }' +
'        .error { color: var(--vscode-errorForeground); background-color: var(--vscode-inputValidation-errorBackground); padding: 8px; border-radius: 4px; margin-bottom: 12px; display: none; }' +
'        .success { color: var(--vscode-testing-iconPassed); background-color: var(--vscode-inputValidation-infoBackground); padding: 8px; border-radius: 4px; margin-bottom: 12px; display: none; }' +
'    </style>' +
'</head>' +
'<body>' +
'    <div class="container">' +
'        <div class="header">' +
'            <div>' +
'                <h2>AI Agent Chat</h2>' +
'                <div class="config-info" id="configInfo">Provider: Loading...</div>' +
'            </div>' +
'            <button class="reset-btn" onclick="resetSession()">Reset</button>' +
'        </div>' +
'        <div id="success" class="success"></div>' +
'        <div id="error" class="error"></div>' +
'        <div class="messages" id="messages"></div>' +
'        <div class="input-area">' +
'            <input type="text" id="messageInput" placeholder="Type a message..." onkeypress="handleKeyPress(event)">' +
'            <button onclick="sendMessage()">Send</button>' +
'        </div>' +
'    </div>' +
'    <script>' +
'        const vscode = acquireVsCodeApi();' +
'        function sendMessage() {' +
'            const input = document.getElementById("messageInput");' +
'            const message = input.value.trim();' +
'            if (!message) return;' +
'            vscode.postMessage({ command: "sendMessage", content: message });' +
'            input.value = "";' +
'            input.focus();' +
'        }' +
'        function handleKeyPress(event) {' +
'            if (event.key === "Enter" && !event.shiftKey) {' +
'                event.preventDefault();' +
'                sendMessage();' +
'            }' +
'        }' +
'        function resetSession() {' +
'            vscode.postMessage({ command: "resetSession" });' +
'        }' +
'        function displayMessage(message) {' +
'            const messagesDiv = document.getElementById("messages");' +
'            const messageEl = document.createElement("div");' +
'            messageEl.className = "message " + message.role;' +
'            const timestamp = new Date(message.timestamp).toLocaleTimeString();' +
'            messageEl.innerHTML = "<div>" + escapeHtml(message.content) + "</div><div class=\\"timestamp\\">" + timestamp + "</div>";' +
'            messagesDiv.appendChild(messageEl);' +
'            messagesDiv.scrollTop = messagesDiv.scrollHeight;' +
'        }' +
'        function escapeHtml(text) {' +
'            const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\"": "&quot;", "\'": "&#039;" };' +
'            return text.replace(/[&<>"\']/g, function(m) { return map[m]; });' +
'        }' +
'        function showError(message) {' +
'            const errorDiv = document.getElementById("error");' +
'            errorDiv.textContent = message;' +
'            errorDiv.style.display = "block";' +
'            setTimeout(function() { errorDiv.style.display = "none"; }, 5000);' +
'        }' +
'        function showSuccess(message) {' +
'            const successDiv = document.getElementById("success");' +
'            successDiv.textContent = message;' +
'            successDiv.style.display = "block";' +
'            setTimeout(function() { successDiv.style.display = "none"; }, 3000);' +
'        }' +
'        function updateConfigDisplay(config) {' +
'            const configInfo = document.getElementById("configInfo");' +
'            if (config) {' +
'                configInfo.textContent = "Provider: " + config.provider + " | Model: " + config.model;' +
'            }' +
'        }' +
'        window.addEventListener("message", function(event) {' +
'            const message = event.data;' +
'            switch (message.type) {' +
'                case "messageReceived": displayMessage(message.message); break;' +
'                case "sessionStarted":' +
'                    console.log("Session started:", message.sessionId);' +
'                    updateConfigDisplay(message.config);' +
'                    break;' +
'                case "sessionReset":' +
'                    document.getElementById("messages").innerHTML = "";' +
'                    showSuccess("Session reset successfully");' +
'                    break;' +
'                case "error": showError(message.message); break;' +
'                case "configData":' +
'                    console.log("Config:", message.config);' +
'                    updateConfigDisplay(message.config);' +
'                    break;' +
'                case "configUpdated":' +
'                    console.log("Config updated:", message.config);' +
'                    updateConfigDisplay(message.config);' +
'                    showSuccess("Settings updated: " + message.config.provider + " / " + message.config.model);' +
'                    break;' +
'            }' +
'        });' +
'        document.getElementById("messageInput").focus();' +
'    </script>' +
'</body>' +
'</html>';
  }
}
