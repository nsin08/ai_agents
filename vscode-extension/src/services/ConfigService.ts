import * as vscode from 'vscode';

export interface AgentConfig {
  provider: string;
  model: string;
  baseUrl: string;
  apiKey: string;
  maxTurns: number;
  timeout: number;
}

export class ConfigService {
  private context: vscode.ExtensionContext;
  private config: AgentConfig;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.config = this.loadConfig();
  }

  /**
   * Load configuration from VSCode settings
   */
  private loadConfig(): AgentConfig {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');

    return {
      provider: workspaceConfig.get('provider', 'mock'),
      model: workspaceConfig.get('model', 'llama2'),
      baseUrl: workspaceConfig.get('baseUrl', 'http://localhost:11434'),
      apiKey: workspaceConfig.get('apiKey', ''),
      maxTurns: workspaceConfig.get('maxTurns', 5),
      timeout: workspaceConfig.get('timeout', 30),
    };
  }

  /**
   * Reload configuration from VSCode settings
   */
  public reload(): void {
    this.config = this.loadConfig();
    console.log('Configuration reloaded:', this.config);
  }

  /**
   * Get current configuration
   */
  public getConfig(): AgentConfig {
    return { ...this.config };
  }

  /**
   * Update a single configuration value
   */
  public async updateSetting(key: keyof AgentConfig, value: unknown): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');
    await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Global);
    this.reload();
  }

  /**
   * Get provider
   */
  public getProvider(): string {
    return this.config.provider;
  }

  /**
   * Get model
   */
  public getModel(): string {
    return this.config.model;
  }

  /**
   * Get base URL (for Ollama)
   */
  public getBaseUrl(): string {
    return this.config.baseUrl;
  }

  /**
   * Get API key for cloud providers
   */
  public getApiKey(): string {
    return this.config.apiKey;
  }

  /**
   * Get max turns
   */
  public getMaxTurns(): number {
    return this.config.maxTurns;
  }

  /**
   * Get timeout
   */
  public getTimeout(): number {
    return this.config.timeout;
  }

  /**
   * Save session to global storage
   */
  public async saveSession(sessionId: string, data: unknown): Promise<void> {
    await this.context.globalState.update(`session-${sessionId}`, data);
  }

  /**
   * Load session from global storage
   */
  public async loadSession(sessionId: string): Promise<unknown | undefined> {
    return this.context.globalState.get(`session-${sessionId}`);
  }

  /**
   * Get all available providers
   */
  public getAvailableProviders(): string[] {
    return ['mock', 'ollama', 'openai', 'anthropic', 'google', 'azure-openai'];
  }
}
