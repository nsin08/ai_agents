import React, { useState, useEffect } from "react";
import "./ConfigPanel.css";
import type { AgentConfig, PresetConfig } from "../types/config";
import configService from "../services/configService";

interface ConfigPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onConfigChange: (config: AgentConfig) => void;
  currentConfig: AgentConfig;
  sessionId?: string;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({
  isOpen,
  onClose,
  onConfigChange,
  currentConfig,
  sessionId,
}) => {
  const [config, setConfig] = useState<AgentConfig>(currentConfig);
  const [presets, setPresets] = useState<PresetConfig[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadPresets();
    }
  }, [isOpen]);

  useEffect(() => {
    setConfig(currentConfig);
  }, [currentConfig]);

  const loadPresets = async () => {
    try {
      const presetList = await configService.listPresets();
      setPresets(presetList);
    } catch (error) {
      console.error("Failed to load presets:", error);
    }
  };

  const handleApplyPreset = async (presetName: string) => {
    setLoading(true);
    try {
      const response = await configService.saveConfig(config, presetName, sessionId);
      setConfig(response.config);
      onConfigChange(response.config);
    } catch (error) {
      console.error("Failed to apply preset:", error);
      alert("Failed to apply preset");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    setLoading(true);
    try {
      const response = await configService.saveConfig(config, undefined, sessionId);
      onConfigChange(response.config);
      alert("Configuration saved successfully!");
    } catch (error) {
      console.error("Failed to save config:", error);
      alert("Failed to save configuration");
    } finally {
      setLoading(false);
    }
  };

  const handleResetConfig = async () => {
    if (!window.confirm("Reset to default configuration?")) {
      return;
    }

    setLoading(true);
    try {
      const response = await configService.resetConfig(sessionId);
      setConfig(response.config);
      onConfigChange(response.config);
    } catch (error) {
      console.error("Failed to reset config:", error);
      alert("Failed to reset configuration");
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = (field: keyof AgentConfig, value: any) => {
    setConfig({ ...config, [field]: value });
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="config-panel-overlay" onClick={onClose}>
      <div className="config-panel" onClick={(e) => e.stopPropagation()}>
        <div className="config-panel-header">
          <h3>⚙️ Agent Configuration</h3>
          <button className="close-button" onClick={onClose} aria-label="Close configuration panel">
            ✕
          </button>
        </div>

        <div className="config-panel-content">
          {/* Presets */}
          <section className="config-section">
            <h4>🎯 Quick Presets</h4>
            <div className="preset-buttons">
              {presets.map((preset) => (
                <button
                  key={preset.name}
                  className="preset-button"
                  onClick={() => handleApplyPreset(preset.name.toLowerCase())}
                  disabled={loading}
                  title={preset.description}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </section>

          {/* Max Turns */}
          <section className="config-section">
            <label htmlFor="max-turns-slider">
              <h4>🔄 Max Turns: {config.max_turns}</h4>
            </label>
            <input
              id="max-turns-slider"
              type="range"
              min="1"
              max="10"
              value={config.max_turns}
              onChange={(e) => updateConfig("max_turns", parseInt(e.target.value))}
              className="config-slider"
            />
            <div className="slider-labels">
              <span>1</span>
              <span>10</span>
            </div>
            <p className="config-help">Number of reasoning iterations (more = better reasoning, slower)</p>
          </section>

          {/* Temperature */}
          <section className="config-section">
            <label htmlFor="temperature-slider">
              <h4>🌡️ Temperature: {config.temperature.toFixed(1)}</h4>
            </label>
            <input
              id="temperature-slider"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.temperature}
              onChange={(e) => updateConfig("temperature", parseFloat(e.target.value))}
              className="config-slider"
            />
            <div className="slider-labels">
              <span>0.0 (Precise)</span>
              <span>2.0 (Creative)</span>
            </div>
            <p className="config-help">Controls randomness (lower = more focused, higher = more creative)</p>
          </section>

          {/* Timeout */}
          <section className="config-section">
            <label htmlFor="timeout-input">
              <h4>⏱️ Timeout (seconds)</h4>
            </label>
            <input
              id="timeout-input"
              type="number"
              min="5"
              max="300"
              value={config.timeout_seconds}
              onChange={(e) => updateConfig("timeout_seconds", parseInt(e.target.value))}
              className="config-number-input"
            />
            <p className="config-help">Maximum time to wait for agent response (5-300 seconds)</p>
          </section>

          {/* System Prompt */}
          <section className="config-section">
            <label htmlFor="system-prompt-textarea">
              <h4>💬 Custom System Prompt (optional)</h4>
            </label>
            <textarea
              id="system-prompt-textarea"
              value={config.system_prompt || ""}
              onChange={(e) => updateConfig("system_prompt", e.target.value || null)}
              className="config-textarea"
              placeholder="Enter custom system prompt..."
              rows={4}
            />
            <p className="config-help">Override default agent behavior with custom instructions</p>
          </section>

          {/* Debug Mode */}
          <section className="config-section">
            <label className="config-checkbox-label">
              <input
                type="checkbox"
                checked={config.enable_debug}
                onChange={(e) => updateConfig("enable_debug", e.target.checked)}
                className="config-checkbox"
              />
              <span>🔧 Enable Debug Mode</span>
            </label>
            <p className="config-help">Show detailed agent metrics and reasoning chain</p>
          </section>
        </div>

        <div className="config-panel-footer">
          <button
            className="reset-button"
            onClick={handleResetConfig}
            disabled={loading}
          >
            Reset to Default
          </button>
          <button
            className="save-button"
            onClick={handleSaveConfig}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save Configuration"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel;
