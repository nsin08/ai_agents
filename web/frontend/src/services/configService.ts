// Config service for agent configuration API
import type { AgentConfig, PresetConfig, ConfigResponse } from '../types/config';

// Use environment variable if available (set in .env), otherwise use default
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ConfigService {
  async getDefaultConfig(): Promise<ConfigResponse> {
    const response = await fetch(`${API_BASE_URL}/api/config/default`);
    if (!response.ok) {
      throw new Error('Failed to get default config');
    }
    return response.json();
  }

  async listPresets(): Promise<PresetConfig[]> {
    const response = await fetch(`${API_BASE_URL}/api/config/presets`);
    if (!response.ok) {
      throw new Error('Failed to list presets');
    }
    return response.json();
  }

  async getPreset(presetName: string): Promise<PresetConfig> {
    const response = await fetch(`${API_BASE_URL}/api/config/presets/${presetName}`);
    if (!response.ok) {
      throw new Error(`Failed to get preset: ${presetName}`);
    }
    return response.json();
  }

  async saveConfig(config: AgentConfig, preset?: string, sessionId?: string): Promise<ConfigResponse> {
    const response = await fetch(`${API_BASE_URL}/api/config/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ config, preset, session_id: sessionId }),
    });
    if (!response.ok) {
      throw new Error('Failed to save config');
    }
    return response.json();
  }

  async resetConfig(sessionId?: string): Promise<ConfigResponse> {
    const url = sessionId 
      ? `${API_BASE_URL}/api/config/reset?session_id=${encodeURIComponent(sessionId)}`
      : `${API_BASE_URL}/api/config/reset`;
    const response = await fetch(url, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Failed to reset config');
    }
    return response.json();
  }

  async getSessionConfig(sessionId: string): Promise<ConfigResponse> {
    const response = await fetch(`${API_BASE_URL}/api/config/${sessionId}`);
    if (!response.ok) {
      throw new Error('Failed to get session config');
    }
    return response.json();
  }
}

const configService = new ConfigService();
export default configService;
