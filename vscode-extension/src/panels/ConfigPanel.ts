import * as vscode from 'vscode';
import axios from 'axios';
import { ConfigService } from '../services/ConfigService';

export class ConfigPanel {
  public static readonly viewType = 'ai-agent.configPanel';
  private panel: vscode.WebviewPanel;
  private configService: ConfigService;
  private extensionUri: vscode.Uri;
  private onDisposeCallback?: () => void;

  constructor(extensionUri: vscode.Uri, configService: ConfigService, onDispose?: () => void) {
    this.extensionUri = extensionUri;
    this.configService = configService;
    this.onDisposeCallback = onDispose;

    // Create webview panel
    this.panel = vscode.window.createWebviewPanel(
      ConfigPanel.viewType,
      'Agent Settings',
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
    const msg = message as { command: string; key?: string; value?: unknown; settings?: any };

    switch (msg.command) {
      case 'updateSettings':
        // Batch update all settings at once
        if (msg.settings) {
          await this.configService.updateSettings(msg.settings);
          vscode.window.showInformationMessage(
            `Settings saved: ${msg.settings.provider} / ${msg.settings.model}`
          );
          // Reload the configuration in the panel to confirm
          this.loadConfiguration();
        }
        break;
      case 'updateSetting':
        // Legacy single setting update (kept for compatibility)
        if (msg.key && msg.value !== undefined) {
          const validKeys = ['provider', 'model', 'baseUrl', 'apiKey', 'maxTurns', 'timeout'];
          if (validKeys.includes(msg.key)) {
            await this.configService.updateSetting(
              msg.key as 'provider' | 'model' | 'baseUrl' | 'apiKey' | 'maxTurns' | 'timeout',
              msg.value
            );
            vscode.window.showInformationMessage(
              'Setting updated: ' + msg.key
            );
          }
        }
        break;
      case 'refreshConfig':
        this.loadConfiguration();
        break;
      case 'fetchOllamaModels':
        await this.fetchOllamaModels();
        break;
    }
  }

  /**
   * Fetch available Ollama models from the local Ollama instance
   */
  private async fetchOllamaModels(): Promise<void> {
    try {
      const config = this.configService.getConfig();
      const baseUrl = config.baseUrl || 'http://localhost:11434';
      
      const response = await axios.get(`${baseUrl}/api/tags`, {
        timeout: 5000,
      });

      const models = response.data.models?.map((m: any) => m.name) || [];
      
      this.panel.webview.postMessage({
        type: 'ollamaModels',
        models,
      });
    } catch (error) {
      console.error('Failed to fetch Ollama models:', error);
      this.panel.webview.postMessage({
        type: 'ollamaModels',
        models: [],
        error: 'Failed to connect to Ollama. Make sure Ollama is running.',
      });
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
    return '<!DOCTYPE html>' +
'<html lang="en">' +
'<head>' +
'    <meta charset="UTF-8">' +
'    <meta name="viewport" content="width=device-width, initial-scale=1.0">' +
'    <title>Agent Settings</title>' +
'    <style>' +
'        * { margin: 0; padding: 0; box-sizing: border-box; }' +
'        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: var(--vscode-editor-background); color: var(--vscode-editor-foreground); padding: 20px; }' +
'        .container { max-width: 600px; }' +
'        h1 { font-size: 1.5em; margin-bottom: 20px; border-bottom: 1px solid var(--vscode-input-border); padding-bottom: 10px; }' +
'        .setting-group { margin-bottom: 20px; }' +
'        label { display: block; margin-bottom: 6px; font-weight: 500; }' +
'        label .description { font-size: 0.85em; opacity: 0.7; font-weight: normal; display: block; margin-top: 2px; }' +
'        input[type="text"], input[type="number"], select { width: 100%; padding: 8px 12px; border: 1px solid var(--vscode-input-border); border-radius: 4px; background-color: var(--vscode-input-background); color: var(--vscode-input-foreground); font-family: inherit; font-size: 1em; }' +
'        input:focus, select:focus { outline: none; border-color: var(--vscode-focusBorder); }' +
'        button { padding: 8px 16px; background-color: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; font-family: inherit; margin-right: 8px; }' +
'        button:hover { background-color: var(--vscode-button-hoverBackground); }' +
'        .button-group { margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--vscode-input-border); }' +
'        .status { padding: 8px; border-radius: 4px; margin-bottom: 12px; display: none; }' +
'        .status.success { background-color: var(--vscode-inputValidation-successBackground); border: 1px solid var(--vscode-inputValidation-successBorder); display: block; }' +
'        .status.error { background-color: var(--vscode-inputValidation-errorBackground); color: var(--vscode-errorForeground); border: 1px solid var(--vscode-inputValidation-errorBorder); display: block; }' +
'        .help-text { font-size: 0.85em; opacity: 0.7; margin-top: 4px; }' +
'    </style>' +
'</head>' +
'<body>' +
'    <div class="container">' +
'        <h1>Agent Settings</h1>' +
'        <div id="status" class="status"></div>' +
'        <div class="setting-group">' +
'            <label>Provider<span class="description">LLM provider to use</span></label>' +
'            <select id="provider">' +
'                <option value="mock">Mock (Testing)</option>' +
'                <option value="ollama">Ollama (Local)</option>' +
'                <option value="openai">OpenAI</option>' +
'                <option value="anthropic">Anthropic</option>' +
'                <option value="google">Google</option>' +
'                <option value="azure-openai">Azure OpenAI</option>' +
'            </select>' +
'            <div class="help-text">Choose the LLM provider. Mock is great for testing.</div>' +
'        </div>' +
'        <div class="setting-group">' +
'            <label>Model<span class="description">Model name for the selected provider</span></label>' +
'            <div id="model-container">' +
'                <input type="text" id="model" placeholder="e.g., llama2, gpt-4, claude-3-opus">' +
'            </div>' +
'            <div class="help-text">Specific model name varies by provider.</div>' +
'        </div>' +
'        <div class="setting-group">' +
'            <label>Base URL<span class="description">Ollama endpoint (ignored for cloud providers)</span></label>' +
'            <input type="text" id="baseUrl" placeholder="http://localhost:11434">' +
'            <div class="help-text">Only used with Ollama provider. Default is local Ollama.</div>' +
'        </div>' +
'        <div class="setting-group">' +
'            <label>API Key<span class="description">API key for cloud providers</span></label>' +
'            <input type="password" id="apiKey" placeholder="Your API key (stored in VSCode settings)">' +
'            <div class="help-text">Required for OpenAI, Anthropic, etc. Leave blank for Ollama or Mock.</div>' +
'        </div>' +
'        <div class="setting-group">' +
'            <label>Max Turns<span class="description">Maximum conversation turns</span></label>' +
'            <input type="number" id="maxTurns" min="1" max="100" value="5">' +
'            <div class="help-text">Limits conversation length to prevent excessive API calls.</div>' +
'        </div>' +
'        <div class="setting-group">' +
'            <label>Timeout (seconds)<span class="description">Request timeout in seconds</span></label>' +
'            <input type="number" id="timeout" min="1" max="300" value="30">' +
'            <div class="help-text">How long to wait for a response before timing out.</div>' +
'        </div>' +
'        <div class="button-group">' +
'            <button onclick="saveSettings()">Save Settings</button>' +
'            <button onclick="resetSettings()" style="background-color: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground);">Reset to Defaults</button>' +
'        </div>' +
'    </div>' +
'    <script>' +
'        const vscode = acquireVsCodeApi();' +
'        let currentProvider = "";' +
'        function saveSettings() {' +
'            const provider = document.getElementById("provider").value;' +
'            const modelElement = document.getElementById("model");' +
'            const model = modelElement.tagName === "SELECT" ? modelElement.value : modelElement.value;' +
'            const baseUrl = document.getElementById("baseUrl").value;' +
'            const apiKey = document.getElementById("apiKey").value;' +
'            const maxTurns = parseInt(document.getElementById("maxTurns").value, 10);' +
'            const timeout = parseInt(document.getElementById("timeout").value, 10);' +
'            if (!model.trim()) { showStatus("Model cannot be empty", "error"); return; }' +
'            // Send all settings in one batch to prevent race conditions' +
'            vscode.postMessage({' +
'                command: "updateSettings",' +
'                settings: {' +
'                    provider: provider,' +
'                    model: model,' +
'                    baseUrl: baseUrl,' +
'                    apiKey: apiKey,' +
'                    maxTurns: maxTurns,' +
'                    timeout: timeout' +
'                }' +
'            });' +
'            showStatus("Settings saved successfully", "success");' +
'        }' +
'        function onProviderChange() {' +
'            const provider = document.getElementById("provider").value;' +
'            const baseUrlInput = document.getElementById("baseUrl");' +
'            const apiKeyInput = document.getElementById("apiKey");' +
'            if (provider === "mock") {' +
'                baseUrlInput.disabled = true;' +
'                apiKeyInput.disabled = true;' +
'                baseUrlInput.style.opacity = "0.5";' +
'                apiKeyInput.style.opacity = "0.5";' +
'                switchToTextInput();' +
'                const modelInput = document.getElementById("model");' +
'                modelInput.disabled = true;' +
'                modelInput.style.opacity = "0.5";' +
'            } else if (provider === "ollama") {' +
'                baseUrlInput.disabled = false;' +
'                apiKeyInput.disabled = true;' +
'                baseUrlInput.style.opacity = "1";' +
'                apiKeyInput.style.opacity = "0.5";' +
'                if (provider !== currentProvider) {' +
'                    currentProvider = provider;' +
'                    vscode.postMessage({ command: "fetchOllamaModels" });' +
'                    showStatus("Fetching available Ollama models...", "success");' +
'                }' +
'            } else {' +
'                baseUrlInput.disabled = true;' +
'                apiKeyInput.disabled = false;' +
'                baseUrlInput.style.opacity = "0.5";' +
'                apiKeyInput.style.opacity = "1";' +
'                if (currentProvider === "ollama") {' +
'                    switchToTextInput();' +
'                }' +
'                const modelInput = document.getElementById("model");' +
'                if (modelInput) {' +
'                    modelInput.disabled = false;' +
'                    modelInput.style.opacity = "1";' +
'                }' +
'            }' +
'            currentProvider = provider;' +
'        }' +
'        function switchToTextInput() {' +
'            const container = document.getElementById("model-container");' +
'            const currentValue = document.getElementById("model").value || "";' +
'            container.innerHTML = \'<input type="text" id="model" placeholder="e.g., gpt-4, claude-3-opus">\';' +
'            document.getElementById("model").value = currentValue;' +
'        }' +
'        function switchToDropdown(models, currentModel) {' +
'            const container = document.getElementById("model-container");' +
'            let html = \'<select id="model">\';' +
'            if (models.length === 0) {' +
'                html += \'<option value="">No models found</option>\';' +
'            } else {' +
'                models.forEach(function(model) {' +
'                    const selected = model === currentModel ? \' selected\' : \'\';' +
'                    html += \'<option value="\' + model + \'"\' + selected + \'>\' + model + \'</option>\';' +
'                });' +
'            }' +
'            html += \'</select>\';' +
'            container.innerHTML = html;' +
'        }' +
'        document.getElementById("provider").addEventListener("change", onProviderChange);' +
'        function resetSettings() {' +
'            if (confirm("Are you sure you want to reset to default settings?")) {' +
'                // Send all default settings in one batch' +
'                vscode.postMessage({' +
'                    command: "updateSettings",' +
'                    settings: {' +
'                        provider: "mock",' +
'                        model: "llama2",' +
'                        baseUrl: "http://localhost:11434",' +
'                        apiKey: "",' +
'                        maxTurns: 5,' +
'                        timeout: 30' +
'                    }' +
'                });' +
'                // Request config reload to update UI' +
'                setTimeout(function() {' +
'                    vscode.postMessage({ command: "refreshConfig" });' +
'                }, 100);' +
'                showStatus("Settings reset to defaults", "success");' +
'            }' +
'        }' +
'        function showStatus(message, type) {' +
'            const statusDiv = document.getElementById("status");' +
'            statusDiv.textContent = message;' +
'            statusDiv.className = "status " + type;' +
'            if (type === "success") { setTimeout(function() { statusDiv.className = "status"; }, 3000); }' +
'        }' +
'        window.addEventListener("message", function(event) {' +
'            const message = event.data;' +
'            if (message.type === "configLoaded") {' +
'                currentProvider = message.config.provider;' +
'                document.getElementById("provider").value = message.config.provider;' +
'                document.getElementById("baseUrl").value = message.config.baseUrl;' +
'                document.getElementById("apiKey").value = message.config.apiKey;' +
'                document.getElementById("maxTurns").value = message.config.maxTurns;' +
'                document.getElementById("timeout").value = message.config.timeout;' +
'                if (message.config.provider === "ollama") {' +
'                    vscode.postMessage({ command: "fetchOllamaModels" });' +
'                } else {' +
'                    document.getElementById("model").value = message.config.model;' +
'                }' +
'                onProviderChange();' +
'            } else if (message.type === "ollamaModels") {' +
'                if (message.error) {' +
'                    showStatus(message.error, "error");' +
'                    switchToTextInput();' +
'                } else if (message.models && message.models.length > 0) {' +
'                    const modelInput = document.getElementById("model");' +
'                    const currentModel = modelInput ? modelInput.value : message.models[0];' +
'                    switchToDropdown(message.models, currentModel);' +
'                    showStatus("Loaded " + message.models.length + " Ollama models", "success");' +
'                } else {' +
'                    showStatus("No Ollama models found. Pull a model with: ollama pull llama2", "error");' +
'                    switchToTextInput();' +
'                }' +
'            }' +
'        });' +
'    </script>' +
'</body>' +
'</html>';
  }
}
