import * as vscode from 'vscode';
import axios from 'axios';
import { AgentConfigurationService } from '../services/AgentConfigurationService';
import type {
  SingleAgentConfig,
  MultiAgentConfig,
  StageConfig,
  AgentConfiguration
} from '../models/AgentRole';

/**
 * Unified settings panel for single-agent and multi-agent configuration.
 * 
 * Features:
 * - Toggle between single-agent and multi-agent modes
 * - Single-agent: One config section with provider/model/settings
 * - Multi-agent: Two config sections (Plan stage + Act stage)
 * - Dynamic form based on selected mode
 * - Validation and error handling
 */
export class SettingsPanel {
  public static readonly viewType = 'ai-agent.settingsPanel';
  private panel: vscode.WebviewPanel;
  private configService: AgentConfigurationService;
  private extensionUri: vscode.Uri;
  private onDisposeCallback?: () => void;

  constructor(
    extensionUri: vscode.Uri,
    configService: AgentConfigurationService,
    onDispose?: () => void
  ) {
    this.extensionUri = extensionUri;
    this.configService = configService;
    this.onDisposeCallback = onDispose;

    // Create webview panel
    this.panel = vscode.window.createWebviewPanel(
      SettingsPanel.viewType,
      'Agent Configuration',
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

    // Listen for configuration changes
    this.configService.onConfigurationChange((config) => {
      this.loadConfiguration(config);
    });

    // Load and display current config
    this.loadConfiguration(this.configService.getConfig());
  }

  public show(): void {
    this.panel.reveal(vscode.ViewColumn.One);
  }

  public dispose(): void {
    this.panel.dispose();
  }

  private loadConfiguration(config: AgentConfiguration): void {
    const providers = this.configService.getAvailableProviders();

    this.panel.webview.postMessage({
      type: 'configLoaded',
      config,
      providers,
    });
  }

  private async handleMessage(message: unknown): Promise<void> {
    const msg = message as any;

    switch (msg.command) {
      case 'getConfig':
        const currentConfig = this.configService.getConfig();
        this.loadConfiguration(currentConfig);
        break;

      case 'toggleMode':
        await this.configService.toggleMode(msg.mode);
        vscode.window.showInformationMessage(
          `Switched to ${msg.mode === 'single' ? 'single-agent' : 'multi-agent'} mode`
        );
        // Reload config after mode change
        const updatedConfig = this.configService.getConfig();
        this.loadConfiguration(updatedConfig);
        break;

      case 'updateSingleConfig':
        await this.configService.updateSingleAgentConfig(msg.config);
        vscode.window.showInformationMessage('Single-agent config saved');
        break;

      case 'updatePlanConfig':
        await this.configService.updatePlanConfig(msg.config);
        vscode.window.showInformationMessage('Plan stage config saved');
        break;

      case 'updateActConfig':
        await this.configService.updateActConfig(msg.config);
        vscode.window.showInformationMessage('Act stage config saved');
        break;

      case 'updateDebugMode':
        await this.configService.updateDebugMode(!!msg.enabled);
        vscode.window.showInformationMessage(`Debug mode ${msg.enabled ? 'enabled' : 'disabled'}`);
        // Reload config to sync UI state
        this.loadConfiguration(this.configService.getConfig());
        break;

      case 'fetchOllamaModels':
        await this.fetchOllamaModels(msg.baseUrl, msg.stage);
        break;

      case 'validateConfig':
        const validation = this.configService.validateConfiguration(msg.config);
        this.panel.webview.postMessage({
          type: 'validationResult',
          valid: validation.valid,
          errors: validation.errors
        });
        break;
    }
  }

  private async fetchOllamaModels(baseUrl: string, stage?: string): Promise<void> {
    try {
      const url = baseUrl || 'http://localhost:11434';
      const response = await axios.get(`${url}/api/tags`, {
        timeout: 5000,
      });

      const models = response.data.models?.map((m: any) => m.name) || [];

      this.panel.webview.postMessage({
        type: 'ollamaModels',
        models,
        stage: stage || 'single'
      });
    } catch (error) {
      console.error('Failed to fetch Ollama models:', error);
      this.panel.webview.postMessage({
        type: 'ollamaModels',
        models: [],
        stage: stage || 'single',
        error: 'Failed to connect to Ollama. Make sure Ollama is running.',
      });
    }
  }

  private getWebviewOptions(
    extensionUri: vscode.Uri
  ): vscode.WebviewPanelOptions & vscode.WebviewOptions {
    return {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'webview')],
    };
  }

  private getHtmlForWebview(webview: vscode.Webview): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Configuration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
            background-color: var(--vscode-editor-background); 
            color: var(--vscode-editor-foreground); 
            padding: 20px; 
        }
        .container { max-width: 700px; }
        h1 { font-size: 1.5em; margin-bottom: 10px; border-bottom: 1px solid var(--vscode-input-border); padding-bottom: 10px; }
        .subtitle { font-size: 0.9em; opacity: 0.7; margin-bottom: 20px; }
        
        .mode-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            padding: 15px;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
        }
        
        .mode-button {
            flex: 1;
            padding: 10px;
            border: 2px solid var(--vscode-input-border);
            border-radius: 4px;
            background-color: transparent;
            color: var(--vscode-input-foreground);
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .mode-button:hover { border-color: var(--vscode-focusBorder); }
        .mode-button.active { 
            background-color: var(--vscode-button-background); 
            color: var(--vscode-button-foreground);
            border-color: var(--vscode-button-background);
        }
        
        .config-section {
            margin-bottom: 30px;
            padding: 20px;
            background-color: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            display: none;
        }
        
        .config-section.active { display: block; }
        .config-section.stage { border-left: 4px solid var(--vscode-focusBorder); }
        
        .stage-header {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--vscode-input-border);
        }
        
        .setting-group { margin-bottom: 16px; }
        label { display: block; margin-bottom: 6px; font-weight: 500; }
        label .description { font-size: 0.85em; opacity: 0.7; font-weight: normal; display: block; margin-top: 2px; }
        
        input[type="text"], 
        input[type="number"], 
        input[type="password"],
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
        
        input:focus, select:focus { 
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
            margin-bottom: 8px;
        }
        
        button:hover { background-color: var(--vscode-button-hoverBackground); }
        
        .button-group { 
            margin-top: 20px; 
            padding-top: 15px; 
            border-top: 1px solid var(--vscode-input-border);
        }

        .toggle-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 20px;
            padding: 12px;
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            background: var(--vscode-input-background);
        }

        .toggle-label {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .toggle-label span {
            font-size: 0.85em;
            opacity: 0.7;
        }

        .toggle {
            position: relative;
            width: 42px;
            height: 22px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 999px;
            cursor: pointer;
        }

        .toggle::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            background: var(--vscode-button-background);
            border-radius: 50%;
            transition: transform 0.2s ease;
        }

        .toggle.enabled {
            background: var(--vscode-button-background);
        }

        .toggle.enabled::after {
            transform: translateX(20px);
            background: var(--vscode-button-foreground);
        }
        
        .status { 
            padding: 12px; 
            border-radius: 4px; 
            margin-bottom: 15px; 
            display: none;
            border-left: 4px solid transparent;
        }
        
        .status.success { 
            background-color: var(--vscode-inputValidation-successBackground); 
            border-left-color: #4ec9b0;
            display: block; 
        }
        
        .status.error { 
            background-color: var(--vscode-inputValidation-errorBackground); 
            color: var(--vscode-errorForeground); 
            border-left-color: #f48771;
            display: block; 
        }
        
        .help-text { 
            font-size: 0.85em; 
            opacity: 0.7; 
            margin-top: 4px; 
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        @media (max-width: 600px) {
            .two-column { grid-template-columns: 1fr; }
            .mode-selector { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Agent Configuration</h1>
        <p class="subtitle">Configure single or multi-agent execution mode</p>
        
        <div id="status" class="status"></div>

        <div class="toggle-row">
            <div class="toggle-label">
                <strong>Debug Mode</strong>
                <span>Verbose logging for multi-agent orchestration</span>
            </div>
            <div id="debugToggle" class="toggle" onclick="toggleDebugMode()"></div>
        </div>
        
        <!-- Mode Selector -->
        <div class="mode-selector">
            <button class="mode-button active" onclick="toggleMode('single', event)">
                👤 Single Agent
            </button>
            <button class="mode-button" onclick="toggleMode('multi', event)">
                🤝 Multi-Agent (Plan + Act)
            </button>
        </div>
        
        <!-- Single-Agent Configuration -->
        <div id="single-config" class="config-section active">
            <div class="setting-group">
                <label>Provider
                    <span class="description">LLM provider</span>
                </label>
                <select id="single-provider" onchange="onProviderChange('single')">
                    <option value="mock">Mock (Testing)</option>
                    <option value="ollama">Ollama (Local)</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                    <option value="azure-openai">Azure OpenAI</option>
                </select>
            </div>
            
            <div class="setting-group">
                <label>Model
                    <span class="description">Model name</span>
                </label>
                <div id="single-model-container">
                    <input type="text" id="single-model" placeholder="e.g., llama2, gpt-4">
                </div>
            </div>
            
            <div class="setting-group">
                <label>Base URL
                    <span class="description">Ollama endpoint (local only)</span>
                </label>
                <input type="text" id="single-baseUrl" placeholder="http://localhost:11434">
            </div>
            
            <div class="setting-group">
                <label>API Key
                    <span class="description">For cloud providers</span>
                </label>
                <input type="password" id="single-apiKey" placeholder="Your API key">
            </div>
            
            <div class="two-column">
                <div class="setting-group">
                    <label>Max Turns
                        <span class="description">Conversation turns</span>
                    </label>
                    <input type="number" id="single-maxTurns" min="1" max="100" value="5">
                </div>
                
                <div class="setting-group">
                    <label>Timeout (sec)
                        <span class="description">Request timeout</span>
                    </label>
                    <input type="number" id="single-timeout" min="1" max="300" value="30">
                </div>
            </div>
            
            <div class="setting-group">
                <label>Temperature
                    <span class="description">Response randomness (0-1)</span>
                </label>
                <input type="number" id="single-temperature" min="0" max="1" step="0.1" value="0.7">
            </div>
            
            <div class="button-group">
                <button onclick="saveSingleConfig()">💾 Save Configuration</button>
                <button onclick="resetSingleConfig()" style="background-color: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground);">↺ Reset to Defaults</button>
            </div>
        </div>
        
        <!-- Multi-Agent Configuration -->
        <div id="multi-config" class="config-section">
            <!-- Plan Stage -->
            <div class="stage">
                <div class="stage-header">📋 Plan Stage (Analysis & Decomposition)</div>
                
                <div class="setting-group">
                    <label>Provider
                        <span class="description">LLM provider for planning</span>
                    </label>
                    <select id="plan-provider" onchange="onProviderChange('plan')">
                        <option value="mock">Mock (Testing)</option>
                        <option value="ollama">Ollama (Local)</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="google">Google</option>
                        <option value="azure-openai">Azure OpenAI</option>
                    </select>
                </div>
                
                <div class="setting-group">
                    <label>Model
                        <span class="description">Model name for planning</span>
                    </label>
                    <div id="plan-model-container">
                        <input type="text" id="plan-model" placeholder="e.g., llama2, gpt-4">
                    </div>
                </div>
                
                <div class="setting-group">
                    <label>Base URL
                        <span class="description">Ollama endpoint</span>
                    </label>
                    <input type="text" id="plan-baseUrl" placeholder="http://localhost:11434">
                </div>
                
                <div class="setting-group">
                    <label>API Key
                        <span class="description">For cloud providers</span>
                    </label>
                    <input type="password" id="plan-apiKey" placeholder="Your API key">
                </div>
                
                <div class="two-column">
                    <div class="setting-group">
                        <label>Max Turns
                            <span class="description">Planning turns</span>
                        </label>
                        <input type="number" id="plan-maxTurns" min="1" max="100" value="3">
                    </div>
                    
                    <div class="setting-group">
                        <label>Timeout (sec)
                            <span class="description">Planning timeout</span>
                        </label>
                        <input type="number" id="plan-timeout" min="1" max="300" value="30">
                    </div>
                </div>
                
                <div class="setting-group">
                    <label>Temperature
                        <span class="description">Randomness for planning</span>
                    </label>
                    <input type="number" id="plan-temperature" min="0" max="1" step="0.1" value="0.5">
                </div>
            </div>
            
            <!-- Act Stage -->
            <div class="stage" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--vscode-input-border);">
                <div class="stage-header">⚙️ Act Stage (Implementation & Execution)</div>
                
                <div class="setting-group">
                    <label>Provider
                        <span class="description">LLM provider for execution</span>
                    </label>
                    <select id="act-provider" onchange="onProviderChange('act')">
                        <option value="mock">Mock (Testing)</option>
                        <option value="ollama">Ollama (Local)</option>
                        <option value="openai">OpenAI</option>
                        <option value="anthropic">Anthropic</option>
                        <option value="google">Google</option>
                        <option value="azure-openai">Azure OpenAI</option>
                    </select>
                </div>
                
                <div class="setting-group">
                    <label>Model
                        <span class="description">Model name for execution</span>
                    </label>
                    <div id="act-model-container">
                        <input type="text" id="act-model" placeholder="e.g., llama2, gpt-4">
                    </div>
                </div>
                
                <div class="setting-group">
                    <label>Base URL
                        <span class="description">Ollama endpoint</span>
                    </label>
                    <input type="text" id="act-baseUrl" placeholder="http://localhost:11434">
                </div>
                
                <div class="setting-group">
                    <label>API Key
                        <span class="description">For cloud providers</span>
                    </label>
                    <input type="password" id="act-apiKey" placeholder="Your API key">
                </div>
                
                <div class="two-column">
                    <div class="setting-group">
                        <label>Max Turns
                            <span class="description">Execution turns</span>
                        </label>
                        <input type="number" id="act-maxTurns" min="1" max="100" value="5">
                    </div>
                    
                    <div class="setting-group">
                        <label>Timeout (sec)
                            <span class="description">Execution timeout</span>
                        </label>
                        <input type="number" id="act-timeout" min="1" max="300" value="30">
                    </div>
                </div>
                
                <div class="setting-group">
                    <label>Temperature
                        <span class="description">Randomness for execution</span>
                    </label>
                    <input type="number" id="act-temperature" min="0" max="1" step="0.1" value="0.7">
                </div>
            </div>
            
            <div class="button-group">
                <button onclick="saveMultiConfig()">💾 Save Configuration</button>
                <button onclick="resetMultiConfig()" style="background-color: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground);">↺ Reset to Defaults</button>
            </div>
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        let currentMode = 'single';
        let currentOllamaProviders = {};
        
        // === MODE TOGGLE ===
        function toggleMode(mode, event) {
            if (event) event.preventDefault();
            currentMode = mode;
            vscode.postMessage({ command: 'toggleMode', mode: mode });
            
            // Update UI
            document.querySelectorAll('.mode-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('single-config').classList.toggle('active', mode === 'single');
            document.getElementById('multi-config').classList.toggle('active', mode === 'multi');
        }
        
        // === CONFIGURATION LOADING ===
        window.addEventListener("message", function(event) {
            const message = event.data;
            
            if (message.type === "configLoaded") {
                currentMode = message.config.mode;
                
                // Update mode buttons
                document.querySelectorAll('.mode-button').forEach(btn => btn.classList.remove('active'));
                if (currentMode === 'single') {
                    document.querySelector('.mode-button:nth-child(1)').classList.add('active');
                } else {
                    document.querySelector('.mode-button:nth-child(2)').classList.add('active');
                }
                
                // Toggle config sections
                document.getElementById('single-config').classList.toggle('active', currentMode === 'single');
                document.getElementById('multi-config').classList.toggle('active', currentMode === 'multi');
                
                if (currentMode === 'single') {
                    loadSingleAgentConfig(message.config);
                } else {
                    loadMultiAgentConfig(message.config);
                }

                setDebugToggle(!!message.config.debugMode);
            } else if (message.type === "ollamaModels") {
                handleOllamaModels(message);
            }
        });

        function toggleDebugMode() {
            const toggle = document.getElementById('debugToggle');
            const enabled = !toggle.classList.contains('enabled');
            setDebugToggle(enabled);
            vscode.postMessage({ command: 'updateDebugMode', enabled: enabled });
        }

        function setDebugToggle(enabled) {
            const toggle = document.getElementById('debugToggle');
            toggle.classList.toggle('enabled', enabled);
        }
        
        function loadSingleAgentConfig(config) {
            document.getElementById('single-provider').value = config.provider || 'mock';
            document.getElementById('single-model').value = config.model || 'llama2';
            document.getElementById('single-baseUrl').value = config.baseUrl || 'http://localhost:11434';
            document.getElementById('single-apiKey').value = config.apiKey || '';
            document.getElementById('single-maxTurns').value = config.maxTurns || 5;
            document.getElementById('single-timeout').value = config.timeout || 30;
            document.getElementById('single-temperature').value = config.temperature || 0.7;
            
            onProviderChange('single');
        }
        
        function loadMultiAgentConfig(config) {
            // Plan stage
            document.getElementById('plan-provider').value = config.plan?.provider || 'mock';
            document.getElementById('plan-model').value = config.plan?.model || 'llama2';
            document.getElementById('plan-baseUrl').value = config.plan?.baseUrl || 'http://localhost:11434';
            document.getElementById('plan-apiKey').value = config.plan?.apiKey || '';
            document.getElementById('plan-maxTurns').value = config.plan?.maxTurns || 3;
            document.getElementById('plan-timeout').value = config.plan?.timeout || 30;
            document.getElementById('plan-temperature').value = config.plan?.temperature || 0.5;
            
            // Act stage
            document.getElementById('act-provider').value = config.act?.provider || 'mock';
            document.getElementById('act-model').value = config.act?.model || 'llama2';
            document.getElementById('act-baseUrl').value = config.act?.baseUrl || 'http://localhost:11434';
            document.getElementById('act-apiKey').value = config.act?.apiKey || '';
            document.getElementById('act-maxTurns').value = config.act?.maxTurns || 5;
            document.getElementById('act-timeout').value = config.act?.timeout || 30;
            document.getElementById('act-temperature').value = config.act?.temperature || 0.7;
            
            onProviderChange('plan');
            onProviderChange('act');
        }
        
        // === PROVIDER HANDLING ===
        function onProviderChange(stage) {
            const prefix = stage + '-';
            const provider = document.getElementById(prefix + 'provider').value;
            const baseUrlInput = document.getElementById(prefix + 'baseUrl');
            const apiKeyInput = document.getElementById(prefix + 'apiKey');
            const modelInput = document.getElementById(prefix + 'model');
            
            // Disable/enable fields based on provider
            if (provider === 'mock') {
                baseUrlInput.disabled = true;
                apiKeyInput.disabled = true;
                modelInput.disabled = true;
                baseUrlInput.style.opacity = '0.5';
                apiKeyInput.style.opacity = '0.5';
                modelInput.style.opacity = '0.5';
            } else if (provider === 'ollama') {
                baseUrlInput.disabled = false;
                apiKeyInput.disabled = true;
                modelInput.disabled = false;
                baseUrlInput.style.opacity = '1';
                apiKeyInput.style.opacity = '0.5';
                modelInput.style.opacity = '1';
                
                // Auto-populate baseUrl if empty
                if (!baseUrlInput.value || baseUrlInput.value.trim() === '') {
                    baseUrlInput.value = 'http://localhost:11434';
                }
                
                // Fetch Ollama models
                const baseUrl = baseUrlInput.value || 'http://localhost:11434';
                vscode.postMessage({ command: 'fetchOllamaModels', baseUrl: baseUrl, stage: stage });
                showStatus('Fetching ' + stage + ' Ollama models...', 'success');
            } else {
                baseUrlInput.disabled = true;
                apiKeyInput.disabled = false;
                modelInput.disabled = false;
                baseUrlInput.style.opacity = '0.5';
                apiKeyInput.style.opacity = '1';
                modelInput.style.opacity = '1';
                
                // Switch to text input if coming from Ollama
                if (currentOllamaProviders[stage]) {
                    switchToTextInput(stage);
                    currentOllamaProviders[stage] = false;
                }
            }
        }
        
        function switchToTextInput(stage) {
            const container = document.getElementById(stage + '-model-container');
            const currentValue = document.getElementById(stage + '-model').value || '';
            container.innerHTML = '<input type="text" id="' + stage + '-model" placeholder="e.g., gpt-4, claude-3-opus">';
            document.getElementById(stage + '-model').value = currentValue;
        }
        
        function switchToDropdown(stage, models, currentModel) {
            const container = document.getElementById(stage + '-model-container');
            let html = '<select id="' + stage + '-model">';
            
            if (models.length === 0) {
                html += '<option value="">No models found</option>';
            } else {
                // Use first model as default if current model is not in list or is empty
                const selectedModel = currentModel && models.includes(currentModel) ? currentModel : models[0];
                models.forEach(function(model) {
                    const selected = model === selectedModel ? ' selected' : '';
                    html += '<option value="' + model + '"' + selected + '>' + model + '</option>';
                });
            }
            
            html += '</select>';
            container.innerHTML = html;
            currentOllamaProviders[stage] = true;
        }
        
        function handleOllamaModels(message) {
            if (message.error) {
                showStatus(message.error, 'error');
            } else if (message.models && message.models.length > 0) {
                const stage = message.stage || 'single';
                const modelInput = document.getElementById(stage + '-model');
                const currentModel = modelInput ? modelInput.value : '';
                // Pass empty string so switchToDropdown auto-selects first model
                switchToDropdown(stage, message.models, currentModel);
                showStatus('Loaded ' + message.models.length + ' Ollama models for ' + stage, 'success');
            } else {
                showStatus('No Ollama models found. Pull a model with: ollama pull llama2', 'error');
            }
        }
        
        // === SAVE FUNCTIONS ===
        function saveSingleConfig() {
            const config = {
                provider: document.getElementById('single-provider').value,
                model: document.getElementById('single-model').value,
                baseUrl: document.getElementById('single-baseUrl').value,
                apiKey: document.getElementById('single-apiKey').value,
                maxTurns: parseInt(document.getElementById('single-maxTurns').value, 10),
                timeout: parseInt(document.getElementById('single-timeout').value, 10),
                temperature: parseFloat(document.getElementById('single-temperature').value)
            };
            
            if (!config.model.trim()) {
                showStatus('Model cannot be empty', 'error');
                return;
            }
            
            vscode.postMessage({ command: 'updateSingleConfig', config: config });
            showStatus('Single-agent configuration saved', 'success');
            // Reload config to confirm what was saved
            setTimeout(function() { vscode.postMessage({ command: 'getConfig' }); }, 500);
        }
        
        function saveMultiConfig() {
            const config = {
                plan: {
                    provider: document.getElementById('plan-provider').value,
                    model: document.getElementById('plan-model').value,
                    baseUrl: document.getElementById('plan-baseUrl').value,
                    apiKey: document.getElementById('plan-apiKey').value,
                    maxTurns: parseInt(document.getElementById('plan-maxTurns').value, 10),
                    timeout: parseInt(document.getElementById('plan-timeout').value, 10),
                    temperature: parseFloat(document.getElementById('plan-temperature').value)
                },
                act: {
                    provider: document.getElementById('act-provider').value,
                    model: document.getElementById('act-model').value,
                    baseUrl: document.getElementById('act-baseUrl').value,
                    apiKey: document.getElementById('act-apiKey').value,
                    maxTurns: parseInt(document.getElementById('act-maxTurns').value, 10),
                    timeout: parseInt(document.getElementById('act-timeout').value, 10),
                    temperature: parseFloat(document.getElementById('act-temperature').value)
                }
            };
            
            if (!config.plan.model.trim() || !config.act.model.trim()) {
                showStatus('Plan and Act models cannot be empty', 'error');
                return;
            }
            
            vscode.postMessage({ command: 'updatePlanConfig', config: config.plan });
            vscode.postMessage({ command: 'updateActConfig', config: config.act });
            showStatus('Multi-agent configuration saved', 'success');
            // Reload config to confirm what was saved
            setTimeout(function() { vscode.postMessage({ command: 'getConfig' }); }, 500);
        }
        
        function resetSingleConfig() {
            if (confirm('Reset single-agent configuration to defaults?')) {
                document.getElementById('single-provider').value = 'mock';
                document.getElementById('single-model').value = 'llama2';
                document.getElementById('single-baseUrl').value = 'http://localhost:11434';
                document.getElementById('single-apiKey').value = '';
                document.getElementById('single-maxTurns').value = '5';
                document.getElementById('single-timeout').value = '30';
                document.getElementById('single-temperature').value = '0.7';
                saveSingleConfig();
            }
        }
        
        function resetMultiConfig() {
            if (confirm('Reset multi-agent configuration to defaults?')) {
                // Plan defaults
                document.getElementById('plan-provider').value = 'mock';
                document.getElementById('plan-model').value = 'llama2';
                document.getElementById('plan-baseUrl').value = 'http://localhost:11434';
                document.getElementById('plan-apiKey').value = '';
                document.getElementById('plan-maxTurns').value = '3';
                document.getElementById('plan-timeout').value = '30';
                document.getElementById('plan-temperature').value = '0.5';
                
                // Act defaults
                document.getElementById('act-provider').value = 'mock';
                document.getElementById('act-model').value = 'llama2';
                document.getElementById('act-baseUrl').value = 'http://localhost:11434';
                document.getElementById('act-apiKey').value = '';
                document.getElementById('act-maxTurns').value = '5';
                document.getElementById('act-timeout').value = '30';
                document.getElementById('act-temperature').value = '0.7';
                
                saveMultiConfig();
            }
        }
        
        // === UTILITY FUNCTIONS ===
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = 'status ' + type;
            
            if (type === 'success') {
                setTimeout(function() {
                    statusDiv.className = 'status';
                }, 3000);
            }
        }
        
        // === INITIALIZATION ===
        // Request config from backend when page loads
        vscode.postMessage({ command: 'getConfig' });
    </script>
</body>
</html>`;
  }
}
