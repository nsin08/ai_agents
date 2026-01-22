import * as vscode from 'vscode';
import { ConfigService } from '../services/ConfigService';

export class ConfigPanel {
  public static readonly viewType = 'ai-agent.configPanel';
  private panel: vscode.WebviewPanel;
  private configService: ConfigService;
  private extensionUri: vscode.Uri;

  constructor(extensionUri: vscode.Uri, configService: ConfigService) {
    this.extensionUri = extensionUri;
    this.configService = configService;

    // Create webview panel
    this.panel = vscode.window.createWebviewPanel(
      ConfigPanel.viewType,
      'AI Agent Configuration',
      vscode.ViewColumn.One,
      this.getWebviewOptions(extensionUri)
    );

    this.panel.webview.html = this.getHtmlForWebview(this.panel.webview);

    // Handle messages from webview
    this.panel.webview.onDidReceiveMessage(
      (message) => this.handleMessage(message),
      undefined
    );

    // Load and display current config
    this.loadConfiguration();
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
   * Load and display current configuration
   */
  private loadConfiguration(): void {
    const config = this.configService.getConfig();
    const providers = this.configService.getAvailableProviders();

    this.panel.webview.postMessage({
      type: 'configLoaded',
      config,
      providers,
    });
  }

  /**
   * Handle messages from webview
   */
  private async handleMessage(message: unknown): Promise<void> {
    const msg = message as { command: string; key?: string; value?: unknown };

    switch (msg.command) {
      case 'updateSetting':
        if (msg.key && msg.value !== undefined) {
          await this.configService.updateSetting(
            msg.key as keyof any,
            msg.value
          );
          vscode.window.showInformationMessage(
            \`Setting updated: \${msg.key}\`
          );
        }
        break;
      case 'refreshConfig':
        this.loadConfiguration();
        break;
    }
  }

  /**
   * Get webview options
   */
  private getWebviewOptions(
    extensionUri: vscode.Uri
  ): vscode.WebviewPanelOptions & vscode.WebviewOptions {
    return {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'webview')],
    };
  }

  /**
   * Get HTML for webview
   */
  private getHtmlForWebview(webview: vscode.Webview): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Configuration</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            padding: 20px;
        }

        .container {
            max-width: 600px;
        }

        h1 {
            font-size: 1.5em;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--vscode-input-border);
            padding-bottom: 10px;
        }

        .setting-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 6px;
            font-weight: 500;
        }

        label .description {
            font-size: 0.85em;
            opacity: 0.7;
            font-weight: normal;
            display: block;
            margin-top: 2px;
        }

        input[type="text"],
        input[type="number"],
        select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            font-family: inherit;
            font-size: 1em;
        }

        input[type="text"]:focus,
        input[type="number"]:focus,
        select:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        button {
            padding: 8px 16px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-family: inherit;
            margin-right: 8px;
        }

        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }

        .button-group {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--vscode-input-border);
        }

        .status {
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 12px;
            display: none;
        }

        .status.success {
            background-color: var(--vscode-inputValidation-successBackground);
            border: 1px solid var(--vscode-inputValidation-successBorder);
            display: block;
        }

        .status.error {
            background-color: var(--vscode-inputValidation-errorBackground);
            color: var(--vscode-errorForeground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            display: block;
        }

        .help-text {
            font-size: 0.85em;
            opacity: 0.7;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Agent Configuration</h1>

        <div id="status" class="status"></div>

        <div class="setting-group">
            <label>
                Provider
                <span class="description">LLM provider to use</span>
            </label>
            <select id="provider">
                <option value="mock">Mock (Testing)</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="google">Google</option>
                <option value="azure-openai">Azure OpenAI</option>
            </select>
            <div class="help-text">Choose the LLM provider. Mock is great for testing.</div>
        </div>

        <div class="setting-group">
            <label>
                Model
                <span class="description">Model name for the selected provider</span>
            </label>
            <input 
                type="text" 
                id="model" 
                placeholder="e.g., llama2, gpt-4, claude-3-opus"
            >
            <div class="help-text">Specific model name varies by provider.</div>
        </div>

        <div class="setting-group">
            <label>
                Base URL
                <span class="description">Ollama endpoint (ignored for cloud providers)</span>
            </label>
            <input 
                type="text" 
                id="baseUrl" 
                placeholder="http://localhost:11434"
            >
            <div class="help-text">Only used with Ollama provider. Default is local Ollama.</div>
        </div>

        <div class="setting-group">
            <label>
                API Key
                <span class="description">API key for cloud providers</span>
            </label>
            <input 
                type="text" 
                id="apiKey" 
                placeholder="Your API key (stored in VSCode settings)"
                type="password"
            >
            <div class="help-text">Required for OpenAI, Anthropic, etc. Leave blank for Ollama/Mock.</div>
        </div>

        <div class="setting-group">
            <label>
                Max Turns
                <span class="description">Maximum conversation turns</span>
            </label>
            <input 
                type="number" 
                id="maxTurns" 
                min="1" 
                max="100" 
                value="5"
            >
            <div class="help-text">Limits conversation length to prevent excessive API calls.</div>
        </div>

        <div class="setting-group">
            <label>
                Timeout (seconds)
                <span class="description">Request timeout in seconds</span>
            </label>
            <input 
                type="number" 
                id="timeout" 
                min="1" 
                max="300" 
                value="30"
            >
            <div class="help-text">How long to wait for a response before timing out.</div>
        </div>

        <div class="button-group">
            <button onclick="saveSettings()">Save Settings</button>
            <button onclick="resetSettings()" style="background-color: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground);">Reset to Defaults</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function saveSettings() {
            const provider = document.getElementById('provider').value;
            const model = document.getElementById('model').value;
            const baseUrl = document.getElementById('baseUrl').value;
            const apiKey = document.getElementById('apiKey').value;
            const maxTurns = parseInt(document.getElementById('maxTurns').value, 10);
            const timeout = parseInt(document.getElementById('timeout').value, 10);

            // Validate inputs
            if (!model.trim()) {
                showStatus('Model cannot be empty', 'error');
                return;
            }

            // Save each setting
            vscode.postMessage({ command: 'updateSetting', key: 'provider', value: provider });
            vscode.postMessage({ command: 'updateSetting', key: 'model', value: model });
            vscode.postMessage({ command: 'updateSetting', key: 'baseUrl', value: baseUrl });
            vscode.postMessage({ command: 'updateSetting', key: 'apiKey', value: apiKey });
            vscode.postMessage({ command: 'updateSetting', key: 'maxTurns', value: maxTurns });
            vscode.postMessage({ command: 'updateSetting', key: 'timeout', value: timeout });

            showStatus('Settings saved successfully', 'success');
        }

        function resetSettings() {
            if (confirm('Are you sure you want to reset to default settings?')) {
                vscode.postMessage({ command: 'updateSetting', key: 'provider', value: 'mock' });
                vscode.postMessage({ command: 'updateSetting', key: 'model', value: 'llama2' });
                vscode.postMessage({ command: 'updateSetting', key: 'baseUrl', value: 'http://localhost:11434' });
                vscode.postMessage({ command: 'updateSetting', key: 'maxTurns', value: 5 });
                vscode.postMessage({ command: 'updateSetting', key: 'timeout', value: 30 });

                vscode.postMessage({ command: 'refreshConfig' });
                showStatus('Settings reset to defaults', 'success');
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = \`status \${type}\`;

            if (type === 'success') {
                setTimeout(() => {
                    statusDiv.className = 'status';
                }, 3000);
            }
        }

        // Handle messages from extension
        window.addEventListener('message', (event) => {
            const message = event.data;

            if (message.type === 'configLoaded') {
                document.getElementById('provider').value = message.config.provider;
                document.getElementById('model').value = message.config.model;
                document.getElementById('baseUrl').value = message.config.baseUrl;
                document.getElementById('apiKey').value = message.config.apiKey;
                document.getElementById('maxTurns').value = message.config.maxTurns;
                document.getElementById('timeout').value = message.config.timeout;
            }
        });
    </script>
</body>
</html>`;
  }
}
