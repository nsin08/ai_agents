// Config service for agent configuration API
import type { AgentConfig, PresetConfig, ConfigResponse } from '../types/config';
import { API_BASE_URL, apiFetch } from '../config/api';

class ConfigService {
  async getDefaultConfig(): Promise<ConfigResponse> {
    return apiFetch<ConfigResponse>(`${API_BASE_URL}/api/config/default`);
  }

  async listPresets(): Promise<PresetConfig[]> {
    return apiFetch<PresetConfig[]>(`${API_BASE_URL}/api/config/presets`);
  }

  async getPreset(presetName: string): Promise<PresetConfig> {
    return apiFetch<PresetConfig>(
      `${API_BASE_URL}/api/config/presets/${presetName}`
    );
  }

  async saveConfig(config: AgentConfig, preset?: string, sessionId?: string): Promise<ConfigResponse> {
    return apiFetch<ConfigResponse>(
      `${API_BASE_URL}/api/config/save`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config, preset, session_id: sessionId }),
      }
    );
  }

  async resetConfig(sessionId?: string): Promise<ConfigResponse> {
    const url = sessionId 
      ? `${API_BASE_URL}/api/config/reset?session_id=${encodeURIComponent(sessionId)}`
      : `${API_BASE_URL}/api/config/reset`;
    return apiFetch<ConfigResponse>(url, { method: 'POST' });
  }

  async getSessionConfig(sessionId: string): Promise<ConfigResponse> {
    return apiFetch<ConfigResponse>(
      `${API_BASE_URL}/api/config/${sessionId}`
    );
  }
}

const configService = new ConfigService();
export default configService;
