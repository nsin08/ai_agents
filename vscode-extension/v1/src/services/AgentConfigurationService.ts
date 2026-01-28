import * as vscode from 'vscode';
import type {
  SingleAgentConfig,
  MultiAgentConfig,
  StageConfig,
  AgentConfiguration
} from '../models/AgentRole';

/**
 * Unified agent configuration service for both single and multi-agent modes.
 * 
 * Single-Agent Mode:
 * - One agent processes entire task
 * - Single provider/model/settings
 * - Simpler, faster execution
 * 
 * Multi-Agent Mode (Plan + Act):
 * - Stage 1: Plan (analysis, decomposition)
 * - Stage 2: Act (implementation, execution)
 * - Independent configs per stage (different models, timeouts, etc.)
 * - Verifier moved to Phase 5
 */
export interface ConfigurationWithDebug extends Record<string, any> {
  debugMode?: boolean;
}

export class AgentConfigurationService {
  private context: vscode.ExtensionContext;
  private currentConfig: AgentConfiguration & ConfigurationWithDebug;
  private onConfigChangeEmitter = new vscode.EventEmitter<AgentConfiguration & ConfigurationWithDebug>();

  public readonly onConfigurationChange = this.onConfigChangeEmitter.event;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.currentConfig = this.loadConfiguration();
    
    // Listen for workspace settings changes
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('aiAgent')) {
        this.currentConfig = this.loadConfiguration();
        this.onConfigChangeEmitter.fire(this.currentConfig);
      }
    });
  }

  /**
   * Load complete configuration from VS Code settings
   */
  private loadConfiguration(): AgentConfiguration & ConfigurationWithDebug {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');
    const mode = workspaceConfig.get<'single' | 'multi'>('mode', 'single');
    const debugMode = workspaceConfig.get<boolean>('debugMode', false);

    if (mode === 'multi') {
      const config = this.loadMultiAgentConfig(workspaceConfig);
      return { ...config, debugMode };
    } else {
      const config = this.loadSingleAgentConfig(workspaceConfig);
      return { ...config, debugMode };
    }
  }

  /**
   * Load single-agent configuration
   */
  private loadSingleAgentConfig(workspaceConfig: vscode.WorkspaceConfiguration): SingleAgentConfig {
    return {
      mode: 'single',
      provider: workspaceConfig.get('provider', 'mock'),
      model: workspaceConfig.get('model', 'llama2'),
      maxTurns: workspaceConfig.get('maxTurns', 5),
      timeout: workspaceConfig.get('timeout', 30),
      temperature: workspaceConfig.get('temperature', 0.7),
      baseUrl: workspaceConfig.get('baseUrl', 'http://localhost:11434'),
      apiKey: workspaceConfig.get('apiKey', '')
    };
  }

  /**
   * Load multi-agent configuration (Plan + Act stages)
   */
  private loadMultiAgentConfig(workspaceConfig: vscode.WorkspaceConfiguration): MultiAgentConfig {
    return {
      mode: 'multi',
      plan: {
        provider: workspaceConfig.get('plan.provider', 'mock'),
        model: workspaceConfig.get('plan.model', 'llama2'),
        maxTurns: workspaceConfig.get('plan.maxTurns', 3),
        timeout: workspaceConfig.get('plan.timeout', 30),
        temperature: workspaceConfig.get('plan.temperature', 0.5),
        baseUrl: workspaceConfig.get('plan.baseUrl', 'http://localhost:11434'),
        apiKey: workspaceConfig.get('plan.apiKey', '')
      },
      act: {
        provider: workspaceConfig.get('act.provider', 'mock'),
        model: workspaceConfig.get('act.model', 'llama2'),
        maxTurns: workspaceConfig.get('act.maxTurns', 5),
        timeout: workspaceConfig.get('act.timeout', 30),
        temperature: workspaceConfig.get('act.temperature', 0.7),
        baseUrl: workspaceConfig.get('act.baseUrl', 'http://localhost:11434'),
        apiKey: workspaceConfig.get('act.apiKey', '')
      }
    };
  }

  /**
   * Get current configuration (includes debug mode)
   */
  public getConfig(): AgentConfiguration & ConfigurationWithDebug {
    const config = this.currentConfig;
    return JSON.parse(JSON.stringify(config));
  }

  /**
   * Get current mode (single or multi)
   */
  public getMode(): 'single' | 'multi' {
    return this.currentConfig.mode;
  }

  /**
   * Toggle between single and multi-agent modes
   */
  public async toggleMode(newMode: 'single' | 'multi'): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');
    await workspaceConfig.update('mode', newMode, vscode.ConfigurationTarget.Workspace);
  }

  /**
   * Update single-agent configuration
   */
  public async updateSingleAgentConfig(config: Partial<SingleAgentConfig>): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');
    const updates: { [key: string]: any } = {};

    if (config.provider !== undefined) updates['provider'] = config.provider;
    if (config.model !== undefined) updates['model'] = config.model;
    if (config.maxTurns !== undefined) updates['maxTurns'] = config.maxTurns;
    if (config.timeout !== undefined) updates['timeout'] = config.timeout;
    if (config.temperature !== undefined) updates['temperature'] = config.temperature;
    if (config.baseUrl !== undefined) updates['baseUrl'] = config.baseUrl;
    if (config.apiKey !== undefined) updates['apiKey'] = config.apiKey;

    for (const [key, value] of Object.entries(updates)) {
      await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Workspace);
    }
  }

  /**
   * Update Plan stage configuration
   */
  public async updatePlanConfig(config: Partial<StageConfig>): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');
    const updates: { [key: string]: any } = {};

    if (config.provider !== undefined) updates['plan.provider'] = config.provider;
    if (config.model !== undefined) updates['plan.model'] = config.model;
    if (config.maxTurns !== undefined) updates['plan.maxTurns'] = config.maxTurns;
    if (config.timeout !== undefined) updates['plan.timeout'] = config.timeout;
    if (config.temperature !== undefined) updates['plan.temperature'] = config.temperature;
    if (config.baseUrl !== undefined) updates['plan.baseUrl'] = config.baseUrl;
    if (config.apiKey !== undefined) updates['plan.apiKey'] = config.apiKey;

    for (const [key, value] of Object.entries(updates)) {
      await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Workspace);
    }
  }

  /**
   * Update Act stage configuration
   */
  public async updateActConfig(config: Partial<StageConfig>): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration('aiAgent');
    const updates: { [key: string]: any } = {};

    if (config.provider !== undefined) updates['act.provider'] = config.provider;
    if (config.model !== undefined) updates['act.model'] = config.model;
    if (config.maxTurns !== undefined) updates['act.maxTurns'] = config.maxTurns;
    if (config.timeout !== undefined) updates['act.timeout'] = config.timeout;
    if (config.temperature !== undefined) updates['act.temperature'] = config.temperature;
    if (config.baseUrl !== undefined) updates['act.baseUrl'] = config.baseUrl;
    if (config.apiKey !== undefined) updates['act.apiKey'] = config.apiKey;

    for (const [key, value] of Object.entries(updates)) {
      await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Workspace);
    }
  }

  /**
   * Get available providers (for UI dropdowns)
   */
  public getAvailableProviders(): string[] {
    return ['mock', 'ollama', 'openai', 'anthropic', 'google', 'azure-openai'];
  }

  /**
   * Check if current provider is local (Ollama) or cloud-based
   */
  public isLocalProvider(provider: string): boolean {
    return provider === 'mock' || provider === 'ollama';
  }

  /**
   * Validate configuration (checks for required fields)
   */
  public validateConfiguration(config: AgentConfiguration): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (config.mode === 'single') {
      const singleConfig = config as SingleAgentConfig;
      if (!singleConfig.provider) errors.push('Provider is required');
      if (!singleConfig.model) errors.push('Model is required');
      if (singleConfig.maxTurns <= 0) errors.push('Max turns must be greater than 0');
      if (singleConfig.timeout <= 0) errors.push('Timeout must be greater than 0');
    } else {
      const multiConfig = config as MultiAgentConfig;
      
      // Validate plan config
      if (!multiConfig.plan.provider) errors.push('Plan provider is required');
      if (!multiConfig.plan.model) errors.push('Plan model is required');
      if (multiConfig.plan.maxTurns <= 0) errors.push('Plan max turns must be greater than 0');
      if (multiConfig.plan.timeout <= 0) errors.push('Plan timeout must be greater than 0');
      
      // Validate act config
      if (!multiConfig.act.provider) errors.push('Act provider is required');
      if (!multiConfig.act.model) errors.push('Act model is required');
      if (multiConfig.act.maxTurns <= 0) errors.push('Act max turns must be greater than 0');
      if (multiConfig.act.timeout <= 0) errors.push('Act timeout must be greater than 0');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}
